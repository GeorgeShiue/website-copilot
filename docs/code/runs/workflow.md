# Workflow

## 一、主要檔案與角色

- [src/app/workflow/workflow.py](src/app/workflow/workflow.py)：定義七個主要入口（爬蟲、圖片摘要、RAG 建置／查詢、Agent 建置／問答與 server 啟動），負責把 config、module 與 RunManager 串起來並執行實際流程。
- [src/app/configs/workflow_config.py](src/app/configs/workflow_config.py)：定義 run 相關 dataclass（`BaseRunConfig` 與各 module 的 RunConfig），供 CLI 與程式使用。
- [src/app/workflow/run_manager.py](src/app/workflow/run_manager.py)：以 `for_run()`（3 層）/ `for_run_no_site()`（2 層）classmethod 建立 `runs/<timestamp>/<module>/<site_id>/<run>/` 路徑，負責 results、module_config、run_config 與 log 的輸出位置。
- [src/app/workflow/run_persistence.py](src/app/workflow/run_persistence.py)：結果持久化與發現函式（從 RunManager 分離的無狀態工具）。
- [src/app/workflow/workflow_helper.py](src/app/workflow/workflow_helper.py)：模組無關的共用 helper（`create_run_context()` / `create_run_no_site_context()` 的 run context 建立、`run_workflow_context()` 的 ExitStack logging 生命週期管理）。
- [src/app/workflow/data_manager.py](src/app/workflow/data_manager.py)：管理 `data/` 目錄的持久化資料，提供 `publish_*` 方法將 run 產物發布到 `data/webpages/<site_id>/` 等路徑。
- [src/main.py](src/main.py)：示範以程式直呼 workflow 的串接入口，依序執行**網站爬蟲** → **圖片摘要** → **RAG 建置**三個階段，最後以 `run_app()` 啟動 Chat 伺服器並阻塞至中斷（CTRL+C）。
- `src/app/tools/webpage_retriever.py`：將 RAG retriever 包裝為 LangChain `StructuredTool`，支援 `site_id` 多站路由，供下游 Agent 動態呼叫檢索。
- `src/app/tools/rag_registry.py`：管理多站 RAG 實例（lazy + LRU 快取），供 Agent 在不同 `site_id` 間路由。
- `src/app/tools/site_discovery.py`：`list_knowledge_bases` 工具，供 LLM 確認可用站點列表。
- [src/app/engines/website_crawler.py](src/app/engines/website_crawler.py)：實際執行網站爬取、Markdown 清理與資料整理的模組。
- [src/app/engines/webpage_image_summarizer.py](src/app/engines/webpage_image_summarizer.py)：實際執行圖片下載、VLM 摘要、快取與 Markdown 增強的模組。
- [src/app/engines/rag/rag.py](src/app/engines/rag/rag.py)：執行查詢、檢索、評估與資源釋放的 runtime 模組。
- [src/app/engines/rag/rag_factory.py](src/app/engines/rag/rag_factory.py)：負責 RAG 建構流程（`RAGBuilder` / `NodePipelineBuilder` / `VectorStoreBuilder`）。
- [src/app/configs/website_crawler_config.py](src/app/configs/website_crawler_config.py)、[src/app/configs/webpage_image_summarizer_config.py](src/app/configs/webpage_image_summarizer_config.py)、[src/app/configs/rag_config.py](src/app/configs/rag_config.py)、[src/app/configs/agent_config.py](src/app/configs/agent_config.py)：各模組對應的設定 dataclass，負責從 `configs/` 載入與驗證。
- [src/utils/config_helper.py](src/utils/config_helper.py)：共用設定工具，提供 TOML 載入、覆寫、寫回與 config 顯示等功能。

## 二、Workflow 解析與執行流程

1. workflow 的核心實作集中在 [src/app/workflow/workflow.py](src/app/workflow/workflow.py)，目前提供七個主要入口：
   - `run_website_crawler()`
   - `run_webpage_image_summarizer()`
   - `run_rag_build()`
   - `run_rag_query()`
   - `run_agent_build()` / `run_agent_query()`
   - `run_app()`
