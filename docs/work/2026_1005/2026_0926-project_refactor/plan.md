# 專案結構重構計畫：改為標準 src layout 並依管線階段分模組

## Context

目前 `src/` 下有兩個頂層套件 `app`、`utils`，入口檔（`cli.py`、`prepare.py`、`serve.py`、`exp.py`）散落在 `src/` 根目錄，測試放在 `src/test/`，而且要靠 pytest 的 `pythonpath = ["src"]` 才能 import。模組依「技術角色」命名（`engines/`、`tools/`、`workflow/`），造成幾個問題：
- `rag_factory.py` 同時負責建庫與 serve 載入。
- RAG 反向依賴 `workflow/` 的 `DataManager` / `RunManager`。
- `storage` 類模組依賴 cleaner 的型別。
- 兩份 `widget.js` 已經分岔。

目標是改成常見的 `src/website_copilot/` 單一套件，依管線階段分模組，依賴方向單一，並提供單一 CLI。**除一項刻意的變更外，執行行為不變**（config 路徑、`data/`、`runs/` 位置不動）。那項刻意變更是：serve 不再需要 `data/webpages/`。

已確認的決策：
- 套件改名為 `src/website_copilot/`，這一輪完成全部模組重組。
- `ingestion/` 下分 `crawling/`、`augmentation/`、`indexing/`。凡是建置或載入 index 的程式碼都放在 `indexing/`，`retrieval/` 分成 `builder.py`（組裝查詢物件）與 `loader.py`（serve 載入）。
- RAG 容器改為回傳式建構：builder 回傳物件，不再從外部寫入欄位。
- `workflow/` 改名為 `pipelines/`，檔名去掉後綴；server 啟動移到 `server/`。
- `DataManager`、`RunManager`、run context 移到 `storage/`；跨層共用型別放在 `schemas.py`。
- 單一 CLI 指令 `website-copilot`（`cli/` 子套件、tyro 子命令），`scripts/` 只放一次性腳本。
- `data/` 維持在版控，不變動。
- `widget.js` 以 `server/static/` 為來源，兩份都進版控，用 `make sync-widget` 同步，並由 CI 比對。
- 刪除 `dev/legacy`、`dev/crawl4ai`、`dev/llama_index`；`dev/marp` 移到 `docs/progress_report/drafts/`。
- 測試分為 `tests/unit`、`tests/integration`。新增 `.env.example` 與 `Makefile`。

在 `dev-tech-debt` 上開新分支 `refactor/project-layout`，每個 phase 一個 commit，詳見「執行步驟」。**每個 phase 的 commit 完成並通過檢查後都先暫停，回報結果（diff 摘要、測試數字、里程碑檢查輸出），等使用者確認後才進行下一個 phase。**

## 目標結構

