# Website Copilot
> 專案涵蓋三階段：資訊檢索（Phase 1）、AI Agent（Phase 2）、嵌入式互動介面（Phase 3）。後續規劃涵蓋網站導航與專責代理。

Website Copilot 是一個 Python 專案，將網站內容轉換為可檢索的知識庫，並以 LangGraph Agent + RAG 檢索回答使用者問題。它會爬取網頁、清理並格式化內容、使用視覺語言模型摘要圖片、建立本地向量索引，並提供可嵌入網站的串流聊天介面（iframe / script widget / Chrome Extension）。


## 專案功能

### Phase 1：資訊檢索

- 爬取網站並匯出已清理的 Markdown 頁面。
- 摘要網頁圖片並將說明附加到 Markdown 輸出中。
- 建立或載入本地 Milvus 向量索引以進行混合檢索，同步進行語意比對與關鍵字比對。
- 利用爬蟲階段注入的頁面類型標籤，在檢索前隔離跨類別雜訊。
- 將檢索能力包裝為工具，供下游 Agent 動態呼叫與過濾。
- 使用 Gemini / GPT 驅動的查詢引擎處理索引後內容，並自動評估回答品質。
- 保存每次執行的輸出 artefacts、日誌和生成的 Markdown。

### Phase 2：AI Agent

- 以 LangGraph `create_agent` 包裝 `webpage_retriever` + `list_knowledge_bases` 工具，自動檢索後回答（回答內含引用來源 URL）。
- 多站 RAG 路由 — `RAGRegistry` 管理多個 `site_id` 對應的 RAG 實例（lazy 載入 + LRU 快取；只讀取已 publish 的向量庫，不建置）；`webpage_retriever` 接受 `site_id` 參數路由至對應知識庫。
- 多輪對話記憶（`InMemorySaver` + `thread_id`）。
- SSE 逐 token 串流（CLI 與 server 共用 `agent.astream_text()` 核心）。
- 對話落盤 `runs/<ts>/server/<config>/results_<thread_id>.json`（CLI `run agent` 為 `runs/<ts>/agent/<config>/`；讀取既有分檔 → 合併本輪 → 覆寫，`thread_id` 未提供時自動 `auto-{uuid}`）。

### Phase 3：嵌入式互動介面

- FastAPI + SSE 聊天 API（`POST /api/chat`，事件協定 token / done / error）。
- iframe 嵌入（`/static/chat.html`）、script widget（`/static/widget.js`，shadow DOM 隔離樣式）。
- Chrome Extension（`extension/`，background 代理繞過 CSP/CORS；`content.js` 偵測 `hostname` 自動帶入 `page_url`）。
- 前端 markdown 渲染（粗體 / 列表 / 連結 / 程式碼，先 escape 防 XSS）。
- Service Worker Keepalive（`chrome.alarms`）、Typing Indicator、跨頁面 session 共享（`chrome.storage.session`）。

## 專案流程

1. 爬取目標網站，從 URL 解析頁面類型，將結果儲存為 Markdown 和 JSON。
2. 摘要爬取結果中的圖片，生成增強版 Markdown。
3. 將處理後的 Markdown 載入 Milvus 向量索引（BGE-M3），同時建立稠密向量與稀疏向量索引。
4. 將檢索能力包裝為工具，支援動態過濾條件供 Agent 呼叫；多站知識庫由 `RAGRegistry` 統一管理。
5. 執行查詢時以 Dense + Sparse 混合檢索，過濾指定頁面類型，由 LLM 生成有來源的回答。
6. Agent 以 LangGraph 推理迴圈呼叫檢索工具（支援 `site_id` 路由），回答附引用來源；聊天伺服器以 SSE 串流傳給前端。
7. 前端以 iframe / widget / Extension 三種表面嵌入網站，支援多輪對話與 markdown 渲染；Extension 自動偵測來源站點。

## 檔案結構

下面範例列出本專案的根目錄與主要子目錄（以實際檔案為準）：