2. 這些函式都會先建立對應的 module 物件，再從對應的 config dataclass 讀取 TOML 設定，最後將設定套用到 module 的 init 與執行參數。
3. 每個 workflow 都會建立或接收 [src/app/workflow/run_manager.py](src/app/workflow/run_manager.py) 的 `RunManager`，用來決定本次執行的輸出目錄。
4. Workflow 會透過 `utils.config_helper.save_module_config_as_toml()` 寫出 `module_config.toml`（agent 的 `run_agent_build` / `run_agent_query` 會寫，`run_app` 不寫），並由 `RunManager` 保存 `results.json`、`results/*.md` 與 `terminal.log`；`DataManager`（[src/app/workflow/data_manager.py](src/app/workflow/data_manager.py)）則負責將 run 產物發布到 `data/` 持久化路徑。
5. `run_config.toml` 由 workflow 函式在收到 `run_config`（非 None）時呼叫 `save_run_config_as_toml()` 寫出；`src/cli.py` 會傳入 run 參數（`src/main.py` 目前不寫出）。

## 三、主要 Workflow 入口

### 1. `run_website_crawler()`

- 目的：從指定網站爬取頁面、清理 Markdown，並產出可供後續流程使用的 crawl results。
- 流程：
  1. 建立 [src/app/engines/website_crawler.py](src/app/engines/website_crawler.py) 的 `WebsiteCrawler`。
  2. 透過 [src/app/configs/website_crawler_config.py](src/app/configs/website_crawler_config.py) 從 `configs/website_crawler/{config_name}.toml` 讀入設定。
  3. 套用 `override_init_config()` 與 `crawl_website()` 的執行參數。
  4. 若爬取成功，寫出 `module_config.toml`、`results.json` 與 `results/*.md`。

### 2. `run_webpage_image_summarizer()`

- 目的：將 crawl results 中的圖片交給 VLM 做摘要，並輸出增強後的 Markdown。
- 流程：
  1. 建立 [src/app/engines/webpage_image_summarizer.py](src/app/engines/webpage_image_summarizer.py) 的 `WebpageImageSummarizer`。
  2. 透過 [src/app/configs/webpage_image_summarizer_config.py](src/app/configs/webpage_image_summarizer_config.py) 載入 `configs/webpage_image_summarizer/{config_name}.toml`。
  3. 若未直接傳入 `crawl_results`，則由 [src/app/workflow/run_persistence.py](src/app/workflow/run_persistence.py) 的 `load_latest_results()` 自動載入最近一次 crawler 結果。
  4. 執行圖片摘要後，寫出 `module_config.toml`、`results.json` 與 `results/*.md`。

### 3. `run_rag_build()`

- 目的：建立 RAG 所需的 nodes、vector store、index、retriever 與 query engine（**不含 query 步驟**），並落盤建置產物。
- 流程：
  1. 透過 [src/app/configs/rag_config.py](src/app/configs/rag_config.py) 載入 `configs/rag/{config_name}.toml`。
  2. 呼叫 `create_rag(...)`（[src/app/engines/rag/rag_factory.py](src/app/engines/rag/rag_factory.py)）建立並回傳已建構的 `RAG`；內部以 `RAGBuilder(config).build_reusable(rag, force_rebuild=...)` 一鍵建構：`build_nodes()` → `build_vector_store()`（**Milvus BGE-M3**，可選 `WeightedRanker` / `RRFRanker`）→ `build_index()` → `build_retriever()`（支援 `query_mode="hybrid"` 與 `filter_dict`）→ `build_query_engine()`。
  3. 在 run 路徑寫出 `module_config.toml` 與（`run_config` 非 None 時）`run_config.toml`，最後 `rag.close()` 釋放資源（**不另存 `module_config.toml` 到向量庫路徑**；該另存行為僅 `run_rag_query` 於 rebuild 時執行）。
  4. 可選 `save_vector_store_to_runs=True`（CLI 旗標 `--run.save-vector-store-to-runs`）：把向量庫改存至本次 run 的 `results/vector_store/milvus.db`，避免覆寫 `data/rag/results/` 固定位置；`module_config.toml` 會記錄覆寫後路徑。

