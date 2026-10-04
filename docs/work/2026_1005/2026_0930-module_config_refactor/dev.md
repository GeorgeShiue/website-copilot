# 模組配置重構：實作紀錄

> 計畫見 [plan.md](./plan.md)。只記錄與 plan 不同或 plan 未明訂的決定、過程中的發現與驗證結果。除特別註明外，每個 Phase 的共同關卡（`scripts/check.sh`、`tests/integration -m "not cost"`＝2 passed、CLI 冒煙）皆通過，括號內為 `check.sh` 的通過測試數（pyright 皆 0 errors）。

## Phase A：config 模型改為 pydantic＋巢狀 class

### 補充（plan 未明訂）

- `BaseModuleConfig` 的 `config_name`、`run_name_fields` 為 `PrivateAttr`，由 `from_toml()` 設定；`ValidationError` 轉 `ConfigValidationError`，訊息為 `設定檔路徑: 欄位路徑: 訊息`，自訂 validator 去掉 pydantic 的 `Value error, ` 前綴。
- `log_config` 欄位順序改為模型宣告順序（舊版依字母排序）。
- `KEEP_IMAGE_CONTENT_THRESHOLD`／`KEEP_TITLE_CONTENT_THRESHOLD` 保留（`WebsiteCrawler` 參數預設值仍使用）；`crawl4ai` 的 `URLPatternFilter` 參數為 `list[str | Pattern]`（list 不變性），呼叫處轉型。
- rag 補上原本缺少、由程式預設值提供的 `alpha = 0.5`、`cutoff = 0.0`；其他模組的 toml 原本就寫齊必填欄位。
- 測試：新增 `test_configs.py`（71 個）；`test_pipeline_prepare.py` 的 fake `build_rag` 改寫 `config.vector_store.milvus_uri`（原本改寫扁平欄位，被 `extra="forbid"` 擋下）；`AgentConfig` 替身由 `MagicMock` 改為真實 config（`log_config` 需要 pydantic model）。

### 與 plan 不同或 plan 未明訂的決定（請審核）

1. **`site_id` 放在設定檔最上層**：依 plan 的 `RAGConfig` 範例，toml 的 `site_id` 由 `[init]` 移到最上層；RAG 的 `webpages_data_folder_path` 一併移到最上層（兩者都在 Phase D 移除），rag 的 `[init]` section 因此消失。
2. **`AgentConfig` 不設 section**：欄位直接放最上層，存取維持 `config.llm_name`，Phase C 的 CLI 參數為 `--module.llm-name`。
3. **`NonEmptyStr` 不 strip**：plan 的 `strip_whitespace=True` 會改寫值，image summarizer prompt 前後換行會被移除、送給 VLM 的內容改變、快照也會不同。改為 `AfterValidator` 只檢查「不可為空白字串」。
4. **`url_patterns`／`allowed_domains` 預設 `None`**：語意是「不過濾」（`WebsiteCrawler` 以 `None` 判斷是否加 filter），Phase D 的 `SiteCrawlConfig` 也是 `= None`；list 另加 `min_length=1`。
5. **`max_depth` 預設 `None`**：舊版即為 `int | None = None`，`None` 代表不限制深度，設為必填會失去這個功能。
6. **`hybrid_ranker_params` 跨欄位規則只在有設定時檢查**：未設定時 `VectorStoreBuilder` 依 ranker 使用預設參數（`k=60`／`weights=[1.0, 0.5]`），`None` 對兩種 ranker 都合法。
7. **overrides 暫為扁平欄位名稱（過渡）**：CLI 中介層與 `exp.py` 仍傳扁平 key，`_apply_flat_overrides` 依欄位名稱放入所屬 section；找不到欄位時報錯（舊版為 warning 後忽略）。Phase C 改為巢狀後刪除。
8. **run name 欄位在載入時解析一次**（舊版每次讀 `run_name` 都重新讀檔）；不經 loader 直接建構的 config，`run_name` 為 `default`。
9. **strict 模式下 int 可放進 float 欄位**：pydantic strict 的既定行為，其餘方向都會被擋；已加測試，未改用 `StrictFloat`。

