# Workflow

## 一、主要檔案與角色

- workflow 依階段拆成下列模組，負責把 config、module 與 RunManager 串起來並執行實際流程：
  - [src/website_copilot/pipelines/prepare.py](src/website_copilot/pipelines/prepare.py)：Prepare 階段（爬蟲、圖片摘要、RAG 建置，以及三階段串接的 `run_prepare()`）。
  - [src/website_copilot/pipelines/serve.py](src/website_copilot/pipelines/serve.py)：Serve 階段（`run_agent_build()` 建構 agent、`run_server_build()` 建立 server、`run_serve()` 管理生命週期）；不 import 爬蟲與 VLM 模組。
  - [src/website_copilot/pipelines/exp.py](src/website_copilot/pipelines/exp.py)：RAG 查詢評估、Agent 問答（`run_agent_query()`）（實驗／除錯用）。
- [src/website_copilot/config/pipeline_config.py](src/website_copilot/config/pipeline_config.py)：定義 run 相關 dataclass（`BaseRunConfig` 與各 module 的 RunConfig），供 CLI 與程式使用。
- [src/website_copilot/storage/run_manager.py](src/website_copilot/storage/run_manager.py)：以 `for_run()`（3 層）/ `for_run_no_site()`（2 層）classmethod 建立 `runs/<timestamp>/<module>/<site_id>/<run>/` 路徑，負責 results、module_config、run_config 與 log 的輸出位置。
- [src/website_copilot/storage/run_persistence.py](src/website_copilot/storage/run_persistence.py)：結果持久化與發現函式（從 RunManager 分離的無狀態工具）。
- [src/website_copilot/storage/run_context.py](src/website_copilot/storage/run_context.py)：模組無關的共用 helper（`create_run_context()` / `create_run_no_site_context()` 的 run context 建立、`run_workflow_context()` 的 ExitStack logging 生命週期管理）。
- [src/website_copilot/storage/data_manager.py](src/website_copilot/storage/data_manager.py)：管理 `data/` 目錄的持久化資料，提供 `publish_*` 方法將 run 產物發布到 `data/aug_webpages/<site_id>/` 等路徑。
- `website-copilot prepare`（`cli/prepare.py` → `run_prepare()`）：Prepare 階段入口，依序執行**網站爬蟲** → **圖片摘要** → **RAG 建置**三個階段並 publish 到 `data/`。
- `website-copilot serve`（`cli/serve.py` → `run_serve()`）：Serve 階段入口，依序以 `run_agent_build()` 建構 agent、`run_server_build(agent)` 建立 Chat 伺服器，啟動並阻塞至中斷（CTRL+C）；只讀取 `data/vector_db/<site_id>.db`（不需要 `data/aug_webpages/`），缺少向量庫的站點不會被列為可用（`RAGRegistry` 經 `load_rag()` 載入，不建置）。
- `src/website_copilot/agent/tools/webpage_retriever.py`：將 RAG retriever 包裝為 LangChain `StructuredTool`，支援 `site_id` 多站路由，供下游 Agent 動態呼叫檢索。
- `src/website_copilot/retrieval/registry.py`：管理多站 RAG 實例（lazy + LRU 快取），供 Agent 在不同 `site_id` 間路由。
- `src/website_copilot/agent/tools/site_discovery.py`：`list_knowledge_bases` 工具，供 LLM 確認可用站點列表。
- [src/website_copilot/ingestion/crawling/website_crawler.py](src/website_copilot/ingestion/crawling/website_crawler.py)：實際執行網站爬取、Markdown 清理與資料整理的模組。
- [src/website_copilot/ingestion/augmentation/image_summarizer.py](src/website_copilot/ingestion/augmentation/image_summarizer.py)：實際執行圖片下載、VLM 摘要、快取與 Markdown 增強的模組。
- [src/website_copilot/retrieval/rag.py](src/website_copilot/retrieval/rag.py)：執行查詢、檢索、評估與資源釋放的 runtime 模組。
- [src/website_copilot/ingestion/indexing/index.py](src/website_copilot/ingestion/indexing/index.py)：`IndexBuilder` 負責向量庫的 clean / nodes / vector store / index 建置與載入，回傳 `IndexHandle`（nodes 與向量庫分別由 `node_pipeline.py`、`vector_store.py` 建立）。
- [src/website_copilot/retrieval/factory.py](src/website_copilot/retrieval/factory.py)：`RAGBuilder` 在 `IndexHandle` 之上建立 retriever / query engine；`build_rag()`（建置）與 `load_rag()`（serve 載入，絕不建置）為兩個入口。
- [src/website_copilot/config/website_crawler_config.py](src/website_copilot/config/website_crawler_config.py)、[src/website_copilot/config/image_summarizer_config.py](src/website_copilot/config/image_summarizer_config.py)、[src/website_copilot/config/rag_config.py](src/website_copilot/config/rag_config.py)、[src/website_copilot/config/agent_config.py](src/website_copilot/config/agent_config.py)：各模組對應的設定 pydantic model，負責從 `configs/` 載入與驗證。
- [src/website_copilot/utils/config_helper.py](src/website_copilot/utils/config_helper.py)：共用設定工具，提供 module_config.yml／run_config.yml 寫出與 config 顯示等功能；YAML 讀取與 extends 展開見 `config/yaml_helper.py`。

