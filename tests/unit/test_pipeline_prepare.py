"""pipelines/prepare.py 測試。

- run_prepare：三階段以同一個站點與 save=False / publish=True 串接；publish=False 時改存 runs/
  並以 runs/ 最新的圖片摘要結果建庫；crawler 無產出時提前結束。
- run_rag_build 的建庫位置與 publish 行為（原子替換到 data/rag/{site_id}/）：
  build_rag 以 fake 替代：在 RAGTarget.milvus_uri 寫出假向量庫，不呼叫 embedding；
  runs/、data/ 與系統暫存資料夾皆在 tmp。
"""

import os
import tempfile
from unittest.mock import patch

import pytest
import yaml

from website_copilot.config.pipeline_config import (
    ImageSummarizerRunConfig,
    PrepareRunConfig,
    RAGBuildRunConfig,
    WebsiteCrawlerRunConfig,
)
from website_copilot.config.rag_config import RAGConfig
from website_copilot.config.site_config import SiteConfig
from website_copilot.ingestion.indexing.index import RAGTarget
from website_copilot.pipelines.prepare import run_rag_build
from website_copilot.storage.data_manager import DataManager
from website_copilot.storage.run_manager import RunManager


SITE = "nculab"


def _run_config(save: bool, publish: bool) -> RAGBuildRunConfig:
    return RAGBuildRunConfig(site=SITE, config_name="test", save=save, publish=publish)


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
        self.site_id = SiteConfig.from_yaml(SITE).site_id
        self.rag_dir = self.data / "rag" / self.site_id
        self.rags: list[_FakeRAG] = []
        self.targets: list[RAGTarget] = []
        self.configs: list[RAGConfig] = []
        # 設為 False 時 fake build_rag 不寫出向量庫（模擬建庫無產出）
        self.write_store = True
        self.build_error: Exception | None = None

    def fake_build_rag(
        self, config: RAGConfig, target: RAGTarget, **_kwargs
    ) -> _FakeRAG:
        self.configs.append(config)
        self.targets.append(target)
        if self.build_error is not None:
            raise self.build_error
        if self.write_store:
            os.makedirs(target.milvus_uri)
            with open(os.path.join(target.milvus_uri, "vec.bin"), "w") as f:
                f.write("new")
        rag = _FakeRAG(target.milvus_uri)
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
        module, config_name, site_id, config, run_name_use_config_name=False, save=True
    ):
        title = "Rag Build (test)"
        if not save:
            return None, title
        run_manager = RunManager.for_run(
            module=module,
            site_id=site_id,
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


def _published_module_config(e: _Env) -> dict:
    with open(e.rag_dir / "module_config.yml", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------- save × publish 四種組合 ----------


def test_save_and_publish_keeps_runs_copy_and_publishes(env):
    run_rag_build(_run_config(save=True, publish=True))

    assert (env.rag_dir / "milvus.db" / "vec.bin").read_text() == "new"
    # runs/ 保留一份（publish 為複製而非移動）
    assert os.path.isdir(env.rags[0].milvus_uri)
    assert env.rag_dir_entries() == {
        "milvus.db",
        "module_config.yml",
        "site_config.yml",
        "run_config.yml",
        "terminal.log",
    }
    # 向量庫建在本次 run 的 results/，資料來源為 data/webpages/{site_id}
    run_path = env.runs.glob(f"*/rag_build/{env.site_id}/r1")
    assert env.targets[0].milvus_uri == str(next(run_path) / "results" / "milvus.db")
    assert env.targets[0].webpages_dir == str(env.data / "webpages" / env.site_id)
    assert env.rags[0].closed


def test_save_only_writes_runs_not_data(env):
    run_rag_build(_run_config(save=True, publish=False))

    assert os.path.isdir(env.rags[0].milvus_uri)
    assert str(env.runs) in env.rags[0].milvus_uri
    assert not env.rag_dir.exists()


def test_publish_only_moves_staging_into_place(env):
    run_rag_build(_run_config(save=False, publish=True))

    assert (env.rag_dir / "milvus.db" / "vec.bin").read_text() == "new"
    # 不留 staging／.tmp／.old，也不寫 runs/
    assert env.rag_dir_entries() == {
        "milvus.db",
        "module_config.yml",
        "site_config.yml",
        "run_config.yml",
    }
    assert not env.runs.exists()
    # 建在 data/rag/{site_id}/.staging-*（已刪除），不直接寫入 milvus.db
    staging = os.path.dirname(env.targets[0].milvus_uri)
    assert os.path.basename(staging).startswith(".staging-")
    assert os.path.dirname(staging) == str(env.rag_dir)


def test_no_save_no_publish_leaves_no_files(env):
    run_rag_build(_run_config(save=False, publish=False))

    assert not env.runs.exists()
    assert not env.rag_dir.exists()
    assert os.listdir(env.systmp) == []
    assert env.targets[0].milvus_uri.startswith(str(env.systmp))
    assert env.rags[0].closed


# ---------- 原子替換與失敗保護 ----------


def test_publish_replaces_existing_store(env):
    env.seed_old_store()
    run_rag_build(_run_config(save=False, publish=True))

    assert os.listdir(env.rag_dir / "milvus.db") == ["vec.bin"]
    assert (env.rag_dir / "milvus.db" / "vec.bin").read_text() == "new"
    assert env.rag_dir_entries() == {
        "milvus.db",
        "module_config.yml",
        "site_config.yml",
        "run_config.yml",
    }


def test_build_failure_keeps_old_store_and_cleans_staging(env):
    env.seed_old_store()
    env.build_error = RuntimeError("embedding failed")

    with pytest.raises(RuntimeError, match="embedding failed"):
        run_rag_build(_run_config(save=False, publish=True))

    assert (env.rag_dir / "milvus.db" / "vec.bin").read_text() == "old"
    assert env.rag_dir_entries() == {"milvus.db"}


def test_published_records_have_no_runtime_paths(env):
    """module_config.yml 不再記錄 milvus_uri 等執行期路徑；站點另存 site_config.yml。"""
    run_rag_build(_run_config(save=False, publish=True))

    module_config = _published_module_config(env)
    assert "milvus_uri" not in module_config["vector_store"]
    assert "site_id" not in module_config
    with open(env.rag_dir / "site_config.yml", encoding="utf-8") as f:
        assert yaml.safe_load(f)["site_id"] == env.site_id


def test_build_does_not_modify_config(env):
    run_rag_build(_run_config(save=True, publish=True))

    assert env.configs[0].model_dump() == RAGConfig.from_yaml("test").model_dump()


def test_webpages_data_use_latest_results(env):
    """webpages_data_use_latest_results：資料來源改為 runs/ 中同站點最新的圖片摘要結果。"""
    latest = env.runs / "20260930_100000" / "image_summarizer" / env.site_id / "r"
    (latest / "results").mkdir(parents=True)

    run_rag_build(
        RAGBuildRunConfig(
            site=SITE,
            config_name="test",
            save=True,
            publish=False,
            webpages_data_use_latest_results=True,
        )
    )

    assert env.targets[0].webpages_dir == str(latest)


def test_missing_vector_store_skips_vector_publish_but_publishes_metadata(env):
    env.write_store = False
    run_rag_build(_run_config(save=True, publish=True))

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
    """publish=True：三階段以同一個站點與 config 名稱、save=False／publish=True 的 RunConfig 串接。"""
    from website_copilot.pipelines import prepare

    with (
        patch.object(prepare, "run_website_crawler", return_value={"p": {}}) as crawl,
        patch.object(prepare, "run_image_summarizer", return_value={"p": {}}) as image,
        patch.object(prepare, "run_rag_build") as rag,
    ):
        prepare.run_prepare(PrepareRunConfig(site="ncucsie", config_name="test"))
    crawl.assert_called_once_with(
        WebsiteCrawlerRunConfig(
            site="ncucsie", config_name="test", save=False, publish=True
        )
    )
    image.assert_called_once_with(
        ImageSummarizerRunConfig(
            site="ncucsie", config_name="test", save=False, publish=True
        ),
        crawl_results={"p": {}},
    )
    rag.assert_called_once_with(
        RAGBuildRunConfig(
            site="ncucsie",
            config_name="test",
            save=False,
            publish=True,
            webpages_data_use_latest_results=False,
        )
    )


def test_run_prepare_without_publish_saves_to_runs_and_builds_from_latest() -> None:
    """publish=False：各階段只存 runs/，RAG 以 runs/ 最新的圖片摘要結果建庫。"""
    from website_copilot.pipelines import prepare

    with (
        patch.object(prepare, "run_website_crawler", return_value={"p": {}}) as crawl,
        patch.object(prepare, "run_image_summarizer", return_value={"p": {}}) as image,
        patch.object(prepare, "run_rag_build") as rag,
    ):
        prepare.run_prepare(
            PrepareRunConfig(site="ncucsie", config_name="test", publish=False)
        )
    crawl.assert_called_once_with(
        WebsiteCrawlerRunConfig(
            site="ncucsie", config_name="test", save=True, publish=False
        )
    )
    image.assert_called_once_with(
        ImageSummarizerRunConfig(
            site="ncucsie", config_name="test", save=True, publish=False
        ),
        crawl_results={"p": {}},
    )
    rag.assert_called_once_with(
        RAGBuildRunConfig(
            site="ncucsie",
            config_name="test",
            save=True,
            publish=False,
            webpages_data_use_latest_results=True,
        )
    )


def test_image_summarizer_loads_latest_results_of_same_site() -> None:
    """未傳入爬蟲結果時，只讀取 runs/ 中同站點的最新結果（S7）。"""
    from website_copilot.pipelines import prepare

    with (
        patch.object(prepare, "load_latest_results", return_value={"p": {}}) as load,
        patch.object(prepare, "ImageSummarizer") as summarizer_cls,
    ):
        prepare.run_image_summarizer(
            ImageSummarizerRunConfig(site="ncucsie", config_name="test", save=False)
        )

    load.assert_called_once_with("runs", "website_crawler", site_id="ncucsie")
    summarize = summarizer_cls.return_value.summarize_crawl_results_images
    assert summarize.call_args.args == ({"p": {}},)


def test_run_prepare_stops_when_crawler_returns_none() -> None:
    from website_copilot.pipelines import prepare

    with (
        patch.object(prepare, "run_website_crawler", return_value=None),
        patch.object(prepare, "run_image_summarizer") as image,
        patch.object(prepare, "run_rag_build") as rag,
    ):
        prepare.run_prepare(PrepareRunConfig(site="ncucsie", config_name="test"))
    image.assert_not_called()
    rag.assert_not_called()
