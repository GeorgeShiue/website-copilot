# 開發實作紀錄 (2026/08/18–08/26)

> 本文檔彙整 `docs/work/2026_0826/` 中所有規劃文件的**實作規格、程式碼設計、資料流變更、測試策略**。
> 各規劃文件保留動機、目標、風險、決策等規劃面內容，實作細節集中於此。

---

## 1. HTML 日期擷取（來源：`2026_0818-html_date_extraction.md`）

### 1-1. `website_crawler.py` — 新增 `_extract_date_from_html()`

從 `CrawlResult.html` 解析結構化日期標籤，回傳 `{"published_date": "...", "modified_date": "..."}`。

**解析優先級（由高到低）**：

| 優先級 | 來源 | 選擇器 / 正則 | 輸出格式 |
|--------|------|--------------|---------|
| 1 | JSON-LD `datePublished` | `soup.select('script[type="application/ld+json"]')` → parsed JSON 中的 `datePublished` | ISO 8601 |
| 2 | OG `article:published_time` | `soup.select('meta[property="article:published_time"]')` | ISO 8601 |
| 3 | `<time datetime>` (itemprop) | `soup.select('time[itemprop="datePublished"]')` 或 `time[datetime]` | ISO 8601 |
| 4 | Generic meta `date` / `pubdate` | `soup.select('meta[name*="date"], meta[name*="pubdate"]')` | 標準化為 ISO 8601 |
| 5 | Dublin Core `dc.date` | `soup.select('meta[name="dc.date"], meta[name="DC.date"]')` | ISO 8601 |
| 6 | HTTP `Last-Modified` | `response_headers.get("Last-Modified")` | ISO 8601 |

**函數簽名**：

```python
def _extract_date_from_html(
    html: str,
    response_headers: dict[str, str] | None = None,
) -> dict[str, str | None]:
    """回傳 ISO 8601 格式（YYYY-MM-DD）。無法擷取時對應值為 None。"""
```

依優先級依次嘗試六層策略，每層回傳第一個匹配值；`modified_date` 從 JSON-LD `dateModified` 或 `<meta property="article:modified_time">` 補充。所有日期經 `_normalize_to_iso8601()` 標準化為 `YYYY-MM-DD`。

### 1-2. `_extract_metadata()` 簽名變更

```python
# Before
@staticmethod
def _extract_metadata(url: str, raw_metadata: dict) -> dict:

# After
@staticmethod
def _extract_metadata(
    url: str, raw_metadata: dict,
    html: str | None = None,
    response_headers: dict[str, str] | None = None,
) -> dict:
```

新增邏輯：呼叫 `_extract_date_from_html(html, response_headers)` 並將 `published_date` / `modified_date` 寫入 metadata。

### 1-3. 呼叫端變更

`_extract_crawl_results_data()` 新增 `html=getattr(crawl_result, "html", None)` 與 `response_headers=getattr(crawl_result, "response_headers", None)`。

### 1-4. `rag_factory.py` — `_build_file_metadata()` 變更

新增 `file_metadata["published_date"] = page_metadata.get("published_date")`，供下游 `MarkdownDateExtractor` 優先使用。

### 1-5. `rag_helper.py` — `_extract_date()` 優先級變更

新增 Strategy 0：優先從 `node.metadata.get("published_date")` 取得 HTML 擷取的日期；無資料時 fallback 至原有四層文字推斷策略。

### 1-6. 資料流變更

```
[改動前]
HTML → crawl4ai → CrawlResult.metadata (僅 title/description)
                 → _extract_metadata() → results.json (無日期)
                 → MarkdownDateExtractor (從 Markdown 文字推斷)

[改動後]
HTML → crawl4ai → CrawlResult.html ──→ _extract_date_from_html()
                                      → results.json (published_date)
                                      → _build_file_metadata() → node metadata
                                      → MarkdownDateExtractor (優先使用 published_date)
                                                          ↓ (無 HTML date 時)
                                              原有四層策略（fallback）
```

### 1-7. results.json 變更前後對比

```json
// [改動前]                    // [改動後]
"metadata": {                  "metadata": {
  "description": "...",          "description": "...",
  "page_type": "general"         "page_type": "general"
}                                "published_date": "2024-10-17",
                                 "modified_date": "2024-10-20"
                               }
```

### 1-8. 測試策略

| 測試類型 | 對象 | 驗證內容 |
|---------|------|---------|
| **單元測試** | `_extract_date_from_html()` | 各種 HTML 結構的日期擷取正確性（JSON-LD / meta property / time element / meta name / HTTP header / 無日期） |
| **單元測試** | `_normalize_to_iso8601()` | 各種日期格式的標準化 |
| **單元測試** | `_extract_date()` (MarkdownDateExtractor) | 有/無 `published_date` 時的行為 |
| **整合測試** | `_extract_metadata()` | 傳入 HTML + headers 後 metadata 包含日期 |
| **端到端** | 完整爬蟲流程 | `results.json` 中有有效 `published_date` |

### 1-9. 實作順序

```
Step 1: website_crawler.py — 新增 _extract_date_from_html() 及輔助函數
Step 2: website_crawler.py — 修改 _extract_metadata() 簽名與邏輯
Step 3: website_crawler.py — 修改 _extract_crawl_results_data() 呼叫端
Step 4: rag_factory.py    — 修改 _build_file_metadata() 傳遞 published_date
Step 5: rag_helper.py     — 修改 MarkdownDateExtractor._extract_date() 優先級
Step 6: 寫單元測試
Step 7: 重新爬取 nculab 驗證 results.json 有日期
```

> ⚠️ Step 7 前置依賴：須等 RunManager Refactor Phase 2 完成後執行（多站目錄結構）。

---

## 2. 多站 RAG — 代碼設計（來源：`2026_0818-multi_site_RAG.md`）

### 2-1. ~~RAGRegistry 設計~~（已過時，已被 §4-6 取代）

> 最終實作版請見 §4-6「Agent 整合」中的 RAGRegistry（整合版）。

### 2-2. Tool 簽名（擴充後）

```python
class WebpageRetrieverInput(BaseModel):
    query: str
    site_id: str  # 目標網站（如 "nculab"、"nctu"）
    filter_dict: dict | None = None
    top_k: int = 10
```

---

## 3. Engines 重構 — Import 變更（來源：`engines_restructure_analysis.md`）

### 3-1. 純函數搬移 import 變更（✅ 已完成）

| 原 import | 新 import | 受影響檔案 |
|-----------|-----------|-----------|
| `app.engines.html_date_extractor` | `utils.html_date_extractor` | `website_crawler.py`、`test/test_html_date_extraction.py` |
| `app.engines.markdown_cleaner` | `utils.markdown_cleaner` | `website_crawler.py` |

### 3-2. RAG 子資料夾 import 變更

| 原路徑 | 新路徑 |
|--------|--------|
| `app.engines.rag.RAG` | `app.engines.rag.RAG`（不變） |
| `app.engines.rag_factory.RAGBuilder` | `app.engines.rag.RAGBuilder` |
| `app.engines.rag_eval_prompts.FAITHFULNESS_*` | `app.engines.rag.rag_eval_prompts.*` |

受影響 consumer：`workflow.py`、`webpage_retriever.py`、`rag_factory.py`（內部），共約 4–5 個 import 語句。

### 3-3. engines/ 內部依賴圖

```
workflow.py ──→ RAG / RAGBuilder / WebsiteCrawler / WebpageImageSummarizer
tools/      ──→ RAG / RAGBuilder
test/       ──→ WebsiteCrawler, resolve_dedup_key, html_date_extractor
rag_factory ──→ RAG, rag_eval_prompts
website_crawler ──→ html_date_extractor, markdown_cleaner
```

---

## 4. RunManager Refactor（來源：`2026_0823-multi_site_refactor_modules.md`）

> Phase A–F 已完成，Phase G–H 待開始。

### 4-1. RunManager 新增（Phase B ✅）

