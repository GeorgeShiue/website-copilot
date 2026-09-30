# Development Log

> 對應規劃文件：[plan.md](./plan.md)；前一輪（plan 1）實作紀錄見 [2026_0926-project_refactor/dev.md](../2026_0926-project_refactor/dev.md)

分支 `dev-tech-debt-refactor`，全部變更收在一個 commit：

| Commit | 內容 |
|---|---|
| `590c94e` | 起點的 pipelines 重組 + plan 2 五點 + 過程中追加的工具調整 |

使用者先把起點變更 commit 為 `wip: project refactor adjusment`（`5b057b7`），之後每完成一點、經使用者確認，就 amend 進同一個 commit；最後依全部內容改寫 commit message。

---

## 基線

- `pytest -m "not slow"`：失敗的只有 `test_webpage_markdown_cleaner.py::test_save_generated_exclude_words`（`KeyError: 'Footer text'`），在 HEAD 上同樣失敗，與 plan 1 的基線相同。
- `pyright`：4 errors，皆在同一個測試檔（`reportOptionalMemberAccess`）。
- `ruff check` / `ruff format --check`：通過。

---

## 起點：補齊 staged 重組

- **測試的 patch 目標**：import 已改，但 `test_run_agent.py` 約 60 個 `@patch` 仍指向 `pipelines.agent.*` / `server.bootstrap.*`，會全數失敗。依函式所在位置拆分：`run_agent_build` 與 server 測試改 patch `pipelines.serve`，`run_agent_query` 測試改 patch `pipelines.exp`。`test_cli.py` 的 serve / agent 分派、中斷關閉、「serve 路徑不載入爬蟲」檢查的模組名同步修正。
- **docstring**：`pipelines/serve.py` 的模組說明是從舊 agent 模組複製過來的，`server/server.py` 仍寫 `run_app` / `serve_forever`，兩者重寫；`pipelines/exp.py`、`storage/run_context.py`、`agent/agent.py` 的說明更新；移除新增檔案結尾多餘的空行。
- **文件**：README 檔案結構樹（移除 `bootstrap.py`、`scripts/multi_site.py`，加入 `server.py`、`pipelines/serve.py`）、`docs/project.md`、`docs/code/runs/{workflow,cli,config}.md`、`docs/code/phase2_3_mvp/{phase2_3_mvp,modules/agent,modules/server}.md` 的路徑、函式名稱與所在模組。

**驗證**：ruff 通過；277 passed / 1 failed（基線那個）。

---

## 1. server 建置 agent 改為呼叫 `run_agent_build()`

- `run_agent_build(config_name, run_config=None, run_manager=None, **config_overrides) -> Agent`：
  - 傳入 `run_manager` 時以 `nullcontext()` 取代 `run_workflow_context`，不另建目錄與 log；`None` 時照舊建立 `agent_build` context。型別標註為 `AbstractContextManager[object]`，讓兩種 context 共用一個變數。
  - 回傳**未關閉**的 agent，由呼叫端負責 `close()`。
  - agent 建立後若落盤失敗，先 `agent.close()` 再 re-raise（plan 決策外補上，避免 RAG 資源外洩）。
- `run_server_build()` 改為 `run_agent_build(config_name, run_manager=run_manager, **config_overrides)`。

**行為變更**：server 的 run 目錄 `runs/<ts>/agent/<config>/` 現在會寫出 `module_config.toml`（先前不寫）。README、`runs/{workflow,cli,config}.md`、`modules/{agent,server}.md` 中「server 不經 `run_agent_build`」「server 不寫 `module_config.toml`」的描述同步更新。

測試：

- `run_agent_build` 測試改為斷言「回傳 agent 且未關閉」；新增「傳入 `run_manager` 時不另建 RunManager」「落盤失敗時關閉 agent」。
- server 的 3 個測試原本未 patch `save_module_config_as_toml`，改動後會真的寫出 `fake_module_config.toml`，補上 patch；並斷言 `module_config.toml` 寫在 server 自己的 run 目錄。

**驗證**：279 passed / 1 failed。

---

## 2. `ChatServer` 退出自動清理 `ChatApp`

