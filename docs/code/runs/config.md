# Config

## 待辦事項

- [x] webpage_image_summarizer 的 litellm_kwargs 改為獨立的 section，並且保存到 module_config.toml
- [x] 調整 website_crawler 的參數型態和預設值 (max_depth 改成 None 代表不限制深度, exclude_words 改成 list)
- [x] 重構 config 架構
- [x] 保留建置 vector store 的 config 到 data/rag/results/（Milvus：`milvus.db`）
- [x] 設計 run config class
- [x] 提供 CLI 參數覆寫 config 功能
- [ ] 使用 yaml + pydantic 取代 toml + dataclass

## 一、config 架構

[src/app/workflow/workflow.py](src/app/workflow/workflow.py)、[src/cli.py](src/cli.py) 與 [src/app/workflow/run_manager.py](src/app/workflow/run_manager.py) 共同負責執行路徑與檔案留存。

專案模組參數實際存放於 `configs/` 目錄下（例如 `configs/website_crawler/`、`configs/webpage_image_summarizer/`、`configs/rag/`、`configs/agent/`），每個模組由對應的 dataclass 在 `src/app/configs/` 中載入與驗證。根據目前程式碼庫，四個主要 config 類分別位於：

- `src/app/configs/website_crawler_config.py`
- `src/app/configs/webpage_image_summarizer_config.py`
- `src/app/configs/rag_config.py`
- `src/app/configs/agent_config.py`

四個 config class 的載入流程一致：

1. 由 `config_name` 組出 TOML 檔路徑（例如 `configs/<module>/<config_name>.toml`）
2. 透過 `sections_to_keys` 定義允許的欄位，逐 section 載入 TOML
3. 使用共用 helper（`src/utils/config_helper.py`）做欄位過濾、覆寫與合併
4. 建構 dataclass 並在 `__post_init__` 或模組內呼叫 `_validate_config()` 進行型別與範圍驗證

備註：`run_config.toml` 不會由 workflow 函式自動產生，而是由呼叫端（`src/cli.py` 與 `src/main.py`）在流程結束時呼叫 `utils.config_helper.save_run_config_as_toml()` 寫出（此機制同為保持執行可追溯性）。

## 二、各模組怎麼載入與覆寫

以下為各模組在程式庫中的實際對應位置與載入流程摘要（已同步程式碼）：

### Website crawler

- Config dataclass: `src/app/configs/website_crawler_config.py`
- TOML 範例與實作：`configs/website_crawler/{config_name}.toml`（例如 `configs/website_crawler/default.toml`）
- 載入流程：
  1. `WebsiteCrawlerConfig.from_toml(config_name, **overrides)` 會依 `DEFAULT_CONFIG_FOLDER_PATH` 組出 `configs/website_crawler/{config_name}.toml`。
  2. 呼叫 `utils.config_helper.load_config_from_toml()` 逐 section 讀入且過濾非允許欄位。
  3. 呼叫 `utils.config_helper.override_config()` 套用 CLI 或程式層級的 overrides（會根據 `sections_to_keys` 過濾）。
  4. 建構 `WebsiteCrawlerConfig` 並在 `__post_init__()` 呼叫 `_validate_config()` 做完整驗證。

欄位說明與驗證重點：

- `init`：`max_depth`、`max_pages`、`content_threshold`、`light_mode`、`wait_for_images`（`max_depth` 為 `None` 時不限制深度，驗證為 int 或 None 且不可小於 0；注意 crawl4ai 的 `max_depth=0` 語意為只爬首頁，因此「不限制」必須省略該參數）。
- `crawl`：`url`、`url_patterns`、`allowed_domains`、`path_prefix`。
- `clean`：`llm_model`、`sample_ratio`、`repeat`、`max_prompt_tokens`、`seed`。exclude_words 一律由 LLM 產生並經全站行覆蓋率驗證，不再提供人工清單與開關。\*\*
  \*\*

### Webpage image summarizer

