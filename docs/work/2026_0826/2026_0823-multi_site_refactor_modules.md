# 多站 RAG 重構模組分析 (2026/08/23)

> 本文檔針對 `2026_0819-multi_site_RAG.md` M2（多站基礎建設）的範圍，
> 分析並決定四個需要重構的核心模組、各模組重構目的，以及合適的執行順序。

---

## 1. 範圍

對照 M2 的七項工作項（2-1 至 2-7），分析 `src/` 中所有模組後，鎖定以下四個**必須重構**的模組：

| # | 模組路徑 | M2 工作項 | 改動量 |
|---|---------|----------|--------|
| 1 | `src/app/workflow/run_manager.py` + `data_manager.py`（新） | 2-1、2-4、2-7 | 大 |
| 2 | `src/app/configs/rag_config.py` | 2-1、2-3、2-4 | 大 |
| 3 | `src/app/engines/rag/rag_factory.py` | 2-5 | 中 |
| 4 | `src/app/workflow/workflow.py` | 2-1、2-7 | 中 |

其餘模組（`webpage_retriever.py`、`agent.py`、`cli.py` 等）在 M2 階段僅需最小程度的準備性改動，核心改造留在 M3/M4。

---

## 2. 各模組重構目的與方法

### 2.1 RunManager (`run_manager.py`) + DataManager（新模組）

**現狀問題：**
- `_filter_run_folders()` 和 `load_latest_*()` 系列方法直接引用全域常數 `RUNS_FOLDER_PATH`，忽略 `self.base_folder`，Agent 場景（`base_folder="chats"`）的 discover 永遠搜不到
- 路徑結構為 `base/module/run`，缺少 `site_id` 維度
- `runs/` 與 `data/` 兩套目錄定位不明——RunManager 目前同時肩負歷史紀錄與持久化資料的職責

**重構目的：**
- 修復 `discover` 方法使用 `self.base_folder` 替代硬編碼常數
- 新增 `set_site_path(site_id)` 建立四層路徑 `runs/<ts>/module/site/run`（必要呼叫）
- 建立「雙系統分離」架構：**RunManager** 專管 `runs/`（歷史執行紀錄），**DataManager** 專管 `data/`（持久化發布區）

**重構方法：**

1. **修復 discover**：將 `load_latest_results_from_json()` 和 `load_latest_summarizer_run_path()` 中直接引用 `RUNS_FOLDER_PATH` 的地方，全部改為使用 `self.base_folder`；同步修正 `_filter_run_folders()` 的掃描根目錄
2. **新增 `set_site_path(site_id)`**：在 `RunManager` 新增 `site_path` 屬性，`set_site_path()` 在 `module_path` 下建立 `{site_id}/` 子目錄；`set_run_path()` 改為偵測 `site_path` 是否存在，存在時在 `site_path` 下建立 run 路徑，不存在時沿用原有 `module_path` 下的邏輯
3. **`site_id` 為必要參數**：所有使用 `RunManager` 的流程必須提供 `site_id` 並呼叫 `set_site_path()`，不保留向後相容的三層路徑模式

**路徑結構變化：**

```
# 現在（三層，無 site_id）
set_module_path("website_crawler")  → runs/<ts>/website_crawler/
set_run_path("default")             → runs/<ts>/website_crawler/default/

# 重構後（四層，set_site_path 為必要呼叫）
set_module_path("website_crawler")  → runs/<ts>/website_crawler/
set_site_path("nculab")             → runs/<ts>/website_crawler/nculab/    ← 必要
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
    TOML: [init] site_id = "nculab"  ──→ Config dataclass.site_id（必要欄位）
                                              │
                                              ├─→ RunManager.set_site_path()（必要呼叫）
                                              ├─→ DataManager.publish_*()
                                              └─→ RAGConfig.site_id（動態路徑解析）
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
- 移除模組級硬編碼常數，路徑改為 `site_id` 動態解析
- `RAGConfig` 新增 `site_id: str` 欄位（必要，無預設值）
- TOML 中的 `webpages_data_folder_path`、`milvus_uri`、`qdrant_db_folder_path` 改為可選，未指定時由 `site_id` 動態產生預設路徑

**重構方法：**

1. **新增 `site_id` 欄位**：在 `RAGConfig` dataclass 加入 `site_id: str`（無預設值，必要欄位），加入 `INIT_KEYS` 集合
2. **路徑動態解析**：將 `WEBPAGES_DATA_FOLDER_PATH` 和 `RAG_RESULTS_FOLDER_PATH` 等硬編碼常數改為函式，接收 `site_id` 回傳對應路徑（如 `f"data/webpages/{site_id}"`）
3. **`from_toml()` 改造**：TOML 檔案中的 `webpages_data_folder_path`、`milvus_uri`、`qdrant_db_folder_path` 改為可選欄位；未指定時在 `__post_init__` 中以 `site_id` 動態產生預設路徑
4. **TOML 設定檔更新**：所有 TOML 的 `[init]` section 必須包含 `site_id` 欄位；路徑欄位可移除（由 `site_id` 動態解析）

**TOML 設定檔前後對比：**

```
# 現在：default.toml（硬編碼單站路徑，無 site_id）
[init]
webpages_data_folder_path = "data/webpages"

