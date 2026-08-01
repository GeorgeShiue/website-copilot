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
from llama_index.core.prompts import PromptTemplate
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.schema import BaseNode, NodeWithScore
from llama_index.core.utils import truncate_text
from llama_index.core.vector_stores import (
    FilterOperator,
    MetadataFilter,
    MetadataFilters,
)
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.milvus import MilvusVectorStore
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from app.configs.rag_config import WEBPAGES_DATA_FOLDER_PATH
from utils.log_helper import log_session, log_source_title
from utils.rag_helper import extract_sources_info

logger = logging.getLogger(__name__)

LLM_API_KEY_ENV_VARS: dict[str, dict[str, str]] = {
    "gemini": {
        "query_engine": "GEMINI_RAG_QUERY_ENGINE_API_KEY",
        "evaluator": "GEMINI_RAG_EVALUATOR_API_KEY",
    },
    "gpt": {
        "query_engine": "OPENAI_RAG_QUERY_ENGINE_API_KEY",
        "evaluator": "OPENAI_RAG_EVALUATOR_API_KEY",
    },
}

FAITHFULNESS_EVAL_TEMPLATE = PromptTemplate(
    "Please tell if a given piece of information "
    "is supported by the context.\n"
    "You need to answer with either YES or NO, followed by a short reason.\n"
    "Answer YES if any of the context supports the information, even "
    "if most of the context is unrelated. "
    "If you answer YES or NO, add a second line starting with 'Reason:' "
    "and explain your decision briefly. "
    "請在 'Reason:' 行以繁體中文簡短說明（只要一句話即可）。 "
    "Some examples are provided below. \n\n"
    "Information: Apple pie is generally double-crusted.\n"
    "Context: An apple pie is a fruit pie in which the principal filling "
    "ingredient is apples. \n"
    "Apple pie is often served with whipped cream, ice cream "
    "('apple pie à la mode'), custard or cheddar cheese.\n"
    "It is generally double-crusted, with pastry both above "
    "and below the filling; the upper crust may be solid or "
    "latticed (woven of crosswise strips).\n"
    "Answer: YES\n"
    "Reason: The context explicitly says the pie is generally double-crusted.\n"
    "Information: Apple pies tastes bad.\n"
    "Context: An apple pie is a fruit pie in which the principal filling "
    "ingredient is apples. \n"
    "Apple pie is often served with whipped cream, ice cream "
    "('apple pie à la mode'), custard or cheddar cheese.\n"
    "It is generally double-crusted, with pastry both above "
    "and below the filling; the upper crust may be solid or "
    "latticed (woven of crosswise strips).\n"
    "Answer: NO\n"
    "Reason: The context describes the pie, but it does not say anything about taste.\n"
    "Information: {query_str}\n"
    "Context: {context_str}\n"
    "Answer: "
)

FAITHFULNESS_REFINE_TEMPLATE = PromptTemplate(
    "We want to understand if the following information is present "
    "in the context information: {query_str}\n"
    "We have provided an existing YES/NO answer: {existing_answer}\n"
    "We have the opportunity to refine the existing answer "
    "(only if needed) with some more context below.\n"
    "------------\n"
    "{context_msg}\n"
    "------------\n"
    "If the existing answer was already YES, still answer YES. "
    "If the information is present in the new context, answer YES. "
    "Otherwise answer NO.\n"
    "After YES or NO, add a new line starting with 'Reason:' and briefly "
    "explain the decision based on the available context.\n"
    "請在 'Reason:' 行以繁體中文簡短說明（只要一句話即可）。\n"
)

RELEVANCY_EVAL_TEMPLATE = PromptTemplate(
    "Please tell if the response for the query is in line with the context \n"
    "information provided.\n"
    "You need to answer with either YES or NO, followed by a short reason.\n"
    "Answer YES if the response for the query is in line with the context \n"
    "information, otherwise NO.\n"
    "After YES or NO, add a second line starting with 'Reason:' and explain \n"
    "your decision briefly.\n"
    "請在 'Reason:' 行以繁體中文簡短說明（只要一句話即可）。\n"
    "Query and Response: \n {query_str}\n"
    "Context: \n {context_str}\n"
    "Answer: "
)

