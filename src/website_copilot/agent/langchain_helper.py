"""LangChain 輔助函式：Agent 層共用的 ChatModel 建立與訊息處理。

提供：
- create_llm()：建立 LangChain ChatModel（Gemini 或 OpenAI，依 model name 自動路由）
- new_thread_id()：產生自動編號的 thread_id（auto-{uuid}）
- thread_config()：建立 LangGraph 多輪對話執行設定
- extract_sources_from_messages()：從 messages 解析工具檢索回的來源 URL
- _message_content_to_text()：將 AIMessage content 轉為純文字

注意：create_llm 為 LangChain ChatModel 版（回傳 ChatGoogleGenerativeAI | ChatOpenAI），
與 retrieval.llama_index_helpers.create_llm（LlamaIndex 版，回傳 GoogleGenAI | OpenAI）對稱。
"""

import re
import uuid
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from website_copilot.utils.llm_provider import get_api_key, resolve_provider

# ToolMessage content 中來源 URL 行的格式（見 webpage_retriever._format_retrieval_results）
SOURCE_URL_PATTERN = re.compile(r"URL: (\S+)")


def new_thread_id() -> str:
    """產生自動編號的 thread_id（auto-{uuid 前 8 碼}）。"""
    return f"auto-{uuid.uuid4().hex[:8]}"


def thread_config(thread_id: str | None) -> dict[str, dict[str, str]]:
    """建立 LangGraph 多輪對話的執行設定（thread_id 區分 session）。

    thread_id 為 None 時自動產生唯一 id（每次呼叫獨立，等同單輪）；
    相同 thread_id 保留對話記憶（M2 多輪）。
    """
    if thread_id is None:
        thread_id = new_thread_id()
    return {"configurable": {"thread_id": thread_id}}


def create_llm(llm_name: str) -> ChatGoogleGenerativeAI | ChatOpenAI:
    """建立 Agent 使用的 LangChain ChatModel（Gemini 或 OpenAI，依 model name 自動路由）。

    供應商與 API key 由 utils.llm_provider 決定（不分大小寫；無法判斷供應商或
    未設定 API key 時報錯），與 retrieval.llama_index_helpers.create_llm 共用。
    """
    provider = resolve_provider(llm_name)
    api_key = get_api_key(provider)
    if provider.keyword == "gemini":
        return ChatGoogleGenerativeAI(model=llm_name, api_key=api_key)
    return ChatOpenAI(
        model=llm_name, api_key=SecretStr(api_key), use_responses_api=True
    )


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

    Gemini / OpenAI 的 content 可能是 list[dict]（含 type/text/extras 等欄位），
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