[vector_store]
milvus_uri = "data/rag/results/milvus.db"
collection_name = "webpages"

# 重構後：所有 TOML 必須在 [init] 指定 site_id
# default.toml（路徑欄位移除，由 site_id 動態解析）
[init]
site_id = "nculab"                          # ← 必要欄位
# webpages_data_folder_path 由 site_id 動態產生：data/webpages/nculab

[vector_store]
# milvus_uri 由 site_id 動態產生：data/rag/nculab/milvus.db
collection_name = "webpages_nculab"         # 每站獨立 collection

# nculab.toml（per-site 設定檔，結構相同）
[init]
site_id = "nculab"

[vector_store]
collection_name = "webpages_nculab"
```

**site_id 注入路徑：**

```
    TOML: [init] site_id = "nculab"
         │
         ▼
    RAGConfig.from_toml("default")
         │  從 TOML 讀取 site_id = "nculab"
         ▼  __post_init__ 動態產生路徑
    webpages_data_folder_path = "data/webpages/nculab"
    milvus_uri = "data/rag/nculab/milvus.db"
    collection_name = "webpages_nculab"
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

1. **`_build_file_metadata()` 簽名擴充**：新增 `site_id: str` 參數（必要），在回傳的 `file_metadata` dict 中加入 `"site_id": site_id`；由於此方法透過 `functools.partial` 綁定為 `SimpleDirectoryReader` 的 `file_metadata` callback，需同步修改 `build()` 方法的 `partial()` 呼叫，將 `site_id` 注入
2. **`build()` 簽名擴充**：新增 `site_id: str` 參數（必要），傳入 `partial(self._build_file_metadata, results_json, site_id=site_id)`
3. **`RAGBuilder.build_nodes()` 傳遞**：從 `RAGBuilder` 的 `config.site_id` 取得值，傳入 `NodePipelineBuilder.build()`
4. 所有 node 的 metadata 必定包含 `site_id` 欄位，作為跨站檢索的 filter 基礎

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
- 所有 `run_*` 函式加入 `site_id: str`（必要）和 `data_manager: DataManager | None = None` 參數
- 在各函式結尾呼叫 `data_manager.publish_*()` 將結果寫入 `data/webpages/{site_id}/` 或 `data/rag/{site_id}/`
- 提取共享的初始化樣板為 helper，減少重複

**重構方法：**

1. **提取共享 helper**：將每個 `run_*` 函式開頭重複的初始化邏輯（RunManager 建立、set_run_path、init_module_run_paths、logging 設定）抽取為 `_init_workflow()` helper 函式，各 `run_*` 函式改為呼叫 helper 取得初始化後的 RunManager
2. **函式簽名擴充**：所有 `run_*` 函式（`run_website_crawler`、`run_webpage_image_summarizer`、`run_rag_build`、`run_rag_query`、`run_agent`）加入 `site_id: str`（必要）和 `data_manager: DataManager | None = None` 兩個參數
3. **`site_id` 注入路徑**：在 helper 或各函式中，無條件呼叫 `run_manager.set_site_path(site_id)`；同時將 `site_id` 傳入下游（如 `RAGConfig` 的 `config_overrides`）
4. **DataManager publish**：在各函式完成核心工作後、回傳結果前，當 `data_manager` 非空時呼叫對應的 `publish_*()` 方法，將結果持久化到 `data/` 目錄
5. **`run_rag_build` 特殊處理**：`webpages_data_use_latest_results=True` 時，從 DataManager 取得 `data/webpages/{site_id}/` 路徑（不再 fallback 到 RunManager discover）

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

