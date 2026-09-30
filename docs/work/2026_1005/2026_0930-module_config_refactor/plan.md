# 模組配置重構 plan

> 對應 [todo.md](../../todo.md)「技術債 → 模組配置」

## Context

目前 module config（`WebsiteCrawlerConfig`／`ImageSummarizerConfig`／`RAGConfig`／`AgentConfig`）是「扁平 dataclass + TOML + 手寫驗證」的組合，累積出以下問題：

1. **site_id 一致性靠檔名慣例**：site_id 在 `configs/{website_crawler,image_summarizer,rag}/` 各寫一次，`prepare --config ncucsie` 能跑對只是因為三個檔名相同；設定檔數量＝站點 × 環境 × 模組（每模組 8 份），多為複製貼上（例：`rag/test_ncucsie.toml` 的 query 仍是 nculab 的問題）。CLI 無法覆寫 site_id；`BaseModuleConfig` 未宣告 site_id，`run_context.py` 需另行處理型別。
2. **section 對照與驗證重複維護**：`INIT_KEYS`／`SECTIONS_TO_KEYS` 等對照表、四個 config 共約 400 行 `_validate_config`，以及專為 tomlkit 型別補洞的 `_normalize_toml_types`。
3. **run name 依賴 TOML 註解**：`filter_commented_configs` 解析 `# run name` 註解決定 run name，與檔案格式綁死。
4. **CLI 中介層手動同步**：`pipeline_config.py` 的 `*ModuleConfig` 手動複製模組欄位成 `X | None = None`；`cli/run.py` 另有 `weights → hybrid_ranker_params` 特例。模組新增欄位時需同步修改，否則 CLI 無法覆寫。

## 討論結論

| # | todo 項目 | 決策 |
|---|---|---|
| 1 | 優化 site_id 參數設定和讀取 | 採用**站點分層**（`configs/sites/` + 獨立 `SiteConfig`，見 Phase D） |
| 2 | run config 永遠儲存 | **捨棄**獨立項目（先前重構後已不需要）；Phase C 的 C3 讓 run_config 成為必填，實際上所有路徑都會記錄 run config |
| 3 | yml 配置檔 | **改用 YAML**：有套件可直接將設定檔轉成 dataclass／model（見 Phase B） |
| 4 | configs 改用 pydantic 參數驗證 | 採用（見 Phase A） |
| 5 | config class 引入巢狀 class 分類 | 採用，巢狀 class 與 YAML 的巢狀 key 一一對應（見 Phase A） |
| 6 | cli module config 移除中介層 | 採用 **tyro 巢狀參數**（`--module.retriever.similarity-top-k 20`，見 Phase C） |

## 實作階段

依 A → B → C → D 順序執行，每個 Phase 的變更為一個 commit。

| Phase | 內容 | 依賴 |
|---|---|---|
| A | config 模型改為 pydantic + 巢狀 class | — |
| B | 設定檔改為 YAML（含 `extends`） | A |
| C | 移除 CLI 中介層 | A |
| D | 站點分層 | A、B |

### 執行順序說明

C（CLI）與 D（站點分層）彼此無相依，兩種順序技術上都可行。選擇先做 C 的理由：

- **避免改了又刪**：若先做站點分層，必須先修改 `pipeline_config.py` 的 `*ModuleConfig`（如從 `RAGModuleConfig` 移除 `query`），之後移除中介層時又整個刪掉。先做 C，D 只需在 run config 加 `site`／`query`，module 的 CLI 參數由 partial model 自動跟著改變。
- **付費整合測試只跑一次**：行為變動最大的站點分層放最後，D 完成後跑一次即涵蓋 C 與 D。

代價：C 到 D 之間，`site_id` 與 `query_engine.query` 會暫時出現在自動產生的 CLI 參數中（如 `--module.site-id`），D 完成後自動消失。

### Phase A：config 模型改為 pydantic + 巢狀 class（todo 4、5）

目標結構（以 RAG 為例）：

```python
class ConfigModel(BaseModel):
    """所有 config（含巢狀 section）的共用基底。"""
    model_config = ConfigDict(strict=True, extra="forbid", validate_assignment=True)

class NodesConfig(ConfigModel):
    chunk_size: PositiveInt
    chunk_overlap: PositiveInt
    paragraph_separator: str

    @model_validator(mode="after")
    def _check_overlap(self) -> Self:
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap 必須小於 chunk_size")
        return self

class RetrieverConfig(ConfigModel):
    query_mode: Literal["hybrid", "default"]
    similarity_top_k: PositiveInt
    hybrid_top_k: PositiveInt
    alpha: float = Field(ge=0, le=1)

class RAGConfig(BaseModuleConfig):
    site_id: str  # Phase D 移除，改由 SiteConfig 提供
    nodes: NodesConfig
    vector_store: VectorStoreConfig
    index: IndexConfig
    retriever: RetrieverConfig
    query_engine: QueryEngineConfig
```

- 驗證規則見下方「驗證機制」。
- 刪除：`SECTIONS_TO_KEYS` 等對照表、`_validate_config`、`_normalize_toml_types`、`load_config_from_toml`／`override_config`／`_filter_allowed_config_keys`。
- run name：現況是**每份設定檔各自**以 `# run name` 註解決定欄位（如 `website_crawler/default` 無、`ncucsie` 為 `max_depth`、`test` 為 `max_pages`），不能改成類別層級的宣告，否則部分 run_name 與 runs/ 資料夾名稱會改變。
  - Phase A 期間保留註解解析：`filter_commented_configs` 追蹤目前所在的 `[section]`，回傳 dotted path（如 `init.max_depth`），以便從巢狀模型取值。
  - run_name 字串仍以**最後一段欄位名**組成（`max_depth-2`，而非 `init.max_depth-2`），與現行完全相同。
  - Phase B 改為 YAML 頂層保留 key `run_name_fields`。
