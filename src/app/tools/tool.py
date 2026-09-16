from langchain_core.tools import StructuredTool

from app.tools.rag_registry import RAGRegistry
from app.tools.site_discovery import create_site_discovery_tool
from app.tools.webpage_retriever import create_webpage_retriever_tool


class Tool:
    """Agent 工具層：自行建立並管理 RAGRegistry。"""

    def __init__(self, config_name: str = "default") -> None:
        self._registry = RAGRegistry(config_name=config_name)
        site_discovery_tool = create_site_discovery_tool(self._registry)
        webpage_retriever_tool = create_webpage_retriever_tool(self._registry)
        self.tools: list[StructuredTool] = [
            site_discovery_tool,
            webpage_retriever_tool,
        ]

    def close(self) -> None:
        """釋放內部 RAGRegistry 資源。"""
        self._registry.close()

    def __enter__(self):
        """進入 context manager，回傳 self。"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """離開 context manager，釋放資源。"""
        self.close()
