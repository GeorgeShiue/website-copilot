# 專案結構重構：實作紀錄

> 對應規劃文件：[plan.md](./plan.md)。只記錄與 plan 不同的決定、過程中的發現與驗證結果、遺留事項；設計本身見 plan。

分支 `dev-tech-debt-refactor`（= `dev-tech-debt` + plan commit `6120df2`；plan 原寫在 `dev-tech-debt` 上另開 `refactor/project-layout`，因此直接在此分支實作）。

| 階段 | Commit | 內容 |
|---|---|---|
| 1 Phase A | `fd12aeb` | 安全網：基線、import 冒煙測試、serve 載入特性測試 |
| 1 Phase B | `e84f6dd` | 純搬移到 `src/website_copilot/` |
| 1 Phase C | `a8db3fd` | RAG 拆成 indexing／retrieval，回傳式建構 |
| 1 Phase D | `2173629` | `website-copilot` CLI、入口邏輯下移 |
| 1 Phase E | `b3805d8` | widget 同步、清理 `dev/`、`.env.example`、文件 |
| 2 | `590c94e` | pipelines 重組＋plan 2 五點（使用者先 commit 起點為 `5b057b7`，之後每點確認後 amend） |
| 4 | — | `refactor: remove redundant files, rename to ImageSummarizer (plan 4)` |
| 5 | — | `test: restructure tests for new project layout, rename slow marker to cost`（第 4、5 節分次 amend；要取回已刪測試，從其父 commit `0c3dbda` 取） |

基線（plan 1 開始前）：`pytest -m "not slow"` 203 passed／1 failed（`test_webpage_markdown_cleaner.py::test_save_generated_exclude_words`，`GenerationResult` 未帶 `hits` 導致 `KeyError`）；`pyright` 4 errors（同一測試檔）；ruff 通過。plan 3 B1 修正後 `check.sh` 才首次通過。

---

## 0. Prepare／Serve 拆分

### 起點：先確認問題是否存在

逐一查證 4 個耦合點：追蹤 `RAGRegistry.get()` → `build_to_retriever(force_rebuild=False)` → `_should_rebuild()`，確認 `milvus.db` 不存在時會走完整建置；`list_sites()` 確實掃描 `data/webpages/`；`create_rag()` 只在 `run_manager` 非 None 時覆寫 `milvus_uri`，`save=False` 因此原地重建（`milvus.db` 實際是資料夾，走 `rmtree`＋`copytree`）。

### 步驟 3、1

- `load_to_retriever()` 疊在 `build_to_retriever(force_rebuild=False)` 之上，只多一道存在性檢查；`list_sites()` 改掃 `data/rag/` 並以 `_site_exists()` 過濾，空資料夾不列出。
- `main.py` 以 `git mv` 保留歷史；`ServerCLI` 整個移除（非保留轉發）；`serve.py` 沿用既有 `ServerRunConfig`。
- 驗證：`RAGRegistry().list_sites()` 回傳 `['claudecode', 'ncucsie', 'nculab']`（`base_folder="data"` 為相對路徑，從 `src/` 執行會得到 `[]`）。

### 步驟 4：規則修正與實作補充

原規劃在 `save=False` 時一律建到 `data/rag/{site}/.staging/`，使用者指出這違反「`save=False` 就不保存」，改為 `publish=True` 才用 `data/` 底下的 staging（為同檔案系統 rename），`publish=False` 用系統暫存資料夾。

- 建庫位置在 `run_rag_build` 決定；`create_rag` 本身不改。
- `publish_vector_store(move=...)`：先清前次中斷殘留的 `.tmp`／`.old`；替換中途失敗時若舊版已成 `.old` 而正式路徑不存在，就改回原名再 re-raise（規劃沒寫，實作時補上）。
- 發布到 `data/` 的 `module_config.toml` 會序列化 `milvus_uri`，因此 publish 後把它改為正式路徑再寫 metadata；`runs/` 的仍記錄 `runs/` 路徑。
- `test_run_rag_build_publish.py` 改寫為 8 個測試（四種組合、替換舊庫、建庫失敗、替換中途失敗、無向量庫仍 publish metadata），並以 `monkeypatch` 導向 `tempfile.tempdir` 才能驗證暫存被清掉。
- 順帶修正 `multi_site.py` 呼叫已不存在的 `run_rag_build(force_rebuild=True)`。

