# 模組配置重構：實作規劃

> 對應 [todo.md](../../todo.md)「技術債 → 模組配置」。實作紀錄見 [dev.md](./dev.md)。

## Context

module config（`WebsiteCrawlerConfig`／`ImageSummarizerConfig`／`RAGConfig`／`AgentConfig`）原本是「扁平 dataclass＋TOML＋手寫驗證」，累積出四個問題：

1. **site_id 一致性靠檔名慣例**：site_id 在 `configs/{website_crawler,image_summarizer,rag}/` 各寫一次，`prepare --config ncucsie` 能跑對只是因為三個檔名相同；設定檔數量＝站點 × 環境 × 模組（每模組 8 份），多為複製貼上（例：`rag/test_ncucsie.toml` 的 query 仍是 nculab 的問題）。CLI 無法覆寫 site_id。
2. **section 對照與驗證重複維護**：`INIT_KEYS`／`SECTIONS_TO_KEYS` 對照表、四個 config 共約 400 行 `_validate_config`，以及專為 tomlkit 型別補洞的 `_normalize_toml_types`。
3. **run name 依賴 TOML 註解**：`filter_commented_configs` 解析 `# run name` 註解，與檔案格式綁死。
4. **CLI 中介層手動同步**：`pipeline_config.py` 的 `*ModuleConfig` 手動複製模組欄位成 `X | None = None`，另有 `weights → hybrid_ranker_params` 特例；模組新增欄位時需同步修改。

## 討論結論與階段

| # | todo 項目 | 決策 |
|---|---|---|
| 1 | 優化 site_id 參數設定和讀取 | **站點分層**：`configs/sites/` 加獨立 `SiteConfig`（Phase D） |
| 2 | run config 永遠儲存 | 捨棄為獨立項目；Phase C 讓 run_config 成為必填，所有路徑都會記錄 |
| 3 | yml 配置檔 | 改用 YAML（Phase B） |
| 4 | configs 改用 pydantic 驗證 | 採用（Phase A） |
| 5 | config class 引入巢狀 class | 採用，巢狀 class 與 YAML 巢狀 key 一一對應（Phase A） |
| 6 | cli module config 移除中介層 | 採用 **tyro 巢狀參數**，如 `--module.retriever.similarity-top-k 20`（Phase C） |

依 A → B → C → C2 → D 順序執行，**每個 Phase 一個 commit**（不合併）。

| Phase | 內容 | 依賴 |
|---|---|---|
| A | config 模型改為 pydantic＋巢狀 class | — |
| B | 設定檔改為 YAML（含 `extends`） | A |
| C | 移除 CLI 中介層 | A |
| C2 | config class 為預設值基準（C 審核後追加，修訂 V2） | A、B、C |
| D | 站點分層 | A、B、C2 |

**為什麼先 C 再 D**：兩者無相依，但先做 C 可避免改了又刪（先做 D 必須先改 `*ModuleConfig`，之後移除中介層又整個刪掉；先做 C，D 只需在 run config 加 `site`／`query`，module 的 CLI 參數由 partial model 自動跟著改變），且行為變動最大的 D 放最後，付費整合測試只需跑一次。代價是 C 到 D 之間 `site_id` 與 `query_engine.query` 會暫時出現在自動產生的 CLI 參數中，D 完成後自動消失。C2 排在 D 之前：D 會重整設定檔結構，在新的預設值基準上進行可避免設定檔改兩次。

---

## Phase A：config 模型改為 pydantic＋巢狀 class

