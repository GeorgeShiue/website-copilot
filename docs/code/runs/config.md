# Config

## 待辦事項

- [x] webpage_image_summarizer 的 litellm_kwargs 改為獨立的 section，並且保存到 module_config.toml
- [x] 調整 website_crawler 的參數型態和預設值 (max_depth 改成 0 代表不限制深度, exclude_words 改成 list)
- [x] 重構 config 架構
- [x] 保留建置 vector store 的 config 到 data/rag/results/qdrant_db
- [x] 設計 run config class
- [x] 提供 CLI 參數覆寫 config 功能
- [ ] 使用 yaml + pydantic 取代 toml + dataclass

## 一、config 架構

[app/workflow/workflow.py](app/workflow/workflow.py)、[cli.py](cli.py) 與 [app/workflow/workflow_manager.py](app/workflow/workflow_manager.py) 共同負責執行路徑與檔案留存。

專案模組參數實際存放於 `configs/` 目錄下（例如 `configs/website_crawler/`、`configs/webpage_image_summarizer/`、`configs/rag/`），每個模組由對應的 dataclass 在 `app/configs/` 中載入與驗證。根據目前程式碼庫，三個主要 config 類分別位於：

- `app/configs/website_crawler_config.py`
- `app/configs/webpage_image_summarizer_config.py`
- `app/configs/rag_config.py`

三個 config class 的載入流程一致：

1. 由 `config_name` 組出 TOML 檔路徑（例如 `configs/<module>/<config_name>.toml`）
2. 透過 `sections_to_keys` 定義允許的欄位，逐 section 載入 TOML
3. 使用共用 helper（`utils/config_helper.py`）做欄位過濾、覆寫與合併
4. 建構 dataclass 並在 `__post_init__` 或模組內呼叫 `_validate_config()` 進行型別與範圍驗證

備註：直接在程式中呼叫 `app/workflow/workflow.py` 或 `main.py` 的 pipeline 時，通常不會自動寫入 `run_config.toml`；由 CLI (`cli.py`) 啟動時，才會呼叫 `utils.config_helper.save_run_config_as_toml()` 並寫出 `run_config.toml`（此機制同為保持執行可追溯性）。

## 二、各模組怎麼載入與覆寫

以下為各模組在程式庫中的實際對應位置與載入流程摘要（已同步程式碼）：

### Website crawler

- Config dataclass: `app/configs/website_crawler_config.py`
- TOML 範例與實作：`configs/website_crawler/{config_name}.toml`（例如 `configs/website_crawler/default.toml`）
- 載入流程：
  1. `WebsiteCrawlerConfig.from_toml(config_name, **overrides)` 會依 `DEFAULT_CONFIG_FOLDER_PATH` 組出 `configs/website_crawler/{config_name}.toml`。
  2. 呼叫 `utils.config_helper.load_config_from_toml()` 逐 section 讀入且過濾非允許欄位。
  3. 呼叫 `utils.config_helper.override_config()` 套用 CLI 或程式層級的 overrides（會根據 `sections_to_keys` 過濾）。
  4. 建構 `WebsiteCrawlerConfig` 並在 `__post_init__()` 呼叫 `_validate_config()` 做完整驗證。

欄位說明與驗證重點：

- `init`：`max_depth`、`max_pages`、`content_threshold`、`light_mode`、`wait_for_images`（`max_depth` 若為 0 表示無限制，驗證為 int 或 None 且不可小於 0）。
- `crawl`：`url`、`url_patterns`、`allowed_domains`、`exclude_words`（`exclude_words` 必須為 list 或 None）。\*\*
  \*\*

### Webpage image summarizer