- `config_name` 由 dataclass 欄位改為 pydantic `PrivateAttr`（由 loader 設定、以 property 讀取），不參與驗證與 `model_dump`；Phase B 的 `run_name_fields` 比照處理。
- `log_config` 改為依巢狀 model 逐 section 產表；`save_module_config` 改為 `model_dump()` 後寫檔。
- `hybrid_ranker_params` 改為明確的 model（`weights: list[float] | None`（長度 2）、`k: PositiveInt | None`），順帶消除 CLI 的 `weights` 特例。strict 模式下 YAML 的 list 無法轉成 tuple，因此用 `list` 加長度約束。
- 呼叫端 `config.similarity_top_k` → `config.retriever.similarity_top_k`，影響範圍：`pipelines/{prepare,exp,serve}.py`、`retrieval/factory.py`、`ingestion/indexing/index.py`、`ingestion/augmentation/image_summarizer.py`、`agent/agent.py`、`storage/{run_context,run_manager,data_manager}.py` 與對應 tests。
- `pyproject.toml` 明確加入 `pydantic`（目前經 fastapi／langchain 間接安裝）。

> 此 Phase 仍讀 TOML（`tomllib` 讀出 dict 後 `model_validate`），讓模型改寫與格式轉換分開驗證。

#### 驗證機制

現況問題：

- 型別檢查不一致：`WebsiteCrawlerConfig` 會排除 bool，`ImageSummarizerConfig` 的 `cache_*`／`max_retries`／`download_timeout` 完全沒檢查型別（例：`max_retries = "6"` 會通過）。
- `allowed_domains` 為字串時會被逐字元檢查，驗證形同無效。
- 沒有跨欄位檢查（`chunk_overlap >= chunk_size`、`RRFRanker` 搭配 `weights` 都不會報錯）。
- config 建立後的修改（`factory.py:119,127`、`prepare.py:288,324` 改寫 `milvus_uri`／`webpages_data_folder_path`）完全繞過驗證。
- 程式預設值與 `default.toml` 不一致：`cache_download_images`（`False` vs `true`）、`vlm_max_workers`（10 vs 20）、圖片摘要 prompt（頁面關聯 20 字 vs 40 字）、Agent system prompt 內容不同。

決策：

| # | 問題 | 決策 |
|---|---|---|
| V1 | 型別嚴格程度 | 先嘗試全面採用 `strict=True`（已實測：巢狀 dict 與 YAML list 在 strict 下可正常載入；lax 模式會把 `True` 轉成 `1`）。若遇到無法相容的情況（如 tyro 產生的值、YAML 的日期型別），改為在個別欄位使用 `StrictInt`／`StrictBool` 等，並記錄在 dev.md |
| V2 | 預設值的單一來源 | 程式不給預設值，`default.yml` 為唯一來源；其他設定檔以 `extends: default` 繼承（見 Phase B） |
| V3 | 跨欄位規則 | 以 `model_validator` 實作，YAML 結構不變 |
| V4 | 建立後的修改 | `validate_assignment=True`，修改時重新驗證 |
| V5 | 錯誤訊息與 CI | loader 將 `ValidationError` 包成 `ConfigValidationError` 並附上設定檔路徑；新增測試載入 `configs/` 下所有設定檔 |

實作細節：

- **共用基底**：`ConfigModel` 設定 `strict=True`、`extra="forbid"`（未知 key 直接報錯，取代目前只 warning 的行為）、`validate_assignment=True`；所有 module config 與巢狀 section 都繼承它。
- **預設值（V2）**
  - 一般欄位不給預設值，設定檔缺欄位即報錯。
  - 語意為「未設定」的可選欄位保留 `None` 預設（`max_pages`、`seed`、`path_prefix`、`webpages_data_folder_path`、`milvus_uri`、`hybrid_ranker_params`），`litellm_kwargs` 保留空 dict 預設。
  - 刪除 `DEFAULT_PROMPT`、`DEFAULT_SYSTEM_PROMPT`、`DEFAULT_LLM_NAME` 等 Python 常數，以 `default` 設定檔的值為準。
  - `DEFAULT_PROMPT` 目前也是 `ImageSummarizer.summarize_crawl_results_images`（`image_summarizer.py:85`）的參數預設值；該函式的 `prompt`、`model` 改為必填，同時移除與 config 不一致的隱藏預設 `model="gemini-3-flash-preview"`。
  - Phase A 尚無 extends，**所有** toml（不只 default）都是完整複製，必須以**現行程式預設值**補齊目前缺少的必填欄位（如 rag 的 `alpha`、`cutoff`），確保載入結果不變；`extends` 在 Phase B 實作。
- **單欄位約束**：優先用型別與 `Field`（`PositiveInt`、`NonNegativeInt`、`Literal`、`Field(ge=, le=, gt=)`、`min_length`）。非空字串用共用型別 `NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]`。
- **型別簡化**：`url_patterns` 由 `str | Pattern | list[...]` 改為 `list[str]`，`allowed_domains` 由 `str | list[str]` 改為 `list[NonEmptyStr]`（YAML 無法產生 `Pattern`；統一成 list 也修正逐字元檢查的 bug）。
- **跨欄位規則（V3）**
  - `NodesConfig`：`chunk_overlap < chunk_size`。
  - `VectorStoreConfig`：`WeightedRanker` 必須有 `weights` 且不可有 `k`；`RRFRanker` 必須有 `k` 且不可有 `weights`。
