# Config

## 待辦事項

- [x] image_summarizer 的 litellm_kwargs 改為獨立的 section，並且保存到 module_config.toml
- [x] 調整 website_crawler 的參數型態和預設值 (max_depth 改成 None 代表不限制深度, exclude_words 改成 list)
- [x] 重構 config 架構
- [x] 保留建置 vector store 的 config 到 data/rag/results/（Milvus：`milvus.db`）
- [x] 設計 run config class
- [x] 提供 CLI 參數覆寫 config 功能
- [ ] 使用 yaml + pydantic 取代 toml + dataclass（pydantic 已完成，yaml 待辦）

## 一、config 架構

`src/website_copilot/pipelines/*.py`、`src/website_copilot/cli/` 與 [src/website_copilot/storage/run_manager.py](src/website_copilot/storage/run_manager.py) 共同負責執行路徑與檔案留存。

專案模組參數實際存放於 `configs/` 目錄下（例如 `configs/website_crawler/`、`configs/image_summarizer/`、`configs/rag/`、`configs/agent/`），每個模組由對應的 pydantic model 在 `src/website_copilot/config/` 中載入與驗證：

- `src/website_copilot/config/website_crawler_config.py`
- `src/website_copilot/config/image_summarizer_config.py`
- `src/website_copilot/config/rag_config.py`
- `src/website_copilot/config/agent_config.py`

模型結構：

- `ConfigModel`（`base_config.py`）：所有 config（含巢狀 section）的共用基底，設定 `strict=True`（不做型別轉換，如 `true` 不可放進 int 欄位、`"6"` 不可放進 int 欄位；int 可放進 float 欄位）、`extra="forbid"`（未知 key 直接報錯）、`validate_assignment=True`（建立後修改欄位也會重新驗證）。
- `BaseModuleConfig`：模組 config 的基底，提供 `from_toml()` 與 `run_name`；`config_name`、`run_name_fields` 由 loader 設為 `PrivateAttr`，不參與驗證與 `model_dump()`。
- 每個 TOML `[section]` 對應一個巢狀 `ConfigModel`（如 `RAGConfig.retriever` 為 `RetrieverConfig`），程式以 `config.retriever.similarity_top_k` 存取；`site_id` 等不屬於任何 section 的欄位寫在 TOML 最上層。
- 程式不給預設值，設定檔為唯一來源：缺少欄位即報錯；只有語意為「未設定」的可選欄位預設為 `None`（`max_depth`、`max_pages`、`seed`、`url_patterns`、`allowed_domains`、`path_prefix`、`webpages_data_folder_path`、`milvus_uri`、`hybrid_ranker_params`），`litellm_kwargs` 預設為空 dict。
- 單欄位約束以型別與 `Field` 表達（`PositiveInt`、`Literal`、`Field(ge=, le=)` 等）；非空字串使用 `NonEmptyStr`（只檢查不改寫，prompt 的前後換行原樣保留）。
- 跨欄位規則以 `model_validator` 實作：`nodes.chunk_overlap < nodes.chunk_size`；`hybrid_ranker_params` 有設定時，`WeightedRanker` 必須有 `weights`（長度 2）且不可有 `k`，`RRFRanker` 必須有 `k` 且不可有 `weights`。

載入流程（`BaseModuleConfig.from_toml(config_name, **overrides)`）：

1. 由 `config_name` 組出 `configs/<module>/<config_name>.toml`，以 `tomllib` 讀成 dict。
2. 扁平 overrides（如 `similarity_top_k=20`）依欄位名稱放入所屬 section；找不到欄位時報錯（過渡機制，CLI 改為巢狀參數後移除）。
3. `model_validate(dict)`；`ValidationError` 轉成 `ConfigValidationError`，訊息含設定檔路徑與欄位路徑，如 `configs/rag/test.toml: retriever.similarity_top_k: Input should be greater than 0`。
4. 設定 `config_name`，並以 `filter_commented_configs()` 解析 `# run name` 註解，記錄為 dotted path（如 `init.max_depth`）。

備註：`run_config.toml` 只在呼叫端傳入 `run_config` 時，由 pipeline 函式呼叫 `utils.config_helper.save_run_config_as_toml()` 寫出（`website-copilot run` 與 `serve` 會傳入，內容含 `save`／`publish`；此機制同為保持執行可追溯性）。

## 二、各模組怎麼載入與覆寫

以下為各模組在程式庫中的實際對應位置與載入流程摘要（已同步程式碼）：

### Website crawler

