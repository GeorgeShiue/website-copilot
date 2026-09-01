# 開發實作紀錄 (2026/08/18–08/28)

> 彙整 `docs/work/2026_0826/` 中所有規劃文件的實作規格與程式碼設計。各規劃文件保留動機與決策面內容，實作細節集中於此。

---

## 1. HTML 日期擷取

從 `CrawlResult.html` 解析結構化日期標籤，回傳 `{"published_date": "...", "modified_date": "..."}`。

**解析優先級**（由高到低）：JSON-LD `datePublished` → OG `article:published_time` → `<time datetime>` → Generic meta `date`/`pubdate` → Dublin Core `dc.date` → HTTP `Last-Modified`。所有日期經 `_normalize_to_iso8601()` 標準化為 `YYYY-MM-DD`。

**變更範圍**：

| 檔案 | 變更 |
|------|------|
| `website_crawler.py` | 新增 `_extract_date_from_html()`（六層策略）；`_extract_metadata()` 新增 `html` / `response_headers` 參數；`_extract_crawl_results_data()` 呼叫端傳入 HTML/headers |
| `rag_factory.py` | `_build_file_metadata()` 新增 `published_date` 注入 |
| `rag_helper.py` | `MarkdownDateExtractor._extract_date()` 新增 Strategy 0：優先從 `node.metadata["published_date"]` 取得 |

**results.json 變更**：`metadata` 新增 `published_date` / `modified_date` 欄位。

**資料流**：HTML → `_extract_date_from_html()` → results.json → node metadata → MarkdownDateExtractor（優先使用；無資料時 fallback 至原有四層文字推斷）。

---

## 2. Engines 重構 — Import 變更

| 原 import | 新 import | 受影響檔案 |
|-----------|-----------|-----------|
| `app.engines.html_date_extractor` | `utils.html_date_extractor` | `website_crawler.py`、test |
| `app.engines.markdown_cleaner` | `utils.markdown_cleaner` | `website_crawler.py` |
| `app.engines.rag_factory.RAGBuilder` | `app.engines.rag.RAGBuilder` | `workflow.py`、`webpage_retriever.py` |
| `app.engines.rag_eval_prompts.*` | `app.engines.rag.rag_eval_prompts.*` | `rag_factory.py` |

---

## 3. RunManager Refactor（Phase A–H）

### 3-1. 四層路徑結構

所有 `runs/` 路徑從三層（`module/run_name/`）改為四層（`module/site/run_name/`）：

```
runs/<ts>/website_crawler/nculab/default/
data/webpages/nculab/       → results.json + results/
data/rag/nculab/            → milvus.db/
```

### 3-2. RunManager 新增

`set_site_path(site_id)` 建立 `runs/<ts>/module/site/` 路徑；`set_run_path()` 優先使用 `site_path` 作為 base。`_filter_run_folders()` 改用 `self.base_folder`。

### 3-3. DataManager（`src/app/workflow/data_manager.py`）

| 方法 | 功能 |
|------|------|
| `publish_crawl_results()` | 覆蓋發布至 `data/webpages/{site_id}/` |
| `publish_markdown()` | 發布 Markdown 至 `data/webpages/{site_id}/results/` |
| `publish_vector_store()` | 複製向量庫至 `data/rag/{site_id}/` |
| `publish_run_metadata()` | 一次複製 `module_config.toml` + `run_config.toml` + `terminal.log` |
| `list_sites()` / `site_exists()` | 掃描 `data/webpages/` |

### 3-4. site_id 唯一來源

> ⚠️ `BaseModuleConfig.site_id` 已被 §14 移除。目前 site_id 由各子類自行宣告（TOML `[init]` section），`AgentConfig` 無 site_id。

TOML `[init]` section → `BaseModuleConfig.site_id` → 分流至 RunManager（`set_site_path`）、DataManager（`publish_*`）、RAGConfig（路徑動態產生）。

### 3-5. CLI publish 控制

`BaseRunConfig.publish: bool = False`；cli.py 分派前 `pop("publish")` 避免洩漏進 config_overrides，條件建立 DataManager。

```bash
uv run python src/cli.py website-crawler-cli              # publish=False
uv run python src/cli.py website-crawler-cli --run.publish  # 發布至 data/
```

### 3-6. 實作進度

| Phase | 狀態 | 改動 |
|-------|------|------|
| A：Config 層 | ✅ | 所有 Config dataclass + 21 個 TOML 加入 `site_id`，移除 `collection_name` |
| B：RunManager + DataManager | ✅ | `run_manager.py`、`data_manager.py`（新）、`workflow.py` |
| C：RAGConfig 路徑動態化 | ✅ | `webpages_data_folder_path` / `milvus_uri` 由 `site_id` 動態產生 |
| D：rag_factory metadata 注入 | ✅ | node metadata 加入 `site_id` |
| E：workflow.py 端到端串接 | ✅ | `_init_workflow()` 呼叫順序修正 |
| F：CLI / main.py | ✅ | publish 控制 + import 路徑更新 |
| G：測試更新 | ✅ | 移除過渡性測試（`test_phase_a_f.py` 等 28 tests），84 tests passed |
| H：文件更新 | ⏳ | README.md / project.md |

---

## 4. Config 重構 — BaseModuleConfig + CLI 重構（2026-08-24）

> ⚠️ §4-1 中 `BaseModuleConfig` 的 `site_id` 欄位已被 §14 移除。目前 `BaseModuleConfig` 僅保留 `config_name`、`from_toml()`、`run_name`；`site_id` 由各子類自行宣告。

### 4-1. BaseModuleConfig（`src/app/configs/base_config.py`）

抽取四個 module config 的重複欄位（`config_name`、`site_id`、`from_toml()`、`run_name`、`validate_site_id()`），消除 ~56 行重複。`_CONFIG_FOLDER_PATH` / `sections_to_keys` 使用 `ClassVar` 避免 dataclass 繼承 ordering 問題。

### 4-2. site_id 從 RunConfig 移至 BaseModuleConfig

`BaseRunConfig` 移除 `site_id`；所有 `run_*()` 改由 `**config_overrides` 傳入 `from_toml()`。

### 4-3. CLI 改名

`...ConfigCLI` → `...ModuleConfig`；config class 從 `cli.py` 移至 `src/app/configs/workflow_config.py`。`cli.py` 僅保留複合 CLI class + 分派。

### 4-4. 驗證

