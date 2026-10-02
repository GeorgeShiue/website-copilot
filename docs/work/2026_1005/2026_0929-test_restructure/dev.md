# 測試新專案結構：實作紀錄

> 對應 [todo.md](../../todo.md)「技術債 → 檔案結構 → 測試新專案結構」。規劃在對話中與使用者逐項確認，沒有另外寫 plan.md，決策整理在下方第 0 節。

分支 `dev-tech-debt-refactor`，接在 plan 4（`0c3dbda`）之後，全部變更合併為一個 commit。

## 0. 決策

| 項目 | 決定 |
|---|---|
| integration 測試分工 | `test_module.py`：每個 run function 一個測試；`test_pipeline.py`（原 `test_main.py`）：`test_prepare`、`test_serve` |
| `test_server` | 從 `test_module.py` 移到 `test_pipeline.py`，改名 `test_serve` |
| 標記 | `slow` 改為 `cost`，只標會呼叫 LLM / VLM / embedding API 的測試 |
| `scripts/test.sh` | 只跑 `tests/unit`，不再用 `-m` 過濾 |
| CI | 維持只跑 integration，路徑改為整個 `tests/integration`（含 `cost` 測試） |
| integration 斷言 | 暫不加，只驗證不拋例外 |
| unit 測試範圍 | 只保留核心、易出錯程式的測試（見第 4 節），其餘刪除，需要時再從 `0c3dbda` 取回 |
| `test_prepare` 不寫入 `data/` | `run_prepare` 加 `publish` 參數，測試傳 `publish=False`；此時 rag build 用 `save=True`（見第 5 節） |

## 1. Integration 測試

| 檔案 | 測試 | cost |
|---|---|---|
| `test_module.py` | `test_website_crawler`、`test_image_summarizer`、`test_rag_build`、`test_agent_query` | ✅ |
| | `test_agent_build`（新增：`run_agent_build` 後 `close()`，只建 LLM client） | |
| `test_pipeline.py` | `test_prepare`（`run_prepare("test", publish=False)`，見第 5 節） | ✅ |
| | `test_serve`（`run_agent_build` + `run_server_build`，啟動 2 秒後關閉） | |

- `test_rag` → `test_rag_build`、`test_agent` → `test_agent_query`，與函式名一致。
- 原 `test_main()` 最後的 agent 問答由 `test_agent_query` 涵蓋，不重複。
- `test_serve` 不直接呼叫 `serve()`，因為其中的 `server.run()` 會阻塞。
- 標記改為逐個測試加 `@pytest.mark.cost`，不再用模組層級 `pytestmark`，讓不花錢的測試可單獨執行：`uv run pytest tests/integration -m "not cost"`（目前為 `test_agent_build`、`test_serve`，需 `.env` 中的 API key 才能建 agent）。

## 2. 標記、腳本、CI、文件

- `pyproject.toml`：marker 改為 `cost`。
- `scripts/test.sh`：`uv run pytest tests/unit "$@"`，註解附上手動執行 integration 的指令；`scripts/check.sh` 註解同步。
- CI：除了規劃中的 `ci-test.yml`，`ci.yml` 也有相同的舊路徑 `tests/integration/test_module.py`，兩者都改為 `tests/integration`。因此 `ci.yml`（push `dev`、PR 到 `main`、手動觸發）與 `ci-test.yml`（push `dev-test`）每次執行都會跑 `cost` 測試並產生 API 費用。
- `README.md`、`docs/code/runs/config.md`：更新測試檔名、`slow` 說明與執行指令。

## 3. Unit 測試依 `pipelines/` 重新分檔

| 新檔案 | 來源 |
|---|---|
| `test_pipeline_prepare.py` | `test_run_rag_build_publish.py`（rename）+ `test_cli.py` 的兩個 `run_prepare` 測試 |
| `test_pipeline_serve.py` | `test_run_agent.py` 中 `run_agent_build`、`run_server_build`、`serve`、`ChatApp`／`ChatServer` 的測試 |
| `test_pipeline_exp.py` | `test_run_agent.py` 中 `run_agent_query` 的測試 + `test_cli.py` 的兩個實驗名稱測試 |
| `agent_stubs.py` | `FakeAgentStub` 等替身與 `setup_mock_run_manager`，serve 與 exp 共用（規劃外，避免兩檔各複製一份） |
| `test_run_manager.py` | `test_runmanager_datamanager.py` 的 RunManager 部分 + `test_runmanager_agent_results.py` |
| `test_data_manager.py` | `test_runmanager_datamanager.py` 的 DataManager 部分 |

