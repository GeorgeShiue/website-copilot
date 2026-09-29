# 專案結構重構 plan 4：實作紀錄

> 計畫與審核清單見 [plan.md](./plan.md)

## 1. 刪除多餘程式與檔案

- 程式：刪除 `DEFAULT_INIT_CONFIG_FOLDER_PATH` 與兩個 `override_init_config()`。`KEEP_TITLE_CONTENT_THRESHOLD` 一度刪除，之後由使用者復原保留。
- 以 `git rm` 刪除：`configs/rag/milvus.toml`、`tests/unit/_helpers.py`、`docs/progress_report/2026_0629/2026_0629_outline.md`、`.aiexclude`、`docs/exp/records/`。
- `run_manager.py`、`run_persistence.py` docstring 不再提 `chats/`。
- 測試：`test_run_agent.py` 的 `mock_save_logging` 改名 `_mock_save_logging`（17 處）；`test_rag_tools.py` 移除 `registry._test_tmp_dir`。
- `.vscode/settings.json`：修正 JSON 與 `pytestArgs`（未追蹤檔）。
- `docs/work/` 中舊開發紀錄仍提到 `_helpers.py`，屬歷史紀錄，未修改。

### 未追蹤目錄（A10～A13）

`rm -rf __pycache__ chats .claude runs/20260928_135728` 被 Claude Code auto mode 以「無法復原的本機刪除」擋下（這些檔案不在 git 中，刪除後無法還原），改由使用者手動執行。

## 2. WebpageImageSummarizer → ImageSummarizer

使用者先將類別改名，其餘由本輪完成：

- 以 Edit 更新 `pipeline_config.py`（`ImageSummarizerRunConfig`／`ImageSummarizerModuleConfig`）、設定類別 `ImageSummarizerConfig`（`_CONFIG_FOLDER_PATH = "configs/image_summarizer"`）、`pipelines/prepare.py`（`run_image_summarizer()`，run context 模組名 `image_summarizer`，區域變數 `image_summarizer`）、`cli/run.py`（`ImageSummarizerCLI`）、整合測試與 `test_image_failure_summary.py` docstring。
- `git mv`：`config/webpage_image_summarizer_config.py` → `config/image_summarizer_config.py`；`configs/webpage_image_summarizer/` → `configs/image_summarizer/`。
- 其餘殘留以 `sed` 統一替換（`WebpageImageSummarizer` → `ImageSummarizer`、`webpage_image_summarizer` → `image_summarizer`、`Webpage image summarizer` → `Image summarizer`）：
  - 程式：`image_summarizer.py`（config import）、`run_context.py`（`SiteModuleConfig`）、`run_persistence.py`（`load_latest_results` 預設 `module_name`）、`data_manager.py`（docstring）、`pipelines/exp.py` 與 `cli/exp.py`（實驗名稱）。
  - 測試：`test_cli.py`、`test_runmanager_datamanager.py`（名稱變短後以 `ruff format` 重新換行）。
  - 文件：`README.md`、`docs/code/runs/{cli,config,workflow}.md`、`docs/code/phase1/modules/data_preprocess.md`。
- README 目錄樹順帶移除已刪除的 `configs/rag/milvus.toml`。
- 最後以 `git grep` 確認除 `docs/work`、`docs/progress_report`、`docs/survey`、`data/` 外已無舊名。

中途 Bash 的 auto mode 安全檢查連續 7 次無回應（服務端暫時錯誤），期間改以 Read／Edit 修改檔案；`git mv` 與全域搜尋待服務恢復後完成。

## 行為變更

- runs 模組資料夾由 `runs/<ts>/webpage_image_summarizer/` 改為 `runs/<ts>/image_summarizer/`，`load_latest_results` 預設值跟著改，舊名存下的 run 不再被自動找到（目前 `runs/` 中無圖片摘要結果，不受影響）。
- `website-copilot exp` 的實驗名稱改為 `image_summarizer_model`／`image_summarizer_prompt`。
- CLI 子命令 `run image-summarizer` 不變。

## 驗證結果

- `scripts/check.sh`：exit 0；ruff 通過、pyright 0 errors、285 passed（6 deselected）、widget 同步檢查通過。
- 刪除階段與更名階段各執行一次，結果相同。
- 未執行 `pytest -m slow tests/integration`（真實爬蟲與付費 API）。

## Commit

- `refactor: remove redundant files, rename to ImageSummarizer (plan 4)`：包含以上所有變更與 `todo.md` 更新。