新增 `site_id: str` 與 `site_path: str` 屬性，以及 `set_site_path(site_id)` 方法——建立 `runs/<ts>/module/site/` 路徑。`set_run_path()` 改為優先使用 `site_path` 作為 base（若已設定），fallback 至 `module_path`。`_filter_run_folders()` 改用 `self.base_folder`（原本硬編碼）。

### 4-2. 路徑結構變化

```
set_module_path("website_crawler")  → runs/<ts>/website_crawler/
set_site_path("nculab")             → runs/<ts>/website_crawler/nculab/    ← 必要
set_run_path("default")             → runs/<ts>/website_crawler/nculab/default/
```

### 4-3. DataManager 介面設計（Phase B ✅）

安放位置：`src/app/workflow/data_manager.py`。

| 方法 | 功能 |
|------|------|
| `publish_crawl_results(site_id, results, json_path, folder_path)` | 覆蓋發布至 `data/webpages/{site_id}/` |
| `publish_markdown(site_id, enhanced_results, folder_path)` | 發布增強 Markdown 至 `data/webpages/{site_id}/results/` |
| `publish_vector_store(site_id, vector_store_type, source_path)` | 複製向量庫至 `data/rag/{site_id}/` |
| `list_sites()` | 掃描 `data/webpages/` 回傳所有 site_id |
| `get_webpages_path(site_id)` | 回傳 `data/webpages/{site_id}/` |
| `get_vector_store_path(site_id)` | 回傳 `data/rag/{site_id}/` |
| `site_exists(site_id)` | 檢查 site 是否存在 |

### 4-4. Workflow 函式簽名（最終版）

> Phase B 時 `run_*` 曾新增 `site_id` 參數，後於 §5-3 階段② 移除。以下為最終簽名：

```python
def run_website_crawler(
    run_manager: RunManager | None = None,
    config_name: str = "default",
    run_name_use_config_name: bool = False,
    data_manager: DataManager | None = None,       # 可選：傳入則發布至 data/
    **config_overrides,
) -> dict[str, dict] | None:
```

所有 `run_*()` 函式遵循相同模式：`config` 由 `Config.from_toml(config_name, **config_overrides)` 建立，`site_id` 從 `config.site_id` 取得。`run_agent()` 特殊：config 在 `run_manager` 初始化之前建立（因需 `config.site_id`）。

### 4-5. 設定檔結構變化（Phase A ✅）

所有 Config dataclass 加入 `site_id: str`（必要）；TOML `[init]` 加入 `site_id = "nculab"`；`collection_name` 已移除，直接使用 `site_id` 作為 collection name；`webpages_data_folder_path` / `milvus_uri` 由 `site_id` 動態產生。

```toml
# configs/rag/nculab.toml
[init]
site_id = "nculab"
[vector_store]
vector_store_type = "milvus"
[index]
embedding_name = "text-embedding-3-small"
[retriever]
query_mode = "hybrid"
similarity_top_k = 10
hybrid_top_k = 10
```

### 4-6. Agent 整合

**Site Discovery 工具**：`create_site_discovery_tool(data_manager)` 回傳 `StructuredTool(name="list_knowledge_bases")`，掃描 `data/rag/` 回傳所有 site_id。

**RAGRegistry（整合版 — 最終設計）**：

```python
class RAGRegistry:
    def __init__(self, data_manager: DataManager) -> None: ...
    def get(self, site_id: str, config_name: str = "default") -> RAG: ...
    def close(self) -> None: ...
```

依 `site_id` 延遲建立 RAG 實例，由 `data_manager` 動態設定 `webpages_data_folder_path` 與 `milvus_uri`。

### 4-7. 目錄結構（重構後）

```
data/
├── webpages/nculab/  → results.json + results/*.md
├── webpages/nctu/
├── rag/nculab/       → milvus.db
└── rag/nctu/

runs/<ts>/
├── website_crawler/nculab/default/   → results.json, results/*.md, module_config.toml
├── webpage_image_summarizer/nculab/default/
├── rag_build/nculab/default/
├── rag_query/nculab/default/
└── agent/nculab/default/
```

### 4-8. 遷移路徑

```bash
data/webpages/results.json       → data/webpages/nculab/results.json
data/webpages/results/           → data/webpages/nculab/results/
data/rag/results/milvus.db       → data/rag/nculab/milvus.db
```

### 4-9. site_id 完整流動路徑

```
                    ┌─────────────────────────────┐
                    │  來源（二擇一或兩者）         │
                    │  1. CLI: --site-id nculab    │
                    │  2. TOML: site_id = "nculab" │
                    └──────────┬──────────────────┘
                               │
                    ┌──────────▼──────────────────┐
                    │  BaseModuleConfig            │
                    │  site_id: str (TOML 唯一來源)│
                    └──────────┬──────────────────┘
                               │
               ┌───────────────┼───────────────┐
               ▼               ▼               ▼
    ┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
    │ RunManager       │ │ DataManager  │ │ RAG Config       │
    │ .set_site_path() │ │ .publish_*() │ │ .webpages_data   │
    │ → runs/.../site/ │ │ → data/.../  │ │   = dynamical    │
    └──────────────────┘ └──────────────┘ └──────────────────┘
```

### 4-10. CLI publish 控制 DataManager 傳遞

**動機**：`exp.py` / `test_module.py` 為實驗性質不需發布；`main.py` 永遠發布；`cli.py` 由 `publish` 參數控制。

**解法**：`BaseRunConfig` 含 `publish: bool = False`，cli.py 在分派前 `pop("publish")` 避免洩漏進 `**config_overrides`，條件建立 `DataManager`。

| 分支 | 傳 data_manager | 理由 |
|------|:---------------:|------|
| `WebsiteCrawlerCLI` | ✅ | 函式支援 |
| `WebpageImageSummarizerCLI` | ✅ | 函式支援 |
| `RAGBuildCLI` | ✅ | 函式支援 |
| `RAGQueryCLI` | ❌ | 函式無此參數 |
| `AgentCLI` | ❌ | 函式無此參數 |
| `ServerCLI` | ❌ | 常駐服務，不涉及 |

> `vars(cli_arg.run)` 為 dataclass `__dict__` 的參考（非副本），`pop("publish")` 同步移除屬性——`save_run_config_as_toml()` 不會將 `publish` 寫入 TOML，為正確行為。

**CLI 使用方式**：

```bash
uv run python src/cli.py website-crawler-cli              # 實驗（publish=False）
uv run python src/cli.py website-crawler-cli --run.publish  # 發布至 data/
```

### 4-11. 實作進度

| Phase | 狀態 | 改動範圍 |
|-------|------|----------|
| **A：Config 層** | ✅ | 所有 Config dataclass + 21 個 TOML |
| **B：RunManager + DataManager** | ✅ | `run_manager.py`、`data_manager.py`（新）、`workflow.py` |
| **C：RAGConfig 路徑動態化** | ✅ | `rag_config.py`、`rag.py`、`rag_factory.py`、`workflow.py`、4 個 RAG TOML |
| **D：rag_factory metadata 注入** | ✅ | `rag_factory.py` node metadata 加入 `site_id` |
| **E：workflow.py 端到端串接** | ✅ | `_init_workflow()` 呼叫順序修正 + `run_agent()` 冗餘移除 |
| **F：CLI / main.py** | ✅ | `workflow_config.py`、`cli.py`、`main.py`（含 publish 控制） |
| **G：測試更新** | ✅ | 移除向後相容測試 + 過渡性測試檔案（2026-08-24：移除 `test_phase_a_f.py`（28 tests）、`test_set_run_path_without_site_path`、`test_main_py_has_site_id_constant`；84 tests passed） |
| **H：文件更新** | ⏳ | README.md / project.md 更新 |

**Phase A 驗證**：15/15 單元測試通過；4 Config `from_toml()` 正確解析 `site_id`；空/缺 `site_id` 正確拋出異常。

**Phase B 已知問題**：

