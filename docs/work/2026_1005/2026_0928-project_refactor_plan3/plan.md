# 專案結構重構 plan 3：agent build 與 server build 分離、統一 agent 建構

> 前一輪（plan 2）見 [2026_0927-project_refactor_plan2/plan.md](../2026_0927-project_refactor_plan2/plan.md)
>
> 本計畫原分為兩輪（2026-09-28 的 serve 拆分、2026-09-29 的 agent 建構統一），事後合併為一份；Part A、Part B 對應兩輪的範圍。

## Context

plan 2 讓 server 改用 `run_agent_build()` 建構 agent，並以可選參數 `run_manager` 共用 server 的 run context。當時 [pipelines/serve.py](../../../../src/website_copilot/pipelines/serve.py) 的呼叫鏈為：

```
serve() → run_server_build() → run_agent_build(run_manager=...)
```

留下的問題（[todo.md](../../todo.md)「專案結構重構 → plan 3」）：

- `run_server_build()` 同時負責建構 agent 與 server，兩個步驟綁在一起，無法單獨使用或測試。
- `run_agent_build()` 為了共用 context 多了 `run_manager` 參數與 `nullcontext()` 分支，兩種執行路徑的落盤行為不一致。
- `run_agent_query()`（[pipelines/exp.py](../../../../src/website_copilot/pipelines/exp.py)）自行載入 config、呼叫 `create_agent()`、寫 `module_config.toml`，與 `run_agent_build()` 重複；例外路徑在 `except` 與 `finally` 各呼叫一次 `agent.close()`。
- `run_agent_build()`／`run_agent_query()` 先 `AgentConfig.from_toml()`，`create_agent()` 內部又讀一次。
- `scripts/check.sh` 與 CI quality-check 從 plan 1 起就不會通過：卡在 `tests/unit/test_webpage_markdown_cleaner.py` 的 pyright 4 errors 與 1 個失敗測試，`git bisect run ./scripts/check.sh` 也因此無法使用。

目標：

1. `run_agent_build()` 脫離 `run_server_build()`，改由 `serve()` 直接呼叫；兩個 build 各自持有獨立的 `RunManager`。
2. 所有 agent 建構（serve、`run agent`）都經過 `run_agent_build()`，`AgentConfig` 只讀一次。
3. `check.sh` 全部通過。

## 已確認的決策

| 問題 | 決策 | 未採用的選項 |
|---|---|---|
| 兩個 build 各自建立 `RunManager`，會產生兩個不同時間戳的 `runs/<ts>/` 目錄 | **暫時接受**，兩個 run 放在不同目錄 | 讓 `RunManager` 可傳入 timestamp，兩者共用同一個 `runs/<ts>/` |
| server 的 run module 名稱 | **改為 `server`**（`runs/<ts>/server/<config>/`） | 維持 `agent` |
| server 目錄是否保留 `module_config.toml`（plan 2 新增） | **不保留**；agent 設定只寫在 `agent_build` 目錄 | 在 `run_server_build()` 中以 `agent.config` 補寫 |
| `run_server_build()` 取得 agent 的方式 | **注入**：參數改為接收 `agent`，`config_name` 由 `agent.config.config_name` 取得 | 保留 `config_name` 參數由呼叫端另外傳入 |
| `run_server_build()` 失敗時 agent 由誰關閉 | **建立者（`serve()`）關閉**；`run_server_build()` 不關閉注入的 agent。成功回傳後所有權轉交 `ChatServer`（同 plan 2） | `run_server_build()` 失敗時自行 `agent.close()` |
| `run agent` 改用 `run_agent_build()` 後的 run 目錄 | **比照 server**：`agent_build/<config>/` 放 `module_config.toml` 與建構日誌；`agent/<config>/` 放對話結果、`run_config.toml` 與日誌，**不寫** `module_config.toml` | `run_agent_build()` 可選擇不建立 run context（等於恢復已移除的 `run_manager` 參數） |
| `create_agent()` 的舊簽名 | **直接替換**為 `create_agent(config: AgentConfig)`，不保留 `config_name` 版本（改完後呼叫端只剩 `run_agent_build()`） | 保留 `config_name` 並新增另一個函式 |
| 檢查基線的修正方向 | **只改測試**，程式行為不變（程式已使用 `GenerationResult.hits`，是測試沒跟上） | — |

## 目標形狀

