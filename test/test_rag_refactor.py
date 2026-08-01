"""RAG 重構整合測試（精簡版）。

自 test_node_pipeline_builder.py / test_rag_builder.py / test_vector_store_builder.py
挑選最必要的核心測試整合於此，降低整體測試開銷。

涵蓋範圍：
- NodePipelineBuilder：空資料夾、基本建構、chunk_size、錯誤處理、metadata 注入
- VectorStoreBuilder：embedding 維度、ranker 參數、qdrant 建構/清理、factory 分派
- RagBuilder：建構編排與 Context Manager 整合
"""

import os
import tempfile
from typing import Any, Generator
from unittest.mock import patch

import pytest

from app.configs.rag_config import RagConfig
from app.modules.rag_factory import NodePipelineBuilder, VectorStoreBuilder

# ═══════════════════════════════════════════════════════════
# 共用 fixtures
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def md_folder() -> Generator[str, None, None]:
    """建立含單一 .md 檔案的臨時資料夾。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        md_content = """# Title

This is a paragraph with some content about the research topic.

## Section 1

More detailed information about section one.
This is a second sentence in section one.

## Section 2

Content for section two with additional details.
"""
        with open(os.path.join(tmpdir, "test_page.md"), "w", encoding="utf-8") as f:
            f.write(md_content)
        yield tmpdir


@pytest.fixture
def empty_folder() -> Generator[str, None, None]:
    """建立空的臨時資料夾。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_config() -> RagConfig:
    """最小化的 RagConfig，供 RagBuilder 測試使用。"""
    return RagConfig(
        config_name="test",
        webpages_data_folder_path="/tmp/test_rag_refactor_webpages",
        vector_store_type="qdrant",
        qdrant_db_folder_path="/tmp/test_rag_refactor_qdrant",
        collection_name="test_collection",
        embedding_name="text-embedding-3-small",
        chunk_size=800,
        chunk_overlap=100,
        paragraph_separator="\n\n",
        query_mode="hybrid",
        similarity_top_k=10,
        hybrid_top_k=10,
        alpha=0.5,
        llm_name="gemini-3.1-flash-lite",
        cutoff=0.0,
        query="test query",
    )


# ═══════════════════════════════════════════════════════════
# 群組 1：NodePipelineBuilder（NPB.1 / NPB.2 / NPB.3 / NPB.6 / NPB.8）
# ═══════════════════════════════════════════════════════════


class TestNodePipelineBuilder:
    """NodePipelineBuilder 的核心行為。"""

    def test_empty_folder_returns_empty_list(self, empty_folder: str) -> None:
        """空資料夾應回傳空列表。"""
        nodes = NodePipelineBuilder().build(empty_folder, {})
        assert nodes == []

    def test_single_md_produces_nodes_with_content_and_metadata(
        self, md_folder: str
    ) -> None:
        """有 .md 檔案時應產出帶內容與 metadata 的 BaseNode。"""
        from llama_index.core.schema import BaseNode

        nodes = NodePipelineBuilder().build(md_folder, {})
        assert len(nodes) > 0
        for node in nodes:
            assert isinstance(node, BaseNode)
            assert node.get_content().strip(), "Node content should not be empty"
            assert node.metadata is not None

    def test_custom_chunk_size_affects_splitting(self, md_folder: str) -> None:
        """較小的 chunk_size 應產出較多且較短的 node。"""
        small_nodes = NodePipelineBuilder(chunk_size=50, chunk_overlap=0).build(
            md_folder, {}
        )
        large_nodes = NodePipelineBuilder(chunk_size=500, chunk_overlap=0).build(
            md_folder, {}
        )
        assert len(small_nodes) >= len(large_nodes)

        bounded_nodes = NodePipelineBuilder(chunk_size=100, chunk_overlap=0).build(
            md_folder, {}
        )
        for node in bounded_nodes:
            # 預留 metadata/formatting 的寬裕空間
            assert len(node.get_content()) <= 300

    def test_nonexistent_folder_raises(self) -> None:
        """不存在的資料夾應拋出 FileNotFoundError。"""
        with pytest.raises(FileNotFoundError, match="Markdown folder not found"):
            NodePipelineBuilder().build("/nonexistent/path/to/folder", {})

    def test_results_json_injects_file_metadata(self, md_folder: str) -> None:
        """results_json 應將 page metadata 注入每個 node。"""
        results_json = {
            "test_page": {
                "url": "https://example.com/test_page",
                "metadata": {
                    "page_type": "paper",
                    "description": "A test research page",
                },
            }
        }
        nodes = NodePipelineBuilder().build(md_folder, results_json)
        for node in nodes:
            assert node.metadata.get("page_title") == "test_page"
            assert node.metadata.get("page_url") == "https://example.com/test_page"
            assert node.metadata.get("page_type") == "paper"
            assert node.metadata.get("description") == "A test research page"

    def test_build_file_metadata_static_helper(self) -> None:
        """_build_file_metadata 應正確組裝 metadata，未知檔案使用預設值。"""
        results_json = {
            "alpha": {
                "url": "https://example.com/alpha",
                "metadata": {"page_type": "paper", "description": "desc"},
            }
        }
        metadata = NodePipelineBuilder._build_file_metadata(
            results_json, "/some/path/alpha.md"
        )
        assert metadata == {
            "page_title": "alpha",
            "page_url": "https://example.com/alpha",
            "page_type": "paper",
            "description": "desc",
        }

        fallback = NodePipelineBuilder._build_file_metadata({}, "/some/path/unknown.md")
        assert fallback == {
            "page_title": "unknown",
            "page_url": "",
            "page_type": "general",
            "description": "",
        }


