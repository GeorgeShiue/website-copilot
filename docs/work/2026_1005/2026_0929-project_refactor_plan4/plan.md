# 專案結構重構 plan 4：刪除多餘檔案與 ImageSummarizer 更名

> 前一輪（plan 3）見 [2026_0928-project_refactor_plan3/plan.md](../2026_0928-project_refactor_plan3/plan.md)

## Context

plan 1～3 完成後，專案中累積了未使用的程式、重複的設定檔與過時的文件／執行產物（[todo.md](../../todo.md)「專案結構重構 → plan 4」）。本輪先盤點多餘項目、逐項審核後刪除；過程中 `WebpageImageSummarizer` 類別更名為 `ImageSummarizer`，再將相關名稱全面對齊。

## 盤點方式

- 程式：`vulture src tests --min-confidence 60` 找未使用的定義，`ruff --select F401,F841,F811` 找未使用的 import／變數，再以 `grep` 確認有無引用（排除框架呼叫的誤報）。
- 檔案：`git ls-files` 列出所有追蹤檔，逐目錄檢查 `configs/`、`data/`、`docs/`、`scripts/`、根目錄設定檔與本機忽略目錄（`chats/`、`runs/`、`__pycache__/`、`.claude/`、`.vscode/`）。

## 審核清單與決策

### A. 建議刪除

| # | 項目 | 理由 | 決策 |
|---|---|---|---|
| A1 | `website_crawler_config.py` 的 `KEEP_TITLE_CONTENT_THRESHOLD` | 未使用 | **保留**（作為嘗試過的數值紀錄） |
| A2 | `webpage_image_summarizer_config.py` 的 `DEFAULT_INIT_CONFIG_FOLDER_PATH` | 未使用 | 刪除 |
| A3 | `WebsiteCrawler.override_init_config()` | 無呼叫端 | 刪除 |
| A4 | `ImageSummarizer.override_init_config()` | 無呼叫端 | 刪除 |
| A5 | `configs/rag/milvus.toml` | 與 `default.toml` 內容完全相同 | 刪除 |
| A6 | `tests/unit/_helpers.py` | 唯一函式 `mock_exit_delegates_to_real` 無人 import | 刪除 |
| A7 | `data/{rag,webpages}/{ncucsie,nculab}/run_config.toml` | 8/31 舊檔，含已不存在的欄位（如 `save_vector_store_to_runs`） | **保留** |
| A8 | `data/rag/*/milvus.db/LOCK`、`manifest.json.prev` | 執行期鎖檔與備份 | **保留** |
| A9 | `docs/progress_report/2026_0629/2026_0629_outline.md` | 已被 `_v2` 取代 | 刪除 |
| A10 | 根目錄 `__pycache__/` | 舊腳本殘留的 `.pyc` | 刪除（未追蹤，由使用者手動執行） |
| A11 | `chats/` | 程式已不寫入 | 刪除（同上） |
| A12 | `.claude/` | 空資料夾 | 刪除（同上） |
| A13 | `runs/20260928_135728` | 舊 run 產物 | 刪除（同上） |

### B. 需要判斷

| # | 項目 | 決策 |
|---|---|---|
| B1 | `.github/workflows/ci-test.yml`（`dev-test` 分支用） | 保留 |
| B2 | `configs/*/test_{nculab,ncucsie,claudecode}.toml`（程式只用 `test.toml`） | 保留 |
| B3 | `.aiexclude`（Gemini Code Assist 排除清單，幾乎等同 `.gitignore`） | **刪除** |
| B4 | `docs/progress_report/*/*_marp.pdf`（由 `_marp.md` 匯出） | 保留 |
| B5 | `docs/progress_report/*/` 由 `.mmd` 產生的 svg／png | 保留 |
| B6 | `docs/work/.../2026_0917-winnow_webpage_clean/` 的 `copilot/` 與 `claude/` 兩套計畫 | 保留 |
| B7 | `data/*/*/terminal.log` | 保留 |
| B8 | `docs/exp/records/`（3.1M 實驗紀錄） | **整包刪除** |

### C. 小清理

| # | 項目 | 決策 |
|---|---|---|
| C1 | `run_manager.py`、`run_persistence.py` docstring 中的 `chats/` | 移除 |
| C2 | `test_run_agent.py` 未使用的 `mock_save_logging` 參數 | 改名 `_mock_save_logging`（`@patch` 仍需擋住寫檔，參數無法移除） |
| C3 | `test_rag_tools.py` 未使用的 `registry._test_tmp_dir` | 移除 |
| C4 | `.vscode/settings.json` 開頭多餘的 `s`、`pytestArgs` 為 `"test"` | 修正為合法 JSON 與 `"tests"`（本機檔，不進版控） |

### 確認不是多餘（掃描誤報）

`retrieval/evaluation.py`（`pipelines/exp.py` 使用）、`transforms.py` 的 `aextract`／`class_name`（LlamaIndex 呼叫）、`server/app.py` 的 `health`／`chat`（FastAPI 路由）、`test_log_helper.py` 的 `_clean_summary`（autouse fixture）、`extension/widget.js`（由 `sync-widget.sh`／`check-widget.sh` 刻意維持同步）。

## ImageSummarizer 更名範圍

使用者已將 `WebpageImageSummarizer` 類別改名為 `ImageSummarizer`，其餘名稱一併對齊：

| 舊 | 新 |
|---|---|
| `WebpageImageSummarizerConfig`／`RunConfig`／`ModuleConfig`／`CLI` | `ImageSummarizerConfig`／`RunConfig`／`ModuleConfig`／`CLI` |
| `run_webpage_image_summarizer()` | `run_image_summarizer()` |
| `config/webpage_image_summarizer_config.py` | `config/image_summarizer_config.py` |
| `configs/webpage_image_summarizer/` | `configs/image_summarizer/` |
| runs 模組資料夾 `webpage_image_summarizer` | `image_summarizer` |
| 實驗名稱 `webpage_image_summarizer_{model,prompt}` | `image_summarizer_{model,prompt}` |

CLI 子命令原本就是 `image-summarizer`，不變。`docs/work/`、`docs/progress_report/` 為歷史紀錄，保留舊名。