- Config dataclass: `app/configs/webpage_image_summarizer_config.py`
- TOML 範例與實作：`configs/webpage_image_summarizer/{config_name}.toml`
- 載入流程與注意：
  1. `WebpageImageSummarizerConfig.from_toml(config_name, **overrides)` 會載入 `configs/webpage_image_summarizer/{config_name}.toml`，並套用 `sections_to_keys` 規則。
  2. `litellm_kwargs` 被設為 residual section（allowed keys 空集合），因此在覆寫時允許任意延伸鍵值並會保留在 config 物件中。
  3. 建構後執行 `_validate_config()` 做型別檢查（例如 `download_timeout > 0`，`vlm_max_workers > 0`，`image_source` 僅允許 `images` 或 `markdown`）。

### RAG

- Config dataclass: `app/configs/rag_config.py`
- TOML 範例與實作：`configs/rag/{config_name}.toml`
- 載入流程：
  1. `RagConfig.from_toml(config_name, **overrides)` 會載入 `configs/rag/{config_name}.toml`。
  2. `utils.config_helper.load_config_from_toml()` 與 `override_config()` 處理合併與覆寫。
  3. 建構 `RagConfig` 後執行 `_validate_config()`（驗證 `qdrant_db_folder_path`、`milvus_uri`、`vector_store_type`、`chunk_size`、`similarity_top_k`、`cutoff`、`hybrid_ranker`、`hybrid_ranker_params` 等）。

欄位摘要：

- `vector_store`：`vector_store_type`（`"qdrant"` 或 `"milvus"`）、`qdrant_db_folder_path`、`milvus_uri`、`collection_name`（預設 `webpages`）、`hybrid_ranker`（`"RRFRanker"` 或 `"WeightedRanker"`，預設 `"WeightedRanker"`）、`hybrid_ranker_params`（dict，例如 `{"weights": [1.0, 0.5]}`）。
- `nodes`：`chunk_size`、`chunk_overlap`、`paragraph_separator`。
- `retriever`：`similarity_top_k`（預設 `10`）、`query_mode`（`"default"` 或 `"hybrid"`）、`hybrid_top_k`（預設 `10`）、`alpha`（預設 `0.5`）。
- `query_engine`：`llm_name`、`cutoff`（預設 `0.0`；hybrid 模式跳過 cutoff）、`query`。
- `query_engine.query` 讓不同實驗可以直接在 config TOML 中切換查詢問題，並由 workflow 讀取後執行。

## 三、共用載入、覆寫與驗證機制

[utils/config_helper.py](utils/config_helper.py) 是專案的設定工具中心，`app/configs/*` 的 dataclass 與 `app/workflow/*` 的流程都會透過它來載入、覆寫、驗證與寫回設定檔。以下依實作（參考 `utils/config_helper.py`）說明主要責任與行為：

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
  - 扁平化 run dataclass（只寫非 None 欄位）並寫入 run_config.toml，通常由 CLI 在流程結束時呼叫以記錄 run-level 參數。

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
- 實際使用範例：各模組的 `from_toml()`（見 `app/configs/*_config.py`）會先呼叫 `load_config_from_toml()`，再呼叫 `override_config()`，最後以回傳的 dict 建構 dataclass 並在 `__post_init__()` 執行 `_validate_config()`。

## 四、留檔機制

目前的 RunManager 實作位於 `app/workflow/workflow_manager.py`（類別 `RunManager`），其行為如下：

- 建立 `runs/<timestamp>/<module>/<run>/` 目錄結構
- 會產生並管理以下檔案路徑：
  - `results.json`
  - `results/`（Markdown 檔案）
  - `module_config.toml`
  - `run_config.toml`
  - `terminal.log`

module_config 與 run_config 的寫入機制：

- `utils/config_helper.save_module_config_as_toml(config, path)` 會依 `sections_to_keys` 把 config 分 section 寫出為 `module_config.toml`；若某 section 的 allowed keys 為空（例如 `litellm_kwargs`），helper 會把該 section 視為 residual section，並把未消耗的 key 寫入該 section。
- `utils/config_helper.save_run_config_as_toml(run_config, path)` 會把 run dataclass 扁平化寫入 `run_config.toml`（只包含非 None 欄位）。通常由 CLI（`cli.py`）在流程結束時呼叫以確保 run-level 參數被紀錄。