| # | 問題 | 狀態 |
|---|------|------|
| 1 | ~~`_init_workflow()` 中 `set_site_path()` 呼叫順序~~ | ✅ Phase E 已修正 |
| 2 | `run_agent()` 中 `set_module_path("agent")` 冗餘呼叫 | 💡 可移除（無副作用） |
| 3 | ~~`run_rag_build()` 中 `data_manager` 無 None 檢查~~ | ✅ 已加入 ValueError 防禦 |

**Phase C 驗證**：`RAGConfig.from_toml()` 路徑動態產生正確；TOML override 有效；`collection_name` 已移除改用 `site_id`。

**Phase D 驗證**：`NodePipelineBuilder` 簽名含 `site_id`；`partial()` 正確注入；`RAGBuilder.build_nodes()` 傳入 `site_id`。

**Phase E 驗證**：`set_site_path()` 在 `set_run_path()` 之前呼叫；`run_agent()` 冗餘呼叫已移除。

**Phase F 驗證**：`BaseRunConfig` 含 `site_id`（後於 §5-3 移至 `BaseModuleConfig`）；`main.py` 傳入 `SITE_ID`。

**Phase F+ 驗證（2026-08-24）**：`publish` 控制正確；`test_main.py` 通過（1 passed, 83.80s）；ruff + pyright 0 errors。

---

## 5. Config 重構 — BaseModuleConfig 抽取 + CLI 重構（2026-08-24）

> **動機**：四個 module config 有大量重複（`config_name`/`site_id`、`from_toml()`、`run_name`、`site_id` 驗證）；`site_id` 在 `BaseRunConfig` 和 module config 雙重持有；CLI 命名不一致。

### 5-1. 三個 TODO 依賴關係

```
TODO 1: 抽取 BaseModuleConfig          ← 階段 ① 基礎
    │
    ├─→ TODO 2: site_id 從 RunConfig    ← 階段 ② 依賴 ①
    │     移至 BaseModuleConfig
    │
    └─→ TODO 3: CLI 重構               ← 階段 ③ 依賴 ①②
          ├─ Step 3a: 改名 ...ConfigCLI → ...ModuleConfig
          ├─ Step 3b: 移動 config class 至 workflow_config.py
          ├─ Step 3c: 移動 → src/app/configs/
          └─ Step 3d: cli.py 清理
```

### 5-2. 階段 ① — BaseModuleConfig（`src/app/configs/base_config.py`）

```python
@dataclass
class BaseModuleConfig:
    _CONFIG_FOLDER_PATH: ClassVar[str] = ""       # 子類覆寫
    sections_to_keys: ClassVar[dict[str, set[str]]] = {}

    config_name: str
    site_id: str

    @classmethod
    def from_toml(cls, config_name: str, **overrides) -> Self: ...

    @property
    def run_name(self) -> str: ...                 # Template Method

    def _post_process_run_name(self, run_name: str) -> str:  # 子類 hook
        return run_name

    @staticmethod
    def validate_site_id(site_id: str) -> None: ...
```

**設計決策**：`_CONFIG_FOLDER_PATH` / `sections_to_keys` 使用 `ClassVar` 避免 dataclass 繼承 ordering 問題。

**重複消除**：~56 行（4 模組 × 欄位/`from_toml`/`run_name`/驗證）。

**`_post_process_run_name()` 覆寫**：`RAGConfig` 用 `.replace("/", "-")` + 移除 `-gemini`；`WebpageImageSummarizerConfig` 用 `.replace("/", "-")`；其餘不覆寫。

### 5-3. 階段 ② — site_id 從 RunConfig 移至 BaseModuleConfig

- `BaseRunConfig` 移除 `site_id: str = "default"`
- `_init_workflow()` 改為 `run_manager.set_site_path(config.site_id)`
- 所有 `run_*()` 移除 `site_id` 參數，改由 `**config_overrides` 傳入 `from_toml()`
- `run_agent()` 特殊：config 在 `run_manager` 初始化之前建立
- `main.py` 確認 TOML 已有正確值後移除冗餘傳入

### 5-4. 階段 ③ — CLI 重構

| Before | After |
|--------|-------|
| `WebsiteCrawlerConfigCLI` | `WebsiteCrawlerModuleConfig` |
| `WebpageImageSummarizerConfigCLI` | `WebpageImageSummarizerModuleConfig` |
| `RAGConfigCLI` | `RAGModuleConfig` |
| `AgentConfigCLI` | `AgentModuleConfig` |

所有 config class 從 `cli.py` 移出至 `src/app/configs/workflow_config.py`（原 `src/app/workflow/workflow_config.py` 已刪除）。`cli.py` 僅保留複合 CLI class + 分派邏輯。`AgentModuleConfig` 新增 `site_id`（替代原 `AgentRunConfig.site_id`）。

### 5-5. site_id 唯一來源原則

`site_id` 的唯一真實來源是 TOML `[init]` section。外部 override 僅在「同一份 config 跑不同站點」或「TOML 為佔位符」時需要。

### 5-6. 最終檔案結構

```
src/app/configs/
├── base_config.py                              ← BaseModuleConfig（新增）
├── workflow_config.py                          ← RunConfig + ModuleConfig
├── website_crawler_config.py                   ← 繼承 BaseModuleConfig
├── rag_config.py                               ← 繼承 BaseModuleConfig
├── webpage_image_summarizer_config.py          ← 繼承 BaseModuleConfig
└── agent_config.py                             ← 繼承 BaseModuleConfig

src/app/workflow/
├── workflow.py          ← _init_workflow + run_*() 更新
├── run_manager.py       ← 不變
└── data_manager.py      ← 不變

src/cli.py    ← 僅保留複合 CLI class + 分派邏輯
src/main.py   ← import 路徑更新，移除冗餘 site_id
```

### 5-7. 驗證結果（2026-08-24）

**Phase ①**：4 config 繼承 `BaseModuleConfig`、`from_toml()` / `run_name` / `validate_site_id()` 正確、pyright + ruff 0 errors。

**Phase ②**：`BaseRunConfig` 不再含 `site_id`、`_init_workflow()` 使用 `config.site_id`、所有 `run_*()` 移除 `site_id`。

**Phase ③**：`...ConfigCLI` 全部改名、config class 搬移完成、import 路徑更新完成。

**端到端測試（`test_main.py`）**：爬蟲 → 圖片摘要 → RAG 建庫 → hybrid query → 四層路徑結構正確。1 passed, 45.3s。

---

## 6. 測試更新：移除向後相容測試 + 過渡性測試檔案（2026-08-24）

### 6-1. 移除原因

Phase A–F 完成後，`_init_workflow()` 統一在 `set_run_path()` 前呼叫 `set_site_path()`，四層路徑結構為唯一路徑。`set_run_path()` 中「不呼叫 `set_site_path` 時 fallback 至 module_path（三層結構）」的向後相容分支已無消費者。`test_phase_a_f.py` 作為重構過程的過渡驗證檔案已完成使命。

### 6-2. 移除清單

| 測試 / 檔案 | 移除原因 |
|-------------|----------|
| `test_set_run_path_without_site_path` | 測試三層路徑 fallback，已無實際使用路徑 |
| `test_main_py_has_site_id_constant` | Phase F 遺留，`main.py` 已無 `SITE_ID` 常數（§5-3 移至 `BaseModuleConfig`），且已處於 FAIL 狀態 |
| **`test_phase_a_f.py`**（整個檔案，28 tests） | Phase A–F 重構過渡性驗證：使用 `inspect.getsource()`/`ast.parse()` 檢查源碼結構（脆弱）、驗證 TOML 欄位不存在、驗證 `BaseRunConfig` 無 `site_id`；永久行為已由其他測試檔覆蓋 |

### 6-3. 驗證結果

- ruff check：通過
- 完整 dev 測試 suite：**84 passed, 0 failed**（移除前 119 個 → 117 個 → 84 個）

### 6-4. 保留的 dev 測試檔案