爬蟲 → 圖片摘要 → RAG 建庫 → hybrid query → 四層路徑正確。ruff + pyright 0 errors。端到端 `test_main.py` 1 passed。

---

## 5. 測試清理（2026-08-24）

移除 `test_phase_a_f.py`（28 tests，使用 `inspect.getsource()` 的過渡性驗證）、`test_set_run_path_without_site_path`（三層 fallback 已無消費者）、`test_main_py_has_site_id_constant`。完整 dev suite：**84 passed, 0 failed**。

保留：`test_runmanager_datamanager.py`（14）、`test_agent.py`（12）、`test_dedup_key.py`（12）、`test_html_date_extraction.py`（30）、`test_server.py`（11）。

---

## 6. 多站端到端驗證（2026-08-25）

`test_multi_site.py`：nculab 與 ncucsie 各爬取 10 頁 → 圖片摘要 → RAG 建庫。

| Site | 爬蟲 | 圖片摘要 | RAG | Publish |
|------|------|----------|-----|---------|
| nculab | ✅ 9 頁 | ✅ 96 張 $0.03 | ✅ | ✅ 8/8 檔案 |
| ncucsie | ✅ 9 頁 | ✅ 96 張 $0.03 | ✅ | ✅ 8/8 檔案 |

修正 Bug：`configs/webpage_image_summarizer/test_ncucsie.toml` 的 `site_id` 錯誤設為 `"nculab"`（會污染 nculab Markdown）。

---

## 7. main.py MainCLI — tyro 整合（2026-08-26）

```python
@dataclass
class MainCLI:
    config_name: str = "default"

def main(cli: MainCLI | None = None) -> None: ...

if __name__ == "__main__":
    main(tyro.cli(MainCLI))
```

```bash
uv run python src/main.py --config-name nculab
```

---

## 8. Bug 修正與 Workflow 細節調整（2026-08-26）

### 8-1. NoneType 防護（`website_crawler.py`）

crawl4ai 某些頁面 `crawl_result.markdown` 為 `None`，新增檢查跳過，避免 `_filter_crawl_results()` 崩潰。

### 8-2. RAG 建構移入 `with` 區塊（`workflow.py`）

`RAGBuilder(config).build()` 原在 `log_run_time` 區塊外，改為 `builder.build(rag)` 在 `with` 內執行，使建構 + query 全部計時。

### 8-3. `build()` 可選 rag 參數（`rag_factory.py`）

`RAGBuilder.build(rag=None)` 支援外部傳入 RAG；不傳時自動建立。完全向後相容。

### 8-4. 端到端流水線驗證

```bash
uv run python src/main.py --config-name nculab   # ✅ 3 modules, 2.27s RAG
uv run python src/main.py --config-name ncucsie  # ✅ 3 modules, 2.49s RAG
```

兩站各 8 個檔案正確 publish 至 `data/`。

---

## 9. Milvus Vector Store 重用機制（2026-08-26）

> 原 `milvus_reuse_plan.md` 已整合至本節。

### 9-1. 問題

`_should_rebuild()` 對 Milvus 硬編回傳 `True`，每次 `build_reusable()` 都刪除舊 DB 重跑。但 `MilvusVectorStore(overwrite=False)` 本身支援連上既有 collection。

### 9-2. 修正（`rag_factory.py`，3 處）

1. **`_should_rebuild()` 統一邏輯**：`force_rebuild` 最高優先；Qdrant/Milvus 各自判斷 `os.path.exists()`；不支援類型拋 `ValueError`
2. **`build_reusable()` 重用分支**：`overwrite=False` 連上既有 collection 後需 `load_collection()`（因 collection 處於 `released` 狀態）
3. docstring 更新

### 9-3. 行為對照

| 情境 | 改前 | 改後 |
|------|------|------|
| `milvus.db` 已存在 + `force_rebuild=False` | 刪除重建 | **直接載入**（~13s vs ~30s+） |
| `milvus.db` 已存在 + `force_rebuild=True` | 刪除重建 | 刪除重建（不變） |

### 9-4. 測試

14 單元測試（`test_rag_reuse.py`）+ 整合驗證：`rag-query-cli` 查詢 ncucsie → 100% faithfulness/relevancy，13.4s。

---

## 10. 多站 RAG 工具實作（2026-08-26，M3）

> 規劃文件：`2026_0826-multi_site_RAG_tool.md`。

### 10-1. RAGRegistry（`src/app/tools/rag_registry.py`）

依 `site_id` 延遲建立 RAG，`OrderedDict` LRU 快取（上限 5），`build_reusable(force_rebuild=False)` 利用 §9 重用機制。

`get(site_id)` 流程：cache hit → 直接回傳；cache miss → `site_exists()` 驗證 → `RAGConfig.from_toml("default", site_id=...)` → `build_reusable()` → 存入快取（超限 eviction + `rag.close()`）。

### 10-2. webpage_retriever 多站路由

`RetrieverInputSchema` 新增必填 `site_id`；`create_webpage_retriever_tool(registry)` 精簡為 ~30 行（原 ~90 行），工具層僅負責 `registry.get(site_id)` → `rag.retrieve()` 路由。

### 10-3. Agent 整合

`create_site_discovery_tool(registry)` → `list_knowledge_bases` 工具（需空 `args_schema`）。`create_agent()` 建立 Registry + 兩個工具；`Agent` 新增 `registry` 欄位，`close()` 委派 `registry.close()`。

### 10-4. System Prompt

`DEFAULT_SYSTEM_PROMPT` 更新為多站路由版：引導 LLM 先查 `list_knowledge_bases`，`webpage_retriever` 必須帶入 `site_id`，可分別檢索多站合併回答。

### 10-5. 測試

| 層級 | 檔案 | 項數 |
|------|------|------|
| 單元 | `test_rag_registry.py` | 13 |
| 整合 | `test_multi_site_tool.py` | 26 |
| 端到端 | `test_module.py::test_agent` | ✅ 25.5s（Agent 自動帶入 `site_id=nculab`，回含 6 個 URL） |

### 10-6. 檔案變更

| 檔案 | 操作 |
|------|------|
| `src/app/tools/rag_registry.py` | **新增** 100 行 |
| `src/app/tools/webpage_retriever.py` | 修改（精簡重寫） |
| `src/app/agent/agent.py` | 修改（discovery tool + registry + 多工具） |
| `src/app/configs/agent_config.py` + TOML×2 | 修改（system_prompt） |
| `scripts/m0_rag_smoke.py` | 修改（改用新 API） |

