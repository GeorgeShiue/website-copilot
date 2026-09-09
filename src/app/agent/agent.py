"""Agent 層：以 LangGraph create_agent 包裝 webpage retriever 工具。

M1 提供：
- Agent：包裝 CompiledStateGraph 與其綁定資源（tool / run_manager / config / checkpointer）
  - agent.ask()：單輪/多輪問答（thread_id 區分 session），回傳回答與來源 URL
  - agent.astream_text()：串流 model 節點文字 token（CLI 與 M3 server 共用核心）
  - agent.astream_result()：串流問答並收集完整結果（含來源 URL）
  - agent.save_results()：將對話結果落盤（含設定摘要）
- create_agent()：建立 retriever tool → LLM → Agent（LangGraph CompiledStateGraph）

資源生命週期：結束後由呼叫者呼叫 registry.close() 釋放 RAG 資源。
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
from app.workflow.run_manager import RunManager
from utils.langchain_helper import (
    _message_content_to_text,
    create_llm,
    extract_sources_from_messages,
    thread_config,
)

logger = logging.getLogger(__name__)


# TODO: 移除 dataclass，改用普通 class
@dataclass
class Agent:
    """包裝 LangGraph Agent 與其綁定資源。

    Attributes:
        graph: LangGraph CompiledStateGraph（create_agent 回傳）。
        tools: 綁定的 StructuredTool 列表（含 discover + retriever）。
        run_manager: 本次執行的 RunManager（供落盤）。
        config: Agent 設定。
        checkpointer: InMemorySaver 實例（多輪記憶，thread_id 區分 session）。
    """

    graph: Any
    tools: list[StructuredTool]
    run_manager: RunManager
    config: AgentConfig
    checkpointer: InMemorySaver = field(default_factory=InMemorySaver)

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
    config: AgentConfig,
    tools: list[StructuredTool],
    run_manager: RunManager,
) -> Agent:
    """組裝 Agent（資源由呼叫端提供）。

    流程：
    1. 以 AgentConfig.llm_name 建立 ChatModel
    2. 組裝 Agent（LangGraph CompiledStateGraph）

    Args:
        config: Agent 設定。
        tools: 工具列表（至少一個）。
        run_manager: RunManager 實例。

    Returns:
        Agent：包裝 Agent、tools、run_manager 與 config。
    """
    if not tools:
        raise ValueError("create_agent requires at least one tool")

    llm = create_llm(config.llm_name)
    logger.info("Successfully built LLM (llm_name=%s)", config.llm_name)

    checkpointer = InMemorySaver()
    logger.info("Successfully built InMemorySaver for multi-turn conversation")

    graph = langchain_create_agent(
        llm,
        tools,
        system_prompt=config.system_prompt,
        checkpointer=checkpointer,
    )
    logger.info(
        "Successfully built Agent (llm=%s, tools=%s)",
        config.llm_name,
        [t.name for t in tools],
    )

    agent = Agent(
        graph=graph,
        tools=tools,
        run_manager=run_manager,
        config=config,
        checkpointer=checkpointer,
    )

    return agent