```text
src/website_copilot/
├── __init__.py
├── schemas.py                     # 跨層共用資料型別（GenerationResult ← webpage_markdown_cleaner）
├── cli/                           # `website-copilot <subcommand>`
│   ├── __init__.py  __main__.py   # main()：tyro 子命令分派
│   ├── prepare.py                 # ← src/prepare.py 的 PrepareCLI（只解析參數）
│   ├── serve.py                   # ← src/serve.py 的 ServeCLI
│   ├── run.py                     # ← src/cli.py（單模組執行：crawler / image summarizer / rag build / rag query / agent）
│   └── exp.py                     # ← src/exp.py（只留參數；邏輯移入 pipelines/eval.py）
├── config/                        # ← app/configs/*；workflow_config.py → pipeline_config.py
├── ingestion/
│   ├── crawling/                  # 網站爬蟲
│   │   ├── website_crawler.py         # ← app/engines/website_crawler.py
│   │   ├── markdown_cleaner.py        # ← app/engines/webpage_markdown_cleaner.py
│   │   └── html_date_extractor.py     # ← utils/html_date_extractor.py
│   ├── augmentation/              # 資料加強
│   │   └── image_summarizer.py        # ← app/engines/webpage_image_summarizer.py
│   └── indexing/                  # RAG 建置
│       ├── source.py             # ← 原 RAG 容器的 results.json / md 目錄載入
│       ├── transforms.py              # ← rag_helper: MarkdownHeadingMergeParser / ImageExtractor / DateExtractor
│       ├── node_pipeline.py           # ← rag_factory: NodePipelineBuilder
│       ├── vector_store.py            # ← VectorStoreBuilder、EMBEDDING_DIM_MAP、create_embed_model
│       └── index.py                   # ← IndexBuilder：clean / build / load，回傳 IndexHandle
├── retrieval/
│   ├── rag.py                     # ← app/engines/rag/rag.py（由建構子接收查詢物件）
│   ├── builder.py                 # ← build_retriever / build_query_engine + create_rag
│   ├── loader.py                  # ← load_rag：serve 載入入口（絕不建置）
│   ├── evaluation.py              # ← build_evaluators + eval prompts + response_to_dict 等
│   ├── registry.py                # ← app/tools/rag_registry.py
│   └── helpers.py                 # ← rag_helper: build_filters / create_llm / extract_sources_info
├── agent/
│   ├── agent.py                   # ← app/agent/agent.py
│   ├── langchain_helper.py        # ← utils/langchain_helper.py
│   └── tools/                     # ← app/tools/{tool,webpage_retriever,site_discovery}.py
├── storage/
│   ├── data_manager.py  run_manager.py  run_persistence.py   # ← app/workflow/*
│   └── run_context.py             # ← app/workflow/workflow_helper.py
├── server/                        # ← app/server/*（含 static/）
│   └── bootstrap.py               # ← serve_workflow.run_app + src/serve.py 的生命週期（run → close）
├── pipelines/                     # 離線批次流程
│   ├── prepare.py                 # ← prepare_workflow.py + src/prepare.py 的三階段串接（run_prepare）
│   ├── agent.py                   # ← serve_workflow 中的 run_agent_build 等單模組流程
│   └── eval.py                    # ← eval_workflow.py + src/exp.py 的實驗邏輯
└── utils/                         # ← utils/{log_helper,config_helper}.py
tests/
├── unit/                          # ← src/test/dev/*（含 _helpers.py）
└── integration/                   # ← src/test/test_module.py、test_main.py（slow marker）
```

**依賴方向**（箭頭表示「可 import」）：
`cli` → `pipelines` / `server` → `agent` → `retrieval` → `indexing` → `augmentation` → `crawling` → `storage` → `config` / `utils` / `schemas`
- 所有層都可以依賴 `schemas`、`config`、`utils`。
- `storage` 不依賴任何 `ingestion` 模組，因為它需要的 `GenerationResult` 放在 `schemas`。
- `indexing` 不 import `retrieval`（回傳式建構，不需要知道 `RAG`），因此不會有循環 import。
- `server/bootstrap.py` 使用 `storage.run_context`，不依賴 `pipelines`。
- `__init__.py` 只做輕量的重新匯出，不在套件層級 import 重型依賴，避免 serve 間接載入 crawl4ai 或 playwright。


## 執行步驟

原則：
- 每個 phase 一個 commit；phase 內的每一步完成後仍先跑「每步檢查」（見驗證一節），全部通過後才在 phase 結束時 commit。
- **搬移與邏輯變更絕不放在同一個 commit**：Phase B 只做搬移，其 commit 應在 `git show -M --stat` 中顯示高相似度的 rename，審閱時只需檢查 import 行；邏輯變更集中在 Phase C、D。
- 大量 import 替換以腳本（`sed` 或 `ruff`）完成，並把各步驟的指令依序寫進該 phase 的 commit message，方便重做。
- 出問題時，對單一 phase `git revert`，或用 `git bisect run make check` 定位到 phase，再依 commit message 的步驟紀錄縮小範圍。

### Phase A：安全網
**A1. 建立基線與 import 冒煙測試**
- 記錄目前 `pytest -m "not slow"` 的通過數量，以及 `pyright` 的錯誤數，作為後續每一步的比對基準。
- 新增 `src/test/dev/test_imports.py`：以 `pkgutil.walk_packages` import `app`、`utils` 底下的所有模組，外加 `cli`、`prepare`、`serve`。之後每次搬移都更新它的 root，可立即發現壞掉的 import 與循環 import。
- 新增 serve 載入的特性測試（characterization test）：使用 tmp 資料夾，patch 掉 embedding，並 patch `RAGBuilder` 為 fake，驗證 `RAGRegistry.get(site_id)` 走 `load_to_retriever` 路徑、向量庫不存在時拋出原錯誤訊息。此測試在 C3 會依新 API 改寫，其餘步驟都不應變動它。
- 驗證：新測試通過。