### 步驟 2：workflow 拆分

以腳本依函式行號切出三個模組，各自只保留需要的 import，原 `workflow.py` 直接 `git rm`（不保留 re-export）。

**踩到的問題**：`sed 's/app\.workflow\.workflow/.../'` 同時把 `app.workflow.workflow_helper` 改成 `serve_workflow_helper`／`prepare_workflow_helper`，17 個測試失敗。之後批次替換模組路徑應加字尾邊界。

import 隔離驗證：`import serve` 後 `crawl4ai`、`playwright`、爬蟲／摘要模組皆未載入；`import prepare` 後 `uvicorn`、agent、server、`langgraph` 皆未載入。`import prepare` 會載入 `fastapi`，經 `-X importtime` 追查是 `litellm.integrations` 經 `starlette` 引入，屬第三方依賴。

### 文件與驗證

README、`docs/code/**`、程式碼 docstring 同步更新；`todo.md` 勾選並新增兩個後續待辦。ruff 通過，pyright 4 errors（基線），203 passed／1 failed（基線），210 個測試可收集。**未執行** slow 端對端測試與完整 prepare／server。

---

## 1. 標準 src layout（plan 1）

### Phase A

- `test_imports.py` **偏離 plan**：不用 `pkgutil.walk_packages`，改以檔案系統掃描，因為 `configs/`、`engines/`、`utils/` 沒有 `__init__.py`（namespace package），`walk_packages` 會整個略過。
- `test_serve_rag_loading.py` **偏離 plan**：plan 寫 patch `RAGBuilder` 為 fake，實作改為只 patch 外部資源（Milvus、embedding、index、retriever），讓真實建構流程被測到；C2 因此只需改 patch 路徑。
- 驗證：新增 42 個測試，245 passed／1 failed。

### Phase B

每步的 `sed` 指令完整記錄在 `e84f6dd` 的 commit message。非純搬移、需留意的三處：

1. **logger 名稱**：`setup_logging` 以字串 `"website_copilot.engines.rag"` 設定等級，搬移後不對應任何模組，RAG debug log 會悄悄失效，因此展開成三個模組的新名稱（C3 再改為套件層級）。
2. `engines/rag/__init__.py` 的重新匯出改為直接 import；`retrieval/__init__.py` 刻意留空，因為 B6 時 indexing ↔ retrieval 仍互相依賴，放重新匯出會循環 import。
3. 測試副作用：serve 載入 Milvus 會在 `data/rag/<site>/milvus.db/.../indexes/` 產生未追蹤的快取，每次驗證後刪除。

驗證：251 passed／1 failed；43 個模組逐一在新 interpreter 單獨 import（pytest 共用 process 可能掩蓋循環 import）；里程碑 `serve.py` → `/api/health`、`/api/chat` SSE、`demo.html` 皆正常。

### Phase C

