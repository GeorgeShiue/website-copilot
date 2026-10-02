import gc
import logging
from typing import Any, Self

from llama_index.core.base.response.schema import Response
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever

from website_copilot.ingestion.indexing.index import IndexHandle
from website_copilot.retrieval.llama_index_helpers import (
    build_filters,
    log_source_nodes,
    source_dict,
)

logger = logging.getLogger(__name__)


class RAG:
    """查詢服務：以 IndexHandle 為底，持有 retriever 與（可選的）query engine。

    Attributes:
        index_handle: 已建置或載入的向量庫 index（close 時一併關閉）。
        retriever: 檢索器；None 表示只建到 index 層級。
        query_engine: 問答引擎；None 表示不支援 query()。
    """

    def __init__(
        self,
        index_handle: IndexHandle,
        retriever: VectorIndexRetriever | None = None,
        query_engine: RetrieverQueryEngine | None = None,
    ) -> None:
        self.index_handle: IndexHandle | None = index_handle
        self.retriever = retriever
        self.query_engine = query_engine
        self._closed: bool = False

    @property
    def milvus_uri(self) -> str | None:
        """本次建構實際使用的向量庫位置。"""
        return self.index_handle.milvus_uri if self.index_handle else None

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        self.close()

    def __del__(self) -> None:
        self.close()

    def close(self) -> None:
        if getattr(self, "_closed", False):
            return

        if self.index_handle is not None:
            self.index_handle.close()

        self._closed = True
        self.index_handle = None
        self.retriever = None
        self.query_engine = None

        gc.collect()

    def query(self, query: str, log_sources: bool = False) -> Response:
        if self.query_engine is None:
            raise RuntimeError("RAG service have not been built, cannot execute query")

        logger.info(f"Query: {query}")
        response = self.query_engine.query(query)
        if isinstance(response, Response):
            logger.info(f"Response: {response.response}")
            if log_sources:
                log_source_nodes(response.source_nodes)
            return response
        raise TypeError(
            f"Query engine returned unexpected response type: {type(response)}"
        )

    def retrieve(
        self,
        query: str,
        filter_dict: dict[str, Any] | None = None,
        similarity_top_k: int | None = None,
    ) -> list[dict[str, Any]]:
        if self.retriever is None:
            raise RuntimeError("Retriever has not been built, cannot retrieve")

        original_filters = self.retriever._filters
        original_top_k = self.retriever.similarity_top_k
        try:
            if filter_dict is not None:
                self.retriever._filters = build_filters(filter_dict)
            if similarity_top_k is not None:
                self.retriever.similarity_top_k = similarity_top_k

            nodes = self.retriever.retrieve(query)
        finally:
            self.retriever._filters = original_filters
            self.retriever.similarity_top_k = original_top_k

        return [source_dict(node) for node in nodes]
