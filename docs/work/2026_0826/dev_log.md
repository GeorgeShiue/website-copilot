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

`create_site_discovery_tool(registry)` → `list_knowledge_bases` 工具（需空 `args_schema`）。`create_rag_agent()` 建立 Registry + 兩個工具；`RAGAgent` 新增 `registry` 欄位，`close()` 委派 `registry.close()`。

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

> 技術債分析：`docs/work/issiue.md` H2 節。專案中 10 處 `except Exception` 分布於 7 個檔案，存在靜默吞錯誤、log level 誤用、exception 類型過寬等問題。

### 18-1. 問題分類

| 嚴重度 | 檔案 | 問題 |
|--------|------|------|
| 🔴 Critical | `rag.py` L78 | `except Exception: pass` — Milvus client 關閉失敗完全靜默，`_closed = True` 在 try 之前導致不可重入，連接洩漏風險 |
| 🟠 Medium | `rag_helper.py` L259+L266 | 用 `except Exception` 包 `.get()` — 過度防禦，掩盖 API 變動 |
| 🟡 Low-Med | `html_date_extractor.py` L111 | `logger.debug` — BeautifulSoup 失敗應為 `warning`，且缺 `exc_info=True` |
| 🟠 Medium | `markdown_cleaner.py` L90 | `except Exception` — `mdformat` 只會拋 `ValueError`/`KeyError`，過寬；`logger.error` 應改 `warning` |
| 🟡 Medium | `webpage_image_summarizer.py` L293 | `except Exception` — 圖片下載失敗應用 `URLError`/`TimeoutError`/`OSError` |
| 🟡 Medium | `webpage_image_summarizer.py` L379+L438 | 缺 `exc_info=True`，async task traceback 喪失 |
| 🟠 Medium | `website_crawler.py` L294 | `_safe_step` f-string + 缺 `exc_info=True` |

`server/app.py` L131 的 `except Exception` 使用 `logger.exception()` + SSE 錯誤回傳，為合理模式，不需修改。

### 18-2. 修正策略

三層原則：
1. **收窄 exception 類型**：能確定的用具體 exception（`URLError`、`ValueError`、`KeyError`），不確定的保留 `Exception` 但加 `exc_info`
2. **不再靜默吞錯誤**：所有 `except Exception` 至少有 `logger.warning/error` + `exc_info=True`
3. **修復控制流缺陷**：`rag.py` 的 `_closed = True` 移至 close 成功之後

### 18-3. 變更範圍

| 優先序 | 檔案 | 變更 |
|--------|------|------|
| P0 | `src/app/engines/rag/rag.py` | `except Exception: pass` → `logger.warning("Milvus client close() failed", exc_info=True)`；`_closed = True` 從 try 前移至 try 後，確保 close 失敗仍可重試 |
| P1 | `src/utils/markdown_cleaner.py` | `except Exception as e` → `except (ValueError, KeyError) as e`；`logger.error(f"...")` → `logger.warning("mdformat failed, using unformatted markdown: %s", e)` |
| P1 | `src/app/engines/website_crawler.py` | `_safe_step` 加 `exc_info=True`；f-string → `%s` lazy formatting |
| P2 | `src/utils/rag_helper.py` | 移除兩處 `except Exception`，改用 `getattr(source_node.node, "metadata", None) or {}` null 檢查 |
| P2 | `src/utils/html_date_extractor.py` | `logger.debug` → `logger.warning(..., exc_info=True)` |
| P2 | `src/app/engines/webpage_image_summarizer.py` | E6：`except Exception` → `except (URLError, TimeoutError, OSError)`，新增 `from urllib.error import URLError`；E7+E8：加 `exc_info=True` |

### 18-4. 關鍵修正詳解

**P0 — `rag.py` close() 連接洩漏修復**

```python
# Before
def close(self) -> None:
    if getattr(self, "_closed", False):
        return
    self._closed = True          # ← close 前就標記，失敗不可重試
    if isinstance(self.vector_store, MilvusVectorStore):
        try:
            self.vector_store._milvusclient.close()
        except Exception:
            pass                 # ← 完全靜默，連接可能洩漏
    self.vector_store = None     # ← 即使 close 失敗仍清 reference

# After
def close(self) -> None:
    if getattr(self, "_closed", False):
        return
    if isinstance(self.vector_store, MilvusVectorStore):
        try:
            self.vector_store._milvusclient.close()
        except Exception:
            logger.warning("Milvus client close() failed", exc_info=True)
    self._closed = True          # ← close 成功後才標記
    self.vector_store = None
```

