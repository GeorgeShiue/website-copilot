# Config

## 待辦事項

- [x] image_summarizer 的 litellm_kwargs 改為獨立的 section，並且保存到 module_config.yml
- [x] 調整 website_crawler 的參數型態和預設值 (max_depth 改成 None 代表不限制深度, exclude_words 改成 list)
- [x] 重構 config 架構
- [x] 保留建置 vector store 的 config 到 data/vector_db/{site_id}.db/meta/
- [x] 設計 run config class
- [x] 提供 CLI 參數覆寫 config 功能
- [x] 使用 yaml + pydantic 取代 toml + dataclass

## 一、config 架構

`src/website_copilot/pipelines/*.py`、`src/website_copilot/cli/` 與 [src/website_copilot/storage/run_manager.py](src/website_copilot/storage/run_manager.py) 共同負責執行路徑與檔案留存。

專案模組參數實際存放於 `configs/` 目錄下（例如 `configs/website_crawler/`、`configs/image_summarizer/`、`configs/rag/`、`configs/agent/`），每個模組由對應的 pydantic model 在 `src/website_copilot/config/` 中載入與驗證：

- `src/website_copilot/config/website_crawler_config.py`
- `src/website_copilot/config/image_summarizer_config.py`
- `src/website_copilot/config/rag_config.py`
- `src/website_copilot/config/agent_config.py`
- `src/website_copilot/config/site_config.py`：`SiteConfig`（站點身分與爬取範圍，`configs/sites/{site_id}.yml`；不是模組 config）

共用模組：

- `src/website_copilot/config/base_config.py`：`ConfigModel`、`BaseModuleConfig`、`NonEmptyStr`。
- `src/website_copilot/config/yaml_helper.py`：讀取 YAML 並展開 `extends`（`load_config_dict`、`deep_merge`）。
- `src/website_copilot/config/prompts.py`：長字串預設值（圖片摘要 prompt、agent system prompt）。
- `src/website_copilot/config/overrides.py`：由 config class 自動產生 CLI 覆寫參數（見 cli.md）。

模型結構：

- `ConfigModel`（`base_config.py`）：所有 config（含巢狀 section）的共用基底，設定 `strict=True`（不做型別轉換，如 `true` 不可放進 int 欄位、`"6"` 不可放進 int 欄位；int 可放進 float 欄位）、`extra="forbid"`（未知 key 直接報錯）、`validate_assignment=True`（建立後修改欄位也會重新驗證）、`validate_default=True`（預設值也經過驗證，含跨欄位規則）。
- `BaseModuleConfig`：模組 config 的基底，提供 `from_yaml()` 與 `run_name`；`config_name`、`run_name_fields`、`source`（來源描述）由 loader 設為 `PrivateAttr`，不參與驗證與 `model_dump()`。`_DEFAULT_RUN_NAME_FIELDS`（ClassVar）為設定檔未寫 `run_name_fields` 時的 run name 欄位。
- 每個 YAML 巢狀 mapping（section）對應一個巢狀 `ConfigModel`（如 `RAGConfig.retriever` 為 `RetrieverConfig`），程式以 `config.retriever.similarity_top_k` 存取；`site_id` 等不屬於任何 section 的欄位寫在 YAML 最上層。
- **config class 的欄位預設值是唯一的預設值來源**（Phase C2）：設定檔只寫與預設值不同的部分，省略的欄位使用預設值；section 以 `default_factory` 建立，因此可直接 `RetrieverConfig()`、`RAGConfig(site_id=..., query_engine=QueryEngineConfig(query=...))` 建立 config，不需讀設定檔。長 prompt 在 `config/prompts.py`。
- **站點與模組參數分離**（Phase D）：模組 config 不含任何站點資訊。站點身分與爬取範圍在 `SiteConfig`（`configs/sites/{site_id}.yml`），pipeline 依 `run_config.site` 以 `SiteConfig.from_yaml(site)` 載入；RAG 的 collection 名稱、建庫來源與向量庫位置為執行期的 `RAGTarget`（由 `retrieval/factory.py` 的 `published_target()`／`build_target()` 依執行模式產生），不寫入 `module_config.yml`。

### SiteConfig