- **共用基底** `ConfigModel`：`strict=True`、`extra="forbid"`（未知 key 直接報錯，取代原本只 warning 的行為）、`validate_assignment=True`；所有 module config 與巢狀 section 都繼承它。四個 config 依 YAML 結構拆成 section（如 RAG 為 `nodes`／`vector_store`／`index`／`retriever`／`query_engine`）。
- **刪除**：`SECTIONS_TO_KEYS` 等對照表、`_validate_config`、`_normalize_toml_types`、`load_config_from_toml`／`override_config`／`_filter_allowed_config_keys`。
- **run name**：原本每份設定檔各自以 `# run name` 註解決定欄位，不能改成類別層級宣告，否則部分 run_name 與 runs/ 資料夾名稱會改變。Phase A 期間保留註解解析（`filter_commented_configs` 追蹤所在 section，回傳 dotted path 如 `init.max_depth`），run_name 字串仍以**最後一段欄位名**組成（`max_depth-2`）；Phase B 改為頂層 `run_name_fields`。
- `config_name` 改為 pydantic `PrivateAttr`（由 loader 設定、以 property 讀取），不參與驗證與 `model_dump`；`run_name_fields` 比照。
- `log_config` 改為依巢狀 model 逐 section 產表；`save_module_config` 改為 `model_dump()` 後寫檔。
- `hybrid_ranker_params` 改為明確的 model（`weights: list[float] | None`（長度 2）、`k: PositiveInt | None`），順帶消除 CLI 的 `weights` 特例。strict 模式下 YAML 的 list 無法轉 tuple，所以用 `list` 加長度約束。
- 呼叫端改為巢狀存取（如 `config.retriever.similarity_top_k`）；`pyproject.toml` 明確加入 `pydantic`。
- 此 Phase 仍讀 TOML（`tomllib` 讀出 dict 後 `model_validate`），讓模型改寫與格式轉換分開驗證。

### 驗證機制

原本的問題：型別檢查不一致（`ImageSummarizerConfig` 的 `max_retries = "6"` 會通過）；`allowed_domains` 為字串時被逐字元檢查；沒有跨欄位檢查（`chunk_overlap >= chunk_size`、`RRFRanker` 搭配 `weights` 都不報錯）；config 建立後的修改（改寫 `milvus_uri` 等）完全繞過驗證；程式預設值與 `default.toml` 不一致（`cache_download_images`、`vlm_max_workers`、prompt、Agent system prompt）。

| # | 問題 | 決策 |
|---|---|---|
| V1 | 型別嚴格程度 | 先嘗試全面 `strict=True`（已實測巢狀 dict 與 YAML list 可正常載入；lax 會把 `True` 轉成 `1`）。遇到不相容時改在個別欄位用 `StrictInt`／`StrictBool`，並記錄在 dev.md |
| V2 | 預設值的單一來源 | ~~程式不給預設值，`default.yml` 為唯一來源~~ → **Phase C2 修訂**：config class 的欄位預設值為唯一來源，yml 只寫差異 |
| V3 | 跨欄位規則 | 以 `model_validator` 實作，YAML 結構不變 |
| V4 | 建立後的修改 | `validate_assignment=True` |
| V5 | 錯誤訊息與 CI | loader 把 `ValidationError` 包成 `ConfigValidationError` 並附設定檔路徑；新增測試載入 `configs/` 下所有設定檔 |

實作細節：

- **預設值（V2 原版）**：一般欄位不給預設值，缺欄位即報錯；語意為「未設定」的可選欄位保留 `None`（`max_pages`、`seed`、`path_prefix`、`webpages_data_folder_path`、`milvus_uri`、`hybrid_ranker_params`），`litellm_kwargs` 保留空 dict。刪除 `DEFAULT_PROMPT`、`DEFAULT_SYSTEM_PROMPT`、`DEFAULT_LLM_NAME` 等常數；`ImageSummarizer.summarize_crawl_results_images` 的 `prompt`、`model` 改為必填，移除與 config 不一致的隱藏預設 `model="gemini-3-flash-preview"`。Phase A 尚無 extends，所有 toml 都是完整複製，需以**現行程式預設值**補齊缺少的必填欄位（如 rag 的 `alpha`、`cutoff`），確保載入結果不變。
- **單欄位約束**：優先用型別與 `Field`（`PositiveInt`、`Literal`、`Field(ge=, le=)`）；非空字串用共用型別 `NonEmptyStr`。
- **型別簡化**：`url_patterns` 由 `str | Pattern | list` 改為 `list[str]`，`allowed_domains` 改為 `list[NonEmptyStr]`（YAML 無法產生 `Pattern`；統一成 list 也修正逐字元檢查的 bug）。
- **跨欄位規則**：`NodesConfig` 要求 `chunk_overlap < chunk_size`；`VectorStoreConfig` 要求 `WeightedRanker` 有 `weights` 無 `k`、`RRFRanker` 有 `k` 無 `weights`。
- **錯誤訊息**：包含設定檔路徑與欄位路徑（如 `configs/rag/test.yml: retriever.similarity_top_k: Input should be greater than 0`）；pydantic 內建約束沿用英文，自訂 validator 用中文。
- **不在驗證範圍**：API key 是否存在、模型名稱是否有效，依賴執行環境，維持在執行時檢查。

