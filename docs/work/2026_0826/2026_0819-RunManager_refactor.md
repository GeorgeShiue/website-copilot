# RunManager Refactor 與多站架構規劃 (2026/08/19)

> 本文檔基於 `2026_0818-multi_site_RAG.md` 的多站拓展需求，分析現有 `RunManager` 的限制，
> 並提出「雙系統分離」架構：**RunManager** 管 `runs/`（歷史紀錄），**DataManager** 管 `data/`（持久化發布區）。

---

## 1. 背景與動機

### 現有問題

`RunManager` 目前承擔了六個不同職責（路徑管理、JSON I/O、MD I/O、MD 渲染、跨 run discover、Rich log），且存在以下關鍵缺陷：

| 問題 | 說明 |
|------|------|
| **硬編碼 `RUNS_FOLDER_PATH`** | `load_latest_results_from_json()`、`load_latest_summarizer_run_path()`、`_filter_run_folders()` 直接引用全域常數，忽略 `self.base_folder`，Agent 場景（`base_folder="chats"`）的 discover 永遠搜不到 |
| **三層路徑無 site 維度** | 路徑結構為 `base/module/run`，多站後需要 `base/module/site_id/run` |
| **`latest_results_json_path` 無 site 隔離** | 同一實例跨模組使用時，後寫結果覆蓋前者的路徑 |
| **`results.json` 語義混用** | 爬取結果、圖片摘要結果、query 結果、聊天結果全部寫入同一檔名 |
| **SRP 違規** | 路徑建立、檔案 I/O、跨 run discover、Markdown 渲染全在同一類別 |

### 多站拓展需求

根據 `2026_0818-multi_site_RAG.md`，專案需要支援多個學校網站的知識庫，包括：
- 每個網站獨立的爬取、摘要、建庫流程
- `site_id` 作為跨模組的維度
- Agent 可根據 `site_id` 動態切換知識庫

---

## 2. 核心決策

### 2.1 雙系統分離

| 系統 | 管理目標 | 目錄 | 寫入者 | 讀取者 |
|------|---------|------|--------|--------|
| **RunManager** | 歷史執行紀錄 | `runs/<ts>/...` | 各 workflow 函式 | discover fallback（測試/獨立模組） |
| **DataManager** | 持久化發布結果 | `data/...` | DataManager.publish() | RAGRegistry、Agent、RAG Build |

```
Pipeline 流程：
Crawler ──dict──→ Summarizer ──dict──→ RAG Build
   │                  │                   │
   ▼                  ▼                   ▼
 runs/              runs/              runs/
   │                  │                   │
   └──────────────────┴───────────────────┘
                      │
                      ▼  DataManager.publish(site_id)
                   data/
                      ▲
                      │  RAGRegistry 讀取（唯讀）
                      │
                    Agent
```

### 2.2 資料傳遞方式

| 場景 | 傳遞方式 | 說明 |
|------|---------|------|
| **Main workflow**（同一 timestamp 內） | 記憶體傳遞（dict） | `run_website_crawler` 回傳 `dict`，直接傳給 `run_webpage_image_summarizer` |
| **獨立模組**（跨 timestamp / 測試） | 檔案傳遞（discover fallback） | `load_latest_results_from_json()` 從 `runs/` 搜尋最新結果 |

### 2.3 site_id 來源

| 來源 | 方式 | 說明 |
|------|------|------|
| **CLI** | `--site-id nculab` | 方便切換網站執行 |
| **TOML config** | `site_id = "nculab"` | 備用，CLI 可覆寫 |

### 2.4 `webpages_data_folder_path` 路徑來源

**選擇 B：DataManager 動態掃描**。RAG config 不再需要硬編碼 `webpages_data_folder_path`，由 `data_manager.get_webpages_path(site_id)` 動態提供。

---

## 3. 目錄結構（重構後）

