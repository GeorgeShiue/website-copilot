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

## Phase B：設定檔改為 YAML

### 變更

- 新增 `config/yaml_helper.py`（初版名為 `yaml_io.py`，審核時改名，與 `config_helper`／`log_helper` 命名一致）：`load_config_dict(folder, name)` 讀取 `{name}.yml`、逐層處理 `extends`（同資料夾、單一繼承、多層、循環偵測、找不到父檔時列出繼承鏈），以 `deep_merge` 由父到子合併；回傳 `LoadedConfig(data, path, chain)`，`source` 為錯誤訊息與存檔檔頭用的來源描述（`configs/rag/test.yml (extends: test_nculab → nculab → default)`）。
- `BaseModuleConfig.from_toml` → `from_yaml`：取出最上層 `run_name_fields`（檢查為字串 list、每個 dotted path 都指向模型欄位），套用 overrides 後只驗證一次；新增 `source` PrivateAttr。
- `utils/config_helper.py`
  - 新增 `dump_yaml`（自訂 SafeDumper：多行字串為 `|` block scalar、只有換行的字串如 `"\n\n"` 用雙引號、`allow_unicode`、`sort_keys=False`、`None` 為 `null`，header 寫成 `# ` 註解）。
  - `save_module_config_as_toml` → `save_module_config`（`model_dump()`，檔頭 `# source: ...`、`# run_name_fields: [...]`）；`save_run_config_as_toml` → `save_run_config`（所有欄位，`None` 為 `null`）。
  - 刪除 `filter_commented_configs`、`_drop_none` 與 tomlkit。
  - dumper 放在 `config_helper` 而非 `yaml_helper`：`yaml_helper` 需要 `ConfigValidationError`，若 `config_helper` 再 import `yaml_helper` 會循環 import。
- `configs/`：26 份 `.toml` 以一次性腳本轉出 `default.yml`（tomllib 讀取 + `dump_yaml`），其餘手寫為 extends：
  - `{site}.yml` extends `default`，`test_{site}.yml` extends `{site}`，`test.yml` extends `test_nculab`（原 `test.toml` 與 `test_nculab.toml` 內容相同；`test.toml` 有 `path_prefix`，不能只 extends default）。
  - `default.yml` 明寫可選欄位為 `null`（`max_pages`、`path_prefix`、`seed`、`webpages_data_folder_path`、`milvus_uri`），讓完整欄位一目了然。
  - 補回註解：`# KEEP_IMAGE_CONTENT_THRESHOLD`、litellm 參數範例、`max_depth` 的 null 語意、RRFRanker 切換寫法、`cutoff` 生效條件。
  - `# run name` 註解改為 `run_name_fields`：crawler 站點檔 `[init.max_depth]`、test 檔 `[init.max_pages]`；image_summarizer 站點／test 檔 `[summarize.model]`；rag 在 default 設定 `[vector_store.vector_store_type]`；各 default 與 agent 為 `[]`。
  - agent 的 system prompt 改為 `|-` block scalar：原 TOML 的 `\\n` 是字面上的反斜線加 n，現在是真正的換行（**送給 LLM 的 prompt 內容改變**，依 plan 屬修正）。
  - 保留 `rag/test_ncucsie.yml` 的 query 為 nculab 的問題（與原 toml 相同，Phase D 處理）。
- 新增 `configs/README.md`：目錄慣例、保留 key、extends 合併規則與 `null`／`{}` 語意、YAML 1.1 撰寫注意事項（`1e-3`、`yes/no`、日期、`*` 開頭需加引號）、`module_config.yml` 檔頭。
- 輸出：runs/ 與 data/ 的 `module_config.toml`／`run_config.toml` 改為 `.yml`；`RunManager.module_config_toml_path`／`run_config_toml_path` 改名 `module_config_path`／`run_config_path`，log 表格標籤去掉 "toml"。
- data/ 既有的舊記錄檔直接轉換為 `.yml`（見下方「data/ 舊記錄檔轉換」），`DataManager.publish_run_metadata` 不做任何清理，只寫 `.yml`。
- `save_generated_exclude_words` 不再輸出 `generated_exclude_words.toml`，只寫 `exclude_words_report.json`（`data/raw_webpages/` 目前沒有舊檔，不需清理）。
- 其餘呼叫端 `from_toml` → `from_yaml`、`save_*_as_toml` → `save_*`，docstring 與 log 標題中的 toml 一併更新。
- 相依套件：加入 `pyyaml>=6.0.3`，移除 `tomlkit`。
- 文件：README（設定說明、configs 目錄樹）、`docs/code/runs/{config,cli,workflow}.md`。`cli.md` 第三節「參數覆寫規則」在 Phase A 漏改（仍描述 `override_config`／`sections_to_keys`），本次一併更新。
- 測試
  - `test_configs.py` 改用 YAML：`_load_dict` 改為 extends 展開後的 dict；新增繼承鏈錯誤訊息、YAML 1.1 陷阱被 strict 攔截、`run_name_fields` 格式／路徑錯誤、存檔檔頭與 `null`／block scalar 輸出、`configs/` 不再有 `.toml`。
  - 新增 `test_config_extends.py`（31 個）：`deep_merge` 各合併規則、多層繼承、循環（含自我繼承）、找不到父檔、`.toml` 不被接受、`extends` 值格式（含 `null`）、`run_name_fields` 繼承／取代／省略、非頂層保留 key 被拒、`null` 清除可選／必填欄位、切換 RRFRanker 需清除 weights、`{}` 不清空 section。
  - `test_pipeline_prepare.py`：改讀 `module_config.yml`。
  - `test_serve_rag_loading.py` 改複製 `default.yml`；`agent_stubs.py`、`test_pipeline_serve.py`、`test_rag_tools.py` 跟著改名。