```text
.
├── .env.example                 # 環境變數範本（cp .env.example .env）
├── prek.toml                    # ruff/prek 設定
├── pyproject.toml               # Python 專案設定、依賴與 `website-copilot` console script
├── README.md
├── uv.lock
├── src/website_copilot/
│   ├── schemas.py               # 跨層共用資料型別（GenerationResult）
│   ├── cli/                     # `website-copilot <subcommand>`（tyro 子命令）
│   │   ├── __init__.py          # main()：prepare / serve / run 分派
│   │   ├── prepare.py  serve.py # 兩階段入口的參數定義
│   │   └── run.py               # run website-crawler | image-summarizer | rag-build | rag-query | agent
│   ├── config/                  # AgentConfig / RAGConfig / 爬蟲與圖片摘要 config；site_config.py（SiteConfig）；pipeline_config.py（RunConfig）；base_config.py（pydantic 基底）、yaml_helper.py（YAML 讀取與 extends）、overrides.py（CLI 覆寫參數自動產生）、prompts.py（長 prompt 預設值）
│   ├── ingestion/
│   │   ├── crawling/            # website_crawler / markdown_cleaner（含 LLM exclude_words）/ html_date_extractor
│   │   ├── augmentation/        # image_summarizer（VLM 圖片摘要）
│   │   └── indexing/            # source / transforms / node_pipeline / vector_store / index（IndexBuilder → IndexHandle）
│   ├── retrieval/
│   │   ├── rag.py               # RAG（index_handle + retriever + query engine）
│   │   ├── factory.py           # RAGBuilder + build_rag（建置）+ load_rag（serve 載入，絕不建置）
│   │   ├── evaluation.py        # evaluator 建立 / 評估 / prompts / 結果序列化
│   │   ├── registry.py          # RAGRegistry（多站 RAG 實例管理，lazy + LRU）
│   │   └── llama_index_helpers.py
│   ├── agent/
│   │   ├── agent.py             # LangGraph Agent（Agent / create_agent / ask / astream_text / astream_result / close）
│   │   ├── langchain_helper.py  # LangChain 輔助（create_llm / thread_config / extract_sources）
│   │   └── tools/               # webpage_retriever（多站路由）/ site_discovery（list_knowledge_bases）
│   ├── storage/                 # DataManager（publish_*）/ RunManager / run_persistence / run_context
│   ├── server/
│   │   ├── app.py               # FastAPI + SSE + DOMAIN_SITE_MAP + resolve_site_id
│   │   ├── server.py            # ChatServer（uvicorn.Server 子類，持有 ChatApp，結束時自動關閉）
│   │   └── static/              # chat.html（iframe）/ widget.js（來源，含 typing indicator）/ demo.html
│   ├── pipelines/
│   │   ├── prepare.py           # run_website_crawler / run_image_summarizer / run_rag_build / run_prepare
│   │   ├── serve.py             # run_agent_build / run_server_build / serve（不 import 爬蟲）
│   │   └── exp.py               # run_rag_query / run_agent_query（實驗／除錯用）
│   └── utils/                   # config_helper / log_helper
├── tests/
│   ├── unit/                    # 單元測試（預設執行）
│   └── integration/             # 整合測試（cost 標記：會呼叫 LLM API）
├── extension/                   # Chrome Extension（M4）
│   ├── manifest.json            # MV3：content_scripts + background + alarms/storage 權限
│   ├── background.js            # 代理 fetch SSE（繞過 CSP/CORS）+ keepalive + thread_id 共享
│   ├── content.js               # 注入 widget + 偵測 hostname 帶入 page_url
│   └── widget.js                # 由 server/static/widget.js 同步（scripts/sync-widget.sh，CI 比對）
├── scripts/                     # 開發常用指令
│   ├── check.sh                 # 依序執行 lint.sh → test.sh → check-widget.sh
│   ├── lint.sh                  # ruff check + ruff format 檢查 + pyright（--fix 自動修正）
│   ├── test.sh                  # pytest tests/unit（額外參數傳給 pytest）
│   ├── check-widget.sh          # 確認 widget.js 兩份一致
│   ├── clean-runs.sh            # 刪除 runs/ 中今天以前的 run（--dry-run / --yes）
│   └── sync-widget.sh           # 同步 widget.js 到 extension/
├── configs/
│   ├── README.md                # 設定檔撰寫說明（站點／模組設定、extends、YAML 注意事項）
│   ├── sites/                   # 站點設定：nculab / ncucsie（site_id、sample_query、爬取範圍）
│   ├── website_crawler/         # 模組設定：test.yml（只寫與 class 預設值不同的部分）
│   ├── image_summarizer/
│   ├── rag/
│   └── agent/
├── data/                        # prepare 與 serve 之間的唯一介面（已 publish 的結果）
│   ├── raw_webpages/<site_id>/  # 爬蟲原始輸出（fit_markdown）
│   ├── aug_webpages/<site_id>/  # 圖片摘要後的最終結果（enhanced_markdown，RAG 建庫讀這份）
│   └── rag/<site_id>.db/        # 向量資料庫（Milvus Lite 資料夾）；建庫設定備份在其中的 meta/
├── docs/
│   ├── project.md               # 專案總覽與路線圖
│   ├── code/                    # 各階段實作說明（phase1 / phase2_3_mvp / runs）
│   ├── work/                    # 工作紀錄
│   └── progress_report/         # 進度報告（依日期分資料夾，marp 投影片與 PDF）
└── runs/                        # 執行結果與聊天記錄（以時間戳資料夾儲存，不進版控）
```

