"""Verify that data/rag/results/ and data/webpages/results/ can be safely removed.

These directories are legacy artifacts from the pre-multi-site version.
All current code paths use site_id-based resolution (data/webpages/{site_id}/,
data/rag/{site_id}/). This test suite confirms no active code depends on the
old fixed-location paths.
"""

from pathlib import Path

import pytest

from app.configs.rag_config import RAGConfig
from app.workflow.data_manager import DataManager

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LEGACY_RAG_RESULTS = PROJECT_ROOT / "data" / "rag" / "results"
LEGACY_WEBPAGES_RESULTS = PROJECT_ROOT / "data" / "webpages" / "results"
LEGACY_WEBPAGES_RESULTS_JSON = PROJECT_ROOT / "data" / "webpages" / "results.json"
LEGACY_WEBPAGES_TERMINAL_LOG = PROJECT_ROOT / "data" / "webpages" / "terminal.log"


# ---------------------------------------------------------------------------
# 1. 所有 rag config 的 site_id 均已定義，路徑解析不經過 legacy 路徑
# ---------------------------------------------------------------------------
class TestRAGConfigPathResolution:
    """RAGConfig.from_toml() must resolve to site_id-based paths, never legacy."""

    @pytest.mark.parametrize(
        "config_name",
        [
            "default",
            "test",
            "test_nculab",
            "test_ncucsie",
            "milvus",
            "qdrant",
        ],
    )
    def test_webpages_path_contains_site_id(self, config_name: str) -> None:
        config = RAGConfig.from_toml(config_name)
        assert config.site_id, f"{config_name} 缺少 site_id"
        assert config.webpages_data_folder_path is not None
        assert config.site_id in config.webpages_data_folder_path
        assert "data/webpages/" + config.site_id == config.webpages_data_folder_path

    @pytest.mark.parametrize(
        "config_name",
        [
            "default",
            "test",
            "test_nculab",
            "test_ncucsie",
            "milvus",
            "qdrant",
        ],
    )
    def test_milvus_uri_contains_site_id(self, config_name: str) -> None:
        config = RAGConfig.from_toml(config_name)
        assert config.site_id in config.milvus_uri
        assert f"data/rag/{config.site_id}/milvus.db" == config.milvus_uri

    @pytest.mark.parametrize(
        "config_name",
        [
            "default",
            "test",
            "test_nculab",
            "test_ncucsie",
            "milvus",
            "qdrant",
        ],
    )
    def test_qdrant_path_contains_site_id(self, config_name: str) -> None:
        config = RAGConfig.from_toml(config_name)
        assert config.site_id in config.qdrant_db_folder_path
        assert f"data/rag/{config.site_id}/qdrant_db" == config.qdrant_db_folder_path

    def test_no_config_references_legacy_paths(self) -> None:
        """Confirm none of the active config files hardcode legacy paths."""
        legacy_fragments = [
            "data/rag/results",
            "data/webpages/results",
            'data/webpages"',
        ]
        config_dir = PROJECT_ROOT / "configs" / "rag"
        for toml_file in config_dir.glob("*.toml"):
            content = toml_file.read_text()
            for frag in legacy_fragments:
                assert frag not in content, (
                    f"{toml_file.name} 仍包含 legacy 路徑片段: {frag}"
                )


# ---------------------------------------------------------------------------
# 2. DataManager 的 publish 方法不產生 legacy 路徑
# ---------------------------------------------------------------------------
class DataManagerPublishPaths:
    """DataManager.publish_*() always writes to data/{module}/{site_id}/."""

    def test_publish_crawl_results_target(self) -> None:
        dm = DataManager(base_folder=str(PROJECT_ROOT / "data"))
        result_path = dm.publish_crawl_results(
            site_id="nculab",
            results={},
            results_json_path=None,
            results_folder_path=None,
        )
        assert "nculab" in result_path
        assert "data/rag/results" not in result_path
        assert "data/webpages/results" not in result_path

    def test_publish_vector_store_target(self) -> None:
        dm = DataManager(base_folder=str(PROJECT_ROOT / "data"))
        result_path = dm.publish_vector_store(
            site_id="nculab",
            vector_store_type="milvus",
            source_path="/tmp/fake_milvus.db",
        )
        assert "nculab" in result_path
        assert "data/rag/results" not in result_path

    def test_publish_markdown_target(self) -> None:
        dm = DataManager(base_folder=str(PROJECT_ROOT / "data"))
        result_path = dm.publish_markdown(
            site_id="nculab",
            enhanced_results={},
            results_folder_path=None,
        )
        assert "nculab" in result_path
        assert "data/webpages/results" not in result_path


# ---------------------------------------------------------------------------
# 3. 程式碼中不存在對 legacy 路徑的硬編碼引用
# ---------------------------------------------------------------------------
class TestNoHardcodedLegacyReferences:
    """src/ 中的 production code 不應在邏輯中引用 legacy 路徑。

    註解和 docstring 中的歷史說明不計入。
    """

    LEGACY_PATHS = [
        "data/rag/results",
    ]

    # 排除本測試檔自身
    EXCLUDE_FILES = {"test_legacy_results_removal.py"}

    @pytest.fixture
    def source_files(self) -> list[Path]:
        src_dir = PROJECT_ROOT / "src"
        return [p for p in src_dir.rglob("*.py") if p.name not in self.EXCLUDE_FILES]

    def test_no_legacy_path_in_code(self, source_files: list[Path]) -> None:
        """掃描所有 .py 檔案，排除註解和 docstring 後，不應有 legacy 路徑。"""
        violations: list[str] = []
        for py_file in source_files:
            lines = py_file.read_text().splitlines()
            in_docstring = False
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                # 追蹤 triple-quote docstring 狀態
                if '"""' in stripped or "'''" in stripped:
                    # 單行 docstring ("""...""")
                    count = stripped.count('"""') or stripped.count("'''")
                    if count == 1:
                        in_docstring = not in_docstring
                    # count >= 2 表示同一行開啟並關閉，不改變狀態
                    continue
                if in_docstring:
                    continue
                if stripped.startswith("#"):
                    continue
                for legacy in self.LEGACY_PATHS:
                    if legacy in line:
                        violations.append(
                            f"{py_file.relative_to(PROJECT_ROOT)}:{i}: {legacy}"
                        )
        assert not violations, "以下 production code 仍引用 legacy 路徑:\n" + "\n".join(
            violations
        )


# ---------------------------------------------------------------------------
# 4. 驗證 legacy 資料確實已存在（確保測試的前提成立）
# ---------------------------------------------------------------------------
class TestLegacyDirectoriesExist:
    """確保 legacy 目錄確實存在，使以上測試有測試意義。"""

    def test_legacy_rag_results_exists(self) -> None:
        assert LEGACY_RAG_RESULTS.exists(), (
            f"{LEGACY_RAG_RESULTS} 不存在 — 測試前提不成立"
        )

    def test_legacy_webpages_results_exists(self) -> None:
        assert LEGACY_WEBPAGES_RESULTS.exists(), (
            f"{LEGACY_WEBPAGES_RESULTS} 不存在 — 測試前提不成立"
        )

    def test_legacy_webpages_results_json_exists(self) -> None:
        assert LEGACY_WEBPAGES_RESULTS_JSON.exists(), (
            f"{LEGACY_WEBPAGES_RESULTS_JSON} 不存在 — 測試前提不成立"
        )
