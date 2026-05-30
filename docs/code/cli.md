# CLI

## 一、主要檔案與角色

- `cli.py`：CLI 入口，使用 `tyro` 解析 dataclass 型態，收集 `run` 與 `module` 參數並 dispatch 到對應 pipeline，結束時寫入 `run_config.toml`。
- `[app/workflow/workflow.py](app/workflow/workflow.py)`：實作主要 pipeline（`run_website_crawler`、`run_webpage_image_summarizer`、`run_rag_build`、`run_rag_query`），負責載入 module config、執行流程、寫入 `module_config.toml` 與結果。
- `[app/workflow/workflow_config.py](app/workflow/workflow_config.py)`：定義 run 相關 dataclass（`BaseRunConfig` 與各 module 的 RunConfig），供 `tyro` 與程式使用。
- `[app/workflow/workflow_manager.py](app/workflow/workflow_manager.py)`：管理 `runs/<timestamp>/<module>/<run>/` 路徑，提供結果儲存、module/run config 路徑、log 與路徑顯示功能。
- `utils/config_helper.py`：共用設定工具，提供載入、覆寫、與寫出 TOML 的 helper 函式。

## 二、CLI 解析與 dispatch 流程

1. `cli.py` 定義 union 型別：`WebsiteCrawlerCLI | WebpageImageSummarizerCLI | RagBuildCLI | RagQueryCLI`。
   - 每個 dataclass 包含兩個欄位：`run`（RunConfig）與 `module`（module-specific overrides dataclass）。
2. 使用 `tyro.cli(...)` 解析命令列並回傳對應的 dataclass 實例 `cli_arg`。
3. 以 `vars(cli_arg.module)` 收集 module 參數，僅保留非 `None` 欄位作為 `module_config_overrides`。
4. 根據 `cli_arg` 型別，呼叫 `RunManager.set_module_path(<module>)`，再呼叫相對應的 `run_*` 函式，並傳入：
   - `run_manager`，
   - `**vars(cli_arg.run)`（如 `config_name`, `run_name_use_config_name`, `force_rebuild` 等），
   - `**module_config_overrides`（僅 CLI 明確提供的 module-level 覆寫）。
5. `run_*` 會透過對應 Config 的 `from_toml(config_name, **config_overrides)`：
   - 組出 `configs/<module>/{config_name}.toml`，
   - 用 `load_config_from_toml()` 載入 sections，
   - 用 `override_config()` 合併 CLI 傳入的 overrides（依 `sections_to_keys` 過濾），
   - 建構 dataclass 並執行模組內驗證。
6. CLI 主流程結束時，`cli.py` 呼叫 `save_run_config_as_toml(cli_arg.run, run_manager.run_config_toml_path)`，把 run-level 參數寫入 `run_config.toml`。

## 三、參數覆寫規則要點

- CLI 的 module-level overrides 由 `vars(cli_arg.module)` 收集，並透過 `utils.config_helper.override_config()` 做 allowed-keys 過濾；未列在 `sections_to_keys` 的欄位會被忽略並記 warning。
- 若某 section 的 allowed-keys 為空集合（例如 `litellm_kwargs`），helper 會允許該 section 的任意 key，使延伸參數能直接以 `**config.litellm_kwargs` 傳入 runtime 呼叫。

## 四、`run_config.toml` 與 `module_config.toml` 的差異與產生時機

- `module_config.toml`：由 pipeline（`run_*`）呼叫 `save_module_config_as_toml(config, run_manager.module_config_toml_path)` 產生，內容以 `sections_to_keys` 為準分 section 寫出；若存在 residual section（section keys 為空），未消耗欄位會寫入該 residual section。
- `run_config.toml`：由 `cli.py` 在 CLI 流程結束時呼叫 `save_run_config_as_toml(...)` 寫出（僅包含非 `None` 欄位）。若直接透過 `[app/workflow/workflow.py](app/workflow/workflow.py)` 或 `main.py` 呼叫 pipeline，通常不會自動寫入 `run_config.toml`。

## 五、執行範例

```bash
# 範例：使用 rag query CLI 並覆寫 module 的 top_k
python cli.py rag-query-cli --run.config-name test --run.force-rebuild --module.top-k 10
```

（備註：開發環境常見 wrapper：`uv run python cli.py ...`，依環境而定）

## 六、注意事項與建議

- 若需讓更多欄位能由 CLI 覆寫，請在對應 `app/configs/*_config.py` 中擴充 `sections_to_keys`。
- 若希望在非 CLI 環境也寫出 `run_config.toml`，可在呼叫端於 pipeline 執行完後顯式呼叫 `utils.config_helper.save_run_config_as_toml()` 並以 `RunManager.run_config_toml_path` 為目標路徑。

## 七、參考與證據

- `cli.py`
- `[app/workflow/workflow.py](app/workflow/workflow.py)`
- `[app/workflow/workflow_config.py](app/workflow/workflow_config.py)`
- `[app/workflow/workflow_manager.py](app/workflow/workflow_manager.py)`
- `utils/config_helper.py`