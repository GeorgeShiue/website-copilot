# 專案結構重構 plan 2：serve 生命週期收斂與開發工具整理

> 前一輪（plan 1，phase A–E）見 [2026_0926-project_refactor/plan.md](../2026_0926-project_refactor/plan.md)；本輪實作紀錄見 [dev.md](./dev.md)

## Context

plan 1 完成 `src/website_copilot/` 重組後，使用者再調整 pipelines 的分組（已 stage）：

- `server/bootstrap.py` → `pipelines/serve.py`；`run_app` → `run_server_build`、`serve_forever` → `serve`。
- 刪除 `pipelines/agent.py`：`run_agent_build` 移到 `pipelines/serve.py`（serve 階段），`run_agent_query` 移到 `pipelines/exp.py`（實驗／除錯用）。
- 刪除 `scripts/multi_site.py`。

這次重組後留下幾個問題，列為 [todo.md](../../todo.md)「專案結構重構 → plan 2」：

- server 仍自行呼叫 `create_agent()`，沒有經過同一模組裡的 `run_agent_build()`；agent 的關閉責任散在呼叫端（`serve()` 的 `finally`、整合測試的 `finally`）。
- Makefile 的指令與 CI 各自維護，CI 沒有檢查格式。
- Gemini 的 API key 分成三個環境變數，實際上都是同一把金鑰。
- `pyproject.toml` 的依賴與 ruff 設定需要檢視。

目標：收斂 serve 路徑的 agent 建構與關閉責任，把開發指令整理成本機與 CI 共用的腳本，並統一金鑰與工具設定。**執行行為的刻意變更只有兩項**：server 的 run 目錄多寫出 `module_config.toml`；`run_server_build()` 的回傳值改為只回傳 `ChatServer`。

## 範圍

todo 在過程中有調整：原本獨立的「新增清理 runs 腳本」併入第 3 點；「更新 gemini api key 環境變數名稱」改寫為「統一為 `GEMINI_API_KEY`」。最終五點：

1. server 建置 agent 改為呼叫 `run_agent_build()`
2. `ChatServer` 退出自動清理 `ChatApp`
3. 捨棄 Makefile，將常見指令整理在 `scripts/` 底下的腳本（含清理 runs 腳本）
4. 統一所有 gemini api key 環境變數名稱為 `GEMINI_API_KEY`
5. `pyproject.toml` 更新（dependency、ruff）

進行方式：依序處理，每完成一點就回報，經使用者確認後 amend 進同一個 commit；遇到需要取捨的設計問題先提問。

## 已確認的決策

| 點 | 問題 | 決策 | 未採用的選項 |
|---|---|---|---|
| 1 | server 呼叫 `run_agent_build()` 時的 run context | **共用**：新增可選參數 `run_manager`，傳入時沿用呼叫端的 context | 各自獨立 context（一次啟動產生兩個 run 目錄、logging 巢狀）；抽出不含 context 的 `_build_agent()`（server 不直接呼叫 `run_agent_build`） |
| 1 | `run_agent_build()` 的回傳與關閉 | **回傳未關閉的 `Agent`**，由呼叫端 `close()`；只改 server | `run_agent_query()` 也改用它 |
| 2 | `run_server_build()` 的回傳值 | **只回傳 `ChatServer`**，`ChatApp` 經 `server.chat_app` 取得 | 維持 `(server, chat_app)` tuple |
| 3 | 腳本形式 | **一個指令一支 bash** | 單一分派腳本 `dev.sh <cmd>`；Python 腳本 |
| 3 | 做成腳本的指令 | `check`、`format`、`sync-widget`；`install`、`serve` 等單行指令在 README 寫原始 `uv` 指令 | 全部做成腳本 |
| 3 | `check.sh` 的組織（使用者追加） | 拆成 `lint.sh`（ruff check、ruff format、pyright）、`test.sh`（pytest）、`check-widget.sh` 三組，`check.sh` 依序呼叫 | 單一腳本 |
| 3 | `format.sh` 併入 `lint.sh`（使用者追加） | **加 `--fix` 參數**：預設只檢查，`check.sh` / `git bisect run` 不改檔 | `lint.sh` 一律自動修正 |
| 3 | 清理 runs 的範圍 | 刪除 `runs/` 中名稱為 `YYYYMMDD_HHMMSS` 且日期早於今天的資料夾 | — |
| 5 | 依賴 | **只移除沒用到的套件** | 補宣告直接 import 的傳遞依賴；下限對齊 lock；填寫 description |
| 5 | Ruff | **擴充不需檢查的路徑** | 啟用 E/F/W/I/UP/B 規則組；只加 import 排序 |
| 5 | 對照 prek（使用者追加） | prek 的 ruff 改為 `uv run` 的 local hook；CI 改用 `scripts/lint.sh`、`scripts/check-widget.sh` | 只把 `rev` 改成與 uv.lock 相同版本 |