- `ChatServer(config, chat_app)` 持有 `ChatApp`，覆寫 `serve()`：`try: await super().serve()` / `finally: chat_app.close()` 並印出 Server Stopped（由 `serve()` 移入）。
  - 實作前確認 uvicorn 0.52.1 的 `run()` 即 `asyncio.run(self.serve())`，因此阻塞的 `server.run()` 與 `await server.serve()` 兩種啟動方式都涵蓋。
- `run_server_build()` 只回傳 `ChatServer`。
- `serve()` 移除 `finally: chat_app.close()`，**保留 `except KeyboardInterrupt`**：uvicorn 的 `capture_signals` 在 serve 結束後會重新發出 SIGINT，不接住終端機會印出 traceback。

測試：

- 新增 `test_chat_server_serve_closes_chat_app_on_exit`，參數化正常結束 / `KeyboardInterrupt` / `RuntimeError` 三種情況，確認都會關閉 `ChatApp` 且例外照常往外拋。第一次把 `KeyboardInterrupt` 類別（而非實例）傳給 `pytest.raises(type(...))` 導致失敗，改為 `KeyboardInterrupt()`。
- `test_run_server_build_*` 改從 `server.chat_app` 取得 ChatApp；`handle_exit` 測試補上 `chat_app` 參數。
- `test_cli.py` 的 serve 測試改為「呼叫 `run()` 並吞下 KeyboardInterrupt」；`tests/integration/test_module.py` 移除手動 `chat_app.close()`（slow 測試，未執行）。

**冒煙驗證**：在 scratchpad 以假的 `ChatApp` 啟動真實 `ChatServer`，1.5 秒後送出 SIGINT，輸出順序為 Server Stopping → `ChatApp` 關閉 → Server Stopped，且 `KeyboardInterrupt` 傳到 `run()` 外，確認 `serve()` 的 `except` 仍然需要。

文件：README 目錄樹、`docs/project.md`、`runs/{workflow,cli}.md`、`phase2_3_mvp` 下的資源生命週期描述改為「由 `ChatServer` 結束時關閉」；`modules/server.md` 檔案清單補上 `server/server.py` 與 `pipelines/serve.py`。

**驗證**：282 passed / 1 failed。

---

## 3. Makefile → `scripts/`

依使用者要求調整了兩次：先把 `check.sh` 拆成三組，再把 `format.sh` 併入 `lint.sh --fix` 並刪除 `format.sh`。最終腳本（皆 `set -euo pipefail`、先切到專案根目錄；git mode `100755`）：

| 腳本 | 內容 |
|---|---|
| `check.sh` | 依序執行 `lint.sh` → `test.sh` → `check-widget.sh`，任一組失敗即中止 |
| `lint.sh [--fix]` | `ruff check`、`ruff format --check`、`pyright`；`--fix` 改為 `ruff check --fix` + `ruff format`；其他參數印出用法並回傳 2 |
| `test.sh [pytest args]` | `pytest -m "not slow"`，額外參數傳給 pytest |
| `check-widget.sh` | 比對兩份 `widget.js`，不一致時提示執行 `sync-widget.sh` |
| `sync-widget.sh` | 複製 `server/static/widget.js` 到 `extension/` |
| `clean-runs.sh [--dry-run] [--yes]` | 見下 |

### 清理 runs 腳本

- `runs/` 第一層為 `YYYYMMDD_HHMMSS`，由 `RunManager` 以 `time.strftime("%Y%m%d_%H%M%S")`（本地時間）產生。
- 只刪除**名稱完全符合此格式**且日期早於今天（`date +%Y%m%d`）的資料夾，其他項目一律保留。
- 刪除前列出清單與合計大小並詢問 `[y/N]`；`--dry-run` 只列出、`--yes` 略過確認；環境變數 `RUNS_DIR` 可指定其他目錄。
- 注意：agent 的 `results_<thread_id>.json` 會跨 run 累積同一 thread 的歷史，清理後舊 thread 的歷史一併移除（已寫入 README）。

**驗證**：