### 4. `run_rag_query()`

- 目的：以既有的 vector store / index 為基礎，重建必要資源並執行多輪 query 與評估。
- 流程：
  1. 建立 `RAG` 實例並載入 `RAGConfig`，以 `RAGBuilder` 進行編排。
  2. 呼叫 `RAGBuilder.build_reusable(rag, force_rebuild=...)`：依 `force_rebuild` 或 `vector_store_type="milvus"`（MilvusLite 不支援增量，每次需重建）決定「重建」整套 RAG 資源，或「載入」既有 index。
  3. 呼叫 `RAGBuilder.build_evaluators(rag)` 注入 Faithfulness / Relevancy evaluator，再針對預設 query 或指定 query 進行多輪查詢與評估。
  4. 回報 faithfulness / relevancy 評估結果，並將每次 query 結果落盤：
     - `results.json` — 結構化結果（`config` / `summary` / `results` 三層；`summary` 含各評估 pass count 與 pass rate）
     - `results/query_{index}.md` — 每次 query 與回覆各一份，含來源與評估
  5. 寫出 `module_config.toml`；若本次為重建（rebuild），另存一份到向量庫路徑（依 `vector_store_type` 決定）。

### 5. `run_agent_build()` / `run_agent_query()`

- 目的：以 LangGraph `create_agent` 包裝 `webpage_retriever` + `list_knowledge_bases` 工具，執行 Agent 問答（CLI 的 `agent-cli` 分支）。舊版 `run_agent()` 已移除；`run_agent_query()` 與 `run_app()` 為完整入口（各自建立 run context、agent、落盤與關閉），`run_agent_build()` 為 agent 建構 + 落盤的程式化 API（**兩者不經過它**）。
- `run_agent_build(config_name="default", run_config=None, **config_overrides) -> None`：
  1. 以 `create_run_no_site_context(module="agent_build", config_name=...)` 建立 `RunManager`（`runs/<ts>/agent_build/<config>/`），並以 `with run_workflow_context(...)` 包住 logging 生命週期。
  2. 載入 `AgentConfig.from_toml(config_name, **config_overrides)` 後呼叫 `create_agent(config_name, **config_overrides)`（內部建立 `Tool(config_name)`、LLM 與編譯圖；失敗時 `tool.close()` 後 re-raise）。
  3. 寫出 `module_config.toml`；`run_config` 非 None 時寫出 `run_config.toml`；最後 `agent.close()` 釋放資源。
- `run_agent_query(config_name="default", query=None, thread_id=None, stream=False, run_config=None, **config_overrides) -> None`：
  1. 以 `create_run_no_site_context(module="agent", config_name=..., base_folder="runs")` 建立 `RunManager` 與落盤路徑（`runs/<ts>/agent/<config>/`），並以 `save_logging_file` / `log_run_paths("init")` 起頭。
  2. 直接呼叫 `create_agent(config_name, **config_overrides)` 建立 `Agent`（**不經 `run_agent_build()`**），依 `stream` 選擇 `agent.astream_result()`（逐 token）或 `agent.ask()` 問答；`thread_id` 相同保留多輪記憶。
  3. `thread_id` 未提供時自動產生 `auto-{uuid}`（每次執行獨立）。
  4. 顯示回答與來源 URL，並以 `RunManager.save_agent_results_as_json(thread_id=..., results=[result], agent_config=agent.config)` 落盤 `results_{thread_id}.json`（讀取既有分檔 → 合併本輪 → 覆寫）且印出實際輸出路徑。
  5. 寫出 `module_config.toml`；`run_config` 非 None 時寫出 `run_config.toml`，最後 `log_run_paths("complete")`；例外路徑與 `finally` 皆呼叫 `agent.close()` 釋放 RAG 資源。