- **錯誤訊息（V5）**
  - loader 捕捉 `ValidationError`，轉成 `ConfigValidationError`，訊息包含設定檔路徑與 pydantic 的欄位路徑（如 `configs/rag/test.yml: retriever.similarity_top_k: Input should be greater than 0`）。
  - pydantic 內建約束沿用英文訊息；自訂 validator（跨欄位規則、`path_prefix` 格式）使用中文訊息。
- **CI 測試（V5）**：新增 `tests/unit/test_configs.py`，以 parametrize 載入 `configs/` 下所有設定檔並驗證，另外針對跨欄位規則與 strict 行為補單元測試。
- **不在 config 驗證範圍**：API key 是否存在（`image_summarizer.py:511`）、模型名稱是否有效，依賴執行環境，維持在執行時檢查。

### Phase B：設定檔改為 YAML（todo 3）

#### 決策

| # | 問題 | 決策 |
|---|---|---|
| B1 | 副檔名 | 統一 `.yml`（與 `.github/workflows` 一致），loader 只接受 `.yml` |
| B2 | PyYAML 的 YAML 1.1 陷阱 | 依賴 strict 模式攔截，並在 `configs/README.md` 寫撰寫注意事項；不換 ruamel.yaml、不自訂 loader |
| B3 | 存檔格式 | 自訂 dumper；存 extends 展開後的完整 config；`None` 輸出為 `null`；檔頭註解記錄來源 |
| B4 | `extends` 語意 | 見下方「`extends` 設計」 |
| B5 | `generated_exclude_words.toml` | 刪除（`exclude_words` 已不是 config 欄位，詞彙已完整記錄在 `exclude_words_report.json`） |
| B6 | 轉換方式 | 一次性腳本轉檔後手動整理；移除 `tomlkit` |

#### 載入流程

```
configs/{module}/{name}.yml
  → yaml.safe_load（逐層處理 extends）
  → deep merge 成單一 dict
  → 取出保留 key（run_name_fields）
  → Config.model_validate(dict)
```

#### `extends` 設計

- **語法**：檔案最上層寫 `extends: <設定名>`，值為單一字串（單一繼承），不含副檔名。
- **範圍**：只能繼承同資料夾的設定（`configs/rag/test.yml` 的 `extends: default` 指向 `configs/rag/default.yml`），不支援路徑或跨資料夾。
- **多層繼承**：允許 A extends B extends C，深度不限；以已走訪清單偵測循環，錯誤訊息列出完整鏈（`a → b → a`）。
- **找不到被繼承的檔案**：報錯並列出繼承鏈。
- **合併規則**（子檔疊在父檔上）：
  - 兩邊都是 dict：遞迴合併。
  - 其他情況（list、純量、`null`、型別不同）：子檔的值整個取代父檔的值。
- **清除值**：寫 `key: null`。可選欄位變成「未設定」；必填欄位則驗證失敗。
  - 因為 dict 是遞迴合併，子檔寫 `key: {}` **不會**清空父檔的 dict；要移除 dict 中的某個 key，需明確寫該 key 為 `null`。
  - 例：父檔用 `WeightedRanker`，子檔改用 `RRFRanker` 時需寫 `hybrid_ranker_params: {weights: null, k: 60}`，否則合併後同時有 `weights` 與 `k`，會被跨欄位規則擋下。
- **只驗證最終結果**：各層原始 dict 不個別驗證（子檔本來就不完整），只在合併完成後 `model_validate` 一次。
- **保留 key**（只在檔案最上層有效）：
  - `extends`：處理後移除，不繼承。
  - `run_name_fields`：dotted path 的 list（如 `[init.max_pages]`），和一般欄位一樣繼承；子檔寫了就整個取代。可省略，省略時為 `[]`，run_name 為 `default`（與現行無 `# run name` 註解時相同）；run_name 字串以最後一段欄位名組成（`max_pages-40`）。
  - 其他層級出現同名 key 視為一般欄位，會被 `extra="forbid"` 擋下。
- **錯誤訊息**：錯誤值可能來自鏈上任一檔，訊息包含實際載入的檔案與繼承鏈，如 `configs/rag/test.yml (extends: default): retriever.similarity_top_k: ...`。
- **與 CLI overrides 的關係**（Phase C）：沿用同一個 deep merge 函式，優先順序為 父檔 < 子檔 < CLI overrides，最後統一驗證一次。
- **附加資訊的存放**：`config_name` 與 `run_name_fields` 不是設定內容，由 loader 設為 pydantic `PrivateAttr`，不參與驗證與 `model_dump`。
- **存檔**：runs/ 與 data/ 的 `module_config.yml` 存展開後的完整 config（`model_dump`），不含 `extends`；附加資訊只寫在檔頭註解，如：
  ```yaml
  # source: configs/rag/test.yml (extends: default)
  # run_name_fields: [vector_store.vector_store_type]
  ```
  往返測試只比對設定內容（`model_dump`）。

範例：

```yaml
# configs/website_crawler/default.yml
run_name_fields: []
init:
  max_depth: 2
  max_pages: null
  content_threshold: 0.25   # KEEP_IMAGE_CONTENT_THRESHOLD
  light_mode: true
  wait_for_images: true
...

# configs/website_crawler/test.yml
extends: default
run_name_fields: [init.max_pages]
init:
  max_pages: 40
```

