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