| 檔案 | 測試數 | 性質 |
|------|--------|------|
| `test_runmanager_datamanager.py` | 14 | RunManager / DataManager 行為測試 |
| `test_agent.py` | 12 | Agent 純函式行為測試 |
| `test_dedup_key.py` | 12 | 去重邏輯行為測試 |
| `test_html_date_extraction.py` | 30 | HTML 日期擷取行為測試 |
| `test_server.py` | 11 | Server API 端點行為測試 |

### 6-5. 建議後續清理

- `set_run_path()` 中 `base_for_run = self.site_path if self.site_path else self.module_path` 的 fallback 可進一步移除，改為強制要求 `site_path` 已設定

---

## 7. 多站 RAG 小範圍端到端驗證（2026-08-25）

### 7-1. 測試腳本

`src/test/dev/test_multi_site.py`：對 nculab 與 ncucsie 兩個 site 各爬取 10 頁，執行圖片摘要與 RAG 建庫，驗證 DataManager 多 site 隔離機制。

Pipeline 流程（每 site）：

```
run_website_crawler(config_name="test_{site}")
    → run_webpage_image_summarizer(config_name="test_{site}", crawl_results=...)
        → run_rag_build(config_name="test_{site}", save_vector_store_to_runs=True)
```

`save_vector_store_to_runs=True`：向量庫先建在 `runs/` 再 publish 到 `data/rag/`，避免 `config.milvus_uri` 與 publish 目標路徑相同導致 self-copy 錯誤。

### 7-2. 測試結果

| Site | 爬蟲 | 圖片摘要 | RAG 建庫 | 狀態 |
|------|------|----------|----------|------|
| **nculab** | ✅ 9 頁 | ✅ 96 張圖片，$0.03 USD | ✅ 向量庫已建立 | **PASS** |
| **ncucsie** | ✅ 9 頁 | ✅ 96 張圖片，$0.03 USD | ✅ 向量庫已建立 | **PASS** |

- 圖片摘要合計：192 張，0 失敗，花費約 $0.06 USD
- RAG 查詢驗證（ncucsie）：「實驗室的成員有哪些人？」成功回覆各實驗室指導老師資訊

### 7-3. 資料隔離驗證

```
data/webpages/nculab/          → results.json (9 頁) + results/*.md
data/webpages/ncucsie/         → results.json (9 頁) + results/*.md
data/rag/nculab/milvus.db/     → 獨立向量庫
data/rag/ncucsie/milvus.db/    → 獨立向量庫
```

兩個 site 的頁面名稱完全不同（nculab: `labintro`, `advisor`, …；ncucsie: `index`, `admission_undergraduate`, …），確認資料隔離機制正常。

### 7-4. Runs 目錄結構

```
runs/20260825_111507/  ← nculab
├── website_crawler/nculab/max_pages-10/
├── webpage_image_summarizer/nculab/model-gemini-3.1-flash-lite/
└── rag_build/nculab/vector_store_type-milvus/

runs/20260825_111615/  ← ncucsie
├── website_crawler/ncucsie/max_pages-10/
├── webpage_image_summarizer/ncucsie/model-gemini-3.1-flash-lite/
└── rag_build/ncucsie/vector_store_type-milvus/
```

四層路徑結構（`runs/<ts>/module/site/run_name/`）正確建立，兩 site 完全獨立。

### 7-5. 發現並修正的 Bug

**`configs/webpage_image_summarizer/test_ncucsie.toml`** 的 `site_id` 錯誤設為 `"nculab"`，已修正為 `"ncucsie"`。

此 bug 會導致 ncucsie 的圖片摘要結果被 `publish_markdown()` 寫入 `data/webpages/nculab/results/`，污染 nculab 的 Markdown 檔案。

### 7-6. 已知非阻斷性警告

- **Milvus gRPC `AllocTimestamp: Method not implemented!`**：milvus-lite 3.2.0 與 pymilvus 之間的已知相容性警告，不影響向量庫建構與查詢功能。

---

## 8. DataManager publish_run_metadata（2026-08-25）

### 8-1. 動機

`runs/` 目錄儲存四個核心檔案（`results.json`、`results/`、`module_config.toml`、`run_config.toml`、`terminal.log`），但 `data/` 目錄僅 publish 結果資料（`results.json`、`results/`、向量庫），缺少元資料檔。需要在 publish 時一併複製元資料，確保 `data/` 為完整的持久化快照。

### 8-2. DataManager 新增方法

| 方法 | 功能 |
|------|------|
| `_copy_single_file(source_path, dest_folder, filename)` | 內部工具，複製單一檔案（接受 `str | None`） |
| `publish_module_config(site_id, category, source_path)` | 複製 `module_config.toml` |
| `publish_run_config(site_id, category, source_path)` | 複製 `run_config.toml` |
| `publish_log(site_id, category, source_path)` | 複製 `terminal.log` |
| `publish_run_metadata(site_id, category, module_config_path, run_config_path, log_path)` | 便利方法，一次發布三個元資料檔 |

`category` 參數決定目標路徑：`"webpages"` → `data/webpages/{site_id}/`，`"rag"` → `data/rag/{site_id}/`。

### 8-3. main.py 呼叫點

在每個模組的 `save_run_config_as_toml()` 之後，呼叫 `data_manager.publish_run_metadata()`：

```python
data_manager.publish_run_metadata(
    site_id=run_manager.site_id,
    category="webpages",  # 或 "rag"
    module_config_path=run_manager.module_config_toml_path,
    run_config_path=run_manager.run_config_toml_path,
    log_path=run_manager.log_path,
)
```

`run_manager.site_id` 由 `_init_workflow()` 內的 `set_site_path(config.site_id)` 設定，時序正確。

### 8-4. 發布後的 `data/` 結構

```
data/
├── webpages/{site_id}/
│   ├── results.json          ← 已有
│   ├── results/              ← 已有
│   ├── module_config.toml    ← 新增
│   ├── run_config.toml       ← 新增
│   └── terminal.log          ← 新增
└── rag/{site_id}/
    ├── milvus.db/            ← 已有
    ├── module_config.toml    ← 新增
    ├── run_config.toml       ← 新增
    └── terminal.log          ← 新增
```

### 8-5. `publish_crawl_results` 重構

`results.json` 的複製邏輯從 4 行手寫改為 `_copy_single_file()` 一行：

```python
# Before
if results_json_path and os.path.isfile(results_json_path):
    dest_json = os.path.join(webpages_path, "results.json")
    shutil.copy2(results_json_path, dest_json)
    logger.info(f"Published results.json to {dest_json}")

# After
self._copy_single_file(results_json_path, webpages_path, "results.json")
```

### 8-6. 驗證結果

`test_multi_site.py` 更新後對 nculab 與 ncucsie 兩站執行完整 pipeline，12 個元資料檔全部 `[OK]`：

| Site | Category | module_config.toml | run_config.toml | terminal.log |
|------|----------|-------------------|-----------------|-------------|
| nculab | webpages | ✅ | ✅ | ✅ |
| nculab | rag | ✅ | ✅ | ✅ |
| ncucsie | webpages | ✅ | ✅ | ✅ |
| ncucsie | rag | ✅ | ✅ | ✅ |

---

## 9. main.py MainCLI — tyro 整合（2026-08-26）

### 9-1. 動機

`main.py` 原本硬編碼所有參數，無法從 CLI 傳入。需改用 `tyro` 使 `config_name` 可從命令列控制。

### 9-2. MainCLI dataclass

```python
@dataclass
class MainCLI:
    """完整流水線：爬蟲 → 圖片摘要 → RAG 建庫，所有模組使用同一個 config_name。"""
    config_name: str = "default"
```

僅保留 `config_name`，其餘參數（`publish`、`webpages_data_use_latest_results` 等）維持硬編碼，確保 `main.py` 為正式完整流水線的單一入口。

### 9-3. 使用方式

```bash
uv run python src/main.py                          # 預設 config
uv run python src/main.py --config-name nculab     # 指定 config
uv run python src/main.py --config-name ncucsie    # 指定 config
```