`test.yml` 展開後等於 `default.yml` 的全部內容，只有 `init.max_pages` 改為 40、`run_name_fields` 改為 `[init.max_pages]`。

Phase B 期間仍保留站點組合檔（Phase D 才刪除），改用 extends 減少重複：`test_{site}.yml` extends `{site}.yml`。

#### 其他變更

- **撰寫注意事項（B2）**：PyYAML 採 YAML 1.1，`1e-3` 會被解析為字串（要寫 `1.0e-3`）、`on/yes/no` 會變成 bool、`2026-09-30` 會變成 date；strict 模式會把這些情況報為型別錯誤。
- **自訂 dumper（B3）**：多行字串輸出為 `|` block scalar、`allow_unicode=True`、`sort_keys=False`（保持模型欄位順序）。`run_config.yml` 也用同一個 dumper。
- 多行 prompt 使用 `|` block scalar。注意：目前 `configs/agent/*.toml` 的 system prompt 寫成 `"\\n"`，TOML 解析後是字面上的反斜線加 n，而非換行。改用 YAML block scalar 後會變成真正的換行，送給 LLM 的 prompt 內容會改變（應屬修正）。
- **轉換（B6）**：一次性腳本以 `tomllib` 讀取、自訂 dumper 輸出；再手動改用 extends、補回自動轉換遺失的註解（如 `# KEEP_IMAGE_CONTENT_THRESHOLD`、litellm 註解掉的參數說明），並把 `# run name` 註解改為 `run_name_fields`。
- **輸出路徑**：runs/ 與 data/ 的 `module_config.toml`／`run_config.toml` 改為 `.yml`；`RunManager` 路徑欄位改名（`module_config_toml_path` → `module_config_path`）。
- 既有 `data/{rag,webpages}/*/` 的舊 `.toml` 記錄檔：~~不轉換，`publish_run_metadata` 寫入時刪除舊檔~~ → 實作時改為一次性轉換為 `.yml`，不加清理邏輯（見 Q4、dev.md）。
- **刪除（B5）**：`save_generated_exclude_words` 不再輸出 `generated_exclude_words.toml`，只保留 `exclude_words_report.json`。
- **相依套件**：加入 `pyyaml`，移除 `tomlkit`；測試中讀取 `module_config.toml` 的地方改讀 yml。
- **文件**：README 與 `docs/code/runs/config.md` 同步更新。

### Phase C：移除 CLI 中介層（todo 6）

目標用法：

```
website-copilot run rag-query --run.config test --module.retriever.similarity-top-k 20
```

#### 原型實測（tyro 1.0.13、pydantic 2.12.5）

| 項目 | 結果 |
|---|---|
| 巢狀參數名稱 | `--module.retriever.similarity-top-k`，符合預期 |
| `Literal` | 自動變成選項清單 |
| list | `--module.vector-store.weights 1.0 0.3` 可直接使用，不再需要 `weights` 特例 |
| 欄位說明 | 可從 `Field(description=...)` 帶進 `--help` |
| 輸出 | `model_dump(exclude_none=True)` 得到 `{'retriever': {'similarity_top_k': 20}, 'vector_store': {'weights': [1.0, 0.3]}}` |
| `dict[str, Any]`（`litellm_kwargs`） | tyro 會產生異常的子命令或報錯，**必須從 CLI 排除** |
| 設成 null | `--module.x.max-pages None` 被視為「未指定」，CLI 無法把欄位設為 null |
| 未指定的 section | 會留下空 `{}`，需清除 |

#### 決策

| # | 問題 | 決策 |
|---|---|---|
| C1 | partial model 產生規則 | 巢狀 section → 巢狀 partial model（以預設實例作為預設值，避免 tyro 將 `Model \| None` 變成子命令）；葉欄位 `X \| None = None`；排除 `dict[str, Any]` 欄位（`litellm_kwargs` 只能寫在設定檔）；複製 `Field` 說明；清除空 section；接受 CLI 無法設為 null 的限制（需要時另寫 extends 設定檔） |
| C2 | pipeline 接收覆寫值的形式 | 只接受巢狀 dict：`overrides={"query_engine": {"query": q}}` |
| C3 | run config 的傳遞 | pipeline 函式只接收 `run_config`（必填）＋ `overrides`，移除展開的 run 參數 |
| C4 | `exp` 實驗 | 8 個實驗全部刪除（引用的設定檔皆已不存在，結果已記錄在 `docs/exp/memo/`） |
| C5 | `--run.config-name` 改名為 `--run.config`（追加需求） | 在 Phase C 實作；只改 CLI 參數名稱（`tyro.conf.arg(name="config")`，已實測可行），Python 屬性維持 `config_name` |

#### 變更範圍

- **partial model（C1）**
  - 新增 `config/overrides.py`（或併入 `base_config.py`）：`make_overrides_model(model)` 以 `pydantic.create_model` 遞迴產生 `{Model}Overrides`，並提供 `prune_empty(dict)`。
  - Phase A 為不易理解的欄位補上 `Field(description=...)`，讓 `--help` 有說明。
- **CLI**
  - `cli/run.py`：`WebsiteCrawlerCLI` 等的 `module` 欄位改為自動產生的 `{Config}Overrides`。
  - 刪除 `pipeline_config.py` 下半部的 `*ModuleConfig` 與 `cli/run.py` 的 overrides 轉換迴圈（含 `weights → hybrid_ranker_params` 特例）與 `run_kwargs` 的 `pop` 處理。
  - 各分支簡化為一行：`run_rag_query(command.run, prune_empty(command.module.model_dump(exclude_none=True)))`。