---

## Phase B：設定檔改為 YAML

| # | 問題 | 決策 |
|---|---|---|
| B1 | 副檔名 | 統一 `.yml`，loader 只接受 `.yml` |
| B2 | PyYAML 的 YAML 1.1 陷阱 | 依賴 strict 模式攔截，並在 `configs/README.md` 寫撰寫注意事項；不換 ruamel.yaml、不自訂 loader |
| B3 | 存檔格式 | 自訂 dumper；存 extends 展開後的完整 config；`None` 輸出為 `null`；檔頭註解記錄來源 |
| B4 | `extends` 語意 | 見下 |
| B5 | `generated_exclude_words.toml` | 刪除（`exclude_words` 已不是 config 欄位，詞彙已完整記錄在 `exclude_words_report.json`） |
| B6 | 轉換方式 | 一次性腳本轉檔後手動整理；移除 `tomlkit` |

**載入流程**：`configs/{module}/{name}.yml` → `yaml.safe_load`（逐層處理 extends）→ deep merge 成單一 dict → 取出保留 key → `Config.model_validate(dict)`。

### `extends` 設計

- **語法與範圍**：檔案最上層寫 `extends: <設定名>`，單一字串（單一繼承），不含副檔名；只能繼承同資料夾的設定。
- **多層繼承**：深度不限；以已走訪清單偵測循環，錯誤訊息列出完整鏈（`a → b → a`）；找不到被繼承的檔案時報錯並列出繼承鏈。
- **合併規則**（子疊在父上）：兩邊都是 dict 則遞迴合併；其他情況（list、純量、`null`、型別不同）子檔的值整個取代父檔的值。
- **清除值**：寫 `key: null`。可選欄位變成「未設定」，必填欄位則驗證失敗。dict 是遞迴合併，子檔寫 `key: {}` **不會**清空父檔的 dict；要移除其中的 key 需明確寫該 key 為 `null`（例：父檔用 `WeightedRanker`，子檔改 `RRFRanker` 時需寫 `weights: null`，否則合併後同時有 `weights` 與 `k`，被跨欄位規則擋下）。
- **只驗證最終結果**：各層原始 dict 不個別驗證，合併完成後 `model_validate` 一次。
- **保留 key**（只在最上層有效）：`extends`（處理後移除，不繼承）；`run_name_fields`（dotted path 的 list，如 `[init.max_pages]`，和一般欄位一樣繼承、子檔寫了就整個取代；可省略，run_name 字串以最後一段欄位名組成）。其他層級出現同名 key 視為一般欄位，被 `extra="forbid"` 擋下。
- **錯誤訊息**：包含實際載入的檔案與繼承鏈，如 `configs/rag/test.yml (extends: default): retriever.similarity_top_k: ...`。
- **與 CLI overrides 的關係**（Phase C）：沿用同一個 deep merge，優先順序父檔 < 子檔 < CLI overrides，最後統一驗證一次。
- **存檔**：runs/ 與 data/ 的 `module_config.yml` 存展開後的完整 config，不含 `extends`；附加資訊（`# source:`、`# run_name_fields:`）只寫在檔頭註解。往返測試只比對設定內容。

Phase B 期間仍保留站點組合檔（D 才刪除），改用 extends 減少重複：`test_{site}.yml` extends `{site}.yml`。

### 其他變更