- `site_id`：須與檔名一致，格式 `^[A-Za-z_][A-Za-z0-9_]*$`（同時作為 `data/`、`runs/` 的資料夾名稱與 Milvus collection 名稱）。
- `sample_query`：`rag-query` 未指定 `--run.query` 時使用。
- `crawl`：`url`（必填）、`url_patterns`、`allowed_domains`（list，null 為不過濾）、`path_prefix`（需以 `/` 開頭，null 時取起始網址的父路徑）。
- `from_yaml(site_id)` 共用模組 config 的 YAML loader（支援 extends）；找不到站點時列出可用站點。每次執行另存 `site_config.yml`（runs/ 與 data/）。
- 單欄位約束以型別與 `Field` 表達（`PositiveInt`、`Literal`、`Field(ge=, le=)` 等）；非空字串使用 `NonEmptyStr`（只檢查不改寫，prompt 的前後換行原樣保留）。
- 跨欄位規則以 `model_validator` 實作：`nodes.chunk_overlap < nodes.chunk_size`；`hybrid_ranker_params` 有設定時，`WeightedRanker` 必須有 `weights`（長度 2）且不可有 `k`，`RRFRanker` 必須有 `k` 且不可有 `weights`。

載入流程（`BaseModuleConfig.from_yaml(config_name, overrides=None)`）：

1. 由 `config_name` 組出 `configs/<module>/<config_name>.yml`，以 `yaml.safe_load` 讀成 dict，逐層處理 `extends` 並以 deep merge 由父到子合併（`config/yaml_helper.py`）。`default.yml` 可省略：檔案不存在時視為空設定（等於 class 預設值）；其他名稱或 `extends: default` 找不到檔案時報錯。
2. 取出最上層保留 key `run_name_fields`（dotted path 的 list），檢查每個路徑都指向模型欄位；未寫時使用 class 的 `_DEFAULT_RUN_NAME_FIELDS`。
3. 巢狀 overrides（如 `{"retriever": {"similarity_top_k": 20}}`）以同一個 deep merge 疊在最上層（父檔 < 子檔 < overrides）。
4. `model_validate(dict)`（只驗證合併後的結果一次，未寫的欄位補上 class 預設值）；`ValidationError` 轉成 `ConfigValidationError`，訊息含設定檔路徑、繼承鏈與欄位路徑，如 `configs/rag/test.yml (extends: test_nculab → nculab → default): retriever.similarity_top_k: Input should be greater than 0`。
5. 設定 `config_name`、`run_name_fields` 與 `source`。

設定檔撰寫方式（`extends` 合併規則、`null` 清除、YAML 1.1 注意事項）見 [configs/README.md](../../../configs/README.md)。

備註：`run_config` 為所有 pipeline 函式的必填參數，`run_config.yml` 一律由 pipeline 函式呼叫 `utils.config_helper.save_run_config()` 寫出（內容含 `save`／`publish`）。

## 二、各模組怎麼載入與覆寫

以下為各模組的欄位摘要；預設值見各 config class，或 `uv run website-copilot run <module> --help` 的 `(default: ...)`：

### Website crawler

- Config model: `WebsiteCrawlerConfig`（`src/website_copilot/config/website_crawler_config.py`），設定檔 `configs/website_crawler/{config_name}.yml`。
- `init`：`max_depth`（null 為不限制深度；注意 crawl4ai 的 `0` 代表只爬首頁）、`max_pages`（null 為不限制，> 0）、`content_threshold`（0～1）、`light_mode`、`wait_for_images`。
- 爬取範圍（`url`、`url_patterns` 等）屬於站點資訊，見 `SiteConfig.crawl`。
- run name 預設為 `[init.max_depth]`。
- `clean`：`llm_model`、`sample_ratio`（0 < x ≤ 1）、`repeat`、`max_prompt_tokens`、`seed`（可省略）。exclude_words 一律由 LLM 產生並經全站行覆蓋率驗證，不提供人工清單與開關。

### Image summarizer

- Config model: `ImageSummarizerConfig`（`src/website_copilot/config/image_summarizer_config.py`），設定檔 `configs/image_summarizer/{config_name}.yml`。
- `init`：`download_timeout`（> 0）、`download_max_workers`（> 0，預設 40；同時下載圖片的執行緒數）、`success_threshold`（0～1）、`max_retries`（≥ 0）。
- `summarize`：`model`、`prompt`、`image_source`（`images` 或 `markdown`）、`summary_max_workers`（> 0，預設 50；同時呼叫 VLM 的請求數）。兩個並行上限皆為每頁各自計算（頁面依序處理）。
- `litellm_kwargs`：任意 key，原樣傳給 litellm（預設為空）。
- run name 預設為 `[summarize.model]`。
- 未傳入爬蟲結果時，只讀取 runs/ 中同站點最新的爬蟲結果（找不到時報錯，不退回其他站點）。

