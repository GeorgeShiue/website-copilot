"""Agent 層：以 LangGraph create_agent 包裝 webpage retriever 工具。

M1 提供：
- Agent：包裝 CompiledStateGraph 與其綁定資源（tool / run_manager / config / checkpointer）
- create_agent()：建立 retriever tool → LLM → Agent（LangGraph CompiledStateGraph）
- ask_agent()：單輪/多輪問答（thread_id 區分 session），回傳回答與來源 URL
- astream_text()：串流 model 節點文字 token 的公開核心（CLI 與 M3 server 共用）
- astream_agent_result()：串流問答並收集完整結果（含來源 URL；CLI 與 M3 server 共用）
- extract_sources_from_messages()：從 messages 解析工具檢索回的來源 URL

資源生命週期：結束後由呼叫者呼叫 agent.close() 釋放 RAG 資源。
"""

import json
import logging
import os
import re
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Callable

from dotenv import load_dotenv
from langchain.agents import create_agent as langchain_create_agent
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
class Agent:
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


def create_agent(
    config: AgentConfig | None = None,
    run_manager: RunManager | None = None,
) -> Agent:
    """建立綁定多站 retriever 工具的 LangGraph Agent。

    建立流程：
    1. 初始化 RunManager（module="agent"）與落盤路徑
    2. 建立 RAGRegistry（多站 RAG 實例管理）
    3. 建立 list_knowledge_bases + webpage_retriever 兩個工具
    4. 以 AgentConfig.llm_name 建立 ChatModel
    5. create_agent 組裝並包裝為 Agent

    Args:
        config: Agent 設定（None 時使用預設）。
        run_manager: 可選的 RunManager（傳 None 時內部自動建立）。

    Returns:
        Agent：包裝 Agent、tools、run_manager、registry 與 config。
        結束後呼叫 agent.close() 釋放 RAG 資源。
    """
    if config is None:
        config = AgentConfig.from_toml("default")

    if run_manager is None:
        run_manager = RunManager.for_run_no_site(
            module="agent",
            run_name=config.config_name,
            base_folder="runs",
        )
    run_title = f"Agent ({config.config_name})"

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

        graph = langchain_create_agent(
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

    return Agent(
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
    agent: Agent,
    query: str,
    thread_id: str | None = None,
) -> dict[str, Any]:
    """單輪/多輪問答：呼叫 Agent 並回傳回答與來源。

    Args:
        agent: create_agent() 回傳的 Agent。
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
    agent: Agent,
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
    agent: Agent,
    query: str,
    thread_id: str | None = None,
    on_token: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    """串流問答並收集完整結果（CLI 與 M3 server 共用）。

    以 astream_text 逐 token 串流輸出；完成後從 graph state
    （InMemorySaver）讀回 messages 擷取來源 URL，補齊 M2 已知限制
    「串流模式 sources 為空」。

    Args:
        agent: create_agent() 回傳的 Agent。
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


def _find_thread_history_path(
    base_folder: str,
    module_name: str,
    history_filename: str,
) -> str | None:
    """跨 run 目錄搜尋 thread 歷史檔（結果為最新時間戳的那份）。

    CLI 每次執行建立新的 timestamped run 目錄，但 thread 歷史需跨 run 累積。
    從 base_folder 下所有 timestamped 子目錄搜尋符合的歷史檔，
    回傳時間戳最新（lexicographically last）的那一個完整路徑；找不到回傳 None。

    Args:
        base_folder: runs/ 或 chats/ 根目錄。
        module_name: 模組名稱（如 "agent"）。
        history_filename: 要搜尋的檔名（如 "results_auto-87d6ce91.json"）。
    """
    if not os.path.isdir(base_folder):
        return None

    latest_path: str | None = None
    for entry in sorted(os.listdir(base_folder), reverse=True):
        entry_path = os.path.join(base_folder, entry)
        if not os.path.isdir(entry_path):
            continue
        # timestamped folder: 20260830_172330 (15 chars, starts with 20)
        if not (entry.startswith("20") and len(entry) == 15):
            continue
        module_path = os.path.join(entry_path, module_name)
        if not os.path.isdir(module_path):
            continue
        # recursively search for the history file
        for root, _dirs, files in os.walk(module_path):
            if history_filename in files:
                candidate = os.path.join(root, history_filename)
                if latest_path is None or candidate > latest_path:
                    latest_path = candidate
        if latest_path is not None:
            break  # already got the latest timestamp
    return latest_path


def save_conversation_results(
    agent: Agent,
    results: list[dict[str, Any]],
    thread_id: str | None = None,
) -> None:
    """將對話結果落盤（含設定摘要）。

    Args:
        agent: create_agent() 回傳的 Agent。
        results: ask_agent() 回傳的 dict 列表。
        thread_id: session 識別（必填）；提供時以 results_<thread_id>.json 分檔
            保留完整多輪對話歷史。None 時不落盤。
    """
    if not thread_id:
        return

    run_manager = agent.run_manager
    config = agent.config

    # 讀取既有歷史（如有）
    safe_id = thread_id.replace("/", "_")
    history_filename = f"results_{safe_id}.json"
    history_path = os.path.join(run_manager.run_path, history_filename)
    existing_results: list[dict[str, Any]] = []

    # 若當前 run 目錄無歷史檔，跨 run 目錄搜尋（CLI 多輪累積場景）
    if not os.path.isfile(history_path):
        found = _find_thread_history_path(
            run_manager.base_folder,
            run_manager.module_name,
            history_filename,
        )
        if found:
            history_path = found

    if os.path.isfile(history_path):
        try:
            with open(history_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
                existing_results = existing.get("results", [])
        except (json.JSONDecodeError, OSError):
            existing_results = []

    # 追加新輪
    existing_results.extend(results)

    results_dict = {
        "config": {
            "config_name": config.config_name,
            "run_name": run_manager.run_name,
            "llm_name": config.llm_name,
            "system_prompt": config.system_prompt,
        },
        "results": existing_results,
    }
    run_manager.save_results_as_json(results_dict, file_path=history_path)