- **撰寫注意事項（B2）**：PyYAML 採 YAML 1.1，`1e-3` 會解析為字串（要寫 `1.0e-3`）、`on/yes/no` 會變 bool、`2026-09-30` 會變 date；strict 模式會把這些報為型別錯誤。
- **自訂 dumper（B3）**：多行字串輸出為 `|` block scalar、`allow_unicode=True`、`sort_keys=False`；`run_config.yml` 也用同一個 dumper。
- 多行 prompt 用 `|` block scalar。注意原 `configs/agent/*.toml` 的 system prompt 寫成 `"\\n"`，TOML 解析後是字面上的反斜線加 n；改用 block scalar 後變成真正的換行，**送給 LLM 的 prompt 內容會改變**（應屬修正）。
- **轉換（B6）**：一次性腳本以 `tomllib` 讀取、自訂 dumper 輸出；再手動改用 extends、補回遺失的註解、把 `# run name` 註解改為 `run_name_fields`。
- **輸出路徑**：runs/ 與 data/ 的 `module_config`／`run_config` 改 `.yml`；`RunManager` 路徑欄位改名（`module_config_toml_path` → `module_config_path`）。
- **`data/` 既有舊 `.toml` 記錄檔**：~~不轉換，`publish_run_metadata` 寫入時刪除舊檔~~ → 實作時改為一次性轉換為 `.yml` 並刪除原檔，不加清理邏輯（理由見 dev.md）。
- 相依套件：加入 `pyyaml`，移除 `tomlkit`。

---

## Phase C：移除 CLI 中介層

目標用法：`website-copilot run rag-query --run.config test --module.retriever.similarity-top-k 20`。

**原型實測**（tyro 1.0.13、pydantic 2.12.5）：巢狀參數名稱、`Literal`（自動變選項清單）、list、欄位說明（可從 `Field(description=...)` 帶入 `--help`）皆符合預期；`dict[str, Any]`（`litellm_kwargs`）會產生異常子命令或報錯，**必須從 CLI 排除**；`--module.x.max-pages None` 被視為「未指定」，CLI 無法把欄位設為 null；未指定的 section 會留下空 `{}`，需清除。

| # | 問題 | 決策 |
|---|---|---|
| C1 | partial model 產生規則 | 巢狀 section → 巢狀 partial model（以預設實例作為預設值，避免 tyro 把 `Model \| None` 變成子命令）；葉欄位 `X \| None = None`；排除 `dict[str, Any]` 欄位；複製 `Field` 說明；清除空 section；接受「CLI 無法設為 null」的限制（需要時另寫 extends 設定檔） |
| C2 | pipeline 接收覆寫值的形式 | 只接受巢狀 dict：`overrides={"query_engine": {"query": q}}` |
| C3 | run config 的傳遞 | pipeline 函式只接收 `run_config`（必填）＋ `overrides`，移除展開的 run 參數 |
| C4 | `exp` 實驗 | 8 個實驗全部刪除（引用的設定檔皆已不存在，結果已記錄在 `docs/exp/memo/`） |
| C5 | `--run.config-name` 改名 `--run.config`（追加） | 只改 CLI 參數名稱，Python 屬性維持 `config_name`（與 `BaseModuleConfig.config_name` 一致，且 `run_config.config` 易被誤讀為 config 物件）；放在 Phase C 是因為 C3 已改寫所有 RunConfig 使用端與 CLI，一次改完 |

### 變更範圍

