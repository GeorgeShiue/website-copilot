import logging
from typing import Any

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from app.tools.rag_registry import RAGRegistry

logger = logging.getLogger(__name__)


class RetrieverInputSchema(BaseModel):
    """Agent 呼叫 retriever 時的輸入 schema。

    LLM 在決定是否呼叫工具時會讀取 Field(description=...) 的內容，
    因此 description 應提供足夠的指引，幫助 LLM 判斷何時使用、如何填寫參數。
    """

    site_id: str = Field(
        description=(
            "目標知識庫的 site_id（如 'nculab'、'ncucsie'）。"
            "可先呼叫 list_knowledge_bases 取得可用站點列表。"
            "若使用者問題來自特定網站，通常已有隱含的 site_id 語境。"
        ),
    )
    query: str = Field(description="搜尋查詢字串，用於檢索網站中的相關網頁內容")
    filter_dict: dict[str, Any] | None = Field(
        default=None,
        description=(
            "可選的 metadata 過濾條件。範例：\n"
            '- {"page_type": "paper"} — 只回傳論文頁面\n'
            '- {"page_type": "paper", "year": (2024, ">=")} — 論文且年份 ≥ 2024\n'
            '- {"page_type": (["paper", "announcement"], "in")} — 論文或公告\n'
            "傳 None 則不過濾。"
        ),
    )
    similarity_top_k: int | None = Field(
        default=None,
        description=(
            "回傳的 top-k 結果數量。預設為 10。"
            "若初次檢索結果不足可調高此值以獲取更廣召回。"
        ),
    )


def create_webpage_retriever_tool(
    registry: RAGRegistry,
) -> StructuredTool:
    """以 RAGRegistry 建立多站 retriever 工具。

    與舊版差異：
    - 不再綁定單一 RAG 實例，改由 registry 依 site_id 延遲載入
    - 不再需要 RunManager / config_name / vector store 隔離
    - RAG 實例生命週期由 registry 管理（LRU 快取 + close）

    Args:
        registry: 多站 RAG 實例管理器。

    Returns:
        StructuredTool: 可直接傳入 create_agent() 的 retriever 工具。
    """

    def _retrieve(
        site_id: str,
        query: str,
        filter_dict: dict[str, Any] | None = None,
        similarity_top_k: int | None = None,
    ) -> str:
        logger.info(
            "Agent tool called: site_id=%s, query=%r, filter_dict=%s, top_k=%s",
            site_id,
            query,
            filter_dict,
            similarity_top_k,
        )
        rag = registry.get(site_id)
        results = rag.retrieve(
            query=query,
            filter_dict=filter_dict,
            similarity_top_k=similarity_top_k,
        )
        return _format_retrieval_results(results)

    tool = StructuredTool(
        name="webpage_retriever",
        description=(
            "檢索指定知識庫中與查詢相關的內容。"
            "必須提供 site_id 參數指定目標知識庫。"
            "可先呼叫 list_knowledge_bases 確認可用的 site_id。"
            "可透過 filter_dict 過濾特定頁面類型"
            '（如 {"page_type": "paper"} 只查論文），'
            "或調整 similarity_top_k 控制回傳數量。"
            "回傳的內容包含原始片段與來源 URL。"
        ),
        args_schema=RetrieverInputSchema,
        func=_retrieve,
    )

    return tool


def _format_retrieval_results(results: list[dict[str, Any]]) -> str:
    """將檢索結果格式化為 Agent 易讀的純文字。

    Args:
        results: retrieve() 回傳的 dict 列表。

    Returns:
        格式化後的純文字字串，每個結果包含標題、分數、類型、URL 與內容片段。
    """
    if not results:
        return "未檢索到相關結果。"

    lines = [f"檢索到 {len(results)} 筆相關結果：\n"]
    for i, result in enumerate(results, 1):
        lines.append(
            f"[{i}] {result['page_title']} "
            f"(score={result['score']:.3f}, type={result['page_type']})"
        )
        lines.append(f"    URL: {result['url']}")
        content = result["content"]
        lines.append(f"    Content: {content}\n")
    formatted_results = "\n".join(lines)

    return formatted_results