- `sync-widget.sh` 從 `/tmp` 執行正常，執行後無 diff；`check-widget.sh` 通過；`test.sh -q tests/unit/test_cli.py` 15 passed（參數有傳入）；`lint.sh --bad` 回傳 2；`lint.sh --fix` 未改動任何檔案。
- `check.sh` 在 `lint.sh` 的 pyright 停下：4 errors 皆為基線。pyright 同時確認第 1、2 點的程式碼沒有型別錯誤。
- `clean-runs.sh` 在 scratchpad 以假目錄（舊日期、今天、`notes/`、`2026_backup/`、`readme.txt`）測試：回答 n 不刪、回答 y 只刪兩個舊 run、再跑一次顯示無需清理。真實 `runs/` 只跑 `--dry-run`：79 個、61M，未刪除。

文件：README 目錄樹（移除 Makefile、加入 `scripts/`）、「執行測試」與「開發」章節；`interface.md`、`phase2_3_mvp.md` 的 `make sync-widget` / `make check-widget`。刪除殘留的 `scripts/__pycache__`。plan 1 的 `plan.md` / `dev.md` 中的 `make` 為當時紀錄，不改。

---

## 4. Gemini API key 統一為 `GEMINI_API_KEY`

原本三個變數：`GEMINI_RAG_QUERY_ENGINE_API_KEY`、`GEMINI_RAG_EVALUATOR_API_KEY`、`GEMINI_WEBPAGE_IMAGE_SUMMARIZER_VLM_API_KEY`。

- `retrieval/llama_index_helpers.py`：`LLM_API_KEY_ENV_VARS` 由「供應商 → 用途 → 變數」簡化為「供應商 → 變數」；`create_llm()` 的 `usage` 參數統一後已無作用，一併移除，唯一有傳入的 `retrieval/evaluation.py` 同步修改。
- `agent/langchain_helper.py`：agent 改讀 `GEMINI_API_KEY`（錯誤訊息、docstring 同步）。
- `config/webpage_image_summarizer_config.py`：`VLM_MODEL_TO_API_KEY["gemini"]`。
- `.env.example`：三個變數合併為一個。
- `ci.yml` / `ci-test.yml`：兩行寫入 `.env` 合併為 `GEMINI_API_KEY=${{ secrets.GEMINI_API_KEY }}`；GitHub secret 本來就叫這個名字，不需修改。
- 文件：README 環境變數表、`modules/agent.md`、`phase1/modules/data_retrieve.md`（引用的是現行的 `llama_index_helpers`，仍在維護，因此一併更新）。

本機 `.env` 含金鑰，未讀取也未修改。

**驗證**：`pyright src` 0 errors；282 passed / 1 failed；除 `docs/work` 等歷程紀錄外無舊變數名殘留。

---

## 5. `pyproject.toml`（dependency、ruff）

### 依賴：沒有可移除的套件

以 AST 掃描 `src`、`tests` 的第三方 import，對照 `importlib.metadata.packages_distributions()` 與 `uv tree`。所有宣告的套件都有用到；沒有直接 import 的幾個：

| 套件 | 用途 |
|---|---|
| `flagembedding` | `BGEM3SparseEmbeddingFunction.__init__` 執行時 import `FlagEmbedding`，沒裝就 `sys.exit(1)` |
| `playwright` | crawl4ai 本身也依賴它，但 CI 直接執行 `playwright install` 指令，保留直接宣告 |
| `milvus-lite` | 本機 Milvus DB；`==3.2.0` 為刻意固定 |
| `mdformat-gfm` | 由 `mdformat` 以 `extensions={"gfm"}` 載入 |
| `llama-index` | meta 套件，帶入實際使用的 core、embeddings-openai |
| `httpx`（dev） | FastAPI `TestClient` 需要 |

盤點時也發現（未處理，使用者未選）：`langchain-core`、`pydantic`、`llama-index-core`、`llama-index-embeddings-openai`、`huggingface-hub` 被直接 import 但只靠傳遞依賴安裝；部分版本下限與 lock 差距大（如 `langchain-openai>=0.3.0`，lock 為 1.6.1）；`description` 仍為範本文字。

### Ruff：`exclude` → `extend-exclude`