## 需求

- Python 3.13.12 或更新版本，已在 `pyproject.toml` 中宣告。
- 可正常執行的 Playwright / 瀏覽器環境，用於爬取。
- 嵌入、查詢與圖片摘要模型的 API 金鑰。

專案依賴已在 `pyproject.toml` 中聲明，包含常見的套件（例如 `crawl4ai`, `playwright`,
`llama-index` 與其外部整合、`litellm`, `rich`, `python-dotenv`, `mdformat` 等）。

## 安裝

```bash
uv sync                     # 建立 .venv 並以 editable 模式安裝專案（含 website-copilot 指令）
uv run playwright install   # 爬蟲所需的瀏覽器
cp .env.example .env        # 填入 API 金鑰
```

如果你使用不同的環境管理方式，請從 `pyproject.toml` 安裝依賴（`pip install -e .`），並確保在執行爬蟲前已安裝 Playwright 瀏覽器。

## 設定

設定分成站點與模組兩類（撰寫方式見 [configs/README.md](configs/README.md)），環境變數從 `.env` 讀取：

- **站點設定**（`configs/sites/{site_id}.yml`）：站點身分（`site_id`）、`sample_query` 與爬取範圍（起始 URL、URL 模式、允許網域、路徑前綴）。CLI 以位置參數指定站點。
- **模組設定**（`configs/{module}/{name}.yml`）：參數的預設值寫在 `src/website_copilot/config/*_config.py` 的 config class，設定檔只寫與預設值不同的部分，以 `--run.config <name>` 指定（省略時為 class 預設值）。`uv run website-copilot run <module> --help` 會列出所有參數與預設值。
  - 爬蟲（`website_crawler`）：爬取深度、頁面數量限制、內容過濾、exclude words 產生。
  - 圖片摘要（`image_summarizer`）：圖片下載逾時、重試、快取、模型、prompt 與圖片來源模式。
  - RAG（`rag`）：切塊、向量庫與 hybrid ranker、embedding、檢索與 query engine。
  - Agent（`agent`）：LLM 與 system prompt。

### 環境變數

範本見 `.env.example`。各模組依設定檔中的模型名稱（`gpt-*` / `gemini-*`）選用對應金鑰：

| Variable | Used by | Purpose |
| --- | --- | --- |
| `OPENAI_API_KEY` | `ingestion/indexing/index.py`、`retrieval/llama_index_helpers.py`、`agent/langchain_helper.py`、`ingestion/augmentation/image_summarizer.py` | Embedding（`text-embedding-3-*`），以及 `gpt-*` 的回答生成 / 評估 / Agent / 圖片摘要。 |
| `GEMINI_API_KEY` | `retrieval/llama_index_helpers.py`、`agent/langchain_helper.py`、`ingestion/augmentation/image_summarizer.py` | `gemini-*` 的回答生成 / 評估 / Agent / 圖片摘要。 |

## 使用方式

### 系統分為兩個階段