- Config dataclass: `src/app/configs/webpage_image_summarizer_config.py`
- TOML 範例與實作：`configs/webpage_image_summarizer/{config_name}.toml`
- 載入流程與注意：
  1. `WebpageImageSummarizerConfig.from_toml(config_name, **overrides)` 會載入 `configs/webpage_image_summarizer/{config_name}.toml`，並套用 `sections_to_keys` 規則。
  2. `litellm_kwargs` 被設為 residual section（allowed keys 空集合），因此在覆寫時允許任意延伸鍵值並會保留在 config 物件中。
  3. 建構後執行 `_validate_config()` 做型別檢查（例如 `download_timeout > 0`，`vlm_max_workers > 0`，`image_source` 僅允許 `images` 或 `markdown`）。

### RAG

- Config dataclass: `src/app/configs/rag_config.py`
- TOML 範例與實作：`configs/rag/{config_name}.toml`
- 載入流程：
  1. `RAGConfig.from_toml(config_name, **overrides)` 會載入 `configs/rag/{config_name}.toml`。
  2. `utils.config_helper.load_config_from_toml()` 與 `override_config()` 處理合併與覆寫。
  3. 建構 `RAGConfig` 後執行 `_validate_config()`（驗證 `site_id`、`milvus_uri`、`vector_store_type`、`chunk_size`、`similarity_top_k`、`cutoff`、`hybrid_ranker`、`hybrid_ranker_params` 等）。

欄位摘要：

- `init`：`site_id`（必須為非空字串）、`webpages_data_folder_path`（預設 `data/webpages/{site_id}`）。
- `vector_store`：`vector_store_type`（預設 `"milvus"`）、`milvus_uri`（預設 `data/rag/{site_id}/milvus.db`）、`hybrid_ranker`（`"RRFRanker"` 或 `"WeightedRanker"`，預設 `"WeightedRanker"`）、`hybrid_ranker_params`（dict，例如 `{"weights": [1.0, 0.5]}`）。
- `nodes`：`chunk_size`、`chunk_overlap`、`paragraph_separator`。
- `retriever`：`similarity_top_k`（預設 `10`）、`query_mode`（`"default"` 或 `"hybrid"`）、`hybrid_top_k`（預設 `10`）、`alpha`（預設 `0.5`）。
- `query_engine`：`query_llm_name`（預設 `gpt-5.6-luna`）、`evaluator_llm_name`（預設 `gpt-5.6-terra`）、`cutoff`（預設 `0.0`；hybrid 模式跳過 cutoff）、`query`。
- `query_engine.query` 讓不同實驗可以直接在 config TOML 中切換查詢問題，並由 workflow 讀取後執行。

目前 `configs/rag/default.toml` 與 `configs/rag/test.toml` 皆設定為 **Milvus hybrid search**（`vector_store_type="milvus"`、`query_mode="hybrid"`、`hybrid_ranker="WeightedRanker"`、`hybrid_ranker_params={weights=[1.0, 0.5]}`、`hybrid_top_k=10`）；`milvus.toml` 保留相同設定的對照檔。Dense 模式的 `cutoff`（如 `0.4`）在 hybrid 模式下不啟用，由融合分數自然排序。

### Agent

- Config dataclass: `src/app/configs/agent_config.py`
- TOML 範例與實作：`configs/agent/{config_name}.toml`（`default` / `test`，08/09 M1 新增）
- 載入流程（與其他模組同一共用機制）：
  1. `AgentConfig.from_toml(config_name, **overrides)` 依 `DEFAULT_CONFIG_FOLDER_PATH` 組出 `configs/agent/{config_name}.toml`，以 `SECTIONS_TO_KEYS = {"agent": {"llm_name", "system_prompt"}}` 載入。
  2. `utils.config_helper.load_config_from_toml()` 與 `override_config()` 處理合併與覆寫。
  3. 建構 `AgentConfig` 後執行 `_validate_config()`（`llm_name` / `system_prompt` 型別與非空驗證）。

欄位摘要：