# 重構後：helper 函式封裝初始化 + site_id 為必要
def _init_workflow(module_name, config, run_name_use_config_name,
                   run_manager=None, site_id=""):
    if run_manager is None:
        run_manager = RunManager(module_name)
    if run_name_use_config_name:
        run_manager.set_run_path(config.config_name)
    else:
        run_manager.set_run_path(config.run_name)
    run_manager.init_module_run_paths()
    run_manager.set_site_path(site_id)          # ← 必要呼叫
    return run_manager

def run_website_crawler(run_manager=None, config_name="default",
                        site_id="nculab", data_manager=None, ...):
    config = WebsiteCrawlerConfig.from_toml(config_name, **config_overrides)
    run_manager = _init_workflow("website_crawler", config,
                                 run_name_use_config_name, run_manager, site_id)
    # ... 核心邏輯（無 if site_id 守譯）...
    if data_manager:
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

四個核心模組之間有明確的依賴鏈，加上 Config 層、CLI 層與測試的配套改動，完整重構順序如下：

```
Phase A：Config 層（site_id 加入所有 dataclass + TOML）
    ↓
Phase B：RunManager + DataManager（§2.1，基礎設施）
    ↓
Phase C：RAGConfig（§2.2，路徑動態化）
    ↓
Phase D：rag_factory.py（§2.3，metadata 注入）
    ↓
Phase E：workflow.py（§2.4，端到端串接）
    ↓
Phase F：CLI / main.py / workflow_config.py（接通 site_id 入口）
    ↓
Phase G：測試更新
    ↓
Phase H：文件更新
```

### 依賴關係圖

```
Phase A: Config 層
  所有 dataclass 加入 site_id: str（必要）
  所有 TOML [init] 加入 site_id = "xxx"
    │
    ▼
Phase B: RunManager + DataManager
  set_site_path()（必要呼叫）
  修復 discover + DataManager publish
    │
    ▼
Phase C: RAGConfig
  路徑動態化（site_id 驅動）
  TOML 路徑欄位可選
    │
    ▼
Phase D: rag_factory.py
  node metadata 注入 site_id
    │
    ▼
Phase E: workflow.py
  run_* 函式：site_id 必要 + DataManager publish
    │
    ▼
Phase F: CLI / main.py
  workflow_config.py BaseRunConfig 加入 site_id
  cli.py 接通 --run.site-id
  main.py 從 Config 取 site_id 傳入
    │
    ▼
Phase G: 測試
  移除向後相容測試
  所有 run_* 呼叫加入 site_id
    │
    ▼
Phase H: 文件
  README.md / project.md 更新 CLI 範例
```

### 各 Phase 說明

| Phase | 模組 | 前置 | 說明 |
|-------|------|------|------|
| **A** | 所有 Config dataclass + TOML | 無 | `WebsiteCrawlerConfig`、`RAGConfig`、`WebpageImageSummarizerConfig`、`AgentConfig` 加入 `site_id: str`（必要）；所有 TOML `[init]` 加入 `site_id`；`SECTIONS_TO_KEYS` 的 `INIT_KEYS` 加入 `site_id` |
| **B** | RunManager + DataManager | Phase A | 修復 discover + `set_site_path()` 改為必要呼叫；DataManager publish + list_sites + get_*_path |
| **C** | RAGConfig | Phase A | 路徑動態化（`site_id` 驅動）；硬編碼常數改為函式；`__post_init__` 動態產生預設路徑 |
| **D** | rag_factory.py | Phase C | `site_id` 為必要參數，node metadata 必定含 `site_id` |
| **E** | workflow.py | Phase A+B | `_init_workflow()` 無條件呼叫 `set_site_path`；`run_*` 函式 `site_id` 必要；`run_agent()` 修正 `set_site_path` 後重建 `RunManager` 的 bug |
| **F** | CLI / main.py | Phase A+E | `workflow_config.py` 的 `BaseRunConfig` 加入 `site_id: str = "default"`；`main.py` 從 Config 取 `site_id` 傳入 |
| **G** | 測試 | Phase B-E | `test_runmanager_datamanager.py` 移除向後相容測試；`test_module.py` 所有 `run_*` 呼叫加入 `site_id` |
| **H** | 文件 | Phase A-H | `README.md` CLI 範例加入 `--run.site-id`；`project.md` 更新使用方式 |

### 驗證標準