- C3 的 `IndexBuilder.build()` 只在重建時讀取 webpages 來源，且在清除舊向量庫**之前**讀取（`results.json` 不存在就直接失敗，舊庫不受影響，與舊版順序相同）。
- plan 未寫、實作時補上：`RAG.evaluate` 移到 `evaluation.evaluate_response(evaluators, query, response)`（因 `RAG` 不再持有 evaluators）；**資源釋放**：回傳式建構後，建置中途失敗不會隨 `rag.close()` 關閉 Milvus client，改由 `IndexBuilder.build/load` 與 `RAGBuilder.build` 失敗時主動關閉。
- `test_run_rag_build_publish.py` 只 fake `create_rag`（簽名與回傳不變），未改寫也通過（plan 原寫要改寫）。
- **使用者追加變更**（amend 進 `a8db3fd`）：`retrieval/builder.py`＋`loader.py` 合併為 `factory.py`；`helpers.py` → `llama_index_helpers.py` 並把 `RAG._log_sources` 移為 `log_source_nodes`；`SourceDocs`／`load_source_docs` → `Source`／`load_source`；embedding 模型改由 `IndexBuilder._create_embed_model` 建立；`log_prepare_workflow_run_summary` → `log_run_summary`。
- 驗證時發現並修正**循環 import**：`llama_index_helpers.py` 寫了 `from ...retrieval.rag import logger`（疑為搬移時編輯器自動補的 import），而 `rag.py` 又 import 它，8 個測試檔收集失敗，改為自建 logger。
- 驗證：259 passed／1 failed；48 個模組單獨 import 成功。里程碑：把 `data/webpages/` 改名後啟動 serve，`/api/chat` 與 `demo.html` 正常（serve 確實不再需要 webpages）；`rag-build`（test config）47 份文件 → 274 nodes，與重構前一致；`rag-query` 含評估 Faithfulness／Relevancy 皆 1/1。

### Phase D

- D1：圖片摘要實驗改在函式內延遲 import `pipelines.prepare`，避免 rag-query 路徑載入爬蟲依賴；`setup_logging` 留在入口層（原本 `exp.py` 在 import 時就呼叫）。
- D2：以 `tyro.conf.subcommand` 命名子命令，`run` 底下第二層 union 用 `tyro.conf.arg(name="")` 讓參數維持 `--run.*`／`--module.*`，實作前先以小腳本確認 tyro 1.0.13 的巢狀行為。`exp` 的名稱為 `Literal` 位置參數，在 CLI 端列出而不 import pipelines，由測試比對與 `EXPERIMENTS` 一致。`cli/__main__.py` 加 `if __name__ == "__main__"`（冒煙測試因此抓到一次失敗）。拿掉 `pythonpath` 後確認 `.venv` 內為 editable install。
- **修正 `run_config.toml` 未記錄 `save`／`publish`**：舊 `src/cli.py` 以 `vars(cli_arg.run)` 後直接 `pop`，等於刪除 run config **物件本身**的屬性，`run_config.toml` 從未記錄兩欄位，且之後讀取會落回類別預設值 `False`。D2 起初為維持「行為不變」保留並回報，使用者決定修正，改 `dict(vars(command.run))` 複製後再拆出；新增回歸測試並確認舊寫法會失敗。版控中既有的 `data/*/run_config.toml` 要等下次 publish 才會更新。
- **使用者追加**：`pipelines/eval.py` → `pipelines/exp.py`（與 `cli/exp.py` 對應、避免與 `retrieval/evaluation.py` 混淆）；`test_cli.py` 兩處 patch 字串漏改，2 個測試失敗，已修正。
- 驗證：278 passed／1 failed；所有子命令 `--help` 正常；`uv run website-copilot serve` 端到端與 `run rag-build` 皆正常。完整 `prepare` **未執行**（固定 publish 並覆寫版控中的 `data/`），改以 `run rag-build` 與 `run_prepare` 單元測試驗證。

### Phase E

- E1：兩份 widget 差異只有 typing indicator、toggle 按鈕與註解空白，無 extension 專屬設定，因此以 extension 版覆蓋 `server/static/widget.js`。
- E2：`git rm` 8 個版控腳本；被 gitignore 的 `dev/crawl4ai/tmp/`（約 34M）刪除後無法復原，保留給使用者處理。marp 原依 plan 移到 `docs/progress_report/drafts/`，使用者 amend 時改為只保留 `2026_0518_marp_v3.md` 並改名，其餘 3 份刪除。
- E3：`.env.example` 只列程式實際讀取的 4 個金鑰。
- E4：順帶修正重構前就已過時的內容（README 環境變數表列了程式未使用的名稱；`docs/code` 的 RAG API 仍描述 `build_reusable`、`build_to_*`）。`phase2_3_mvp.md` 的啟動方式演變刻意保留為歷程。
- 驗證：pyright 4 errors（= 基線）；278 passed／1 failed；`/static/widget.js` 與 `extension/widget.js` 逐位元相同。