### RAG

- Config model: `RAGConfig`（`src/website_copilot/config/rag_config.py`），設定檔 `configs/rag/{config_name}.yml`。
- `vector_store`：`vector_store_type`（僅 `"milvus"`）、`hybrid_ranker`（`"RRFRanker"` 或 `"WeightedRanker"`）、`hybrid_ranker_params`（預設 `{weights: [1.0, 0.5]}`；改用 RRFRanker 時寫 `{k: 60}`；寫 `null` 時依 ranker 使用內建參數）。
- `nodes`：`chunk_size`、`chunk_overlap`、`paragraph_separator`。
- `index`：`embedding_name`。
- `retriever`：`query_mode`（`"default"` 或 `"hybrid"`）、`similarity_top_k`、`hybrid_top_k`、`alpha`（0～1）。
- `query_engine`：`query_llm_name`、`evaluator_llm_name`、`cutoff`（0～1；hybrid 模式不使用）。查詢問題在 `RAGQueryRunConfig.query`（`--run.query`），未指定時使用站點的 `sample_query`。
- 執行期目標 `RAGTarget(site_id, aug_webpages_dir, milvus_uri)`：
  - 資料來源：預設 `data/aug_webpages/{site_id}`；`--run.aug-webpages-data-use-latest-results` 時為 runs/ 中同站點最新的 image_summarizer 結果。
  - 向量庫：rag-build 依 save／publish 建在 run 的 `results/milvus.db`、`data/vector_db/.staging-*/{site_id}.db` 或系統暫存（publish 時連同 `meta/` 原子替換到 `data/vector_db/{site_id}.db`）；rag-query 與 serve 使用 `data/vector_db/{site_id}.db`（rag-query 可用 `--run.vector-store-run` 改查 runs/ 的向量庫）。Milvus collection 名稱固定為 `chunks`。

目前 class 預設值與 `configs/rag/test.yml` 皆為 **Milvus hybrid search**（`query_mode="hybrid"`、`hybrid_ranker="WeightedRanker"`、`hybrid_ranker_params={weights=[1.0, 0.5]}`、`hybrid_top_k=10`）。

### Agent

- Config model: `AgentConfig`（`src/website_copilot/config/agent_config.py`），設定檔 `configs/agent/{config_name}.yml`（無 section）。
- 欄位：`llm_name`（與 RAG config 的 `query_llm_name` **解耦**）、`system_prompt`。
- agent 為多站，不需要站點；`test.yml` 目前與預設值相同。`run_name` 為 `default`。

各模組都沒有 `default.yml`：`--run.config default`（預設）即 class 預設值。

## 三、共用 helper（`utils/config_helper.py`）

- `save_module_config(config, file_path)`：以 `config.model_dump()` 寫出完整 config（extends 展開並補上 class 預設值，不含 `extends`），檔頭註解記錄來源與 run name 欄位，如：
  ```yaml
  # source: configs/rag/test.yml
  # run_name_fields: [vector_store.vector_store_type]
  ```
- `save_run_config(config, file_path)`：將 run dataclass 的所有欄位寫入 `run_config.yml`，由 pipeline 函式在收到 `run_config` 時呼叫。
- `save_site_config(site, file_path)`：將站點設定寫入 `site_config.yml`（檔頭記錄來源）。
- `dump_yaml(data, path, header)`：兩者共用的自訂 dumper，多行字串為 `|` block scalar、`allow_unicode=True`、`sort_keys=False`（保持模型欄位順序）、`None` 輸出為 `null`。
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
  - `module_config.yml`
  - `run_config.yml`
  - `terminal.log`

module_config 與 run_config 的寫入機制：

- `utils/config_helper.save_module_config(config, path)` 會以 `model_dump()` 把 config 分 section 寫出為 `module_config.yml`。
- `utils/config_helper.save_run_config(run_config, path)` 會把 run dataclass 的所有欄位寫入 `run_config.yml`（`None` 為 `null`）。由 workflow 函式呼叫 `save_run_config()` 寫出；`website-copilot run` 會傳入 run 參數（`website-copilot prepare` 目前不寫出）。