## 二、Workflow 解析與執行流程

1. workflow 的核心實作分散在 `pipelines/prepare.py`／`pipelines/serve.py`／`pipelines/exp.py`，共提供七個主要入口（另有 `run_prepare()` 串接 prepare 三階段、`run_serve()` 串接 `run_agent_build()` 與 `run_server_build()` 並管理生命週期）：
   - `run_website_crawler()`
   - `run_image_summarizer()`
   - `run_rag_build()`
   - `run_rag_query()`
   - `run_agent_build()` / `run_agent_query()`
   - `run_server_build()`
2. 這些函式都會先建立對應的 module 物件，再從對應的 config model 讀取 YAML 設定，最後將設定套用到 module 的 init 與執行參數。
3. 每個 workflow 都會建立或接收 [src/website_copilot/storage/run_manager.py](src/website_copilot/storage/run_manager.py) 的 `RunManager`，用來決定本次執行的輸出目錄。
4. Workflow 會透過 `utils.config_helper.save_module_config()` 寫出 `module_config.yml`（agent 的 `run_agent_build` / `run_agent_query` 會寫；`run_server_build` 不寫，server 的 run 目錄只有 `run_config.yml`），並由 `RunManager` 保存 `results.json`、`results/*.md` 與 `terminal.log`；`DataManager`（[src/website_copilot/storage/data_manager.py](src/website_copilot/storage/data_manager.py)）則負責將 run 產物發布到 `data/` 持久化路徑。
5. 所有入口的簽名一致：`run_xxx(run_config, overrides=None)`。`run_config`（RunConfig，必填）提供 `config_name`、`save`、`publish` 等執行參數，`overrides` 為 module config 的巢狀覆寫值（如 `{"retriever": {"similarity_top_k": 20}}`）；`run_config.yml` 一律以 `save_run_config()` 寫出。
6. 有站點的入口（crawler／summarizer／rag_build／rag_query）以 `SiteConfig.from_yaml(run_config.site)` 載入站點，以 `site.site_id` 決定 runs/ 與 data/ 的資料夾，並把站點設定另存為 `site_config.yml`。
7. `run_prepare(run_config: PrepareRunConfig)` 以同一個 `site` 與 `config_name` 建立 `WebsiteCrawlerRunConfig`／`ImageSummarizerRunConfig`／`RAGBuildRunConfig` 傳給各階段；`publish=True`（預設）時各階段 `save=False, publish=True`，`publish=False`（`--run.no-publish`）時 `save=True, publish=False` 且 RAG 以 runs/ 中本次的圖片摘要結果建庫。

## 三、主要 Workflow 入口

