"""在 index 之上組裝查詢物件（retriever / query engine），並提供 RAG 的建置（build_rag）與 serve 載入（load_rag）入口。

站點、資料來源與向量庫位置以 RAGTarget 傳入（published_target／vector_store_run_target／build_target 依執行模式產生），
config 只含可調參數，建置過程中不會被改寫。
"""

import logging
import os
from typing import Any

import yaml
from llama_index.core import VectorStoreIndex, get_response_synthesizer
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.vector_stores.types import VectorStoreQueryMode

from website_copilot.config.rag_config import RAGConfig
from website_copilot.ingestion.indexing.index import (
    IndexBuilder,
    IndexHandle,
    RAGTarget,
)
from website_copilot.ingestion.indexing.source import load_source
from website_copilot.retrieval.llama_index_helpers import build_filters, create_llm
from website_copilot.retrieval.rag import RAG
from website_copilot.storage.data_paths import aug_webpages_path, vector_store_path
from website_copilot.storage.run_persistence import load_latest_run_path
from website_copilot.utils.config_helper import MODULE_CONFIG_FILE, SITE_CONFIG_FILE
from website_copilot.utils.log_helper import log_session, print_log

logger = logging.getLogger(__name__)


class RAGBuilder:
    def __init__(self, config: RAGConfig) -> None:
        self.config = config

    def build(self, index_handle: IndexHandle, build_query_engine: bool = True) -> RAG:
        """在 index 之上建 retriever（與 query engine），回傳 RAG。

        建置失敗時關閉 index_handle，避免 Milvus 連線外洩。
        """
        try:
            retriever = self.build_retriever(index_handle.index)
            query_engine = (
                self.build_query_engine(retriever) if build_query_engine else None
            )
        except BaseException:
            index_handle.close()
            raise
        return RAG(index_handle, retriever=retriever, query_engine=query_engine)

    def build_retriever(
        self, index: VectorStoreIndex, filter_dict: dict[str, Any] | None = None
    ) -> VectorIndexRetriever:
        filters = build_filters(filter_dict)
        if filter_dict:
            logger.info(f"Building retriever with filters: {filter_dict}")

        vector_store_query_mode = (
            VectorStoreQueryMode.HYBRID
            if self.config.retriever.query_mode == "hybrid"
            else VectorStoreQueryMode.DEFAULT
        )
        return VectorIndexRetriever(
            index=index,
            similarity_top_k=self.config.retriever.similarity_top_k,
            filters=filters,
            vector_store_query_mode=vector_store_query_mode,
            hybrid_top_k=self.config.retriever.hybrid_top_k,
            alpha=self.config.retriever.alpha,
        )

    def build_query_engine(
        self, retriever: VectorIndexRetriever
    ) -> RetrieverQueryEngine:
        llm = create_llm(self.config.query_engine.query_llm_name)
        response_synthesizer = get_response_synthesizer(llm)

        node_postprocessors = []
        if self.config.retriever.query_mode != "hybrid":
            node_postprocessors.append(
                SimilarityPostprocessor(
                    similarity_cutoff=self.config.query_engine.cutoff
                )
            )

        return RetrieverQueryEngine(
            retriever,
            response_synthesizer,
            node_postprocessors=node_postprocessors,
        )


def _run_source(run_path: str) -> str:
    """讀取 run 的 module_config.yml 檔頭的 `# source:`；讀不到時回傳 unknown。"""
    try:
        with open(os.path.join(run_path, MODULE_CONFIG_FILE), encoding="utf-8") as f:
            for line in f:
                if line.startswith("# source:"):
                    return line.removeprefix("# source:").strip()
                if not line.startswith("#"):
                    break
    except OSError:
        pass
    return "unknown"


def _log_target(target: RAGTarget) -> None:
    """記錄本次 RAG 的站點、資料來源與向量庫位置（不寫入 module_config.yml）。"""
    log_session("RAG Target", style="cyan")
    print_log(f"site_id: {target.site_id}")
    print_log(f"aug_webpages_dir: {target.aug_webpages_dir}")
    print_log(f"milvus_uri: {target.milvus_uri}")


def published_target(site_id: str, data_folder: str = "data") -> RAGTarget:
    """已 publish 的位置：資料來源 data/aug_webpages/{site_id}、向量庫 data/vector_db/{site_id}.db。

    serve 載入與 rag-query 使用；rag-build 一律不直接寫入這裡（見 build_target）。
    """
    return RAGTarget(
        site_id=site_id,
        aug_webpages_dir=aug_webpages_path(site_id, data_folder),
        milvus_uri=vector_store_path(site_id, data_folder),
    )