### 驗證

- config 快照：動工前以舊程式載入 4 模組 × 26 份設定檔作為 baseline，Phase A 後**26 份完全相同，無差異**。
- `save_module_config_as_toml` 新舊輸出比對：值相同，結構差異僅為預期的 `site_id`、`webpages_data_folder_path`、`[agent]` 移到最上層。
- `check.sh`：216 passed。

## Phase B：設定檔改為 YAML

### 補充（plan 未明訂）

- 新增 `config/yaml_helper.py`（初版名為 `yaml_io.py`，審核時改名，與 `config_helper`／`log_helper` 命名一致），`load_config_dict` 回傳 `LoadedConfig(data, path, chain)`；`source` 為錯誤訊息與存檔檔頭用的來源描述。
- dumper 放在 `config_helper` 而非 `yaml_helper`：`yaml_helper` 需要 `ConfigValidationError`，若 `config_helper` 再 import `yaml_helper` 會循環 import。
- 轉檔時 `default.yml` 明寫可選欄位為 `null`，讓完整欄位一目了然；補回註解（`# KEEP_IMAGE_CONTENT_THRESHOLD`、litellm 參數範例、`max_depth` 的 null 語意、RRFRanker 切換寫法、`cutoff` 生效條件）。
- `run_name_fields`：crawler 站點檔 `[init.max_depth]`、test 檔 `[init.max_pages]`；image_summarizer 站點／test 檔 `[summarize.model]`；rag 在 default 設定 `[vector_store.vector_store_type]`；各 default 與 agent 為 `[]`。
- agent 的 system prompt 改為 `|-` block scalar：**送給 LLM 的 prompt 內容改變**（原 `\\n` 是字面反斜線加 n），依 plan 屬修正。
- 新增 `configs/README.md`。`cli.md` 第三節「參數覆寫規則」在 Phase A 漏改，本次一併更新。
- 測試：`test_configs.py` 改用 YAML；新增 `test_config_extends.py`（31 個）。

### 與 plan 不同或 plan 未明訂的決定（請審核）

1. **`test.yml` extends `test_nculab`**：plan 範例寫 extends `default` 只改 `max_pages`，但現行 `test.toml` 還有 `path_prefix = "/site/nculab"`，且 run name 欄位與 `test_nculab` 相同（兩者原本內容完全相同）。為了載入結果不變而改。Phase D 刪除站點組合檔時重新整理。
2. **`extends: null` 報錯**：值必須是非空字串。
3. **`run_name_fields` 在載入時檢查路徑**：每個 dotted path 必須指向模型欄位，避免拼錯欄位時到 `run_name` 才以 `AttributeError` 失敗。
4. **`run_config.yml` 寫出所有欄位**：舊版略過 `None`（TOML 無 null），現在輸出 `null`，紀錄更完整。
5. **`dump_yaml` 對「只有換行」的字串用雙引號**：PyYAML 預設輸出跨行單引號字串，難以閱讀。
6. **data/ 舊記錄檔改為直接轉換（推翻 plan Q4）**：初版依 Q4 在 `publish_run_metadata` 寫入時刪除舊 `.toml`，審核時改為一次性轉換既有檔案並移除清理邏輯。理由：程式不留過渡邏輯、data/ 與 git 立即一致、publish 不會刪除它沒寫的檔案，也避免「先刪舊檔、新檔寫入失敗」時資料夾沒有任何記錄。代價：不在 git 中、另外 publish 的 data/（如部署機）不會被清理，舊 `.toml` 會與新 `.yml` 並存（程式不讀取，不影響功能）。

### data/ 舊記錄檔轉換

git 追蹤的 9 份舊記錄檔以一次性腳本轉換後刪除原檔：