- **config 載入（C2）**：`Config.from_yaml(config_name, overrides=None)`，overrides 以 Phase B 的同一個 deep merge 疊在 extends 展開結果之上（父檔 < 子檔 < overrides），最後驗證一次。
- **pipeline 簽名（C3）**
  ```python
  def run_website_crawler(run_config: WebsiteCrawlerRunConfig, overrides: dict | None = None) -> ...
  def run_image_summarizer(run_config: ImageSummarizerRunConfig, overrides: dict | None = None, crawl_results=None) -> ...
  def run_rag_build(run_config: RAGBuildRunConfig, overrides: dict | None = None) -> None
  def run_rag_query(run_config: RAGQueryRunConfig, overrides: dict | None = None) -> None
  def run_agent_query(run_config: AgentRunConfig, overrides: dict | None = None) -> None
  def run_agent_build(run_config: AgentRunConfig | ServeRunConfig, overrides: dict | None = None) -> Agent
  def run_prepare(run_config: PrepareRunConfig) -> None
  ```
  - `config_name`、`save`、`publish`、`run_name_use_config_name` 等一律從 `run_config` 讀取，不再重複傳遞。
  - `PrepareRunConfig` 新增 `publish: bool = True`，CLI 可用 `--run.no-publish` 只寫 runs/（原本 CLI 的 prepare 一定會 publish）；`run_prepare` 依此決定 `save = not publish`，並以同一個 `config_name` 建立 `WebsiteCrawlerRunConfig`／`ImageSummarizerRunConfig`／`RAGBuildRunConfig` 傳給各階段；`serve` 同理。
  - run config 不再是選填，因此所有路徑（含 `run_prepare`）的 run config 都會被記錄；publish 到 data/ 的檔案因此多出 `run_config.yml`，`test_pipeline_prepare.py` 中檢查 data/ 檔案清單的斷言在 Phase C 更新。
  - `retrieval/factory.py` 的 `build_rag(config_name, **config_overrides)` 改為 `overrides` 參數。
- **刪除 exp（C4）**
  - 刪除 `cli/exp.py`、`cli/__init__.py` 的 `exp` 子命令，以及 `pipelines/exp.py` 的 8 個實驗函式、`EXPERIMENTS`、`run_experiment`。
  - `pipelines/exp.py` 仍保留 `run_rag_query`／`run_agent_query`（`run rag-query`／`run agent` 使用）。
  - README、`docs/code/runs/{cli,config}.md` 移除 `exp` 相關說明。
- **CLI 參數改名（C5）**
  - 所有 RunConfig（`BaseRunConfig`、`AgentRunConfig`、`PrepareRunConfig`、`ServeRunConfig`）的 `config_name` 以 `Annotated[str, tyro.conf.arg(name="config")]` 標註，CLI 變為 `--run.config test`。
  - Python 屬性維持 `config_name`：與 `BaseModuleConfig.config_name` 一致，且 `run_config.config` 在程式中容易被誤讀為 config 物件。
  - 放在 Phase C 的理由：C3 已經改寫所有 RunConfig 的使用端與 CLI，一次改完；Phase D 新增 `site` 時直接沿用最終的參數名稱，文件也只需更新一次。
  - README、`docs/code/runs/{cli,config,workflow}.md`、`docs/code/phase*/modules/*.md` 中的 `--run.config-name` 一併更新（`docs/work/`、`docs/progress_report/` 為歷史紀錄，不改）。
- **tests**：`tests/integration`、`tests/unit/test_pipeline_*.py` 改用新簽名（`run_website_crawler(WebsiteCrawlerRunConfig(config_name="test"))`、`run_prepare(PrepareRunConfig(config_name="test", publish=False))`）；新增 `--run.config` 參數名稱的 CLI 測試。
- **過渡狀態**：`site_id` 與 `query_engine.query` 會暫時出現在 CLI（`--module.site-id`），Phase D 移除欄位後自動消失。

### Phase D：站點分層（todo 1）

#### 現況分析

比對各模組的站點檔與 `default.toml`，真正因站點而異的欄位只有：

| 模組 | 因站點而異的欄位 | 其餘欄位 |
|---|---|---|
| website_crawler | `site_id`、`url`、`url_patterns`、`allowed_domains`、`path_prefix`；claudecode 另有 `max_prompt_tokens = 500000` | 與 default 相同 |
| image_summarizer | `site_id` | 與 default 相同 |
| rag | `site_id`、`query` | 與 default 相同 |

此外 `default.toml` 實際就是 nculab 的設定，而 `test.toml` 與 default 的差異只有 `max_pages = 40`（屬於環境差異，與站點無關）。

#### 設計

**站點身分與模組參數分離**：新增獨立的 `SiteConfig`，模組 config 不再包含任何站點資訊。

```yaml
# configs/sites/ncucsie.yml —— 站點身分
site_id: ncucsie
sample_query: 介紹資工系課程
crawl:
  url: https://www.csie.ncu.edu.tw/
  url_patterns: ["*csie.ncu.edu.tw*"]
  allowed_domains: [www.csie.ncu.edu.tw]
  path_prefix: /
```