---

## 11. Chrome Extension 站點偵測與 Server 路由（2026-08-26，M4）

> 規劃文件：`2026_0826-chrome_extension_site_detection.md`。

### 11-1. Extension

`content.js` 偵測 `window.location.hostname`，經 `background.js` 透傳 `page_url` 至 Server。

### 11-2. Server（`src/app/server/app.py`）

- `DOMAIN_SITE_MAP`：精確匹配 + 子域名 suffix 匹配
- `resolve_site_id(page_url)` → `site_id` 或 `None`
- `_enrich_query_with_site_context()`：前綴 `[使用者瀏覽 {site_id} 網站]` 供 LLM 感知站點
- `ChatRequest` 新增 `page_url` 欄位

### 11-3. 協定

`content.js` → `background.js` → `Server` 全鏈路新增 `page_url` 欄位。

### 11-4. 測試

`test_server.py`：18 passed（原 11 + M4 新增 7：resolve_site_id 精確/suffix/None/unknown、enrich_query、endpoint 串接）。

---

## 12. Chrome Extension Service Worker Keepalive（2026-08-26）

### 12-1. 問題

切站後 widget 顯示「與背景程序連線中斷」。Manifest V3 Service Worker 約 30 秒無活動即被 Chrome 終止，新 port 建立時 SW 尚未就緒，觸發 `onDisconnect`。

### 12-2. 修正

使用 `chrome.alarms` API（每 25 秒）保持 SW 活躍。port 斷開時清除 alarm。`manifest.json` 新增 `"permissions": ["alarms"]`。

選用 `chrome.alarms` 而非 `port.postMessage`：不產生額外 port 事件，為 Chrome 官方推薦機制。

### 12-3. 驗證

nculab 問答 → 切至 ncucsie 問答 → 快速切換多站：全部正確，無「連線中斷」錯誤。

---

## 13. Chrome Extension Typing Indicator — 等待動畫（2026-08-26）

### 13-1. 動機

使用者送出問題後，從 `streamChat()` 發起到第一個 `token` 事件到達之間，widget 的回覆氣泡為空白，缺乏視覺回饋。加入 typing indicator（三個跳動圓點）提供即時等待狀態提示。

### 13-2. 改動

| 檔案 | 變更 |
|------|------|
| `extension/widget.js` | 新增 `createTypingIndicator()` 函數；CSS 新增 `.wc-typing` 樣式 + `@keyframes wc-bounce` 動畫（含 `-webkit-` prefix）；`sendQuery()` 送出時立即顯示 indicator，收到首個 token 時移除 |

### 13-3. CSS 設計

`.wc-typing` 為 flex 容器，內含三個 6px 圓形 `span`，透過 `animation: wc-bounce 1.4s infinite ease-in-out` 實現跳動效果。三個圓點分別設定 `animation-delay: 0s / 0.2s / 0.4s`，形成連續波浪感。加入 `-webkit-animation` + `@-webkit-keyframes` 確保 shadow DOM 相容性。`min-height: 20px` 確保 `.wc-msg`（`white-space: pre-wrap`）內的 indicator 有最小可見高度。

### 13-4. JS 邏輯

| 時機 | 行為 |
|------|------|
| 送出後立即 | `respEl` 內建立 typing indicator DOM，立即可見 |
| 首個 token 到達（elapsed < 300ms） | 直接 `removeChild`（快速回應避免閃爍） |
| 首個 token 到達（elapsed ≥ 300ms） | CSS fade-out（`opacity .15s` transition）後 `transitionend` 移除 |
| `done` 事件 | `innerHTML = renderMarkdown(ev.response)` 整體替換（含殘留 indicator） |
| 錯誤 / 例外 | 先 `textContent = ''` 清除 indicator，再顯示紅色錯誤訊息 |

文字追加改用 `appendChild(document.createTextNode(...))` 而非 `textContent +=`，避免覆蓋 typing indicator DOM 節點。`transitionend` 監聽搭配 `parentNode === respEl` 安全檢查，防止 `done` 事件已替換 innerHTML 後的殘留執行。

### 13-5. 教訓

Chrome Extension 修改 `extension/*.js` 後，**必須**到 `chrome://extensions/` 點擊 🔄 重新載入按鈕，再重新整理頁面，新版本才會生效。僅重新整理頁面（F5 / Ctrl+R）不足，content script 仍使用舊版快取。已記錄至 `/memories/repo/extension_reload_required.md`。

---

## 14. BaseModuleConfig 移除 site_id 重構（2026-08-26）

> 初始嘗試在 `AgentConfig` 繞寫 `from_toml()` 處理 site_id，但因 `BaseModuleConfig.from_toml()` 內 `_filter_allowed_config_keys` 會過濾掉不在 `sections_to_keys` 中的 key，導致 overrides 注入的 `site_id` 被丟棄，dataclass 建構時缺少必填欄位。經多次修正後，改為將 `site_id` 從 `BaseModuleConfig` 完全移除。

### 14-1. 動機

`site_id` 在 `BaseModuleConfig` 中的問題：
- `AgentConfig` 不需要 `site_id`（多站管理由 `RAGRegistry` 工具層處理），卻被迫繼承必填欄位
- 為繞過繼承，`AgentConfig.from_toml()` 完全改寫，引入 `load_config_from_toml` + 手動注入的複雜邏輯
- `_filter_allowed_config_keys` 的過濾機制與 overrides 注入衝突，反覆引入 bug

### 14-2. 改動

| 檔案 | 變更 |
|------|------|
| `src/app/configs/base_config.py` | 移除 `site_id: str` 欄位、`validate_site_id()` 靜態方法、`ConfigValidationError` import |
| `src/app/configs/website_crawler_config.py` | 新增 `site_id: str` 欄位；`_validate_config` 改為本地驗證（inline `ConfigValidationError`） |
| `src/app/configs/webpage_image_summarizer_config.py` | 同上 |
| `src/app/configs/rag_config.py` | 同上 |
| `src/app/configs/agent_config.py` | 完全移除 `site_id` 欄位；移除 `from_toml()` 繞寫（回歸標準繼承）；移除 `os` / `load_config_from_toml` import；移除 `DEFAULT_INIT_CONFIG_FOLDER_PATH` 常數 |
| `src/app/configs/workflow_config.py` | `AgentModuleConfig` 已無 `site_id`（前次改動） |

