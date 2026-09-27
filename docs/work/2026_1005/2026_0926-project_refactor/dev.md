# Development Log

> 對應規劃文件：[plan.md](./plan.md)；後續調整（plan 2）見 [2026_0927-project_refactor_plan2/](../2026_0927-project_refactor_plan2/plan.md)

分支 `dev-tech-debt-refactor`（= `dev-tech-debt` + plan commit `6120df2`），每個 phase 一個 commit：

| Phase | Commit | 內容 |
|---|---|---|
| A | `fd12aeb` | 安全網：基線、import 冒煙測試、serve 載入特性測試 |
| B | `e84f6dd` | 純搬移到 `src/website_copilot/`（無邏輯變更） |
| C | `a8db3fd` | RAG 拆成 indexing / retrieval，回傳式建構，serve 不需 `data/webpages/` |
| D | `2173629` | `website-copilot` CLI、入口邏輯下移 |
| E | `b3805d8` | widget 同步、清理 `dev/`、Makefile、`.env.example`、文件更新 |

plan 原寫在 `dev-tech-debt` 上另開 `refactor/project-layout`；因 `dev-tech-debt-refactor` 已是 `dev-tech-debt` 加上 plan commit，直接在此分支實作。C、D、E 的 commit 各自 amend 過使用者追加的變更（見各 phase 的「使用者追加變更」與 E2）。

---

## 基線（Phase A 開始前）

- `pytest -m "not slow"`：**203 passed / 1 failed**。失敗的是 `test_webpage_markdown_cleaner.py::test_save_generated_exclude_words`（`run_persistence.save_generated_exclude_words` 讀 `result.hits[w]`，但測試建立的 `GenerationResult` 未帶 `hits` → `KeyError`），重構前即存在，不在本次範圍內，全程保留作為比對基準。
- `pyright`：**4 errors**，皆在同一個測試檔（`reportOptionalMemberAccess`）。
- `ruff check` / `ruff format --check`：通過。

---

## Phase A：安全網

- **`test_imports.py`**：逐一 import `app/`、`utils/` 下所有模組與 `cli`、`prepare`、`serve`。
  - **偏離 plan**：不用 `pkgutil.walk_packages`，改以檔案系統掃描列出模組。`configs/`、`engines/`、`utils/` 沒有 `__init__.py`（namespace package），`walk_packages` 會整個略過。
- **`test_serve_rag_loading.py`**（特性測試）：tmp 目錄 + 真實 `RAGConfig` / `RAGRegistry`，只 patch Milvus、embedding、index、retriever 等外部資源。鎖定：
  - `RAGRegistry.get()` 走「載入既有向量庫」路徑：不 clean、不建 nodes / index，重新 `load_collection`，只建到 retriever、不建 query engine。
  - 向量庫不存在時，`FileNotFoundError` 訊息與原本逐字相同。
  - **偏離 plan**：plan 寫「patch `RAGBuilder` 為 fake」，實作改為只 patch 外部資源，讓真實建構流程被測到；C2 因此只需改 patch 路徑、斷言不變。

**驗證**：新增 42 個測試通過；245 passed / 1 failed（基線那個）。

---

## Phase B：純搬移

每一步的 `sed` 指令完整記錄在 `e84f6dd` 的 commit message，可重做。

- **B1 測試搬家**：`src/test/dev/*` → `tests/unit/`，`test_module.py`、`test_main.py` → `tests/integration/`；`testpaths = ["tests"]`；CI 路徑改為 `tests/integration/test_module.py`。兩個新測試的 `parents[...]` 路徑同步修正。
- **B2 改名**：`git mv src/app src/website_copilot`、`git mv src/utils src/website_copilot/utils`；以 sed 改寫 `from/import app.`、`"app.`（patch 字串）、`from utils.` 等；`packages = ["src/website_copilot"]`。import 路徑變長造成 12 個檔案需 `ruff format`（機械變更，一併記入 commit）。
- **B3**：`GenerationResult` 移到 `website_copilot/schemas.py`；cleaner、crawler、`data_manager`、`run_persistence` 改 import。
- **B4**：`workflow/` 拆成 `storage/{data_manager,run_manager,run_persistence,run_context}` + `pipelines/{prepare,eval}` + `server/bootstrap.py`；`configs/` → `config/`，`workflow_config.py` → `pipeline_config.py`。原 `workflow/__init__.py` 的重新匯出全是 storage 模組，直接移為 `storage/__init__.py`。
- **B5**：`engines/` 拆成 `ingestion/crawling/{website_crawler,markdown_cleaner,html_date_extractor}` 與 `ingestion/augmentation/image_summarizer`。
- **B6**：`rag_factory` → `ingestion/indexing/index.py`；`rag`、`rag_eval_prompts`（→ `evaluation`）、`utils/rag_helper`（→ `helpers`）、`tools/rag_registry`（→ `registry`）→ `retrieval/`；其他 tools → `agent/tools/`；`utils/langchain_helper` → `agent/`。

