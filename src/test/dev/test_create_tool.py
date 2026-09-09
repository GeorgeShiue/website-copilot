"""Tool 類別測試。

涵蓋：
- Tool(registry).tools 回傳 tools 列表
- tools 結構正確（名稱、數量、型別）
- registry 由外部傳入，Tool 不修改它

所有外部依賴以 mock 替代，不觸發真實 RAG / Milvus 資源。
"""

from unittest.mock import MagicMock, patch

from app.tools.rag_registry import RAGRegistry


# ===========================================================================
# 基礎設施
# ===========================================================================


def _make_mock_registry() -> MagicMock:
    """建立 mock RAGRegistry。"""
    registry = MagicMock(spec=RAGRegistry)
    registry.list_sites.return_value = ["test_site"]
    return registry


# ===========================================================================
# Tool 類別測試
# ===========================================================================


@patch("app.tools.tool.create_webpage_retriever_tool")
@patch("app.tools.tool.create_site_discovery_tool")
def test_tool_returns_tools_list(
    mock_create_discovery,
    mock_create_retriever,
):
    """Tool(registry).tools 回傳 tools 列表。"""
    from app.tools.tool import Tool

    mock_registry = _make_mock_registry()

    mock_discovery = MagicMock(name="discovery_tool")
    mock_retriever = MagicMock(name="retriever_tool")
    mock_create_discovery.return_value = mock_discovery
    mock_create_retriever.return_value = mock_retriever

    tool = Tool(registry=mock_registry)

    assert isinstance(tool.tools, list)
    assert len(tool.tools) == 2


@patch("app.tools.tool.create_webpage_retriever_tool")
@patch("app.tools.tool.create_site_discovery_tool")
def test_tool_tools_correct_names(
    mock_create_discovery,
    mock_create_retriever,
):
    """tools 包含 list_knowledge_bases 與 webpage_retriever 兩個工具。"""
    from app.tools.tool import Tool

    mock_registry = _make_mock_registry()

    mock_discovery = MagicMock(name="discovery_tool")
    mock_discovery.name = "list_knowledge_bases"
    mock_retriever = MagicMock(name="retriever_tool")
    mock_retriever.name = "webpage_retriever"
    mock_create_discovery.return_value = mock_discovery
    mock_create_retriever.return_value = mock_retriever

    tool = Tool(registry=mock_registry)

    assert len(tool.tools) == 2
    assert tool.tools[0].name == "list_knowledge_bases"
    assert tool.tools[1].name == "webpage_retriever"


@patch("app.tools.tool.create_webpage_retriever_tool")
@patch("app.tools.tool.create_site_discovery_tool")
def test_tool_passes_registry_to_tool_creators(
    mock_create_discovery,
    mock_create_retriever,
):
    """Tool 將 registry 傳入工具建立函數。"""
    from app.tools.tool import Tool

    mock_registry = _make_mock_registry()
    mock_create_discovery.return_value = MagicMock(name="discovery_tool")
    mock_create_retriever.return_value = MagicMock(name="retriever_tool")

    Tool(registry=mock_registry)

    # create_site_discovery_tool receives the registry
    mock_create_discovery.assert_called_once_with(mock_registry)
    # create_webpage_retriever_tool receives the registry
    mock_create_retriever.assert_called_once_with(mock_registry)


@patch("app.tools.tool.create_webpage_retriever_tool")
@patch("app.tools.tool.create_site_discovery_tool")
def test_tool_does_not_modify_registry(
    mock_create_discovery,
    mock_create_retriever,
):
    """Tool 不觸發任何 RAG 建構操作。"""
    from app.tools.tool import Tool

    mock_registry = _make_mock_registry()
    mock_create_discovery.return_value = MagicMock(name="discovery_tool")
    mock_create_retriever.return_value = MagicMock(name="retriever_tool")

    tool = Tool(registry=mock_registry)

    assert len(tool.tools) == 2
    # Verify no RAG building happened on the registry
    mock_registry.get.assert_not_called()
    mock_registry.close.assert_not_called()