### 1. `run_website_crawler()`

- 目的：從指定網站爬取頁面、清理 Markdown，並產出可供後續流程使用的 crawl results。
- 流程：
  1. 建立 [src/website_copilot/ingestion/crawling/website_crawler.py](src/website_copilot/ingestion/crawling/website_crawler.py) 的 `WebsiteCrawler`。
  2. 載入站點（`configs/sites/{site}.yml`）與爬蟲參數（[src/website_copilot/config/website_crawler_config.py](src/website_copilot/config/website_crawler_config.py)，`configs/website_crawler/{config_name}.yml` 或 class 預設值）。
  3. 以爬蟲參數建立 `WebsiteCrawler`，以站點的 `crawl`（起始 URL、URL 模式、允許網域、路徑前綴）呼叫 `crawl_website()`。
  4. 若爬取成功，寫出 `module_config.yml`、`site_config.yml`、`results.json` 與 `results/*.md`。

### 2. `run_image_summarizer()`

- 目的：將 crawl results 中的圖片交給 VLM 做摘要，並輸出增強後的 Markdown。
- 流程：
  1. 建立 [src/website_copilot/ingestion/augmentation/image_summarizer.py](src/website_copilot/ingestion/augmentation/image_summarizer.py) 的 `ImageSummarizer`。
  2. 載入站點與 [src/website_copilot/config/image_summarizer_config.py](src/website_copilot/config/image_summarizer_config.py) 的參數（`configs/image_summarizer/{config_name}.yml` 或 class 預設值）。
  3. 若未直接傳入 `crawl_results`，則由 [src/website_copilot/storage/run_persistence.py](src/website_copilot/storage/run_persistence.py) 的 `load_latest_results(..., site_id=...)` 載入 runs/ 中**同站點**最近一次的 crawler 結果（找不到時報錯，不退回其他站點）。
  4. 執行圖片摘要後，寫出 `module_config.yml`、`site_config.yml`、`results.json` 與 `results/*.md`。

### 3. `run_rag_build()`

- 目的：建立 RAG 所需的 nodes、vector store、index、retriever 與 query engine（**不含 query 步驟**），並落盤建置產物。
- 流程：
  1. 載入站點與 [src/website_copilot/config/rag_config.py](src/website_copilot/config/rag_config.py) 的參數（`configs/rag/{config_name}.yml` 或 class 預設值）。
  2. 依 save／publish 決定向量庫位置，以 `build_target()` 產生 `RAGTarget`（資料來源預設 `data/aug_webpages/{site_id}`，`aug_webpages_data_use_latest_results` 時為 runs/ 中同站點最新的圖片摘要結果），再呼叫 `build_rag(config, target)`（[src/website_copilot/retrieval/factory.py](src/website_copilot/retrieval/factory.py)）；內部先以 `load_source()` 讀取 aug_webpages 來源（來源缺少時在清除既有向量庫前就失敗），再由 `IndexBuilder(config, target).build(source)` 重建：`clean()` → `build_nodes()` → `build_vector_store()`（**Milvus BGE-M3**，可選 `WeightedRanker` / `RRFRanker`）→ `build_index()`，回傳 `IndexHandle`（建庫只到 index 層級，不建 retriever / query engine）。
  3. `save=True` 時在 run 路徑寫出 `module_config.yml`、`site_config.yml` 與 `run_config.yml`，最後 `rag.close()` 釋放資源。config 在建庫過程中不會被改寫（位置都在 `RAGTarget`）。
  4. 一律重建，且**絕不直接寫入** `data/vector_db/<site_id>.db`；`publish=True` 時由 `DataManager.publish_vector_store()` 原子替換（先放 `<site_id>.db.tmp` 並寫入 `meta/`（module／site／run config 與 log），舊版 rename 成 `.old`、新版 rename 成 `<site_id>.db`，再刪 `.old`；中途失敗會還原舊版，向量庫與設定紀錄一定同版）。建庫結束時 `IndexHandle.close()` 會一併停止本地 Milvus Lite server（確保資料已 flush 後才搬移資料夾）。向量庫位置屬於執行期資訊，不寫入 `module_config.yml`（改記錄在 log 的「RAG Target」）。建庫位置：

     | save | publish | 建庫位置 | 結束後留下的檔案 |
     |---|---|---|---|
     | True | True | `runs/.../results/milvus.db` | runs/ 保留一份，另複製到 data/ 後原子替換 |
     | True | False | `runs/.../results/milvus.db` | 只有 runs/ |
     | False | True | `data/vector_db/.staging-*/<site_id>.db` | 以 rename 移入正式位置，staging 刪除；只有 data/ |
     | False | False | 系統暫存資料夾 | 無（結束時刪除） |

  5. 暫存資料夾（staging 或系統暫存）以 `try/finally` 保證刪除，建庫失敗時舊向量庫不受影響。