- `test_cli.py::test_serve_runs_server_and_swallows_interrupt` 與 `test_run_agent.py::test_serve_builds_agent_then_server_and_runs` 合併為一個，加入 KeyboardInterrupt 斷言。
- `setup_method`／`tempfile.mkdtemp()` 改為 pytest 的 `tmp_path`（原 `_make_registry` 建立的暫存目錄從未清除）。
- `test_webpage_markdown_cleaner.py` → `test_markdown_cleaner.py`。
- 移除過時內容：`TestRAGRetrieverSmoke`（來源 `scripts/m0_rag_smoke.py` 已不存在，且與其他測試重複）、`TestLoadRag`（由 `test_serve_rag_loading.py` 涵蓋）、`test_agent_base_folder_discover`（測試已不使用的 `chats/`）、docstring 中的 code review 編號。

這一步結束時為 273 個測試。

## 4. 只保留核心與易出錯程式的測試

依「出錯後果」與「出錯機率」把所有測試分為 S / A / B / C 四級，使用者決定刪除 B、C 級。

**保留（S、A 級，87 個函式）**

| 檔案 | 數量 | 內容 |
|---|---|---|
| `test_pipeline_prepare.py` | 10 | 向量庫原子替換、staging 清理、`run_prepare` 階段串接 |
| `test_serve_rag_loading.py` | 3 | serve 讀取已 publish 的向量庫 |
| `test_rag_tools.py` | 16 | `_should_rebuild`、重建前先讀來源、registry 快取與 LRU、retriever 依 site_id 路由 |
| `test_run_manager.py` | 6 | 對話紀錄存檔：合併、跨 run、JSON 損壞與結構錯誤的 fallback |
| `test_markdown_cleaner.py` | 10 | LLM 產生 exclude_words 的失敗處理、門檻過濾、投票 |
| `test_dedup_key.py` | 11 | URL 百分比編碼的去重鍵與結果過濾 |
| `test_agent_server.py` | 15 | SSE 串流與 error 事件、Gemini 回應解析、`resolve_site_id` |
| `test_pipeline_serve.py` | 7 | agent／server 在各種失敗情況下的資源關閉 |
| `test_pipeline_exp.py` | 7 | `run_agent_query` 的落盤與 agent 關閉 |
| `test_imports.py` | 2 | 所有模組可 import；CLI 與 serve 路徑不載入爬蟲（自 `test_cli.py` 移入） |

**刪除**

- 整個檔案：`test_cli.py`、`test_create_tool.py`、`test_data_manager.py`、`test_html_date_extraction.py`、`test_image_failure_summary.py`、`test_log_helper.py`。
- 其餘檔案中的 B、C 級測試：簡單 getter、固定屬性（schema、tool metadata）、內部實作細節（直接檢查 `_cache`）、log 格式、CLI 單純分派、run 資料夾查找、日期擷取、CORS、耗時統計等。
- 連帶移除沒人用的 helper（`_make_client_with_origins`）與空掉的段落標題，並改寫各檔 docstring 的「涵蓋」清單。

**實作中的問題**：以 AST 依保留清單刪除時，`test_rag_tools.py` 的 `TestListSites`、`TestGetCacheMiss` 等類別名稱沒列入清單，整個類別被刪掉，A 級的 7 個 registry 測試跟著消失。發現後從 HEAD 還原該檔並補上類別名稱重做。

## 5. `test_prepare` 不再覆寫 `data/`

**問題**：使用者執行 `uv run pytest tests/integration/test_pipeline.py` 後發現結果被 publish。`run_prepare()` 把三個階段寫死為 `save=False, publish=True`，`test_prepare` 因此以 test config（40 頁）的結果覆寫了 `data/webpages/nculab/` 與 `data/rag/nculab/module_config.toml`（共 17 個被追蹤的檔案）。該次執行在 rag build publish 前中斷，`milvus.db` 未被替換，但留下 `data/rag/nculab/.staging-5ktj1ra4/`（`finally` 未執行到）。

**考慮過的做法**

| 做法 | 結果 |
|---|---|
| `test_prepare` 以 fixture 切換到 `tmp_path` 工作目錄執行（`configs/` 用 symlink） | 不改正式程式且會端到端測到 publish；未採用 |
| 另寫 `run_prepare_test()`，只存 `runs/` 並開 `webpages_data_use_latest_results` | 會複製 `run_prepare` 的串接邏輯，且測試用函式放進正式 `pipelines/`；改為在 `run_prepare` 加參數 |
| `run_prepare(config_name, publish=True)` | **採用** |

