"""run_rag_build 的 publish 行為：向量庫與 run 元資料發布到 data/rag/{site_id}/。

create_rag 以 fake 替代（不建真實向量庫、不呼叫 embedding）；run 目錄與 data 目錄皆在 tmp。
"""

from unittest.mock import patch

import pytest

from app.configs.rag_config import RAGConfig
from app.workflow.data_manager import DataManager
from app.workflow.run_manager import RunManager
from app.workflow.workflow import run_rag_build


class _FakeRAG:
    def __init__(self, milvus_uri: str | None) -> None:
        self.milvus_uri = milvus_uri
        self.closed_before_publish: bool | None = None
        self.closed = False

    def close(self) -> None:
        self.closed = True


@pytest.fixture
def env(tmp_path):
    source = tmp_path / "runs_milvus.db"
    source.mkdir()
    (source / "vec.bin").write_text("v")
    rag = _FakeRAG(str(source))
    config = RAGConfig.from_toml("test")

    def _run_context(
        module, config_name, config, run_name_use_config_name=False, save=True
    ):
        run_manager = RunManager.for_run(
            module=module,
            site_id=config.site_id,
            run_name="r1",
            base_folder=str(tmp_path / "runs"),
        )
        return run_manager, "Rag Build (test)"

    data_manager = DataManager(base_folder=str(tmp_path / "data"))

    with (
        patch("app.workflow.workflow.create_rag", return_value=rag),
        patch("app.workflow.workflow.create_run_context", side_effect=_run_context),
        patch("app.workflow.workflow.DataManager", return_value=data_manager),
    ):
        yield rag, config, tmp_path


def test_publishes_vector_store_and_metadata(env):
    rag, config, tmp_path = env
    run_rag_build(config_name="test", publish=True)

    dest = tmp_path / "data" / "rag" / config.site_id
    assert (dest / "milvus.db" / "vec.bin").read_text() == "v"
    assert (dest / "module_config.toml").is_file()
    assert rag.closed


def test_publish_false_does_not_publish(env):
    rag, _, tmp_path = env
    run_rag_build(config_name="test")

    assert not (tmp_path / "data" / "rag").exists()
    assert rag.closed


def test_missing_vector_store_skips_vector_publish_but_publishes_metadata(env):
    rag, config, tmp_path = env
    rag.milvus_uri = str(tmp_path / "does_not_exist")
    run_rag_build(config_name="test", publish=True)

    dest = tmp_path / "data" / "rag" / config.site_id
    assert not (dest / "milvus.db").exists()
    assert (dest / "module_config.toml").is_file()
