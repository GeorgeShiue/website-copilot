from langchain_core.tools import StructuredTool

from app.tools.rag_registry import RAGRegistry
from app.tools.site_discovery import create_site_discovery_tool
from app.tools.webpage_retriever import create_webpage_retriever_tool


# TODO: 將此 method 和 RAGRegistry 整合成一個 Tool class
def create_tool(
    registry: RAGRegistry,
) -> list[StructuredTool]:
    """建立 Agent 所需的工具層。

    流程：接收外部 registry → 建立 discovery_tool + retriever_tool → 回傳 tools

    Args:
        registry: RAGRegistry 實例（由呼叫方建立並管理生命週期）。

    Returns:
        工具列表。
    """
    discovery_tool = create_site_discovery_tool(registry)
    retriever_tool = create_webpage_retriever_tool(registry)

    return [discovery_tool, retriever_tool]
