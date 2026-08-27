import gc
import json
import logging
import os
from typing import Any, Self, Sequence

from llama_index.core import VectorStoreIndex
from llama_index.core.base.response.schema import Response
from llama_index.core.evaluation import (
    FaithfulnessEvaluator,
    RelevancyEvaluator,
)
from llama_index.core.evaluation.base import EvaluationResult
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.schema import BaseNode, NodeWithScore
from llama_index.core.utils import truncate_text
from llama_index.vector_stores.milvus import MilvusVectorStore

from utils.log_helper import log_session, log_source_title
from utils.rag_helper import build_filters, extract_sources_info

logger = logging.getLogger(__name__)


class RAG:
    def __init__(
        self,
        webpages_data_folder_path: str,
    ) -> None:
        self.webpages_data_folder_path = webpages_data_folder_path
        self.md_docs_folder_path = os.path.join(webpages_data_folder_path, "results")
        self.results_json_path = os.path.join(webpages_data_folder_path, "results.json")
        self.results_json: dict[str, Any] = self._load_results_json()

        self.vector_store: MilvusVectorStore | None = None
        self.index: VectorStoreIndex | None = None
        self.nodes: Sequence[BaseNode] | None = None
        self.retriever: VectorIndexRetriever | None = None
        self.query_engine: RetrieverQueryEngine | None = None
        self.evaluators: tuple[FaithfulnessEvaluator, RelevancyEvaluator] | None = None
        self._closed: bool = False

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

    def _load_results_json(
        self, results_json_path: str | None = None
    ) -> dict[str, Any]:
        if results_json_path is None:
            results_json_path = self.results_json_path
        if not os.path.exists(results_json_path):
            raise FileNotFoundError(
                f"Results JSON file not found at {results_json_path}"
            )
        with open(results_json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def close(self) -> None:
        if getattr(self, "_closed", False):
            return
        self._closed = True

        if isinstance(self.vector_store, MilvusVectorStore):
            try:
                self.vector_store._milvusclient.close()
            except Exception:
                pass

        self.vector_store = None
        self.index = None
        self.retriever = None
        self.query_engine = None
        self.evaluators = None

        gc.collect()

    def query(self, query: str, log_sources: bool = False) -> Response:
        if self.query_engine is None:
            raise RuntimeError("RAG service have not been built, cannot execute query")

        logger.info(f"Query: {query}")
        response = self.query_engine.query(query)
        if isinstance(response, Response):
            logger.info(f"Response: {response.response}")
            if log_sources:
                self._log_sources(response.source_nodes)
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

        results = []
        for node in nodes:
            page_title, score, page_type = extract_sources_info(node)
            results.append(
                {
                    "page_title": page_title,
                    "score": score,
                    "page_type": page_type,
                    "content": node.node.get_content(),
                    "url": node.node.metadata.get("page_url", ""),
                }
            )

        return results

    def evaluate(
        self,
        query: str,
        response: Response,
    ) -> tuple[EvaluationResult, EvaluationResult]:
        if self.evaluators is None:
            raise RuntimeError("Evaluators have not been built, cannot evaluate")
        faithfulness_evaluator, relevancy_evaluator = self.evaluators

        faithfulness_result = faithfulness_evaluator.evaluate_response(
            response=response
        )
        self._log_evaluation_result("Faithfulness", faithfulness_result)

        relevancy_result = relevancy_evaluator.evaluate_response(
            query=query,
            response=response,
        )
        self._log_evaluation_result("Relevancy", relevancy_result)
        return faithfulness_result, relevancy_result

    def _log_sources(self, source_nodes: Sequence[NodeWithScore]) -> None:
        log_session("Sources", style="blue")
        logger.info(f"Retrieved {len(source_nodes)} sources")
        for source_node in source_nodes:
            page_title, score, page_type = extract_sources_info(source_node)
            log_source_title(page_title, score, page_type)
            raw_content = source_node.node.get_content()
            format_content = truncate_text(raw_content, max_length=500)
            logger.info(format_content)

    def _log_evaluation_result(
        self, evaluation_type: str, evaluation_result: EvaluationResult
    ) -> None:
        log_session(f"{evaluation_type} Result", style="blue")
        logger.info(f"Passing: {evaluation_result.passing}")
        reason = None
        if evaluation_result.feedback:
            reason = evaluation_result.feedback.split("Reason:", 1)[-1].strip()
        logger.info(f"Reason: {reason}")