### 9-4. main() 簽名

```python
def main(cli: MainCLI | None = None) -> None:
    if cli is None:
        cli = MainCLI()
    ...

if __name__ == "__main__":
    import tyro
    main(tyro.cli(MainCLI))
```

保留 `cli: MainCLI | None = None` 參數，方便程式碼直接呼叫（如 `main(MainCLI(config_name="nculab"))`）而不必經過 tyro 解析。

---

## 10. website_crawler.py — NoneType 防護（2026-08-26）

### 10-1. 問題

ncucsie 爬蟲執行時抛出 `Error during filtering crawl results: 'NoneType' object has no attribute 'fit_markdown'`。

原因：crawl4ai 回傳的某些頁面 `crawl_result.markdown` 為 `None`，`_filter_crawl_results()` 未做防護直接存取 `crawl_result.markdown.fit_markdown`。

### 10-2. 修正

在 `_filter_crawl_results()` 中新增 `crawl_result.markdown is None` 檢查：

```python
if crawl_result.markdown is None:
    self._crawl_stats["error_pages"] += 1
    logger.debug(f"Webpage {crawl_result.url} has no markdown, skipping...")
    continue
```

跳過無法解析的頁面，避免整體流程中斷。

---

## 11. workflow.py — RAG 建構移入 `with` 區塊（2026-08-26）

### 11-1. 動機

`run_rag_build()` 中 `RAGBuilder(config).build()` 在 `with (rag, log_run_time(...))` 區塊**外面**執行，導致 nodes → vector store → index → retriever → query engine 的建構時間不被 `log_run_time` 計算。

### 11-2. 修正

```python
# Before
rag = RAGBuilder(config).build()    # 建構在 with 外，不計時
with (rag, log_run_time(run_title)):
    rag.query(...)                  # 只計 query

# After
rag = RAG(webpages_data_folder_path=...)
builder = RAGBuilder(config)
with (rag, log_run_time(run_title)):
    builder.build(rag)              # 建構 + query 全部計時
    rag.query(...)
```

現在 `log_run_time` 涵蓋完整的 nodes → vector store → index → retriever → query engine → query 流程。

---

## 12. rag_factory.py — build() 可選 rag 參數（2026-08-26）

### 12-1. 動機

`RAGBuilder.build()` 和 `build_to_retriever()` 內部透過 `_create_rag()` 建立新 `RAG` 物件，無法接受外部已建立的 `RAG`。為配合 §11 將建構移入 `with` 區塊，需支援外部傳入 `RAG`。

### 12-2. 修正

```python
# Before
def build(self) -> RAG:
    rag = self._create_rag()         # 內部建立
    ...

# After
def build(self, rag: RAG | None = None) -> RAG:
    rag = rag or self._create_rag()  # 有傳入就用，沒有就自動建立
    ...
```

`build_to_retriever()` 同理。完全向後相容：不傳 `rag` 時行為不變。

### 12-3. 影響評估

| 呼叫點 | 影響 |
|--------|------|
| `rag_factory.py:build()` 內部 | 無影響 |
| `webpage_retriever.py:build_to_retriever()` | 無影響，不傳 `rag` 時自動建立 |
| `workflow.py:run_rag_build` | 從 5 行改為 `builder.build(rag)` 一行 |
| `workflow.py:run_rag_query` | 已用 `build_reusable(rag)`，不受影響 |

---

## 13. 端到端流水線驗證（2026-08-26）

### 13-1. nculab 完整流水線

```bash
uv run python src/main.py --config-name nculab
```

| 模組 | 狀態 |
|------|------|
| Website Crawler | ✅ 完成 |
| Webpage Image Summarizer | ✅ 完成 |
| RAG Build | ✅ 完成（2.27s） |

`data/webpages/nculab/`：`results.json`（334 KB）+ `results/` + `module_config.toml` + `run_config.toml` + `terminal.log`

`data/rag/nculab/`：`milvus.db/` + `module_config.toml` + `run_config.toml` + `terminal.log`

### 13-2. ncucsie 完整流水線

```bash
uv run python src/main.py --config-name ncucsie
```

首次執行因 §10 的 NoneType 問題失敗，修正後重新執行成功。

| 模組 | 狀態 |
|------|------|
| Website Crawler | ✅ 完成 |
| Webpage Image Summarizer | ✅ 完成 |
| RAG Build | ✅ 完成（2.49s） |

`data/webpages/ncucsie/`：`results.json`（396 KB）+ `results/` + `module_config.toml` + `run_config.toml` + `terminal.log`

`data/rag/ncucsie/`：`milvus.db/` + `module_config.toml` + `run_config.toml` + `terminal.log`

### 13-3. 兩站總覽

| Site | Crawler | Image | RAG | Publish |
|------|---------|-------|-----|---------|
| nculab | ✅ | ✅ | ✅ | ✅ 8/8 檔案 |
| ncucsie | ✅ | ✅ | ✅ | ✅ 8/8 檔案 |

---

## 14. Milvus Vector Store 重用機制（2026-08-26）

> 規劃文件已整合至本節，原 `milvus_reuse_plan.md` 已刪除。

### 14-1. 動機

`_should_rebuild()` 對 Milvus 硬編回傳 `True`，每次 `build_reusable()` 都刪除舊 DB + 重跑 nodes pipeline + 重建 index。 llama-index 的 `MilvusVectorStore(overwrite=False)` 本身支援連上既有 collection，但專案未利用此能力。

### 14-2. 根因分析

追溯 `llama-index-vector-stores-milvus` v1.1.0 原始碼（`base.py` L318-420）：

```python
# MilvusVectorStore.__init__ 的核心邏輯
if overwrite and collection_name in self.client.list_collections():
    self.client.drop_collection(collection_name)  # overwrite=True 才 drop

if collection_name in self.client.list_collections():
    self._collection_initialized = True           # 直接連上既有 collection
    self._create_index_if_required()              # 只補建 index，不動資料
```

`overwrite=False`（也是預設值）時，只要 collection 已存在就直接連上，不做任何破壞。

### 14-3. 實作變更（`rag_factory.py`，3 處修改）

#### 變更 A：`_should_rebuild()` 統一邏輯

```python
# BEFORE
def _should_rebuild(self, force_rebuild: bool) -> bool:
    if self.config.vector_store_type == "milvus":
        return True                                    # ← Milvus 特例硬編
    assert self.config.qdrant_db_folder_path is not None
    return force_rebuild or not os.path.exists(self.config.qdrant_db_folder_path)

# AFTER
def _should_rebuild(self, force_rebuild: bool) -> bool:
    if force_rebuild:
        return True
    if self.config.vector_store_type == "qdrant":
        assert self.config.qdrant_db_folder_path is not None
        return not os.path.exists(self.config.qdrant_db_folder_path)
    elif self.config.vector_store_type == "milvus":
        assert self.config.milvus_uri is not None
        return not os.path.exists(self.config.milvus_uri)
    raise ValueError(f"Unsupported vector_store_type: {self.config.vector_store_type}")
```

#### 變更 B：`build_reusable()` docstring 更新

移除「Milvus 一律重建（現有設計限制）」及 `Returns` 段落（回傳值已於近期重構中移除）。

#### 變更 C：`build_reusable()` 重用分支加入 `load_collection()`

```python
# BEFORE
        else:
            self.build_vector_store(rag, overwrite=False)
            self.load_index(rag)

# AFTER
        else:
            self.build_vector_store(rag, overwrite=False)
            # Milvus 重用既有 collection 時，需手動載入（ released → loaded ）
            if self.config.vector_store_type == "milvus":
                assert rag.vector_store is not None
                rag.vector_store.client.load_collection(
                    rag.vector_store.collection_name
                )
            self.load_index(rag)
```

**變更理由**：整合測試中發現 `MilvusVectorStore(overwrite=False)` 連上既有 collection 後，collection 處於 `released` 狀態，查詢時拋出 `MilvusException: Collection 'xxx' is in state 'released'`。需手動 `load_collection()` 將其載入記憶體。