```python
def run_agent_build(config_name="default", run_config=None, **config_overrides) -> Agent:
    # 一律建立自己的 run context：runs/<ts>/agent_build/<config>/
    # config = AgentConfig.from_toml(...)；agent = create_agent(config)
    # 寫出 module_config.toml（與 run_config.toml，若有傳入）

def run_server_build(agent, run_config=None, allowed_origins=None,
                     host="127.0.0.1", port=8000) -> ChatServer:
    # 建立自己的 run context：runs/<ts>/server/<config>/
    # 只寫出 run_config.toml；對話結果由 server 的 _event_stream() 落盤於此

def serve(run_config: ServeRunConfig) -> None:
    agent = run_agent_build(run_config.config_name)
    try:
        server = run_server_build(agent, run_config=run_config, ...)
    except Exception:
        agent.close()
        raise
    try:
        server.run()          # ChatServer 結束時自動關閉 ChatApp / agent
    except KeyboardInterrupt:
        pass

def run_agent_query(config_name, query, ..., **config_overrides) -> None:
    agent = run_agent_build(config_name, **config_overrides)
    try:
        # 建立 runs/<ts>/agent/<config>/，問答並落盤對話結果與 run_config.toml
        ...
    finally:
        agent.close()         # 只關閉一次
```

## 執行步驟

### Part A：serve 拆分（2026-09-28）

#### A1. `run_agent_build()` 獨立 run context

- 移除 `run_manager` 參數與 `nullcontext()` 分支，一律走 `create_run_no_site_context(module="agent_build")` + `run_workflow_context`。
- 保留「落盤失敗時先 `agent.close()` 再 re-raise」的守衛。

#### A2. `run_server_build()` 接收注入的 agent

- 簽名改為 `run_server_build(agent, run_config=None, allowed_origins=None, host=..., port=...)`，移除 `config_name` 與 `**config_overrides`。
- `create_run_no_site_context(module="server", config_name=agent.config.config_name)`。
- 不再呼叫 `run_agent_build()`；失敗時只記錄 log 並 re-raise，不關閉 agent。
- 不寫 `module_config.toml`，只寫 `run_config.toml`。

#### A3. `serve()` 串接兩個 build

- 依序呼叫 `run_agent_build()` → `run_server_build(agent, ...)`，server build 失敗時關閉 agent。
- 更新 `pipelines/serve.py` 與 `server/server.py` 的模組 docstring。

#### A4. 測試

- [tests/unit/test_run_agent.py](../../../../tests/unit/test_run_agent.py)
  - 刪除 `test_run_agent_build_reuses_given_run_manager`。
  - `test_run_server_build_*` 改為傳入 mock agent，不再 patch `create_agent`／`run_agent_build`；斷言 `RunManager` 以 `module="server"` 建立、不寫 `module_config.toml`。
  - `test_run_server_build_closes_agent_when_chat_app_creation_fails` 改為斷言 `run_server_build()` **不**關閉 agent，關閉責任移到 `serve()` 的測試。
  - 新增 `serve()` 測試：兩個 build 的呼叫順序與參數；`run_server_build()` 失敗時 agent 被關閉且例外往外拋。
- [tests/unit/test_cli.py](../../../../tests/unit/test_cli.py) 的 serve 測試多 patch `run_agent_build`。
- [tests/integration/test_module.py](../../../../tests/integration/test_module.py) 改為先 `run_agent_build()` 再 `run_server_build(agent, ...)`。

#### A5. 文件

- README（專案結構註解、run 目錄說明）。
- `docs/code/runs/{workflow,config,cli}.md`、`docs/code/phase2_3_mvp/modules/{server,agent}.md`、`docs/project.md`：呼叫鏈、`run_server_build` 簽名、server run 目錄改為 `server/`、`module_config.toml` 只在 `agent_build/`。

### Part B：統一 agent 建構與恢復檢查基線（2026-09-29）

#### B1. 修正檢查基線

- `test_save_generated_exclude_words`：建立 `GenerationResult` 時補上 `hits={"Footer text": 10}`（[run_persistence.py](../../../../src/website_copilot/storage/run_persistence.py) 讀取 `result.hits[w]`，原本拋出 `KeyError`）。
- pyright 4 errors：`generate_exclude_words()` 回傳 `GenerationResult | None`，測試在存取 `.words`／`.votes`／`.cost_usd` 前先 `assert result is not None`。
- 完成後 `scripts/check.sh` 應全部通過，作為後續步驟的新基線。