| 類型 | 檔案 | 轉換方式 |
|---|---|---|
| module_config | `data/rag/{claudecode,ncucsie,nculab}/`、`data/webpages/{ncucsie,nculab}/` | `[init]` 的 `site_id`（rag 另含 `webpages_data_folder_path`）移到最上層，以現行模型 `model_validate` 後由 `save_module_config` 寫出；檔頭 `# source: 轉換自舊版 module_config.toml`，`# run_name_fields` 由原 `# run name` 註解轉換 |
| run_config | `data/rag/{ncucsie,nculab}/`、`data/webpages/{ncucsie,nculab}/` | `dump_yaml` 原樣轉格式；已不存在的欄位（`save_vector_store_to_runs`）與缺少的欄位（`save`）不補不刪，保留當時執行的紀錄 |

驗證：9 份 `.yml` 與 `git show HEAD:<原 .toml>` 比對，module_config 在位置調整後逐欄位相同且可被現行模型讀回，run_config 完全相同。`runs/` 中的舊 `.toml` 為歷史紀錄、程式不讀回，不轉換。

### 驗證

- 轉檔比對：26 份舊 `.toml` 與新 `.yml` 經 extends 展開後的 dict，扣除明寫為 `null` 的可選欄位後**完全相同**，`run_name_fields` 與原 `# run name` 註解解析結果也全部相同；唯一例外為 agent prompt 的 `\\n`，比對前先換算。
- config 快照與 baseline **26 份無差異**，`run_name` 全部相同。
- `check.sh`：257 passed（移除舊檔清理測試後重跑）；實際產生的 `module_config.yml` 檔頭為 `# source: configs/agent/test.yml (extends: default)`，prompt 為 block scalar。
- `grep -rn toml src tests scripts`：只剩 `.toml` 不被接受、`configs/` 無 `.toml` 的測試。

## Phase C：移除 CLI 中介層

### 補充（plan 未明訂）

- `overrides.py`：partial model 不帶約束、不設 strict，只負責收集值，範圍與跨欄位規則在 `from_yaml()` 合併後統一驗證；`overrides_to_dict(model)` ＝ `prune_empty(model_dump(exclude_none=True))`。
- 有套用 overrides 時 `source` 結尾加 ` + overrides`。
- 動態產生的 model 不能當靜態型別，以 `TYPE_CHECKING` 分支讓 pyright 視為 `BaseModel`；`module` 欄位加 docstring 作為 `--help` 說明（tyro 把欄位後的註解當說明，不能用 `# type: ignore`）。
- `run_prepare`：`save = not publish`、`webpages_data_use_latest_results = not publish`；`RAGRegistry.get` 改 `RAGConfig.from_yaml(config_name, {"site_id": site_id})`。
- 測試：新增 `test_overrides.py`（16 個）、`test_cli.py`（12 個，以 mock 攔截 pipeline 函式）；autouse fixture 以 mock 取代 `save_run_config`（run_config 必填後會實際寫檔到 mock RunManager 的假路徑）。

### 與 plan 不同或 plan 未明訂的決定（請審核）

1. **`hybrid_ranker_params` 的 CLI 路徑**：plan 原型寫 `--module.vector-store.weights`，但 Phase A 已把它做成獨立 model，巢狀規則下為 `--module.vector-store.hybrid-ranker-params.weights 1.0 0.3`（與設定檔結構一致）。
2. **`run_server_build(agent, run_config)`**：plan 的 C3 簽名清單沒列；為與「不重複傳遞」一致，一併移除 `host`／`port`／`allowed_origins`，改從 `run_config` 讀取，`run_config` 改必填。
3. **`source` 標示 `+ overrides`**：只看 `module_config.yml` 無法得知有沒有經過 CLI 覆寫。
4. **`agent_build` 目錄也寫 `run_config.yml`**：`run_agent_build` 的 `run_config` 改必填後，`runs/<ts>/agent_build/<config>/` 也會有（原本只有 server 與 agent 目錄有）。
5. **bool 覆寫以值指定**：`--module.init.light-mode False`，而非 `--flag`／`--no-flag`（後者無法表達「未指定」）。
6. **`--help` 顯示 `{None}|INT`**：tyro 會把 `None` 列為可選值，C2 的 K7 處理。

### 驗證