### 非純搬移、需留意的三處

1. **logger 名稱**：`setup_logging` 以字串 `"website_copilot.engines.rag"` 設定 log 等級，涵蓋 rag / rag_factory / prompts 三個模組。搬移後此名稱不對應任何模組，RAG 的 debug log 會悄悄失效，因此展開成三個模組的新名稱（C3 再改為套件層級，見下）。
2. **`engines/rag/__init__.py` 的重新匯出**改為直接 import 各模組；`retrieval/__init__.py` 刻意留空，因為 B6 時 indexing ↔ retrieval 仍互相依賴，放重新匯出會形成循環 import。
3. **測試副作用**：serve 載入 Milvus 會在 `data/rag/<site>/milvus.db/.../indexes/` 產生未追蹤的 index 快取，每次驗證後刪除（之後每個 phase 同樣處理）。

**驗證**：251 passed / 1 failed；43 個模組逐一在新 interpreter 單獨 import 成功（pytest 共用 process 可能掩蓋循環 import，故另外檢查）；設定檔、CI、scripts 無舊路徑。里程碑：`uv run python src/serve.py` → `/api/health` ok、`/api/chat` SSE 完整回答、`/static/demo.html` 200。rename 相似度多數 ≥ 90%，較低者為小檔或 patch 字串多的測試檔。

---

## Phase C：RAG 重構

### C1：抽出 helper 模組

- `indexing/vector_store.py`：`VectorStoreBuilder`（不含 `clean_milvus`，其邏輯併入 builder 的 clean）、`EMBEDDING_DIM_MAP`。
- `indexing/node_pipeline.py`：`NodePipelineBuilder`。
- `indexing/transforms.py`：3 個 Markdown transformation（自 `retrieval/helpers.py`）。
- `indexing/source.py`：來源載入（results.json + md 目錄），由 `RAG` 建構子呼叫。
- `retrieval/evaluation.py`：補入 `response_to_dict`、`evaluation_result_to_dict`、`extract_sources_list`。

### C2：拆分 `RAGBuilder`（mutate 模式，中間狀態）

- `indexing/index.py` 的 `IndexBuilder`：clean / nodes / vector store / index / load / `build_or_load` / `_should_rebuild` / Build Stats 表。
- retrieval 端的 `RAGBuilder`（retriever、query engine）與 `create_rag`；serve 載入函式 `load_to_retriever(config, rag)`；`build_evaluators(config, rag)`。
- 特性測試只改 patch 路徑，斷言不變。

### C3：回傳式建構、移除 webpages 依賴（本次唯一刻意的行為變更）

- **`IndexHandle(vector_store, index, milvus_uri, close())`**；`IndexBuilder.build(source)` / `load()` / `build_or_load(force_rebuild)` 回傳它。只有重建時才讀取 webpages 來源，且在清除舊向量庫**之前**讀取（results.json 不存在就直接失敗，舊庫不受影響，順序與舊版相同）。
- **`RAG(index_handle, retriever=None, query_engine=None)`**：移除 webpages / nodes / evaluators 欄位，`milvus_uri` 改為 handle 的 property。
- **`RAGBuilder.build_retriever(index)` / `build_query_engine(retriever)` / `build(handle)`** 皆回傳值。
- **`load_to_retriever(config, rag)` → `load_rag(config) -> RAG`**：serve 只走 `IndexBuilder.load()`，完全不讀 webpages。
- **`build_evaluators(config)`** 回傳 tuple；因 `RAG` 不再持有 evaluators，`RAG.evaluate` 移到 `evaluation.evaluate_response(evaluators, query, response)`（plan 未寫，實作時補）。
- **資源釋放**（plan 未寫，實作時補）：舊版的 vector store 掛在 `rag` 上，建置中途失敗會隨 `rag.close()` 關閉；回傳式建構後改由 `IndexBuilder.build/load` 與 `RAGBuilder.build` 在失敗時主動關閉 Milvus client，避免連線外洩。
- `indexing` 不再 import `retrieval`，循環依賴解除；`retrieval/__init__.py` 說明同步更新。
- `setup_logging` 的 RAG logger 改為套件層級 `ingestion.indexing` 與 `retrieval`。多涵蓋到的模組（registry、helpers）沒有 debug log，實際輸出不變。
- **測試**：特性測試改用新 API，並新增「刪除 `data/webpages/` 後 `registry.get()` 仍成功」；registry 測試改 patch `load_rag`；新增 `load_rag`、handle 失敗關閉、重建前先讀來源等測試。`test_run_rag_build_publish.py` 僅 fake `create_rag`（簽名與回傳的 `milvus_uri` 不變），未改寫也通過（plan 原寫要改寫）。