結果檔案與產出：

- `RunManager.save_results_as_json(results, file_path=None)` 會寫出 `results.json`（或指定分檔）。
- 模組無關的 Markdown／發現函式位於 `src/website_copilot/storage/run_persistence.py`（無狀態函式，非 RunManager 方法）：`save_results_as_md()` 把每頁結果寫入 `results/*.md`、`save_query_results_as_md()` 寫 `results/query_{index}.md`、`load_latest_results()` / `load_latest_run_path()` 供跨 run 探索。
- 目前主要 workflow 入口的行為：
  - `run_website_crawler()`：寫 `module_config.yml`、`results.json`、`results/*.md`
  - `run_image_summarizer()`：寫 `module_config.yml`、`results.json`、`results/*.md`
  - `run_rag_build()`：寫 `module_config.yml`（與 `run_config.yml`）；`save=True` 時向量庫建在本次 run 的 `results/milvus.db`；`save=False` 時建在暫存資料夾（結束即刪）；`publish=True` 時才原子替換到 `data/vector_db/<site_id>.db`（詳見 workflow.md）。
  - `run_rag_query()`：寫 `results.json`（query 三層結構）、`results/query_{index}.md`（每次 query 一份）與 `module_config.yml`；重建（rebuild）時另存一份 `module_config.yml` 到向量庫路徑。
  - `run_agent_query()`：經 `run_agent_build()` 建構 agent（`module_config.yml` 寫在 `agent_build/`）；本身只寫 `run_config.yml`，並呼叫 `RunManager.save_agent_results_as_json()` 寫 `results_{thread_id}.json`（讀取既有分檔 → 合併本輪 → 覆寫；`thread_id` 未提供時自動 `auto-{uuid}`）；對話結果位於 `runs/<ts>/agent/<config>/`（`RunManager.for_run_no_site()`，**無 `site_id` 層、不寫 `results.json`**）。
  - `run_agent_build()`：寫 `module_config.yml` 與 `run_config.yml` 至 `runs/<ts>/agent_build/<config>/`。
  - `run_server_build()`：只寫 `run_config.yml`（不寫 `module_config.yml`）；對話結果由 server 的 `_event_stream()` 以 `save_agent_results_as_json()` 落盤至 `runs/<ts>/server/<config>/results_{thread_id}.json`。
- module_config.yml
- run_config.yml
- terminal.log

### module_config.yml

save_module_config() 以 `model_dump()` 輸出完整 config（不含站點與向量庫位置等執行期資訊，這些記錄在 `site_config.yml` 與 log），section 結構與 `configs/` 的設定檔相同，可再以對應的 config model 讀回驗證。

### run_config.yml

save_run_config() 會把 run dataclass 的所有欄位寫成 YAML（`None` 為 `null`）。

寫入時機：`run_config` 為所有 pipeline 函式的必填參數，因此所有入口都會寫出 `run_config.yml`：

- `website-copilot run <module>`（`cli/run.py`）：tyro 解析 CLI → `run_xxx(command.run, overrides)` → 函式內呼叫 `save_run_config(run_config, run_manager.run_config_path)`（publish 時另寫到 `data/`）。
- `website-copilot prepare`：`run_prepare` 以同一個站點與 config 名稱建立各階段的 RunConfig，各階段各自寫出（publish 時寫到 `data/{category}/{site_id}/run_config.yml`）。
- `website-copilot serve`：同一個 `ServeRunConfig` 由 `run_agent_build()` 與 `run_server_build()` 各自寫出。

### 結果檔案

- `RunManager.save_results_as_json(results, file_path=None)` 會寫出 results.json（或指定分檔）
- `run_persistence.save_results_as_md()` 會寫出 results/\*.md（無狀態函式）
- `run_persistence.save_query_results_as_md()` 會把每次 query 與回覆寫成 results/query_{index}.md（run_rag_query 專用）
- `RunManager.save_agent_results_as_json(thread_id, results, agent_config)` 會把 agent 對話結果寫入 results_{thread_id}.json（讀取既有分檔 → 合併本輪 → 覆寫；run_agent_query 與 server `_event_stream` 使用）

