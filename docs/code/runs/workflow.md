# Workflow

## 一、主要檔案與角色

- [app/workflow/workflow.py](app/workflow/workflow.py)：定義四個主要 workflow 入口，負責把 config、module 與 RunManager 串起來，並執行實際的爬蟲、圖片摘要與 RAG 建置／查詢流程。
- [app/workflow/workflow_config.py](app/workflow/workflow_config.py)：定義 workflow 層的 run dataclass，提供 CLI 與程式端共用的參數結構。
- [app/workflow/workflow_manager.py](app/workflow/workflow_manager.py)：管理 `runs/<timestamp>/<module>/<run>/` 路徑，負責 results、module_config、run_config 與 log 的輸出位置。
- [main.py](main.py)：示範以程式直呼 workflow 的串接入口，依序執行**網站爬蟲** → **圖片摘要** → **RAG 建置**三個階段。
- `app/tools/webpage_retriever.py`：將 RAG retriever 包裝為 LangChain `StructuredTool`，供下游 Agent 動態呼叫檢索。
- [app/modules/website_crawler.py](app/modules/website_crawler.py)：實際執行網站爬取、Markdown 清理與資料整理的模組。
- [app/modules/webpage_image_summarizer.py](app/modules/webpage_image_summarizer.py)：實際執行圖片下載、VLM 摘要、快取與 Markdown 增強的模組。
- [app/modules/rag.py](app/modules/rag.py)：執行查詢、檢索、評估與資源釋放的 runtime 模組。
- [app/modules/rag_factory.py](app/modules/rag_factory.py)：負責 RAG 建構流程（`RAGBuilder` / `NodePipelineBuilder` / `VectorStoreBuilder`）。
- [app/configs/website_crawler_config.py](app/configs/website_crawler_config.py)、[app/configs/webpage_image_summarizer_config.py](app/configs/webpage_image_summarizer_config.py)、[app/configs/rag_config.py](app/configs/rag_config.py)：各模組對應的設定 dataclass，負責從 `configs/` 載入與驗證。
- [utils/config_helper.py](utils/config_helper.py)：共用設定工具，提供 TOML 載入、覆寫、寫回與 config 顯示等功能。

## 二、Workflow 解析與執行流程

1. workflow 的核心實作集中在 [app/workflow/workflow.py](app/workflow/workflow.py)，目前提供四個主要入口：
   - `run_website_crawler()`
   - `run_webpage_image_summarizer()`
   - `run_rag_build()`
   - `run_rag_query()`
2. 這些函式都會先建立對應的 module 物件，再從對應的 config dataclass 讀取 TOML 設定，最後將設定套用到 module 的 init 與執行參數。
3. 每個 workflow 都會建立或接收 [app/workflow/workflow_manager.py](app/workflow/workflow_manager.py) 的 `RunManager`，用來決定本次執行的輸出目錄。
4. Workflow 會透過 `utils.config_helper.save_module_config_as_toml()` 寫出 `module_config.toml`，並由 `RunManager` 保存 `results.json`、`results/*.md` 與 `terminal.log`。
5. 若流程是透過 CLI 進入，`cli.py` 會在執行完畢後額外寫出 `run_config.toml`；若直接呼叫 workflow 函式，通常只會產生 module-level artifacts。

## 三、四條主要 Workflow

### 1. `run_website_crawler()`

- 目的：從指定網站爬取頁面、清理 Markdown，並產出可供後續流程使用的 crawl results。
- 流程：
  1. 建立 [app/modules/website_crawler.py](app/modules/website_crawler.py) 的 `WebsiteCrawler`。
  2. 透過 [app/configs/website_crawler_config.py](app/configs/website_crawler_config.py) 從 `configs/website_crawler/{config_name}.toml` 讀入設定。
  3. 套用 `override_init_config()` 與 `crawl_website()` 的執行參數。
  4. 若爬取成功，寫出 `module_config.toml`、`results.json` 與 `results/*.md`。

### 2. `run_webpage_image_summarizer()`

- 目的：將 crawl results 中的圖片交給 VLM 做摘要，並輸出增強後的 Markdown。
- 流程：
  1. 建立 [app/modules/webpage_image_summarizer.py](app/modules/webpage_image_summarizer.py) 的 `WebpageImageSummarizer`。
  2. 透過 [app/configs/webpage_image_summarizer_config.py](app/configs/webpage_image_summarizer_config.py) 載入 `configs/webpage_image_summarizer/{config_name}.toml`。
  3. 若未直接傳入 `crawl_results`，則由 [app/workflow/workflow_manager.py](app/workflow/workflow_manager.py) 自動載入最近一次 crawler 結果。
  4. 執行圖片摘要後，寫出 `module_config.toml`、`results.json` 與 `results/*.md`。

### 3. `run_rag_build()`

