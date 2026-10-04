"""data/ 目錄的路徑規則（純函式，不存取檔案系統）。

DataManager（寫入）、retrieval.factory（RAGTarget）、RAGRegistry（serve 唯讀載入）
共用這份規則；獨立成不帶副作用的模組，讓 serve 階段查路徑時不會建立 data/
（DataManager 建構時會 makedirs）。

佈局：
    data/raw_webpages/{site_id}/    爬蟲原始輸出
    data/aug_webpages/{site_id}/    augmenter 處理後的最終結果（RAG 建庫讀這份）：
                                    results.json、results/*.md，以及文件原檔 files/
    data/vector_db/{site_id}.db/    向量庫（Milvus Lite 要求資料夾名稱以 .db 結尾）
"""

import os

DEFAULT_DATA_FOLDER = "data"

RAW_WEBPAGES = "raw_webpages"
AUG_WEBPAGES = "aug_webpages"
VECTOR_DB = "vector_db"

# aug_webpages（及 runs/ 的 augmenter 結果）內存放文件原檔的資料夾，與 results/ 並列
FILES_FOLDER = "files"

VECTOR_STORE_SUFFIX = ".db"


def site_data_path(
    category: str, site_id: str, data_folder: str = DEFAULT_DATA_FOLDER
) -> str:
    """data/{category}/{site_id}（category 為 RAW_WEBPAGES 或 AUG_WEBPAGES）。"""
    return os.path.join(data_folder, category, site_id)


def aug_webpages_path(site_id: str, data_folder: str = DEFAULT_DATA_FOLDER) -> str:
    """建庫資料來源 data/aug_webpages/{site_id}。"""
    return site_data_path(AUG_WEBPAGES, site_id, data_folder)


def vector_db_folder(data_folder: str = DEFAULT_DATA_FOLDER) -> str:
    """存放所有向量庫的資料夾 data/vector_db。"""
    return os.path.join(data_folder, VECTOR_DB)


def vector_store_name(site_id: str) -> str:
    """向量庫資料夾名稱 {site_id}.db。"""
    return f"{site_id}{VECTOR_STORE_SUFFIX}"


def vector_store_path(site_id: str, data_folder: str = DEFAULT_DATA_FOLDER) -> str:
    """已發布向量庫的位置 data/vector_db/{site_id}.db。"""
    return os.path.join(vector_db_folder(data_folder), vector_store_name(site_id))


def site_id_from_vector_store_name(name: str) -> str | None:
    """`{site_id}.db` 回傳 site_id；其他名稱（`.staging-*`、`.db.tmp`、`.db.old` 等
    publish 中間產物）回傳 None。"""
    if name.startswith(".") or not name.endswith(VECTOR_STORE_SUFFIX):
        return None
    return name.removesuffix(VECTOR_STORE_SUFFIX)