```
data/
├── webpages/
│   ├── nculab/
│   │   ├── results.json
│   │   └── results/
│   │       └── *.md
│   └── nctu/
│       ├── results.json
│       └── results/
├── rag/
│   ├── nculab/
│   │   └── milvus.db
│   └── nctu/
│       └── milvus.db

runs/<ts>/
├── website_crawler/
│   └── nculab/                     ← set_site_path("nculab")
│       └── default/
│           ├── results.json
│           ├── results/*.md
│           ├── module_config.toml
│           └── terminal.log
├── webpage_image_summarizer/
│   └── nculab/
│       └── default/
├── rag_build/
│   └── nculab/
│       └── default/
├── rag_query/
│   └── nculab/
│       └── default/
└── agent/                          ← base_folder="chats"
    └── nculab/
        └── default/
```

---

## 4. RunManager 改動

### 4.1 新增屬性與方法

```python
class RunManager:
    def __init__(self, module_name="", base_folder="runs"):
        # ... 現有屬性 ...
        self.site_id: str = ""
        self.site_path: str = ""        # ← 新增

    def set_site_path(self, site_id: str) -> None:
        """設定 site 路徑（可選）。不呼叫時 run_path 直接掛在 module_path 下。"""
        if not self.module_name:
            raise ValueError("Module name must be set before setting site path.")
        self.site_id = site_id
        self.site_path = os.path.join(self.module_path, site_id)
        os.makedirs(self.site_path, exist_ok=True)
```

### 4.2 修改 `set_run_path()`

```python
def set_run_path(self, run_name: str) -> None:
    if not self.module_name:
        raise ValueError("Module name must be set before setting run path.")
    if not run_name:
        raise ValueError("Run name must be provided to set run path.")

    self.run_name = run_name
    base = self.site_path if self.site_path else self.module_path
    run_path = os.path.join(base, self.run_name)
    os.makedirs(run_path, exist_ok=True)
    self.run_path = run_path
```

### 4.3 修改 `_filter_run_folders()`

```python
def _filter_run_folders(self) -> list[str]:
    """篩選出符合實驗資料夾命名規則的資料夾名稱列表。"""
    folder_names = os.listdir(self.base_folder)  # ← 改用 self.base_folder
    run_folder_names = []
    for folder_name in folder_names:
        if folder_name.startswith("20") and len(folder_name) == 15:
            run_folder_names.append(folder_name)
    if not run_folder_names:
        raise FileNotFoundError(f"No run folders found in {self.base_folder}.")
    return run_folder_names
```

### 4.4 路徑結構變化

```
# 現在（三層）
set_module_path("website_crawler")  → runs/<ts>/website_crawler/
set_run_path("default")             → runs/<ts>/website_crawler/default/

# 多站（四層，set_site_path 可選）
set_module_path("website_crawler")  → runs/<ts>/website_crawler/
set_site_path("nculab")             → runs/<ts>/website_crawler/nculab/
set_run_path("default")             → runs/<ts>/website_crawler/nculab/default/

# 單站（不呼叫 set_site_path，向後相容）
set_module_path("website_crawler")  → runs/<ts>/website_crawler/
set_run_path("default")             → runs/<ts>/website_crawler/default/
```

### 4.5 不動的部分

- `save_results_as_json()` / `save_results_as_md()`（路徑已由 `run_path` 決定，自動繼承 site 層級）
- `log_run_paths()`（基於 `run_path`，自動正確）
- `load_latest_*()`（暫留，fallback 用，多站模式下不啟用）
- `_render_query_result_md()` 及其他 MD 渲染方法

---

## 5. 新增 DataManager

### 5.1 職責界線

| 職責 | DataManager | RunManager |
|------|------------|------------|
| 管理 `data/` 目錄 | ✅ | ❌ |
| 管理 `runs/` 目錄 | ❌ | ✅ |
| Publish 結果到持久化目錄 | ✅ | ❌ |
| Discover 歷史執行結果 | ❌ | ✅（暫留 fallback） |
| 掃描可用 site 列表 | ✅ | ❌ |
| 提供 site 資料路徑 | ✅ | ❌ |

### 5.2 介面設計

