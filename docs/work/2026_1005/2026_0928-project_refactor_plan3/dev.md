# 專案結構重構 plan 3：實作紀錄

> 計畫見 [plan.md](./plan.md)（Part A：2026-09-28 serve 拆分；Part B：2026-09-29 統一 agent 建構）

## Part A：serve 拆分

### A1. `run_agent_build()` 獨立 run context

- 移除 `run_manager` 參數與 `nullcontext()` 分支；一律建立 `runs/<ts>/agent_build/<config>/`。
- 落盤失敗時先 `agent.close()` 再 re-raise 的守衛保留。

### A2. `run_server_build()` 接收注入的 agent

- 簽名：`run_server_build(agent, run_config=None, allowed_origins=None, host="127.0.0.1", port=8000) -> ChatServer`；移除 `config_name` 與 `**config_overrides`。
- run context：`create_run_no_site_context(module="server", config_name=agent.config.config_name)`，路徑 `runs/<ts>/server/<config>/`。
- 不寫 `module_config.toml`，只寫 `run_config.toml`；失敗時只記錄 log 並 re-raise，不關閉 agent。

### A3. `serve()` 串接兩個 build

- `run_agent_build(config_name=run_config.config_name)` → `run_server_build(agent, ...)`；server build 失敗時 `agent.close()` 後 re-raise。
- 成功後 agent 由 `ChatServer` 結束時的 `ChatApp.close()` 關閉（沿用 plan 2）。
- `server/server.py` 的 docstring 仍正確，未修改。

### A4. 測試

- `test_run_agent.py`
  - 刪除 `test_run_agent_build_reuses_given_run_manager`。
  - `test_run_agent_build_calls_create_agent_and_returns_agent` 補斷言 `module="agent_build"`。
  - `test_run_server_build_*` 改為傳入 `_FakeAgentStub`，不再 patch `create_agent`／`AgentConfig`；斷言 `for_run_no_site(module="server", run_name="test", base_folder="runs")` 與不寫 `module_config.toml`。
  - `test_run_server_build_closes_agent_when_chat_app_creation_fails` 改為 `test_run_server_build_does_not_close_injected_agent_on_failure`。
  - 新增 `test_serve_builds_agent_then_server_and_runs`、`test_serve_closes_agent_when_server_build_fails`。
- `test_cli.py`：serve 測試多 patch `run_agent_build`。
- `tests/integration/test_module.py`：`test_server` 改為先 `run_agent_build()` 再 `run_server_build(agent, ...)`。

### A5. 文件

README、`docs/project.md`、`docs/code/runs/{workflow,config,cli}.md`、`docs/code/phase2_3_mvp/{phase2_3_mvp.md,modules/server.md,modules/agent.md}`：呼叫鏈、`run_server_build` 簽名、server 對話落盤改為 `runs/<ts>/server/<config>/`、`module_config.toml` 只在 `agent_build/`。

### Part A 驗證

- 此時檢查基線尚未修正：ruff 通過；pyright 4 errors、283 passed、1 failed，皆為既有的 `test_webpage_markdown_cleaner.py` 問題（於 B1 修正）。
- 實際執行 `website-copilot serve --run.config-name test --run.port 8011`，送出一次 `/api/chat` 後 SIGINT：

  ```
  runs/20260928_135728/agent_build/test/terminal.log
  runs/20260928_135728/agent_build/test/module_config.toml
  runs/20260928_135728/server/test/terminal.log
  runs/20260928_135728/server/test/results_plan3-verify.json
  runs/20260928_135728/server/test/run_config.toml
  ```

  SSE 串流正常回傳 `done`；中斷後印出 `Server Stopping` → `Server Stopped`，agent 經 `ChatApp.close()` 關閉。本次兩個 build 恰好落在同一秒，所以共用同一個時間戳目錄；跨秒時會分成兩個目錄（計畫中已接受）。此 run 目錄已於之後的專案清理中刪除。

## Part B：統一 agent 建構與恢復檢查基線

### B1. 修正檢查基線

只改 `tests/unit/test_webpage_markdown_cleaner.py`，程式不變：