### 14-3. 改後架構

```
BaseModuleConfig（通用基底）
  ├── config_name: str
  ├── from_toml() — 標準 TOML 載入 + overrides
  └── run_name — 統一命名
       │
       ├── WebsiteCrawlerConfig: site_id: str（必填，TOML [init] 提供）
       ├── RAGConfig:             site_id: str（必填，TOML [init] 提供）
       ├── WebpageImageSummarizerConfig: site_id: str（必填，TOML [init] 提供）
       └── AgentConfig:           （無 site_id，TOML 無 [init] section）
```

四個子類完全對稱，`AgentConfig` 不再有特殊 `from_toml()` 繞寫。

### 14-4. 測試

| 項目 | 結果 |
|------|------|
| `pytest src/test/dev/` | 82 passed |
| `ruff check` | 0 新增錯誤 |
| `pyright` | 0 errors |
| `server_up.py` | ✅ 啟動成功 |

---

## 15. Chrome Extension 跨頁面記憶共享（2026-08-26）

### 15-1. 問題

`widget.js` 的 `threadId` 為閉包變數，頁面重新載入或切換時丢失。導致：
- 刷新頁面 → 新對話（agent 記憶丢失）
- 切換站點 → 新對話（無法延續上下文）
- 開新 tab → 新對話

使用者期望跨頁面共享同一份對話記憶。

### 15-2. 方案

以 `background.js`（Service Worker）為 thread_id 的唯一管理者，透過 `chrome.storage.session` 持久化。`content.js` 與 `widget.js` 完全不動。

### 15-3. 改動

| 檔案 | 變更 |
|------|------|
| `extension/manifest.json` | `"permissions"` 新增 `"storage"` |
| `extension/background.js` | 收到 chat 請求時從 `chrome.storage.session.get('thread_id')` 讀取並覆寫 `msg.thread_id`；done 事件後從 SSE response 解析 `thread_id` 寫回 storage；docstring 更新 |

### 15-4. 協定流程

```
content.js → background.js → Server
  payload.thread_id=null   從 storage 讀取 thread_id    用 thread_id 問答
                           覆寫 msg.thread_id            回傳 done + thread_id
                            ← 解析 done 事件 ←
                           寫回 storage
                           轉發 done 給 content
```

### 15-5. 效果

| 場景 | 改前 | 改後 |
|------|------|------|
| 同頁面連續提問 | ✅ 共享 | ✅ 共享（不變） |
| 刷新頁面 | ❌ 新對話 | ✅ 延續 |
| 同 tab 切到不同站點 | ❌ 新對話 | ✅ 延續 |
| 開新 tab 同站點 | ❌ 新對話 | ✅ 延續 |
| 關閉 Chrome | — | 對話清除（session 生命週期） |

### 15-6. 已知限制

- 兩個 tab 同時首次提問（thread_id 均為 null）時，各自建立 thread_id，後寫入 storage 的覆蓋前者。單人本地使用幾乎不會發生。
- `chrome.storage.session` 生命週期與 Chrome 程序相同，關閉 Chrome 後對話清除。

---

## 16. System Prompt site_id 優先級修正（2026-08-26）

### 16-1. 問題

跨頁面共享 thread_id 後，agent 對話歷史中累積了不同站點的問答記錄。LLM 在決定 `webpage_retriever` 的 `site_id` 參數時，傾向延續歷史模式（如之前都是 ncucsie），忽略當前訊息中的 `[使用者瀏覽 nculab 網站]` 前綴。

### 16-2. 修正

強化 system prompt 中的站點路由規則：

| 規則 | 舊版 | 新版 |
|------|------|------|
| 工具流程第 3 點 | `若問題來自特定網站（如對話中有 site 語境），直接使用該 site 檢索` | `使用者訊息若以 [使用者瀏覽 X 網站] 開頭，必須使用 X 作為 site_id` |
| 回答規則 | — | 新增 `當前訊息的站點前綴優先於對話歷史中的站點` |

### 16-3. 改動

| 檔案 | 變更 |
|------|------|
| `src/app/configs/agent_config.py` | `DEFAULT_SYSTEM_PROMPT` 更新 |
| `configs/agent/default.toml` | `system_prompt` 同步更新 |
| `configs/agent/test.toml` | `system_prompt` 同步更新 |

---

## 17. 移除 Qdrant Vector Store（2026-08-26）

### 17-1. 動機

Qdrant 不支援 hybrid search 的 BGE-M3 稀疏向量，自 §9 改用 Milvus BGE-M3 後已無實際使用。移除可減少依賴套件（qdrant-client、fastembed 等 11 個）、簡化型別系統（消除 `QdrantVectorStore | MilvusVectorStore` union），並統一 codebase 僅保留 Milvus 路徑。

### 17-2. 依賴清理

`pyproject.toml` 移除 `llama-index-vector-stores-qdrant>=0.10.1` + `fastembed>=0.8.0`；`uv lock` 移除 11 個套件：

| 套件 | 原因 |
|------|------|
| `llama-index-vector-stores-qdrant` | Qdrant 向量庫整合 |
| `qdrant-client` | Qdrant 客戶端 |
| `fastembed` | Qdrant BM25 稀疏向量生成 |
| `onnxruntime`、`mmh3`、`loguru`、`flatbuffers`、`portalocker`、`py-rust-stemmers`、`pywin32`、`win32-setctime` | fastembed 傳遞依賴 |

### 17-3. 型別簡化

```
VectorStoreBuilder.build()     → 回傳 MilvusVectorStore（原為 tuple[QdrantClient | None, QdrantVectorStore | MilvusVectorStore]）
RAG.qdrant_client              → 整個刪除
RAG.vector_store               → MilvusVectorStore（原為 QdrantVectorStore | MilvusVectorStore）
RAGBuilder.clean_vector_store() → 直接呼叫 clean_milvus()（原為 if/elif 分支）
RAGBuilder._should_rebuild()   → 僅 milvus 路徑判斷（原為 if qdrant / elif milvus / raise）
```

### 17-4. 變更範圍

