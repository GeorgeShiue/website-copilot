# 多站 RAG 重構模組分析 (2026/08/19)

> 本文檔針對 `2026_0819-multi_site_RAG.md` M2（多站基礎建設）的範圍，
> 分析並決定四個需要重構的核心模組、各模組重構目的，以及合適的執行順序。

---

## 1. 範圍

對照 M2 的七項工作項（2-1 至 2-7），分析 `src/` 中所有模組後，鎖定以下四個**必須重構**的模組：

| # | 模組路徑 | M2 工作項 | 改動量 |
|---|---------|----------|--------|
| 1 | `src/app/workflow/workflow_manager.py` + `data_manager.py`（新） | 2-1、2-4、2-7 | 大 |
| 2 | `src/app/configs/rag_config.py` | 2-1、2-3、2-4 | 大 |
| 3 | `src/app/engines/rag/rag_factory.py` | 2-5 | 中 |
| 4 | `src/app/workflow/workflow.py` | 2-1、2-7 | 中 |

其餘模組（`webpage_retriever.py`、`agent.py`、`cli.py` 等）在 M2 階段僅需最小程度的準備性改動，核心改造留在 M3/M4。

---

## 2. 各模組重構目的與方法

### 2.1 RunManager (`workflow_manager.py`) + DataManager（新模組）

**現狀問題：**
- `_filter_run_folders()` 和 `load_latest_*()` 系列方法直接引用全域常數 `RUNS_FOLDER_PATH`，忽略 `self.base_folder`，Agent 場景（`base_folder="chats"`）的 discover 永遠搜不到
- 路徑結構為 `base/module/run`，缺少 `site_id` 維度
- `runs/` 與 `data/` 兩套目錄定位不明——RunManager 目前同時肩負歷史紀錄與持久化資料的職責

**重構目的：**
- 修復 `discover` 方法使用 `self.base_folder` 替代硬編碼常數
- 新增 `set_site_path(site_id)` 建立四層路徑 `runs/<ts>/module/site/run`（可選呼叫，不呼叫時向後相容）
- 建立「雙系統分離」架構：**RunManager** 專管 `runs/`（歷史執行紀錄），**DataManager** 專管 `data/`（持久化發布區）

**重構方法：**

1. **修復 discover**：將 `load_latest_results_from_json()` 和 `load_latest_summarizer_run_path()` 中直接引用 `RUNS_FOLDER_PATH` 的地方，全部改為使用 `self.base_folder`；同步修正 `_filter_run_folders()` 的掃描根目錄
2. **新增 `set_site_path(site_id)`**：在 `RunManager` 新增 `site_path` 屬性，`set_site_path()` 在 `module_path` 下建立 `{site_id}/` 子目錄；`set_run_path()` 改為偵測 `site_path` 是否存在，存在時在 `site_path` 下建立 run 路徑，不存在時沿用原有 `module_path` 下的邏輯
3. **向後相容**：不呼叫 `set_site_path()` 時，路徑結構與現有完全相同，所有既有測試與流程不受影響

**路徑結構變化：**

```
# 現在（三層）
set_module_path("website_crawler")  → runs/<ts>/website_crawler/
set_run_path("default")             → runs/<ts>/website_crawler/default/

# 多站（四層，set_site_path 可選）
set_module_path("website_crawler")  → runs/<ts>/website_crawler/
set_site_path("nculab")             → runs/<ts>/website_crawler/nculab/
set_run_path("default")             → runs/<ts>/website_crawler/nculab/default/
```

**DataManager 設計概要：**

DataManager 是本重構新增的模組（`src/app/workflow/data_manager.py`），與 RunManager 的職責界線如下：

| 職責 | DataManager | RunManager |
|------|------------|------------|
| 管理 `data/` 目錄 | ✅ | ❌ |
| 管理 `runs/` 目錄 | ❌ | ✅ |
| Publish 結果到持久化目錄 | ✅ | ❌ |
| Discover 歷史執行結果 | ❌ | ✅（暫留 fallback） |
| 掃描可用 site 列表 | ✅ | ❌ |
| 提供 site 資料路徑 | ✅ | ❌ |

主要介面：
- **Publish**：`publish_crawl_results()`、`publish_markdown()`、`publish_vector_store()`
- **Discover**：`list_sites()`、`get_webpages_path()`、`get_vector_store_path()`

**site_id 流動路徑：**

```
    CLI: --site-id nculab  ──┐
                             ├──→ WorkflowConfig → ┬─ RunManager.set_site_path()
    TOML: site_id = "nculab" ─┘                    ├─ DataManager.publish_*()
                                                   └─ RAGConfig.site_id（動態路徑）
```

**遷移路徑：**

既有的單站資料需搬移至 per-site 目錄結構：