### Phase B：純搬移（無邏輯變更）
**B1. 測試搬家**
- `src/test/dev/*` → `tests/unit/`，`test_module.py`、`test_main.py` → `tests/integration/`，刪除 `src/test/__init__.py`。
- `pyproject.toml` 的 `testpaths = ["tests"]`（`pythonpath = ["src"]` 暫時保留）；CI 路徑改為 `tests/integration/test_module.py`。
- 驗證：通過數量與基線相同。

**B2. 套件改名 `app` + `utils` → `website_copilot`**
- `git mv src/app src/website_copilot`，`git mv src/utils src/website_copilot/utils`。
- 腳本替換：`from app.` / `import app.` / `"app.`（patch 字串）→ `website_copilot.`，`from utils.` → `from website_copilot.utils.`，範圍包含 `src`、`tests`、`scripts`。
- `pyproject.toml` 的 `packages = ["src/website_copilot"]`。
- 驗證：每步檢查全部通過，並用舊入口執行 `uv run python src/serve.py --help`。

**B3. 抽出 `schemas.py`**
- 將 `GenerationResult` 從 cleaner 移到 `website_copilot/schemas.py`，並更新 cleaner、`data_manager`、`run_persistence` 的 import。
- 驗證：每步檢查。

**B4. `workflow/` 拆成 `storage/` + `pipelines/`，並將 `configs` 改名為 `config`**
- `data_manager`、`run_manager`、`run_persistence`、`workflow_helper`（改名為 `run_context`）移到 `storage/`。
- `prepare_workflow`、`eval_workflow` 移到 `pipelines/{prepare,eval}.py`；`serve_workflow.py` 整檔移到 `server/bootstrap.py`。
- `configs/` → `config/`，`workflow_config.py` → `pipeline_config.py`。
- 驗證：每步檢查，並確認 `storage` 沒有 import `ingestion`（grep）。

**B5. `engines/` 拆成 `ingestion/{crawling,augmentation}`**
- 將 `website_crawler`、`webpage_markdown_cleaner`（改名為 `markdown_cleaner`）、`utils/html_date_extractor` 移到 `crawling/`；`webpage_image_summarizer`（改名為 `image_summarizer`）移到 `augmentation/`。
- 驗證：每步檢查。

**B6. RAG 與 tools 搬移（整檔，不拆）**
- `engines/rag/rag_factory.py` → `ingestion/indexing/index.py`；`rag.py` → `retrieval/rag.py`；`rag_eval_prompts.py` → `retrieval/evaluation.py`；`utils/rag_helper.py` → `retrieval/helpers.py`。
- `tools/rag_registry.py` → `retrieval/registry.py`；其他 tools 移到 `agent/tools/`；`utils/langchain_helper.py` → `agent/`。
- 此時 `indexing` 仍會 import `retrieval`，屬於過渡狀態，會在 C3 消除。`__init__.py` 保持精簡以避免循環 import。
- 驗證：每步檢查，並執行 import 冒煙測試，確認沒有循環 import。
- **里程碑檢查**：`uv run python src/serve.py` 啟動並呼叫 `/api/chat`，確認端到端正常後再進入 Phase C。

### Phase C：RAG 重構（邏輯變更，逐步進行）
**C1. 抽出 helper 模組（函式搬家，簽名不變）**
- `indexing/vector_store.py`：`VectorStoreBuilder`（不含 `clean_milvus`）、`EMBEDDING_DIM_MAP`、`create_embed_model()`。
- `indexing/transforms.py`：3 個 Markdown transformation。
- `indexing/source.py`：`load_source_docs()`，暫時仍由 `RAG._load_results_json` 呼叫。
- `retrieval/evaluation.py`：補入 `response_to_dict`、`evaluation_result_to_dict`、`extract_sources_list`。
- 驗證：每步檢查。

**C2. 拆分 `RAGBuilder` 類別（仍採用 mutate 模式）**
- `indexing/index.py` 的 `IndexBuilder`：包含 clean、nodes、vector store、index、load、`build_or_load`、`_should_rebuild` 與 Build Stats 表。
- `retrieval/builder.py` 的 `RAGBuilder`：`build_retriever`、`build_query_engine`；`create_rag` 移到這裡。
- `retrieval/loader.py`：`load_to_retriever(config, rag)`。
- `retrieval/evaluation.py`：`build_evaluators(config, rag)`。
- 同步更新呼叫端與測試的 patch 目標。
- 驗證：每步檢查。A1 的 serve 特性測試只允許改 patch 路徑，斷言不變。