def vector_store_run_target(
    site_id: str, run_path: str, data_folder: str = "data"
) -> RAGTarget:
    """runs/ 中 rag-build 建出的向量庫（<run_path>/results/milvus.db），供 rag-query 唯讀查詢。

    以 <run_path>/site_config.yml 核對站點；log 印出建庫時的設定來源（module_config.yml 檔頭）。

    Raises:
        FileNotFoundError: run_path 或其 results/milvus.db 不存在時。
        ValueError: run 的站點與 site_id 不一致時。
    """
    if not os.path.isdir(run_path):
        raise FileNotFoundError(f"vector_store_run 不存在或不是資料夾: {run_path}")
    milvus_uri = os.path.join(run_path, "results", "milvus.db")
    if not os.path.exists(milvus_uri):
        raise FileNotFoundError(
            f"找不到向量庫: {milvus_uri}（vector_store_run 應為 rag-build 的 run 資料夾）"
        )
    site_config_path = os.path.join(run_path, SITE_CONFIG_FILE)
    if not os.path.isfile(site_config_path):
        raise FileNotFoundError(f"找不到 {site_config_path}，無法核對站點")
    with open(site_config_path, encoding="utf-8") as f:
        run_site = (yaml.safe_load(f) or {}).get("site_id")
    if run_site != site_id:
        raise ValueError(
            f"站點不一致: vector_store_run 屬於 {run_site!r}，但指定的站點為 {site_id!r}"
        )
    print_log(f"vector_store_run: {run_path}（建庫設定 {_run_source(run_path)}）")
    return RAGTarget(
        site_id=site_id,
        aug_webpages_dir=aug_webpages_path(site_id, data_folder),
        milvus_uri=milvus_uri,
    )


def build_target(
    site_id: str,
    milvus_uri: str,
    use_latest_results: bool = False,
    runs_folder: str = "runs",
    data_folder: str = "data",
) -> RAGTarget:
    """rag-build 的目標：向量庫位置由呼叫端依 save／publish 決定，資料來源依執行模式決定。

    Args:
        site_id: 站點識別碼。
        milvus_uri: 向量庫建置位置（run 的 results/milvus.db、data/vector_db/.staging-*/{site_id}.db 或系統暫存）。
        use_latest_results: True 時改用 runs/ 中同站點最新一次 augmenter
            的結果（需該次以 save=True 執行）；False 時使用 data/aug_webpages/{site_id}。
        runs_folder: runs/ 根目錄。
        data_folder: data/ 根目錄。
    """
    if use_latest_results:
        log_session("Finding Latest Webpages Data", style="cyan")
        aug_webpages_dir = load_latest_run_path(
            runs_folder, "augmenter", site_id=site_id
        )
    else:
        aug_webpages_dir = aug_webpages_path(site_id, data_folder)
    return RAGTarget(
        site_id=site_id, aug_webpages_dir=aug_webpages_dir, milvus_uri=milvus_uri
    )


def build_rag(config: RAGConfig, target: RAGTarget) -> RAG:
    """重建向量庫並回傳 RAG（只建到 vector store／index 層級，不含 retriever）。

    一律重建：先讀取 target.aug_webpages_dir 的來源，成功後才清除既有向量庫並建庫。
    不會改寫 config；查詢請以 load_rag 載入已建好的向量庫。

    Args:
        config: RAG 參數。
        target: 站點、資料來源與向量庫位置（見 build_target）。

    Returns:
        已建構的 RAG 實例（呼叫端負責 close）。

    Raises:
        FileNotFoundError: 資料來源缺少 results.json 時（此時不會清除既有向量庫）。
    """
    _log_target(target)
    log_session("Building RAG to Vector Store", style="cyan")
    source = load_source(target.aug_webpages_dir)
    return RAG(IndexBuilder(config, target).build(source))


def load_rag(
    config: RAGConfig, target: RAGTarget, build_query_engine: bool = False
) -> RAG:
    """只載入既有向量庫（預設到 retriever 層級；build_query_engine 時含 query engine），絕不建置。

    供 serve（retriever）與 rag-query（query engine）使用。

    Raises:
        FileNotFoundError: 向量庫不存在時（應先執行 prepare 階段 publish）。
    """
    if not os.path.exists(target.milvus_uri):
        raise FileNotFoundError(
            f"Vector store not found: {target.milvus_uri}"
            "（請先執行 prepare 階段建置並 publish 向量庫）"
        )
    index_handle: IndexHandle = IndexBuilder(config, target).load()
    return RAGBuilder(config).build(index_handle, build_query_engine=build_query_engine)
