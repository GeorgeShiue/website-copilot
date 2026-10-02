import logging
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

from website_copilot.utils.llm_provider import get_api_key, resolve_provider
from website_copilot.utils.log_helper import log_session, log_source_title

logger = logging.getLogger(__name__)


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


def create_llm(llm_name: str) -> GoogleGenAI | OpenAI:
    """建立 RAG 使用的 llama_index LLM（供應商與 API key 依 model name 決定，見 llm_provider）。"""
    provider = resolve_provider(llm_name)
    api_key = get_api_key(provider)
    if provider.keyword == "gemini":
        return GoogleGenAI(model=llm_name, api_key=api_key)
    return OpenAI(model=llm_name, api_key=api_key)


def extract_sources_info(source_node: NodeWithScore) -> tuple[str, float, str]:
    metadata = getattr(source_node.node, "metadata", None) or {}
    page_title = metadata.get("page_title", "Unknown")
    score = source_node.get_score()
    page_type = metadata.get("page_type", "Unknown")
    return page_title, score, page_type


def source_dict(
    source_node: NodeWithScore, max_content_length: int | None = None
) -> dict[str, Any]:
    """將檢索來源節點序列化為 dict（page_title／score／page_type／url／content）。

    max_content_length 為內容片段最大字元數；None 表示不截斷。
    rag-query 的 results.json（evaluation.extract_sources_list）與 Agent 檢索工具
    （RAG.retrieve）共用。
    """
    page_title, score, page_type = extract_sources_info(source_node)
    content = source_node.node.get_content()
    if max_content_length is not None:
        content = content[:max_content_length]
    return {
        "page_title": page_title,
        "score": score,
        "page_type": page_type,
        "url": source_node.node.metadata.get("page_url", ""),
        "content": content,
    }


def log_source_nodes(source_nodes: Sequence[NodeWithScore]) -> None:
    log_session("Sources", style="blue")
    logger.info(f"Retrieved {len(source_nodes)} sources")
    for source_node in source_nodes:
        page_title, score, page_type = extract_sources_info(source_node)
        log_source_title(page_title, score, page_type)
        raw_content = source_node.node.get_content()
        format_content = truncate_text(raw_content, max_length=500)
        logger.info(format_content)