### 4. `run_rag_query()`

- 目的：以既有的 vector store / index 為基礎，執行多輪 query 與評估。只查詢、不建庫也不寫入 `data/`；建庫一律走 `run_rag_build()`。
- 流程：
  1. 載入站點與 `RAGConfig`，決定向量庫位置並以 `load_rag(config, target, build_query_engine=True)` 載入（向量庫不存在時報錯，不退回重建）：預設為 `published_target(site_id)`（`data/vector_db/{site_id}/milvus.db`）；指定 `--run.vector-store-run <rag-build 的 run 資料夾>` 時為 `vector_store_run_target()`（該 run 的 `results/milvus.db`，以 `site_config.yml` 核對站點、log 印出建庫設定來源）。再由 `RAGBuilder.build()` 建立 retriever（支援 `query_mode="hybrid"` 與 `filter_dict`）與 query engine。
  2. 呼叫 `build_evaluators(config)` 取得 Faithfulness / Relevancy evaluator。
  3. 以 `run_config.query`（`--run.query`）或站點的 `sample_query`（兩者皆無時報錯）進行多輪查詢，並以 `evaluate_response(evaluators, query, response)` 評估。
  4. 回報 faithfulness / relevancy 評估結果，並將每次 query 結果落盤：
     - `results.json` — 結構化結果（`config` / `summary` / `results` 三層；`summary` 含各評估 pass count 與 pass rate）
     - `results/query_{index}.md` — 每次 query 與回覆各一份，含來源與評估
  5. 寫出 `module_config.yml`、`site_config.yml` 與 `run_config.yml`。

### 5. `run_agent_build()` / `run_agent_query()`

- 目的：以 LangGraph `create_agent` 包裝 `webpage_retriever` + `list_knowledge_bases` 工具，執行 Agent 問答（`website-copilot run agent`；`run_agent_build()` 定義於 `pipelines/serve.py`、`run_agent_query()` 定義於 `pipelines/exp.py`）。舊版 `run_agent()` 已移除；`run_agent_query()` 與 `run_server_build()` 為完整入口（各自建立 run context、agent、落盤與關閉）；`run_agent_build()` 為 agent 建構 + 落盤的程式化 API，`run_serve()` 透過它建構 agent 後注入 `run_server_build()`，`run_agent_query()` 也透過它建構 agent。
- `run_agent_build(run_config: AgentRunConfig | ServeRunConfig, overrides=None) -> Agent`：
  1. 一律以 `create_run_no_site_context(module="agent_build", config_name=...)` 建立自己的 `RunManager`（`runs/<ts>/agent_build/<config>/`），並以 `with run_workflow_context(...)` 包住 logging 生命週期。
  2. 載入 `AgentConfig.from_yaml(run_config.config_name, overrides)` 後呼叫 `create_agent(config)`（內部建立 `Tool(config.config_name)`、LLM 與編譯圖；失敗時 `tool.close()` 後 re-raise）。
  3. 寫出 `module_config.yml` 與 `run_config.yml`（落盤失敗時 `agent.close()` 後 re-raise）；回傳**未關閉**的 agent，由呼叫端負責 `close()`。
