"""Tool 類別測試。

涵蓋：
- Tool(config_name).tools 回傳 tools 列表
- tools 結構正確（名稱、數量、型別）
- Tool 透過內部建立的 registry 傳入工具建立函數
- Tool 不觸發任何 RAG 建構操作

所有外部依賴以 mock 替代，不觸發真實 RAG / Milvus 資源。
"""

from unittest.mock import MagicMock, patch


# ===========================================================================
# Tool 類別測試
# ===========================================================================


@patch("app.tools.tool.create_webpage_retriever_tool")
@patch("app.tools.tool.create_site_discovery_tool")
@patch("app.tools.tool.RAGRegistry")
def test_tool_returns_tools_list(
    mock_rag_registry_cls,
    mock_create_discovery,
    mock_create_retriever,
):
    """Tool(config_name).tools 回傳 tools 列表。"""
    from app.tools.tool import Tool

    mock_discovery = MagicMock(name="discovery_tool")
    mock_retriever = MagicMock(name="retriever_tool")
    mock_create_discovery.return_value = mock_discovery
    mock_create_retriever.return_value = mock_retriever

    tool = Tool(config_name="test")

    assert isinstance(tool.tools, list)
    assert len(tool.tools) == 2


@patch("app.tools.tool.create_webpage_retriever_tool")
@patch("app.tools.tool.create_site_discovery_tool")
@patch("app.tools.tool.RAGRegistry")
def test_tool_tools_correct_names(
    mock_rag_registry_cls,
    mock_create_discovery,
    mock_create_retriever,
):
    """tools 包含 list_knowledge_bases 與 webpage_retriever 兩個工具。"""
    from app.tools.tool import Tool

    mock_discovery = MagicMock(name="discovery_tool")
    mock_discovery.name = "list_knowledge_bases"
    mock_retriever = MagicMock(name="retriever_tool")
    mock_retriever.name = "webpage_retriever"
    mock_create_discovery.return_value = mock_discovery
    mock_create_retriever.return_value = mock_retriever

    tool = Tool(config_name="test")

    assert len(tool.tools) == 2
    assert tool.tools[0].name == "list_knowledge_bases"
    assert tool.tools[1].name == "webpage_retriever"


@patch("app.tools.tool.create_webpage_retriever_tool")
@patch("app.tools.tool.create_site_discovery_tool")
@patch("app.tools.tool.RAGRegistry")
def test_tool_passes_registry_to_tool_creators(
    mock_rag_registry_cls,
    mock_create_discovery,
    mock_create_retriever,
):
    """Tool 將內部建立的 registry 傳入工具建立函數。"""
    from app.tools.tool import Tool

    mock_create_discovery.return_value = MagicMock(name="discovery_tool")
    mock_create_retriever.return_value = MagicMock(name="retriever_tool")

    Tool(config_name="test")

    # RAGRegistry was created with the correct config_name
    mock_rag_registry_cls.assert_called_once_with(config_name="test")
    internal_registry = mock_rag_registry_cls.return_value

    # create_site_discovery_tool receives the internal registry
    mock_create_discovery.assert_called_once_with(internal_registry)
    # create_webpage_retriever_tool receives the internal registry
    mock_create_retriever.assert_called_once_with(internal_registry)


@patch("app.tools.tool.create_webpage_retriever_tool")
@patch("app.tools.tool.create_site_discovery_tool")
@patch("app.tools.tool.RAGRegistry")
def test_tool_does_not_modify_registry(
    mock_rag_registry_cls,
    mock_create_discovery,
    mock_create_retriever,
):
    """Tool 不觸發任何 RAG 建構操作。"""
    from app.tools.tool import Tool

    mock_create_discovery.return_value = MagicMock(name="discovery_tool")
    mock_create_retriever.return_value = MagicMock(name="retriever_tool")

    tool = Tool(config_name="test")

    internal_registry = mock_rag_registry_cls.return_value
    assert len(tool.tools) == 2
    # Verify no RAG building happened on the registry
    internal_registry.get.assert_not_called()
    internal_registry.close.assert_not_called()