# ═══════════════════════════════════════════════════════════
# 群組 2：VectorStoreBuilder（VSB.1 / VSB.2 / VSB.3 / VSB.5 / VSB.6）
# ═══════════════════════════════════════════════════════════


class TestVectorStoreBuilder:
    """VectorStoreBuilder 的靜態方法與 factory 分派。"""

    @pytest.mark.parametrize(
        ("embedding_name", "expected_dim"),
        [("text-embedding-3-small", 1536), ("text-embedding-3-large", 3072)],
    )
    def test_resolve_embedding_dim_known(
        self, embedding_name: str, expected_dim: int
    ) -> None:
        """已知 embedding 名稱應回傳正確維度。"""
        assert VectorStoreBuilder.resolve_embedding_dim(embedding_name) == expected_dim

    def test_resolve_embedding_dim_unknown_raises(self) -> None:
        """未知名稱應拋出 ValueError。"""
        with pytest.raises(ValueError, match="Unknown embedding_name"):
            VectorStoreBuilder.resolve_embedding_dim("unknown-model")

    @pytest.mark.parametrize(
        ("hybrid_ranker", "expected_params"),
        [
            ("RRFRanker", {"k": 60}),
            ("WeightedRanker", {"weights": [1.0, 0.5]}),
        ],
    )
    def test_default_hybrid_ranker_params_known(
        self, hybrid_ranker: str, expected_params: dict
    ) -> None:
        """支援的 ranker 應回傳預設參數。"""
        assert (
            VectorStoreBuilder.default_hybrid_ranker_params(hybrid_ranker)
            == expected_params
        )

    def test_default_hybrid_ranker_params_unknown_raises(self) -> None:
        """不支援的 ranker 應拋出 ValueError。"""
        with pytest.raises(ValueError, match="Unsupported hybrid_ranker"):
            VectorStoreBuilder.default_hybrid_ranker_params("UnknownRanker")

    def test_build_qdrant_creates_dir_and_returns_client_store(self) -> None:
        """build_qdrant 應建立巢狀目錄並回傳 client 與 store。"""
        from qdrant_client import QdrantClient

        with tempfile.TemporaryDirectory() as tmpdir:
            qdrant_path = os.path.join(tmpdir, "a", "b", "qdrant_db")
            client, store = VectorStoreBuilder.build_qdrant(
                collection_name="test_collection",
                db_folder_path=qdrant_path,
            )
            assert isinstance(client, QdrantClient)
            assert store is not None
            assert os.path.isdir(qdrant_path)

    def test_clean_qdrant_removes_dir_and_noop_on_missing(self) -> None:
        """clean_qdrant 應刪除目錄，對不存在的路徑/None 不拋錯。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "qdrant_db")
            os.makedirs(db_path)
            with open(os.path.join(db_path, "data.txt"), "w") as f:
                f.write("test data")
            VectorStoreBuilder.clean_qdrant(db_path)
            assert not os.path.exists(db_path)

        VectorStoreBuilder.clean_qdrant("/nonexistent/path")
        VectorStoreBuilder.clean_qdrant(None)

    def test_build_dispatch_qdrant(self) -> None:
        """build(type='qdrant') 應分派到 build_qdrant 並回傳 (client, store)。"""
        from qdrant_client import QdrantClient

        with tempfile.TemporaryDirectory() as tmpdir:
            client, store = VectorStoreBuilder.build(
                vector_store_type="qdrant",
                collection_name="test",
                embedding_name="text-embedding-3-small",
                qdrant_db_folder_path=os.path.join(tmpdir, "qdrant_db"),
            )
            assert isinstance(client, QdrantClient)
            assert store is not None

    @patch("app.modules.rag_factory.MilvusVectorStore")
    def test_build_dispatch_milvus(self, mock_milvus: object) -> None:
        """build(type='milvus') 應分派到 build_milvus 並回傳 (None, store)。"""
        client, store = VectorStoreBuilder.build(
            vector_store_type="milvus",
            collection_name="test",
            embedding_name="text-embedding-3-small",
            milvus_uri="/tmp/test_milvus.db",
        )
        assert client is None
        assert store is not None

    def test_build_unknown_type_raises(self) -> None:
        """不支援的 vector_store_type 應拋出 ValueError。"""
        with pytest.raises(ValueError, match="Unsupported vector_store_type"):
            VectorStoreBuilder.build(
                vector_store_type="unknown",
                collection_name="test",
                embedding_name="text-embedding-3-small",
            )

    def test_build_missing_required_args_raises(self) -> None:
        """缺少必要路徑/URI 參數時應拋出 ValueError。"""
        with pytest.raises(ValueError, match="qdrant_db_folder_path is required"):
            VectorStoreBuilder.build(
                vector_store_type="qdrant",
                collection_name="test",
                embedding_name="text-embedding-3-small",
            )
        with pytest.raises(ValueError, match="milvus_uri is required"):
            VectorStoreBuilder.build(
                vector_store_type="milvus",
                collection_name="test",
                embedding_name="text-embedding-3-small",
            )


# ═══════════════════════════════════════════════════════════
# 群組 3：RagBuilder（RB.1 / RB.2 / RB.3）
# ═══════════════════════════════════════════════════════════


class TestRagBuilder:
    """RagBuilder 的建構編排與 Context Manager 整合。"""

    @staticmethod
    def _create_rag() -> Any:
        """建立 Rag 實例，同時 mock _load_results_json 避免檔案依賴。"""
        from app.modules.rag import Rag

        with patch.object(Rag, "_load_results_json", return_value={}):
            return Rag()

    def test_build_calls_all_five_steps(self, mock_config: RagConfig) -> None:
        """build() 應依序呼叫全部 5 個建構步驟。"""
        from app.modules.rag import Rag
        from app.modules.rag_factory import RagBuilder

        builder = RagBuilder(mock_config)
        with (
            patch.object(Rag, "_load_results_json", return_value={}),
            patch.object(builder, "build_nodes") as build_nodes,
            patch.object(builder, "build_vector_store") as build_vs,
            patch.object(builder, "build_index") as build_idx,
            patch.object(builder, "build_retriever") as build_ret,
            patch.object(builder, "build_query_engine") as build_qe,
        ):
            builder.build()

        build_nodes.assert_called_once()
        build_vs.assert_called_once()
        build_idx.assert_called_once()
        build_ret.assert_called_once()
        build_qe.assert_called_once()

    def test_build_to_retriever_skips_query_engine(
        self, mock_config: RagConfig
    ) -> None:
        """build_to_retriever() 應建到 retriever 但不建 query engine。"""
        from app.modules.rag import Rag
        from app.modules.rag_factory import RagBuilder

        builder = RagBuilder(mock_config)
        with (
            patch.object(Rag, "_load_results_json", return_value={}),
            patch.object(builder, "build_nodes"),
            patch.object(builder, "build_vector_store"),
            patch.object(builder, "build_index"),
            patch.object(builder, "build_retriever"),
            patch.object(builder, "build_query_engine") as build_qe,
        ):
            builder.build_to_retriever()

        build_qe.assert_not_called()

    def test_build_returns_rag_with_context_manager(
        self, mock_config: RagConfig
    ) -> None:
        """build() 回傳的 Rag 應支援 Context Manager 協定。"""
        from app.modules.rag import Rag
        from app.modules.rag_factory import RagBuilder

        builder = RagBuilder(mock_config)
        with (
            patch.object(Rag, "_load_results_json", return_value={}),
            patch.object(builder, "build_nodes"),
            patch.object(builder, "build_vector_store"),
            patch.object(builder, "build_index"),
            patch.object(builder, "build_retriever"),
            patch.object(builder, "build_query_engine"),
        ):
            rag = builder.build()

        assert hasattr(rag, "__enter__")
        assert hasattr(rag, "__exit__")