- **partial model（C1）**：新增 `config/overrides.py`，`make_overrides_model(model)` 以 `pydantic.create_model` 遞迴產生 `{Model}Overrides`，另提供 `prune_empty(dict)`；Phase A 為不易理解的欄位補 `Field(description=...)`。
- **CLI**：`cli/run.py` 的 `module` 欄位改為自動產生的 overrides model；刪除 `pipeline_config.py` 下半部的 `*ModuleConfig`、overrides 轉換迴圈（含 `weights` 特例）與 `run_kwargs` 的 `pop`；各分支簡化為一行呼叫。
- **config 載入（C2）**：`from_yaml(config_name, overrides=None)`，overrides 以同一個 deep merge 疊在 extends 展開結果上，最後驗證一次。
- **pipeline 簽名（C3）**：`run_website_crawler`／`run_image_summarizer`／`run_rag_build`／`run_rag_query`／`run_agent_query`／`run_agent_build` 皆為 `(run_config, overrides=None, ...)`，`run_prepare(run_config)`；`config_name`、`save`、`publish`、`run_name_use_config_name` 等一律從 `run_config` 讀取。`PrepareRunConfig` 新增 `publish: bool = True`（CLI 用 `--run.no-publish` 只寫 runs/），`run_prepare` 依此決定 `save = not publish`，並以同一個 `config_name` 建立三個階段的 RunConfig；`serve` 同理。run config 不再選填，所有路徑都會記錄，publish 到 data/ 的檔案因此多出 `run_config.yml`。`build_rag` 的 `**config_overrides` 改為 `overrides` 參數。
- **刪除 exp（C4）**：刪除 `exp` 子命令與 `pipelines/exp.py` 的 8 個實驗函式；`pipelines/exp.py` 保留 `run_rag_query`／`run_agent_query`。
- **改名（C5）**：所有 RunConfig 的 `config_name` 以 `tyro.conf.arg(name="config")` 標註；README、`docs/code/**` 的 `--run.config-name` 一併更新（`docs/work/`、`docs/progress_report/` 為歷史紀錄，不改）。
- **過渡狀態**：`site_id` 與 `query_engine.query` 暫時出現在 CLI（`--module.site-id`），Phase D 後消失。

---

## Phase C2：config class 為預設值基準

**背景**：Phase C 審核時比較「`default.yml` 為唯一預設值基準」（V2）與「config class 為唯一預設值基準」，決定採後者：型別與值寫在一起（IDE／pyright／`--help` 直接可見）；不依賴 yml 也能建立 config（程式與測試可直接 `RetrieverConfig()`，未來打包成套件不需隨附 `configs/`）。**代價（已接受）**：調整基準值需改程式碼；長 prompt 回到 Python 常數；只看 yml 無法得知完整設定值（以 `module_config.yml` 與 `--help` 補足）；設定檔漏寫欄位時改為使用預設值，不再報錯（拼錯欄位名稱仍由 `extra="forbid"` 擋下）。

| # | 問題 | 決策 |
|---|---|---|
| K1 | 預設值來源 | config class 欄位預設值為唯一來源（修訂 V2）；yml 只寫與預設值不同的部分 |
| K2 | 必填欄位 | 站點欄位不以 nculab 的值當預設：`site_id`、`crawl.url`、`query_engine.query` 在 Phase D 前維持必填，`crawl` 的 `url_patterns`／`allowed_domains`／`path_prefix` 維持 `None` 預設，nculab 的值留在 `default.yml`；其餘參數欄位皆有預設值，值等於 Phase C 的 `default.yml` |
| K3 | 設定名稱 `default` | `default.yml` 可省略：`from_yaml("default")` 在檔案不存在時等於 class 預設值；其他名稱仍須有檔案。此例外只適用於直接載入 `default`，`extends: default` 指向不存在的檔案照舊報錯 |
| K4 | `run_name_fields` 預設 | 改為 class 層級的 `_DEFAULT_RUN_NAME_FIELDS`（ClassVar）；yml 有寫就整個取代（含寫 `[]` 明確清空），沒寫時用 class 預設 |
| K5 | 長 prompt | 移到 `config/prompts.py`，config class 引用常數 |
| K6 | 模組建構子的預設值 | 一併移除，避免第三套預設值：建構子維持個別參數（不改收 config 物件，ingestion 模組不依賴 config 套件），與 config 對應的參數一律必填；「未設定」語意的參數（`crawl_website` 的 `url_patterns` 等）必填但可傳 `None`；`WebsiteCrawler` 的 `cleaner` 改必填；不在 config 中的內部參數（如 `max_low_occ_ratio`）保留預設 |
| K7 | `--help` 顯示 | 葉欄位以 `help_behavior_hint` 顯示 class 預設值 `(default: X)`（長字串截斷），必填欄位標示「必填，來自設定檔」；`--module` 說明註明「設定檔的值優先於此預設」；以 `metavar` 去除 `{None}\|` 前綴 |
| K8 | 預設值本身的驗證 | `ConfigModel` 開啟 `validate_default=True`（含跨欄位規則），另以單元測試確認各 config 的 class 預設值有效 |