RELEVANCY_REFINE_TEMPLATE = PromptTemplate(
    "We want to understand if the following query and response is in line with \n"
    "the context information: \n {query_str}\n"
    "We have provided an existing YES/NO answer: \n {existing_answer}\n"
    "We have the opportunity to refine the existing answer (only if needed) with \n"
    "some more context below.\n"
    "------------\n"
    "{context_msg}\n"
    "------------\n"
    "If the existing answer was already YES, still answer YES. If the information \n"
    "is present in the new context, answer YES. Otherwise answer NO.\n"
    "After YES or NO, add a new line starting with 'Reason:' and briefly explain \n"
    "the decision based on the available context.\n"
    "請在 'Reason:' 行以繁體中文簡短說明（只要一句話即可）。\n"
)


class Rag:
    def __init__(
        self,
        webpages_data_folder_path: str = WEBPAGES_DATA_FOLDER_PATH,
    ) -> None:
        self.webpages_data_folder_path = webpages_data_folder_path
        self.md_docs_folder_path = os.path.join(webpages_data_folder_path, "results")
        self.results_json_path = os.path.join(webpages_data_folder_path, "results.json")
        self.results_json: dict[str, Any] = self._load_results_json()

        self.qdrant_client: QdrantClient | None = None
        self.vector_store: QdrantVectorStore | MilvusVectorStore | None = None
        self.index: VectorStoreIndex | None = None
        self.nodes: Sequence[BaseNode] | None = None
        self.retriever: VectorIndexRetriever | None = None
        self.query_engine: RetrieverQueryEngine | None = None
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

        if self.qdrant_client is not None:
            self.qdrant_client.close()

        if isinstance(self.vector_store, MilvusVectorStore):
            try:
                self.vector_store._milvusclient.close()
            except Exception:
                pass

        self.qdrant_client = None
        self.vector_store = None
        self.index = None
        self.retriever = None
        self.query_engine = None

        gc.collect()

    @staticmethod
    def build_filters(
        filter_dict: dict[str, Any] | None,
    ) -> MetadataFilters | None:
        if filter_dict is None:
            return None
        filter_list = []
        for key, entry in filter_dict.items():
            if isinstance(entry, tuple):
                value, operator = entry
            else:
                value, operator = entry, FilterOperator.EQ
            filter_list.append(MetadataFilter(key=key, value=value, operator=operator))
        return MetadataFilters(filters=filter_list)

    @staticmethod
    def create_llm(llm_name: str, usage: str = "query_engine") -> GoogleGenAI | OpenAI:
        for provider, env_vars in LLM_API_KEY_ENV_VARS.items():
            if provider in llm_name:
                api_key = os.getenv(env_vars[usage])
                if provider == "gemini":
                    return GoogleGenAI(model=llm_name, api_key=api_key)
                elif provider == "gpt":
                    return OpenAI(model=llm_name, api_key=api_key)
        raise ValueError(f"Unsupported LLM name: {llm_name}")

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
                self.retriever._filters = self.build_filters(filter_dict)
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

    # TODO: 創建評估器的機制移動到 rag_factory.py
    def evaluate(
        self,
        query: str,
        response: Response,
    ) -> tuple[EvaluationResult, EvaluationResult]:
        llm_name: str = "gpt-5.4"  # gpt-5.4 or gemini-3.1-pro
        llm = self.create_llm(llm_name, "evaluator")
        faithfulness_evaluator = FaithfulnessEvaluator(
            llm=llm,
            eval_template=FAITHFULNESS_EVAL_TEMPLATE,
            refine_template=FAITHFULNESS_REFINE_TEMPLATE,
        )
        faithfulness_result = faithfulness_evaluator.evaluate_response(
            response=response
        )
        self._log_evaluation_result("Faithfulness", faithfulness_result)

        relevancy_evaluator = RelevancyEvaluator(
            llm=llm,
            eval_template=RELEVANCY_EVAL_TEMPLATE,
            refine_template=RELEVANCY_REFINE_TEMPLATE,
        )
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
