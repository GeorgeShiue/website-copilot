"""Agent 層：以 LangGraph create_agent 包裝 webpage retriever 工具。

M1 提供：
- RAGAgent：包裝 CompiledStateGraph 與其綁定資源（tool / run_manager / config / checkpointer）
- create_rag_agent()：建立 retriever tool → LLM → Agent（LangGraph CompiledStateGraph）
- ask_agent()：單輪/多輪問答（thread_id 區分 session），回傳回答與來源 URL
- astream_text()：串流 model 節點文字 token 的公開核心（CLI 與 M3 server 共用）
- astream_agent_result()：串流問答並收集完整結果（含來源 URL；CLI 與 M3 server 共用）
- extract_sources_from_messages()：從 messages 解析工具檢索回的來源 URL

資源生命週期：結束後由呼叫者呼叫 agent.close() 釋放 RAG 資源。
"""

import logging
import os
import re
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Callable

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver

from app.configs.agent_config import AgentConfig
from app.tools.webpage_retriever import (
    create_webpage_retriever_tool,
)
from app.workflow.workflow_manager import RunManager
from utils.config_helper import log_config, save_module_config_as_toml
from utils.log_helper import log_run_time, log_session, save_logging_file

logger = logging.getLogger(__name__)

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


@dataclass
class RAGAgent:
    """包裝 LangGraph Agent 與其綁定資源。

    Attributes:
        graph: LangGraph CompiledStateGraph（create_agent 回傳）。
        tool: 綁定的 retriever StructuredTool（含動態綁定的 .rag 資源）。
        run_manager: 本次執行的 RunManager（供落盤）。
        config: Agent 設定。
        checkpointer: InMemorySaver 實例（多輪記憶，thread_id 區分 session）。
    """

    graph: Any
    tool: Any
    run_manager: RunManager
    config: AgentConfig
    checkpointer: InMemorySaver = field(default_factory=InMemorySaver)

    def close(self) -> None:
        """釋放 RAG 資源（tool.rag.close()）。"""
        getattr(self.tool, "rag").close()


def create_agent_llm(llm_name: str) -> ChatGoogleGenerativeAI:
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