- `run_agent_query(run_config: AgentRunConfig, overrides=None) -> None`（`query`、`thread_id`、`stream` 由 `run_config` 提供）：
  1. 以 `run_agent_build(run_config, overrides)` 建構 `Agent`（獨立的 `runs/<ts>/agent_build/<config>/`，寫出 `module_config.yml` 與 `run_config.yml`）。
  2. 以 `create_run_no_site_context(module="agent", config_name=..., base_folder="runs")` 建立 `RunManager` 與落盤路徑（`runs/<ts>/agent/<config>/`），並以 `run_workflow_context` 起頭；依 `stream` 選擇 `agent.astream_result()`（逐 token）或 `agent.ask()` 問答；`thread_id` 相同保留多輪記憶。
  3. `thread_id` 未提供時自動產生 `auto-{uuid}`（每次執行獨立）。
  4. 顯示回答與來源 URL，並以 `RunManager.save_agent_results_as_json(thread_id=..., results=[result], agent_config=agent.config)` 落盤 `results_{thread_id}.json`（讀取既有分檔 → 合併本輪 → 覆寫）且印出實際輸出路徑。
  5. 寫出 `run_config.yml`（不寫 `module_config.yml`），最後 `log_run_paths("complete")`；例外路徑只記錄 log 後 re-raise，由 `finally` 呼叫一次 `agent.close()` 釋放 RAG 資源。

### 6. `run_server_build()`

- 目的：以注入的 agent 透過 `ChatApp.create()` 建立 FastAPI app，並回傳持有 `chat_app` 的 `ChatServer`（**非阻塞**的 `uvicorn.Server` 子類；由 `run_serve()` 使用）。
- 流程：
  1. `run_server_build(agent, run_config: ServeRunConfig) -> ChatServer`（`host`／`port`／`allowed_origins` 由 `run_config` 提供）以 `create_run_no_site_context(module="server", config_name=agent.config.config_name, base_folder="runs")` 建立自己的 `RunManager`（`runs/<ts>/server/<config>/`，與 `run_agent_build` 的 run 目錄分開、時間戳可能不同）；不寫 `module_config.yml`。
  2. `ChatApp.create(agent=agent, run_manager=run_manager, allowed_origins=run_config.allowed_origins)` 組裝 app，再以 `uvicorn.Config(chat_app.app, host=..., port=...)` 建立 `uvicorn.Server`。
  3. 寫出 `run_config.yml`（路徑為 `run_manager.run_config_path`），最後 `log_run_paths("complete")`。
  4. 建立 app / server 過程失敗時 re-raise，**不關閉**注入的 agent（由建立 agent 的呼叫端負責）。
  5. 呼叫端只需 `server.run()` 阻塞（或 `await server.serve()`）；`ChatServer.serve()` 結束時（正常／中斷／例外）於 `finally` 自動呼叫 `chat_app.close()` 釋放 agent。
- `run_serve(run_config)`：以同一個 `ServeRunConfig` 呼叫 `run_agent_build(run_config)` → `run_server_build(agent, run_config)`（失敗時 `agent.close()` 後 re-raise）→ `server.run()`，並吞下 `KeyboardInterrupt`。

## 四、Workflow 與 RunManager

`RunManager` 是 workflow 的輸出樞紐，透過兩個 classmethod 建立目錄結構：

- `RunManager.for_run(module=..., site_id=..., run_name=...)` — 3 層：`runs/<timestamp>/<module>/<site_id>/<run>/`（crawler / summarizer / rag_build / rag_query）。
- `RunManager.for_run_no_site(module=..., run_name=..., base_folder=...)` — 2 層：`runs/<timestamp>/<module>/<run>/`（agent；`base_folder` 可切換根目錄）。兩者皆會呼叫 `init_module_run_paths()` 建出下列路徑：