**發現的回歸錯誤**：`webpages_data_use_latest_results` 在 `0303b47` 加入時是讀 `runs/` 中最新的 image summarizer 結果；之後拆出 DataManager 時（約 `8e5e6e8`）改成 `data_manager.get_webpages_path(site_id)`，與預設的 `data/webpages/<site>` 相同，參數實際上沒有作用（CLI 的 `run rag-build --run.webpages-data-use-latest-results` 也受影響）。若不修正，不 publish 時 rag build 會用 `data/webpages/` 的舊資料建庫，測試照樣通過但沒有測到本次產出。

**變更**

- `retrieval/factory.py`：`build_rag` 的 `webpages_data_use_latest_results=True` 改為以 `load_latest_run_path(runs, "image_summarizer", site_id=config.site_id)` 取得路徑（run 目錄的 `results.json` + `results/*.md` 與建庫來源格式相同）；移除因此不再使用的 `data_manager` 參數。
- `storage/run_persistence.py`：`load_latest_run_path` 加 `site_id` 參數，只搜尋 `runs/<ts>/<module>/<site_id>/`，避免讀到其他 site 較新的 run。
- `pipelines/prepare.py`：`run_prepare(config_name, publish=True)`。`publish=False` 時三個階段皆 `save=True, publish=False`，rag build 另傳 `webpages_data_use_latest_results=True`；`publish=True` 的行為不變。
- `tests/integration/test_pipeline.py`：`test_prepare` 改傳 `publish=False`。
- unit test 新增 2 個：`test_run_prepare_without_publish_saves_to_runs_and_builds_from_latest`（`test_pipeline_prepare.py`）、`test_build_rag_uses_latest_summarizer_run_of_same_site`（`test_rag_tools.py`，較新的其他 site run 不會被選中）；原 `test_run_prepare_chains_stages_with_publish` 補上 `webpages_data_use_latest_results=False` 斷言。
- `README.md`、`docs/code/runs/config.md`：註明 `test_prepare` 只存 `runs/`、不寫入 `data/`。
- 資料還原：`git restore data/` 還原 17 個被覆寫的檔案，刪除 `.staging-5ktj1ra4/`。`data/raw_webpages/` 未被 git 追蹤，無法判斷是否為該次產生，保留不動。

實作期間 Bash 的 auto mode 安全檢查多次無回應，改以 Read／Edit 修改檔案，檢查與測試待恢復後執行。

## 驗證結果

| 階段 | unit 測試數 | 說明 |
|---|---|---|
| 開始前 | 285 | `-m "not slow"`，6 deselected |
| 第 3 節分檔 | 284 | 合併 serve 重複測試 −1 |
| 第 3 節刪除過時與精簡 | 273 | −11 |
| 第 4 節 | 143 | 87 個函式，參數化展開後 143 |
| 第 5 節 | 145 | 新增 2 個 |

- 每一步都執行 `./scripts/test.sh`；最後 `./scripts/check.sh` exit 0（ruff、pyright 0 errors、143 passed、widget 同步檢查）。
- 第 5 節完成後 `./scripts/check.sh` exit 0（145 passed）。
- integration：第 1～4 節只以 `pytest --collect-only` 確認收集到 7 個測試、`-m "not cost"` 為 2 個。第 5 節後實際執行 `uv run pytest tests/integration/test_pipeline.py`：**2 passed**（3 分 15 秒，API 花費 $0.073）。
  - rag build 讀取 `runs/20260929_222457/image_summarizer/nculab/model-gpt-5.6-luna`（本次圖片摘要結果，34 頁）。
  - 產出在 `runs/20260929_222431`（crawler）、`222457`（image summarizer）、`222711`（rag build 向量庫）、`222741`（agent build、server）。
  - 執行前後 `git status --short data` 相同（只有未追蹤的 `data/raw_webpages/`），未寫入 `data/`。
- `test_module.py` 未實際執行。

## Commit

- `test: restructure tests for new project layout, rename slow marker to cost`：包含以上所有變更、本紀錄與 `todo.md` 更新（勾選「測試新專案結構」）。第 4、5 節是分次 amend 進同一個 commit。
- 要取回已刪除的測試，從 `0c3dbda`（本 commit 的父 commit）的 `tests/unit/` 取原始版本。
