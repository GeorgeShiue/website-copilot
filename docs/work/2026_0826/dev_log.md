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