**P2 — `rag_helper.py` 消除不必要 exception handling**

```python
# Before
try:
    page_title = source_node.node.metadata.get("page_title", "Unknown")
except Exception:
    page_title = "Unknown"

# After — null 檢查取代 exception
metadata = getattr(source_node.node, "metadata", None) or {}
page_title = metadata.get("page_title", "Unknown")
```

**P2 — `webpage_image_summarizer.py` exception 收窄**

```python
# Before
except Exception as e:
    logger.warning("Image download failed (url=%s) : %s", url, e)

# After — 僅捕獲網路 I/O 相關 exception
except (URLError, TimeoutError, OSError) as e:
    logger.warning("Image download failed (url=%s): %s", url, e)
```

### 18-5. 驗證

| 項目 | 結果 |
|------|------|
| `pytest src/test/dev/test_html_date_extraction.py` | 35 passed |
| `pytest src/test/dev/test_dedup_key.py` | 12 passed |
| Pylance 診斷（6 個修改檔案） | 0 errors |
| 語法檢查（`get_errors`） | 0 errors |

---

## 19. 測試檔案整合（2026-08-27）

### 19-1. 動機

`src/test/dev/` 累積 10 個測試檔案，部分檔案測試同一子系統的不同層面（如 `test_agent.py` 純函式 vs `test_server.py` SSE/CORS），替身基礎設施重複。另有 `test_legacy_results_removal.py` 測試前提已不存在（legacy 目錄已移除），`scripts/m0_rag_smoke.py` 功能可被單元測試取代。

### 19-2. 刪除

| 檔案 | 原因 |
|------|------|
| `test_legacy_results_removal.py` | legacy 目錄（`data/rag/results`、`data/webpages/results`）已不存在，`TestLegacyDirectoriesExist` 會直接 FAIL |
| `scripts/m0_rag_smoke.py` | 功能合併至 `test_rag_tools.py` 的 `TestRAGRetrieverSmoke` |

### 19-3. 合併 A：`test_agent.py` + `test_server.py` → `test_agent_server.py`

兩者測試同一個 agent 層（`app.agent.agent` 和 `app.server.app`），共用相似的替身概念（`_FakeConfig` / `FakeRunManager` / `FakeAgent`）。合併後統一替身基礎設施，消除重複。

| 來源 | 合併內容 |
|------|---------|
| `test_agent.py` | Agent 純函式：`thread_config` / `extract_sources_from_messages` / `_message_content_to_text` / `save_conversation_results` |
| `test_server.py` | Server 層：SSE 串流 / error 事件 / health / CORS / static files / `resolve_site_id` / `_enrich_query_with_site_context` |

衝突處理：兩邊的 `_FakeConfig` 完全相同 → 保留一份；`_FakeRunManager` 統一採用 test_server.py 版本（`saved` 初始為 `{}` 而非 `None`，兼容兩邊測試）。

### 19-4. 合併 B：`test_rag_registry.py` + `test_rag_reuse.py` + `test_multi_site_tool.py` + `m0_rag_smoke.py` → `test_rag_tools.py`

四者都測試 RAG 子系統（registry 快取、builder 重建、retriever 工具、smoke 驗證），共用 mock 基礎設施（`_make_mock_registry`、`_make_fake_retrieval_results`）。

| 來源 | 合併內容 |
|------|---------|
| `test_rag_registry.py` | `RAGRegistry`：cache hit / cache miss / LRU eviction / close / list_sites |
| `test_rag_reuse.py` | `RAGBuilder._should_rebuild`：Milvus 路徑判斷 |
| `test_multi_site_tool.py` | Retriever 工具：schema 驗證、tool 建立、retrieve 路由、格式化 |
| `m0_rag_smoke.py` | Smoke 驗證：registry + tool 建立 → invoke → close（改用 mock registry） |

衝突處理：`_make_mock_registry` 保留使用 `spec=RAGRegistry` 的版本（更嚴謹）。`_FakeRAGConfig` 從 15 個欄位精簡至 2 個（`vector_store_type`、`milvus_uri`），因 `_should_rebuild` 僅讀取這兩個欄位。