---

## 2. serve 生命週期收斂與開發工具整理（plan 2）

- **起點補齊**：`test_run_agent.py` 約 60 個 `@patch` 仍指向 `pipelines.agent.*`／`server.bootstrap.*`，依函式所在位置拆分改 patch `pipelines.serve`／`pipelines.exp`；`pipelines/serve.py` 的模組說明是從舊 agent 模組複製過來的，重寫。
- **第 1 點**：`run_agent_build` 以 `nullcontext()` 沿用呼叫端 context，型別標註 `AbstractContextManager[object]` 讓兩種 context 共用一個變數；agent 建立後落盤失敗時先 `close()` 再 re-raise（plan 外補上，避免 RAG 資源外洩）。server 的 3 個測試原本未 patch `save_module_config_as_toml`，改動後會真的寫出 `fake_module_config.toml`，補 patch。
- **第 2 點**：實作前確認 uvicorn 0.52.1 的 `run()` 即 `asyncio.run(self.serve())`，兩種啟動方式都涵蓋。`serve()` 移除 `finally: chat_app.close()` 但**保留 `except KeyboardInterrupt`**：uvicorn 的 `capture_signals` 在 serve 結束後會重新發出 SIGINT，不接住終端機會印 traceback（以假 `ChatApp` 加真實 `ChatServer` 送 SIGINT 冒煙驗證）。新增參數化測試（正常結束／`KeyboardInterrupt`／`RuntimeError`）。
- **第 3 點**：腳本皆 `set -euo pipefail` 並先切到專案根目錄，可從任意目錄執行。`clean-runs.sh` 刪除前列出清單與大小並確認，環境變數 `RUNS_DIR` 可指定其他目錄；注意 agent 的 `results_<thread_id>.json` 會跨 run 累積歷史，清理後舊 thread 歷史一併移除（已寫入 README）。真實 `runs/` 只跑 `--dry-run`（79 個、61M）。
- **第 4 點**：本機 `.env` 含金鑰，未讀取也未修改，由使用者自行改名；GitHub secret 本來就叫 `GEMINI_API_KEY`。
- **第 5 點**：以 AST 掃描 import 對照 `uv tree`，所有宣告的套件都有用到。沒有直接 import 的幾個：`flagembedding`（`BGEM3SparseEmbeddingFunction` 執行時 import，沒裝就 `sys.exit(1)`）、`playwright`（CI 直接執行 `playwright install`）、`milvus-lite`（`==3.2.0` 刻意固定）、`mdformat-gfm`（由 `mdformat` 載入）、`llama-index`（meta 套件）、`httpx`（FastAPI `TestClient`）。未處理（使用者未選）：`langchain-core`、`pydantic`、`llama-index-core` 等只靠傳遞依賴安裝；部分版本下限與 lock 差距大；`description` 仍為範本文字。
  - ruff `exclude = [".venv"]` 會**取代**內建預設排除清單（`.git`、`build`、`dist` 等），改 `extend-exclude`。試跑 `--select E,F,W,I,UP,B` 得 95 個問題，使用者決定規則組維持預設。
  - prek 的 ruff 原為 `ruff-pre-commit` `rev = "v0.15.0"`（獨立環境），`uv run ruff` 為 0.15.12，版本漂移，改 local hook。CI 原本只跑 `ruff check .` 與 `pyright .`，未檢查格式。
- 測試數 277 → 282；`.env` 未改名時 gemini 模型讀不到金鑰（目前預設設定使用 gpt，不受影響）。

---

## 3. agent build 與 server build 分離（plan 3）