| Phase | 驗證標準 |
|-------|---------|
| **A** | 所有 Config 的 `from_toml()` 不傳 `site_id` 時 `TypeError`；所有 TOML 可正確解析 |
| **B** | `set_site_path` 正確建立四層目錄；Agent 的 `load_latest_*` 正常運作；`DataManager` 可正確 publish 到 `data/` 並 `list_sites()` 回傳可用站點 |
| **C** | `RAGConfig.from_toml("default")`（TOML 含 `site_id="nculab"`）正確解析到 `data/webpages/nculab/` 和 `data/rag/nculab/milvus.db` |
| **D** | 建庫後的 node metadata 含有 `site_id` 欄位；可用 `{"site_id": "nculab"}` 過濾檢索結果 |
| **E** | `run_website_crawler(config_name="nculab")`（TOML 含 `site_id`）同時寫入 `runs/` 和 `data/webpages/nculab/` |
| **F** | CLI `website-crawler-cli --run.config-name nculab` 正常運作（`site_id` 從 TOML 讀取） |
| **G** | 所有 pytest 通過（`-m slow` 端到端 + 單元測試） |
| **H** | README.md 的 CLI 範例與實際執行結果一致 |

---

## 4. 決策紀錄

### 4.1 `site_id` 為必要參數（2026-08-23）

**決策**：`site_id` 從可選參數改為必要參數，移除所有向後相容的三層路徑模式。

**理由**：
1. 多站 RAG 是本分支（`dev-multi-site-RAG`）的核心目標，單站模式已無存在必要
2. 必要參數可於型態層級（Python `TypeError`）即時發現遺漏，避免執行到一半才因路徑錯誤而失敗
3. 移除 `if site_id:` 守譯可減少分支複雜度，讓所有流程的路徑結構一致（四層）
4. TOML 設定檔必須明確指定 `site_id`，避免隱式的空字串預設值造成誤用

**影響範圍**：

| 層級 | 改動 |
|------|------|
| Config dataclass | `site_id: str`（無預設值）加入 `WebsiteCrawlerConfig`、`RAGConfig`、`WebpageImageSummarizerConfig`、`AgentConfig` |
| TOML 設定檔 | 所有 `[init]` section 必須包含 `site_id = "xxx"` |
| `workflow.py` | 所有 `run_*` 函式 `site_id: str`（必要）；`_init_workflow()` 無條件呼叫 `set_site_path()` |
| `workflow_config.py` | `BaseRunConfig` 加入 `site_id: str = "default"`（CLI 入口預設值） |
| CLI | 使用者可透過 `--run.site-id` 或 TOML 指定 |
| `rag_factory.py` | `site_id` 為必要參數，node metadata 必定含 `site_id` |
| 測試 | 移除向後相容測試；所有 `run_*` 呼叫加入 `site_id` |
| 文件 | CLI 範例加入 `--run.site-id` |

**已知 bug 修正**：`run_agent()` 第 504-508 行 `set_site_path` 後重建 `RunManager` 會覆蓋 `site_path`，需在 Phase E 一併修正。

---

### 4.2 移除 `collection_name`，直接使用 `site_id`（2026-08-23）

**決策**：移除 `RAGConfig.collection_name` 欄位，向量庫的 collection name 直接使用 `site_id`。

**理由**：
1. `collection_name` 在多站模式下與 `site_id` 一一對應，無獨立存在的必要
2. 減少設定檔的冗餘欄位，降低配置錯誤風險
3. 確保 collection name 與站點識別碼一致，避免命名不匹配

**影響範圍**：

| 層級 | 改動 |
|------|------|
| `rag_config.py` | 移除 `DEFAULT_COLLECTION_NAME`、`collection_name` 欄位、`VECTOR_STORE_KEYS` 中的 `collection_name`、`_validate_config` 中的 `collection_name` 驗證 |
| `rag_factory.py` | `VectorStoreBuilder.build()` 呼叫改為 `collection_name=self.config.site_id` |
| `workflow.py` | 查詢結果 dict 中 `collection_name` 改為 `config.site_id` |
| TOML 設定檔 | 移除所有 `[vector_store]` 中的 `collection_name` 欄位 |

**RAG 設定檔前後對比**：

```toml
# 改動前
[vector_store]
vector_store_type = "milvus"
collection_name = "webpages_nculab"

# 改動後
[vector_store]
vector_store_type = "milvus"
# collection_name 由 site_id 自動同步
```

