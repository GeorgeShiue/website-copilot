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


def _close_vector_store(vector_store: MilvusVectorStore) -> None:
    if isinstance(vector_store, MilvusVectorStore):
        try:
            vector_store._milvusclient.close()
        except Exception:
            logger.warning("Milvus client close() failed", exc_info=True)


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
        _close_vector_store(self.vector_store)


class IndexBuilder:
    def __init__(self, config: RAGConfig) -> None:
        self.config = config
        self._build_stats: dict[str, str] = {}

    def build_or_load(self, force_rebuild: bool = False) -> IndexHandle:
        """建到 index 層級，視情況重建或載入既有 index。不含 retriever／query engine。

        - force_rebuild=True 或 store 路徑不存在時重建（讀取 webpages 來源）。
        - 否則載入既有向量庫（不讀取 webpages）。
        """
        if self._should_rebuild(force_rebuild):
            assert self.config.webpages_data_folder_path is not None
            source = load_source(self.config.webpages_data_folder_path)
            return self.build(source)
        return self.load()

    def build(self, source: Source) -> IndexHandle:
        """重建：clean（整檔刪除）→ nodes → vector store → index。"""
        self._build_stats = {}
        # record=False：細部步驟只印耗時，不進入 prepare workflow 的階段摘要
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
            _close_vector_store(vector_store)
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
            _close_vector_store(vector_store)
            raise
        self._log_build_stats()
        return self._handle(vector_store, index)

    def _handle(
        self, vector_store: MilvusVectorStore, index: VectorStoreIndex
    ) -> IndexHandle:
        assert self.config.vector_store.milvus_uri is not None
        return IndexHandle(
            vector_store=vector_store,
            index=index,
            milvus_uri=self.config.vector_store.milvus_uri,
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
        assert self.config.vector_store.milvus_uri is not None
        return not os.path.exists(self.config.vector_store.milvus_uri)

    def clean(self) -> None:
        """整檔刪除既有向量庫（重建前呼叫）。"""
        milvus_uri = self.config.vector_store.milvus_uri
        if milvus_uri and os.path.exists(milvus_uri):
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
            site_id=self.config.site_id,
        )
        self._build_stats["Documents loaded"] = str(builder.last_doc_count)
        self._build_stats["Nodes produced"] = str(len(nodes))
        return nodes

    def build_vector_store(self) -> MilvusVectorStore:
        vector_store_config = self.config.vector_store
        assert vector_store_config.milvus_uri is not None
        params = vector_store_config.hybrid_ranker_params
        logger.info(
            "Building Milvus vector store (sparse embedding: BGE-M3, hybrid_ranker=%s)",
            vector_store_config.hybrid_ranker,
        )
        return VectorStoreBuilder.build(
            collection_name=self.config.site_id,
            embedding_name=self.config.index.embedding_name,
            milvus_uri=vector_store_config.milvus_uri,
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
