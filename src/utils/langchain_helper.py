"""LangChain 輔助函式：Agent 層共用的 ChatModel 建立與訊息處理。

提供：
- create_llm()：建立 LangChain ChatModel（Gemini）
- thread_config()：建立 LangGraph 多輪對話執行設定
- extract_sources_from_messages()：從 messages 解析工具檢索回的來源 URL
- _message_content_to_text()：將 AIMessage content 轉為純文字

注意：create_llm 為 LangChain ChatModel 版（回傳 ChatGoogleGenerativeAI），
與 utils.rag_helper.create_llm（LlamaIndex 版，回傳 GoogleGenAI | OpenAI）對稱。
"""

import os
import re
import uuid
from typing import Any

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# ToolMessage content 中來源 URL 行的格式（見 webpage_retriever._format_retrieval_results）
SOURCE_URL_PATTERN = re.compile(r"URL: (\S+)")


def thread_config(thread_id: str | None) -> dict[str, dict[str, str]]:
    """建立 LangGraph 多輪對話的執行設定（thread_id 區分 session）。

    thread_id 為 None 時自動產生唯一 id（每次呼叫獨立，等同單輪）；
    相同 thread_id 保留對話記憶（M2 多輪）。
    """
    if thread_id is None:
        thread_id = f"auto-{uuid.uuid4().hex[:8]}"
    return {"configurable": {"thread_id": thread_id}}


def create_llm(llm_name: str) -> ChatGoogleGenerativeAI:
    """建立 Agent 使用的 LangChain ChatModel（Gemini）。

    沿用 RAG query LLM 的 API key 環境變數（GEMINI_RAG_QUERY_ENGINE_API_KEY），
    與 utils.rag_helper.create_llm 的 gemini 分支對稱。
    """
    load_dotenv()
    api_key = os.getenv("GEMINI_RAG_QUERY_ENGINE_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_RAG_QUERY_ENGINE_API_KEY is not set. "
            "Please set it in .env before running the agent."
        )
    return ChatGoogleGenerativeAI(model=llm_name, api_key=api_key)


def extract_sources_from_messages(messages: list[Any]) -> list[str]:
    """從 Agent 回傳的 messages 中擷取檢索來源 URL（依出現順序去重）。

    retriever tool 的 ToolMessage content 含 "URL: <url>" 行，
    此函數以正則解析並回傳去重後的 URL 列表。
    """
    sources: list[str] = []
    for message in messages:
        content = getattr(message, "content", "")
        if not isinstance(content, str):
            continue
        for match in SOURCE_URL_PATTERN.finditer(content):
            url = match.group(1)
            if url not in sources:
                sources.append(url)
    return sources


def _message_content_to_text(content: Any) -> str:
    """將 AIMessage content 轉為純文字。

    Gemini 的 content 可能是 list[dict]（含 type/text/extras 等欄位），
    此處串接所有 text 欄位；純字串則原樣回傳。
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(parts)
    return str(content)
