"""pipelines/prepare.py 測試。

- run_prepare：三階段以 save=False / publish=True 串接；publish=False 時改存 runs/
  並以 runs/ 最新的圖片摘要結果建庫；crawler 無產出時提前結束。
- run_rag_build 的建庫位置與 publish 行為（原子替換到 data/rag/{site_id}/）：
  build_rag 以 fake 替代：依 config.vector_store.milvus_uri／run_manager 決定位置寫出假向量庫，
  不呼叫 embedding；runs/、data/ 與系統暫存資料夾皆在 tmp。
"""

import os
import tempfile
from unittest.mock import patch

import pytest
import yaml

from website_copilot.config.rag_config import RAGConfig
from website_copilot.pipelines.prepare import run_rag_build
from website_copilot.storage.data_manager import DataManager
from website_copilot.storage.run_manager import RunManager


class _FakeRAG:
    def __init__(self, milvus_uri: str | None) -> None:
        self.milvus_uri = milvus_uri
        self.closed = False

    def close(self) -> None:
        self.closed = True


class _Env:
    def __init__(self, tmp_path) -> None:
        self.tmp_path = tmp_path
        self.runs = tmp_path / "runs"
        self.data = tmp_path / "data"
        self.systmp = tmp_path / "systmp"
        self.site_id = RAGConfig.from_yaml("test").site_id
        self.rag_dir = self.data / "rag" / self.site_id
        self.rags: list[_FakeRAG] = []
        # 設為 False 時 fake build_rag 不寫出向量庫（模擬建庫無產出）
        self.write_store = True
        self.build_error: Exception | None = None

    def fake_build_rag(self, config, run_manager=None, **_kwargs) -> _FakeRAG:
        if run_manager is not None:
            config.vector_store.milvus_uri = os.path.join(
                run_manager.results_folder_path, "milvus.db"
            )
        if self.build_error is not None:
            raise self.build_error
        if self.write_store:
            os.makedirs(config.vector_store.milvus_uri)
            with open(
                os.path.join(config.vector_store.milvus_uri, "vec.bin"), "w"
            ) as f:
                f.write("new")
        rag = _FakeRAG(config.vector_store.milvus_uri)
        self.rags.append(rag)
        return rag

    def seed_old_store(self) -> None:
        store = self.rag_dir / "milvus.db"
        store.mkdir(parents=True)
        (store / "vec.bin").write_text("old")

    def rag_dir_entries(self) -> set[str]:
        return set(os.listdir(self.rag_dir)) if self.rag_dir.exists() else set()


@pytest.fixture
def env(tmp_path, monkeypatch):
    e = _Env(tmp_path)
    e.systmp.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(e.systmp))

    def _run_context(
        module, config_name, config, run_name_use_config_name=False, save=True
    ):
        title = "Rag Build (test)"
        if not save:
            return None, title
        run_manager = RunManager.for_run(
            module=module,
            site_id=config.site_id,
            run_name="r1",
            base_folder=str(e.runs),
        )
        return run_manager, title

    data_manager = DataManager(base_folder=str(e.data))

    with (
        patch(
            "website_copilot.pipelines.prepare.build_rag",
            side_effect=e.fake_build_rag,
        ),
        patch(
            "website_copilot.pipelines.prepare.create_run_context",
            side_effect=_run_context,
        ),
        patch(
            "website_copilot.pipelines.prepare.DataManager",
            return_value=data_manager,
        ),
    ):
        yield e


def _published_milvus_uri(e: _Env) -> str:
    with open(e.rag_dir / "module_config.yml", encoding="utf-8") as f:
        return yaml.safe_load(f)["vector_store"]["milvus_uri"]


# ---------- save × publish 四種組合 ----------


def test_save_and_publish_keeps_runs_copy_and_publishes(env):
    run_rag_build(config_name="test", save=True, publish=True)

    assert (env.rag_dir / "milvus.db" / "vec.bin").read_text() == "new"
    # runs/ 保留一份（publish 為複製而非移動）
    assert os.path.isdir(env.rags[0].milvus_uri)
    assert env.rag_dir_entries() == {"milvus.db", "module_config.yml", "terminal.log"}
    assert _published_milvus_uri(env) == str(env.rag_dir / "milvus.db")
    assert env.rags[0].closed


def test_save_only_writes_runs_not_data(env):
    run_rag_build(config_name="test", save=True, publish=False)

    assert os.path.isdir(env.rags[0].milvus_uri)
    assert str(env.runs) in env.rags[0].milvus_uri
    assert not env.rag_dir.exists()


def test_publish_only_moves_staging_into_place(env):
    run_rag_build(config_name="test", save=False, publish=True)

    assert (env.rag_dir / "milvus.db" / "vec.bin").read_text() == "new"
    # 不留 staging／.tmp／.old，也不寫 runs/
    assert env.rag_dir_entries() == {"milvus.db", "module_config.yml"}
    assert not env.runs.exists()
    assert _published_milvus_uri(env) == str(env.rag_dir / "milvus.db")