- 目的：建立 RAG 所需的 nodes、vector store、index、retriever 與 query engine，並立即執行範例查詢。
- 流程：
  1. 透過 [app/configs/rag_config.py](app/configs/rag_config.py) 載入 `configs/rag/{config_name}.toml`。
  2. 使用 `RAGBuilder(config).build()` 一鍵建構完整 RAG 管線：`build_nodes()` → `build_vector_store()`（支援 **Qdrant BM25** 或 **Milvus BGE-M3**，可選 `WeightedRanker` / `RRFRanker`）→ `build_index()` → `build_retriever()`（支援 `query_mode="hybrid"` 與 `filter_dict`）→ `build_query_engine()`。
  3. 執行範例 query，最後寫出 `module_config.toml`，並把部分設定另存到向量庫路徑（依 `vector_store_type` 決定存至 `qdrant_db_folder_path/` 或 `milvus_uri/`）。
  4. 可選 `save_vector_store_to_runs=True`（CLI 旗標 `--run.save-vector-store-to-runs`）：把向量庫改存至本次 run 的 `results/vector_store/{qdrant_db | milvus.db}`，避免覆寫 `data/rag/results/` 固定位置；`module_config.toml` 會記錄覆寫後路徑。

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

## 四、Workflow 與 RunManager

`RunManager` 是 workflow 的輸出樞紐，負責建立與管理每次執行的目錄結構：

- `runs/<timestamp>/<module>/<run>/results.json`
- `runs/<timestamp>/<module>/<run>/results/`
- `runs/<timestamp>/<module>/<run>/module_config.toml`
- `runs/<timestamp>/<module>/<run>/run_config.toml`
- `runs/<timestamp>/<module>/<run>/terminal.log`

> 註：`rag_query` 會在 `results/` 下額外產生每次 query 一份的 `query_{index}.md`；`rag_build` 開啟 `save_vector_store_to_runs` 時，向量庫寫入 `results/vector_store/`（而非 `data/rag/results/`）。

Workflow 內部常見行為：

- `run_manager.set_module_path(<module>)`：決定本次 workflow 的模組子目錄。
- `run_manager.set_run_path(<run_name>)`：決定本次執行的 run 名稱。
- `run_manager.init_module_run_paths()`：初始化上述所有輸出路徑。
- `run_manager.save_results_as_json()`：寫出 JSON 結果（crawler / summarizer 的爬取結果，或 `run_rag_query` 的 query 三層結構）。
- `run_manager.save_results_as_md()`：寫出 Markdown 結果（每頁一份 `results/*.md`）。
- `run_manager.save_query_results_as_md()`：`run_rag_query` 專用，每次 query 與回覆各寫一份 `results/query_{index}.md`。
- `run_manager.load_latest_results_from_json()`：當 image summarizer 沒有直接收到 crawl_results 時，會自動載入最近一次 crawler 的輸出。

## 五、Workflow 與 Config 的互動

Workflow 不直接手寫 TOML，而是依賴各 module 的 config dataclass 與共用 helper：

1. `app/configs/*_config.py` 會從 `configs/<module>/<config_name>.toml` 載入設定。
2. `utils.config_helper.load_config_from_toml()` 與 `override_config()` 負責讀入、過濾與覆寫。
3. `save_module_config_as_toml()` 會把實際使用到的設定寫回 `module_config.toml`，方便追蹤本次執行。
4. `save_run_config_as_toml()` 則由 CLI 入口寫出 run-level 參數；直接呼叫 workflow 函式時不一定會產生。

這表示 workflow 層的責任是「編排與執行」，而不是「定義設定格式」。設定格式與驗證應該維持在 `app/configs/`。

## 六、使用範例

```bash
# 先爬取，再做圖片摘要
python main.py
```

```bash
# 只跑 workflow 層的 RAG 建置流程（通常透過 CLI 或程式入口呼叫）
python cli.py rag-build-cli --run.config-name default
```

```bash
# 執行 RAG 查詢流程並允許重建
python cli.py rag-query-cli --run.config-name test --run.force-rebuild
```

## 七、注意事項與建議

- 若要修改 workflow 的執行行為，優先檢查 [app/workflow/workflow.py](app/workflow/workflow.py) 與對應的 `app/configs/*_config.py`，不要把設定邏輯分散到 module 本體。
- 若要調整輸出目錄與 artifacts 命名，優先修改 [app/workflow/workflow_manager.py](app/workflow/workflow_manager.py)。
- 若要新增 workflow，建議先在 `app/workflow/workflow.py` 定義入口，再補上對應的 config dataclass 與 RunManager 輸出行為。

## 八、參考與證據

- [app/workflow/workflow.py](app/workflow/workflow.py)
- [app/workflow/workflow_config.py](app/workflow/workflow_config.py)
- [app/workflow/workflow_manager.py](app/workflow/workflow_manager.py)
- [main.py](main.py)
- [app/modules/website_crawler.py](app/modules/website_crawler.py)
- [app/modules/webpage_image_summarizer.py](app/modules/webpage_image_summarizer.py)
- [app/modules/rag.py](app/modules/rag.py)
- [app/configs/website_crawler_config.py](app/configs/website_crawler_config.py)
- [app/configs/webpage_image_summarizer_config.py](app/configs/webpage_image_summarizer_config.py)
- [app/configs/rag_config.py](app/configs/rag_config.py)
- [utils/config_helper.py](utils/config_helper.py)