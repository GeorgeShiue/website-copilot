"""向量庫 index 的建置與載入（clean → nodes → vector store → index）。

建置結果以 IndexHandle 回傳；本模組不依賴 retrieval（查詢物件由 retrieval 在 handle 之上組裝）。
"""

import logging
import os
import shutil
from collections.abc import Sequence
from dataclasses import dataclass

from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.schema import BaseNode
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.milvus import MilvusVectorStore
from rich.table import Table

from website_copilot.config.rag_config import RAGConfig
from website_copilot.ingestion.indexing.node_pipeline import NodePipelineBuilder
from website_copilot.ingestion.indexing.source import Source, load_source
from website_copilot.ingestion.indexing.vector_store import (
    VectorStoreBuilder,
)
from website_copilot.utils.log_helper import log_run_time, log_session, print_log

logger = logging.getLogger(__name__)


def _close_vector_store(vector_store: MilvusVectorStore, milvus_uri: str) -> None:
    """關閉 Milvus client，並停止本地（.db）模式的 Milvus Lite server。

    Milvus Lite server 與 client 分開：只關 client，server 會一直開到程式結束才 flush。
    publish 前若 server 還開著，搬移資料夾後 flush 會寫回原路徑，已發布的向量庫只剩
    未 flush 的 WAL（且原路徑留下殘骸）。因此關閉時必須一併 release server。
    """
    if isinstance(vector_store, MilvusVectorStore):
        try:
            vector_store._milvusclient.close()
        except Exception:
            logger.warning("Milvus client close() failed", exc_info=True)
        if milvus_uri.endswith(".db") and "://" not in milvus_uri:
            try:
                from milvus_lite.server_manager import server_manager_instance

                server_manager_instance.release_server(milvus_uri)
            except Exception:
                logger.warning("Milvus Lite server release failed", exc_info=True)


# 所有站點的 Milvus collection 名稱：向量庫已是每站一份（data/vector_db/{site_id}.db），
# collection 不再重複 site_id（站點資訊仍在 node metadata）。
COLLECTION_NAME = "chunks"


@dataclass(frozen=True)
class RAGTarget:
    """RAG 的執行期目標：由站點與執行模式決定，不是可調參數（不寫入 module_config）。

    Attributes:
        site_id: 站點識別碼，寫入 node metadata。
        aug_webpages_dir: 建庫資料來源（含 results.json 與 results/*.md 的資料夾）。
        milvus_uri: 向量庫位置（Milvus Lite 資料夾，名稱須以 .db 結尾）。
    """

    site_id: str
    aug_webpages_dir: str
    milvus_uri: str


@dataclass
class IndexHandle:
    """已建置或載入的向量庫 index。

    Attributes:
        vector_store: 連線中的 Milvus 向量庫。
        index: 建於 vector_store 之上的 VectorStoreIndex。
        milvus_uri: 向量庫實際位置。
    """

    vector_store: MilvusVectorStore
    index: VectorStoreIndex
    milvus_uri: str

    def close(self) -> None:
        """關閉 Milvus client 連線。"""
        _close_vector_store(self.vector_store, self.milvus_uri)