**變更範圍**：四個 `*_config.py` 的欄位加預設值（section 改 `default_factory`；`hybrid_ranker_params` 預設 `weights=[1.0, 0.5]`）；`load_config_dict` 在名稱為 `default` 且檔案不存在時回傳空 dict；各模組 `default.yml` 刪除模組參數、只留站點欄位，`agent/default.yml` 刪除；模組建構子依 K6 改必填；`make_overrides_model` 從欄位預設值產生 help hint 與 metavar；文件同步。

---

## Phase D：站點分層

### 現況分析

真正因站點而異的欄位只有：website_crawler 的 `site_id`、`url`、`url_patterns`、`allowed_domains`、`path_prefix`（claudecode 另有 `max_prompt_tokens = 500000`）；image_summarizer 的 `site_id`；rag 的 `site_id`、`query`。其餘與 default 相同。`default.toml` 實際就是 nculab 的設定，`test.toml` 與 default 的差異只有 `max_pages = 40`（環境差異，與站點無關）。

### 設計

**站點身分與模組參數分離**：新增獨立的 `SiteConfig`，模組 config 不再包含任何站點資訊。

- `configs/sites/{nculab,ncucsie,claudecode}.yml`：`site_id`、`sample_query`、`crawl`（`url`、`url_patterns`、`allowed_domains`、`path_prefix`，後三者可省略）。
- 模組參數預設值在 config class（C2），各模組不再需要 `default.yml`：`--run.config default` 等於 class 預設值。
- 刪除所有 `{site}.yml`、`test_{site}.yml` 與各模組 `default.yml`；`website_crawler/test.yml` 只剩 `run_name_fields: [init.max_pages]` 與 `init.max_pages: 40`；`image_summarizer/test.yml`、`rag/test.yml` 只有註解；`agent/test.yml` 不變（agent 為多站）。

### 決策

| # | 問題 | 決策 |
|---|---|---|
| S1 | 站點檔如何接入程式 | 獨立的 `SiteConfig`；pipeline 依 `run_config.site` 自行載入，不另外傳參數 |
| S2 | 站點特有的模組參數（claudecode 的 `max_prompt_tokens`） | 直接把 class 預設值提高到 `500000`，站點檔不提供模組覆寫 |
| S3 | RAG 的 `query` | 從 `RAGConfig` 移到 `RAGQueryRunConfig`；未指定時使用 `site.sample_query` |
| S4 | 未提供站點 | 必填，不設預設值（避免誤將錯誤站點 publish 到 data/） |
| S5 | RAG 內部如何取得 site_id 與路徑 | 新增執行期物件 `RAGTarget(site_id, webpages_dir, milvus_uri)`，由 factory 依站點與執行模式產生；`RAGConfig` 移除路徑欄位 |
| S6 | site_id 規則 | 格式 `^[A-Za-z_][A-Za-z0-9_]*$`（Milvus collection 名稱與路徑皆可用）；保留欄位並檢查必須與檔名一致 |
| S7 | image-summarizer 讀到其他站點的爬蟲結果（既有 bug） | `load_latest_results` 加 `site_id` 過濾；找不到該站點結果時報錯，不退回其他站點 |
| S8 | 站點在 CLI 的形式 | 位置參數：`website-copilot prepare ncucsie --run.config test`（已實測 tyro `Positional` 可行） |
| S9 | 站點顯示名稱／描述 | 不納入本次重構，列入 todo「功能進度」 |
| S10 | prepare 的 run 資料夾名稱 | 舊站點檔的 run name 欄位搬進 class 的 `_DEFAULT_RUN_NAME_FIELDS`：crawler `[init.max_depth]`、image_summarizer `[summarize.model]`（rag 原本即為 `[vector_store.vector_store_type]`），使 `prepare {site}` 的 run 名稱與原本相同 |

**S5–S7 的依據**：site_id 不只用在路徑，`IndexBuilder` 以它作為 **Milvus collection 名稱**並寫入 node metadata，已 publish 的向量庫以 site_id 為 collection 名稱；`run_image_summarizer` 未傳入爬蟲結果時 `load_latest_results` **不分站點**，單獨對 ncucsie 執行時若最近一次爬的是 nculab 會拿到 nculab 的資料；`milvus_uri`／`webpages_data_folder_path` 在 4 處被改寫，本質是「站點 × 執行模式」決定的執行期值，而非可調參數。