所有功能都透過 `website-copilot` 指令執行（`uv run website-copilot --help` 查看子命令）：

| 階段 | 入口 | 職責 |
|---|---|---|
| Prepare | `website-copilot prepare` | 網站爬蟲 → 圖片摘要 → RAG 建置，結果 publish 到 `data/` |
| Serve | `website-copilot serve` | 啟動 Chat 伺服器，只讀取 `data/vector_db/<site_id>.db`，不做任何建置（不需要 `data/aug_webpages/`） |

兩階段唯一的介面是 `data/` 目錄：站點只有在 prepare 成功 publish 向量庫後，才會出現在 server 的可用知識庫中。

### Prepare：爬取、圖片摘要與 RAG 建置

```bash
uv run website-copilot prepare ncucsie                 # 站點為必填的位置參數
uv run website-copilot prepare nculab --run.config test --run.no-publish
```

站點（位置參數）決定爬取範圍與 `data/` 下的資料夾，`--run.config` 決定各階段使用的模組設定（預設 `default`，即 class 預設值）。這會依序執行網站爬蟲、圖片摘要、RAG 建置，並發布到 `data/`；加上 `--run.no-publish` 則只存到 `runs/`、不寫入 `data/`。重新 prepare 後需重啟 server 才會載入新的向量庫。

各階段也可以單獨執行（`website-copilot run <module>`）：

```bash
uv run website-copilot run website-crawler nculab --module.init.max-pages 10
uv run website-copilot run image-summarizer nculab     # 讀取 runs/ 中同站點最新的爬蟲結果
uv run website-copilot run rag-build nculab --run.publish
```

### 執行 RAG 查詢

```bash
# 查詢已 publish 的向量庫；未指定 --run.query 時使用站點的 sample_query
uv run website-copilot run rag-query ncucsie
uv run website-copilot run rag-query nculab --run.query "實驗室的成員有哪些人？"
# 查詢 runs/ 中 rag-build 建出的實驗向量庫（只查詢，不建庫、不寫入 data/）
uv run website-copilot run rag-query nculab --run.vector-store-run runs/<ts>/rag_build/nculab/<run_name>

# 自訂 top-k（透過 CLI 覆寫，巢狀結構與設定檔相同）
uv run website-copilot run rag-query nculab --module.retriever.similarity-top-k 10 --module.retriever.hybrid-top-k 20
```

`--module.*` 由各 module config 自動產生（`uv run website-copilot run rag-query --help` 可列出所有參數）。

### 執行 Agent 問答（CLI）

```bash
# 單輪問答（自動檢索 + 附引用來源 + 落盤 runs/）
uv run website-copilot run agent --run.query "實驗室的成員有哪些人？"

# 多輪對話（相同 thread-id 記得上下文）
uv run website-copilot run agent --run.query "實驗室的成員有哪些人？" --run.thread-id demo
uv run website-copilot run agent --run.query "這些人中，有誰是研究生？" --run.thread-id demo

# 串流顯示（逐 token 輸出）
uv run website-copilot run agent --run.query "實驗室的研究方向？" --run.stream
```

### 啟動聊天伺服器（SSE）

```bash
# 啟動 serve 階段（阻塞至中斷）
uv run website-copilot serve --run.port 8000

# 限縮 CORS 來源（預設全開放）
uv run website-copilot serve --run.allowed-origins https://lab.example.edu.tw
```

啟動後瀏覽器開啟 **http://localhost:8000/**（自動轉至嵌入示範頁），即可用 iframe 與 widget 兩種方式對話。

### 三種嵌入方式

```html
<!-- ① iframe：網頁任意位置 -->
<iframe src="http://localhost:8000/static/chat.html" width="360" height="520"></iframe>

<!-- ② script widget：<\/body> 前加一行（右下角浮動 🤖） -->
<script src="http://localhost:8000/static/widget.js" data-endpoint="http://localhost:8000"><\/script>

<!-- ③ Chrome Extension：chrome://extensions → 載入未封裝項目 → 選 extension/ 資料夾 -->
<!--    在任何網站右下角浮出 widget（background 代理繞過 CSP/CORS） -->
```

### 執行測試