結果檔案與產出：

- `RunManager.save_results_as_json()` 會寫出 `results.json`。
- `RunManager.save_results_as_md()` 會把每頁結果寫入 `results/*.md`。
- 目前四個主要 workflow 的行為：
  - `run_website_crawler()`：寫 `module_config.toml`、`results.json`、`results/*.md`
  - `run_webpage_image_summarizer()`：寫 `module_config.toml`、`results.json`、`results/*.md`
  - `run_rag_build()`：寫 `module_config.toml`，並將部分設定另存到向量庫路徑（依 `vector_store_type` 決定存至 `qdrant_db_folder_path/` 或 `milvus_uri/`）。
  - `run_rag_query()`：寫 `module_config.toml`，並將部分設定另存到向量庫路徑（依 `vector_store_type` 決定）。
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

目前實際寫入時機在 [cli.py](cli.py)：

- tyro 解析 CLI
- 執行對應 run\_\* 流程
- 最後呼叫 `save_run_config_as_toml(cli_arg.run, run_manager.run_config_toml_path)`

因此：

- 走 CLI 入口時，run_config.toml 會被寫出
- 直接呼叫 [run.py](run.py) 或 [main.py](main.py) 內函式時，通常不會自動寫 run_config.toml

### 結果檔案

- RunManager.save_results_as_json() 會寫出 results.json
- RunManager.save_results_as_md() 會寫出 results/\*.md

四條流程目前行為：

- run_website_crawler()：寫 module_config.toml、results.json、results/\*.md
- run_webpage_image_summarizer()：寫 module_config.toml、results.json、results/\*.md
- run_rag_build()：寫 module_config.toml，另存一份到向量庫路徑（依 `vector_store_type` 決定存至 `qdrant_db_folder_path/` 或 `milvus_uri/`）
- run_rag_query()：寫 module_config.toml，另存一份到向量庫路徑（依 `vector_store_type` 決定）

## 五、測試與實驗如何使用 config

倉庫中的測試與實驗（現況）：

- `test/test_module.py` 的 smoke test 會透過程式 API 依序呼叫：
  - `run_website_crawler(config_name="test")`
  - `run_webpage_image_summarizer(config_name="test")`
  - `run_rag_build(config_name="test")`

- `test/test_main.py` 會測試 crawler 與 summarizer 的串接流程（共用同一個 RunManager）。
- `exp.py` 仍保留為手動實驗入口，方便針對不同 `config_name` 或模型版本做比較。

## 六、結論

簡短結論：

`configs/`（TOML）→ `utils/config_helper` 載入與過濾 → `app/configs/*.py` 建構 dataclass 並驗證 → `app/workflow/workflow_manager.py`（RunManager）負責寫出 module/run artifacts。

重點：

- 三個主要模組（crawler、webpage_image_summarizer、rag）使用一致的 config 載入與覆寫流程。
- 驗證邏輯被放在各 config 類的 `_validate_config()` 中，以在建構時即捕捉錯誤。
- `save_module_config_as_toml()` 的 residual section 機制允許像 `litellm_kwargs` 之類的彈性欄位被保留並寫入 module_config.toml。

## Evidence

- [utils/config_helper.py](utils/config_helper.py)
- [app/website_crawler_config.py](app/website_crawler_config.py)
- [app/webpage_image_summarizer_config.py](app/webpage_image_summarizer_config.py)
- [app/rag_config.py](app/rag_config.py)
- [app/website_crawler.py](app/website_crawler.py)
- [run.py](run.py)
- [cli.py](cli.py)
- [run_config.py](run_config.py)
- [utils/run_manager.py](utils/run_manager.py)
- [main.py](main.py)
- [test/test_module.py](test/test_module.py)
- [test/test_main.py](test/test_main.py)
