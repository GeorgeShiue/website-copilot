# 資料儲存重構：實作紀錄

> 計畫見 [plan.md](./plan.md)

## Phase 1：移除 `run_rag_query` 的 `force_rebuild`、新增 `--run.vector-store-run`

### 變更

- `RAGQueryRunConfig`：刪除 `force_rebuild`，新增 `vector_store_run: str | None`（CLI `--run.vector-store-run`）。
- `retrieval/factory.py`
  - 新增 `vector_store_run_target(site_id, run_path)`：向量庫為 `<run_path>/results/milvus.db`；路徑不存在、缺向量庫、缺 `site_config.yml` 報 `FileNotFoundError`，`site_config.yml` 的 `site_id` 與指定站點不一致報 `ValueError`；log 印出建庫 run 的 `module_config.yml` 檔頭 `# source:`（D11，不比對建置參數）。
  - `load_rag(config, target, build_query_engine=False)`：新增 `build_query_engine`，供 rag-query 使用。
- `pipelines/exp.py` 的 `run_rag_query`：由 `build_rag(..., force_rebuild=...)` 改為 `load_rag(..., build_query_engine=True)`。連帶修正既有行為：原本向量庫不存在時 `build_or_load` 會自動建庫到 `data/rag/{site}/milvus.db`，現在報錯。
- `pipelines/prepare.py` 的 `run_rag_build`：save 時補存 `site_config.yml`（驗證時發現 rag-build 的 run 資料夾原本沒有，`vector_store_run` 無法核對站點）。
- `.gitignore`：`data/rag/**/indexes/`（D5）。
- 文件：README、`docs/code/runs/{cli,workflow}.md`、`docs/code/phase1/modules/data_retrieve.md`。
- 測試：新增 `test_pipeline_rag_query.py`（預設查已發布向量庫且不建庫、`vector_store_run` 覆寫 target、錯誤傳遞、不再有 `build_rag`、tmp data 目錄樹 hash 前後相同）；`test_rag_tools.py` 新增 `vector_store_run_target` 各情境與 `load_rag` 不建庫；`test_cli.py` 新增 `--run.vector-store-run`、`--run.force-rebuild` 被拒；`test_pipeline_prepare.py` 檢查 rag-build run 含 `site_config.yml`。

### 驗證

- `scripts/check.sh`：exit 0（ruff、pyright、352 passed、widget 同步）。
- `uv run pytest tests/integration -m "not cost"`：2 passed、5 deselected。
- CLI 冒煙：`prepare`／`serve --help`、`run rag-query`／`rag-build --help` 皆 exit 0；`rag-query --help` 有 `--run.vector-store-run`。
- `git check-ignore`：`indexes/*.idx` 命中新規則，`*.parquet` 不被忽略。
- grep `force_rebuild`：只剩 `build_rag`／`IndexBuilder`／`run_prepare` 內部使用與「已移除」的測試。
- **付費實測**（使用者已確認；log 未顯示費用，僅 embedding 與少量 LLM）：
  - `run rag-build nculab --run.config test` → run 資料夾含 `site_config.yml`。
  - `rag-query nculab --run.vector-store-run <該 run>`：exit 0，log 印出 `建庫設定 configs/rag/test.yml`。
  - `rag-query nculab`（已發布向量庫）：exit 0。
  - `rag-query ncucsie --run.vector-store-run <nculab 的 run>`：`ValueError: 站點不一致`；`--run.vector-store-run runs/nope`：`FileNotFoundError`。
  - `data/rag`、`data/webpages`（排除 `indexes/`）所有檔案的 sha256 清單於上述查詢前後完全相同。
- 驗證過程中的小插曲：第一版 tree-hash 腳本用 `sorted(os.walk())` 先走完整棵樹，`indexes` 的剪枝無效，導致誤報 data/ 有變動；改為逐檔 sha256 清單（`find -prune`）後確認無變動。

## Phase 2：向量庫路徑重整

### 變更

- **佈局（D1、D10 方案 i）**：`data/rag/{site_id}.db/` 為 Milvus 資料夾，collection 固定為 `chunks`（`ingestion/indexing/index.py` 的 `COLLECTION_NAME`），建庫設定紀錄放在其中的 `meta/`。parquet 路徑由 `data/rag/nculab/milvus.db/collections/nculab/partitions/_default/data/*.parquet` 縮短為 `data/rag/nculab.db/collections/chunks/partitions/_default/data/*.parquet`。
- `storage/data_manager.py`
  - `vector_store_path(site_id)`；`create_vector_store_staging` 改在 `data/rag/` 下建 `.staging-*`（向量庫建在其中的 `{site_id}.db`）。
  - `publish_vector_store(site_id, source_path, move, write_meta)`：放到 `{site_id}.db.tmp` → 呼叫 `write_meta(<tmp>/meta)` → `os.replace` 整個資料夾；失敗還原舊版並清掉 `.tmp`／`.old`；來源不是資料夾報 `NotADirectoryError`。
  - `publish_run_metadata` 拆出 `write_run_metadata(dest_folder, ...)` 供 meta 寫入共用（webpages／raw_webpages 仍用原函式）。
