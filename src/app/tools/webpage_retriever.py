import logging
import os
from typing import Any

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from app.configs.rag_config import RAGConfig
from app.engines.rag import RAG
from app.engines.rag_factory import RAGBuilder
from app.workflow.workflow_manager import RunManager
from utils.config_helper import log_config, save_module_config_as_toml
from utils.log_helper import log_run_time, log_session, save_logging_file

logger = logging.getLogger(__name__)


class RetrieverInputSchema(BaseModel):
    """Agent 呼叫 retriever 時的輸入 schema。

    LLM 在決定是否呼叫工具時會讀取 Field(description=...) 的內容，
    因此 description 應提供足夠的指引，幫助 LLM 判斷何時使用、如何填寫參數。
    """

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
    run_manager: RunManager | None = None,
    config_name: str = "default",
    run_name_use_config_name: bool = False,
    **config_overrides,
) -> StructuredTool:
    """建立 RAG 資源至 retriever 層級，並回傳包裝好的 StructuredTool。

    與 run_rag_build 的差異：
    - 只建到 retriever，不建 query engine
    - 不回傳 None，而是回傳可直接給 Agent 使用的工具
    - 不呼叫 rag.close()（工具需保持活著以回應多次呼叫）

    Args:
        run_manager: 可選的 RunManager 實例（傳 None 時內部自動建立）。
        config_name: RAG config 名稱（對應 configs/rag/{name}.toml）。
        run_name_use_config_name: 是否以 config 名稱為 run name。
        **config_overrides: 可覆寫 config 中的任何欄位。

    Returns:
        StructuredTool: 包裝好的 retriever 工具，可直接傳入 create_agent()。
        tool.rag 已自動綁定 RAG 實例，結束後請透過 tool.rag.close() 釋放資源。

    Notes:
        Vector store 會被隔離至當輪 run 的 results/ 底下
        （如 chats/<ts>/agent/<config>/results/），避免工具建構時
        覆寫正式向量庫（data/rag/results/）。
    """
    # ----- 初始化設定和路徑 -----
    config = RAGConfig.from_toml(config_name, **config_overrides)
    if run_manager is None:
        run_manager = RunManager("webpage_retriever_tool")
    if run_name_use_config_name:
        run_manager.set_run_path(config_name)
    else:
        run_manager.set_run_path(config.run_name)
    run_manager.init_module_run_paths()

    # 隔離 vector store 至當輪 run 的 results/（chats/<ts>/agent/<config>/results/），
    # 避免 build_to_retriever 重建時覆寫正式向量庫 data/rag/results/
    config.milvus_uri = os.path.join(run_manager.results_folder_path, "milvus.db")
    config.qdrant_db_folder_path = os.path.join(
        run_manager.results_folder_path, "qdrant_db"
    )

    run_title = f"Webpage Retriever Tool ({config_name})"
    with (
        save_logging_file(run_manager.log_path),
        log_run_time(run_title),
    ):
        # ----- 輸出開始訊息 -----
        log_session(run_title, style="purple")
        log_config("RAG Config Loaded from toml", config)

        # ----- 使用 RAGBuilder 一鍵建構到 retriever 層級 -----
        log_session("Building Retriever Tool", style="cyan")
        rag = RAGBuilder(config).build_to_retriever()

        # ----- 包裝為工具並回傳 -----
        # 完成宣告由 log_run_time 的 "Completed in ..." 承擔
        tool = _webpage_retriever_to_tool(rag)

        # ----- 儲存設定 -----
        save_module_config_as_toml(config, run_manager.module_config_toml_path)

        # ---- 輸出完成訊息 -----
        log_session("Webpage Retriever Tool Ready", style="green")

    return tool


def _webpage_retriever_to_tool(rag: RAG) -> StructuredTool:
    """將 webpage retriever 包裝為 LangChain StructuredTool。

    Args:
        rag: 已初始化至 retriever 層級的 RAG 實例
            （需已完成 build_nodes → build_vector_store → build_index → build_retriever）。

    Returns:
        StructuredTool: 可直接傳入 create_agent()、ToolNode 或
            create_react_agent() 的工具實例。name 為 "webpage_retriever"。
    """

    def _retrieve(
        query: str,
        filter_dict: dict[str, Any] | None = None,
        similarity_top_k: int | None = None,
    ) -> str:
        logger.info(
            f"Agent tool called: query={query!r}, "
            f"filter_dict={filter_dict}, top_k={similarity_top_k}"
        )
        results = rag.retrieve(
            query=query,
            filter_dict=filter_dict,
            similarity_top_k=similarity_top_k,
        )
        formatted_results = _format_retrieval_results(results)

        return formatted_results

    tool = StructuredTool(
        name="webpage_retriever",
        description=(
            "檢索網站網頁中與查詢相關的內容。"
            "可透過 filter_dict 過濾特定頁面類型"
            '（如 {"page_type": "paper"} 只查論文），'
            "或調整 similarity_top_k 控制回傳數量。"
            "回傳的內容包含原始片段與來源 URL。"
        ),
        args_schema=RetrieverInputSchema,
        func=_retrieve,
    )

    # 將 RAG 實例綁定為工具屬性，讓外部呼叫者可在 Agent 結束後釋放資源
    # 使用方式: tool.rag.close()
    # StructuredTool 為 Pydantic v2 模型，須繞過 __setattr__ 以動態綁定
    object.__setattr__(tool, "rag", rag)

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