### 14-4. 單元測試（`src/test/dev/test_rag_reuse.py`，14 項）

使用 `_FakeRAGConfig` + `patch("os.path.exists")` 驗證 `_should_rebuild()` 邏輯，無需實際 Milvus 連線：

| 測試群組 | 項數 | 驗證 |
|----------|------|------|
| `TestShouldRebuildMilvus` | 4 | Milvus 路徑判斷 + force_rebuild |
| `TestShouldRebuildQdrant` | 3 | Qdrant 路徑判斷（不受影響） |
| `TestShouldRebuildUnified` | 7 | parametrized 驗證兩種 store 統一邏輯 + unsupported 例外 |

### 14-5. 整合測試結果

```bash
uv run python src/cli.py rag-query-cli --run.config-name ncucsie
```

| 指標 | 結果 |
|------|------|
| `Cleaned Milvus vector store` | **無** — 舊 DB 未被刪除 ✓ |
| `Loading Markdown Documents` | **無** — nodes pipeline 跳過 ✓ |
| `Successfully loaded index from vector store` | ✓ 既有 index 載入成功 |
| Query 回應 | ✓ 正確回覆「資工系課程」 |
| Faithfulness / Relevancy | **100% / 100%** |
| 執行時間 | **13.4s**（重建約 30s+） |

### 14-6. 行為對照

| 情境 | 改前 | 改後 |
|------|------|------|
| `milvus.db` 不存在 | 全新建構 | 全新建構（不變） |
| `milvus.db` 已存在 + `force_rebuild=False` | 刪除重建 | **直接載入** |
| `milvus.db` 已存在 + `force_rebuild=True` | 刪除重建 | 刪除重建（不變） |
| Qdrant 行為 | 不變 | 不變 |

### 14-7. 影響範圍

| Workflow | 影響 |
|----------|------|
| `run_rag_query()` | **受益**：milvus.db 已存在時跳過重建 |
| `run_rag_build()` | 無影響——使用 `build()` 全新建構 |
| `create_webpage_retriever_tool()` | 無影響——使用 `build_to_retriever()` |
| Server 端 (`create_rag_agent`) | 無影響 |

### 14-8. 檔案變更總覽

| 檔案 | 操作 | 說明 |
|------|------|------|
| `src/app/engines/rag/rag_factory.py` | 修改 | `_should_rebuild()` 統一邏輯 + `build_reusable()` docstring + `load_collection()` |
| `src/test/dev/test_rag_reuse.py` | 新增 | `_should_rebuild` 單元測試（14 項） |

---

## 15. 多站 RAG 工具實作（2026-08-26）

> 規劃文件：`2026_0826-multi_site_RAG_tool.md`（M3：多站 RAG 檢索）。

### 15-1. 動機

M2 完成後資料與向量庫已按 `site_id` 隔離（`data/webpages/{site_id}/`、`data/rag/{site_id}/`），但 Agent 工具層仍硬綁單一 RAG 實例（`create_webpage_retriever_tool(config_name="default")`），無法同時存取多站知識庫。需要：
- `RAGRegistry` 管理多站 RAG 的延遲建立、LRU 快取與生命週期
- `webpage_retriever` 改為依 `site_id` 路由至對應 RAG 實例
- `list_knowledge_bases` 工具供 LLM 發現可用站點
- System prompt 引導 LLM 正確使用多站工具

### 15-2. 變更範圍

```
src/app/tools/rag_registry.py       ← 新增（100 行）
src/app/tools/webpage_retriever.py  ← 修改（126 行，原 ~130 行精簡重寫）
src/app/agent/agent.py              ← 修改（369 行）
src/app/configs/agent_config.py     ← 修改（DEFAULT_SYSTEM_PROMPT）
configs/agent/default.toml          ← 修改（system_prompt）
configs/agent/test.toml             ← 修改（system_prompt）
scripts/m0_rag_smoke.py             ← 修改（改用新 API）
src/test/dev/test_rag_registry.py   ← 新增（354 行，13 項測試）
src/test/dev/test_multi_site_tool.py ← 新增（381 行，26 項測試）
```

### 15-3. 模組一：RAGRegistry（`src/app/tools/rag_registry.py`）

```python
class RAGRegistry:
    _cache: OrderedDict[str, RAG]     # site_id → RAG 的 LRU 快取
    _data_manager: DataManager        # site 存在性驗證
    _default_config_name: str         # 預設 "default"
    _max_cached: int                  # 快取上限，預設 5

    def list_sites(self) -> list[str]: ...
    def get(self, site_id: str) -> RAG: ...
    def close(self) -> None: ...
    def _evict_if_needed(self) -> None: ...
```

**`get(site_id)` 流程**：

1. cache hit → `move_to_end` 更新 LRU 順序 → 直接回傳
2. `DataManager.site_exists(site_id)` → 不存在則 `ValueError`
3. `RAGConfig.from_toml("default", site_id=site_id)` — 路徑由 site_id 動態產生
4. `RAG(webpages_data_folder_path=...)` + `RAGBuilder(config).build_reusable(rag, force_rebuild=False)`
5. 存入 `_cache` → 超出 `max_cached` 則 `popitem(last=False)` eviction + `rag.close()`

**設計決策**：

| 決策 | 選擇 | 理由 |
|------|------|------|
| 快取資料結構 | `OrderedDict`（手動 LRU） | 比 `functools.lru_cache` 更可控，支援 eviction 時釋放 RAG |
| RAG 路徑來源 | 直接指向 `data/rag/{site_id}/` | Agent 問答不經 runs/ 中間層，直接指向正式資料 |
| Config 建立 | `RAGConfig.from_toml("default", site_id=site_id)` | 用 default 設定 + override site_id，避免每個站都要一份 config |
| Build 策略 | `build_reusable(force_rebuild=False)` | 利用 §14 Milvus 重用機制：skip nodes pipeline，`load_collection()` ~13s |
| 不需 RunManager | Registry 不建立 RunManager | Agent 問答指向正式 data/；RunManager 僅供建庫流程使用 |

### 15-4. 模組二：webpage_retriever.py — 多站路由

**RetrieverInputSchema 變更**：

```python
class RetrieverInputSchema(BaseModel):
    site_id: str = Field(description="目標知識庫的 site_id（如 'nculab'、'ncucsie'）")
    query: str = Field(description="搜尋查詢字串")
    filter_dict: dict[str, Any] | None = Field(default=None, ...)
    similarity_top_k: int | None = Field(default=None, ...)
```

**`create_webpage_retriever_tool` 簽名變更**：

```python
# BEFORE（~90 行，含 RunManager / config / RAGBuilder / 隔離邏輯）
def create_webpage_retriever_tool(
    run_manager: RunManager | None = None,
    config_name: str = "default",
    run_name_use_config_name: bool = False,
    **config_overrides,
) -> StructuredTool:

# AFTER（~30 行，Registry 延遲載入）
def create_webpage_retriever_tool(
    registry: RAGRegistry,
) -> StructuredTool:
```

精簡幅度：RunManager、config 載入、vector store 隔離等全部移至 RAGRegistry，工具層僅負責 `registry.get(site_id)` → `rag.retrieve()` 路由。

### 15-5. 模組三：agent.py — 站點發現工具與 Agent 整合

**`create_site_discovery_tool`（新增）**：

```python
class _DiscoveryInputSchema(BaseModel):
    """list_knowledge_bases 工具的輸入 schema（無參數）。"""

def create_site_discovery_tool(registry: RAGRegistry) -> StructuredTool:
    """建立 list_knowledge_bases 工具。掃描 data/webpages/ 回傳所有可用 site_id。"""
```

> `StructuredTool` 在 langchain-core 中要求 `args_schema` 為必填欄位，即使工具無參數也需提供空 schema。

**`create_rag_agent` 流程變更**：