- Config model: `WebsiteCrawlerConfig`（`src/website_copilot/config/website_crawler_config.py`），設定檔 `configs/website_crawler/{config_name}.toml`。
- 最上層：`site_id`。
- `init`：`max_depth`（可省略，省略時不限制深度；注意 crawl4ai 的 `0` 代表只爬首頁）、`max_pages`（可省略，> 0）、`content_threshold`（0～1）、`light_mode`、`wait_for_images`。
- `crawl`：`url`、`url_patterns`（list，可省略）、`allowed_domains`（list，可省略）、`path_prefix`（可省略，需以 `/` 開頭）。
- `clean`：`llm_model`、`sample_ratio`（0 < x ≤ 1）、`repeat`、`max_prompt_tokens`、`seed`（可省略）。exclude_words 一律由 LLM 產生並經全站行覆蓋率驗證，不提供人工清單與開關。

### Image summarizer

- Config model: `ImageSummarizerConfig`（`src/website_copilot/config/image_summarizer_config.py`），設定檔 `configs/image_summarizer/{config_name}.toml`。
- 最上層：`site_id`。
- `init`：`download_timeout`（> 0）、`success_threshold`（0～1）、`max_retries`（≥ 0）、`cache_download_images`、`cache_image_captions`。
- `summarize`：`model`、`prompt`、`image_source`（`images` 或 `markdown`）、`vlm_max_workers`（> 0）。
- `litellm_kwargs`：任意 key，原樣傳給 litellm（可為空 table）。

### RAG

- Config model: `RAGConfig`（`src/website_copilot/config/rag_config.py`），設定檔 `configs/rag/{config_name}.toml`。
- 最上層：`site_id`、`webpages_data_folder_path`（可省略，預設 `data/webpages/{site_id}`）。
- `vector_store`：`vector_store_type`（僅 `"milvus"`）、`milvus_uri`（可省略，預設 `data/rag/{site_id}/milvus.db`）、`hybrid_ranker`（`"RRFRanker"` 或 `"WeightedRanker"`）、`hybrid_ranker_params`（可省略，如 `{ weights = [1.0, 0.5] }` 或 `{ k = 60 }`；省略時依 ranker 使用預設值）。
- `nodes`：`chunk_size`、`chunk_overlap`、`paragraph_separator`。
- `index`：`embedding_name`。
- `retriever`：`query_mode`（`"default"` 或 `"hybrid"`）、`similarity_top_k`、`hybrid_top_k`、`alpha`（0～1）。
- `query_engine`：`query_llm_name`、`evaluator_llm_name`、`cutoff`（0～1；hybrid 模式不使用）、`query`。

目前 `configs/rag/*.toml` 皆設定為 **Milvus hybrid search**（`query_mode="hybrid"`、`hybrid_ranker="WeightedRanker"`、`hybrid_ranker_params={weights=[1.0, 0.5]}`、`hybrid_top_k=10`）。

### Agent

- Config model: `AgentConfig`（`src/website_copilot/config/agent_config.py`），設定檔 `configs/agent/{config_name}.toml`（無 section）。
- 欄位：`llm_name`（與 RAG config 的 `query_llm_name` **解耦**）、`system_prompt`。
- 現行 `configs/agent/{default,test}.toml` 未標註 `# run name`，故 `run_name` 為 `default`。

## 三、共用 helper（`utils/config_helper.py`）

- `save_module_config_as_toml(config, toml_file_path)`：以 `config.model_dump()` 寫出 TOML，頂層欄位在前、每個巢狀 section 為一個 `[table]`，`None` 值略過（TOML 無 null）。
- `save_run_config_as_toml(config, toml_file_path)`：扁平化 run dataclass（只寫非 None 欄位）寫入 `run_config.toml`，由 pipeline 函式在收到 `run_config` 時呼叫。
- `filter_commented_configs(config_path, comment_keyword)`：解析 TOML 原始文字，找出註解含關鍵字（如 `run name`）的欄位，回傳 dotted path（如 `init.max_depth`；最上層欄位只有欄位名）。
- `log_config(title, config)`：以 Rich table 輸出 config，最上層欄位一張表、每個 section 一張表。
- 例外類別：`ConfigValidationError`（設定驗證失敗，含設定檔路徑）、`EnvironmentVariableError`。

`run_name` 由 run name 欄位組成，以最後一段欄位名命名（如 `max_depth-2`、`max_pages-40`）；值為 `None` 的欄位略過，沒有 run name 欄位時為 `default`。

## 四、留檔機制

目前的 RunManager 實作位於 `src/website_copilot/storage/run_manager.py`（類別 `RunManager`），其行為如下：

- 以 classmethod 建立目錄結構：
  - `RunManager.for_run(module=..., site_id=..., run_name=...)` → `runs/<timestamp>/<module>/<site_id>/<run>/`（3 層，crawler / summarizer / rag_build / rag_query）
  - `RunManager.for_run_no_site(module=..., run_name=..., base_folder="runs")` → `runs/<timestamp>/<module>/<run>/`（2 層，agent 專用，`base_folder` 可切換根目錄）
  - 兩者皆內部呼叫 `init_module_run_paths()` 建出下列路徑