def create_rag_agent(
    config: AgentConfig | None = None,
    run_manager: RunManager | None = None,
) -> RAGAgent:
    """建立綁定 webpage_retriever 工具的 LangGraph Agent。

    建立流程：
    1. 初始化 RunManager（module="agent"）與落盤路徑
    2. 以 RAG config（test）建立 retriever tool（RAG 資源，檢索參數由 RAG 層管理）
    3. 以 AgentConfig.llm_name 建立 ChatModel
    4. create_agent 組裝並包裝為 RAGAgent

    Args:
        config: Agent 設定（None 時使用預設）。
        run_manager: 可選的 RunManager（傳 None 時內部自動建立）。

    Returns:
        RAGAgent：包裝 Agent、tool、run_manager 與 config。
        結束後呼叫 agent.close() 釋放 RAG 資源。
    """
    if config is None:
        # 與其他模組一致：預設由 configs/agent/default.toml 載入
        config = AgentConfig.from_toml()

    if run_manager is None:
        # 聊天記錄與實驗分離：預設落盤至 chats/（RunManager base_folder 參數化）
        run_manager = RunManager("agent", base_folder="chats")
    run_manager.set_run_path(config.config_name)
    run_manager.init_module_run_paths()
    run_title = f"RAG Agent ({config.config_name})"

    with (
        save_logging_file(run_manager.log_path),
        log_run_time(run_title),
    ):
        # ----- 建立 retriever tool（綁定 RAG 資源） -----
        # run_name_use_config_name：讓 tool 的 run path 與 Agent 一致（runs/<ts>/agent/<config_name>/）
        # similarity_top_k 等檢索參數沿用 RAG config 預設，Agent 不覆寫
        tool = create_webpage_retriever_tool(
            run_manager=run_manager,
            config_name="default",
            run_name_use_config_name=True,
        )

        # ----- 輸出開始訊息 -----
        log_session(run_title, style="purple")
        log_config("Agent Config Loaded from toml", config)

        # ----- 建立 LLM 與 Agent -----
        log_session("Building Agent", style="cyan")

        llm = create_agent_llm(config.llm_name)
        logger.info("Successfully built LLM (llm_name=%s)", config.llm_name)

        # InMemorySaver：多輪對話記憶（M2），以 thread_id 區分 session
        checkpointer = InMemorySaver()
        logger.info("Successfully built InMemorySaver for multi-turn conversation")

        graph = create_agent(
            llm,
            [tool],
            system_prompt=config.system_prompt,
            checkpointer=checkpointer,
        )
        logger.info(
            f"Successfully built Agent (llm={config.llm_name}, tools=[webpage_retriever]"
        )

        # ----- 儲存設定 -----
        save_module_config_as_toml(config, run_manager.module_config_toml_path)
        log_session("Run Paths", style="cyan")
        run_manager.log_run_paths("init")

        # ----- 輸出完成訊息 -----
        log_session("Agent Ready", style="green")

    return RAGAgent(
        graph=graph,
        tool=tool,
        run_manager=run_manager,
        config=config,
        checkpointer=checkpointer,
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


def ask_agent(
    agent: RAGAgent,
    query: str,
    thread_id: str | None = None,
) -> dict[str, Any]:
    """單輪/多輪問答：呼叫 Agent 並回傳回答與來源。

    Args:
        agent: create_rag_agent() 回傳的 RAGAgent。
        query: 使用者問題。
        thread_id: session 識別（None 時每次獨立；相同 thread_id 保留對話記憶，M2）。

    Returns:
        dict：含 query、response（文字）、sources（URL 列表）、timestamp。
    """
    config = thread_config(thread_id)
    response = agent.graph.invoke({"messages": [("human", query)]}, config=config)
    messages = response["messages"]

    final_message = messages[-1]
    answer = _message_content_to_text(final_message.content)

    return {
        "query": query,
        "response": answer,
        "sources": extract_sources_from_messages(messages),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }


async def astream_text(
    agent: RAGAgent,
    query: str,
    config: dict[str, dict[str, str]],
) -> AsyncIterator[str]:
    """依執行設定串流 model 節點的文字 token（CLI 與 M3 server 共用核心）。

    只輸出 model 節點的 token（跳過工具呼叫與其他節點）；
    Gemini content 可能是 list[dict]，統一轉純文字。
    """
    async for chunk, metadata in agent.graph.astream(
        {"messages": [("human", query)]},
        config=config,
        stream_mode="messages",
    ):
        if metadata.get("langgraph_node") == "model":
            text = _message_content_to_text(chunk.content)
            if text:
                yield text


async def astream_agent_result(
    agent: RAGAgent,
    query: str,
    thread_id: str | None = None,
    on_token: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    """串流問答並收集完整結果（CLI 與 M3 server 共用）。

    以 astream_text 逐 token 串流輸出；完成後從 graph state
    （InMemorySaver）讀回 messages 擷取來源 URL，補齊 M2 已知限制
    「串流模式 sources 為空」。

    Args:
        agent: create_rag_agent() 回傳的 RAGAgent。
        query: 使用者問題。
        thread_id: session 識別（None 時每次獨立；相同 thread_id 保留對話記憶）。
        on_token: 可選的逐 token 回呼（如 CLI 即時列印）。

    Returns:
        dict：含 query、response（回答全文）、sources（URL 列表）、timestamp。
    """
    config = thread_config(thread_id)
    chunks: list[str] = []
    async for text in astream_text(agent, query, config):
        chunks.append(text)
        if on_token is not None:
            on_token(text)

    state = agent.graph.get_state(config)
    messages = state.values.get("messages", []) if state.values else []
    return {
        "query": query,
        "response": "".join(chunks),
        "sources": extract_sources_from_messages(messages),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }


def save_conversation_results(
    agent: RAGAgent,
    results: list[dict[str, Any]],
) -> None:
    """將對話結果落盤為 results.json（含設定摘要）。

    Args:
        agent: create_rag_agent() 回傳的 RAGAgent。
        results: ask_agent() 回傳的 dict 列表。
    """
    run_manager = agent.run_manager
    config = agent.config

    results_dict = {
        "config": {
            "config_name": config.config_name,
            "run_name": run_manager.run_name,
            "llm_name": config.llm_name,
            "system_prompt": config.system_prompt,
        },
        "results": results,
    }
    run_manager.save_results_as_json(results_dict)
