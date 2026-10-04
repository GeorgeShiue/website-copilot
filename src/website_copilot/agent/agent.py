"""Agent 層：以 LangGraph create_agent 包裝 webpage retriever 工具。

M1 提供：
- Agent：包裝 CompiledStateGraph 與其綁定資源（Tool / config / checkpointer）
  - agent.ask()：單輪/多輪問答（thread_id 區分 session），回傳回答與來源 URL
  - agent.astream_text()：串流 model 節點文字 token（CLI 與 M3 server 共用核心）
  - agent.astream_result()：串流問答並收集完整結果（含來源 URL）
  - agent.close()：釋放 Tool 管理的資源（RAGRegistry 等）
- create_agent()：建立 Agent（Tool 資源由 Agent 管理生命週期）

資源生命週期：Agent 擁有 Tool 實例，close() 時釋放 Tool 內部資源。
落盤責任不在 Agent：由呼叫端（run_agent_build / run_agent_query / server）自行負責，
agent 層因此不需知道 workflow 層。
"""

import time
from typing import Any, AsyncIterator, Callable

from langchain.agents import create_agent as langchain_create_agent
from langgraph.checkpoint.memory import InMemorySaver
from rich.table import Table

from website_copilot.agent.langchain_helper import (
    create_llm,
    extract_sources_from_messages,
    message_content_to_text,
    thread_config,
)
from website_copilot.agent.tools.tool import Tool
from website_copilot.config.agent_config import AgentConfig
from website_copilot.utils.log_helper import log_session, print_log


def state_messages(graph: Any, config: dict[str, dict[str, str]]) -> list[Any]:
    """取得 thread 目前的對話 messages（thread 尚無 state 時為空 list）。"""
    state = graph.get_state(config)
    return state.values.get("messages", []) if state.values else []


def build_result(query: str, response: str, messages: list[Any]) -> dict[str, Any]:
    """組出一輪問答結果：query、response、sources（messages 中檢索工具回傳的來源 URL）、timestamp。

    Agent.ask／Agent.astream_result 與 server 的 SSE 串流共用，落盤格式
    （RunManager.save_agent_results_as_json）依賴這四個欄位與順序。
    """
    return {
        "query": query,
        "response": response,
        "sources": extract_sources_from_messages(messages),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }


class Agent:
    """包裝 LangGraph Agent 與其綁定資源。

    Agent 擁有 Tool 實例，負責其生命週期管理。

    Attributes:
        graph: LangGraph CompiledStateGraph（create_agent 回傳）。
        tool: Tool 實例（管理 RAGRegistry 等資源）。
        config: Agent 設定。
        checkpointer: InMemorySaver 實例（多輪記憶，thread_id 區分 session）。
    """

    def __init__(
        self,
        graph: Any,
        tool: Tool,
        config: AgentConfig,
        checkpointer: InMemorySaver,
    ) -> None:
        self.graph = graph
        self.tool = tool
        self.config = config
        self.checkpointer = checkpointer

    def close(self) -> None:
        """釋放 Tool 管理的資源（RAGRegistry 等）。"""
        self.tool.close()

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
        answer = message_content_to_text(final_message.content)
        return build_result(query, answer, messages)

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
                text = message_content_to_text(chunk.content)
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
        messages = state_messages(self.graph, config)
        return build_result(query, "".join(chunks), messages)


def create_agent(config: AgentConfig) -> Agent:
    """組裝 Agent（Tool 資源由 Agent 管理生命週期）。

    config 由呼叫端載入（已套用覆寫值），本函式不再讀取設定檔。

    流程：
    1. 以 Tool(config.config_name) 建立工具實例
    2. 以 AgentConfig.llm_name 建立 ChatModel
    3. 組裝 Agent（LangGraph CompiledStateGraph）

    Args:
        config: 已載入的 AgentConfig。

    Returns:
        Agent：包裝 Tool 與 config。
    """
    tool = Tool(config.config_name)
    try:
        if not tool.tools:
            raise ValueError("create_agent requires at least one tool")

        llm = create_llm(config.llm_name)
        checkpointer = InMemorySaver()
        graph = langchain_create_agent(
            llm,
            tool.tools,  # langchain_create_agent needs list[StructuredTool]
            system_prompt=config.system_prompt,
            checkpointer=checkpointer,
        )

        agent = Agent(
            graph=graph,
            tool=tool,
            config=config,
            checkpointer=checkpointer,
        )

        log_session("Agent Stats", style="green")
        table = Table(show_header=True, header_style="bold green")
        table.add_column("Config", style="green", no_wrap=True)
        table.add_column("Value", style="white")
        table.add_row("LLM", config.llm_name)
        table.add_row("Tools", str([t.name for t in tool.tools]))
        table.add_row("Knowledge bases", str(tool.list_sites()))
        print_log(table)
    except Exception:
        tool.close()
        raise

    return agent