```python
# BEFORE
tool = create_webpage_retriever_tool(run_manager=run_manager, config_name="default", ...)
graph = create_agent(llm, [tool], system_prompt=config.system_prompt, ...)
return RAGAgent(graph=graph, tool=tool, ...)

# AFTER
registry = RAGRegistry(DataManager())
discovery_tool = create_site_discovery_tool(registry)
retriever_tool = create_webpage_retriever_tool(registry)
graph = create_agent(llm, [discovery_tool, retriever_tool], system_prompt=config.system_prompt, ...)
return RAGAgent(graph=graph, tools=[discovery_tool, retriever_tool], registry=registry, ...)
```

**RAGAgent dataclass 擴充**：

```python
@dataclass
class RAGAgent:
    graph: Any
    tools: list[StructuredTool]             # 改為 list（原 tool: Any）
    run_manager: RunManager
    config: AgentConfig
    checkpointer: InMemorySaver = field(default_factory=InMemorySaver)
    registry: RAGRegistry | None = None     # 新增

    def close(self) -> None:
        if self.registry is not None:
            self.registry.close()
```

### 15-6. System Prompt 更新

```python
DEFAULT_SYSTEM_PROMPT = (
    "你是多站網站助理，可從多個學校網站知識庫中檢索資訊。\n\n"
    "## 使用工具的流程\n"
    "1. 若不確定有哪些可用的知識庫，先使用 list_knowledge_bases 查詢\n"
    "2. 使用 webpage_retriever 時必須提供 site_id 參數\n"
    "3. 若問題來自特定網站（如對話中有 site 語境），直接使用該 site 檢索\n\n"
    "## 回答規則\n"
    "- 根據檢索結果回答，必須列出參考來源的 URL\n"
    "- 若檢索結果不足以回答，請誠實說明\n"
    "- 若問題可能涉及多個站點，可分別檢索後合併回答"
)
```

`configs/agent/default.toml` 與 `configs/agent/test.toml` 同步更新。

### 15-7. 資料流變更

```
[改動前]
Agent query → create_webpage_retriever_tool(config_name="default")
            → RAGBuilder.build_to_retriever() → 單一 RAG 實例
            → rag.retrieve(query) → 回傳結果

[改動後]
Agent query → webpage_retriever(site_id="nculab", query="...")
            → RAGRegistry.get("nculab")
              ├─ 快取命中 → 直接回傳已有 RAG（<1ms）
              └─ 快取未命中 → RAGConfig + RAG + build_reusable（~13s）
            → rag.retrieve(query) → 回傳結果
```

### 15-8. 向後相容性

| 呼叫點 | 影響 |
|--------|------|
| `create_rag_agent()` | **改動**：建立 Registry + 兩個工具 |
| `run_agent()` (workflow.py) | **不受影響**：`agent.close()` 呼叫不變，內部改為 `registry.close()` |
| `app.py` (Server) | **M4 改動**：此階段不受影響（Server 層尚未加 `page_url`） |
| `run_rag_query()` (workflow.py) | **不受影響**：使用 `build_reusable()` 開獨立 RAG |
| `run_rag_build()` (workflow.py) | **不受影響**：使用 `build()` 全新建構 |

**不受影響的檔案**：`rag.py`、`rag_factory.py`、`rag_config.py`、`data_manager.py`、`cli.py`。

### 15-9. 測試策略

#### 單元測試：`test_rag_registry.py`（13 項，全部 mock）

| 測試群組 | 項數 | 驗證 |
|----------|------|------|
| `TestListSites` | 2 | 委派 DataManager / 空站點 |
| `TestGetSiteNotFound` | 3 | ValueError / 錯誤訊息含可用站點 / 空站點顯示「（無）」 |
| `TestGetCacheMiss` | 2 | 首次呼叫觸發 RAGConfig + RAG + build_reusable / 結果存入快取 |
| `TestGetCacheHit` | 2 | 第二次呼叫回傳相同實例 / move_to_end 更新 LRU 順序 |
| `TestLRUEviction` | 2 | 超出 max_cached 淘汰最久未使用項 / 未超出不淘汰 |
| `TestClose` | 2 | 釋放所有快取中 RAG / 空快取不報錯 |

#### 整合測試：`test_multi_site_tool.py`（26 項，全部 mock）

| 測試群組 | 項數 | 驗證 |
|----------|------|------|
| `TestRetrieverInputSchema` | 4 | site_id 欄位存在 / 必填 / 有效建構 / 選項預設值 |
| `TestCreateWebpageRetrieverTool` | 5 | 回傳 StructuredTool / name / description 含 site_id / 含 list_knowledge_bases / args_schema |
| `TestRetrieveRouting` | 3 | 呼叫 registry.get(site_id) / filter/top_k 傳遞 / 錯誤傳播 |
| `TestFormatRetrievalResults` | 3 | 空結果 / 單筆含標題分數URL / 多筆計數正確 |
| `TestCreateSiteDiscoveryTool` | 5 | StructuredTool / name / description / 有站點格式化 / 空站點提示 |
| `TestRAGAgent` | 4 | tools+registry 欄位 / close 呼叫 registry.close() / None 安全 / tools 為 list |
| `TestEndToEndFlow` | 2 | discovery → retrieve 串接 / 多站結果不混雜 |

#### 端到端驗證

| 測試 | 驗證 | 結果 |
|------|------|------|
| `test_module.py::test_agent` | 真實 LLM + Milvus：Agent 自動帶入 `site_id=nculab` → 正確檢索 → 回答含 6 個來源 URL | ✅ PASSED（25.5s） |
| `m0_rag_smoke.py` | 改用新 API（`RAGRegistry` + `site_id`）的 smoke test | ✅ 通過 |
| 回歸測試 | 既有 37 個相關測試（`test_agent.py` / `test_server.py` / `test_rag_reuse.py`） | ✅ 37 passed |

#### 測試過程修正的問題

| # | 問題 | 修正 |
|---|------|------|
| 1 | `create_site_discovery_tool` 缺少 `args_schema` | 新增 `_DiscoveryInputSchema`（空 schema），langchain-core 要求 `StructuredTool` 必須有 `args_schema` |
| 2 | `agent.py` 缺少 `from pydantic import BaseModel` | 新增 import |
| 3 | LRU eviction 測試中 mock RAG 路徑全部相同 | 改用 `config_side_effect` 為每 site 產生獨立 `webpages_data_folder_path` |

### 15-10. 端到端 E2E 驗證結果

```bash
uv run pytest src/test/test_module.py::test_agent -v -m slow
```

**Agent 建立階段**：
- `RAGRegistry(DataManager())` 建立成功
- `list_knowledge_bases` + `webpage_retriever` 兩個工具正確綁定
- LLM `gemini-3.1-flash-lite` 成功載入

**問答階段**（query: "實驗室的成員有哪些人？"）：
- LLM 正確選擇 `webpage_retriever` 並帶入 `site_id="nculab"`
- Registry cache miss → `build_reusable(force_rebuild=False)` → Milvus `load_collection` ~13s
- Hybrid 檢索回傳結果，LLM 回答含教授與學生名單
- 6 個參考來源 URL 全部來自 `sites.google.com/site/nculab/`

**資源釋放**：
- `agent.close()` → `registry.close()` → `Closing RAG for site_id=nculab` ✓

**落盤**：`chats/20260826_095040/agent/nculab/test/results.json`

### 15-11. 檔案變更總覽

| 檔案 | 操作 | 行數 | 說明 |
|------|------|------|------|
| `src/app/tools/rag_registry.py` | **新增** | 100 | RAGRegistry（lazy + LRU + close） |
| `src/app/tools/webpage_retriever.py` | 修改 | 126 | RetrieverInputSchema 加 site_id；工具改用 registry 路由 |
| `src/app/agent/agent.py` | 修改 | 369 | create_site_discovery_tool + RAGAgent tools/registry + create_rag_agent |
| `src/app/configs/agent_config.py` | 修改 | — | DEFAULT_SYSTEM_PROMPT 更新為多站路由版 |
| `configs/agent/default.toml` | 修改 | — | system_prompt 同步更新 |
| `configs/agent/test.toml` | 修改 | — | system_prompt 同步更新 |
| `scripts/m0_rag_smoke.py` | 修改 | 44 | 改用新 API（RAGRegistry + site_id） |
| `src/test/dev/test_rag_registry.py` | **新增** | 354 | RAGRegistry 單元測試（13 項） |
| `src/test/dev/test_multi_site_tool.py` | **新增** | 381 | 多站工具整合測試（26 項） |