- `test_save_generated_exclude_words`：`GenerationResult` 補上 `hits={"Footer text": 10}`（原本 `run_persistence.save_generated_exclude_words()` 讀 `result.hits[w]` 拋 `KeyError`）。
- pyright 4 errors：`generate_exclude_words()` 回傳 `GenerationResult | None`，兩處測試在存取屬性前加上 `assert result is not None`。

結果：`scripts/check.sh` 自 plan 1 以來首次 exit 0（pyright 0 errors、284 passed）。

### B2. `create_agent(config: AgentConfig)`

- `agent/agent.py`：移除內部 `AgentConfig.from_toml()`，改為 `Tool(config.config_name)`；更新函式與模組 docstring。
- `run_agent_build()` 改為 `create_agent(config)`（config 已套用覆寫值）。
- 測試：`create_agent` 的斷言改為以 `AgentConfig.from_toml()` 的回傳值呼叫。

這一步結束時 pyright 回報 `exp.py` 仍以舊簽名呼叫 `create_agent`，由 B3 一併處理。

### B3. `run_agent_query()` 改用 `run_agent_build()`

- `pipelines/exp.py`：
  - 移除 `create_agent`／`AgentConfig` import 與函式內的 config 載入、`log_config`、`save_module_config_as_toml`；改 import `pipelines.serve.run_agent_build`。
  - 流程改為 `agent = run_agent_build(config_name, **config_overrides)` → `try:` 建立 `module="agent"` 的 run context 並問答、落盤 → `finally: agent.close()`。
  - run context 的建立也放在 `try` 內，建立失敗時 agent 同樣會被關閉。
  - 內層 `except` 只記錄 `Agent Query Failed` 並 re-raise，不再關閉 agent（修正原本 `except` 與 `finally` 各關閉一次）。
- 測試（`test_run_agent.py`）：
  - `run_agent_query` 區段的 patch 由 `create_agent`／`AgentConfig`／`save_module_config_as_toml` 改為 `pipelines.exp.run_agent_build`。
  - `_FakeAgentStub` 改記錄 `close_count`（`close_called` 改為 property），兩個例外路徑測試斷言 `close_count == 1`。
  - 新增 `test_run_agent_query_builds_agent_via_run_agent_build`：覆寫值轉發給 `run_agent_build`，且 `run_agent_query` 不呼叫 `save_module_config_as_toml`。
  - 起初以 `hasattr(exp, "save_module_config_as_toml")` 斷言，但 `run_rag_query` 仍使用該函式，改為 patch 後 `assert_not_called()`。

### B4. 文件

README（聊天記錄段落）、`docs/code/runs/{workflow,config,cli}.md`、`docs/code/phase2_3_mvp/modules/agent.md`：`run_agent_query` 經 `run_agent_build`、`create_agent(config)` 簽名、`agent/` 不再有 `module_config.toml`、例外路徑只關閉一次。

## 最終驗證結果

- `scripts/check.sh`：exit 0；ruff 通過、pyright 0 errors、285 passed、widget 同步檢查通過。
- 實際執行 `website-copilot run agent --run.query "你好" --run.config-name test --run.thread-id plan4-verify`：

  ```
  runs/20260929_115058/agent_build/test/terminal.log
  runs/20260929_115058/agent_build/test/module_config.toml
  runs/20260929_115058/agent/test/terminal.log
  runs/20260929_115058/agent/test/results_plan4-verify.json
  runs/20260929_115058/agent/test/run_config.toml
  ```

  log 依序為 `Agent Build (test)` → `Agent Build Completed` → `Agent (test)` → 回答 → `Agent Query Completed`。

## 未處理與備註

- 對話歷史跨 run 查找範圍改變（見 plan.md「行為變更」第 3 點）：server 不再讀到舊 `runs/*/agent/` 的歷史，本輪未調整查找邏輯。
- `pipelines/exp.py` 現在 import `pipelines/serve.py`，執行 `run agent`／`run rag-query` 時會一併載入 uvicorn 與 FastAPI；exp 為實驗／除錯用途，影響可接受。若之後在意載入成本，可把 `run_agent_build` 移到不依賴 server 的模組（例如 `pipelines/agent.py`）。
- 未執行 `pytest -m slow tests/integration`（真實爬蟲與付費 API）。