- 會產生並管理以下檔案路徑：
  - `results.json`（爬取結果，或 `run_rag_query` 的 query 三層結構）
  - `results/`（Markdown 檔案；`rag_query` 另含每次 query 一份的 `query_{index}.md`，`rag_build` 旗標開啟時含 `vector_store/`）
  - `module_config.toml`
  - `run_config.toml`
  - `terminal.log`

module_config 與 run_config 的寫入機制：

- `utils/config_helper.save_module_config_as_toml(config, path)` 會以 `model_dump()` 把 config 分 section 寫出為 `module_config.toml`。
- `utils/config_helper.save_run_config_as_toml(run_config, path)` 會把 run dataclass 扁平化寫入 `run_config.toml`（只包含非 None 欄位）。由 workflow 函式在收到 `run_config`（非 None）時呼叫 `save_run_config_as_toml()` 寫出；`website-copilot run` 會傳入 run 參數（`website-copilot prepare` 目前不寫出）。

結果檔案與產出：

- `RunManager.save_results_as_json(results, file_path=None)` 會寫出 `results.json`（或指定分檔）。
- 模組無關的 Markdown／發現函式位於 `src/website_copilot/storage/run_persistence.py`（無狀態函式，非 RunManager 方法）：`save_results_as_md()` 把每頁結果寫入 `results/*.md`、`save_query_results_as_md()` 寫 `results/query_{index}.md`、`load_latest_results()` / `load_latest_run_path()` 供跨 run 探索。
- 目前主要 workflow 入口的行為：
  - `run_website_crawler()`：寫 `module_config.toml`、`results.json`、`results/*.md`
  - `run_image_summarizer()`：寫 `module_config.toml`、`results.json`、`results/*.md`
  - `run_rag_build()`：寫 `module_config.toml`（與 `run_config.toml`）；`save=True` 時向量庫建在本次 run 的 `results/milvus.db`；`save=False` 時建在暫存資料夾（結束即刪）；`publish=True` 時才原子替換到 `data/rag/<site_id>/milvus.db`（詳見 workflow.md）。
  - `run_rag_query()`：寫 `results.json`（query 三層結構）、`results/query_{index}.md`（每次 query 一份）與 `module_config.toml`；重建（rebuild）時另存一份 `module_config.toml` 到向量庫路徑。
  - `run_agent_query()`：經 `run_agent_build()` 建構 agent（`module_config.toml` 寫在 `agent_build/`）；本身只寫 `run_config.toml`，並呼叫 `RunManager.save_agent_results_as_json()` 寫 `results_{thread_id}.json`（讀取既有分檔 → 合併本輪 → 覆寫；`thread_id` 未提供時自動 `auto-{uuid}`）；對話結果位於 `runs/<ts>/agent/<config>/`（`RunManager.for_run_no_site()`，**無 `site_id` 層、不寫 `results.json`**）。
  - `run_agent_build()`：寫 `module_config.toml`（與 `run_config.toml`，若有傳入）至 `runs/<ts>/agent_build/<config>/`。
  - `run_server_build()`：只寫 `run_config.toml`（不寫 `module_config.toml`）；對話結果由 server 的 `_event_stream()` 以 `save_agent_results_as_json()` 落盤至 `runs/<ts>/server/<config>/results_{thread_id}.json`。
- module_config.toml
- run_config.toml
- terminal.log

### module_config.toml

save_module_config_as_toml() 以 `model_dump()` 輸出完整 config（含 RAG 推導出的 `webpages_data_folder_path`／`milvus_uri`），section 結構與 `configs/` 的設定檔相同，可再以對應的 config model 讀回驗證。

### run_config.toml

save_run_config_as_toml() 會把 run dataclass 扁平化成 TOML（只寫非 None 欄位）。

目前實際寫入時機：

- `website-copilot run <module>`（`cli/run.py`）：tyro 解析 CLI → 以 `run_config=command.run` 傳入對應 pipeline 函式 → 函式內在流程中呼叫 `save_run_config_as_toml(run_config, run_manager.run_config_toml_path)`
- `website-copilot prepare`：目前不傳入 `run_config`，因此不寫出 `run_config.toml`
- `website-copilot serve`：傳入 `ServeRunConfig`，由 `run_server_build()` 寫出 `run_config.toml`

因此：

- 走 `website-copilot run` 入口時，run_config.toml 會被寫出（由 pipeline 函式代為寫入）
- 直接呼叫 `src/website_copilot/pipelines/*.py` 內函式時，需在呼叫時傳入 `run_config` 才會寫出；`website-copilot prepare` 目前不寫出

### 結果檔案