### 變更範圍

- **config 模型**：新增 `config/site_config.py`（`SiteConfig`、`SiteCrawlConfig`，`from_yaml(site_id)`，共用 YAML loader，不是 `BaseModuleConfig`）；三個模組 config 移除 `site_id`，crawler 移除 `crawl` 區塊；`RAGConfig` 移除 `query_engine.query`、`webpages_data_folder_path`、`milvus_uri` 與路徑推導；`CleanConfig.max_prompt_tokens` 預設改 `500000`。
- **run config／CLI**：`BaseRunConfig`、`PrepareRunConfig` 新增必填位置參數 `site`；`RAGQueryRunConfig` 新增 `query: str | None`；`AgentRunConfig`／`ServeRunConfig` 不加 site。用法如 `prepare ncucsie --run.config test`、`run rag-query ncucsie --run.config test --run.query "介紹資工系課程"`；`--module.site-id`、`--module.query-engine.query` 隨欄位移除消失。
- **pipelines**：簽名不變，內部以 `SiteConfig.from_yaml(run_config.site)` 載入站點；`run_prepare` 以同一個 `run_config.site` 建立三個階段的 RunConfig 以保證 site 一致；`run_rag_query` 的 query 取 `run_config.query or site.sample_query`，兩者皆無時報錯；`run_image_summarizer` 只讀同站點的最新結果（S7）。
- **storage**：`load_latest_results` 新增 `site_id` 參數；`create_run_context` 改收 `site_id`；`publish_run_metadata` 與 runs/ 落盤多存一份 `site_config.yml`，讓 data/ 的紀錄可重現。
- **retrieval（S5）**：`factory` 依執行模式產生 `RAGTarget`：資料來源預設 `data/webpages/{site_id}`，`webpages_data_use_latest_results` 時為 runs/ 中同站點最新的 image_summarizer 結果；向量庫 `save=True` 為該 run 的 `results/milvus.db`，只 publish 時為 `data/rag/{site_id}/.staging-*`，兩者皆否為系統暫存資料夾，serve 載入時為 `data/rag/{site_id}/milvus.db`。`IndexBuilder`、`build_rag`、`load_rag` 改收 `RAGTarget`，原本改寫 config 的 4 處全部移除；`RAGRegistry.get(site_id)` 以 `RAGConfig.from_yaml(config_name)` 加上 serve 用的 target 載入，不需讀站點檔。`module_config.yml` 不再記錄 `milvus_uri`，唯一不固定的「latest results」來源路徑改寫入 log。
- 文件：README 與 `docs/code/runs/config.md` 更新 CLI 用法與設定檔結構。

---

## 已確認決策

| # | 問題 | 決策 |
|---|---|---|
| Q1 | Phase 是否合併 | 不合併；每個 Phase 一個 commit |
| Q2 | YAML 轉 config 的套件 | PyYAML＋pydantic `model_validate` |
| Q3 | 未知 key 的處理 | 改為報錯（`extra="forbid"`） |
| Q4 | `data/` 下已 publish 的舊 `.toml` 記錄檔 | ~~寫入新 `.yml` 時刪除舊 `.toml`~~ → Phase B 審核時改為一次性轉換為 `.yml` 並刪除原檔，publish 不做清理 |
| Q5 | `exp.py` 引用不存在的 config | 8 個實驗全部刪除，連同 `exp` 子命令（Phase C） |
| Q6 | 執行順序 | A → B → C → C2 → D |
| E1 | 快照比對工具是否進版控 | 一次性腳本放 scratchpad，結果貼進 dev.md |
| E2 | 付費整合測試時機 | 最後一個 Phase（D）完成後執行一次 |
| E3 | 付費測試由誰執行 | Claude 執行，每次執行前先確認 |

---

## 驗證

**共同關卡**（每個 commit 都必須通過）同 [code_cleanup plan 的共同關卡](../2026_1001-code_cleanup/plan.md)：`scripts/check.sh`、`tests/integration -m "not cost"`、CLI 冒煙。本重構另有：Phase A、B 需檢查 `exp --help`（Phase C 起 `exp` 子命令移除）；結果記錄在各 Phase 的 `dev.md`。