**C3. 回傳式建構與移除 `webpages` 依賴（本次唯一的行為變更）**
- 新增 `IndexHandle`；`IndexBuilder.build`、`load`、`build_or_load` 改為回傳值；`RAGBuilder` 的方法改為回傳值；新增 `RAG(index_handle, retriever, query_engine)`，並移除 webpages 相關欄位；`load_to_retriever` 改為 `load_rag(config) -> RAG`；`build_evaluators(config)` 改為回傳 tuple。
- `indexing` 不再 import `retrieval`。
- 改寫 A1 的特性測試與 `test_rag_tools.py`、`test_run_rag_build_publish.py`。新增測試：沒有 `data/webpages/` 時 `load_rag` 仍能成功。
- 驗證：每步檢查，並確認 serve 路徑不會載入爬蟲模組（驗證第 5 項）。
- **里程碑檢查**：serve 端到端測試（包含將 `data/webpages/` 改名後再啟動）；以 test config 跑一次 prepare 的 RAG build。

### Phase D：入口
**D1. 邏輯下移（保留舊入口作為薄包裝）**
- `run_prepare()` 移到 `pipelines/prepare.py`；`serve_forever()` 移到 `server/bootstrap.py`；`run_agent_build` 等函式移到 `pipelines/agent.py`；`exp.py` 的迴圈移到 `pipelines/eval.py`。
- 舊的 `src/prepare.py`、`src/serve.py`、`src/exp.py` 只保留參數解析，並呼叫新函式。
- 驗證：每步檢查，並用舊入口執行 serve 與 prepare（test config）。

**D2. `cli/` 與 console script**
- 新增 `cli/` 子命令，以及 `[project.scripts] website-copilot`。
- 刪除舊入口；刪除 `pythonpath = ["src"]`；更新 `scripts/multi_site.py`。
- 驗證：每步檢查、各子命令的 `--help`，以及 `uv run website-copilot serve` 端到端。

### Phase E：雜項（步驟順序不限，合併為一個 commit）
- **E1 widget**：以 extension 版覆蓋 static；新增 `make sync-widget` 與 CI `cmp`。驗證：`/static/demo.html` 顯示 typing indicator，且 `make sync-widget && git diff --exit-code extension/`。
- **E2 dev/**：刪除 `legacy`、`crawl4ai`、`llama_index`，`marp` 移到 `docs/progress_report/drafts/`，並移除 ruff 與 pyright 的 `dev/**` 排除規則。驗證：ruff 與 pyright 通過。
- **E3 `.env.example` 與 Makefile**：Makefile 新增 `check` 目標（ruff、pyright、pytest），同時作為 bisect 用指令。
- **E4 文件**：README、`docs/code/**`，將舊路徑與舊指令全數改新；以 grep 確認沒有殘留。

## 驗證

**每步檢查**（phase 內每一步完成後執行，每個 phase commit 前必須通過；E3 之後用 `make check` 執行）：
1. `uv sync`（B2 之後）。
2. `uv run ruff check . && uv run ruff format --check .`。
3. `uv run pyright`：錯誤數不得高於 A1 的基線。
4. `uv run pytest -m "not slow"`：通過數量不少於基線，且包含 import 冒煙測試。
5. C3 之後：`uv run python -c "import website_copilot.retrieval.registry, sys; print([m for m in sys.modules if 'crawl4ai' in m or 'ingestion.crawling' in m])"` 應輸出空 list。

**里程碑檢查**（B6、C3、D2 結束時）：
- serve 端到端：啟動 serve 並讀取既有的 `data/rag/*`，呼叫 `/api/chat` 取得 SSE，並確認 `/static/demo.html` 能正常使用。
- prepare：以 test config（或 `scripts/multi_site.py`）跑小規模建庫，確認 `runs/` 與 publish 行為不變（需要 API key）。

**完成後**：
- `grep -rn "from app\.\|from utils\.\|\"app\.\|src/test\|dev/" src tests scripts .github README.md docs/code` 無殘留。
- 可選：`uv run pytest -m slow tests/integration`。