- `runs/<timestamp>/<module>/<site_id>/<run>/results.json`
- `runs/<timestamp>/<module>/<site_id>/<run>/results/`
- `runs/<timestamp>/<module>/<site_id>/<run>/module_config.yml`
- `runs/<timestamp>/<module>/<site_id>/<run>/run_config.yml`
- `runs/<timestamp>/<module>/<site_id>/<run>/terminal.log`

`DataManager` 則負責將 run 產物發布到 `data/` 持久化路徑（如 `data/aug_webpages/<site_id>/`）。

**publish 時的 `terminal.log`**：發布到 `data/` 時，各階段的執行日誌一併保留（crawler → `data/raw_webpages/<site_id>/terminal.log`、summarizer → `data/aug_webpages/<site_id>/terminal.log`、rag_build → `data/vector_db/<site_id>.db/meta/terminal.log`），並隨 git 追蹤。
- `save=True`：複製 run 的 `terminal.log`。
- `save=False, publish=True`（`prepare` 預設）：沒有 `runs/`，改由 `storage.run_context.publish_log_file()` 在系統暫存資料夾建立 `terminal.log`，`run_workflow_context(log_path=...)` 把輸出寫進去，發布後整個暫存資料夾刪除。
- 發布一律在 `run_workflow_context` **結束之後**才進行（crawler／summarizer 的 `publish_run_metadata`、rag_build 的 `publish_vector_store` 皆然），確保 log 已關檔並壓縮進度列、內容完整；因此 log 不含發布動作本身的訊息。
- `save=False, publish=False`：不記錄 log 檔。

> 註：`rag_query` 會在 `results/` 下額外產生每次 query 一份的 `query_{index}.md`；`rag_build` 在 `save=True` 時把向量庫寫入 `results/milvus.db`，只有 publish 才會原子替換到 `data/vector_db/<site_id>.db`。
>
> 註：agent 對話結果由 `run_manager.save_agent_results_as_json()` 寫入 `results_{thread_id}.json`（讀取既有分檔 → 合併本輪 → 覆寫；未提供 `thread_id` 時自動 `auto-{uuid}`，CLI 與 server 行為一致）；agent 路徑無 `site_id` 層，也**不寫 `results.json`**。

Workflow 內部常見行為：

- `RunManager.for_run()` / `RunManager.for_run_no_site()`：建立本次 workflow 的 `RunManager`（取代已移除的 `set_module_path()` / `set_site_path()` / `set_run_path()` setter）。
- `run_manager.init_module_run_paths()`：初始化上述所有輸出路徑（由兩個 classmethod 內部呼叫）。
- `run_manager.log_run_paths("init" | "complete")`：以 Rich 表格顯示本次執行路徑。
- `run_manager.save_results_as_json(results, file_path=None)`：寫出 JSON 結果（crawler / summarizer 的爬取結果、`run_rag_query` 的 query 三層結構，或 agent 指定分檔）。
- `run_manager.save_agent_results_as_json(thread_id, results, agent_config)`：agent 對話結果落盤（呼叫端 `run_agent_query` / server `_event_stream` 傳入 `agent_config`）— 依 `thread_id` 寫出 `results_{thread_id}.json`（讀取既有分檔 → 合併本輪 → 覆寫；無既有分檔時以 `RunManager.find_thread_history_path()` 回掃歷史 run）。
- `run_manager.find_thread_history_path(base_folder, module_name, history_filename)`（staticmethod）：跨 timestamped run 目錄搜尋最新的 thread 歷史檔。
- 模組無關的持久化／發現函式位於 [src/website_copilot/storage/run_persistence.py](src/website_copilot/storage/run_persistence.py)：`save_results_as_md()`、`save_query_results_as_md()`、`load_latest_results()`、`load_latest_run_path()`（皆為無狀態函式，**非 RunManager 方法**）；image summarizer 未直接收到 `crawl_results` 時即呼叫 `load_latest_results()` 載入最近一次 crawler 輸出。

## 五、Workflow 與 Config 的互動

Workflow 不直接手寫設定檔，而是依賴各 module 的 config model 與共用 helper：

