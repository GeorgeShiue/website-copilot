"""Agent 層：以 LangGraph create_agent 包裝 webpage retriever 工具。

M1 提供：
- Agent：包裝 CompiledStateGraph 與其綁定資源（tool / run_manager / config / checkpointer）
  - agent.ask()：單輪/多輪問答（thread_id 區分 session），回傳回答與來源 URL
  - agent.astream_text()：串流 model 節點文字 token（CLI 與 M3 server 共用核心）
  - agent.astream_result()：串流問答並收集完整結果（含來源 URL）
  - agent.save_results()：將對話結果落盤（含設定摘要）
- create_agent()：建立 retriever tool → LLM → Agent（LangGraph CompiledStateGraph）

資源生命週期：結束後由呼叫者呼叫 agent.close() 釋放 RAG 資源。
"""

import json
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Callable

from langchain.agents import create_agent as langchain_create_agent
from langchain_core.tools import StructuredTool
from langgraph.checkpoint.memory import InMemorySaver

from app.configs.agent_config import AgentConfig
from app.tools.rag_registry import RAGRegistry
from app.tools.site_discovery import create_site_discovery_tool
from app.tools.webpage_retriever import (
    create_webpage_retriever_tool,
)
from app.workflow.data_manager import DataManager
from app.workflow.run_manager import RunManager
from utils.config_helper import log_config, save_module_config_as_toml
from utils.langchain_helper import (
    _message_content_to_text,
    create_llm,
    extract_sources_from_messages,
    thread_config,
)
from utils.log_helper import log_run_time, log_session, save_logging_file

logger = logging.getLogger(__name__)


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

    def ask(self, query: str, thread_id: str | None = None) -> dict[str, Any]:
        """單輪/多輪問答：回傳回答與來源。

        Args:
            query: 使用者問題。
            thread_id: session 識別（None 時每次獨立）。

        Returns:
            dict：含 query、response（文字）、sources（URL 列表）、timestamp。
        """
        config = thread_config(thread_id)
        response = self.graph.invoke({"messages": [("human", query)]}, config=config)
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
        self, query: str, config: dict[str, dict[str, str]]
    ) -> AsyncIterator[str]:
        """依執行設定串流 model 節點的文字 token。"""
        async for chunk, metadata in self.graph.astream(
            {"messages": [("human", query)]},
            config=config,
            stream_mode="messages",
        ):
            if metadata.get("langgraph_node") == "model":
                text = _message_content_to_text(chunk.content)
                if text:
                    yield text

    async def astream_result(
        self,
        query: str,
        thread_id: str | None = None,
        on_token: Callable[[str], None] | None = None,
    ) -> dict[str, Any]:
        """串流問答並收集完整結果。"""
        config = thread_config(thread_id)
        chunks: list[str] = []
        async for text in self.astream_text(query, config):
            chunks.append(text)
            if on_token is not None:
                on_token(text)
        state = self.graph.get_state(config)
        messages = state.values.get("messages", []) if state.values else []
        return {
            "query": query,
            "response": "".join(chunks),
            "sources": extract_sources_from_messages(messages),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def save_results(
        self,
        results: list[dict[str, Any]],
        thread_id: str | None = None,
    ) -> None:
        """將對話結果落盤（含設定摘要）。"""
        if not thread_id:
            return
        run_manager = self.run_manager
        config = self.config
        safe_id = thread_id.replace("/", "_")
        history_filename = f"results_{safe_id}.json"
        history_path = os.path.join(run_manager.run_path, history_filename)
        existing_results: list[dict[str, Any]] = []
        if not os.path.isfile(history_path):
            found = RunManager.find_thread_history_path(
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

        llm = create_llm(config.llm_name)
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
