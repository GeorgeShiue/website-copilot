"""IndexHandle.close 必須停止本地 Milvus Lite server，publish 搬移資料夾才安全。

只關 client 時 server 會等到程式結束才 flush：搬移資料夾後 flush 寫回原路徑，
已發布的向量庫只剩未 flush 的 WAL，原路徑還留下殘骸。以真實 Milvus Lite（4 維假向量）驗證。
"""

import os
import shutil
from pathlib import Path

from llama_index.core.schema import TextNode
from llama_index.vector_stores.milvus import MilvusVectorStore

from website_copilot.ingestion.indexing.index import IndexHandle


def _parquets(store: Path) -> list[Path]:
    return list(store.rglob("*.parquet"))


def test_close_flushes_and_releases_server(tmp_path: Path) -> None:
    uri = str(tmp_path / "staging" / "s.db")
    os.makedirs(os.path.dirname(uri))
    store = MilvusVectorStore(uri=uri, collection_name="chunks", dim=4, overwrite=True)
    store.add([TextNode(text="hi", embedding=[0.1, 0.2, 0.3, 0.4])])

    IndexHandle(vector_store=store, index=None, milvus_uri=uri).close()  # type: ignore[arg-type]

    # close 後資料已 flush 成 parquet（不只是 WAL）
    assert _parquets(Path(uri))

    # 搬移後原路徑不會被殘留的 server 寫回
    moved = tmp_path / "published.db"
    shutil.move(uri, moved)
    from milvus_lite.server_manager import server_manager_instance

    server_manager_instance.release_all()
    assert not Path(uri).exists()
    assert _parquets(moved)
