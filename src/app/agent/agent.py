"""Agent 層：以 LangGraph create_agent 包裝 webpage retriever 工具。

M1 提供：
- Agent：包裝 CompiledStateGraph 與其綁定資源（Tool / config / checkpointer）
  - agent.ask()：單輪/多輪問答（thread_id 區分 session），回傳回答與來源 URL
  - agent.astream_text()：串流 model 節點文字 token（CLI 與 M3 server 共用核心）
  - agent.astream_result()：串流問答並收集完整結果（含來源 URL）
  - agent.close()：釋放 Tool 管理的資源（RAGRegistry 等）
- create_agent()：建立 Agent（Tool 資源由 Agent 管理生命週期）

資源生命週期：Agent 擁有 Tool 實例，close() 時釋放 Tool 內部資源。
落盤責任不在 Agent：由呼叫端（run_agent_query / run_app / server）自行負責，
agent 層因此不需知道 workflow 層。
"""

import logging
import time
from typing import Any, AsyncIterator, Callable

from langchain.agents import create_agent as langchain_create_agent
from langchain_core.tools import StructuredTool
from langgraph.checkpoint.memory import InMemorySaver

from app.configs.agent_config import AgentConfig
from app.tools.tool import Tool
from utils.langchain_helper import (
    _message_content_to_text,
    create_llm,
    extract_sources_from_messages,
    thread_config,
)

logger = logging.getLogger(__name__)


class Agent:
    """包裝 LangGraph Agent 與其綁定資源。

    Agent 擁有 Tool 實例，負責其生命週期管理。

    Attributes:
        graph: LangGraph CompiledStateGraph（create_agent 回傳）。
        tool: Tool 實例（管理 RAGRegistry 等資源）。
        tools: 綁定的 StructuredTool 列表（向後相容，回傳 tool.tools）。
        config: Agent 設定。
        checkpointer: InMemorySaver 實例（多輪記憶，thread_id 區分 session）。
    """

    def __init__(
        self,
        graph: Any,
        tool: Tool,
        config: AgentConfig,
        checkpointer: InMemorySaver | None = None,
    ) -> None:
        self.graph = graph
        self.tool = tool
        self.config = config
        self.checkpointer = checkpointer or InMemorySaver()

    @property
    def tools(self) -> list[StructuredTool]:
        """向後相容：回傳 Tool 內的 StructuredTool 列表。"""
        return self.tool.tools

    def close(self) -> None:
        """釋放 Tool 管理的資源（RAGRegistry 等）。"""
        self.tool.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

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


def create_agent(
    config_name: str = "default",
    **config_overrides,
) -> Agent:
    """組裝 Agent（Tool 資源由 Agent 管理生命週期）。

    內部建立 AgentConfig 和 Tool，方便 workflow 層直接呼叫。

    流程：
    1. 以 AgentConfig.from_toml() 建立設定
    2. 以 Tool() 建立工具實例
    3. 以 AgentConfig.llm_name 建立 ChatModel
    4. 組裝 Agent（LangGraph CompiledStateGraph）

    Args:
        config_name: AgentConfig 名稱（對應 configs/agent/{name}.toml）。
        **config_overrides: AgentConfig 覆寫值（llm_name / system_prompt）。

    Returns:
        Agent：包裝 Tool 與 config。
    """
    config = AgentConfig.from_toml(config_name, **config_overrides)
    tool = Tool(config_name)
    try:
        if not tool.tools:
            raise ValueError("create_agent requires at least one tool")

        llm = create_llm(config.llm_name)
        logger.info("Successfully built LLM (llm_name=%s)", config.llm_name)

        checkpointer = InMemorySaver()
        logger.info("Successfully built InMemorySaver for multi-turn conversation")

        graph = langchain_create_agent(
            llm,
            tool.tools,  # langchain_create_agent needs list[StructuredTool]
            system_prompt=config.system_prompt,
            checkpointer=checkpointer,
        )
        logger.info(
            "Successfully built Agent (llm=%s, tools=%s)",
            config.llm_name,
            [t.name for t in tool.tools],
        )

        agent = Agent(
            graph=graph,
            tool=tool,
            config=config,
            checkpointer=checkpointer,
        )
    except Exception:
        tool.close()
        raise

    return agent