- **Part A**：驗證時實際執行 `serve --run.config-name test --run.port 8011`，`agent_build/` 與 `server/` 兩個 build 恰好落在同一秒，所以共用同一時間戳目錄；跨秒時會分成兩個目錄（plan 已接受）。
- **Part B**：B1 結果 `check.sh` 自 plan 1 以來首次 exit 0（pyright 0 errors、284 passed）。B3 `run_agent_query()` 的 run context 建立也放在 `try` 內，建立失敗時 agent 同樣會被關閉；內層 `except` 只記錄並 re-raise。測試起初以 `hasattr(exp, "save_module_config_as_toml")` 斷言，但 `run_rag_query` 仍使用該函式，改為 patch 後 `assert_not_called()`。
- 驗證：`check.sh` exit 0，285 passed；實際執行 `run agent` 產生 `agent_build/`（含 `module_config.toml`）與 `agent/`（對話結果與 `run_config.toml`，無 `module_config.toml`）。

---

## 4. 刪除多餘檔案與更名（plan 4）

- `KEEP_TITLE_CONTENT_THRESHOLD` 一度刪除，之後由使用者復原保留。`mock_save_logging` 改名 `_mock_save_logging`（17 處；`@patch` 仍需擋住寫檔，參數無法移除）。`.vscode/settings.json` 為未追蹤檔，順手修正開頭多餘的 `s` 與 `pytestArgs`。
- `rm -rf __pycache__ chats .claude runs/20260928_135728` 被 auto mode 以「無法復原的本機刪除」擋下，改由使用者手動執行。
- 更名：使用者先改類別，其餘用 `git mv`（設定檔與 `configs/` 資料夾）加 `sed` 統一替換；`ruff format` 重新換行；最後以 `git grep` 確認除 `docs/work`、`docs/progress_report`、`docs/survey`、`data/` 外無舊名。
- **行為變更**：runs 模組資料夾改為 `runs/<ts>/image_summarizer/`，`load_latest_results` 預設值跟著改，舊名存下的 run 不再被自動找到（當時 `runs/` 中無圖片摘要結果）；實驗名稱改為 `image_summarizer_model`／`image_summarizer_prompt`。
- 驗證：`check.sh` exit 0，285 passed（6 deselected）。

---

## 5. 測試新專案結構

- integration 測試：`test_agent_build` 為新增（`run_agent_build` 後 `close()`，只建 LLM client）；`test_serve` 不直接呼叫 `serve()`（`server.run()` 會阻塞）；不花錢的測試可單獨執行 `pytest tests/integration -m "not cost"`（`test_agent_build`、`test_serve`，需 `.env` 的 API key）。
- CI：除規劃中的 `ci-test.yml`，`ci.yml` 也有相同舊路徑，兩者都改為整個 `tests/integration`。
- 分檔時額外抽出 `agent_stubs.py`（規劃外，避免 serve 與 exp 兩檔各複製替身）；`setup_method`／`tempfile.mkdtemp()` 改 pytest `tmp_path`（原暫存目錄從未清除）；移除過時內容（`TestRAGRetrieverSmoke` 來源腳本已不存在、`TestLoadRag` 由 `test_serve_rag_loading.py` 涵蓋、測試已不使用的 `chats/`）。
- 精簡後保留 87 個函式（S、A 級）：向量庫原子替換、serve 讀取向量庫、`_should_rebuild`、registry 快取與 LRU、對話紀錄存檔 fallback、exclude_words 失敗處理與投票、URL 去重鍵、SSE 串流與 error 事件、agent／server 失敗時的資源關閉；刪除 `test_cli.py`、`test_create_tool.py`、`test_data_manager.py`、`test_html_date_extraction.py`、`test_image_failure_summary.py`、`test_log_helper.py`，以及其餘檔案中的 B、C 級測試。
- **實作中的問題**：以 AST 依保留清單刪除時，`test_rag_tools.py` 的 `TestListSites`、`TestGetCacheMiss` 等類別名稱沒列入清單，整個類別被刪掉，A 級的 7 個 registry 測試跟著消失，發現後從 HEAD 還原並補上類別名稱重做。

### `test_prepare` 不再覆寫 `data/`

