import logging
import os
from typing import Any, Sequence

from llama_index.core.schema import NodeWithScore
from llama_index.core.utils import truncate_text
from llama_index.core.vector_stores import (
    FilterOperator,
    MetadataFilter,
    MetadataFilters,
)
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.llms.openai import OpenAI

from website_copilot.utils.log_helper import log_session, log_source_title

logger = logging.getLogger(__name__)

LLM_API_KEY_ENV_VARS: dict[str, dict[str, str]] = {
    "gemini": {
        "query_engine": "GEMINI_RAG_QUERY_ENGINE_API_KEY",
        "evaluator": "GEMINI_RAG_EVALUATOR_API_KEY",
    },
    "gpt": {
        "query_engine": "OPENAI_API_KEY",
        "evaluator": "OPENAI_API_KEY",
    },
}


def build_filters(filter_dict: dict[str, Any] | None) -> MetadataFilters | None:
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


def create_llm(llm_name: str, usage: str = "query_engine") -> GoogleGenAI | OpenAI:
    for provider, env_vars in LLM_API_KEY_ENV_VARS.items():
        if provider in llm_name:
            api_key = os.getenv(env_vars[usage])
            if provider == "gemini":
                return GoogleGenAI(model=llm_name, api_key=api_key)
            elif provider == "gpt":
                return OpenAI(model=llm_name, api_key=api_key)
    raise ValueError(f"Unsupported LLM name: {llm_name}")


def extract_sources_info(source_node: NodeWithScore) -> tuple[str, float, str]:
    metadata = getattr(source_node.node, "metadata", None) or {}
    page_title = metadata.get("page_title", "Unknown")
    score = source_node.get_score()
    page_type = metadata.get("page_type", "Unknown")
    return page_title, score, page_type


def log_source_nodes(source_nodes: Sequence[NodeWithScore]) -> None:
    log_session("Sources", style="blue")
    logger.info(f"Retrieved {len(source_nodes)} sources")
    for source_node in source_nodes:
        page_title, score, page_type = extract_sources_info(source_node)
        log_source_title(page_title, score, page_type)
        raw_content = source_node.node.get_content()
        format_content = truncate_text(raw_content, max_length=500)
        logger.info(format_content)
