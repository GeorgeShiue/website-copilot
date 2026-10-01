"""在 index 之上組裝查詢物件（retriever / query engine），並提供 RAG 的建置（build_rag）與 serve 載入（load_rag）入口。"""

import logging
import os
from typing import Any

from llama_index.core import VectorStoreIndex, get_response_synthesizer
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.vector_stores.types import VectorStoreQueryMode

from website_copilot.config.rag_config import RAGConfig
from website_copilot.ingestion.indexing.index import IndexBuilder, IndexHandle
from website_copilot.retrieval.llama_index_helpers import build_filters, create_llm
from website_copilot.retrieval.rag import RAG
from website_copilot.storage.run_manager import RunManager
from website_copilot.storage.run_persistence import load_latest_run_path
from website_copilot.utils.log_helper import log_session

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


def build_rag(
    config_name: str = "default",
    force_rebuild: bool = False,
    webpages_data_use_latest_results: bool = False,
    run_manager: RunManager | None = None,
    build_query_engine: bool = True,
    config: RAGConfig | None = None,
    overrides: dict[str, Any] | None = None,
) -> RAG:
    """建立並建構 RAG 實例。僅執行建構流程，不包含 query 步驟。

    Args:
        config_name: RAGConfig 名稱（對應 configs/rag/{name}.yml）。config 為
            None 時才會用它從 yml 解析。
        force_rebuild: 是否強制重建向量庫。
        webpages_data_use_latest_results: 是否改用 runs/ 中該 site 最新一次
            image summarizer 的結果建庫（需該次以 save=True 執行）；False 時
            使用 config.webpages_data_folder_path（預設 data/webpages/{site_id}）。
        run_manager: 呼叫端已建立的 RunManager（可選）。傳入時向量庫會建到
            該 run 的 results/ 目錄下；None 時使用 config 的預設持久化路徑。
        build_query_engine: 是否建到 retriever／query engine 層級；
            False 時僅建到 vector store／index 層級（不含 retriever）。
        config: 呼叫端已建立的 RAGConfig（可選）。傳入時直接沿用，不再重新
            解析 yml；此時 config_name／overrides 會被忽略。
        overrides: RAGConfig 的巢狀覆寫值（含 site_id），僅在 config 為 None 時生效。

    Returns:
        已建構的 RAG 實例（呼叫端負責 close）。
    """
    if config is None:
        config = RAGConfig.from_yaml(config_name, overrides)

    # ----- 解決 webpages 資料路徑（改用 runs/ 中最新的 image summarizer 結果）-----
    if webpages_data_use_latest_results:
        log_session("Finding Latest Webpages Data", style="cyan")
        config.webpages_data_folder_path = load_latest_run_path(
            run_manager.base_folder if run_manager is not None else "runs",
            "image_summarizer",
            site_id=config.site_id,
        )

    # ----- 解決向量庫存放位置（預設位置 vs 呼叫端 run 的 results/）-----
    if run_manager is not None:
        config.vector_store.milvus_uri = os.path.join(
            run_manager.results_folder_path, "milvus.db"
        )

    if build_query_engine:
        log_session("Building RAG to Query Engine", style="cyan")
        index_handle = IndexBuilder(config).build_or_load(force_rebuild=force_rebuild)
        rag = RAGBuilder(config).build(index_handle)
    else:
        log_session("Building RAG to Vector Store", style="cyan")
        index_handle = IndexBuilder(config).build_or_load(force_rebuild=force_rebuild)
        rag = RAG(index_handle)

    return rag


def load_rag(config: RAGConfig) -> RAG:
    """只載入既有向量庫到 retriever 層級，絕不建置（供 serve 階段使用）。

    Raises:
        FileNotFoundError: 向量庫不存在時（應先執行 prepare 階段 publish）。
    """
    assert config.vector_store.milvus_uri is not None
    if not os.path.exists(config.vector_store.milvus_uri):
        raise FileNotFoundError(
            f"Vector store not found: {config.vector_store.milvus_uri}"
            "（請先執行 prepare 階段建置並 publish 向量庫）"
        )
    index_handle: IndexHandle = IndexBuilder(config).load()
    rag = RAGBuilder(config).build(index_handle, build_query_engine=False)
    return rag
