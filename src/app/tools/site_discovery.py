"""Site Discovery 工具：list_knowledge_bases（供 LLM 確認可用站點）。

掃描 data/webpages/ 回傳所有可用 site_id，供 LLM 在呼叫 webpage_retriever 前確認站點。
"""

from langchain_core.tools import StructuredTool
from pydantic import BaseModel

from app.tools.rag_registry import RAGRegistry


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