## 執行步驟

### 起點：補齊 staged 重組

- 測試的 patch 目標依函式所在位置改指 `pipelines.serve` / `pipelines.exp`。
- 模組 docstring（`pipelines/serve.py`、`server/server.py`、`pipelines/exp.py`、`storage/run_context.py`、`agent/agent.py`）改為新名稱與新職責。
- README 與 `docs/code/**`、`docs/project.md` 的路徑與函式名稱。

### 1. `run_agent_build()` 共用 run context

- `run_agent_build(config_name, run_config=None, run_manager=None, **config_overrides) -> Agent`：有 `run_manager` 時以 `nullcontext()` 沿用呼叫端的 context；沒有時照舊建立 `agent_build` context。
- 建立 agent 後若落盤失敗，先 `agent.close()` 再 re-raise。
- `run_server_build()` 改呼叫 `run_agent_build(run_manager=run_manager)`；server 的 run 目錄因此寫出 `module_config.toml`。

### 2. `ChatServer` 持有並關閉 `ChatApp`

- `ChatServer(config, chat_app)`；覆寫 `serve()`，以 `try/finally` 在結束時呼叫 `chat_app.close()`。uvicorn 的 `run()` 內部就是 `asyncio.run(self.serve())`，兩種啟動方式都涵蓋。
- `run_server_build()` 只回傳 `ChatServer`；`serve()` 與整合測試移除手動 `chat_app.close()`，`serve()` 保留 `except KeyboardInterrupt`。

### 3. `scripts/`

- 刪除 Makefile，新增 `check.sh`、`lint.sh [--fix]`、`test.sh [pytest args]`、`check-widget.sh`、`sync-widget.sh`、`clean-runs.sh [--dry-run] [--yes]`。
- 所有腳本 `set -euo pipefail` 並先切到專案根目錄，可從任意目錄執行。
- `clean-runs.sh` 刪除前列出清單與大小並確認；不符合命名格式的項目一律保留。

### 4. `GEMINI_API_KEY`

- 程式：`llama_index_helpers.LLM_API_KEY_ENV_VARS` 簡化為「供應商 → 變數」，移除 `create_llm()` 失去作用的 `usage` 參數；`langchain_helper`、`VLM_MODEL_TO_API_KEY` 改讀 `GEMINI_API_KEY`。
- `.env.example`、CI 寫入 `.env` 的步驟、README 與 `docs/code` 的環境變數說明。
- 本機 `.env` 含金鑰，由使用者自行改名。

### 5. `pyproject.toml` 與工具一致性

- 逐一確認沒有直接 import 的依賴是否在執行時使用，移除沒用到的。
- ruff 的 `exclude` 改為 `extend-exclude`，保留內建預設排除，另外排除 `runs`、`chats`、`data`、`docs`、`extension`。
- prek 的 ruff 改為 local hook（`uv run ruff ... --force-exclude`），版本由 uv.lock 決定。
- CI 的 lint、type check、widget 檢查改為執行 `scripts/lint.sh`、`scripts/check-widget.sh`。

## 驗證

**每點檢查**：

1. `uv run ruff check .`、`uv run ruff format --check .`。
2. `uv run pyright`：錯誤數不得高於基線（4 errors，皆在 `test_webpage_markdown_cleaner.py`）。
3. `uv run pytest -m "not slow"`：通過數不少於前一點，失敗只能是基線那 1 個。

**個別驗證**：

- 第 2 點：以真實 `ChatServer` 搭配假的 `ChatApp` 送出 SIGINT，確認 `ChatApp` 有被關閉。
- 第 3 點：各腳本單獨執行；`clean-runs.sh` 只在 scratchpad 的假目錄實際刪除，真實 `runs/` 只跑 `--dry-run`。
- 第 5 點：`ruff check --show-settings` 確認排除清單；`prek validate-config` 與 `prek run --files` 確認 hook。

**完成後**：`grep` 確認 `pipelines.agent`、`server.bootstrap`、`serve_forever`、`run_app`、`make `、舊 Gemini 變數名在 `src`、`tests`、`.github`、README、`docs/code` 中無殘留（`docs/work` 的歷程紀錄不改）。
