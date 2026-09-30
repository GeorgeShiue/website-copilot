# 模組配置重構：實作紀錄

> 計畫見 [plan.md](./plan.md)

## Phase A：config 模型改為 pydantic + 巢狀 class

### 變更

- `config/base_config.py`
  - 新增 `ConfigModel`（`strict=True`、`extra="forbid"`、`validate_assignment=True`）與 `NonEmptyStr`。
  - `BaseModuleConfig` 改為 pydantic model：`config_name`、`run_name_fields` 為 `PrivateAttr`（以 property 讀取），由 `from_toml()` 設定，不參與驗證與 `model_dump()`。
  - `from_toml()`：`tomllib` 讀出 dict → 套用 overrides → `model_validate`；`ValidationError` 轉成 `ConfigValidationError`（`format_validation_error()`），訊息為 `設定檔路徑: 欄位路徑: 訊息`，自訂 validator 的訊息去掉 pydantic 的 `Value error, ` 前綴。
  - `run_name` 以 dotted path 取值（`get_field()`），字串以最後一段欄位名組成。
- 四個 module config 改為巢狀 model：
  - `WebsiteCrawlerConfig`：`site_id` + `init`／`crawl`／`clean`。
  - `ImageSummarizerConfig`：`site_id` + `init`／`summarize` + `litellm_kwargs`（dict，預設 `{}`）。
  - `RAGConfig`：`site_id`、`webpages_data_folder_path` + `nodes`／`vector_store`／`index`／`retriever`／`query_engine`；路徑推導由 `__post_init__` 改為 `model_validator(mode="after")`。`hybrid_ranker_params` 改為 `HybridRankerParams`（`weights: list[float]`（長度 2）、`k: PositiveInt`，皆可省略）。
  - `AgentConfig`：`llm_name`、`system_prompt`（無 section）。
- 刪除：`SECTIONS_TO_KEYS`／`*_KEYS`／`DEFAULT_*_SECTION` 對照表、四個 `_validate_config`、`_normalize_toml_types`、`load_config_from_toml`／`load_config_section_from_toml`／`override_config`／`_filter_allowed_config_keys`／`_load_toml_section`、未使用的 `ConfigNotFoundError`／`ConfigInvalidTypeError`、`DEFAULT_PROMPT`／`DEFAULT_SYSTEM_PROMPT`／`DEFAULT_LLM_NAME`／`DEFAULT_LLM_MODEL`／`DEFAULT_CONFIG_NAME`。`KEEP_IMAGE_CONTENT_THRESHOLD`／`KEEP_TITLE_CONTENT_THRESHOLD` 保留（`WebsiteCrawler` 參數預設值仍使用）。
- `utils/config_helper.py`
  - `filter_commented_configs` 追蹤目前的 `[section]`，回傳 dotted path（`init.max_depth`；最上層欄位只有欄位名）。
  - `save_module_config_as_toml`：`model_dump()` 後遞迴略過 `None`，最上層欄位在前、section 為 `[table]`、section 內的 dict 為 inline table。
  - `log_config`：最上層欄位一張表（標題為 class 名稱）、每個 section 一張表；欄位順序改為模型宣告順序（舊版依字母排序）。
- `configs/*.toml`
  - `site_id` 由 `[init]` 移到最上層；rag 的 `[init]` 因此清空並刪除。
  - agent 刪除 `[agent]` section 標頭（欄位改在最上層）。
  - rag 補上原本缺少、由程式預設值提供的 `alpha = 0.5`、`cutoff = 0.0`。其他模組的 toml 原本就寫齊必填欄位。
- 呼叫端改為巢狀存取：`pipelines/{prepare,exp}.py`、`retrieval/{factory,evaluation}.py`、`ingestion/indexing/index.py`（`hybrid_ranker_params` 以 `model_dump(exclude_none=True)` 轉回 dict 傳給 Milvus）。
- `ImageSummarizer.summarize_crawl_results_images` 的 `model`、`prompt` 改為必填，移除隱藏預設 `model="gemini-3-flash-preview"`。
- `WebsiteCrawler` 的 `url_patterns`／`allowed_domains` 型別簡化為 `list[str] | None`；crawl4ai 的 `URLPatternFilter` 參數為 `list[str | Pattern]`（list 不變性），呼叫處轉型。
- `DataManager.publish_run_metadata` 的 `config` 型別由 `object` 改為 `BaseModel`。
- `pyproject.toml` 明確加入 `pydantic>=2.12.5`。
- 文件：`docs/code/runs/config.md` 第一～三節、module_config.toml 小節與結論改寫為 pydantic 版本；`docs/code/runs/workflow.md` 的 config 載入說明同步更新。
- 測試
  - 新增 `tests/unit/test_configs.py`（71 個）：載入 `configs/` 下所有設定檔；bool 放 int 欄位、字串數字、`allowed_domains` 為字串、未知 key（最上層與 section）、缺必填欄位、空白字串、`path_prefix`、跨欄位規則、`weights` 長度、`validate_assignment`、錯誤訊息含設定檔路徑、扁平 overrides、run name 解析與組成、PrivateAttr 不進 `model_dump`、`save_module_config_as_toml` 往返與 section 結構。
  - `test_pipeline_prepare.py`：fake `build_rag` 改寫 `config.vector_store.milvus_uri`（原本改寫扁平的 `config.milvus_uri`，被 `extra="forbid"` 擋下）。
  - `test_pipeline_serve.py`：`AgentConfig` 替身由 `MagicMock` 改為真實的 `AgentConfig`（`log_config` 需要 pydantic model）。
  - `test_rag_tools.py`：刪除扁平的 `_FakeRAGConfig`，`_make_builder()` 改用 `RAGConfig.from_toml("test")`。