### 19-5. 內部精簡

| 檔案 | 精簡 |
|------|------|
| `test_runmanager_datamanager.py` | `import json` 從 test method 內部移至模組頂端 |
| `test_rag_tools.py` | `_FakeRAGConfig` 精簡（15 → 2 欄位）；`_make_builder` 加 `# type: ignore[arg-type]` |
| `test_html_date_extraction.py` | `TestParseHttpDate`（4 tests）+ `TestNormalizeToIso8601`（6 tests）改用 `@pytest.mark.parametrize` |
| `test_dedup_key.py` | `from urllib.parse import urlparse` 從 `_make_crawler` 內部移至模組頂端 |

### 19-6. 結果

```
src/test/dev/  (10 → 6 檔案，40% 減少)
├── test_agent_server.py          ← 合併 A + 精簡
├── test_rag_tools.py             ← 合併 B + 精簡
├── test_dedup_key.py             ← 保留 + 精簡
├── test_html_date_extraction.py  ← 保留 + 精簡
├── test_runmanager_datamanager.py ← 保留 + 精簡
└── test_multi_site.py            ← 保留（整合測試）

scripts/  ← §21 整個刪除
```

| 項目 | 結果 |
|------|------|
| `pytest src/test/dev/` | **125 passed**, 0 failed |
| Pylance 診斷（全部 dev 測試） | 0 errors |

---

## 20. Server 架構重構 — 統一入口與工具抽取（2026-08-28）

> 目標：消除 server 啟動/測試的重工，建立單一統一入口 `workflow.run_server()`。

### 20-1. 問題

重構前 server 相關程式碼分散於三個檔案，呼叫鏈冗長：

```
server_up.py → spawn(cli.py server-cli) → app.run_server()
m3_server_smoke.py → spawn(cli.py server-cli) → app.run_server()
test_module.py → workflow.run_server() → spawn(cli.py server-cli) → app.run_server()
cli.py server-cli → app.run_server()（一行轉發）
```

問題：
- `cli.py ServerCLI` 分支僅一行轉發，是多餘的間接層
- `server_up.py` 與 `cli.py server-cli` 功能完全重疊
- `app.run_server` 與 `workflow.run_server` 命名衝突
- subprocess command 路徑過長（3 層間接）

### 20-2. 新架構

```
cli.py server-cli → workflow.run_server(mode="block")
                       └─→ spawn(app.start_uvicorn()) → app.start_uvicorn()

test_module.py    → workflow.run_server(mode="validate")
                       └─→ spawn(app.start_uvicorn()) → app.start_uvicorn()
                           → validate SSE → shutdown
```

### 20-3. 新增 `src/utils/server_helper.py`

從 `server_up.py` 和 `m3_server_smoke.py` 提取共用工具：

| 函式 | 職責 | 來源 |
|------|------|------|
| `spawn_server()` | subprocess 啟動 `app.start_uvicorn()` | 兩者共有 |
| `wait_ready()` | health polling (`/api/health`) | 兩者共有 |
| `shutdown_server()` | SIGTERM → SIGKILL 優雅關閉 | 兩者共有 |
| `parse_sse_events()` | SSE body → event dict 列表 | `m3_server_smoke.py` |
| `stream_chat()` | POST `/api/chat` | `m3_server_smoke.py` |
| `check_single_turn()` | SSE 協定驗證 | `m3_server_smoke.py` |
| `latest_results_json()` | 最新 results.json 查找 | `m3_server_smoke.py` |
| `check_persistence()` | 落盤驗證 | `m3_server_smoke.py` |

**常數**：`HEALTH_TIMEOUT_SEC=600`、`DEFAULT_QUERY`、`DEFAULT_FOLLOW_UP`。

**`spawn_server()` 設計**：
- `output` 參數：`Literal["inherit", "devnull"] | Path`（三種模式）
- `config_name` 以 `assert config_name.isidentifier()` 防禦注入
- subprocess command 直接呼叫 `app.start_uvicorn()`（跳過 `cli.py server-cli`）
- file handle 生命週期：`proc._output_fh` 附加，由 `shutdown_server()` 關閉

### 20-4. `workflow.run_server()` 重構