```bash
# 單元測試（全部 mock，不需 API 金鑰）
./scripts/test.sh              # = uv run pytest tests/unit

# 整合測試（需 API 金鑰；cost 標記的測試會產生 API 費用）
uv run pytest tests/integration
uv run pytest tests/integration -m "not cost"   # 略過會呼叫 LLM API 的測試
```

## 輸出

每次執行會在 `runs/<timestamp>/<module>/<site_id>/<run_name>/`（無 site 的模組如 agent 為 `runs/<timestamp>/<module>/<run_name>/`）下產生以下 artefacts：

- `results.json` — 結構化結果（爬取/摘要結果，或 `run_rag_query` 的 query 三層結構）
- `results/*.md` — 每頁的 Markdown 內容（`run_rag_query` 另含每次 query 一份的 `results/query_{index}.md`）
- `module_config.yml` — 本次執行的模組參數備份（不含站點與向量庫位置等執行期資訊）
- `site_config.yml` — 本次使用的站點設定（有站點的模組）
- `run_config.yml` — run-level 參數（含 `save` / `publish`；所有入口都會寫出，`website-copilot prepare` 由各階段各自寫出）
- `terminal.log` — 執行日誌

向量資料庫預設持久化於 `data/vector_db/<site_id>.db/`（Milvus Lite 要求資料夾名稱以 `.db` 結尾，collection 固定為 `chunks`）：
- `collections/chunks/…` — Milvus Lite 向量儲存（`indexes/` 為載入時產生的可重建索引，已被 `.gitignore` 忽略）
- `meta/` — 建庫的 `module_config.yml`／`site_config.yml`／`run_config.yml`／`terminal.log`，與向量庫同一次原子替換

發布到 `data/` 的爬蟲與圖片摘要結果（`data/raw_webpages/<site_id>/`、`data/aug_webpages/<site_id>/`）同樣附有 `module_config.yml`／`site_config.yml`／`run_config.yml`／`terminal.log`。即使 publish 模式不寫 `runs/`（`prepare` 預設），日誌也會保留。

`run_rag_build` 絕不直接寫入 `data/vector_db/<site_id>.db`，只透過 publish 原子替換（先放 `<site_id>.db.tmp`、寫入 `meta/`，再 rename 取代舊版），因此執行中的 server 不會讀到建到一半的向量庫，建庫失敗時舊版也完整保留。建庫位置依 `save`／`publish` 而定：

| save | publish | 建庫位置 | 結束後留下的檔案 |
|---|---|---|---|
| True | True | `runs/.../results/milvus.db` | runs/ 保留一份，另複製到 data/ 後原子替換 |
| True | False | `runs/.../results/milvus.db` | 只有 runs/ |
| False | True | `data/vector_db/.staging-*/<site_id>.db` | 以 rename 移入正式位置，staging 刪除；只有 data/ |
| False | False | 系統暫存資料夾 | 無（結束時刪除） |

### 聊天記錄（`runs/`）

Agent 對話落盤於 `runs/<timestamp>/server/<config>/`（`website-copilot serve`）或 `runs/<timestamp>/agent/<config>/`（`website-copilot run agent`）：

- `results_<thread_id>.json` — 依 thread_id 分檔的對話歷史（讀取既有分檔 → 合併本輪 → 覆寫；`thread_id` 未提供時自動 `auto-{uuid}`）；跨 run 查找歷史只在同一 module（`server` 或 `agent`）內進行
- `run_config.yml` / `terminal.log` — 設定備份與日誌（不含 `module_config.yml`）

> 註：`website-copilot serve` 與 `website-copilot run agent` 另會產生 `runs/<timestamp>/agent_build/<config>/`（`run_agent_build` 寫出 `module_config.yml` 與建構日誌），與對話的 run 目錄分開；`results.json` 僅用於爬蟲／摘要／`run_rag_query` 等模組，agent 不寫。

## 開發