- `RunManager.save_results_as_json(results, file_path=None)` 會寫出 results.json（或指定分檔）
- `run_persistence.save_results_as_md()` 會寫出 results/\*.md（無狀態函式）
- `run_persistence.save_query_results_as_md()` 會把每次 query 與回覆寫成 results/query_{index}.md（run_rag_query 專用）
- `RunManager.save_agent_results_as_json(thread_id, results, agent_config)` 會把 agent 對話結果寫入 results_{thread_id}.json（讀取既有分檔 → 合併本輪 → 覆寫；run_agent_query 與 server `_event_stream` 使用）

主要流程目前行為：

- run_website_crawler()：寫 module_config.toml、results.json、results/\*.md
- run_image_summarizer()：寫 module_config.toml、results.json、results/\*.md
- run_rag_build()：寫 module_config.toml（與 run_config.toml）；`save=True` 時向量庫建在本次 run 的 `results/milvus.db`；`save=False` 時建在暫存資料夾（結束即刪）；`publish=True` 時才原子替換到 `data/rag/<site_id>/milvus.db`（詳見 workflow.md）
- run_rag_query()：寫 results.json（query 三層結構）、`results/query_{index}.md`（每次 query 一份）與 module_config.toml；重建時另存一份到向量庫路徑
- run_agent_query()：寫 run_config.toml 與 `results_{thread_id}.json`（module_config.toml 由 run_agent_build 寫在 `agent_build/`）（`RunManager.save_agent_results_as_json()` 讀取既有分檔 → 合併本輪 → 覆寫；thread_id 未提供時自動 `auto-{uuid}`）；檔案位於 `runs/<ts>/agent/<config>/`
- run_agent_build()：寫 module_config.toml（與 run_config.toml）至 `runs/<ts>/agent_build/<config>/`
- run_server_build()：只寫 run_config.toml；對話結果由 server 的 `_event_stream()` 落盤至 `runs/<ts>/server/<config>/results_{thread_id}.json`

## 五、測試與實驗如何使用 config

倉庫中的測試與實驗（現況）：

- `tests/integration/test_module.py` 會透過程式 API 逐一呼叫各 run function（皆使用 `config_name="test"`）：
  - `run_website_crawler`、`run_image_summarizer`、`run_rag_build`
  - `run_agent_build`、`run_agent_query`

- `tests/integration/test_pipeline.py` 會執行 `run_prepare(config_name="test", publish=False)`（只存到 `runs/`，RAG 以 `runs/` 中本次的圖片摘要結果建庫，不寫入 `data/`），並以 `run_agent_build` + `run_server_build` 啟動後自動關閉 server。
- `website-copilot exp <name>`（實驗定義於 `pipelines/exp.py` 的 `EXPERIMENTS`）為手動實驗入口，方便針對不同 `config_name` 或模型版本做比較。

## 六、結論

簡短結論：

`configs/`（TOML）→ `src/website_copilot/config/*.py` 的 pydantic model 載入並驗證 → `src/website_copilot/storage/run_manager.py`（RunManager）負責寫出 module/run artifacts；`src/website_copilot/storage/data_manager.py`（DataManager）負責發布到 `data/` 持久化路徑。

重點：

- 四個主要模組（crawler、image_summarizer、rag、agent）使用一致的 config 載入與覆寫流程。
- `BaseModuleConfig`（`src/website_copilot/config/base_config.py`）為共用基底，不綁定 `site_id`；需要 `site_id` 的子類（如 `RAGConfig`、`WebsiteCrawlerConfig`）自行宣告欄位。
- 驗證以 pydantic 型別、`Field` 約束與 `model_validator` 表達，在建構與修改欄位時即捕捉錯誤。
- `pipeline_config.py`（`src/website_copilot/config/pipeline_config.py`）定義 RunConfig 與 ModuleConfig dataclass，供 CLI（tyro）與程式端共用。

## Evidence

- [src/website_copilot/utils/config_helper.py](src/website_copilot/utils/config_helper.py)
- [src/website_copilot/config/base_config.py](src/website_copilot/config/base_config.py)
- [src/website_copilot/config/pipeline_config.py](src/website_copilot/config/pipeline_config.py)
- [src/website_copilot/config/website_crawler_config.py](src/website_copilot/config/website_crawler_config.py)
- [src/website_copilot/config/image_summarizer_config.py](src/website_copilot/config/image_summarizer_config.py)
- [src/website_copilot/config/rag_config.py](src/website_copilot/config/rag_config.py)
- [src/website_copilot/config/agent_config.py](src/website_copilot/config/agent_config.py)
- [src/website_copilot/ingestion/crawling/website_crawler.py](src/website_copilot/ingestion/crawling/website_crawler.py)
- [src/website_copilot/cli/](src/website_copilot/cli/)
- [tests/integration/test_module.py](tests/integration/test_module.py)
- [tests/integration/test_pipeline.py](tests/integration/test_pipeline.py)