```yaml
# configs/website_crawler/default.yml —— 爬蟲參數，不含站點資訊
run_name_fields: [init.max_depth]   # 沿用舊站點檔的 run name 欄位
init:
  max_depth: 2
  max_pages: null
  content_threshold: 0.25
  light_mode: true
  wait_for_images: true
clean:
  llm_model: gpt-5.6-luna
  sample_ratio: 0.1
  repeat: 5
  max_prompt_tokens: 500000
```

```python
class SiteCrawlConfig(ConfigModel):
    url: NonEmptyStr
    url_patterns: list[str] | None = None
    allowed_domains: list[NonEmptyStr] | None = None
    path_prefix: str | None = None  # 需以 / 開頭

class SiteConfig(ConfigModel):
    _CONFIG_FOLDER_PATH: ClassVar[str] = "configs/sites"

    site_id: NonEmptyStr
    sample_query: str | None = None
    crawl: SiteCrawlConfig
```

設定檔結構：

```
configs/sites/{nculab,ncucsie,claudecode}.yml
configs/website_crawler/{default,test}.yml       # test：extends default，只寫 max_pages: 40
configs/image_summarizer/{default,test}.yml
configs/rag/{default,test}.yml
configs/agent/{default,test}.yml                 # agent 為多站，不受影響
```

刪除所有 `{nculab,ncucsie,claudecode}.yml` 與 `test_{nculab,ncucsie,claudecode}.yml`（Phase B 由 TOML 轉來）。

#### 決策

| # | 問題 | 決策 |
|---|---|---|
| S1 | 站點檔如何接入程式 | 獨立的 `SiteConfig`；pipeline 依 `run_config.site` 自行載入，不另外傳參數（符合 C3「不重複傳遞」） |
| S2 | 站點特有的模組參數（claudecode 的 `max_prompt_tokens`） | 直接把 default 提高到 `500000`，站點檔不提供模組覆寫 |
| S3 | RAG 的 `query` | 從 `RAGConfig` 移到 `RAGQueryRunConfig`；未指定時使用 `site.sample_query` |
| S4 | 未提供站點 | 必填，不設預設值（避免誤將錯誤站點 publish 到 data/） |
| S5 | RAG 內部如何取得 site_id 與路徑 | 新增執行期物件 `RAGTarget(site_id, webpages_dir, milvus_uri)`，由 factory 依站點與執行模式產生；`RAGConfig` 移除路徑欄位 |
| S6 | site_id 規則 | 格式 `^[A-Za-z_][A-Za-z0-9_]*$`（Milvus collection 名稱與路徑皆可用）；保留欄位並檢查必須與檔名一致 |
| S7 | image-summarizer 讀到其他站點的爬蟲結果（既有 bug） | `load_latest_results` 加 `site_id` 過濾；找不到該站點結果時報錯，不退回其他站點 |
| S8 | 站點在 CLI 的形式 | 位置參數：`website-copilot prepare ncucsie --run.config test`（已實測 tyro `Positional` 可行） |
| S9 | 站點顯示名稱／描述 | 不納入本次重構，列入 todo「功能進度」 |
| S10 | Phase D 後 prepare 的 run 資料夾名稱 | 舊站點檔的 run name 欄位搬進 default：crawler `[init.max_depth]`、image_summarizer `[summarize.model]`（rag 原本即為 `[vector_store.vector_store_type]`），使 `prepare {site}` 的 run 名稱與原本相同 |

#### 補充現況（S5–S7 的依據）

- site_id 不只用在路徑：`IndexBuilder` 以它作為 **Milvus collection 名稱**（`index.py:166`）並寫入 node metadata（`index.py:153`），因此從 `RAGConfig` 移除後仍需另一個管道傳入；已 publish 的向量庫以 site_id 為 collection 名稱，格式必須符合 Milvus 規則。
- `run_image_summarizer` 未傳入爬蟲結果時呼叫 `load_latest_results(..., "website_crawler")`，**不分站點**：單獨對 ncucsie 執行時，若最近一次爬的是 nculab，會拿到 nculab 的資料（`load_latest_run_path` 已支援 `site_id`，rag-build 路徑無此問題）。
- `milvus_uri`／`webpages_data_folder_path` 在 4 處被改寫（`factory.py:119,127`、`prepare.py:288,324`），本質是「站點 × 執行模式」決定的執行期值，而非可調參數。

#### 變更範圍

- **config 模型**
  - 新增 `config/site_config.py`（`SiteConfig`、`SiteCrawlConfig`，`from_yaml(site_id)`）。
  - `SiteConfig` 共用 Phase B 的 YAML loader（支援 extends，但目前無用途）；它不是 `BaseModuleConfig`，沒有 `config_name`／`run_name_fields`。
  - `configs/{website_crawler,image_summarizer}/default.yml` 設定 `run_name_fields`（S10）。
  - `WebsiteCrawlerConfig`／`ImageSummarizerConfig`／`RAGConfig` 移除 `site_id`；`WebsiteCrawlerConfig` 移除 `crawl` 區塊（url 類欄位改由 `site.crawl` 提供）。
  - `RAGConfig`：移除 `query_engine.query`、`webpages_data_folder_path`、`milvus_uri` 與 `__post_init__` 的路徑推導（改由 `RAGTarget` 提供，見 retrieval）。
  - `SiteConfig.site_id` 加格式約束與「與檔名一致」檢查（S6）。
  - `WebsiteCrawlerConfig.clean.max_prompt_tokens` 的 default 設定改為 `500000`。