### 使用者追加變更（amend 進 `a8db3fd`）

使用者自行調整命名與結構：`retrieval/builder.py` + `loader.py` 合併為 `retrieval/factory.py`（`RAGBuilder` + `build_rag`（原 `create_rag`）+ `load_rag`）；`retrieval/helpers.py` → `llama_index_helpers.py`，並把 `RAG._log_sources` 移為 `log_source_nodes`；`SourceDocs` / `load_source_docs` → `Source` / `load_source`；embedding 模型改由 `IndexBuilder._create_embed_model` 建立；`log_prepare_workflow_run_summary` → `log_run_summary`。

驗證時發現並修正：

- **循環 import**：`llama_index_helpers.py` 寫了 `from website_copilot.retrieval.rag import logger`（疑為搬移 `_log_sources` 時編輯器自動補的 import），而 `rag.py` 又 import `llama_index_helpers`，導致 8 個測試檔收集失敗。改為 helpers 自建 `logger = logging.getLogger(__name__)`。
- **跟著改名的地方**：`test_log_helper.py`、`test_run_rag_build_publish.py`（patch `build_rag`）、`test_rag_tools.py` / `test_serve_rag_loading.py`（patch 路徑改 `factory`、`IndexBuilder._create_embed_model`），以及 `pipelines/prepare.py`、`data_manager.py`、`langchain_helper.py`、`log_helper.py` 的註解與 docstring。
- plan.md 的決策、目標結構、C1–C3 描述同步改為最終名稱。

**驗證**：259 passed / 1 failed（`loader.py` 刪除後冒煙測試少一個模組）；48 個模組單獨 import 成功；`import website_copilot.retrieval.registry` 不載入 crawl4ai / `ingestion.crawling`。里程碑：

- 將 `data/webpages/` 改名後啟動 serve，`/api/chat` SSE 正常、`demo.html` 200（serve 確實不再需要 webpages）。
- `rag-build`（test config）：47 份文件 → 274 nodes，`milvus.db` 與 `module_config.toml` 寫在 `runs/`，與重構前一致。
- `rag-query`（test config）含評估：Faithfulness / Relevancy 皆 1/1，`log_source_nodes` 正常輸出 10 個來源。

---

## Phase D：入口

### D1：邏輯下移

- `pipelines/prepare.py::run_prepare()`：三階段串接（原 `src/prepare.py` 的 `main`）。
- `server/bootstrap.py::serve_forever(run_config)`：`run_app` → `server.run()` → `finally chat_app.close()`。bootstrap 此後只保留 server 相關程式。
- `pipelines/agent.py`：`run_agent_build` / `run_agent_query`（自 bootstrap 移出）；`test_run_agent.py` 中 agent 流程的測試改 patch `pipelines.agent`，`run_app` 測試維持 `server.bootstrap`。
- `exp.py` 的實驗函式移入 pipelines，加上 `EXPERIMENTS` 名稱表與 `run_experiment(name)`；圖片摘要實驗改在函式內延遲 import `pipelines.prepare`，避免 rag-query 路徑載入爬蟲依賴。
- `setup_logging` 留在入口層呼叫（原本 `exp.py` 在 import 時就呼叫）。
- 舊入口暫時保留為薄包裝，用來驗證：三個舊入口的 `--help`、`src/serve.py` 端到端都正常。

### D2：`cli/` 與 console script

- `website-copilot prepare | serve | run <website-crawler | image-summarizer | rag-build | rag-query | agent> | exp [name]`。
  - 以 `tyro.conf.subcommand` 明確命名子命令，`run` 底下的第二層 union 用 `tyro.conf.arg(name="")` 讓參數維持 `--run.*` / `--module.*`（不會變成 `--command.run.*`），再搭配 `OmitSubcommandPrefixes`。實作前先以小腳本確認 tyro 1.0.13 的巢狀子命令行為。
  - `exp` 的名稱為 `Literal` 位置參數，在 CLI 端列出而不 import pipelines（避免解析參數時載入 RAG 依賴），由測試比對它與 `EXPERIMENTS` 一致。
