"""RAG 重構整合測試（精簡版）。

自 test_node_pipeline_builder.py / test_rag_builder.py / test_vector_store_builder.py
挑選最必要的核心測試整合於此，降低整體測試開銷。

涵蓋範圍：
- NodePipelineBuilder：空資料夾、基本建構、chunk_size、錯誤處理、metadata 注入
- VectorStoreBuilder：embedding 維度、ranker 參數、qdrant 建構/清理、factory 分派
- RAGBuilder：建構編排與 Context Manager 整合
- Query 結果儲存：來源序列化、response_to_dict、RunManager JSON/MD 儲存
"""

import json
import os
import tempfile
from typing import Any, Generator
from unittest.mock import patch

import pytest

from app.configs.rag_config import RAGConfig
from app.modules.rag_factory import NodePipelineBuilder, VectorStoreBuilder
from app.workflow.workflow_manager import (
    QUERY_MD_FILE_PREFIX,
    RESULTS_JSON_NAME,
    RunManager,
)
from utils.rag_helper import extract_sources_list, response_to_dict

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
def mock_config() -> RAGConfig:
    """最小化的 RAGConfig，供 RAGBuilder 測試使用。"""
    return RAGConfig(
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
        query_llm_name="gemini-3.1-flash-lite",
        evaluator_llm_name="gpt-5.4",
        cutoff=0.0,
        query="test query",
    )


@pytest.fixture
def run_manager(tmp_path) -> Generator[RunManager, None, None]:
    """指向臨時目錄的 RunManager，避免污染 ./runs。"""
    with patch("app.workflow.workflow_manager.RUNS_FOLDER_PATH", str(tmp_path)):
        rm = RunManager("rag_query")
        rm.set_run_path("test-run")
        rm.init_module_run_paths()
        yield rm


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
# 群組 3：RAGBuilder（RB.1 / RB.2 / RB.3）
# ═══════════════════════════════════════════════════════════


class TestRAGBuilder:
    """RAGBuilder 的建構編排與 Context Manager 整合。"""

    @staticmethod
    def _create_rag() -> Any:
        """建立 RAG 實例，同時 mock _load_results_json 避免檔案依賴。"""
        from app.modules.rag import RAG

        with patch.object(RAG, "_load_results_json", return_value={}):
            return RAG()

    def test_build_calls_all_five_steps(self, mock_config: RAGConfig) -> None:
        """build() 應依序呼叫全部 5 個建構步驟。"""
        from app.modules.rag import RAG
        from app.modules.rag_factory import RAGBuilder

        builder = RAGBuilder(mock_config)
        with (
            patch.object(RAG, "_load_results_json", return_value={}),
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
        self, mock_config: RAGConfig
    ) -> None:
        """build_to_retriever() 應建到 retriever 但不建 query engine。"""
        from app.modules.rag import RAG
        from app.modules.rag_factory import RAGBuilder

        builder = RAGBuilder(mock_config)
        with (
            patch.object(RAG, "_load_results_json", return_value={}),
            patch.object(builder, "build_nodes"),
            patch.object(builder, "build_vector_store"),
            patch.object(builder, "build_index"),
            patch.object(builder, "build_retriever"),
            patch.object(builder, "build_query_engine") as build_qe,
        ):
            builder.build_to_retriever()

        build_qe.assert_not_called()

    def test_build_returns_rag_with_context_manager(
        self, mock_config: RAGConfig
    ) -> None:
        """build() 回傳的 RAG 應支援 Context Manager 協定。"""
        from app.modules.rag import RAG
        from app.modules.rag_factory import RAGBuilder

        builder = RAGBuilder(mock_config)
        with (
            patch.object(RAG, "_load_results_json", return_value={}),
            patch.object(builder, "build_nodes"),
            patch.object(builder, "build_vector_store"),
            patch.object(builder, "build_index"),
            patch.object(builder, "build_retriever"),
            patch.object(builder, "build_query_engine"),
        ):
            rag = builder.build()

        assert hasattr(rag, "__enter__")
        assert hasattr(rag, "__exit__")