### 與 plan 不同或 plan 未明訂的決定（請審核）

1. **`test.yml` extends `test_nculab`**：plan 範例寫 `test.yml` extends `default` 只改 `max_pages`，但現行 `test.toml` 還有 `path_prefix = "/site/nculab"`（default 沒有），且 run name 欄位與 `test_nculab` 相同。為了載入結果不變，改為 extends `test_nculab`（兩者原本內容完全相同）。Phase D 刪除站點組合檔時會重新整理。
2. **`extends: null` 報錯**：值必須是非空字串；寫 `null` 不視為「沒有繼承」。
3. **`run_name_fields` 在載入時檢查路徑**：每個 dotted path 必須指向模型欄位（中間段必須是 section），否則報錯；避免拼錯欄位時到 `run_name` 才以 `AttributeError` 失敗。
4. **`run_config.yml` 寫出所有欄位**：舊版略過 `None` 欄位（TOML 無 null），現在依 B3 輸出 `null`，紀錄更完整。
5. **`dump_yaml` 對「只有換行」的字串用雙引號**：PyYAML 預設會把 `"\n\n"` 輸出成跨行的單引號字串，難以閱讀。
6. **data/ 舊記錄檔改為直接轉換（推翻 plan Q4）**：初版依 Q4 在 `publish_run_metadata` 寫入時刪除舊 `.toml`；審核時改為一次性轉換既有檔案並移除清理邏輯。理由：程式不留過渡邏輯、data/ 與 git 立即一致（不必等下次 publish）、publish 不會刪除它沒寫的檔案，也避免「先刪舊檔、新檔寫入失敗」時資料夾沒有任何記錄。代價：不在 git 中、另外 publish 的 data/（如部署機）不會被清理，舊 `.toml` 會與新 `.yml` 並存（程式不讀取，不影響功能）。

### data/ 舊記錄檔轉換

git 追蹤的 9 份舊記錄檔（data/ 下沒有其他 `.toml`）以一次性腳本（scratchpad，不進版控）轉換後刪除原檔：

| 類型 | 檔案 | 轉換方式 |
|---|---|---|
| module_config | `data/rag/{claudecode,ncucsie,nculab}/`、`data/webpages/{ncucsie,nculab}/` | `[init]` 的 `site_id`（rag 另含 `webpages_data_folder_path`）移到最上層，以現行模型 `model_validate` 後由 `save_module_config` 寫出；檔頭 `# source: 轉換自舊版 module_config.toml`，`# run_name_fields` 由原 `# run name` 註解轉換（rag `[vector_store.vector_store_type]`、webpages `[summarize.model]`） |
| run_config | `data/rag/{ncucsie,nculab}/`、`data/webpages/{ncucsie,nculab}/` | `dump_yaml` 原樣轉格式；已不存在的欄位（`save_vector_store_to_runs`）與缺少的欄位（`save`）不補不刪，保留當時執行的紀錄 |

驗證：9 份 `.yml` 與 `git show HEAD:<原 .toml>` 比對，module_config 在上述位置調整後逐欄位相同且可被現行模型讀回，run_config 完全相同。`runs/` 中的舊 `.toml` 為歷史執行紀錄、程式不讀回，不轉換。

### 驗證

- 轉檔比對：26 份舊 `.toml`（`tomllib` 讀取）與新 `.yml` 經 extends 展開後的 dict，扣除明寫為 `null` 的可選欄位後**完全相同**；`run_name_fields` 與原 `# run name` 註解解析結果也全部相同。唯一例外為 agent prompt 的 `\\n`，比對前先換算。
- config 快照比對：與動工前 baseline **26 份無差異**（agent prompt 的 `\\n` 換算後），`run_name` 全部相同。
- `scripts/check.sh`：exit 0（ruff、pyright 0 errors、257 passed、widget 同步；移除舊檔清理測試後重跑）。
- `uv run pytest tests/integration -m "not cost"`：2 passed、5 deselected；實際產生的 `runs/<ts>/agent_build/test/module_config.yml` 檔頭為 `# source: configs/agent/test.yml (extends: default)`，prompt 為 block scalar。
- CLI 冒煙：`prepare`／`serve`／`exp --help` 與 `run {website-crawler,image-summarizer,rag-build,rag-query,agent} --help` 皆 exit 0。
- `grep -rn toml src tests scripts`：只剩 `.toml` 不被接受、`configs/` 無 `.toml` 的測試。