### 6. `run_app()`

- 目的：以 `ChatApp.create()` 建立 FastAPI app，並回傳 `(server, chat_app)`（`server` 為**非阻塞**的 `uvicorn.Server`；CLI 的 `server-cli` 分支與 `src/main.py` 皆使用）。
- 流程：
  1. `run_app(config_name="default", run_config=None, allowed_origins=None, host="127.0.0.1", port=8000, **config_overrides) -> tuple[uvicorn.Server, ChatApp]` 自行建立 run context（`RunManager`）並直接呼叫 `create_agent(config_name, **config_overrides)` 建立 agent（**不經 `run_agent_build()`**）。
  2. `ChatApp.create(agent=agent, run_manager=run_manager, allowed_origins=allowed_origins)` 組裝 app，再以 `uvicorn.Config(chat_app.app, host=..., port=...)` 建立 `uvicorn.Server`。
  3. `run_config` 非 None 時寫出 `run_config.toml`（路徑為 `run_manager.run_config_toml_path`），最後 `log_run_paths("complete")`。
  4. 建立 app / server 過程失敗時 `agent.close()` 後 re-raise（資源守衛）。
  5. 呼叫端負責 `server.run()` 阻塞與 `chat_app.close()`（`ChatApp.close()` 釋放 agent）。

## 四、Workflow 與 RunManager

`RunManager` 是 workflow 的輸出樞紐，透過兩個 classmethod 建立目錄結構：

- `RunManager.for_run(module=..., site_id=..., run_name=...)` — 3 層：`runs/<timestamp>/<module>/<site_id>/<run>/`（crawler / summarizer / rag_build / rag_query）。
- `RunManager.for_run_no_site(module=..., run_name=..., base_folder=...)` — 2 層：`runs/<timestamp>/<module>/<run>/`（agent；`base_folder` 可切換根目錄）。兩者皆會呼叫 `init_module_run_paths()` 建出下列路徑：

- `runs/<timestamp>/<module>/<site_id>/<run>/results.json`
- `runs/<timestamp>/<module>/<site_id>/<run>/results/`
- `runs/<timestamp>/<module>/<site_id>/<run>/module_config.toml`
- `runs/<timestamp>/<module>/<site_id>/<run>/run_config.toml`
- `runs/<timestamp>/<module>/<site_id>/<run>/terminal.log`

`DataManager` 則負責將 run 產物發布到 `data/` 持久化路徑（如 `data/webpages/<site_id>/`）。

> 註：`rag_query` 會在 `results/` 下額外產生每次 query 一份的 `query_{index}.md`；`rag_build` 開啟 `save_vector_store_to_runs` 時，向量庫寫入 `results/vector_store/`（而非 `data/rag/results/`）。
>
> 註：agent 對話結果由 `run_manager.save_agent_results_as_json()` 寫入 `results_{thread_id}.json`（讀取既有分檔 → 合併本輪 → 覆寫；未提供 `thread_id` 時自動 `auto-{uuid}`，CLI 與 server 行為一致）；agent 路徑無 `site_id` 層，也**不寫 `results.json`**。

Workflow 內部常見行為：

- `RunManager.for_run()` / `RunManager.for_run_no_site()`：建立本次 workflow 的 `RunManager`（取代已移除的 `set_module_path()` / `set_site_path()` / `set_run_path()` setter）。
- `run_manager.init_module_run_paths()`：初始化上述所有輸出路徑（由兩個 classmethod 內部呼叫）。
- `run_manager.log_run_paths("init" | "complete")`：以 Rich 表格顯示本次執行路徑。
- `run_manager.save_results_as_json(results, file_path=None)`：寫出 JSON 結果（crawler / summarizer 的爬取結果、`run_rag_query` 的 query 三層結構，或 agent 指定分檔）。
- `run_manager.save_agent_results_as_json(thread_id, results, agent_config)`：agent 對話結果落盤（呼叫端 `run_agent_query` / server `_event_stream` 傳入 `agent_config`）— 依 `thread_id` 寫出 `results_{thread_id}.json`（讀取既有分檔 → 合併本輪 → 覆寫；無既有分檔時以 `RunManager.find_thread_history_path()` 回掃歷史 run）。
- `run_manager.find_thread_history_path(base_folder, module_name, history_filename)`（staticmethod）：跨 timestamped run 目錄搜尋最新的 thread 歷史檔。
- 模組無關的持久化／發現函式位於 [src/app/workflow/run_persistence.py](src/app/workflow/run_persistence.py)：`save_results_as_md()`、`save_query_results_as_md()`、`load_latest_results()`、`load_latest_run_path()`（皆為無狀態函式，**非 RunManager 方法**）；image summarizer 未直接收到 `crawl_results` 時即呼叫 `load_latest_results()` 載入最近一次 crawler 輸出。