- 各子命令模組頂層只 import 參數 dataclass，執行邏輯在 `main()` 內延遲 import；有測試保證 CLI 與 serve 路徑不載入爬蟲。
- `[project.scripts] website-copilot = "website_copilot.cli:main"`；`cli/__main__.py` 加上 `if __name__ == "__main__"`，讓 `python -m website_copilot.cli` 可用，import 時也不會觸發執行（冒煙測試因此抓到一次失敗）。
- 刪除 `src/{cli,prepare,serve,exp}.py` 與 pytest 的 `pythonpath = ["src"]`，改靠 editable install（確認 `.venv` 內為 `_editable_impl_website_copilot.pth`）；`test_imports.py` 移除入口模組清單。
- `scripts/multi_site.py` 只 import `pipelines.prepare`，不需修改（已確認可 import）。
- `config/pipeline_config.py` 中提及 `prepare.py` / `serve.py` 的 docstring 改為新指令。
- 新增 `tests/unit/test_cli.py`：各子命令分派、module override 轉換（`weights` → `hybrid_ranker_params`）、`save` / `publish` 拆出、exp 名稱一致、`serve_forever` 中斷時關閉、`run_prepare` 串接與提前結束、serve 路徑不載入爬蟲。

### 修正：`run_config.toml` 未記錄 `save` / `publish`（使用者決定修正，amend 進 D）

舊 `src/cli.py` 以 `run_kwargs = vars(cli_arg.run)` 後直接 `pop("save")` / `pop("publish")`，等於刪除 run config **物件本身**的屬性：

- `run_config.toml` 從未記錄這兩個欄位。
- 之後讀取 `run_config.publish` 會落回 dataclass 的類別預設值 `False`，即使命令列傳了 `--run.publish`。

D2 起初為維持「行為不變」保留此寫法並回報；使用者決定修正，改為 `dict(vars(command.run))` 複製後再拆出。新增回歸測試 `test_run_config_keeps_save_and_publish`，並確認舊寫法會讓它失敗（`assert False is True`）。實跑 `rag-build` 後，`run_config.toml` 含 `publish = false`、`save = true`。之後 publish 到 `data/` 的 `run_config.toml` 也會帶上這兩個欄位；版控中既有的 `data/*/run_config.toml` 要等下次 publish 才會更新。

### 使用者追加變更：`pipelines/eval.py` → `pipelines/exp.py`（amend 進 D）

改名理由：與 `cli/exp.py` 對應，並避免與 `retrieval/evaluation.py` 混淆。驗證時發現 `test_cli.py` 兩處 patch 字串仍為 `pipelines.eval.*`（2 個測試失敗），一併修正；另更新 `cli/exp.py` 註解與 `storage/run_context.py` 的說明（順便補上漏列的 `pipelines.agent`，並移除過時的「`*_workflow` 模組」字樣）。plan.md 的 B4、D1、D2 與目標結構同步註明此改名。

**驗證**：278 passed / 1 failed；55 個模組在 `src/` 以外的目錄單獨 import 成功（確認拿掉 `pythonpath` 後仍可 import）；所有子命令 `--help` 正常，參數名稱與舊版一致。里程碑：`uv run website-copilot serve` 端到端（health、`/api/chat` SSE、demo.html、關閉時印出 Server Stopped）；`website-copilot run rag-build --run.config-name test` 產出與先前一致；改名後以 `run rag-query` 實跑 `pipelines.exp.run_rag_query`，評估 1/1。

完整的 `website-copilot prepare` **未執行**：它固定 publish 並覆寫版控中的 `data/`，且會重新爬取網站。prepare 路徑改以 `run rag-build` 與 `run_prepare` 的單元測試（mock 各階段）驗證。

---

## Phase E：雜項