主要流程目前行為：

- run_website_crawler()：寫 module_config.yml、results.json、results/\*.md
- run_image_summarizer()：寫 module_config.yml、results.json、results/\*.md
- run_rag_build()：寫 module_config.yml（與 run_config.yml）；`save=True` 時向量庫建在本次 run 的 `results/milvus.db`；`save=False` 時建在暫存資料夾（結束即刪）；`publish=True` 時才原子替換到 `data/vector_db/<site_id>.db`（詳見 workflow.md）
- run_rag_query()：寫 results.json（query 三層結構）、`results/query_{index}.md`（每次 query 一份）與 module_config.yml；重建時另存一份到向量庫路徑
- run_agent_query()：寫 run_config.yml 與 `results_{thread_id}.json`（module_config.yml 由 run_agent_build 寫在 `agent_build/`）（`RunManager.save_agent_results_as_json()` 讀取既有分檔 → 合併本輪 → 覆寫；thread_id 未提供時自動 `auto-{uuid}`）；檔案位於 `runs/<ts>/agent/<config>/`
- run_agent_build()：寫 module_config.yml（與 run_config.yml）至 `runs/<ts>/agent_build/<config>/`
- run_server_build()：只寫 run_config.yml；對話結果由 server 的 `_event_stream()` 落盤至 `runs/<ts>/server/<config>/results_{thread_id}.json`

## 五、測試與實驗如何使用 config

倉庫中的測試與實驗（現況）：

- `tests/integration/test_module.py` 會透過程式 API 逐一呼叫各 run function（皆以 `config_name="test"` 的 RunConfig 呼叫）：
  - `run_website_crawler`、`run_image_summarizer`、`run_rag_build`
  - `run_agent_build`、`run_agent_query`

- `tests/integration/test_pipeline.py` 會執行 `run_prepare(PrepareRunConfig(config_name="test", publish=False))`（只存到 `runs/`，RAG 以 `runs/` 中本次的圖片摘要結果建庫，不寫入 `data/`），並以 `run_agent_build` + `run_server_build` 啟動後自動關閉 server。

## 六、結論

簡短結論：

`configs/`（YAML，含 extends）→ `src/website_copilot/config/*.py` 的 pydantic model 載入並驗證 → `src/website_copilot/storage/run_manager.py`（RunManager）負責寫出 module/run artifacts；`src/website_copilot/storage/data_manager.py`（DataManager）負責發布到 `data/` 持久化路徑。

重點：

- 四個主要模組（crawler、image_summarizer、rag、agent）使用一致的 config 載入與覆寫流程。
- `BaseModuleConfig`（`src/website_copilot/config/base_config.py`）為模組 config 的共用基底；模組 config 不含站點資訊，站點由 `SiteConfig` 提供。
- 驗證以 pydantic 型別、`Field` 約束與 `model_validator` 表達，在建構與修改欄位時即捕捉錯誤。
- `pipeline_config.py`（`src/website_copilot/config/pipeline_config.py`）定義 RunConfig dataclass，供 CLI（tyro）與程式端共用；CLI 的 `--module.*` 覆寫參數由 `config/overrides.py` 從 module config 自動產生。

## Evidence

- [src/website_copilot/utils/config_helper.py](src/website_copilot/utils/config_helper.py)
- [src/website_copilot/config/base_config.py](src/website_copilot/config/base_config.py)
- [src/website_copilot/config/yaml_helper.py](src/website_copilot/config/yaml_helper.py)
- [src/website_copilot/config/pipeline_config.py](src/website_copilot/config/pipeline_config.py)
- [src/website_copilot/config/website_crawler_config.py](src/website_copilot/config/website_crawler_config.py)
- [src/website_copilot/config/image_summarizer_config.py](src/website_copilot/config/image_summarizer_config.py)
- [src/website_copilot/config/rag_config.py](src/website_copilot/config/rag_config.py)
- [src/website_copilot/config/agent_config.py](src/website_copilot/config/agent_config.py)
- [src/website_copilot/ingestion/crawling/website_crawler.py](src/website_copilot/ingestion/crawling/website_crawler.py)
- [src/website_copilot/cli/](src/website_copilot/cli/)
- [tests/integration/test_module.py](tests/integration/test_module.py)
- [tests/integration/test_pipeline.py](tests/integration/test_pipeline.py)