`grep EXPERIMENTS|run_experiment|ExpCLI` 無結果；`check.sh`：290 passed；config 快照與 Phase B **完全相同**；`exp` 已不在子命令清單；過渡狀態 `--module.site-id` 暫時出現在 CLI（依 plan）。

## Phase C2：config class 為預設值基準

### 補充（plan 未明訂）

- `_run_name_fields` 改為 `None` 表示「使用 class 預設」，不經 loader 建立的 config 也有正確的 `run_name`。`source` 在 `default` 無檔案時為 `{Class} 預設值（{path} 不存在）`。
- `prompts.py` 的兩個常數由 `default.yml` 產生並確認逐字相同。
- `overrides.py` 的 `_format_default`：None／bool／list 以 YAML flow 呈現，字串截斷為 60 字並把換行顯示為 `\n`；可選 section 的預設值取自上層的預設實例（`hybrid_ranker_params.weights` 顯示 `[1.0, 0.5]`，而非該 class 自己的 `None`）。
- K6 改必填的建構子清單：`WebsiteCrawler.__init__`、`crawl_website`、`WebpageMarkdownCleaner.__init__`、`ImageSummarizer.__init__`／`summarize_crawl_results_images`、`NodePipelineBuilder.__init__`、`VectorStoreBuilder.build`；pipeline 原本就以 keyword 傳入，呼叫端不需修改。
- `configs/`：各模組 `default.yml` 只留 nculab 站點欄位；刪除 `agent/default.yml`，`agent/test.yml` 改為只有註解。

### 實作中的發現

- **class 預設值不會與設定檔寫的 mapping 逐欄合併**：deep merge 只在設定檔之間進行；設定檔寫 `hybrid_ranker_params: {k: 60}` 時，pydantic 以這個 dict 建立 `HybridRankerParams`，其 `weights` 為該 class 自己的預設 `None`，不會帶入 `VectorStoreConfig` 預設實例的 `[1.0, 0.5]`。因此繼承鏈沒寫 `weights` 時，改用 RRFRanker 只需寫 `{k: 60}`；繼承鏈有寫 `weights` 時才需要 `weights: null`。已更新欄位說明、`configs/README.md`、`cli.md` 並加測試。CLI 只指定 `--module.vector-store.hybrid-ranker RRFRanker` 時仍因預設 `weights` 被跨欄位規則擋下。
- scratchpad 中先前的快照檔已被清除，比對基準改以 `git worktree` 檢出 Phase C 的 commit（`2ccd068`），用同一支快照腳本重新產生。

### 驗證

- class 預設值逐欄位比對：以 Phase C 的 `default.yml` 展開為基準，四個模組「只給站點欄位、其餘用 class 預設」的 `model_dump()` **逐欄位相同**（RAG 扣除由 site_id 推導的路徑），`run_name_fields` 也相同。
- config 快照與 Phase C（`2ccd068`）**完全相同**（26 份，含已無檔案的 `agent/default`）。
- `check.sh`：323 passed；`--help` 顯示 `(default: ...)` 與必填標示，不再有 `{None}|`。

## Phase D：站點分層

### 補充（plan 未明訂）

- `SiteConfig.from_yaml(site_id)`：找不到站點時列出可用站點；site_id 格式錯誤訊息為中文。
- `site` 位置參數的 metavar 設為 `SITE`（tyro 預設顯示 `STR`）。
- `published_target(site_id, data_folder)`（serve 與 rag-query）、`build_target(...)`（rag-build）、`log_target()`（取代 module_config 中的路徑記錄）；`RAGRegistry.get` 的 `base_folder` 現在也決定向量庫位置（原本只用於檢查站點是否存在）。
- `run_prepare` 的 run title 加上站點；`RunManager.site_config_path`，log 表格只在有站點的 run 顯示；`save_site_config()` 放在 `utils/config_helper.py`。
- 順帶刪除 `workflow.md` 中早已不存在的 `override_init_config()` 敘述。
- 測試：新增 `test_site_config.py`（20 個）、`test_run_persistence.py`；`test_pipeline_prepare.py` 以實際 target 位置取代讀 `module_config` 的 `milvus_uri`；`test_serve_rag_loading.py` 新增 repo 內已 publish 的三個向量庫皆能載入。