- `agent`：`llm_name`（預設 `gpt-5.6-luna`，與 RAG config 的 `query_llm_name` **解耦**，Agent 可獨立更換不影響檢索）、`system_prompt`（要求先使用 `webpage_retriever` 工具檢索再回答、回答列出參考來源 URL）。
- `run_name` property：依 TOML 中 `# run name` 註解的欄位生成（如 `llm_name-<model>`）；現行 `configs/agent/{default,test}.toml` 未標註該註解，故 `run_name` 回傳 `default`。

## 三、共用載入、覆寫與驗證機制

[src/utils/config_helper.py](src/utils/config_helper.py) 是專案的設定工具中心，`src/app/configs/*` 的 dataclass 與 `src/app/workflow/*` 的流程都會透過它來載入、覆寫、驗證與寫回設定檔。以下依實作（參考 `src/utils/config_helper.py`）說明主要責任與行為：

- load_config_section_from_toml(config_path, config_section, allowed_keys)
  - 讀取指定 TOML 檔案的 section，要求該 section 為 table（Mapping）。
  - 會以 allowed_keys 篩選欄位；若 allowed_keys 為空集合，代表允許所有鍵（常用於 residual section，例如 `litellm_kwargs`）。
  - 可能拋出 FileNotFoundError / ConfigNotFoundError / ConfigInvalidTypeError（見程式實作）。

- load_config_from_toml(config_path, sections_to_keys)
  - 以 sections_to_keys（section -> allowed keys）為藍圖，逐一呼叫上面的函式並合併成單一 dict，供各 module 的 `from_toml()` 使用。

- override_config(config, overrides, sections_to_keys)
  - 依 sections_to_keys 計算允許的欄位集合，過濾 `overrides`（例如 CLI 傳入的覆寫），然後合併到原始 config。未知 key 會被忽略並記 warning。

- save_module_config_as_toml(config, toml_file_path)
  - 將 config 物件依 sections_to_keys 分 section 寫回 TOML；每個 section 只寫出在 sections_to_keys 定義的欄位。
  - 若某 section 的 allowed keys 為空（residual section），函式會把剩餘未消耗的鍵寫入該 section；注意：不支援多個 residual section（會拋出 ValueError）。

- save_run_config_as_toml(config, toml_file_path)
  - 扁平化 run dataclass（只寫非 None 欄位）並寫入 run_config.toml，通常由呼叫端（`src/cli.py` 或 `src/main.py`）在流程結束時呼叫以記錄 run-level 參數。

- filter_commented_configs(config_path, comment_keyword)
  - 解析 TOML 原始文字，抓出在註解中包含指定關鍵字（例如 `run name`）的設定鍵，供 `run_name` 生成使用。

- log_config(title, config)
  - 以 Rich table 顯示分 section 的設定值（用於啟動時或 debug 時列印）、會依 sections_to_keys 排序顯示。

- 定義的例外類別
  - `ConfigNotFoundError`, `ConfigInvalidTypeError`, `ConfigValidationError`, `EnvironmentVariableError`（供上層使用以表達不同類型的失敗原因）。

重要行為與注意事項：

- allowed_keys 為空集合時，其行為是「允許所有 key 並作為 residual section」，此模式被用於 `litellm_kwargs`（允許自由延伸的參數）。
- `load_config_section_from_toml()` 會對未知鍵發出 warning 並忽略，避免使用者在 TOML 中打錯鍵時造成未預期的覆寫。
- `save_module_config_as_toml()` 會跳過 `config_name`、`sections_to_keys` 等 metadata，僅寫出實際的設定值；若發現多個 residual section，會以錯誤中斷以避免不明行為。
- 實際使用範例：各模組的 `from_toml()`（見 `src/app/configs/*_config.py`）會先呼叫 `load_config_from_toml()`，再呼叫 `override_config()`，最後以回傳的 dict 建構 dataclass 並在 `__post_init__()` 執行 `_validate_config()`。

## 四、留檔機制

目前的 RunManager 實作位於 `src/app/workflow/run_manager.py`（類別 `RunManager`），其行為如下：

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