使用者執行 `pytest tests/integration/test_pipeline.py` 後發現結果被 publish：`run_prepare()` 把三階段寫死為 `save=False, publish=True`，`test_prepare` 以 test config（40 頁）的結果覆寫了 `data/webpages/nculab/` 與 `data/rag/nculab/module_config.toml`（17 個被追蹤檔案）；該次在 rag build publish 前中斷，`milvus.db` 未被替換，但留下 `.staging-5ktj1ra4/`（`finally` 未執行到）。

考慮過的做法：(1) `test_prepare` 以 fixture 切換到 `tmp_path` 工作目錄執行（`configs/` 用 symlink）——不改正式程式且會端到端測到 publish，未採用；(2) 另寫 `run_prepare_test()`——會複製串接邏輯且測試用函式放進正式 `pipelines/`，不採；(3) `run_prepare(config_name, publish=True)`——採用。

**發現的回歸錯誤**：`webpages_data_use_latest_results` 在 `0303b47` 加入時讀 `runs/` 最新的 image summarizer 結果，拆出 DataManager 時（約 `8e5e6e8`）改成 `data_manager.get_webpages_path(site_id)`，與預設的 `data/webpages/<site>` 相同，參數實際沒有作用（CLI 的 `run rag-build --run.webpages-data-use-latest-results` 也受影響）。不修正的話，不 publish 時 rag build 會用 `data/webpages/` 的舊資料建庫，測試照樣通過但沒有測到本次產出。

資料還原：`git restore data/` 還原 17 個被覆寫的檔案並刪除 `.staging-5ktj1ra4/`；`data/raw_webpages/` 未被追蹤，無法判斷是否為該次產生，保留不動。

### 驗證

| 階段 | unit 測試數 |
|---|---|
| 開始前 | 285 |
| 分檔（合併 serve 重複測試） | 284 |
| 刪除過時與精簡 | 273 |
| 只保留核心 | 143（87 個函式，參數化展開後） |
| `test_prepare` 修正 | 145 |

每步執行 `./scripts/test.sh`，最後 `./scripts/check.sh` exit 0。integration：第 1–4 節只以 `--collect-only` 確認收集 7 個測試、`-m "not cost"` 為 2 個；第 5 節後實際執行 `test_pipeline.py`：**2 passed**（3 分 15 秒，API 花費 $0.073），rag build 讀取本次圖片摘要結果（34 頁），執行前後 `git status --short data` 相同。`test_module.py` 未實際執行。

---

## 遺留事項

- **對話歷史跨 run 查找範圍改變**（plan 3 行為變更第 3 點）：server 不再讀到舊 `runs/*/agent/` 的歷史，查找邏輯未調整。
- **`pipelines/exp.py` import `pipelines/serve.py`**：執行 `run agent`／`run rag-query` 時會一併載入 uvicorn 與 FastAPI。exp 為實驗／除錯用途，影響可接受；若在意可把 `run_agent_build` 移到不依賴 server 的模組。
- **prepare 重新 publish 後，已在執行的 server 仍使用舊向量庫**（Linux 上已開啟的檔案不受 rename 影響），需重啟；可考慮以 manifest mtime 讓 registry 自動 evict。
- **`run_rag_query --run.force-rebuild`** 仍於 `data/rag/` 原地重建（評估工具，未改）。
- **pyright 的 `exclude`** 未比照 ruff 擴充（`runs`、`data` 等），需要時再對齊。
- **本機 `.env`**：三個舊 Gemini 變數需改為 `GEMINI_API_KEY`。
- **未執行**：完整 `website-copilot prepare`（會覆寫版控中的 `data/`）、`pytest tests/integration` 的 `cost` 測試（真實爬蟲與付費 API），皆需使用者同意。
- **`dev/crawl4ai/tmp/`**：gitignore 的本機輸出仍在，是否刪除由使用者決定。
- **force push**：plan 2 amend 後的 `590c94e` 若分支已 push，需 `git push --force-with-lease`。