```python
class DataManager:
    """管理 data/ 目錄下的持久化發布結果。

    職責：
    - publish：將 runs/ 中的執行結果覆蓋發布至 data/
    - discover：掃描 data/ 目錄，提供 site 列表與路徑
    - 不負責 runs/ 的建立或發現（那是 RunManager 的職責）
    """

    def __init__(self, data_folder: str = "data") -> None:
        self.data_folder = data_folder

    # ──────── Publish（寫入 data/）──────

    def publish_crawl_results(
        self, site_id: str, results: dict
    ) -> None:
        """將爬取結果覆蓋發布至 data/webpages/{site_id}/。"""
        site_path = self._webpages_site_path(site_id)
        os.makedirs(os.path.join(site_path, "results"), exist_ok=True)
        with open(os.path.join(site_path, "results.json"), "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

    def publish_markdown(
        self, site_id: str, results: dict, markdown_type: str
    ) -> None:
        """將 Markdown 結果覆蓋發布至 data/webpages/{site_id}/results/。"""
        site_path = self._webpages_site_path(site_id)
        results_dir = os.path.join(site_path, "results")
        os.makedirs(results_dir, exist_ok=True)
        for page_title, result in results.items():
            md_file_path = os.path.join(results_dir, page_title + ".md")
            with open(md_file_path, "w", encoding="utf-8") as f:
                f.write(result[markdown_type])

    def publish_vector_store(
        self, site_id: str, source_db_path: str
    ) -> None:
        """將向量庫從 runs/ 複製至 data/rag/{site_id}/。"""
        dest_dir = self.get_vector_store_path(site_id)
        os.makedirs(dest_dir, exist_ok=True)
        # 複製 milvus.db 或 qdrant_db/ 至 dest_dir

    # ──────── Discover（掃描 data/）──────

    def list_sites(self) -> list[str]:
        """掃描 data/webpages/ 目錄，回傳所有已發佈的 site_id。"""
        webpages_path = os.path.join(self.data_folder, "webpages")
        if not os.path.isdir(webpages_path):
            return []
        return sorted(
            d for d in os.listdir(webpages_path)
            if os.path.isdir(os.path.join(webpages_path, d))
        )

    def get_webpages_path(self, site_id: str) -> str:
        """回傳 data/webpages/{site_id}/ 路徑（供 RAG 讀取）。"""
        return self._webpages_site_path(site_id)

    def get_vector_store_path(self, site_id: str) -> str:
        """回傳 data/rag/{site_id}/ 路徑（供 RAGRegistry 讀取）。"""
        return os.path.join(self.data_folder, "rag", site_id)

    # ──────── 內部方法 ────────

    def _webpages_site_path(self, site_id: str) -> str:
        return os.path.join(self.data_folder, "webpages", site_id)
```

### 5.3 安放位置

建議安放於 `src/app/workflow/data_manager.py`，與 `workflow_manager.py` 同層。

---

## 6. Workflow 函式改動

### 6.1 簽名變化（所有 `run_*` 函式）

```python
# 現在
def run_website_crawler(
    run_manager: RunManager | None = None,
    config_name: str = "default",
    run_name_use_config_name: bool = False,
    **config_overrides,
) -> dict[str, dict] | None:

# 多站後
def run_website_crawler(
    run_manager: RunManager | None = None,
    config_name: str = "default",
    run_name_use_config_name: bool = False,
    site_id: str = "",                            # ← 新增（可選）
    data_manager: DataManager | None = None,       # ← 新增（可選）
    **config_overrides,
) -> dict[str, dict] | None:
```

`site_id` 為空時，所有新邏輯跳過，向後相容現有單站流程。

### 6.2 `run_website_crawler` 完整改動