```bash
data/webpages/results.json       → data/webpages/nculab/results.json
data/webpages/results/           → data/webpages/nculab/results/
data/rag/results/milvus.db       → data/rag/nculab/milvus.db
```

---

### 2.2 RAGConfig (`rag_config.py`)

**現狀問題：**
- 模組級硬編碼：`WEBPAGES_DATA_FOLDER_PATH = "data/webpages"`、`RAG_RESULTS_FOLDER_PATH = "data/rag/results"`
- 所有 TOML 設定檔（`configs/rag/default.toml`、`milvus.toml`）的路徑欄位寫死為單站路徑
- `RAGConfig` dataclass 沒有 `site_id` 欄位，`from_toml()` 無法動態解析路徑

**重構目的：**
- 移除模組級硬編碼常數，路徑改為 `site_id` 動態解析（由 DataManager 提供）
- `RAGConfig` 新增 `site_id: str = ""` 欄位
- TOML 中的 `webpages_data_folder_path`、`milvus_uri`、`qdrant_db_folder_path` 改為可選，未指定時由 DataManager 根據 `site_id` 動態提供預設值

**重構方法：**

1. **新增 `site_id` 欄位**：在 `RAGConfig` dataclass 加入 `site_id: str = ""`，加入 `INIT_KEYS` 集合
2. **路徑動態解析**：將 `WEBPAGES_DATA_FOLDER_PATH` 和 `RAG_RESULTS_FOLDER_PATH` 等硬編碼常數改為函式，接收 `site_id` 回傳對應路徑（如 `f"data/webpages/{site_id}"`）；`site_id` 為空時回傳原有預設值（向後相容）
3. **`from_toml()` 改造**：TOML 檔案中的 `webpages_data_folder_path`、`milvus_uri`、`qdrant_db_folder_path` 改為可選欄位；未指定時在 `__post_init__` 中以 `site_id` 動態產生預設路徑
4. **TOML 設定檔更新**：`configs/rag/default.toml` 和 `milvus.toml` 移除硬編碼路徑，改為僅在 per-site 設定檔（如 `configs/rag/nculab.toml`）中明確指定路徑

**TOML 設定檔前後對比：**

```
# 現在：default.toml（硬編碼單站路徑）
[init]
webpages_data_folder_path = "data/webpages"

[vector_store]
milvus_uri = "data/rag/results/milvus.db"
collection_name = "webpages"

# 重構後：default.toml（路徑欄位移除，由 site_id 動態解析）
[init]
# webpages_data_folder_path 由 site_id 動態產生：data/webpages/{site_id}

[vector_store]
# milvus_uri 由 site_id 動態產生：data/rag/{site_id}/milvus.db
collection_name = "webpages"

# 重構後：nculab.toml（per-site 設定檔，可覆寫路徑）
[init]
site_id = "nculab"

[vector_store]
collection_name = "webpages_nculab"  # 每站獨立 collection
```

**site_id 注入路徑：**

```
    CLI: --site-id nculab
         │
         ▼
    RAGConfig.from_toml("default", site_id="nculab")
         │
         ▼  __post_init__ 動態產生路徑
    webpages_data_folder_path = "data/webpages/nculab"
    milvus_uri = "data/rag/nculab/milvus.db"
    collection_name = "webpages_nculab"（或沿用 default 的 "webpages"）
```

**M2 工作項對應：**

| 工作項 | 改動內容 |
|-------|---------|
| 2-1 目錄重構 | 路徑從 `data/webpages` → `data/webpages/{site_id}/` |
| 2-3 向量庫隔離 | 路徑從 `data/rag/results/milvus.db` → `data/rag/{site_id}/milvus.db` |
| 2-4 RAG 設定檔 per site | `from_toml()` 支援 `site_id` 注入，路徑欄位可選 |

---

### 2.3 rag_factory.py

**現狀問題：**
- `NodePipelineBuilder._build_file_metadata()` 產出的 node metadata 僅有 `page_title`、`page_url`、`page_type`、`published_date`、`description`，缺少 `site_id`
- 多站模式下，不同網站的同名頁面（如都有「成員」頁面）會在向量庫中混淆，metadata filter 無法按站點過濾

**重構目的：**
- `NodePipelineBuilder._build_file_metadata()` 新增 `site_id` 參數，寫入 `file_metadata["site_id"] = site_id`
- `RAGBuilder.build_nodes()` 將 `site_id` 傳入 `NodePipelineBuilder`
- 確保所有 node 的 metadata 包含 `site_id` 欄位，作為跨站檢索的 filter 基礎

**重構方法：**