| 檔案 | 變更 |
|------|------|
| `pyproject.toml` | 移除 `llama-index-vector-stores-qdrant`、`fastembed` |
| `uv.lock` | 自動更新（移除 11 套件） |
| `configs/rag/qdrant.toml` | **整檔刪除** |
| `src/app/configs/rag_config.py` | `DEFAULT_VECTOR_STORE_TYPE` 改 `"milvus"`；刪除 `_default_qdrant_db_path()`、`qdrant_db_folder_path` 欄位/keys/驗證；`vector_store_type` 驗證改為僅允許 `"milvus"` |
| `src/app/engines/rag/rag_factory.py` | 刪除 Qdrant imports、`build_qdrant()`、`clean_qdrant()`；`VectorStoreBuilder.build()` 簡化回傳型別；`build_vector_store()` 不再設定 `rag.qdrant_client`；`clean_vector_store()` 直接呼叫 `clean_milvus()` |
| `src/app/engines/rag/rag.py` | 刪除 Qdrant imports；`RAG.__init__` 移除 `self.qdrant_client`；`close()` 移除 qdrant_client 關閉；`vector_store` 型別簡化 |
| `src/app/workflow/workflow.py` | `run_rag_build()` 移除 qdrant 分支，僅保留 milvus 路徑 |
| `src/app/workflow/data_manager.py` | `publish_vector_store()` 移除 `vector_store_type` 參數，固定為 Milvus |
| `src/test/dev/test_rag_reuse.py` | 刪除 `TestShouldRebuildQdrant` 測試類別；`TestShouldRebuildUnified` 移除 qdrant parametrize |
| `src/test/dev/test_runmanager_datamanager.py` | 刪除 `test_publish_vector_store_qdrant` |
| `src/test/dev/test_legacy_results_removal.py` | 從 parametrize 移除 `"qdrant"` |
| `README.md` | 功能描述改為 Milvus only |

### 17-5. 驗證

| 項目 | 結果 |
|------|------|
| `uv lock` | 11 套件移除 |
| Pylance 診斷 | 0 errors（所有修改檔案） |
| `pytest src/test/test_module.py::test_rag` | **PASSED**（45s，完整 RAG 建構 + hybrid query） |

---

## 18. Exception Handling 改善（2026-08-27）

> 技術債：10 處 `except Exception` 分布於 7 個檔案，存在靜默吞錯誤、log level 誤用、exception 類型過寬。

### 18-1. 問題與修正

三層原則：(1) 能確定的用具體 exception（`URLError`、`ValueError`、`KeyError`）；(2) 不再靜默吞錯誤，至少 `logger.warning` + `exc_info=True`；(3) `rag.py` 的 `_closed = True` 移至 close 成功之後。

| 嚴重度 | 檔案 | 問題 → 修正 |
|--------|------|-------------|
| 🔴 P0 | `rag.py` | `except Exception: pass` → `logger.warning` + `_closed` 移至 try 後 |
| 🟠 P1 | `markdown_cleaner.py` | `except Exception` → `except (ValueError, KeyError)`；`logger.error` → `warning` |
| 🟠 P1 | `website_crawler.py` | `_safe_step` 加 `exc_info=True`；f-string → `%s` lazy formatting |
| 🟡 P2 | `rag_helper.py` | 移除 `except Exception`，改用 `getattr(..., "metadata", None) or {}` |
| 🟡 P2 | `html_date_extractor.py` | `logger.debug` → `logger.warning(..., exc_info=True)` |
| 🟡 P2 | `webpage_image_summarizer.py` | `except Exception` → `except (URLError, TimeoutError, OSError)`；補 `exc_info=True` |

### 18-2. 驗證

Pylance 0 errors（6 個修改檔案）；`pytest test_html_date_extraction` 35 passed、`test_dedup_key` 12 passed。

---

## 19. 測試檔案整合（2026-08-27）

`src/test/dev/` 從 10 → 6 個檔案（-40%），移除已失效測試，合併同子系統測試。

### 19-1. 刪除

| 檔案 | 原因 |
|------|------|
| `test_legacy_results_removal.py` | legacy 目錄已不存在，測試前提失效 |
| `scripts/m0_rag_smoke.py` | 功能合併至 `test_rag_tools.py` |

### 19-2. 合併

| 合併結果 | 來源 | 合併原因 |
|----------|------|----------|
| `test_agent_server.py` | `test_agent.py` + `test_server.py` | 同 agent 層，共用替身（`_FakeConfig` / `FakeRunManager`） |
| `test_rag_tools.py` | `test_rag_registry.py` + `test_rag_reuse.py` + `test_multi_site_tool.py` + `m0_rag_smoke.py` | 同 RAG 子系統，共用 mock 基礎設施 |

### 19-3. 內部精簡

- `test_html_date_extraction.py`：`TestParseHttpDate` + `TestNormalizeToIso8601` 改用 `@pytest.mark.parametrize`
- `test_runmanager_datamanager.py` / `test_dedup_key.py`：import 移至模組頂端
- `test_rag_tools.py`：`_FakeRAGConfig` 從 15 → 2 欄位

### 19-4. 結果

`pytest src/test/dev/`：**125 passed**, 0 failed。Pylance 0 errors。

---

## 20. Server 架構重構 — 統一入口與工具抽取（2026-08-28）

> 消除 server 啟動/測試的重工，建立單一統一入口 `workflow.run_server()`。

### 20-1. 問題

呼叫鏈冗長（3 層間接）：`cli.py server-cli` 僅一行轉發、`server_up.py` 功能重疊、`app.run_server` 與 `workflow.run_server` 命名衝突。

### 20-2. 新架構

```
cli.py server-cli → workflow.run_server(mode="block") → spawn(app.start_uvicorn())
test_module.py    → workflow.run_server(mode="validate") → spawn → SSE 驗證 → shutdown
```

### 20-3. 新增 `src/utils/server_helper.py`

從 `server_up.py` + `m3_server_smoke.py` 提取共用工具：

| 函式 | 職責 |
|------|------|
| `spawn_server()` / `wait_ready()` / `shutdown_server()` | subprocess 生命週期 |
| `parse_sse_events()` / `stream_chat()` / `check_single_turn()` | SSE 協定驗證 |
| `latest_results_json()` / `check_persistence()` | 落盤驗證 |

### 20-4. 呼叫端改動

| 檔案 | 改動 |
|------|------|
| `app.py` | `run_server` → `start_uvicorn`（解決命名衝突） |
| `cli.py` | import 改為 `workflow.run_server`；`mode="block"` |
| `test_module.py` | `test_server()` 從 ~30 行手動管理縮為 2 行 `run_server()` 呼叫 |
| `scripts/server_up.py` | **刪除**（功能由 `cli.py server-cli` 取代） |
| `scripts/m3_server_smoke.py` | **刪除**（功能由 `workflow.run_server()` 取代） |