- `pipelines/prepare.py` 的 `run_rag_build`：publish 時以 `write_meta` 把 module／site／run config 與 log 寫進 `meta/`（與向量庫同一次替換）；建庫無產出時略過 publish 並印出訊息（紀錄隨向量庫發布，沒有向量庫就沒有地方放）。
- `retrieval/{factory,registry}.py`：`published_target` 的 `milvus_uri` 為 `data/rag/{site_id}.db`；`RAGRegistry` 只認 `{site_id}.db` 資料夾，忽略 `.staging-*`／`.db.tmp`／`.db.old`／同名檔案。
- `pipelines/exp.py`：結果中的 `collection_name` 改為 `chunks`。
- **Milvus Lite server 未停止的 bug（驗證中發現並修正）**：`_close_vector_store` 只關 client，in-process 的 Milvus Lite server 要到程式結束才 flush。publish 搬移資料夾後，結束時的 flush 寫回原 staging 路徑（重新產生 `.staging-*/…db` 殘骸），已發布的向量庫則只剩未 flush 的 WAL（claudecode 的 WAL 達 82MB、沒有 parquet）。現在 `_close_vector_store(vector_store, milvus_uri)` 一併呼叫 `server_manager_instance.release_server()`；新增 `tests/unit/test_index_close.py` 以真實 Milvus Lite 驗證 close 後已有 parquet、搬移後原路徑不會被重建。
- 既有三個站點以 `run rag-build <site> --run.no-save --run.publish` 重建並發布（D7 方案 b，實際執行兩輪：第一輪發現上述 bug，清掉後重跑）；舊的 `data/rag/{nculab,ncucsie,claudecode}/` 刪除。
- 文件：README、`docs/code/runs/{cli,config,workflow}.md`、`docs/code/phase1/modules/data_retrieve.md`。
- 測試：`test_pipeline_prepare.py`（新佈局、`meta/` 同版、舊版 meta 被取代、建庫失敗保留舊版、`write_meta` 失敗保留舊版、殘留 `.tmp`／`.old` 清除、來源非資料夾、無產出略過）、`test_rag_tools.py`（Registry 忽略中間產物與同名檔案）、`test_serve_rag_loading.py`（repo 內三個站點以 `chunks` 載入）、新增 `test_published_layout.py`（repo 內已發布向量庫：collection 為 `chunks`、parquet 路徑 site_id 只出現一次且無 `milvus.db`、`meta/` 內容、`data/rag` 無殘留）、`test_index_close.py`。

### 驗證

- `scripts/check.sh`：exit 0（ruff、pyright 0 errors、370 passed、widget 同步）。
- `uv run pytest tests/integration`（含 cost）：7 passed，455 秒。
- **遷移前基準**（動工前以舊向量庫產生）與遷移後比較：

  | 站點 | 筆數 舊 → 新 | 頁面集合 | top-k url（sample_query） | 體積（不含 `indexes/`） |
  |---|---|---|---|---|
  | nculab | 277 → 274 | 相同（47 頁） | 重疊 5/6 | 1.5M（舊 3.2M 含 indexes） |
  | ncucsie | 737 → 723 | 相同（192 頁） | 重疊 8/9 | 3.1M（舊 3.3M） |
  | claudecode | 6465 → 6463 | 相同（193 頁） | 5/5，順序相同 | 29M（舊 29M） |

  筆數與 text hash **不完全相同**，已逐一檢視原因：新舊差異在於目前 `data/webpages/` 的 markdown 與舊向量庫建庫時的版本有空白差異（舊 chunk 為 `**圖片摘要：**  \n> …`，行尾有兩個空格，現在的 markdown 沒有），使個別頁面的 chunk 邊界偏移、少 1 個 chunk（例：nculab 的 `projects` 9 → 8）。以「空白正規化後的行」比較：nculab 舊 1 / 1300 行、新 0 / 1299 行不見於對方；claudecode 5 / 34042 與 4 / 34041；ncucsie 61 / 2797 與 65 / 2801（行被 chunk 邊界切開所致）。新向量庫 node metadata 的 `site_id` 皆正確。此差異來自資料來源（webpages）而非本次改動：`IndexBuilder.build_nodes` 與 chunk 參數（800／100）未變。
- 路徑與結構：三個站點 `list_collections()` 皆為 `chunks`、`meta/` 含三個 config、`data/rag` 下無 `.staging-*`／`.tmp`／`.old`／舊版資料夾（`test_published_layout.py` 持續檢查）；WAL 已 flush 為 parquet。
- `rag-query <site>`（已發布向量庫）三站皆 exit 0，結果中 `collection_name` 為 `chunks`。
- 未做：`prepare nculab --run.config test` 的完整 publish 流程——它會以 `max_pages=40` 的測試資料覆寫 `data/webpages` 與 `data/rag` 內已提交的 nculab 資料；publish 位置與 `meta/` 已由單元測試與上述三站的實際 `rag-build --run.publish` 覆蓋。