```python
def run_website_crawler(
    run_manager: RunManager | None = None,
    config_name: str = "default",
    run_name_use_config_name: bool = False,
    site_id: str = "",
    data_manager: DataManager | None = None,
    **config_overrides,
) -> dict[str, dict] | None:
    # ----- 初始化設定和路徑 -----
    website_crawler = WebsiteCrawler()
    config = WebsiteCrawlerConfig.from_toml(config_name, **config_overrides)
    if run_manager is None:
        run_manager = RunManager("website_crawler")
    if site_id:                                   # ← 新增
        run_manager.set_site_path(site_id)        # ← 新增
    if run_name_use_config_name:
        run_manager.set_run_path(config_name)
    else:
        run_manager.set_run_path(config.run_name)
    run_manager.init_module_run_paths()

    # ... 現有爬蟲邏輯（不動）...

    # ----- 儲存至 runs/（歷史紀錄）-----
    save_module_config_as_toml(config, run_manager.module_config_toml_path)
    run_manager.save_results_as_json(crawl_results)
    run_manager.save_results_as_md(crawl_results, "fit_markdown")

    # ----- 發佈至 data/（持久化）-----
    if data_manager and site_id:                  # ← 新增
        data_manager.publish_crawl_results(site_id, crawl_results)
        data_manager.publish_markdown(site_id, crawl_results, "fit_markdown")

    log_session("Website Crawling Completed", style="cyan")
    return crawl_results
```

### 6.3 `run_webpage_image_summarizer` 改動

```python
def run_webpage_image_summarizer(
    run_manager: RunManager | None = None,
    config_name: str = "default",
    run_name_use_config_name: bool = False,
    crawl_results: dict[str, dict] | None = None,
    site_id: str = "",                            # ← 新增
    data_manager: DataManager | None = None,       # ← 新增
    **config_overrides,
) -> dict[str, dict] | None:
    # ... 初始化（含 set_site_path）...

    # ... 現有摘要邏輯（不動）...

    # ----- 儲存至 runs/ -----
    run_manager.save_results_as_json(enhanced_results)
    run_manager.save_results_as_md(enhanced_results, "enhanced_markdown")

    # ----- 發佈至 data/（覆蓋爬取結果為增強版本）-----
    if data_manager and site_id:                  # ← 新增
        data_manager.publish_crawl_results(site_id, enhanced_results)
        data_manager.publish_markdown(site_id, enhanced_results, "enhanced_markdown")

    return enhanced_results
```

### 6.4 `run_rag_build` 改動

```python
def run_rag_build(
    run_manager: RunManager | None = None,
    config_name: str = "default",
    run_name_use_config_name: bool = False,
    webpages_data_use_latest_results: bool = False,  # 保留 fallback
    save_vector_store_to_runs: bool = False,
    site_id: str = "",                               # ← 新增
    data_manager: DataManager | None = None,          # ← 新增
    **config_overrides,
) -> None:
    config = RAGConfig.from_toml(config_name, **config_overrides)

    # ── 多站模式：DataManager 提供路徑 ──
    if site_id and data_manager:
        config.webpages_data_folder_path = data_manager.get_webpages_path(site_id)
        config.milvus_uri = os.path.join(
            data_manager.get_vector_store_path(site_id), "milvus.db"
        )
    # ── 單站 fallback：沿用現有邏輯 ──
    elif webpages_data_use_latest_results:
        webpages_data_folder_path = run_manager.load_latest_summarizer_run_path()
        config.webpages_data_folder_path = webpages_data_folder_path

    # ... 現有 RAG build 邏輯（不動）...

    # ----- publish 向量庫至 data/ -----
    if data_manager and site_id:                  # ← 新增
        data_manager.publish_vector_store(site_id, config.milvus_uri)
```

### 6.5 `run_rag_query` 與 `run_agent`

`run_rag_query` 和 `run_agent` 的改動模式相同：加入 `site_id` 和 `data_manager` 參數（可選），在適當時機呼叫 DataManager。

---

## 7. CLI 與 main.py 改動

### 7.1 CLI dataclass 新增 `site_id`

```python
@dataclass
class WebsiteCrawlerRunConfig:
    run_name: str = "default"
    run_name_use_config_name: bool = False
    site_id: str = ""          # ← 新增

# 其他 RunConfig 類比新增
```

### 7.2 `cli.py` 分派邏輯

```python
# 現在
elif isinstance(cli_arg, WebsiteCrawlerCLI):
    run_manager.set_module_path("website_crawler")
    run_website_crawler(run_manager, **vars(cli_arg.run), **module_config_overrides)

# 多站後
elif isinstance(cli_arg, WebsiteCrawlerCLI):
    run_manager.set_module_path("website_crawler")
    run_website_crawler(
        run_manager,
        data_manager=data_manager,              # ← 新增
        **vars(cli_arg.run),                    # 含 site_id
        **module_config_overrides,
    )
```

