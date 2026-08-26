"""多站 RAG 工具整合測試（mock registry，驗證工具串接邏輯）。

涵蓋：
- webpage_retriever 工具：schema 驗證、tool 建立、retrieve 路由
- list_knowledge_bases 工具：格式化輸出、空站點處理
- RAGAgent dataclass：tools / registry / close 行為
- 端到端流程：mock graph 模擬 Agent 呼叫工具的完整流程

不觸發真實 LLM / Milvus；所有 RAG 實例以 mock 替代。
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest
from langchain_core.tools import StructuredTool

from app.agent.agent import (
    RAGAgent,
    create_site_discovery_tool,
)
from app.tools.rag_registry import RAGRegistry
from app.tools.webpage_retriever import (
    RetrieverInputSchema,
    _format_retrieval_results,
    create_webpage_retriever_tool,
)

# ---------- Helpers ----------


def _make_mock_registry(
    existing_sites: list[str] | None = None,
) -> MagicMock:
    """建立 mock RAGRegistry。"""
    registry = MagicMock(spec=RAGRegistry)
    registry.list_sites.return_value = existing_sites or []
    return registry


def _make_fake_retrieval_results(n: int = 2) -> list[dict[str, Any]]:
    """建立假的檢索結果。"""
    return [
        {
            "page_title": f"Page_{i}",
            "score": 0.9 - i * 0.1,
            "page_type": "paper" if i % 2 == 0 else "general",
            "url": f"https://example.com/page_{i}",
            "content": f"Content of page {i}",
        }
        for i in range(1, n + 1)
    ]


# ---------- RetrieverInputSchema ----------


class TestRetrieverInputSchema:
    """RetrieverInputSchema 欄位驗證。"""

    def test_has_site_id_field(self) -> None:
        """schema 包含必要的 site_id 欄位。"""
        fields = list(RetrieverInputSchema.model_fields.keys())
        assert "site_id" in fields
        assert "query" in fields
        assert "filter_dict" in fields
        assert "similarity_top_k" in fields

    def test_site_id_is_required(self) -> None:
        """site_id 為必要欄位，缺少時 Pydantic 拒絕。"""
        with pytest.raises(Exception):
            RetrieverInputSchema(query="test")  # type: ignore[call-arg]

    def test_valid_construction(self) -> None:
        """提供 site_id + query 可正常建立。"""
        schema = RetrieverInputSchema(site_id="nculab", query="成員")
        assert schema.site_id == "nculab"
        assert schema.query == "成員"
        assert schema.filter_dict is None
        assert schema.similarity_top_k is None

    def test_optional_fields_defaults(self) -> None:
        """filter_dict 與 similarity_top_k 預設為 None。"""
        schema = RetrieverInputSchema(site_id="x", query="y")
        assert schema.filter_dict is None
        assert schema.similarity_top_k is None


# ---------- create_webpage_retriever_tool ----------


class TestCreateWebpageRetrieverTool:
    """create_webpage_retriever_tool 工廠函數。"""

    def test_returns_structured_tool(self) -> None:
        """回傳 StructuredTool 實例。"""
        registry = _make_mock_registry()
        tool = create_webpage_retriever_tool(registry)
        assert isinstance(tool, StructuredTool)

    def test_tool_name(self) -> None:
        """工具名稱為 webpage_retriever。"""
        registry = _make_mock_registry()
        tool = create_webpage_retriever_tool(registry)
        assert tool.name == "webpage_retriever"

    def test_tool_description_mentions_site_id(self) -> None:
        """工具描述提及 site_id。"""
        registry = _make_mock_registry()
        tool = create_webpage_retriever_tool(registry)
        assert "site_id" in tool.description

    def test_tool_description_mentions_list_knowledge_bases(self) -> None:
        """工具描述提及 list_knowledge_bases。"""
        registry = _make_mock_registry()
        tool = create_webpage_retriever_tool(registry)
        assert "list_knowledge_bases" in tool.description

    def test_tool_has_correct_args_schema(self) -> None:
        """工具使用 RetrieverInputSchema。"""
        registry = _make_mock_registry()
        tool = create_webpage_retriever_tool(registry)
        assert tool.args_schema is RetrieverInputSchema


# ---------- retrieve routing ----------


class TestRetrieveRouting:
    """webpage_retriever 工具的 site_id 路由邏輯。"""

    def test_calls_registry_get_with_site_id(self) -> None:
        """_retrieve 呼叫 registry.get(site_id)。"""
        registry = _make_mock_registry()
        fake_rag = MagicMock()
        fake_rag.retrieve.return_value = _make_fake_retrieval_results(1)
        registry.get.return_value = fake_rag

        tool = create_webpage_retriever_tool(registry)
        result = tool.invoke({"site_id": "nculab", "query": "test"})

        registry.get.assert_called_once_with("nculab")
        fake_rag.retrieve.assert_called_once()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_passes_filter_and_top_k(self) -> None:
        """filter_dict 與 similarity_top_k 正確傳遞。"""
        registry = _make_mock_registry()
        fake_rag = MagicMock()
        fake_rag.retrieve.return_value = _make_fake_retrieval_results(1)
        registry.get.return_value = fake_rag

        tool = create_webpage_retriever_tool(registry)
        tool.invoke(
            {
                "site_id": "nculab",
                "query": "paper",
                "filter_dict": {"page_type": "paper"},
                "similarity_top_k": 3,
            }
        )

        fake_rag.retrieve.assert_called_once_with(
            query="paper",
            filter_dict={"page_type": "paper"},
            similarity_top_k=3,
        )

    def test_propagates_registry_error(self) -> None:
        """registry.get 拋出 ValueError 時工具向上傳播。"""
        registry = _make_mock_registry()
        registry.get.side_effect = ValueError("site_id 'x' 不存在")

        tool = create_webpage_retriever_tool(registry)
        with pytest.raises(ValueError, match="不存在"):
            tool.invoke({"site_id": "x", "query": "test"})


# ---------- _format_retrieval_results ----------


class TestFormatRetrievalResults:
    """_format_retrieval_results 格式化邏輯。"""

    def test_empty_results(self) -> None:
        """空結果回傳提示字串。"""
        result = _format_retrieval_results([])
        assert "未檢索到" in result

    def test_single_result(self) -> None:
        """單筆結果包含標題、分數、URL。"""
        results = _make_fake_retrieval_results(1)
        formatted = _format_retrieval_results(results)
        assert "Page_1" in formatted
        assert "0.800" in formatted
        assert "https://example.com/page_1" in formatted

    def test_multiple_results_count(self) -> None:
        """多筆結果正確計數。"""
        results = _make_fake_retrieval_results(3)
        formatted = _format_retrieval_results(results)
        assert "3 筆" in formatted


# ---------- create_site_discovery_tool ----------


class TestCreateSiteDiscoveryTool:
    """create_site_discovery_tool 工廠函數。"""

    def test_returns_structured_tool(self) -> None:
        registry = _make_mock_registry()
        tool = create_site_discovery_tool(registry)
        assert isinstance(tool, StructuredTool)

    def test_tool_name(self) -> None:
        registry = _make_mock_registry()
        tool = create_site_discovery_tool(registry)
        assert tool.name == "list_knowledge_bases"

    def test_tool_description_mentions_webpage_retriever(self) -> None:
        registry = _make_mock_registry()
        tool = create_site_discovery_tool(registry)
        assert "webpage_retriever" in tool.description

    def test_invoke_with_sites(self) -> None:
        """有站點時回傳格式化列表。"""
        registry = _make_mock_registry(existing_sites=["nculab", "ncucsie"])
        tool = create_site_discovery_tool(registry)
        result = tool.invoke({})
        assert "nculab" in result
        assert "ncucsie" in result
        assert "可用的知識庫" in result

    def test_invoke_empty_sites(self) -> None:
        """無站點時回傳提示。"""
        registry = _make_mock_registry(existing_sites=[])
        tool = create_site_discovery_tool(registry)
        result = tool.invoke({})
        assert "沒有可用的知識庫" in result


# ---------- RAGAgent dataclass ----------


class TestRAGAgent:
    """RAGAgent dataclass 結構與 close 行為。"""

    def test_has_tools_and_registry_fields(self) -> None:
        """RAGAgent 包含 tools 和 registry 欄位。"""
        fields = {f.name for f in RAGAgent.__dataclass_fields__.values()}
        assert "tools" in fields
        assert "registry" in fields
        assert "graph" in fields
        assert "run_manager" in fields
        assert "config" in fields
        assert "checkpointer" in fields

    def test_close_calls_registry_close(self) -> None:
        """close() 呼叫 registry.close()。"""
        mock_registry = MagicMock(spec=RAGRegistry)
        agent = RAGAgent(
            graph=MagicMock(),
            tools=[],
            run_manager=MagicMock(),
            config=MagicMock(),
            registry=mock_registry,
        )
        agent.close()
        mock_registry.close.assert_called_once()

    def test_close_without_registry(self) -> None:
        """registry 為 None 時 close() 不報錯。"""
        agent = RAGAgent(
            graph=MagicMock(),
            tools=[],
            run_manager=MagicMock(),
            config=MagicMock(),
            registry=None,
        )
        agent.close()  # should not raise

    def test_tools_is_list(self) -> None:
        """tools 欄位為 list[StructuredTool]。"""
        mock_tool = MagicMock(spec=StructuredTool)
        agent = RAGAgent(
            graph=MagicMock(),
            tools=[mock_tool],
            run_manager=MagicMock(),
            config=MagicMock(),
        )
        assert isinstance(agent.tools, list)
        assert len(agent.tools) == 1


# ---------- 端到端流程模擬 ----------


class TestEndToEndFlow:
    """模擬 Agent 呼叫工具的完整流程（全部 mock）。"""

    def test_discovery_then_retrieve(self) -> None:
        """先呼叫 list_knowledge_bases，再呼叫 webpage_retriever。"""
        registry = _make_mock_registry(existing_sites=["nculab", "ncucsie"])

        # 模擬 retriever tool 需要的 RAG
        fake_rag = MagicMock()
        fake_rag.retrieve.return_value = _make_fake_retrieval_results(2)
        registry.get.return_value = fake_rag

        # 建立兩個工具
        discover_tool = create_site_discovery_tool(registry)
        retriever_tool = create_webpage_retriever_tool(registry)

        # Step 1: 發現站點
        sites_result = discover_tool.invoke({})
        assert "nculab" in sites_result
        assert "ncucsie" in sites_result

        # Step 2: 檢索特定站點
        search_result = retriever_tool.invoke(
            {
                "site_id": "nculab",
                "query": "實驗室成員",
            }
        )
        registry.get.assert_called_with("nculab")
        assert "Page_1" in search_result

    def test_multi_site_no_mixing(self) -> None:
        """先查 nculab 再查 ncucsie，registry.get 收到正確 site_id。"""
        registry = _make_mock_registry(existing_sites=["nculab", "ncucsie"])

        rag_nculab = MagicMock()
        rag_nculab.retrieve.return_value = [
            {
                "page_title": "NCU_Lab_Member",
                "score": 0.95,
                "page_type": "general",
                "url": "https://nculab.example.com/member",
                "content": "Lab member info",
            }
        ]
        rag_ncucsie = MagicMock()
        rag_ncucsie.retrieve.return_value = [
            {
                "page_title": "NCUCSIE_Course",
                "score": 0.88,
                "page_type": "course",
                "url": "https://ncucsie.example.com/course",
                "content": "Course info",
            }
        ]

        def get_side_effect(site_id: str) -> MagicMock:
            if site_id == "nculab":
                return rag_nculab
            return rag_ncucsie

        registry.get.side_effect = get_side_effect

        retriever_tool = create_webpage_retriever_tool(registry)

        # 查 nculab
        result_1 = retriever_tool.invoke(
            {
                "site_id": "nculab",
                "query": "成員",
            }
        )
        assert "NCU_Lab_Member" in result_1
        assert "NCUCSIE_Course" not in result_1

        # 查 ncucsie
        result_2 = retriever_tool.invoke(
            {
                "site_id": "ncucsie",
                "query": "課程",
            }
        )
        assert "NCUCSIE_Course" in result_2
        assert "NCU_Lab_Member" not in result_2

        # 驗證 registry.get 收到的 site_id 順序
        calls = [c.args[0] for c in registry.get.call_args_list]
        assert calls == ["nculab", "ncucsie"]