# ═══════════════════════════════════════════════════════════
# 群組 4：RAGBuilder.build_reusable（重建 / 載入決策與編排）
# ═══════════════════════════════════════════════════════════


class TestRAGBuilderReusable:
    """build_reusable() 的重建 / 載入決策與編排。"""

    @staticmethod
    def _build_reusable(builder, rag, *, force_rebuild: bool = False):
        """執行 build_reusable，mock 所有下游步驟以避免真實建構。"""
        with (
            patch.object(builder, "clean_vector_store") as clean,
            patch.object(builder, "build_nodes") as build_nodes,
            patch.object(builder, "build_vector_store") as build_vs,
            patch.object(builder, "build_index") as build_idx,
            patch.object(builder, "load_index") as load_idx,
            patch.object(builder, "build_retriever") as build_ret,
            patch.object(builder, "build_query_engine") as build_qe,
        ):
            rebuilt = builder.build_reusable(rag, force_rebuild=force_rebuild)

        return rebuilt, {
            "clean": clean,
            "build_nodes": build_nodes,
            "build_vs": build_vs,
            "build_idx": build_idx,
            "load_idx": load_idx,
            "build_ret": build_ret,
            "build_qe": build_qe,
        }

    def test_rebuilds_when_store_path_missing(
        self, mock_config: RAGConfig, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """store 路徑不存在 → 走重建路徑並回傳 True。"""
        monkeypatch.setattr(os.path, "exists", lambda p: False)
        from app.modules.rag_factory import RAGBuilder

        builder = RAGBuilder(mock_config)
        rag = TestRAGBuilder._create_rag()
        rebuilt, calls = self._build_reusable(builder, rag)

        assert rebuilt is True
        calls["clean"].assert_called_once_with(rag)
        calls["build_nodes"].assert_called_once_with(rag)
        calls["build_vs"].assert_called_once_with(rag)  # overwrite=True 為預設值
        calls["build_idx"].assert_called_once_with(rag)
        calls["load_idx"].assert_not_called()
        calls["build_ret"].assert_called_once_with(rag)
        calls["build_qe"].assert_called_once_with(rag)

    def test_loads_when_store_path_exists(
        self, mock_config: RAGConfig, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """store 路徑存在 → 走載入路徑並回傳 False。"""
        monkeypatch.setattr(os.path, "exists", lambda p: True)
        from app.modules.rag_factory import RAGBuilder

        builder = RAGBuilder(mock_config)
        rag = TestRAGBuilder._create_rag()
        rebuilt, calls = self._build_reusable(builder, rag)

        assert rebuilt is False
        calls["clean"].assert_not_called()
        calls["build_nodes"].assert_not_called()
        calls["build_idx"].assert_not_called()
        calls["build_vs"].assert_called_once_with(rag, overwrite=False)
        calls["load_idx"].assert_called_once_with(rag)
        calls["build_ret"].assert_called_once_with(rag)
        calls["build_qe"].assert_called_once_with(rag)

    def test_force_rebuild_overrides_existing_store(
        self, mock_config: RAGConfig, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """store 路徑存在但 force_rebuild=True → 仍走重建並回傳 True。"""
        monkeypatch.setattr(os.path, "exists", lambda p: True)
        from app.modules.rag_factory import RAGBuilder

        builder = RAGBuilder(mock_config)
        rag = TestRAGBuilder._create_rag()
        rebuilt, calls = self._build_reusable(builder, rag, force_rebuild=True)

        assert rebuilt is True
        calls["build_nodes"].assert_called_once_with(rag)
        calls["load_idx"].assert_not_called()

    def test_milvus_always_rebuilds(self) -> None:
        """Milvus 即使路徑存在也一律重建並回傳 True。"""
        from app.modules.rag_factory import RAGBuilder

        milvus_config = RAGConfig(
            config_name="test",
            webpages_data_folder_path="/tmp/test_rag_refactor_webpages",
            vector_store_type="milvus",
            milvus_uri="/tmp/test_rag_refactor_milvus.db",
            collection_name="test_collection",
            embedding_name="text-embedding-3-small",
            chunk_size=800,
            chunk_overlap=100,
            paragraph_separator="\n\n",
            query_mode="hybrid",
            similarity_top_k=10,
            hybrid_top_k=10,
            alpha=0.5,
            query_llm_name="gemini-3.1-flash-lite",
            evaluator_llm_name="gpt-5.4",
            cutoff=0.0,
            query="test query",
        )
        builder = RAGBuilder(milvus_config)
        rag = TestRAGBuilder._create_rag()
        rebuilt, calls = self._build_reusable(builder, rag)

        assert rebuilt is True
        calls["build_nodes"].assert_called_once_with(rag)
        calls["load_idx"].assert_not_called()


# ═══════════════════════════════════════════════════════════
# 群組 5：RAGBuilder.build_evaluators 與 RAG.evaluate
# ═══════════════════════════════════════════════════════════


class TestRAGBuilderEvaluators:
    """build_evaluators() 注入 evaluator，RAG.evaluate() 僅負責執行。"""

    def test_build_evaluators_injects_tuple(self, mock_config: RAGConfig) -> None:
        """build_evaluators() 應以 config 的 evaluator_llm_name 建立兩個 evaluator 並注入。"""
        from app.modules.rag_eval_prompts import (
            FAITHFULNESS_EVAL_TEMPLATE,
            FAITHFULNESS_REFINE_TEMPLATE,
            RELEVANCY_EVAL_TEMPLATE,
            RELEVANCY_REFINE_TEMPLATE,
        )
        from app.modules.rag_factory import RAGBuilder

        builder = RAGBuilder(mock_config)
        rag = TestRAGBuilder._create_rag()

        fake_llm = object()
        fake_faithfulness = object()
        fake_relevancy = object()
        with (
            patch(
                "app.modules.rag_factory.create_llm", return_value=fake_llm
            ) as create_llm,
            patch(
                "app.modules.rag_factory.FaithfulnessEvaluator",
                return_value=fake_faithfulness,
            ) as f_class,
            patch(
                "app.modules.rag_factory.RelevancyEvaluator",
                return_value=fake_relevancy,
            ) as r_class,
        ):
            builder.build_evaluators(rag)

        create_llm.assert_called_once_with(mock_config.evaluator_llm_name, "evaluator")
        f_class.assert_called_once_with(
            llm=fake_llm,
            eval_template=FAITHFULNESS_EVAL_TEMPLATE,
            refine_template=FAITHFULNESS_REFINE_TEMPLATE,
        )
        r_class.assert_called_once_with(
            llm=fake_llm,
            eval_template=RELEVANCY_EVAL_TEMPLATE,
            refine_template=RELEVANCY_REFINE_TEMPLATE,
        )
        assert rag.evaluators == (fake_faithfulness, fake_relevancy)

    def test_evaluate_raises_when_not_built(self) -> None:
        """未建 evaluator 時呼叫 evaluate() 應拋 RuntimeError。"""

        rag = TestRAGBuilder._create_rag()
        with pytest.raises(RuntimeError, match="Evaluators have not been built"):
            rag.evaluate("test query", object())

    def test_evaluate_uses_injected_evaluators(self) -> None:
        """evaluate() 應使用注入的 evaluator 執行並回傳 (faithfulness, relevancy)。"""
        from unittest.mock import Mock

        rag = TestRAGBuilder._create_rag()
        faithfulness_evaluator = Mock()
        relevancy_evaluator = Mock()
        faithfulness_evaluator.evaluate_response.return_value = "f_result"
        relevancy_evaluator.evaluate_response.return_value = "r_result"
        rag.evaluators = (faithfulness_evaluator, relevancy_evaluator)

        query = "test query"
        response = object()
        with patch.object(rag, "_log_evaluation_result"):
            f_result, r_result = rag.evaluate(query, response)

        assert f_result == "f_result"
        assert r_result == "r_result"
        faithfulness_evaluator.evaluate_response.assert_called_once_with(
            response=response
        )
        relevancy_evaluator.evaluate_response.assert_called_once_with(
            query=query, response=response
        )


# ═══════════════════════════════════════════════════════════
# 群組 6：Query 結果序列化與儲存（濃縮自 test_query_result_storage.py）
# ═══════════════════════════════════════════════════════════


class TestQueryResultStorage:
    """Query 結果序列化函式與 RunManager 儲存行為。"""

    @staticmethod
    def _make_source_node(
        score: float = 0.9,
        title: str = "測試頁",
        page_type: str = "personnel",
        content: str = "內容",
        url: str = "https://example.com",
    ) -> Any:
        """建立帶 metadata 的測試來源節點。"""
        from llama_index.core.schema import NodeWithScore, TextNode

        node = TextNode(
            text=content,
            metadata={"page_title": title, "page_type": page_type, "page_url": url},
        )
        return NodeWithScore(node=node, score=score)

    @staticmethod
    def _make_response(source_nodes: list[Any], response_text: str = "這是答案") -> Any:
        """建立測試 Response。"""
        from llama_index.core.base.response.schema import Response

        return Response(response=response_text, source_nodes=source_nodes, metadata={})

    @staticmethod
    def _make_evaluation_result(passing: bool = True) -> Any:
        """建立測試 EvaluationResult。"""
        from llama_index.core.evaluation.base import EvaluationResult

        return EvaluationResult(
            query="測試問題",
            contexts=["context"],
            response="這是答案",
            passing=passing,
            feedback="Reason: 內容皆來自來源",
            score=None,
        )

    @staticmethod
    def _sample_query_results() -> dict[str, Any]:
        """建立一份含單次 query 結果的 dict。"""
        response = TestQueryResultStorage._make_response(
            [TestQueryResultStorage._make_source_node(score=0.997)]
        )
        return {
            "config": {
                "config_name": "test",
                "run_name": "test-run",
                "query": "實驗室的成員有哪些人？",
                "query_times": 1,
            },
            "summary": {"query_times": 1},
            "results": [
                response_to_dict(
                    query="實驗室的成員有哪些人？",
                    response=response,
                    faithfulness_result=TestQueryResultStorage._make_evaluation_result(),
                    relevancy_result=TestQueryResultStorage._make_evaluation_result(),
                    index=1,
                    timestamp="2026-08-03 20:33:22",
                )
            ],
        }

    # ── 序列化函式 ──

    def test_extract_sources_list_serializes_and_truncates(self) -> None:
        """每個來源節點應序列化為 5 欄位 dict，內容可依 max_content_length 截斷。"""
        nodes = [
            self._make_source_node(score=0.997, content="a" * 100),
            self._make_source_node(score=0.8, title="第二頁"),
        ]
        sources = extract_sources_list(nodes)

        assert [s["page_title"] for s in sources] == ["測試頁", "第二頁"]
        assert sources[0]["score"] == 0.997
        assert sources[0]["page_type"] == "personnel"
        assert sources[0]["url"] == "https://example.com"
        # 預設 800 字元上限內不截斷
        assert sources[0]["content"] == "a" * 100

        truncated = extract_sources_list(
            [self._make_source_node(content="a" * 100)], max_content_length=10
        )
        assert truncated[0]["content"] == "a" * 10

    def test_extract_sources_list_missing_url_falls_back_to_empty(self) -> None:
        """缺少 page_url 時 url 欄位應為空字串。"""
        from llama_index.core.schema import NodeWithScore, TextNode

        node = TextNode(
            text="內容",
            metadata={"page_title": "無 URL 頁", "page_type": "general"},
        )
        sources = extract_sources_list([NodeWithScore(node=node, score=0.5)])
        assert sources[0]["url"] == ""

    def test_response_to_dict_assembles_entry_with_evaluation(self) -> None:
        """response_to_dict 應組裝完整 entry，並將評估結果轉為可序列化 dict。"""
        response = self._make_response([self._make_source_node(score=0.997)])
        entry = response_to_dict(
            query="實驗室的成員有哪些人？",
            response=response,
            faithfulness_result=self._make_evaluation_result(),
            relevancy_result=self._make_evaluation_result(),
            index=1,
            timestamp="2026-08-03 20:33:22",
        )

        assert entry["index"] == 1
        assert entry["timestamp"] == "2026-08-03 20:33:22"
        assert entry["query"] == "實驗室的成員有哪些人？"
        assert entry["response"] == "這是答案"
        assert entry["sources"][0]["score"] == 0.997
        assert entry["evaluation"]["faithfulness"] == {
            "passing": True,
            "score": None,
            "feedback": "Reason: 內容皆來自來源",
        }
        assert entry["evaluation"]["relevancy"]["passing"] is True

    def test_response_to_dict_omits_evaluation_when_none(self) -> None:
        """未傳入評估結果時不應包含 evaluation 欄位。"""
        entry = response_to_dict(query="問題", response=self._make_response([]))
        assert "evaluation" not in entry

    # ── RunManager 儲存 ──

    def test_save_results_as_json_roundtrips(self, run_manager: RunManager) -> None:
        """save_results_as_json 應寫出 results.json 且可 round-trip。"""
        query_results = self._sample_query_results()
        run_manager.save_results_as_json(query_results)

        json_path = os.path.join(run_manager.run_path, RESULTS_JSON_NAME)
        assert os.path.isfile(json_path)
        with open(json_path, "r", encoding="utf-8") as f:
            assert json.load(f) == query_results

    def test_save_query_results_as_md_writes_one_file_per_query(
        self, run_manager: RunManager
    ) -> None:
        """每次 query 應各自寫成一份 Markdown 檔案。"""
        query_results = self._sample_query_results()
        second = self._make_response(
            [self._make_source_node(score=0.9, title="另一頁")],
            response_text="第二次答案",
        )
        query_results["results"].append(
            response_to_dict(
                query="實驗室的成員有哪些人？",
                response=second,
                index=2,
                timestamp="2026-08-03 20:33:30",
            )
        )
        run_manager.save_query_results_as_md(query_results)

        for index in (1, 2):
            md_path = os.path.join(
                run_manager.results_folder_path, f"{QUERY_MD_FILE_PREFIX}{index}.md"
            )
            assert os.path.isfile(md_path)

        first_content = open(
            os.path.join(
                run_manager.results_folder_path, f"{QUERY_MD_FILE_PREFIX}1.md"
            ),
            "r",
            encoding="utf-8",
        ).read()
        assert "# Query #1: 實驗室的成員有哪些人？" in first_content
        assert "這是答案" in first_content
        assert "# Evaluation" in first_content
        assert "# Sources (1)" in first_content

        second_content = open(
            os.path.join(
                run_manager.results_folder_path, f"{QUERY_MD_FILE_PREFIX}2.md"
            ),
            "r",
            encoding="utf-8",
        ).read()
        assert "# Query #2:" in second_content
        assert "第二次答案" in second_content

    def test_save_query_results_as_md_escapes_pipe_in_table_cells(
        self, run_manager: RunManager
    ) -> None:
        """表格欄位中的 | 字元應被跳脫，避免破壞 Markdown 表格。"""
        from llama_index.core.schema import NodeWithScore, TextNode

        node = TextNode(
            text="內容",
            metadata={
                "page_title": "A|B",
                "page_type": "general",
                "page_url": "https://example.com/a|b",
            },
        )
        entry = response_to_dict(
            query="問題",
            response=self._make_response([NodeWithScore(node=node, score=0.5)]),
            index=1,
        )
        query_results = {
            "config": {"config_name": "test", "run_name": "test-run"},
            "summary": {"query_times": 1},
            "results": [entry],
        }
        run_manager.save_query_results_as_md(query_results)

        md_path = os.path.join(
            run_manager.results_folder_path, f"{QUERY_MD_FILE_PREFIX}1.md"
        )
        content = open(md_path, "r", encoding="utf-8").read()
        assert "| A\\|B |" in content
        assert "https://example.com/a\\|b" in content