### 7.3 `main.py`

```python
def main() -> None:
    run_manager = RunManager()
    data_manager = DataManager()              # ← 新增

    # ----- Website Crawler -----
    run_manager.set_module_path("website_crawler")
    crawl_results = run_website_crawler(
        run_manager=run_manager,
        site_id="nculab",                     # ← 新增
        data_manager=data_manager,            # ← 新增
        **vars(website_crawler_run_config),
    )

    # ... 後續模組類比 ...
```

---

## 8. 設定檔結構（多站後）

### 8.1 RAG 設定檔

`webpages_data_folder_path` 不再需要，由 DataManager 動態提供。此 config 只保留向量庫與檢索參數。

```toml
# configs/rag/nculab.toml
[vector_store]
vector_store_type = "milvus"
collection_name = "webpages_nculab"

[index]
embedding_name = "text-embedding-3-small"

[retriever]
query_mode = "hybrid"
similarity_top_k = 10
hybrid_top_k = 10
```

### 8.2 爬蟲設定檔

```toml
# configs/website_crawler/nculab.toml
[init]
max_depth = 2
content_threshold = 0.25
light_mode = true
wait_for_images = true

[crawl]
url = "https://sites.google.com/site/nculab/labintro"
url_patterns = ["*nculab*"]
allowed_domains = ["sites.google.com"]
exclude_words = ["..."]
```

---

## 9. Agent 整合

### 9.1 Site Discovery 工具

Agent 透過非 system prompt 方式得知可用的 site_id 列表。

```python
def create_site_discovery_tool(data_manager: DataManager) -> StructuredTool:
    """掃描 data/rag/ 目錄，回傳所有已建庫的 site_id 列表。"""

    def _list_sites() -> str:
        sites = data_manager.list_sites()
        return "\n".join(f"- {s}" for s in sites) if sites else "No sites available."

    return StructuredTool(
        name="list_knowledge_bases",
        description="列出所有可用的知識庫 site_id 列表。",
        func=_list_sites,
    )
```

### 9.2 RAGRegistry

管理多個 site 的 RAG 實例，從 `data/rag/{site_id}/` 載入向量庫。

```python
class RAGRegistry:
    """依 site_id 管理多個 RAG 實例。"""

    def __init__(self, data_manager: DataManager) -> None:
        self._data_manager = data_manager
        self._instances: dict[str, RAG] = {}

    def get(self, site_id: str, config_name: str = "default") -> RAG:
        if site_id not in self._instances:
            config = RAGConfig.from_toml(config_name)
            config.webpages_data_folder_path = self._data_manager.get_webpages_path(site_id)
            config.milvus_uri = os.path.join(
                self._data_manager.get_vector_store_path(site_id), "milvus.db"
            )
            self._instances[site_id] = RAGBuilder(config).build()
        return self._instances[site_id]

    def close(self) -> None:
        for rag in self._instances.values():
            rag.close()
```

### 9.3 Tool 簽名

```python
class WebpageRetrieverInput(BaseModel):
    query: str
    site_id: str                    # Agent 決定查哪個網站
    filter_dict: dict | None = None
    similarity_top_k: int | None = None
```

---

## 10. site_id 完整流動路徑