## 五、Workflow 與 Config 的互動

Workflow 不直接手寫 TOML，而是依賴各 module 的 config dataclass 與共用 helper：

1. `src/app/configs/*_config.py` 會從 `configs/<module>/<config_name>.toml` 載入設定。
2. `utils.config_helper.load_config_from_toml()` 與 `override_config()` 負責讀入、過濾與覆寫。
3. `save_module_config_as_toml()` 會把實際使用到的設定寫回 `module_config.toml`，方便追蹤本次執行。
4. `save_run_config_as_toml()` 由 workflow 函式在 `run_config` 非 None 時寫出 run-level 參數（`src/cli.py` 會傳入；`src/main.py` 目前不寫出）。

這表示 workflow 層的責任是「編排與執行」，而不是「定義設定格式」。設定格式與驗證應該維持在 `src/app/configs/`。

## 六、使用範例

```bash
# 依序執行爬蟲 → 圖片摘要 → RAG 建置，最後啟動 Chat 伺服器（阻塞至中斷）
python src/main.py --run.config-name nculab  # 省略時使用 default
```

```bash
# 只跑 workflow 層的 RAG 建置流程（通常透過 CLI 或程式入口呼叫）
python src/cli.py rag-build-cli --run.config-name default
```

```bash
# 執行 RAG 查詢流程並允許重建
python src/cli.py rag-query-cli --run.config-name test --run.force-rebuild
```

## 七、注意事項與建議

- 若要修改 workflow 的執行行為，優先檢查 [src/app/workflow/workflow.py](src/app/workflow/workflow.py) 與對應的 `src/app/configs/*_config.py`，不要把設定邏輯分散到 module 本體。
- 若要調整輸出目錄與 artifacts 命名，優先修改 [src/app/workflow/run_manager.py](src/app/workflow/run_manager.py)。
- 若要新增 workflow，建議先在 `src/app/workflow/workflow.py` 定義入口，再補上對應的 config dataclass 與 RunManager 輸出行為。

## 八、參考與證據

- [src/app/workflow/workflow.py](src/app/workflow/workflow.py)
- [src/app/workflow/workflow_helper.py](src/app/workflow/workflow_helper.py)
- [src/app/configs/workflow_config.py](src/app/configs/workflow_config.py)
- [src/app/workflow/run_manager.py](src/app/workflow/run_manager.py)
- [src/app/workflow/run_persistence.py](src/app/workflow/run_persistence.py)
- [src/app/workflow/data_manager.py](src/app/workflow/data_manager.py)
- [src/main.py](src/main.py)
- [src/app/engines/website_crawler.py](src/app/engines/website_crawler.py)
- [src/app/engines/webpage_image_summarizer.py](src/app/engines/webpage_image_summarizer.py)
- [src/app/engines/rag/rag.py](src/app/engines/rag/rag.py)
- [src/app/configs/website_crawler_config.py](src/app/configs/website_crawler_config.py)
- [src/app/configs/webpage_image_summarizer_config.py](src/app/configs/webpage_image_summarizer_config.py)
- [src/app/configs/rag_config.py](src/app/configs/rag_config.py)
- [src/utils/config_helper.py](src/utils/config_helper.py)