def test_no_save_no_publish_leaves_no_files(env):
    run_rag_build(config_name="test", save=False, publish=False)

    assert not env.runs.exists()
    assert not env.rag_dir.exists()
    assert os.listdir(env.systmp) == []
    assert env.rags[0].closed


# ---------- 原子替換與失敗保護 ----------


def test_publish_replaces_existing_store(env):
    env.seed_old_store()
    run_rag_build(config_name="test", save=False, publish=True)

    assert os.listdir(env.rag_dir / "milvus.db") == ["vec.bin"]
    assert (env.rag_dir / "milvus.db" / "vec.bin").read_text() == "new"
    assert env.rag_dir_entries() == {"milvus.db", "module_config.yml"}


def test_build_failure_keeps_old_store_and_cleans_staging(env):
    env.seed_old_store()
    env.build_error = RuntimeError("embedding failed")

    with pytest.raises(RuntimeError, match="embedding failed"):
        run_rag_build(config_name="test", save=False, publish=True)

    assert (env.rag_dir / "milvus.db" / "vec.bin").read_text() == "old"
    assert env.rag_dir_entries() == {"milvus.db"}


def test_missing_vector_store_skips_vector_publish_but_publishes_metadata(env):
    env.write_store = False
    run_rag_build(config_name="test", save=True, publish=True)

    assert not (env.rag_dir / "milvus.db").exists()
    assert (env.rag_dir / "module_config.yml").is_file()


def test_swap_failure_restores_old_store(tmp_path):
    """tmp → milvus.db 的 rename 失敗時，舊向量庫還原且不留 .tmp／.old。"""
    data_manager = DataManager(base_folder=str(tmp_path / "data"))
    rag_dir = tmp_path / "data" / "rag" / "site"
    (rag_dir / "milvus.db").mkdir(parents=True)
    (rag_dir / "milvus.db" / "vec.bin").write_text("old")
    source = tmp_path / "new.db"
    source.mkdir()
    (source / "vec.bin").write_text("new")

    real_replace = os.replace

    def _flaky_replace(src, dst):
        if str(src).endswith(".tmp"):
            raise OSError("disk error")
        return real_replace(src, dst)

    with (
        patch(
            "website_copilot.storage.data_manager.os.replace",
            side_effect=_flaky_replace,
        ),
        pytest.raises(OSError, match="disk error"),
    ):
        data_manager.publish_vector_store(site_id="site", source_path=str(source))

    assert (rag_dir / "milvus.db" / "vec.bin").read_text() == "old"
    assert os.listdir(rag_dir) == ["milvus.db"]


# ===========================================================================
# run_prepare：階段串接與提前結束
# ===========================================================================


def test_run_prepare_chains_stages_with_publish() -> None:
    from website_copilot.pipelines import prepare

    with (
        patch.object(prepare, "run_website_crawler", return_value={"p": {}}) as crawl,
        patch.object(prepare, "run_image_summarizer", return_value={"p": {}}) as image,
        patch.object(prepare, "run_rag_build") as rag,
    ):
        prepare.run_prepare("test")
    crawl.assert_called_once_with(config_name="test", save=False, publish=True)
    image.assert_called_once_with(
        config_name="test", crawl_results={"p": {}}, save=False, publish=True
    )
    rag.assert_called_once_with(
        config_name="test",
        webpages_data_use_latest_results=False,
        save=False,
        publish=True,
    )


def test_run_prepare_without_publish_saves_to_runs_and_builds_from_latest() -> None:
    """publish=False：各階段只存 runs/，RAG 以 runs/ 最新的圖片摘要結果建庫。"""
    from website_copilot.pipelines import prepare

    with (
        patch.object(prepare, "run_website_crawler", return_value={"p": {}}) as crawl,
        patch.object(prepare, "run_image_summarizer", return_value={"p": {}}) as image,
        patch.object(prepare, "run_rag_build") as rag,
    ):
        prepare.run_prepare("test", publish=False)
    crawl.assert_called_once_with(config_name="test", save=True, publish=False)
    image.assert_called_once_with(
        config_name="test", crawl_results={"p": {}}, save=True, publish=False
    )
    rag.assert_called_once_with(
        config_name="test",
        webpages_data_use_latest_results=True,
        save=True,
        publish=False,
    )


def test_run_prepare_stops_when_crawler_returns_none() -> None:
    from website_copilot.pipelines import prepare

    with (
        patch.object(prepare, "run_website_crawler", return_value=None),
        patch.object(prepare, "run_image_summarizer") as image,
        patch.object(prepare, "run_rag_build") as rag,
    ):
        prepare.run_prepare("test")
    image.assert_not_called()
    rag.assert_not_called()