- 原本的 `exclude = [".venv"]` 會**取代** ruff 內建的預設排除清單（`.git`、`build`、`dist`、`node_modules` 等），實際只排除 `.venv`。以 `ruff check --show-settings` 確認。
- 改為 `extend-exclude = [".venv", "runs", "chats", "data", "docs", "extension"]`（附註解），保留內建預設。
- 改後 `ruff check --show-files` 只剩 `src/`、`tests/` 與 `pyproject.toml`。
- 盤點時試跑 `--select E,F,W,I,UP,B --statistics`：95 個問題（E501 66、UP006 9、UP035 8、I001 5、UP015 4、B008 2、B017 1），24 個可自動修正；使用者決定規則組維持預設。

### 對照 prek 設定的追加調整

- **ruff 版本漂移**：prek hook 為 `ruff-pre-commit` `rev = "v0.15.0"`（獨立環境），`uv run ruff` 為 uv.lock 的 0.15.12。改為 `repo = "local"` hook，以 `uv run ruff check --force-exclude --fix` / `uv run ruff format --force-exclude` 執行。`prek validate-config` 通過，`prek run --files` 兩個 hook 皆執行並通過。
- **CI 未檢查格式**：CI 原本只跑 `ruff check .` 與 `pyright .`，兩個步驟合併為 `./scripts/lint.sh`，CI 因此也檢查 `ruff format --check`；widget 檢查步驟的 `cmp` 改為 `./scripts/check-widget.sh`。`interface.md` 的 CI 描述同步更新。
- 確認維持不變的部分：ruff-pre-commit 原生 hook 的 entry 即帶 `--force-exclude`（查本機 prek 快取的 `.pre-commit-hooks.yaml`），local hook 沿用；`check --fix` 在 `format` 之前為官方建議順序；`types_or` 去掉 `jupyter` 沒有影響（專案無 notebook）。

**驗證**：ruff check / format 通過；282 passed / 1 failed。

---

## 最終狀態摘要

- **serve 路徑**：`serve()` → `run_server_build()`（`run_agent_build(run_manager=...)` 在同一 run context 建構 agent，寫出 `module_config.toml` 與 `run_config.toml`）→ 回傳 `ChatServer` → `server.run()`；`ChatServer.serve()` 結束時自動 `chat_app.close()`。
- **exp 路徑**：`run_rag_query`、`run_agent_query`（仍直接呼叫 `create_agent()`）與批次實驗在 `pipelines/exp.py`。
- **工具**：本機與 CI 共用 `scripts/lint.sh`、`scripts/check-widget.sh`；prek、`lint.sh`、CI 的 ruff 版本與設定一致。
- **測試數**：277 → 282 passed（新增 `run_agent_build` 共用 context / 失敗關閉、`ChatServer` 清理測試），基線失敗的 1 個與 pyright 4 errors 維持不變。

## 遺留事項

- **本機 `.env`**：需把三個舊 Gemini 變數改為 `GEMINI_API_KEY`；未改名時 gemini 模型會讀不到金鑰（目前預設設定使用 gpt，不受影響）。
- **`check.sh` 與 CI quality-check 目前不會通過**：卡在基線的 pyright 4 errors 與 1 個失敗測試（皆在 `test_webpage_markdown_cleaner.py`）。修正前 `git bisect run ./scripts/check.sh` 無法直接使用。
- **pyright 的 `exclude`** 未比照 ruff 擴充（`runs`、`data` 等未排除），需要時再對齊。
- **未執行**：`pytest -m slow tests/integration`（真實爬蟲與付費 API）。
- **force push**：amend 後的 `590c94e` 若分支已 push，需 `git push --force-with-lease`。

## 過程中的操作失誤

- 為確認「失敗的測試是否為基線」，以 `git stash` / `git stash pop` 暫時還原工作區。`stash pop` 未加 `--index`，檔案內容雖完整恢復，但原本的 staged / unstaged 區分遺失，全部變成 unstaged。嘗試以 `git read-tree <stash 的 index commit>^{tree}` 還原 staging 時被權限拒絕，改為告知使用者還原指令；使用者隨後自行 commit 為 `5b057b7`。之後不再用 stash 切換工作區判斷基線。