1. **`_build_file_metadata()` 簽名擴充**：新增 `site_id: str` 參數，在回傳的 `file_metadata` dict 中加入 `"site_id": site_id`；由於此方法透過 `functools.partial` 綁定為 `SimpleDirectoryReader` 的 `file_metadata` callback，需同步修改 `build()` 方法的 `partial()` 呼叫，將 `site_id` 注入
2. **`build()` 簽名擴充**：新增 `site_id: str = ""` 參數，傳入 `partial(self._build_file_metadata, results_json, site_id=site_id)`
3. **`RAGBuilder.build_nodes()` 傳遞**：從 `RAGBuilder` 的 `config.site_id` 取得值，傳入 `NodePipelineBuilder.build()`
4. **向後相容**：`site_id` 預設為空字串時，node metadata 中 `site_id` 為 `""`，與現有單站流程行為一致

**Node metadata 前後對比：**

```
# 現在：_build_file_metadata() 回傳
{
    "page_title": "labintro",
    "page_url": "https://sites.google.com/site/nculab/labintro",
    "page_type": "general",
    "published_date": "2025-01-15",
    "description": "實驗室介紹"
}

# 重構後：新增 site_id 欄位
{
    "page_title": "labintro",
    "page_url": "https://sites.google.com/site/nculab/labintro",
    "page_type": "general",
    "published_date": "2025-01-15",
    "description": "實驗室介紹",
    "site_id": "nculab"                    ← 新增
}
```

**site_id 傳遞鏈：**

```
    RAGConfig.site_id = "nculab"
         │
         ▼
    RAGBuilder.build_nodes(rag)
         │  取 self.config.site_id
         ▼
    NodePipelineBuilder.build(md_folder, results_json, site_id="nculab")
         │  注入 partial callback
         ▼
    _build_file_metadata(results_json, file_path, site_id="nculab")
         │  回傳 file_metadata["site_id"] = "nculab"
         ▼
    SimpleDirectoryReader 讀取 .md → 每個 Document 帶有 site_id metadata
         │
         ▼
    IngestionPipeline → BaseNode.metadata["site_id"] = "nculab"
```

**M2 工作項對應：**

| 工作項 | 改動內容 |
|-------|---------|
| 2-5 metadata 加入 site_id | node metadata 注入 `site_id`，供 M3 的 metadata filter 過濾使用 |

---

### 2.4 Workflow (`workflow.py`)

**現狀問題：**
- 五個 `run_*` 函式各有 ~20 行相同的初始化樣板（建立 RunManager → set_run_path → init_module_run_paths）
- 沒有 `site_id` 參數，無法區分不同網站的執行
- 沒有 DataManager 整合，爬取/摘要完成後只寫入 `runs/`，不會持久化到 `data/`

**重構目的：**
- 所有 `run_*` 函式加入 `site_id: str = ""` 和 `data_manager: DataManager | None = None` 參數（可選，為空時跳過新邏輯，向後相容）
- 在各函式結尾呼叫 `data_manager.publish_*()` 將結果寫入 `data/webpages/{site_id}/` 或 `data/rag/{site_id}/`
- 提取共享的初始化樣板為 helper，減少重複

**重構方法：**

1. **提取共享 helper**：將每個 `run_*` 函式開頭重複的初始化邏輯（RunManager 建立、set_run_path、init_module_run_paths、logging 設定）抽取為 `_init_workflow()` helper 函式，各 `run_*` 函式改為呼叫 helper 取得初始化後的 RunManager
2. **函式簽名擴充**：所有 `run_*` 函式（`run_website_crawler`、`run_webpage_image_summarizer`、`run_rag_build`、`run_rag_query`、`run_agent`）加入 `site_id: str = ""` 和 `data_manager: DataManager | None = None` 兩個可選參數
3. **`site_id` 注入路徑**：在 helper 或各函式中，當 `site_id` 非空時呼叫 `run_manager.set_site_path(site_id)`；同時將 `site_id` 傳入下游（如 `RAGConfig` 的 `config_overrides`）
4. **DataManager publish**：在各函式完成核心工作後、回傳結果前，當 `data_manager` 非空時呼叫對應的 `publish_*()` 方法，將結果持久化到 `data/` 目錄
5. **`run_rag_build` 特殊處理**：`webpages_data_use_latest_results=True` 時，改為從 DataManager 取得 `data/webpages/{site_id}/` 路徑，而非從 RunManager discover

**初始化樣板前後對比：**