- `utils/config_helper.save_module_config_as_toml(config, path)` 會依 `sections_to_keys` 把 config 分 section 寫出為 `module_config.toml`；若某 section 的 allowed keys 為空（例如 `litellm_kwargs`），helper 會把該 section 視為 residual section，並把未消耗的 key 寫入該 section。
- `utils/config_helper.save_run_config_as_toml(run_config, path)` 會把 run dataclass 扁平化寫入 `run_config.toml`（只包含非 None 欄位）。由 workflow 函式在收到 `run_config`（非 None）時呼叫 `save_run_config_as_toml()` 寫出；`src/cli.py` 會傳入 run 參數（`src/main.py` 目前不寫出）。

結果檔案與產出：

- `RunManager.save_results_as_json(results, file_path=None)` 會寫出 `results.json`（或指定分檔）。
- 模組無關的 Markdown／發現函式位於 `src/app/workflow/run_persistence.py`（無狀態函式，非 RunManager 方法）：`save_results_as_md()` 把每頁結果寫入 `results/*.md`、`save_query_results_as_md()` 寫 `results/query_{index}.md`、`load_latest_results()` / `load_latest_run_path()` 供跨 run 探索。
- 目前主要 workflow 入口的行為：
  - `run_website_crawler()`：寫 `module_config.toml`、`results.json`、`results/*.md`
  - `run_webpage_image_summarizer()`：寫 `module_config.toml`、`results.json`、`results/*.md`
  - `run_rag_build()`：寫 `module_config.toml`（與 `run_config.toml`）；開啟 `save_vector_store_to_runs` 時，向量庫改存至 `results/vector_store/milvus.db`（`module_config.toml` 記錄覆寫後路徑），否則寫入 config 預設位置（`data/rag/results/`）。
  - `run_rag_query()`：寫 `results.json`（query 三層結構）、`results/query_{index}.md`（每次 query 一份）與 `module_config.toml`；重建（rebuild）時另存一份 `module_config.toml` 到向量庫路徑。
  - `run_agent_query()`：寫 `module_config.toml`（與 `run_config.toml`），並呼叫 `RunManager.save_agent_results_as_json()` 寫 `results_{thread_id}.json`（讀取既有分檔 → 合併本輪 → 覆寫；`thread_id` 未提供時自動 `auto-{uuid}`）；對話結果位於 `runs/<ts>/agent/<config>/`（`RunManager.for_run_no_site()`，**無 `site_id` 層、不寫 `results.json`**）。
  - `run_app()`：寫 `run_config.toml`（**不寫 `module_config.toml`**）；對話結果同樣由 server 的 `_event_stream()` 以 `save_agent_results_as_json()` 落盤至 `runs/<ts>/agent/<config>/results_{thread_id}.json`。
- module_config.toml
- run_config.toml
- terminal.log

### module_config.toml

save_module_config_as_toml() 會依 sections_to_keys 以分 section 形式輸出 TOML。

行為重點：

- 只有 sections_to_keys 中的欄位會被顯式寫出
- 若 config 存在 residual section（section keys 為空），未消耗欄位會寫入 residual section
- 若沒有 residual section，未消耗欄位不會寫入 module_config.toml

### run_config.toml

save_run_config_as_toml() 會把 run dataclass 扁平化成 TOML（只寫非 None 欄位）。

目前實際寫入時機：

- `src/cli.py`：tyro 解析 CLI → 以 `run_config=cli_arg.run` 傳入對應 workflow 函式 → 函式內在流程中呼叫 `save_run_config_as_toml(run_config, run_manager.run_config_toml_path)`
- `src/main.py`：目前不傳入 `run_config`，因此不寫出 `run_config.toml`

因此：

- 走 `src/cli.py` 入口時，run_config.toml 會被寫出（由 workflow 函式代為寫入）
- 直接呼叫 `src/app/workflow/workflow.py` 內函式時，需在呼叫時傳入 `run_config` 才會寫出；`src/main.py` 目前不寫出

### 結果檔案

- `RunManager.save_results_as_json(results, file_path=None)` 會寫出 results.json（或指定分檔）
- `run_persistence.save_results_as_md()` 會寫出 results/\*.md（無狀態函式）
- `run_persistence.save_query_results_as_md()` 會把每次 query 與回覆寫成 results/query_{index}.md（run_rag_query 專用）
- `RunManager.save_agent_results_as_json(thread_id, results, agent_config)` 會把 agent 對話結果寫入 results_{thread_id}.json（讀取既有分檔 → 合併本輪 → 覆寫；run_agent_query 與 server `_event_stream` 使用）