- `./scripts/check.sh`：依序執行三組檢查，任一組失敗即中止（可用於 `git bisect run`）；各組也可單獨執行：
  - `./scripts/lint.sh`：`ruff check`、`ruff format --check`、`pyright`；加 `--fix` 改為自動修正 ruff 問題並格式化（`ruff check --fix`、`ruff format`）
  - `./scripts/test.sh`：`pytest tests/unit`（額外參數會傳給 pytest，如 `./scripts/test.sh -x`）
  - `./scripts/check-widget.sh`：確認 `extension/widget.js` 與來源一致
- 格式化與 lint 透過 `ruff` 與 `prek.toml` 設定（`./scripts/lint.sh --fix` 自動修正）。
- `widget.js` 以 `src/website_copilot/server/static/widget.js` 為來源，修改後執行 `./scripts/sync-widget.sh` 同步到 `extension/`（CI 會比對兩份是否一致）。
- `./scripts/clean-runs.sh`：刪除 `runs/` 中今天以前的 run 資料夾（依 `YYYYMMDD_HHMMSS` 名稱判斷，其他項目保留）；刪除前會列出清單與合計大小並要求確認，`--dry-run` 只列出、`--yes` 略過確認。注意 agent 的 `results_<thread_id>.json` 會跨 run 累積對話歷史，清理後舊 thread 的歷史也會一併移除。
- `tests/integration/test_module.py` 以測試設定檔逐一執行各 run function（爬蟲、摘要器、RAG 建置、agent 建構與問答）。
- `tests/integration/test_pipeline.py` 以測試設定檔執行 prepare 完整流程（`publish=False`：只存到 `runs/`，不覆寫 `data/`），並啟動後自動關閉 server。

## 文件

專案的實作筆記與路線圖位於 `docs/`：

- `docs/project.md` — 專案總覽、階段規劃與路線圖
- `docs/code/phase1/phase1.md` — Phase 1 實作概覽與已知問題
- `docs/code/phase1/modules/data_collect.md` — 爬蟲模組說明
- `docs/code/phase1/modules/data_preprocess.md` — 圖片摘要模組說明
- `docs/code/phase1/modules/data_retrieve.md` — RAG 檢索模組說明
- `docs/code/phase2_3_mvp/phase2_3_mvp.md` — Phase 2/3 實作概覽
- `docs/code/phase2_3_mvp/modules/agent.md` — Agent 模組說明
- `docs/code/phase2_3_mvp/modules/server.md` — 聊天伺服器說明
- `docs/code/phase2_3_mvp/modules/interface.md` — 嵌入表面說明
- `docs/code/runs/cli.md` — CLI 使用方式
- `docs/code/runs/config.md` — 設定機制說明
- `docs/code/runs/workflow.md` — Workflow 流程說明
- `docs/work/2026_0921/2026_0907-workflow_module_refactor/dev_log.md` — 9/7–9/10 實作紀錄（§七：Agent / RunManager 責任重構，含 CR / QA）
- `docs/survey/phase1/data_process_method.md` — 資料處理方法 survey

## 狀態

目前實作涵蓋：

- 網站爬取、Markdown 清理與頁面類型分類
- HTML 日期擷取（JSON-LD → OG → `<time>` → Generic meta → Dublin Core → HTTP Last-Modified）
- 圖片摘要與快取/重試邏輯
- 本地向量檢索（Milvus BGE-M3）
- 稠密 + 稀疏混合檢索（WeightedRanker / RRFRanker）
- Metadata 頁面類型過濾
- 多站 RAG（`RAGRegistry` + `list_knowledge_bases` + `webpage_retriever` site_id 路由）
- RAG Retriever Tool（StructuredTool 封裝，供 Agent 呼叫）
- Gemini / GPT 驅動的來源檢索式查詢引擎
- 自動化回答品質評估（Faithfulness + Relevancy）
- Query 結果落盤（`results.json` + `results/query_{index}.md`）；RAG 建庫位置依 `save`／`publish` 決定，publish 以原子替換更新 `data/vector_db/<site_id>.db`
- Prepare／Serve 兩階段分離（`website-copilot prepare`／`website-copilot serve`，以 `data/` 為唯一介面）
- Chrome Extension 站點偵測（`hostname` → `page_url` → `resolve_site_id`）
- Service Worker Keepalive + Typing Indicator + 跨頁面 session 共享

後續規劃請參閱 `docs/project.md`。
