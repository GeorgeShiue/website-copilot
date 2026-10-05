"""RAG 評估（Faithfulness / Relevancy）：Prompt 模板與結果序列化。"""

import logging
from collections.abc import Sequence
from typing import Any

from llama_index.core.base.response.schema import Response
from llama_index.core.evaluation import FaithfulnessEvaluator, RelevancyEvaluator
from llama_index.core.evaluation.base import EvaluationResult
from llama_index.core.prompts import PromptTemplate
from llama_index.core.schema import NodeWithScore

from website_copilot.config.rag_config import RAGConfig
from website_copilot.retrieval.llama_index_helpers import (
    create_llm,
    source_dict,
)
from website_copilot.utils.log_helper import log_session

logger = logging.getLogger(__name__)

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


def extract_sources_list(
    source_nodes: Sequence[NodeWithScore],
    max_content_length: int | None = 800,
) -> list[dict[str, Any]]:
    """將檢索來源節點序列化為可寫入 JSON 的 dict 列表。

    Args:
        source_nodes: 檢索回傳的來源節點。
        max_content_length: 內容片段最大字元數；None 表示不截斷。

    Returns:
        每個 dict 包含 page_title / score / page_type / url / content（見 source_dict），
        與 RAG.retrieve() 的回傳形狀相同。
    """
    return [source_dict(node, max_content_length) for node in source_nodes]


def response_to_dict(
    query: str,
    response: Response,
    faithfulness_result: EvaluationResult | None = None,
    relevancy_result: EvaluationResult | None = None,
    index: int = 1,
    timestamp: str = "",
    max_content_length: int | None = 800,
) -> dict[str, Any]:
    """將單次 query 的回應與評估結果組裝為可寫入 JSON 的 dict。"""
    result: dict[str, Any] = {
        "index": index,
        "timestamp": timestamp,
        "query": query,
        "response": response.response,
        "sources": extract_sources_list(response.source_nodes, max_content_length),
    }
    if faithfulness_result is not None or relevancy_result is not None:
        result["evaluation"] = {
            "faithfulness": (
                _evaluation_result_to_dict(faithfulness_result)
                if faithfulness_result is not None
                else None
            ),
            "relevancy": (
                _evaluation_result_to_dict(relevancy_result)
                if relevancy_result is not None
                else None
            ),
        }
    return result


Evaluators = tuple[FaithfulnessEvaluator, RelevancyEvaluator]


def build_evaluators(config: RAGConfig) -> Evaluators:
    """建立 Faithfulness / Relevancy evaluator。"""
    llm = create_llm(config.query_engine.evaluator_llm_name)
    faithfulness_evaluator = FaithfulnessEvaluator(
        llm=llm,
        eval_template=FAITHFULNESS_EVAL_TEMPLATE,
        refine_template=FAITHFULNESS_REFINE_TEMPLATE,
    )
    relevancy_evaluator = RelevancyEvaluator(
        llm=llm,
        eval_template=RELEVANCY_EVAL_TEMPLATE,
        refine_template=RELEVANCY_REFINE_TEMPLATE,
    )
    logger.info(
        "Successfully built evaluators (llm=%s)",
        config.query_engine.evaluator_llm_name,
    )
    return faithfulness_evaluator, relevancy_evaluator


def evaluate_response(
    evaluators: Evaluators,
    query: str,
    response: Response,
) -> tuple[EvaluationResult, EvaluationResult]:
    """以 Faithfulness / Relevancy evaluator 評估單次回應並記錄結果。"""
    faithfulness_evaluator, relevancy_evaluator = evaluators

    faithfulness_result = faithfulness_evaluator.evaluate_response(response=response)
    _log_evaluation_result("Faithfulness", faithfulness_result)

    relevancy_result = relevancy_evaluator.evaluate_response(
        query=query,
        response=response,
    )
    _log_evaluation_result("Relevancy", relevancy_result)
    return faithfulness_result, relevancy_result


def _log_evaluation_result(
    evaluation_type: str, evaluation_result: EvaluationResult
) -> None:
    log_session(f"{evaluation_type} Result", style="blue")
    logger.info(f"Passing: {evaluation_result.passing}")
    reason = None
    if evaluation_result.feedback:
        reason = evaluation_result.feedback.split("Reason:", 1)[-1].strip()
    logger.info(f"Reason: {reason}")


def _evaluation_result_to_dict(result: EvaluationResult) -> dict[str, Any]:
    """將 EvaluationResult 轉為可寫入 JSON 的 dict。"""
    return {
        "passing": bool(getattr(result, "passing", False)),
        "score": getattr(result, "score", None),
        "feedback": getattr(result, "feedback", None),
    }