- **E1 widget**：兩份的差異只有 typing indicator、toggle 按鈕（💬 → 🤖）與註解空白，沒有 extension 專屬設定，因此以 extension 版覆蓋 `server/static/widget.js`，此後 static 為唯一來源。新增 `make sync-widget` / `make check-widget`，並在 `ci.yml`、`ci-test.yml` 的 quality-check 加上 `cmp` 步驟。
- **E2 dev/**：`git rm` 刪除 legacy / crawl4ai / llama_index 的 8 個版控腳本；移除 ruff 與 pyright 的 `dev/**` 排除規則（確認剩下的目錄沒有 `.py`，pyright 錯誤數不變）。
  - 被 gitignore 的 `dev/crawl4ai/tmp/`（約 34M 本機輸出）不在版控內，刪除後無法復原，因此保留由使用者處理。
  - marp：原先依 plan 移到 `docs/progress_report/drafts/`；使用者 amend 時改為只保留 `2026_0518_marp_v3.md`，並改名為 `docs/progress_report/2026_0518/2026_0518_marp.md`，其餘 3 份刪除，不建立 `drafts/`。README 檔案結構樹、plan.md（決策與 E2）與 Phase E 的 commit message 隨後同步改為此結果，並 amend 進 Phase E。
- **E3**：
  - `.env.example` 只列程式實際讀取的 4 個金鑰：`OPENAI_API_KEY`、`GEMINI_RAG_QUERY_ENGINE_API_KEY`、`GEMINI_RAG_EVALUATOR_API_KEY`、`GEMINI_WEBPAGE_IMAGE_SUMMARIZER_VLM_API_KEY`（與 `.env` 的 key 一致；確認未被 `.gitignore` 的 `.env` 規則擋掉）。
  - Makefile：`help`（預設目標）/ `install` / `check`（lint + typecheck + test + check-widget）/ `lint` / `format` / `typecheck` / `test` / `sync-widget` / `check-widget` / `serve`。
- **E4 文件**：
  - README：檔案結構樹、安裝（`uv sync` + `.env.example`）、環境變數表、所有指令、測試、`run_config.toml` 說明、開發（Makefile、widget 同步規則）。
  - `docs/code/runs/cli.md` 依新 CLI 整份改寫；其餘 `docs/code/**` 先以對照表機械替換路徑，再逐一處理需要上下文的行。`serve_workflow` 的對照只適用於 `run_app`，提到 `run_agent_*` 的地方另外改指 `pipelines/agent.py`。
  - 順帶修正重構前就已過時的內容：README 環境變數表原列 `OPENAI_RAG_EMBEDDING_API_KEY` 等程式未使用的名稱；`docs/code` 的 RAG API 仍描述 `build_reusable`、`build_to_*`，改為 `IndexBuilder` / `RAGBuilder` / `build_rag` / `load_rag`。
  - `docs/code/phase2_3_mvp/phase2_3_mvp.md` 的啟動方式演變（`server-cli` → `src/serve.py` → `website-copilot serve`）刻意保留為歷程；`docs/work/` 下的工作紀錄不改。

**驗證**：ruff / format 通過；pyright 4 errors（= 基線）；278 passed / 1 failed；plan「完成後」的收尾 grep 無殘留。serve 端到端：送出的 `/static/widget.js` 含 typing indicator 且與 `extension/widget.js` 逐位元相同，`/api/chat` SSE 與 demo.html 正常。

---

## 最終狀態摘要

- **指令取用**：`uv sync` 以 editable 模式安裝，產生 `.venv/bin/website-copilot`；以 `uv run website-copilot <子命令>` 執行（或 `python -m website_copilot.cli`）。舊的 `python src/*.py` 入口與 `pythonpath = ["src"]` 皆已移除。clone 後須先 `uv sync`，測試與 `scripts/multi_site.py` 才能 import `website_copilot`。
- **依賴方向**：`indexing` 不 import `retrieval`；`storage` 不 import `ingestion`；serve 路徑（`cli.serve`、`server.bootstrap`、`retrieval.registry`）不載入 crawl4ai / `ingestion.crawling`，皆有測試或檢查保證。
- **測試數**：203 → 278 passed（新增冒煙、特性、RAG 回傳式建構、CLI 測試），基線失敗的 1 個與 pyright 4 errors 維持不變。

## 遺留事項

- **`make check` 目前不會通過**：卡在基線的 pyright 4 errors 與 1 個失敗測試（皆在 `test_webpage_markdown_cleaner.py`，看起來是測試未跟上 `GenerationResult.hits`）。修正前，plan 所述「以 `git bisect run make check` 定位」無法直接使用。
- **未執行**：完整 `website-copilot prepare`（會覆寫版控中的 `data/`）與 `pytest -m slow tests/integration`（真實爬蟲與付費 API），皆需使用者同意。
- **`dev/crawl4ai/tmp/`**：gitignore 的本機輸出仍在，是否刪除由使用者決定。

## 過程中的操作失誤

- 兩次以 `pkill -f "...serve.py"` 關閉 server 時，比對字串同時出現在該次 shell 指令本身，連同 shell 一起被終止，後續指令沒有執行。其中一次發生在把 `data/webpages` 改名以驗證 C3 之後，「改回原名」那一步因此未執行；隨即發現並還原，版控中的 `data/` 無變動。之後改為記錄 PID，以 `kill -INT $PID` 關閉。