#### B2. `create_agent(config: AgentConfig)`

- [agent/agent.py](../../../../src/website_copilot/agent/agent.py)：移除內部的 `AgentConfig.from_toml()`，`Tool(config.config_name)` 改由傳入的 config 取得名稱；更新模組與函式 docstring。
- `run_agent_build()` 以已載入（已套用覆寫）的 config 呼叫 `create_agent(config)`。
- 測試：`create_agent` 的斷言改為以 config 物件呼叫。

#### B3. `run_agent_query()` 改用 `run_agent_build()`

- 移除 `run_agent_query()` 內的 config 載入、`log_config`、`create_agent()` 與 `save_module_config_as_toml()`，改為 `agent = run_agent_build(config_name, **config_overrides)`。
- `run_agent_query()` 保留自己的 run context（`module="agent"`），負責問答、落盤對話結果、`run_config.toml`；不寫 `module_config.toml`。
- 關閉：`except` 只記錄 log 並 re-raise，`finally` 關閉一次 agent。
- 測試（`test_run_agent.py` 的 `run_agent_query` 區段）：patch 目標改為 `pipelines.exp.run_agent_build`；新增「例外路徑 `agent.close()` 只呼叫一次」與「不寫 `module_config.toml`」的斷言。

#### B4. 文件

- README（聊天記錄段落：`agent/` 不再有 `module_config.toml`，`run agent` 另產生 `agent_build/`）。
- `docs/code/runs/{workflow,config,cli}.md`、`docs/code/phase2_3_mvp/modules/agent.md`：`run_agent_query` 經 `run_agent_build`、`create_agent(config)` 簽名、`module_config.toml` 只在 `agent_build/`。
- 本目錄 `dev.md` 記錄實作過程。

## 行為變更

1. `website-copilot serve` 一次啟動會產生兩個 run 目錄：`runs/<ts1>/agent_build/<config>/` 與 `runs/<ts2>/server/<config>/`，兩者的時間戳可能不同。
2. server 的 run 目錄由 `agent/` 改為 `server/`，且不再寫出 `module_config.toml`（撤銷 plan 2 的行為變更）。
3. **對話歷史的跨 run 查找範圍改變**：`RunManager.save_agent_results_as_json()` 以 `find_thread_history_path(base_folder, module_name, ...)` 跨 run 目錄搜尋同一個 thread 的歷史。module 改為 `server` 後，server 只會找到 `runs/*/server/` 底下的歷史，不再讀到舊的 `runs/*/agent/`（舊版 server 與 `website-copilot run agent`）的歷史。`run_agent_query()` 仍使用 `agent`，不受影響。
4. `website-copilot run agent` 一次執行同樣產生兩個 run 目錄：`runs/<ts1>/agent_build/<config>/` 與 `runs/<ts2>/agent/<config>/`；`agent/` 不再寫出 `module_config.toml`。
5. 簽名改變：`run_server_build()` 第一個參數改為 `agent`，失敗時不再關閉 agent；`create_agent()` 改為 `create_agent(config: AgentConfig) -> Agent`。

## 驗證

**每步檢查**：Part A 期間以 `scripts/lint.sh`、`scripts/test.sh -m "not slow"` 檢查，錯誤數不得高於基線；Part B 的 B1 完成後改用 `scripts/check.sh`（lint + test + widget），之後每一步都必須全部通過。

**個別驗證**：

- 實際執行 `website-copilot serve`，確認產生 `agent_build/` 與 `server/` 兩個 run 目錄，且各自的 `terminal.log`、`run_config.toml`／`module_config.toml` 符合預期；送出一次 `/api/chat` 確認對話落盤在 `server/` 目錄；中斷後確認 agent 有被關閉。
- 實際執行 `website-copilot run agent --run.query "你好" --run.config-name test`，確認產生 `agent_build/`（`module_config.toml`）與 `agent/`（`results_<thread_id>.json`、`run_config.toml`，無 `module_config.toml`）。

**完成後**：`grep` 確認 `run_agent_build(.*run_manager`、`module="agent"`（`pipelines/serve.py`）、`create_agent(config_name`、`run_agent_query` 內的 `create_agent(` 在 `src`、`tests`、README、`docs/code` 中無殘留（`docs/work` 的歷程紀錄不改）。