### 與 plan 不同或 plan 未明訂的決定（請審核）

1. **`RAGTarget` 放在 `ingestion/indexing/index.py`**：plan 寫在 retrieval，但 `IndexBuilder` 需要它，而 index 模組的既有分層不依賴 retrieval。產生 target 的函式仍在 `retrieval/factory.py`。
2. **`build_rag` 不再負責決定位置**：原本依 `run_manager`／`webpages_data_use_latest_results` 改寫 config；現在由呼叫端以 `build_target()` 產生 target 後傳入。
3. **測試站點的查詢問題**：`rag/test_claudecode.yml` 原本的 query「如何設定 hooks 與 MCP 伺服器？」不再保留（測試設定與站點無關，改用站點的 `sample_query`）；`rag/test_ncucsie.yml` 誤用 nculab 問題的問題隨之修正。

### 驗證

- **快照比對**（舊 C2 的 `{module}/{site}`、`test_{site}`、`default`、`test` vs 新「模組設定＋`sites/{site}.yml`」），差異全部符合預期：
  - `max_prompt_tokens` 200000 → 500000（nculab、ncucsie、所有 test 設定；claudecode 本來就是 500000）。
  - `website_crawler/default` 的 run_name `default` → `max_depth-2`、`image_summarizer/default` 的 `default` → `model-gpt-5.6-luna`（S10）；**所有 `{site}` 設定的 run_name 與舊版相同**。
  - `website_crawler/default` 的 `path_prefix` 由未設定 → `/site/nculab`（舊 `default.yml` 是不完整的 nculab 設定，現在 `default`＋nculab 等於舊 `nculab.yml`）。
  - `rag/test_ncucsie`、`rag/test_claudecode` 的 query 改為站點的 `sample_query`。
  - 其餘欄位（含 site_id、url 類欄位、rag 的資料來源與向量庫路徑）全部相同。
- 路徑：`data/{category}/{site_id}/` 與 `runs/<ts>/<module>/<site_id>/<run_name>/` 結構不變。
- `check.sh`：338 passed；`prepare --run.config test`（缺站點）由 tyro 報錯；`run rag-query unknown_site` 報 `Site config not found: configs/sites/unknown_site.yml（可用的站點：claudecode, ncucsie, nculab）`。
- **付費整合測試**（E2，2026-10-01 執行，使用者已確認）：
  - `prepare nculab --run.config test --run.no-publish`：約 3 分鐘；crawler $0.0211、image summarizer $0.0612、rag build 無費用，合計 $0.0823。
  - `uv run pytest tests/integration`（含 cost）：7 passed，386 秒。
  - `run rag-query nculab --run.config test --module.retriever.similarity-top-k 7 --module.query-engine.query-llm-name gpt-5.6-terra`：`module_config.yml` 檔頭為 `# source: configs/rag/test.yml + overrides`，兩個覆寫值正確；run 目錄含 `site_config.yml`、`run_config.yml`，query 取自 `sample_query`。
  - 測試後 `data/rag/nculab/milvus.db/.../indexes/` 出現未追蹤檔案（整合測試載入已 publish 向量庫產生），未納入 commit。

### 收尾（Phase D 後的遺漏檢查）

- `docs/work/todo.md`「模組配置」五項標記完成。
- `docs/code/phase1/modules/{data_collect,data_preprocess,data_retrieve}.md`、`docs/code/phase2_3_mvp/modules/{agent,server}.md` 仍描述 TOML／`from_toml`／`_validate_config`／舊簽名（plan 的文件清單未列這些檔案），已更新；`grep -rn toml docs/code` 無殘留。
- `DEFAULT_CONFIG_NAME`：Phase A 刪除後，C2 的 K3 重新需要這個常數，故保留於 `base_config.py`，僅用於「`default` 無檔案」的判斷。
