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
from langchain_core.tools import StructuredTool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import BaseModel

from app.configs.agent_config import AgentConfig
from app.tools.rag_registry import RAGRegistry
from app.tools.webpage_retriever import (
    create_webpage_retriever_tool,
)
from app.workflow.data_manager import DataManager
from app.workflow.run_manager import RunManager
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
        tools: 綁定的 StructuredTool 列表（含 discover + retriever）。
        run_manager: 本次執行的 RunManager（供落盤）。
        config: Agent 設定。
        checkpointer: InMemorySaver 實例（多輪記憶，thread_id 區分 session）。
        registry: 多站 RAG 實例管理器（M3）。
    """

    graph: Any
    tools: list[StructuredTool]
    run_manager: RunManager
    config: AgentConfig
    checkpointer: InMemorySaver = field(default_factory=InMemorySaver)
    registry: RAGRegistry | None = None

    def close(self) -> None:
        """釋放 RAG 資源（registry.close()）。"""
        if self.registry is not None:
            self.registry.close()


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


class _DiscoveryInputSchema(BaseModel):
    """list_knowledge_bases 工具的輸入 schema（無參數）。"""


def create_site_discovery_tool(registry: RAGRegistry) -> StructuredTool:
    """建立 list_knowledge_bases 工具。

    掃描 data/webpages/ 回傳所有可用 site_id，供 LLM 在呼叫 webpage_retriever 前確認站點。
    """

    def _list_sites() -> str:
        sites = registry.list_sites()
        if not sites:
            return "目前沒有可用的知識庫。"
        return "可用的知識庫：" + "、".join(sites)

    return StructuredTool(
        name="list_knowledge_bases",
        description=(
            "列出所有可用的知識庫站點。"
            "在呼叫 webpage_retriever 前應先確認可用的 site_id。"
        ),
        args_schema=_DiscoveryInputSchema,
        func=_list_sites,
    )


def create_rag_agent(
    config: AgentConfig | None = None,
    run_manager: RunManager | None = None,
) -> RAGAgent:
    """建立綁定多站 retriever 工具的 LangGraph Agent。

    建立流程：
    1. 初始化 RunManager（module="agent"）與落盤路徑
    2. 建立 RAGRegistry（多站 RAG 實例管理）
    3. 建立 list_knowledge_bases + webpage_retriever 兩個工具
    4. 以 AgentConfig.llm_name 建立 ChatModel
    5. create_agent 組裝並包裝為 RAGAgent

    Args:
        config: Agent 設定（None 時使用預設）。
        run_manager: 可選的 RunManager（傳 None 時內部自動建立）。

    Returns:
        RAGAgent：包裝 Agent、tools、run_manager、registry 與 config。
        結束後呼叫 agent.close() 釋放 RAG 資源。
    """
    if config is None:
        config = AgentConfig.from_toml("default")

    if run_manager is None:
        run_manager = RunManager.for_run_no_site(
            module="agent",
            run_name=config.config_name,
            base_folder="chats",
        )
    run_title = f"RAG Agent ({config.config_name})"

    with (
        save_logging_file(run_manager.log_path),
        log_run_time(run_title),
    ):
        # ----- 建立多站 RAG Registry -----
        registry = RAGRegistry(DataManager())

        # ----- 建立工具（discover + retriever） -----
        discovery_tool = create_site_discovery_tool(registry)
        retriever_tool = create_webpage_retriever_tool(registry)

        # ----- 輸出開始訊息 -----
        log_session(run_title, style="purple")
        log_config("Agent Config Loaded from toml", config)

        # ----- 建立 LLM 與 Agent -----
        log_session("Building Agent", style="cyan")

        llm = create_agent_llm(config.llm_name)
        logger.info("Successfully built LLM (llm_name=%s)", config.llm_name)

        checkpointer = InMemorySaver()
        logger.info("Successfully built InMemorySaver for multi-turn conversation")

        graph = create_agent(
            llm,
            [discovery_tool, retriever_tool],
            system_prompt=config.system_prompt,
            checkpointer=checkpointer,
        )
        logger.info(
            "Successfully built Agent (llm=%s, tools=[list_knowledge_bases, "
            "webpage_retriever])",
            config.llm_name,
        )

        # ----- 儲存設定 -----
        save_module_config_as_toml(config, run_manager.module_config_toml_path)
        log_session("Run Paths", style="cyan")
        run_manager.log_run_paths("init")

        # ----- 輸出完成訊息 -----
        log_session("Agent Ready", style="green")

    return RAGAgent(
        graph=graph,
        tools=[discovery_tool, retriever_tool],
        run_manager=run_manager,
        config=config,
        checkpointer=checkpointer,
        registry=registry,
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
    thread_id: str | None = None,
) -> None:
    """將對話結果落盤（含設定摘要）。

    Args:
        agent: create_rag_agent() 回傳的 RAGAgent。
        results: ask_agent() 回傳的 dict 列表。
        thread_id: 提供時另以 results_<thread_id>.json 分檔保留對話歷史
            （results.json 仍維持最新一輪，向後相容）。
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
    if thread_id:
        # 檔名安全化：thread_id 為 auto-{uuid}（無特殊字元），仍以防萬一置換
        safe_id = thread_id.replace("/", "_")
        run_manager.save_results_as_json(
            results_dict,
            file_path=os.path.join(run_manager.run_path, f"results_{safe_id}.json"),
        )