### 20-5. 驗證

Pylance 0 errors（4 個修改檔案）；Ruff 0 issues。

---

## 21. Scripts 資料夾刪除（2026-08-28）

`scripts/` 僅存 `server_up.py`（§20 刪）、`m3_server_smoke.py`（§20 刪）、`m4b_extension_test.py`。整併刪除。

> ⚠️ `m4b_extension_test.py` 被一併刪除。如需恢復，可從 git 歷史還原。

---

## 22. RunManager 重構 — Atomic 初始化與職責分離（2026-08-30）

> Commit: `89f18bf` — `refactor: update workflow and run manager integration`

### 22-1. 問題

§3 的 RunManager 採用 step-by-step 初始化（`set_module_path` → `set_site_path` → `set_run_path`），存在時序耦合、呼叫端重複、職責過重（>400 行含 Markdown 儲存/結果查詢）等問題。

### 22-2. RunManager 重構

| 移除 | 新增 | 說明 |
|------|------|------|
| `set_module_path()` | `for_run(module, site_id, run_name)` | Atomic 3 層初始化：module → site → run |
| `set_site_path()` | `for_run_no_site(module, run_name)` | Atomic 2 層初始化（Agent 使用） |
| `set_run_path()` | — | — |
| 5 個 `_set_*()` private 方法 | `init_module_run_paths()` 內直接設定屬性 | 消除冗餘間接層 |
| 模組級 `os.makedirs(RUNS_FOLDER_PATH)` | — | 目錄僅在 classmethod 時建立 |
| `_log_run_path_init/complete()` | `log_run_paths()` 內聯邏輯 | `RUN_PATH_COMPLETE` 改為局部變數 |
| `latest_results_json_path` / `latest_run_path` | — | 結果查詢轉移至 `run_persistence.py` |

### 22-3. 新增 `run_persistence.py`

從 `RunManager` 提取 Markdown 持久化和結果查詢，改為模組級純函數：

| 函數 | 原位置 | 說明 |
|------|--------|------|
| `save_results_as_md()` | `RunManager.save_results_as_md()` | 將爬取結果寫入 Markdown |
| `save_query_results_as_md()` | `RunManager.save_query_results_as_md()` | 將 query 結果各寫為 Markdown |
| `load_latest_results(base_folder, module_name)` | `RunManager.load_latest_results_from_json()` | 從 JSON 讀取最新模組結果 |
| `load_latest_run_path(base_folder, module_name)` | `RunManager.load_latest_summarizer_run_path()` | 回傳最新模組 run path |
| `_filter_run_folders(base_folder)` | `RunManager._filter_run_folders()` | 篩選符合 timestamp 格式的資料夾 |

輔助函數 `_render_query_result_md()`、`_format_score()`、`_escape_md_cell()`、`_to_blockquote()` 一併遷移。

### 22-4. workflow.py 重構

- **移除 `_init_workflow()`**：各 `run_*()` 直接呼叫 `RunManager.for_run()`
- **`run_*()` 回傳 RunManager**：`run_website_crawler()` / `run_webpage_image_summarizer()` 回傳 `tuple[dict | None, RunManager]`；`run_rag_build()` / `run_rag_query()` / `run_agent()` 回傳 `RunManager`
- **Markdown 儲存**：改用 `save_results_as_md()` / `save_query_results_as_md()` 純函數
- **結果查詢**：改用 `load_latest_results()` 純函數
- **Agent 初始化**：`run_agent()` 移除自動建立 RunManager，改由 `create_agent()` 內 `RunManager.for_run_no_site()` 建立

### 22-5. 呼叫端重構

| 檔案 | 改動 |
|------|------|
| `cli.py` | 移除全域 `RunManager()`，從各 `run_*()` 回傳取得；run config 儲存條件改為 `run_manager is not None` |
| `main.py` | 各模組使用獨立 `run_manager`（`crawl_run_manager`、`summarizer_run_manager`、`rag_build_run_manager`） |
| `exp.py` | 移除所有 `RunManager` 建立和 `set_module_path()` 呼叫 |
| `agent.py` / `app.py` | `create_agent()` 改用 `RunManager.for_run_no_site()` |
| `workflow/__init__.py` | 新增 `run_persistence` 函數 export |

### 22-6. 其他改動

| 檔案 | 變更 |
|------|------|
| `rag_factory.py` | MilvusVectorStore 新增 gRPC keepalive（`grpc.keepalive_time_ms: 300_000`），避免 `ENHANCE_YOUR_CALM GOAWAY` |
| `server_helper.py` | `wait_ready()` 回傳值改 `None`；`spawn_server()` 新增 `PYTHONPATH` 確保子進程 import 正常 |
| `docs/work/todo.md` | 「拆分 run manager」標記完成 |

### 22-7. 變更範圍

| 檔案 | 操作 | 說明 |
|------|------|------|
| `src/app/workflow/run_manager.py` | **重構** | 406 → ~170 行（-58%）；step-by-step → atomic classmethod |
| `src/app/workflow/run_persistence.py` | **新增** | 235 行；Markdown 持久化 + 結果查詢純函數 |
| `src/app/workflow/workflow.py` | 修改 | 移除 `_init_workflow()`；`run_*()` 回傳 RunManager + 使用 `run_persistence` |
| `src/cli.py` | 修改 | 移除全域 RunManager；從 `run_*()` 回傳取得 |
| `src/main.py` | 修改 | 各模組使用獨立 run_manager |
| `src/exp.py` | 修改 | 移除所有 RunManager 建立 |
| `src/app/agent/agent.py` / `app.py` | 修改 | 改用 `for_run_no_site()` |
| `src/app/engines/rag/rag_factory.py` | 修改 | gRPC keepalive |
| `src/utils/server_helper.py` | 修改 | `wait_ready()` + `PYTHONPATH` |
| `src/test/` × 3 | 修改 | 改用 `for_run()` / `for_run_no_site()` + `run_persistence` |

### 22-8. 驗證

| 項目 | 結果 |
|------|------|
| Pylance 診斷（15 個修改檔案） | 0 errors |
| Ruff lint | 0 issues |

---

## 23. 統一各模組留檔機制（2026-08-30）