主要流程目前行為：

- run_website_crawler()：寫 module_config.toml、results.json、results/\*.md
- run_webpage_image_summarizer()：寫 module_config.toml、results.json、results/\*.md
- run_rag_build()：寫 module_config.toml（與 run_config.toml）；開啟 `save_vector_store_to_runs` 時，向量庫改存至 `results/vector_store/milvus.db`，否則寫入 config 預設位置（`data/rag/results/`）
- run_rag_query()：寫 results.json（query 三層結構）、`results/query_{index}.md`（每次 query 一份）與 module_config.toml；重建時另存一份到向量庫路徑
- run_agent_query()：寫 module_config.toml（與 run_config.toml）與 `results_{thread_id}.json`（`RunManager.save_agent_results_as_json()` 讀取既有分檔 → 合併本輪 → 覆寫；thread_id 未提供時自動 `auto-{uuid}`）；檔案位於 `runs/<ts>/agent/<config>/`
- run_app()：寫 run_config.toml（不寫 module_config.toml）；對話結果由 server 的 `_event_stream()` 落盤至 `runs/<ts>/agent/<config>/results_{thread_id}.json`

## 五、測試與實驗如何使用 config

倉庫中的測試與實驗（現況）：

- `src/test/test_module.py` 的 smoke test 會透過程式 API 依序呼叫：
  - `run_website_crawler(config_name="test")`
  - `run_webpage_image_summarizer(config_name="test")`
  - `run_rag_build(config_name="test")`

- `src/test/test_main.py` 會測試 crawler 與 summarizer 的串接流程（共用同一個 RunManager）。
- `src/exp.py` 仍保留為手動實驗入口，方便針對不同 `config_name` 或模型版本做比較。

## 六、結論

簡短結論：

`configs/`（TOML）→ `utils/config_helper` 載入與過濾 → `src/app/configs/*.py` 建構 dataclass 並驗證 → `src/app/workflow/run_manager.py`（RunManager）負責寫出 module/run artifacts；`src/app/workflow/data_manager.py`（DataManager）負責發布到 `data/` 持久化路徑。

重點：

- 四個主要模組（crawler、webpage_image_summarizer、rag、agent）使用一致的 config 載入與覆寫流程。
- `BaseModuleConfig`（`src/app/configs/base_config.py`）為共用基底，不綁定 `site_id`；需要 `site_id` 的子類（如 `RAGConfig`、`WebsiteCrawlerConfig`）自行宣告欄位。
- `workflow_config.py`（`src/app/configs/workflow_config.py`）定義 RunConfig 與 ModuleConfig dataclass，供 CLI（tyro）與程式端共用。
- 驗證邏輯被放在各 config 類的 `_validate_config()` 中，以在建構時即捕捉錯誤。
- `save_module_config_as_toml()` 的 residual section 機制允許像 `litellm_kwargs` 之類的彈性欄位被保留並寫入 module_config.toml。

## Evidence

- [src/utils/config_helper.py](src/utils/config_helper.py)
- [src/app/configs/base_config.py](src/app/configs/base_config.py)
- [src/app/configs/workflow_config.py](src/app/configs/workflow_config.py)
- [src/app/configs/website_crawler_config.py](src/app/configs/website_crawler_config.py)
- [src/app/configs/webpage_image_summarizer_config.py](src/app/configs/webpage_image_summarizer_config.py)
- [src/app/configs/rag_config.py](src/app/configs/rag_config.py)
- [src/app/configs/agent_config.py](src/app/configs/agent_config.py)
- [src/app/engines/website_crawler.py](src/app/engines/website_crawler.py)
- [src/cli.py](src/cli.py)
- [src/main.py](src/main.py)
- [src/test/test_module.py](src/test/test_module.py)
- [src/test/test_main.py](src/test/test_main.py)
