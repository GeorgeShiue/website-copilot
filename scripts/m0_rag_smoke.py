"""RAG retriever tool 的 smoke 驗證腳本（源自 M0 依賴升級驗證）。

確認 webpage_retriever StructuredTool 可正常建立並執行檢索（含資源釋放）。
依賴升級（如 langchain-core / langgraph）後重跑此腳本做回歸檢查。

執行：uv run python scripts/m0_rag_smoke.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from app.tools.webpage_retriever import create_webpage_retriever_tool


def main() -> None:
    tool = create_webpage_retriever_tool(config_name="test")
    try:
        result = tool.invoke({"query": "實驗室的成員有哪些人？", "similarity_top_k": 3})
        assert isinstance(result, str) and len(result) > 0, "檢索結果為空"
        print("SMOKE RESULT (前 500 字元):")
        print(result[:500])
        print("\nSMOKE OK: retriever tool 檢索正常")
    finally:
        # tool.rag 為 create_webpage_retriever_tool 動態綁定的屬性（Pydantic v2 繞過驗證）
        getattr(tool, "rag").close()
        print("SMOKE CLEANUP: rag.close() 已釋放資源")


if __name__ == "__main__":
    main()