- **run config／CLI**
  - `PrepareRunConfig`、`BaseRunConfig`（website-crawler／image-summarizer／rag-build）、`RAGQueryRunConfig` 新增必填位置參數 `site: Annotated[str, tyro.conf.Positional]`（S8）。
  - `RAGQueryRunConfig` 新增 `query: str | None = None`。
  - `AgentRunConfig`／`ServeRunConfig` 不加 site（agent 為多站）。
  - 用法：`website-copilot prepare ncucsie --run.config test`、`website-copilot run rag-query ncucsie --run.config test --run.query "介紹資工系課程"`。
  - Phase C 自動產生的 `--module.site-id`、`--module.query-engine.query` 隨模型欄位移除而消失。
- **pipelines**
  - `run_website_crawler`／`run_image_summarizer`／`run_rag_build`／`run_rag_query` 簽名不變（仍為 `run_config` + `overrides`），內部以 `SiteConfig.from_yaml(run_config.site)` 載入站點，所有 `config.site_id` 改為 `site.site_id`。
  - `run_prepare` 以同一個 `run_config.site` 建立三個階段的 RunConfig，由此保證 site 一致（站點檔讀取三次，成本可忽略）。
  - `run_rag_query` 的 query 取 `run_config.query or site.sample_query`，兩者皆無時報錯。
  - `run_image_summarizer` 未傳入爬蟲結果時，只讀取同站點的最新結果（S7）。
- **storage**
  - `load_latest_results` 新增 `site_id` 參數，只搜尋 `runs/<ts>/<module>/<site_id>/`（S7）。
  - `create_run_context` 改收 `site_id` 參數，移除 `run_context.py` 對 `config.site_id` 的型別處理。
  - `publish_run_metadata` 與 runs/ 落盤多存一份 `site_config.yml`，讓 data/ 的紀錄可重現。
- **retrieval（S5）**
  - 新增執行期物件：
    ```python
    @dataclass(frozen=True)
    class RAGTarget:
        site_id: str        # Milvus collection 名稱、node metadata
        webpages_dir: str   # 建庫資料來源
        milvus_uri: str     # 向量庫位置
    ```
  - `factory` 依執行模式產生 `RAGTarget`：
    - 資料來源：預設 `data/webpages/{site_id}`；`webpages_data_use_latest_results` 時為 runs/ 中同站點最新的 image_summarizer 結果。
    - 向量庫：`save=True` 為該 run 的 `results/milvus.db`；只 publish 時為 `data/rag/{site_id}/.staging-*`；兩者皆否時為系統暫存資料夾；serve 載入時為 `data/rag/{site_id}/milvus.db`。
  - `IndexBuilder(config, target)`、`build_rag`、`load_rag` 改收 `RAGTarget`；原本改寫 config 的 4 處全部移除。
  - `RAGRegistry.get(site_id)` 以 `RAGConfig.from_yaml(config_name)` 加上 serve 用的 `RAGTarget` 載入；serve 端只需 site_id，不需讀站點檔。
  - `module_config.yml` 不再記錄 `milvus_uri`：publish 與 runs/ 的位置皆為固定規則；唯一不固定的「latest results」來源路徑改寫入 log。
- **tests**：`test_pipeline_prepare.py` 等改由 `SiteConfig.from_yaml("nculab")` 取得 site_id；原本從 `module_config` 讀 `milvus_uri` 驗證向量庫位置的斷言（`test_pipeline_prepare.py:109`）改為檢查實際檔案位置；新增 `SiteConfig` 驗證、site 位置參數必填、`RAGTarget` 各執行模式、`load_latest_results` 站點過濾的測試。
- **文件**：README 與 `docs/code/runs/config.md` 更新 CLI 用法與設定檔結構。

## 已確認決策

| # | 問題 | 決策 |
|---|---|---|
| Q1 | Phase 是否合併 | 不合併；每個 Phase 一個 commit |
| Q2 | YAML 轉 config 的套件 | PyYAML + pydantic `BaseModel.model_validate` |
| Q3 | 未知 key 的處理 | 改為報錯（`extra="forbid"`） |
| Q4 | `data/` 下已 publish 的舊 `.toml` 記錄檔 | ~~不轉換；`publish_run_metadata` 寫入新 `.yml` 時刪除同資料夾的舊 `.toml`~~ → Phase B 審核時改為：一次性轉換為 `.yml` 並刪除原檔，publish 不做清理（理由見 dev.md） |
| Q5 | `exp.py` 引用不存在的 config | 8 個實驗全部刪除，連同 `exp` 子命令（Phase C） |
| Q6 | 執行順序 | A → B → C（CLI）→ D（站點分層），理由見「執行順序說明」 |

## 驗證

### 共同關卡（每個 commit 都必須通過）

1. `scripts/check.sh`（ruff、pyright、`tests/unit`、widget 同步）通過，確保 `git bisect run` 可用。
2. `uv run pytest tests/integration -m "not cost"`（`test_agent_build`、`test_serve`，免費）通過。
3. CLI 冒煙：`website-copilot {prepare,serve} --help` 與 `website-copilot run <module> --help` 皆能正常輸出（Phase A、B 另需檢查 `exp --help`；Phase C 起 `exp` 子命令移除）。
4. 驗證結果記錄在該 Phase 的 `dev.md`。

### config 快照比對