### config 快照比對

- **動工前**：以當時的程式載入所有模組 × 所有 config 名稱，輸出正規化 JSON（全部欄位值＋`run_name`）作為 baseline。
- **每個 Phase 後**：以新程式產生同格式快照（巢狀展平）與 baseline 比對。預期差異事先列出，清單外的差異一律視為 bug。
- `run_name` 必須一併比對：它決定 runs/ 資料夾名稱，影響人工比對不同 run 的可讀性。
- 比對腳本為一次性工具，放在 scratchpad，結果（含預期差異的確認）貼進各 Phase 的 `dev.md`。

| Phase | 預期差異 |
|---|---|
| A | 無。toml 已寫的欄位本來就優先於程式預設值；缺漏欄位以現行程式預設值補齊；僅型別正規化 |
| B | 無（extends 解析後應與 TOML 完全相同）；唯一例外為 agent prompt 的 `\n`，比對前先換算 |
| C | 無（config 結構不變，只改 CLI） |
| C2 | 無（預設值由 `default.yml` 移到 config class，載入結果應完全相同） |
| D | `site_id` 與 url 類欄位移到 `SiteConfig`；`query` 移到 run config；`milvus_uri`／`webpages_data_folder_path` 移到 `RAGTarget`；nculab／ncucsie 的 `max_prompt_tokens` 由 200000 變為 500000；`default` 設定本身的 run_name 由 `default` 變為 `max_depth-2`（crawler）／`model-gpt-5.6-luna`（image_summarizer），而「站點＋default」的 run_name 與舊 `{site}.toml` 相同（S10） |

### 各 Phase 額外檢查

- **Phase A**：`test_configs.py` parametrize 載入所有設定檔；反例測試涵蓋 bool 放 int 欄位、字串數字、未知 key、跨欄位規則、`validate_assignment`、錯誤訊息含設定檔路徑；`save_module_config` 輸出與舊版比對 section 結構。
- **Phase B**：每份舊 `.toml` 的 dict 與新 `.yml` 經 extends 解析後完全相同；extends 單元測試（多層繼承、循環、找不到父檔、list 取代、`null` 清除、`{}` 不清空 dict、`run_name_fields` 繼承與取代、非頂層保留 key 被拒）；往返測試（config → `module_config.yml` → 讀回，`model_dump` 相等）；data/ 舊記錄檔轉換後內容相同且可被現行模型讀回；`grep -rn toml src tests scripts` 無遺漏。
- **Phase C**：override 測試（巢狀參數正確寫入、未指定欄位不被 `None` 覆蓋、型別錯誤被擋下）；CLI → pipeline 的 override 傳遞以 mock 驗證；partial model 測試（巢狀結構、`dict` 欄位被排除、說明被帶入、空 section 被清除）；`run_prepare` 以 mock 確認各階段 RunConfig；`exp` 移除後 `grep -rn "EXPERIMENTS\|run_experiment\|ExpCLI"` 無結果。
- **Phase D**：快照比對（每個站點 × 模組的「`sites/{site}.yml`＋class 預設值」等於舊 `{site}.toml`，扣除預期差異）；路徑不變；未提供站點時 CLI 報錯、site_id 格式不符或與檔名不一致時報錯；`RAGTarget` 各執行模式路徑正確且 config 不再被改寫；image-summarizer 只讀同站點結果；`run_prepare` 三階段 `site` 相同；`RAGRegistry` 仍能載入現有 `data/rag/*`；過渡期的 `--module.site-id` 已消失。

### 付費整合測試

Phase D 完成後執行一次，由 Claude 執行、每次執行前先向使用者確認，結果與花費記錄在 `dev.md`：

- `website-copilot prepare nculab --run.config test --run.no-publish`（只寫 runs/，`max_pages=40`）。
- `uv run pytest tests/integration`（含 cost）。
- `website-copilot run rag-query nculab --run.config test` 加巢狀 override，確認寫入 `module_config.yml` 的值正確（涵蓋 Phase C 的實際執行）。