```
                    ┌─────────────────────────────┐
                    │  來源（二擇一或兩者）         │
                    │  1. CLI: --site-id nculab    │
                    │  2. TOML: site_id = "nculab" │
                    └──────────┬──────────────────┘
                               │
                    ┌──────────▼──────────────────┐
                    │  WorkflowConfig / CLI dataclass│
                    │  site_id: str                 │
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

---

## 11. 與 `2026_0818-multi_site_RAG.md` 的映射

| 多站規劃工作項 | 本文檔對應改動 | 關係 |
|--------------|--------------|------|
| 2-1 資料目錄結構重構 | 目錄結構章節 | 直接支持 |
| 2-2 爬蟲設定檔模板化 | 設定檔結構章節 | 直接支持 |
| 2-3 向量庫隔離 | `configs/rag/{site_id}.toml` + `data/rag/{site_id}/` | 直接支持 |
| 2-4 RAG 設定檔 per site | DataManager 動態提供路徑（不需硬編碼） | 簡化了規劃 |
| 2-5 metadata 加入 site_id | 不在本文檔範圍（屬 engine 層改動） | 互不衝突 |
| 2-6 Agent 設定檔 | `get_available_sites()` + `RAGRegistry` | 直接支持 |
| 2-7 腳本化建庫 | CLI `--site-id` 參數 | 直接支持 |
| 3-1 Tool 參數擴充 | `WebpageRetrieverInput.site_id` | 直接支持 |
| 3-2 多 RAG 實例管理 | `RAGRegistry` | 直接支持 |
| 3-3 動態切換 | `RAGRegistry.get(site_id)` | 直接支持 |
| 3-4 Agent prompt | `list_knowledge_bases` 工具 | 直接支持 |
| 3-5 metadata filter | 不在本文檔範圍（屬 engine 層改動） | 互不衝突 |
| 3-6 fallback | 不在本文檔範圍（屬 Agent 邏輯） | 互不衝突 |

---

## 12. 衝突分析與解決

| 衝突 | 解法 |
|------|------|
| `runs/` vs `data/` 兩套目錄定位不明 | 雙系統分離：RunManager 管 `runs/`，DataManager 管 `data/` |
| Agent retriever 向量庫隔離 vs 正式向量庫 | `RAGRegistry` 從 `data/rag/{site_id}/` 載入正式向量庫 |
| discover 不支援多 site 篩選 | `load_latest_*` 暫留 fallback；多站模式下由 DataManager 提供路徑 |
| `webpages_data_use_latest_results` 覆蓋邏輯 | 多站模式下由 DataManager 覆蓋；單站 fallback 保留 |

---

## 13. 實作 Phase

```
Phase 1：基礎設施（不破壞現有流程）
├── RunManager: P0（discover 用 base_folder）+ P1（set_site_path）
├── 新增 DataManager 類別（publish + list_sites + get_*_path）
└── 單站流程不受影響（site_id 為空時所有新邏輯跳過）

Phase 2：目錄重構 + Workflow 接入
├── data/webpages/ 搬移至 data/webpages/nculab/
├── data/rag/results/ 搬移至 data/rag/nculab/
├── 所有 run_* 函式加入 site_id + data_manager 參數（可選）
├── main.py / cli.py 建立 DataManager 並傳入
└── 現有 default.toml RAG config 移除 webpages_data_folder_path 硬編碼

Phase 3：多站生效
├── 爬蟲設定檔模板化（configs/website_crawler/{site_id}.toml）
├── RAG 設定檔 per site（configs/rag/{site_id}.toml）
├── site_id 從 config 或 CLI 注入
└── 第二個學校網站端到端測試

Phase 4：Agent 整合
├── get_available_sites() 工具（掃描 data/rag/）
├── RAGRegistry 從 data/rag/{site_id}/ 載入
├── Agent prompt 調校
└── 多站端到端測試
```

---

## 14. 遷移路徑

```bash
# Phase 2 的目錄搬移（由 migration script 或手動執行）
data/webpages/results.json       → data/webpages/nculab/results.json
data/webpages/results/           → data/webpages/nculab/results/
data/rag/results/milvus.db       → data/rag/nculab/milvus.db
```

---

## 15. 驗證標準

| Phase | 驗證標準 |
|-------|---------|
| **Phase 1** | 單站流程（無 site_id）完全不受影響；`set_site_path` 可選呼叫正確建立四層目錄 |
| **Phase 2** | `data/webpages/nculab/` 內容正確；`run_website_crawler(site_id="nculab")` 同時寫入 `runs/` 和 `data/` |
| **Phase 3** | 能為 2+ 個學校網站分別爬取、建庫，目錄與向量庫完全隔離 |
| **Phase 4** | Agent 收到查詢自動路由至對應 site_id；`list_knowledge_bases` 正確回傳所有可用站點 |