- **動工前**：以目前程式載入所有模組 × 所有 config 名稱，輸出正規化 JSON（全部欄位值 + `run_name`）作為 baseline。
- **每個 Phase 後**：以新程式產生同格式快照（巢狀結構展平後）與 baseline 比對。預期差異事先列出，清單外的差異一律視為 bug。
- `run_name` 必須一併比對：它決定 runs/ 資料夾名稱，影響人工比對不同 run 的可讀性（`load_latest_results`／`load_latest_run_path` 以時間戳排序後搜尋 `results.json`／`results/`，不依賴 run_name，功能上不受影響）。
- 比對腳本為一次性工具，放在 scratchpad、不進版控；比對結果（含預期差異的確認）貼進各 Phase 的 `dev.md`。

| Phase | 預期差異 |
|---|---|
| A | 無。toml 已寫的欄位本來就優先於程式預設值（`cache_download_images`、`vlm_max_workers`、prompt 等值不變）；toml 缺漏的欄位以現行程式預設值補齊。僅型別正規化（tomlkit 型別 → 原生型別） |
| B | 無（extends 解析後應與 TOML 完全相同）；唯一例外為 agent prompt 的 `\n`，比對前先換算 |
| C | 無（config 結構不變，只改 CLI） |
| D | `site_id` 與 url 類欄位移到 `SiteConfig`；`query` 移到 run config；`milvus_uri`／`webpages_data_folder_path` 移到 `RAGTarget`；nculab／ncucsie 的 `max_prompt_tokens` 由 200000 變為 500000；`default` 設定本身的 run_name 由 `default` 變為 `max_depth-2`（crawler）／`model-gpt-5.6-luna`（image_summarizer），而「站點 + default」的 run_name 與舊 `{site}.toml` 相同（S10） |

### 各 Phase 額外檢查

**Phase A**

- 新增 `tests/unit/test_configs.py`：parametrize 載入所有設定檔；反例測試涵蓋 bool 放進 int 欄位、字串數字、未知 key、跨欄位規則、`validate_assignment`、錯誤訊息包含設定檔路徑。
- `save_module_config` 的輸出與舊版比對，確認 section 結構相同。

**Phase B**

- 每份舊 `.toml` 的 dict 與新 `.yml` 經 extends 解析後的 dict 完全相同。
- extends 單元測試：多層繼承、循環偵測、找不到父檔、list 整個取代、`null` 清除、`{}` 不清空 dict、`run_name_fields` 繼承與取代、非頂層保留 key 被拒。
- run_name：快照中每份設定的 `run_name` 與 baseline 相同（驗證 `run_name_fields` 取代註解後行為不變）。
- 往返測試：config → `module_config.yml` → 讀回驗證，`model_dump` 與原 config 相等（確保 runs/ 與 data/ 的紀錄可重現；`config_name`／`run_name_fields` 為附加資訊，不在比對範圍）。
- data/ 舊記錄檔轉換後與原 `.toml` 內容相同，且 module_config 可被現行模型讀回（取代原「publish 後不再有舊檔」的檢查）。
- `grep -rn toml src tests scripts` 確認無遺漏（僅允許刻意保留者）。

**Phase C**

- override 測試：各層巢狀參數正確寫入最終 config；未指定的欄位不會被 `None` 覆蓋；型別錯誤被 tyro 或 strict 擋下。
- CLI → pipeline 的 override 傳遞以 mock 驗證（攔截 pipeline 函式，檢查收到的 config），不實際呼叫 API。
- partial model 產生測試：巢狀結構、`dict[str, Any]` 欄位被排除、欄位說明被帶入、空 section 被清除。
- pipeline 簽名：以 mock 確認 `run_prepare` 建立並傳遞各階段的 RunConfig。
- exp 移除：`website-copilot exp` 不再存在；`grep -rn "EXPERIMENTS\|run_experiment\|ExpCLI" src tests README.md docs/code` 無結果。

**Phase D**

- 快照比對：每個站點 × 模組的「`sites/{site}.yml` + 模組 default」等於舊的 `{site}.toml`（扣除預期差異），run_name 也相同（S10）。
- 路徑不變：`data/{category}/{site_id}/` 與 runs/ 結構和原本一致。
- 未提供站點位置參數時 CLI 報錯；site_id 格式不符或與檔名不一致時報錯。
- `RAGTarget`：各執行模式（save／publish／皆否／serve）產生的路徑正確；config 物件在建庫過程中不再被改寫。
- image-summarizer 單獨執行時只讀取同站點的爬蟲結果（S7）。
- `run_prepare` 建立的三個階段 RunConfig 的 `site` 相同（mock 驗證）。
- serve 端：`RAGRegistry` 仍能載入現有 `data/rag/{nculab,ncucsie,claudecode}` 向量庫（擴充 `test_serve_rag_loading`）。
- Phase C 過渡期的 `--module.site-id`、`--module.query-engine.query` 已從 CLI 消失。

### 付費整合測試

- **時機**：Phase D 完成後（即全部完成後）執行一次：
  - `website-copilot prepare nculab --run.config test --run.no-publish`（只寫 runs/，`max_pages=40`）
  - `uv run pytest tests/integration`（含 cost 測試）
  - `website-copilot run rag-query nculab --run.config test` 加上巢狀 override，確認寫入 `module_config.yml` 的值正確（涵蓋 Phase C 的實際執行）
- **執行者**：由 Claude 執行，每次執行前先向使用者確認；結果與花費摘要記錄在 `dev.md`。

### 已確認決策（驗證）

| # | 問題 | 決策 |
|---|---|---|
| E1 | 快照比對工具是否進版控 | 一次性腳本放 scratchpad，結果貼進 dev.md |
| E2 | 付費整合測試時機 | 最後一個 Phase（D）完成後執行一次 |
| E3 | 付費測試由誰執行 | Claude 執行，每次執行前先確認 |