1. `src/website_copilot/config/*_config.py` 的 pydantic model 以 `from_yaml()` 從 `configs/<module>/<config_name>.yml` 載入設定。
2. `from_yaml()` 展開 `extends`、套用 overrides 後以 `model_validate()` 驗證，失敗時拋出含設定檔路徑與繼承鏈的 `ConfigValidationError`。
3. `save_module_config()` 會把實際使用到的設定寫回 `module_config.yml`，方便追蹤本次執行。
4. `save_run_config()` 由 workflow 函式寫出 run-level 參數（`run_config` 為必填，所有入口都會寫出）。

這表示 workflow 層的責任是「編排與執行」，而不是「定義設定格式」。設定格式與驗證應該維持在 `src/website_copilot/config/`。

## 六、使用範例

```bash
# Prepare：依序執行爬蟲 → 圖片摘要 → RAG 建置，publish 到 data/
uv run website-copilot prepare nculab                       # 站點為必填的位置參數
uv run website-copilot prepare ncucsie --run.config test   # 模組設定省略時使用 class 預設值

# Serve：啟動 Chat 伺服器（阻塞至中斷）
uv run website-copilot serve --run.port 8000
```

```bash
# 只跑 workflow 層的 RAG 建置流程（通常透過 CLI 或程式入口呼叫）
uv run website-copilot run rag-build nculab
```

```bash
# 先以 rag-build 建出實驗向量庫（寫入 runs/），再以 --run.vector-store-run 查詢它
uv run website-copilot run rag-build nculab --run.config test
uv run website-copilot run rag-query nculab --run.config test --run.vector-store-run runs/<ts>/rag_build/nculab/<run_name>
```

## 七、注意事項與建議

- 若要修改 workflow 的執行行為，優先檢查對應階段的 `src/website_copilot/pipelines/*.py`與對應的 `src/website_copilot/config/*_config.py`，不要把設定邏輯分散到 module 本體。
- 若要調整輸出目錄與 artifacts 命名，優先修改 [src/website_copilot/storage/run_manager.py](src/website_copilot/storage/run_manager.py)。
- 若要新增 workflow，建議先在 `src/website_copilot/pipelines/` 定義入口（serve 路徑不可 import 爬蟲／VLM 模組），再補上對應的 config model、RunManager 輸出行為與 `cli/` 子命令。

## 八、參考與證據

- [src/website_copilot/pipelines/prepare.py](src/website_copilot/pipelines/prepare.py)
- [src/website_copilot/pipelines/serve.py](src/website_copilot/pipelines/serve.py)
- [src/website_copilot/pipelines/exp.py](src/website_copilot/pipelines/exp.py)
- [src/website_copilot/storage/run_context.py](src/website_copilot/storage/run_context.py)
- [src/website_copilot/config/pipeline_config.py](src/website_copilot/config/pipeline_config.py)
- [src/website_copilot/storage/run_manager.py](src/website_copilot/storage/run_manager.py)
- [src/website_copilot/storage/run_persistence.py](src/website_copilot/storage/run_persistence.py)
- [src/website_copilot/storage/data_manager.py](src/website_copilot/storage/data_manager.py)
- [src/website_copilot/cli/](src/website_copilot/cli/)
- [src/website_copilot/ingestion/crawling/website_crawler.py](src/website_copilot/ingestion/crawling/website_crawler.py)
- [src/website_copilot/ingestion/augmentation/image_summarizer.py](src/website_copilot/ingestion/augmentation/image_summarizer.py)
- [src/website_copilot/retrieval/rag.py](src/website_copilot/retrieval/rag.py)
- [src/website_copilot/config/website_crawler_config.py](src/website_copilot/config/website_crawler_config.py)
- [src/website_copilot/config/image_summarizer_config.py](src/website_copilot/config/image_summarizer_config.py)
- [src/website_copilot/config/rag_config.py](src/website_copilot/config/rag_config.py)
- [src/website_copilot/utils/config_helper.py](src/website_copilot/utils/config_helper.py)