### 與 plan 不同或 plan 未明訂的決定（請審核）

1. **`site_id` 放在設定檔最上層**：依 plan 的 `RAGConfig` 範例（`site_id` 為頂層欄位），toml 的 `site_id` 由 `[init]` 移到最上層。RAG 的 `webpages_data_folder_path` 原本也在 `[init]`，一併移到最上層（兩者都在 Phase D 移除），rag 的 `[init]` section 因此消失。
2. **`AgentConfig` 不設 section**：原本只有一個 `[agent]` section，改成欄位直接放最上層，存取維持 `config.llm_name`，也讓 Phase C 的 CLI 參數為 `--module.llm-name`（而非 `--module.agent.llm-name`）。
3. **`NonEmptyStr` 不 strip**：plan 定義為 `StringConstraints(strip_whitespace=True, min_length=1)`，但 strip 會改寫值，image summarizer 的 prompt 前後換行會被移除，送給 VLM 的內容改變、快照也會不同。改為 `AfterValidator` 只檢查「不可為空白字串」、不改寫值，prompt 也套用。
4. **`url_patterns`／`allowed_domains` 預設 `None`**：plan 的可選欄位清單未列出這兩個，但它們的語意是「不過濾」（`WebsiteCrawler` 以 `None` 判斷是否加 filter），且 Phase D 的 `SiteCrawlConfig` 也是 `= None`。list 另加 `min_length=1`（沿用舊版「列表不可為空」）。
5. **`max_depth` 預設 `None`**：plan 的可選欄位清單未列出，但舊版 `max_depth` 即為 `int | None = None`，`None` 代表不限制深度（`docs/code/runs/config.md` 有記載），設為必填會失去這個功能。
6. **`hybrid_ranker_params` 跨欄位規則只在有設定時檢查**：`hybrid_ranker_params` 為可選欄位，未設定時 `VectorStoreBuilder` 依 ranker 使用預設參數（`k=60`／`weights=[1.0, 0.5]`），因此 `None` 對兩種 ranker 都合法。
7. **overrides 暫為扁平欄位名稱（過渡）**：Phase A 的 CLI 中介層與 `exp.py` 仍傳扁平 key（`similarity_top_k=20`、`site_id=...`），`_apply_flat_overrides` 依欄位名稱放入所屬 section（各模型的欄位名稱在最上層與 section 間皆唯一）；找不到欄位時報錯（舊版為 warning 後忽略）。Phase C 改為巢狀 overrides 後刪除。`cli/run.py` 的 `weights → hybrid_ranker_params` 特例依 plan 留到 Phase C 刪除。
8. **run name 欄位在載入時解析**：舊版每次讀 `run_name` 都重新讀檔；現在由 `from_toml()` 解析一次存入 `_run_name_fields`（Phase B 改為 `run_name_fields` key 時介面不變）。不經 `from_toml()` 直接建構的 config，`run_name` 為 `default`。
9. **strict 模式下 int 可放進 float 欄位**：pydantic strict 的既定行為（`download_timeout = 10` 會通過），其餘方向（bool → int、str → int、float → int）都會被擋。已加測試，未改用 `StrictFloat`。

### 驗證

- config 快照比對：動工前以舊程式載入 4 模組 × 26 份設定檔（全部欄位值 + `run_name` + `config_name`）作為 baseline；Phase A 後以新程式產生（巢狀展平）比對，**26 份完全相同，無差異**（含 rag 補上的 `alpha`／`cutoff` 與推導出的 `webpages_data_folder_path`／`milvus_uri`）。
- `save_module_config_as_toml` 新舊輸出比對（claudecode／agent test）：所有值相同；結構差異僅為預期的 `init.site_id` → 最上層 `site_id`、rag `init.webpages_data_folder_path` → 最上層、agent `[agent]` → 最上層。
- `scripts/check.sh`：exit 0（ruff、pyright 0 errors、216 passed、widget 同步）。
- `uv run pytest tests/integration -m "not cost"`：2 passed、5 deselected。
- CLI 冒煙：`prepare`／`serve`／`exp --help` 與 `run {website-crawler,image-summarizer,rag-build,rag-query,agent} --help` 皆 exit 0。