```
# 現在：每個 run_* 函式開頭重複 ~8 行
def run_website_crawler(run_manager=None, config_name="default", ...):
    config = WebsiteCrawlerConfig.from_toml(config_name, **config_overrides)
    if run_manager is None:
        run_manager = RunManager("website_crawler")
    if run_name_use_config_name:
        run_manager.set_run_path(config_name)
    else:
        run_manager.set_run_path(config.run_name)
    run_manager.init_module_run_paths()
    # ... 核心邏輯 ...

# 重構後：helper 函式封裝初始化
def _init_workflow(module_name, config, run_name_use_config_name, run_manager=None):
    if run_manager is None:
        run_manager = RunManager(module_name)
    if run_name_use_config_name:
        run_manager.set_run_path(config.config_name)
    else:
        run_manager.set_run_path(config.run_name)
    run_manager.init_module_run_paths()
    return run_manager

def run_website_crawler(run_manager=None, config_name="default",
                        site_id="", data_manager=None, ...):
    config = WebsiteCrawlerConfig.from_toml(config_name, **config_overrides)
    run_manager = _init_workflow("website_crawler", config, run_name_use_config_name, run_manager)
    if site_id:
        run_manager.set_site_path(site_id)
    # ... 核心邏輯 ...
    if data_manager and site_id:
        data_manager.publish_crawl_results(site_id, crawl_results)
    return crawl_results
```

**各函式的 DataManager publish 對應：**

| 函式 | publish 方法 | 产出 |
|------|-------------|------|
| `run_website_crawler` | `publish_crawl_results(site_id, results)` | `data/webpages/{site_id}/results.json` + `results/*.md` |
| `run_webpage_image_summarizer` | `publish_markdown(site_id, enhanced_results)` | `data/webpages/{site_id}/results/*.md`（含圖片摘要） |
| `run_rag_build` | `publish_vector_store(site_id, config)` | `data/rag/{site_id}/milvus.db` 或 `qdrant_db/` |
| `run_rag_query` | — | 不需 publish（query 結果留在 `runs/`） |
| `run_agent` | — | 不需 publish（聊天記錄留在 `chats/`） |

**M2 工作項對應：**

| 工作項 | 改動內容 |
|-------|---------|
| 2-1 目錄重構 | 爬取/摘要結果從 `runs/` publish 到 `data/` |
| 2-7 腳本化建庫 | `run_*` 函式接受 `site_id` 參數；main.py pipeline 改為支援 `--site-id` |

---

## 3. 重構順序

四個模組之間有明確的依賴鏈，合適的重構順序如下：

```
Phase 1：RunManager（基礎設施）
    ↓
Phase 2：RAGConfig（路徑動態化）
    ↓
Phase 3：rag_factory.py（metadata 注入）
    ↓
Phase 4：workflow.py（端到端串接）
```

### 依賴關係圖

```
RunManager + DataManager
  set_site_path()  ──────────────────────────┐
  修復 discover    ─────┐                      │
  DataManager      ─────┤                      │
  publish + paths  ─────┘                      │
                        │                      │
                        ▼                      │
                    RAGConfig                  │
                    site_id 動態解析            │
                    TOML 路徑可選              │
                        │                      │
                        ▼                      │
                    rag_factory.py             │
                    node metadata 注入 site_id │
                        │                      │
                        ▼                      │
                    workflow.py ◄──────────────┘
                    site_id 參數 + DataManager publish
```

### 各 Phase 說明

| Phase | 模組 | 前置 | 說明 |
|-------|------|------|------|
| **1** | RunManager + DataManager | 無 | 修復 discover + `set_site_path()`；建立 DataManager（publish + list_sites + get_*_path），為後續模組提供四層路徑能力與 `data/` 管理 |
| **2** | RAGConfig | Phase 1 | 路徑動態化依賴 RunManager 的 site_path 建立機制；改完後 TOML 設定檔可支援 per-site 配置 |
| **3** | rag_factory.py | Phase 2 | node metadata 注入 site_id 需要 RAGConfig 能正確解析 per-site 路徑 |
| **4** | workflow.py | Phase 1+2 | publish 到 `data/` 需要 RunManager 的路徑能力、DataManager 的 publish 方法、以及 RAGConfig 的 site_id 解析 |

### 驗證標準

| Phase | 驗證標準 |
|-------|---------|
| **Phase 1** | 單站流程（無 site_id）完全不受影響；`set_site_path` 正確建立四層目錄；Agent 的 `load_latest_*` 不再搜不到；`DataManager` 可正確 publish 到 `data/` 並 `list_sites()` 回傳可用站點 |
| **Phase 2** | `RAGConfig.from_toml("default", site_id="nculab")` 正確解析到 `data/webpages/nculab/` 和 `data/rag/nculab/milvus.db` |
| **Phase 3** | 建庫後的 node metadata 含有 `site_id` 欄位；可用 `{"site_id": "nculab"}` 過濾檢索結果 |
| **Phase 4** | `run_website_crawler(site_id="nculab")` 同時寫入 `runs/` 和 `data/webpages/nculab/`；main.py 的 `--site-id` 參數正常運作 |