class IndexBuilder:
    def __init__(self, config: RAGConfig, target: RAGTarget) -> None:
        self.config = config
        self.target = target
        self._build_stats: dict[str, str] = {}

    def build_or_load(self, force_rebuild: bool = False) -> IndexHandle:
        """建到 index 層級，視情況重建或載入既有 index。不含 retriever／query engine。

        - force_rebuild=True 或 store 路徑不存在時重建（讀取 aug_webpages 來源）。
        - 否則載入既有向量庫（不讀取 aug_webpages）。
        """
        if self._should_rebuild(force_rebuild):
            source = load_source(self.target.aug_webpages_dir)
            return self.build(source)
        return self.load()

    def build(self, source: Source) -> IndexHandle:
        """重建：clean（整檔刪除）→ nodes → vector store → index。"""
        self._build_stats = {}
        # record=False：細部步驟只印耗時，不進入 Prepare Pipeline 的階段摘要
        with log_run_time("Clean vector store", record=False):
            self.clean()
        with log_run_time("Build nodes", record=False):
            nodes = self.build_nodes(source)
        with log_run_time("Build vector store", record=False):
            vector_store = self.build_vector_store()
        try:
            with log_run_time("Build index", record=False):
                index = self.build_index(vector_store, nodes)
        except BaseException:
            _close_vector_store(vector_store, self.target.milvus_uri)
            raise
        self._log_build_stats()
        return self._handle(vector_store, index)

    def load(self) -> IndexHandle:
        """載入：build_vector_store（沿用既有 collection）→ load_index。"""
        self._build_stats = {}
        vector_store = self.build_vector_store()
        try:
            # Milvus 重用既有 collection 時，需手動載入（ released → loaded ）
            if self.config.vector_store.vector_store_type == "milvus":
                vector_store.client.load_collection(vector_store.collection_name)
            index = self.load_index(vector_store)
        except BaseException:
            _close_vector_store(vector_store, self.target.milvus_uri)
            raise
        self._log_build_stats()
        return self._handle(vector_store, index)

    def _handle(
        self, vector_store: MilvusVectorStore, index: VectorStoreIndex
    ) -> IndexHandle:
        return IndexHandle(
            vector_store=vector_store,
            index=index,
            milvus_uri=self.target.milvus_uri,
        )

    def _log_build_stats(self) -> None:
        log_session("RAG Build Stats", style="green")
        table = Table(show_header=True, header_style="bold green")
        table.add_column("Metric", style="green", no_wrap=True)
        table.add_column("Value", style="white")
        for metric, value in self._build_stats.items():
            table.add_row(metric, value)
        print_log(table)

    def _should_rebuild(self, force_rebuild: bool) -> bool:
        """決定是否需要重建 vector store / index。

        force_rebuild=True 或 store 路徑不存在時重建。
        """
        if force_rebuild:
            return True
        return not os.path.exists(self.target.milvus_uri)

    def clean(self) -> None:
        """整檔刪除既有向量庫（重建前呼叫）。"""
        milvus_uri = self.target.milvus_uri
        if os.path.exists(milvus_uri):
            if os.path.isdir(milvus_uri):
                shutil.rmtree(milvus_uri)
            else:
                os.remove(milvus_uri)
            logger.info("Cleaned Milvus vector store: %s", milvus_uri)

    def build_nodes(self, source: Source) -> list[BaseNode]:
        builder = NodePipelineBuilder(
            chunk_size=self.config.nodes.chunk_size,
            chunk_overlap=self.config.nodes.chunk_overlap,
            paragraph_separator=self.config.nodes.paragraph_separator,
        )
        nodes = builder.build(
            md_folder_path=source.md_folder_path,
            results_json=source.results_json,
            site_id=self.target.site_id,
        )
        self._build_stats["Documents loaded"] = str(builder.last_doc_count)
        self._build_stats["Nodes produced"] = str(len(nodes))
        return nodes

    def build_vector_store(self) -> MilvusVectorStore:
        vector_store_config = self.config.vector_store
        params = vector_store_config.hybrid_ranker_params
        logger.info(
            "Building Milvus vector store (sparse embedding: BGE-M3, hybrid_ranker=%s)",
            vector_store_config.hybrid_ranker,
        )
        return VectorStoreBuilder.build(
            collection_name=COLLECTION_NAME,
            embedding_name=self.config.index.embedding_name,
            milvus_uri=self.target.milvus_uri,
            hybrid_ranker=vector_store_config.hybrid_ranker,
            hybrid_ranker_params=(
                params.model_dump(exclude_none=True) if params is not None else None
            ),
        )

    def _create_embed_model(self, embedding_name: str) -> OpenAIEmbedding:
        api_key = os.getenv("OPENAI_API_KEY")
        return OpenAIEmbedding(
            model=embedding_name, embed_batch_size=256, api_key=api_key
        )

    def build_index(
        self, vector_store: MilvusVectorStore, nodes: Sequence[BaseNode]
    ) -> VectorStoreIndex:
        logger.info(
            "Building index (dense embedding: %s, nodes=%d)",
            self.config.index.embedding_name,
            len(nodes),
        )
        embed_model = self._create_embed_model(self.config.index.embedding_name)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex(
            nodes,
            storage_context=storage_context,
            embed_model=embed_model,
            show_progress=True,
        )
        self._build_stats["Index nodes"] = str(len(nodes))
        return index

    def load_index(self, vector_store: MilvusVectorStore) -> VectorStoreIndex:
        embed_model = self._create_embed_model(self.config.index.embedding_name)
        index = VectorStoreIndex.from_vector_store(
            vector_store, embed_model, show_progress=True
        )
        self._build_stats["Index nodes"] = "loaded from existing vector store"
        return index