---

## 16. Chrome Extension 站點偵測與 Server 路由（2026-08-26）

> 規劃文件：`2026_0826-chrome_extension_site_detection.md`（M4：Extension 站點偵測與路由）。

### 16-1. 動機

M3 完成後 Agent 工具層已支援多站 RAG 路由（`webpage_retriever(site_id=...)`），但 Chrome Extension 未能偵測使用者瀏覽的網站，無法自動帶入 `site_id`。需在 Extension 偵測 `window.location.hostname`、經後端映射為 `site_id`、前綴至 user query 供 LLM 感知站點。

### 16-2. 變更範圍

```
extension/content.js        ← 修改：偵測 window.location.hostname + 帶入 page_url
extension/background.js     ← 修改：轉發 page_url 至 Server
src/app/server/app.py       ← 修改：ChatRequest + DOMAIN_SITE_MAP + resolve_site_id + _enrich_query
src/test/dev/test_server.py ← 修改：新增 M4 單元測試（7 項）
```

### 16-3. Extension content.js

在 IIFE 內、`proxyStreamChat` 外部一次性偵測 hostname：

```javascript
const currentHostname = window.location.hostname;
```

`port.postMessage` 時帶入 `page_url: currentHostname`。

### 16-4. Extension background.js

`JSON.stringify` 時透傳 `page_url: msg.page_url` 至 Server。

### 16-5. Server app.py — mapping + enrichment

**`DOMAIN_SITE_MAP`**：模組層級 dict，支援精確匹配與子域名 suffix 匹配。

**`resolve_site_id(page_url)`**：從 hostname 解析 site_id；無匹配回傳 None。

**`_enrich_query_with_site_context(query, site_id)`**：將 site_id 前綴至 query（如 `[使用者瀏覽 nculab 網站] ...`），供 LLM 感知當前站點。

**endpoint 整合**：`chat()` 呼叫 `resolve_site_id(req.page_url)`，傳入 `_event_stream(..., site_id=site_id)`；`_event_stream` 內以 `_enrich_query_with_site_context()` 產生 `enriched_query` 替代原始 query。

### 16-6. 協定變更摘要

| 欄位 | Before | After |
|------|--------|-------|
| `content → background` | `{ type, query, thread_id }` | `{ type, query, thread_id, page_url }` |
| `background → server` | `{ query, thread_id }` | `{ query, thread_id, page_url }` |
| `ChatRequest` | `query, thread_id` | `query, thread_id, page_url` |

### 16-7. 測試結果

```bash
uv run pytest src/test/dev/test_server.py -v
```

**18 passed, 0 failed**（原 11 項 + M4 新增 7 項）

| 測試 | 驗證 |
|------|------|
| `test_resolve_site_id_exact_match` | 精確匹配 nculab / ncucsie |
| `test_resolve_site_id_suffix_match` | 子域名 suffix 匹配 |
| `test_resolve_site_id_none_and_empty` | None / 空字串 / 空白 → None |
| `test_resolve_site_id_unknown` | localhost / example.com → None |
| `test_enrich_query_with_site_context` | 有 site_id 時前綴正確 |
| `test_enrich_query_with_site_context_none` | None 時原樣回傳 |
| `test_chat_page_url_routed_to_enriched_query` | page_url 串接 endpoint 完整流程 |

**ruff check**：通過（0 errors）。

### 16-8. 檔案變更總覽

| 檔案 | 操作 | 說明 |
|------|------|------|
| `extension/content.js` | 修改 | 偵測 `window.location.hostname` + 帶入 `page_url` |
| `extension/background.js` | 修改 | 轉發 `page_url` 至 Server |
| `src/app/server/app.py` | 修改 | `ChatRequest.page_url` + `DOMAIN_SITE_MAP` + `resolve_site_id` + `_enrich_query_with_site_context` + endpoint 整合 |
| `src/test/dev/test_server.py` | 修改 | 新增 M4 單元測試（7 項） |

---

## 17. Chrome Extension Service Worker Keepalive 修正（2026-08-26）

### 17-1. 問題

M4 站點偵測功能完成後，手動測試發現：在 nculab 問答成功後，切至 ncucsie 頁面問答時 widget 顯示「錯誤：與背景程序連線中斷」。

錯誤來源為 `content.js` 的 `port.onDisconnect` 監聽器：

```javascript
port.onDisconnect.addListener(() => {
    controller.error(new Error('與背景程序連線中斷'));
});
```

### 17-2. 根因分析

Manifest V3 的 `background.js` 為 Service Worker，Chrome 會在 **~30 秒無活動** 待終止它。時序如下：

```
1. nculab 問答 → port 連線正常 → 收到回應 ✓
2. 切到 ncucsie 頁面 → nculab 的 port 斷開（正常）
3. ncucsie 送出查詢 → chrome.runtime.connect() 建新 port
4. Service Worker 剛被 Chrome 終止又重啟
   → 新 port 的背景端尚未就緒
   → 立即觸發 onDisconnect → 錯誤
```

### 17-3. 修正方案：chrome.alarms Keepalive

使用 `chrome.alarms` API 保持 Service Worker 活躍。每 25 秒觸發 alarm，SW 收到 alarm 事件後重新計時，避免被 Chrome 終止。

**運作機制**：

```
content.js 建立 port
  → background.js 建立 alarm（每 25 秒）
  → SW 被 alarm 喚醒 → 重新計時 → 避免被終止
port 斷開 → alarm 清除
```

**為何選用 chrome.alarms 而非 port.postMessage keepalive**：
- `port.postMessage` 會在 content.js 端產生實際的 message 事件，需額外處理過濾
- `chrome.alarms` 是 Chrome 官方推薦的 SW 保持活躍機制，不產生額外的 port 事件
- alarm 事件在 SW 端處理，content.js 完全不感知

### 17-4. 變更內容

**`extension/manifest.json`**：新增 `"permissions": ["alarms"]`（Chrome 要求明確聲明 alarms 權限）。

**`extension/background.js`**：

```javascript
// 頂層：alarm 事件處理（SW 被喚醒時不做任何事，僅保持活躍）
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'wc-keepalive') return;
});

chrome.runtime.onConnect.addListener((port) => {
  if (port.name !== 'wc-chat') return;

  // 建立 keepalive alarm（每 25 秒）
  const ALARM_NAME = 'wc-keepalive';
  chrome.alarms.create(ALARM_NAME, { periodInMinutes: 25 / 60 });

  // port 斷開時清除 alarm
  port.onDisconnect.addListener(() => {
    chrome.alarms.clear(ALARM_NAME);
  });

  port.onMessage.addListener(async (msg) => {
    // ... 原有 fetch 邏輯不變
    // onDisconnect 內同時 abort + clear alarm
  });
});
```

### 17-5. 測試結果

手動 E2E 驗證：

| 步驟 | 預期 | 結果 |
|------|------|------|
| nculab 問答 | site_id="nculab"，正確回答 | ✅ |
| 切至 ncucsie 問答 | site_id="ncucsie"，正確回答 | ✅ 無「連線中斷」錯誤 |
| 快速切換多站 | 各站獨立回答 | ✅ |

### 17-6. 檔案變更總覽

| 檔案 | 操作 | 說明 |
|------|------|------|
| `extension/manifest.json` | 修改 | 新增 `"permissions": ["alarms"]` |
| `extension/background.js` | 修改 | 新增 `chrome.alarms` keepalive 機制（alarm 建立 / 清除 / 事件處理） |

---