> 將 `rag_build`、`rag_query`、`agent` 三個模組的留檔機制對齊 crawler + image_summarizer 的完整度。

### 23-1. 動機

§3–§5 建立 RunManager + DataManager 留檔機制時，僅 crawler 與 image_summarizer 完整串接。三個模組存在以下缺口：

| 模組 | 缺口 |
|------|------|
| `rag_build` | `run_rag_build()` 未呼叫 `save_results_as_json()`，無 `results.json` 落盤 |
| `rag_query` | `cli.py` 的 `RAGQueryCLI` 區塊未呼叫 `publish_run_metadata()`，`publish=True` 時不會發布 metadata |
| `agent` | `cli.py` 的 `AgentCLI` 區塊未呼叫 `publish_run_metadata()`；`AgentRunConfig` 無 `publish` 欄位，CLI 無法接收 `--publish` 參數 |

### 23-2. 改動

| 檔案 | 變更 |
|------|------|
| `src/app/configs/workflow_config.py` | `AgentRunConfig` 新增 `publish: bool = False`（L48） |
| `src/app/workflow/workflow.py` | `run_rag_build()` 儲存設定和結果區塊新增 `results_dict` + `save_results_as_json()`（L296–317） |
| `src/cli.py` | 共用區塊後新增 `RAGQueryCLI` 的 `publish_run_metadata()` 呼叫（L143–151） |
| `src/cli.py` | `AgentCLI` 區塊內新增 `publish_run_metadata()` 呼叫（L113–128） |

**設計決策**：

- `AgentRunConfig` 不繼承 `BaseRunConfig`（`query: str` 無預設值會導致 dataclass `TypeError: non-default argument follows default argument`），直接加 `publish` 欄位。
- `publish` 在 `cli.py` 分派前經 `pop("publish")` 提取，不會洩漏進 `**config_overrides`。
- `run_rag_build` 的 `results_dict` 在 `with (rag, ...)` context 內執行，確保 `rag` 屬性尚未關閉。

### 23-3. JSON Structure for rag_build results.json

`run_rag_build()` 新增的 `results.json` 結構：

```json
{
    "config": {
        "config_name": "default",
        "run_name": "20260830_100000",
        "site_id": "nculab",
        "query": "...",
        "embedding_name": "bge-m3",
        "vector_store_type": "milvus",
        "collection_name": "nculab",
        "chunk_size": 512,
        "chunk_overlap": 50
    },
    "summary": {
        "total_nodes": 1234,
        "total_pages": 90
    },
    "vector_store": {
        "uri": "data/rag/nculab/milvus.db",
        "saved_to_runs": false
    }
}
```

| 欄位 | 來源 | 說明 |
|------|------|------|
| `config.*` | `RAGBuildConfig` + `RunManager` | 建庫設定全貌 |
| `summary.total_nodes` | `len(rag.nodes)` | build_nodes 產出的 node 數量 |
| `summary.total_pages` | `len(rag.results_json)` | 載入的 crawl results 頁數 |
| `vector_store.uri` | `config.milvus_uri` | 向量庫檔案路徑 |
| `vector_store.saved_to_runs` | `save_vector_store_to_runs` 參數 | 是否複製至 `runs/` 目錄 |

### 23-4. Agent site_id Decision

Agent 模組的 `publish_run_metadata()` 使用 `cli_arg.run.config_name` 作為 `site_id`，而非其他值。

**理由**：Agent 為跨站查詢工具，透過 `RAGRegistry` 同時檢索多個知識庫，無單一站點可對應。`config_name` 是唯一有意義的識別碼（如 `"default"`），`category` 固定為 `"agent"`。`AgentRunManager` 由 `RunManager.for_run_no_site()` 建立，`site_id` 為空字串 `""`；若直接使用會導致目標路徑為 `data/agent//`，不正確。

### 23-5. CR Review Notes

Code Review（Round 1, 2026-08-30 01:00）結果：**pass**，無 CRITICAL 或 MAJOR issue。2 項非阻斷建議：

**S1 — `rag.results_json` null guard 不必要**

`src/app/workflow/workflow.py:309`

`rag.results_json` 型別為 `dict[str, Any]`，在 `RAG.__init__` 經 `_load_results_json()` 初始化，永遠不會是 `None`。`if rag.results_json else 0` 防禦無害但誤導（暗示可能為 `None`）。空 dict `{}` 亦為 falsy，但 `len({})` 已為 0，guard 無實際作用。

```python
# 現行（無害但誤導）：
"total_pages": len(rag.results_json) if rag.results_json else 0,

# 較簡潔：
"total_pages": len(rag.results_json),
```

> 注意：`rag.nodes` 型別為 `Sequence[BaseNode] | None`，初始值為 `None`，null check 確實必要且正確。

**S2 — AgentCLI `module_config.toml` 不會被發布**

`src/cli.py:127`

`publish_run_metadata()` 會複製 `module_config.toml`，但 `run_agent()` 從未呼叫 `save_module_config_as_toml()`。`_copy_single_file` 輔助函式在檔案不存在時靜默跳過，不會崩潰。結果是 `data/agent/{config_name}/` 僅包含 `run_config.toml` 與 `terminal.log`，無 `module_config.toml`。

此行為可接受：`AgentModuleConfig` 僅含 optional 的 `llm_name` 與 `system_prompt`，無實質 module config 需持久化。

### 23-6. 驗證

| 項目 | 結果 |
|------|------|
| `pytest src/test/dev/` | **45/45 passed** |
| `pyright` | 0 errors |
| `ruff check` | 0 issues |
| 既有測試不受影響 | ✅ `test_runmanager_datamanager.py` 15/15、`test_agent_server.py` 30/30 |

**結構驗證**：

- [x] `AgentRunConfig` 有 `publish: bool = False` 欄位（L48）
- [x] `run_rag_build()` 呼叫 `save_results_as_json(results_dict)`，結構為 `{config, summary, vector_store}`（L296–317）
- [x] `cli.py` `RAGQueryCLI` 的 `publish_run_metadata()` 置於共用區塊之後，guards 為 `isinstance(cli_arg, RAGQueryCLI) and data_manager is not None and run_manager is not None`（L143–151）
- [x] `cli.py` `AgentCLI` 的 `publish_run_metadata()` 置於 `save_run_config_as_toml` + `log_run_paths` 之後，以 `cli_arg.run.config_name` 作為 `site_id`（L113–128）

---

## 24. Agent 函數搬移重構（2026-09-01）