```python
def run_server(
    host, port, config_name,
    mode: Literal["validate", "block"] = "validate",
    *, output, allowed_origins, startup_timeout,
    query, follow_up,
) -> None:
```

| mode | 行為 |
|------|------|
| `"validate"` | spawn → wait_ready → SSE 單輪/多輪 → 落盤 → shutdown |
| `"block"` | spawn → wait_ready → `proc.wait()` → Ctrl+C → shutdown |

validate 核心邏輯抽取為 `_validate_server()` 私有函式。

### 20-5. `app.run_server()` → `app.start_uvicorn()`

解決 `app.run_server` 與 `workflow.run_server` 的命名衝突：

```python
# app.py — 純 factory + 啟動器
def create_app()      → FastAPI app
def start_uvicorn()   → setup_logging + create_app + uvicorn.run

# workflow.py — 生命週期管理
def run_server()      → spawn + wait + validate/block + shutdown
```

### 20-6. `cli.py` 改動

- import 從 `from app.server.app import run_server` 改為 `from app.workflow.workflow import run_server`
- ServerCLI 分支：`run_server(**vars(cli_arg.run), mode="block")`
- 合併重複的 `from app.workflow.workflow import` 區塊

### 20-7. `test_module.py` 改動

```python
# Before（~30 行）
def test_server():
    proc = spawn_server(...)
    try:
        elapsed = wait_ready(...)
        events = stream_chat(...)
        single = check_single_turn(events)
        ...
    finally:
        shutdown_server(proc)

# After（2 行）
def test_server():
    """驗證 server 啟動、health check、SSE 單輪/多輪、落盤。"""
    run_server(host="127.0.0.1", port=SERVER_PORT, config_name="test")
```

### 20-8. 變更範圍

| 檔案 | 操作 | 說明 |
|------|------|------|
| `src/utils/server_helper.py` | **新增** | 共用 server 工具（8 函式 + 4 常數） |
| `src/app/workflow/workflow.py` | 修改 | `run_server()` 重構 + `_validate_server()` + `Literal` import |
| `src/app/server/app.py` | 修改 | `run_server` → `start_uvicorn`（函式名 + docstring） |
| `src/cli.py` | 修改 | import 改為 `workflow.run_server` + `mode="block"` + 合併 import |
| `src/test/test_module.py` | 修改 | 新增 `test_server()`（2 行呼叫） |
| `scripts/server_up.py` | **刪除** | 功能由 `cli.py server-cli` 取代 |
| `scripts/m3_server_smoke.py` | **刪除** | 功能由 `workflow.run_server()` 取代 |

### 20-9. 驗證

| 項目 | 結果 |
|------|------|
| Pylance 診斷（4 個修改檔案） | 0 errors |
| Ruff lint | 0 issues |
| Import 解析 | ✅ |
| server_up.py 已刪除 | ✅ |

---

## 21. Scripts 資料夾刪除（2026-08-28）

### 21-1. 動機

`scripts/` 資料夾原存放三個腳本：

| 檔案 | 狀態 |
|------|------|
| `server_up.py` | §20 已刪除（功能由 `cli.py server-cli` 取代） |
| `m3_server_smoke.py` | §20 已刪除（功能由 `workflow.run_server()` 取代） |
| `m4b_extension_test.py` | Playwright E2E 測試，尚在使用 |

§20 重構後，`server_up.py` 和 `m3_server_smoke.py` 已無功能殘留。`m4b_extension_test.py` 為 Chrome Extension 的 E2E 測試，獨立於 server 架構。

### 21-2. 改動

| 操作 | 說明 |
|------|------|
| 刪除 `scripts/` 資料夾 | 整個目錄（含 `m4b_extension_test.py`） |

> ⚠️ `m4b_extension_test.py` 被一併刪除。如需恢復，可從 git 歷史還原。

### 21-3. 測試檔案結構（改後）

```
src/test/
├── test_module.py        ← 端到端測試（5 tests：crawler、summarizer、rag、agent、server）
├── test_main.py          ← 主流程測試
└── dev/
    ├── test_agent_server.py
    ├── test_rag_tools.py
    ├── test_dedup_key.py
    ├── test_html_date_extraction.py
    ├── test_runmanager_datamanager.py
    └── test_multi_site.py
```