`src/app/agent/agent.py` 原先同時包含 Agent 核心（`Agent` dataclass + `create_agent()` 工廠）與多個非 Agent 核心的純函數／工具建立函數，職責混雜。本次重構將這些函數搬移到正確的模組層：

- 跨層 LangChain 輔助函數 → `src/utils/langchain_helper.py`（新檔）
- Site Discovery 工具 → `src/app/tools/site_discovery.py`（新檔）
- Thread History 搜尋 → `RunManager.find_thread_history_path()`（staticmethod）

重構後 `agent.py` 僅保留 `Agent` dataclass + `create_agent()` 工廠，職責單一。

### 24-1. 搬移總覽

| 目的地模組 | 搬移 Symbol | 原位置（agent.py） |
|---|---|---|
| `src/utils/langchain_helper.py`（新檔） | `SOURCE_URL_PATTERN` | L44 |
| | `thread_config()` | L46–54 |
| | `create_llm()`（原 `create_agent_llm` rename） | L182–195 |
| | `extract_sources_from_messages()` | L311–326 |
| | `_message_content_to_text()` | L329–347 |
| `src/app/tools/site_discovery.py`（新檔） | `_DiscoveryInputSchema` | L198–199 |
| | `create_site_discovery_tool()` | L202–222 |
| `src/app/workflow/run_manager.py` | `RunManager.find_thread_history_path()`（原 `_find_thread_history_path`，改 staticmethod） | L351–389 |

### 24-2. 新模組結構

#### `src/utils/langchain_helper.py`（LangChain 輔助函式）

```python
SOURCE_URL_PATTERN = re.compile(r"URL: (\S+)")          # L22
def thread_config(thread_id: str | None) -> dict[str, dict[str, str]]  # L25
def create_llm(llm_name: str) -> ChatGoogleGenerativeAI  # L36
def extract_sources_from_messages(messages: list[Any]) -> list[str]   # L52
def _message_content_to_text(content: Any) -> str        # L70
```

- `create_llm` 為 **LangChain ChatModel 版**（回傳 `ChatGoogleGenerativeAI`），與 `utils.rag_helper.create_llm`（LlamaIndex 版，回傳 `GoogleGenAI | OpenAI`）同名但不同模組；docstring 已明確標註對稱性避免混淆。
- 依賴：`os` / `re` / `uuid` / `dotenv` / `langchain_google_genai`。

#### `src/app/tools/site_discovery.py`（Site Discovery 工具）

```python
class _DiscoveryInputSchema(BaseModel): ...              # L12
def create_site_discovery_tool(registry: RAGRegistry) -> StructuredTool  # L16
```

- 僅 import `RAGRegistry`（單向依賴，無循環 import 風險）。

#### `src/app/workflow/run_manager.py`（追加 staticmethod）

```python
@staticmethod
def find_thread_history_path(
    base_folder: str,
    module_name: str,
    history_filename: str,
) -> str | None:                                          # L177
```

- 邏輯保留完整：timestamped folder 過濾（15 chars、`startswith("20")`）、lexicographically last、找到即 break。

### 24-3. 檔案變更清單

| File | Action | Description |
|------|--------|-------------|
| `src/utils/langchain_helper.py` | **Add** | 5 個 symbol：`SOURCE_URL_PATTERN`、`thread_config`、`extract_sources_from_messages`、`_message_content_to_text`、`create_llm` |
| `src/app/tools/site_discovery.py` | **Add** | `_DiscoveryInputSchema`、`create_site_discovery_tool` |
| `src/app/workflow/run_manager.py` | **Modify** | 追加 `@staticmethod find_thread_history_path()`（`save_results_as_json` 之後） |
| `src/app/agent/agent.py` | **Modify** | 刪 5 個 import、加 2 個 import；移除 8 個搬移 symbol；`create_agent_llm` → `create_llm`；`_find_thread_history_path` → `RunManager.find_thread_history_path`；docstring 更新 |
| `src/app/server/app.py` | **Modify** | `extract_sources_from_messages` / `thread_config` 改從 `utils.langchain_helper` import |
| `src/test/dev/test_agent_server.py` | **Modify** | 3 個函數改從 `utils.langchain_helper` import；docstring 更新 |
| `docs/code/phase2_3_mvp/modules/agent.md` | **Modify** | 模組清單新增 `site_discovery.py` / `langchain_helper.py`；函數描述同步 |
| `docs/code/phase2_3_mvp/modules/server.md` | **Modify** | `thread_config` / `extract_sources_from_messages` 來源標註為 `utils.langchain_helper` |
| `README.md` | **Modify** | 環境變數表 `GEMINI_RAG_QUERY_ENGINE_API_KEY` 使用位置改為 `utils/rag_helper.py`、`utils/langchain_helper.py`（CR 建議修正） |

### 24-4. 決策記錄

| 決策 | 理由 |
|---|---|
| `create_agent_llm` rename 為 `create_llm` | 與 `rag_helper.create_llm` 命名對稱；docstring 標註「LangChain ChatModel 版」避免混淆 |
| `StructuredTool` 保留於 agent.py | `Agent.tools` 欄位型別仍需要 |
| `test_rag_tools.py` 無需變更 | 該檔未實際 import `create_site_discovery_tool`（僅 docstring 提及） |
| `docs/work/` 歷史記錄不修改 | 歷史工作記錄保持原樣 |
| `_message_content_to_text` 由 agent.py re-import | 仍被 `Agent.ask` / `astream_text` 使用 |

### 24-5. 驗證結果

| 驗證項目 | 結果 |
|---|---|
| `uv run ruff check src/` | ✅ All checks passed! |
| `uv run pyright src/` | ✅ 2 errors 均為 pre-existing（`rag_factory.py:297` milvus_uri 型別、`test_agent_server.py:131` CoroutineType），與本次重構無關 |
| `uv run pytest`（src/test/dev/ 全部 5 檔） | ✅ 127/127 passed |
| 搬移完整性（grep） | ✅ `create_agent_llm` / `_find_thread_history_path` 全倉無殘留 |
| Edge cases 行為 | ✅ `thread_config(None)` 產生 `auto-{uuid}`；`create_llm` 缺 env 拋 ValueError；`extract_sources_from_messages` 依序去重；`find_thread_history_path` 最新 timestamp / 非 timestamped 過濾 / 不存在回傳 None / 巢狀遞迴搜尋 |
