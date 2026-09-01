# 多網站 RAG 檢索規劃 (2026/08/19)

## 1. 摘要

| 目標 | 核心問題 | 優先度 |
|------|---------|--------|
| **擷取網頁時間資訊** | 目前時間 metadata 僅靠 `MarkdownDateExtractor` 從內容推斷，頁面無明顯日期時不精確；應在爬蟲階段從 HTML 結構化標籤擷取 | 高 |
| **建置多個不同學校網站知識庫** | 爬蟲設定、資料目錄、向量庫全部指向單一網站（`nculab`），缺乏多網站隔離機制 | 高 |
| **RAG 工具支援檢索不同網站知識庫** | `webpage_retriever` StructuredTool 目前硬綁單一 RAG 實例，無法根據查詢目標切換知識庫 | 高 |
| **Chrome Extension 站點偵測與 Agent 路由** | Extension 無法得知使用者正在瀏覽哪個網站，Server 無法自動路由至對應知識庫 | 高 |

**結論**：四個目標有明確的依賴順序——先完成時間擷取與多站基礎建設（可並行），再改造 RAG 工具支援多站檢索，最後結合 Chrome Extension 站點偵測讓 Agent 自動路由。

---

## 2. 里程碑與執行順序

```
目標 1（時間擷取）         目標 2（多站建庫）           目標 3（多站 RAG 檢索）      目標 4（Extension 站點偵測）
─────────────────         ──────────────────           ────────────────────          ───────────────────────
1-1 HTML metadata          2-1 目錄重構 ←───────────── 依賴 2-1                       4-1 Extension 偵測 URL
1-2 metadata 欄位擴充      2-2 設定檔模板化            3-1 Tool 參數擴充 ←── 依賴 2-4  4-2 Background 轉發
1-3 降級改進               2-3 向量庫隔離              3-2 RAGRegistry ←─── 依賴 2-3   4-3 後端 domain mapping
1-4 日期格式驗證           2-4 RAG 設定檔 per site     3-3 Tool 改用 Registry ← 3-2     4-4 query 前綴 site 語境
1-5 重新處理               2-5 metadata 加入 site_id   3-4 站點發現工具                  4-5 Agent 整合（M3+M4 串接）
                           2-6 Agent 設定檔            3-5 System prompt 更新          4-6 端到端測試
                           2-7 腳本化建庫              3-6 Agent 整合（Registry）
```

### 里程碑切分

| 里程碑 | 內容 | 依賴 | 預估工作量 |
|--------|------|------|-----------|
| **M1：時間擷取** | 1-1 → 1-2 → 1-3 → 1-4 → 1-5 | 無 | 中 |
| **M2：多站基礎建設** | 2-1 → 2-2 → 2-3 → 2-5 → 2-7 | 無 | 中 |
| **M3：多站 RAG 檢索** | 3-1 → 3-2 → 3-3 → 3-4 → 3-5 → 3-6 | M2 | 高（核心改造） |
| **M4：Extension 站點偵測與路由** | 4-1 → 4-2 → 4-3 → 4-4 → 4-5 → 4-6 | M3 | 中 |

> **M1 與 M2 可並行**（互不依賴）；M3 必須等 M2 完成後才能開始；M4 必須等 M3 完成後才能開始。M3 可獨立驗證（CLI Agent + site_id 前綴）；M4 為 Chrome Extension 端到端整合。

---

## 3. 目標 1：擷取網頁時間資訊

> **核心問題**：目前時間 metadata 僅靠 `MarkdownDateExtractor` 從 Markdown 內容推斷（四層遞減策略），頁面無明顯日期時萃取不精確。應在**爬蟲階段**就從 HTML 結構化標籤擷取。

### 工作項目

| # | 工作項目 | 涉及模組 | 說明 |
|---|---------|---------|------|
| 1-1 | **爬蟲 HTML metadata 擷取** | `website_crawler.py` | 從 `<meta>` 標籤、`<time datetime>` 元素、JSON-LD `datePublished` 等結構化標籤擷取發佈日期 |
| 1-2 | **metadata 欄位擴充** | `website_crawler.py` / `_extract_metadata()` | 將擷取到的日期寫入 `crawl_result["metadata"]["published_date"]`（ISO 8601 格式） |
| 1-3 | **MarkdownDateExtractor 降級改進** | `rag.py` / `NodePipelineBuilder` | 當 HTML metadata 有 `published_date` 時直接注入 node metadata，跳過內容推斷 |
| 1-4 | **日期格式驗證** | `rag_config.py` / `rag_helper.py` | 確保 `published_date` 為有效 ISO 8601，無效則回落到 `MarkdownDateExtractor` |
| 1-5 | **已有資料重新處理** | 爬蟲 pipeline | 對已爬取的 `data/webpages/results/` 重新執行 metadata 擷取（或重新爬取） |

> 具體實作規格（解析優先級、程式碼設計、測試案例），請參閱 [dev_log.md](dev_log.md) §1。
>
> **實作成果 (2026/08/19)**：HTML 日期擷取功能已完成實作與 35 個單元測試（全部通過），但經端到端驗證，nculab（Google Sites）與 csie（自架 PHP 站）的所有頁面均無法從 HTML 擷取到日期——兩個網站皆無結構化日期標籤（JSON-LD、OG meta、`<time>` 元素等），伺服器也不回傳 `Last-Modified` 標頭。HTML 日期擷取僅對有 SEO 套件的網站（如 WordPress、Medium）有效，對這兩個目標網站不適用。後續仍須依賴 `MarkdownDateExtractor` 內容推斷作為主要日期來源。

---

## 4. 目標 2：建置多個不同學校網站知識庫

> **核心問題**：目前爬蟲設定、資料目錄、向量庫全部指向單一網站（`nculab`），缺乏多網站隔離機制。

### 工作項目

| # | 工作項目 | 涉及模組 | 說明 |
|---|---------|---------|------|
| 2-1 | **資料目錄結構重構** | 專案根目錄 | 改為 `data/webpages/{site_id}/` 結構，每個網站獨立 `results.json` + `results/` 目錄 |
| 2-2 | **爬蟲設定檔模板化** | `configs/website_crawler/` | 建立 `{site_id}.toml` 模板（`url`、`url_patterns`、`allowed_domains`、`exclude_words` 可調） |
| 2-3 | **向量庫隔離** | `rag_config.py` | 每個網站獨立 `collection_name`（如 `webpages_nculab`、`webpages_nctu`）或獨立 Milvus DB 檔案 |
| 2-4 | **RAG 設定檔 per site** | `configs/rag/` | 建立 `{site_id}.toml`，指定對應的 `webpages_data_folder_path` 與 `collection_name` |
| 2-5 | **metadata 加入 site_id** | 爬蟲 + RAG pipeline | 所有 node 的 metadata 注入 `site_id` 欄位，作為跨網站檢索的過濾條件 |
| 2-6 | **Agent 設定檔多 site 支援** | `configs/agent/` | `AgentConfig` 可指定多個 `rag_config_names`，讓 Agent 知道可呼叫哪些知識庫 |
| 2-7 | **腳本化建庫流程** | `scripts/` | 建立一鍵腳本：爬取 → 圖片摘要 → 建索引，支援 `--site-id` 參數 |

### 目錄結構（重構後）

```
data/
├── webpages/
│   ├── nculab/
│   │   ├── results.json
│   │   └── results/
│   │       └── *.md
│   ├── nctu/
│   │   ├── results.json
│   │   └── results/
│   └── ...
├── rag/
│   ├── nculab/
│   │   └── milvus.db
│   ├── nctu/
│   │   └── milvus.db
│   └── ...
```

> 具體的 DataManager 介面設計、RunManager 改動、Workflow 函式簽名變化，請參閱 [dev_log.md](dev_log.md) §3。

---

## 5. 目標 3：RAG 工具支援檢索不同網站知識庫

> **核心問題**：`webpage_retriever` StructuredTool 目前硬綁單一 RAG 實例，無法根據查詢目標切換知識庫。
> M2 完成後，資料與向量庫已按 site_id 隔離，但 Agent 工具層仍缺少多站路由能力。

### 工作項目

| # | 工作項目 | 涉及模組 | 說明 |
|---|---------|---------|------|
| 3-1 | **Tool 參數擴充** | `webpage_retriever.py` | `RetrieverInputSchema` 加入 `site_id: str` 參數，Agent 可根據使用者問題選擇目標網站 |
| 3-2 | **多 RAG 實例管理** | `rag_registry.py`（新） | 建立 `RAGRegistry`，依 `site_id` 延遲建立 RAG 實例並以 LRU 快取；利用 Milvus 重用機制（§14）避免每次重建 |
| 3-3 | **Tool 改用 Registry** | `webpage_retriever.py` | `create_webpage_retriever_tool` 改為接收 `RAGRegistry`；`_retrieve` 內部以 `registry.get(site_id)` 路由至對應 RAG |
| 3-4 | **站點發現工具** | `agent.py` | 新增 `create_site_discovery_tool(registry)` → `list_knowledge_bases` 工具，掃描 `data/rag/` 回傳可用 site_id |
| 3-5 | **System prompt 更新** | `agent_config.py` / TOML | 更新為多站路由版本，指引 LLM 先用 `list_knowledge_bases` 確認站點再呼叫 `webpage_retriever` |
| 3-6 | **Agent 整合** | `agent.py` | `create_agent` 建立 Registry + 兩個工具；`Agent` 新增 `registry` 欄位，`close()` 改用 `registry.close()` |

> 具體的 RAGRegistry 設計、Tool 簽名變更、Agent 整合流程，請參閱 [2026_0826-multi_site_RAG_tool.md](2026_0826-multi_site_RAG_tool.md)。

---

## 6. 目標 4：Chrome Extension 站點偵測與 Agent 路由

> **核心問題**：Chrome Extension 無法得知使用者正在瀏覽哪個網站，Server 無法自動路由至對應知識庫。
> M3 完成後 Agent 工具已支援 `site_id` 多站路由，但 `site_id` 來源仍依賴 LLM 自行判斷。
> 本目標從 Extension 前端偵測 → 後端映射 → query 語境注入，實現無感的自動多站路由。

### 工作項目

| # | 工作項目 | 涉及模組 | 說明 |
|---|---------|---------|------|
| 4-1 | **Extension 偵測當前 URL** | `extension/content.js` | `content.js` 讀取 `window.location.hostname`，在每次 chat 請求時帶入 `page_url` 欄位 |
| 4-2 | **Background 轉發 page_url** | `extension/background.js` | `background.js` 將 `page_url` 透傳至 Server `/api/chat` endpoint |
| 4-3 | **後端 domain → site_id 映射** | `src/app/server/app.py` | `ChatRequest` 新增 `page_url` 欄位；`DOMAIN_SITE_MAP` dict + `resolve_site_id()` 函數，支援精確匹配與子域名 suffix 匹配 |
| 4-4 | **query 前綴 site 語境** | `src/app/server/app.py` | `_enrich_query_with_site_context()` 將 site_id 前綴至 user query（如 `[使用者瀏覽 nculab 網站] 實驗室成員`），讓 LLM 從 message 內容感知當前站點 |
| 4-5 | **Agent 整合** | `src/app/agent/agent.py` | M3 的 `Agent` + `RAGRegistry` 與 M4 的 `site_id` 前綴機制串接，`_event_stream` 接收 `site_id` 參數 |
| 4-6 | **端到端測試** | Chrome + Server + Agent | Chrome 開啟 nculab 頁面 → Extension 自動偵測 → Server 映射 → Agent 路由 → 正確檢索；切換至 csie 頁面 → 自動切換 |

### 全域資料流

```
Extension content.js                    Server app.py                     Agent + RAG
───────────────────                     ─────────────                     ───────────
window.location.hostname                ChatRequest.page_url
        │                                      │
        ├─ port.postMessage({                  ├─ resolve_site_id(page_url)
        │    page_url: hostname })              │   → "nculab"
        │                                      │
        └─ background.js                       └─ _enrich_query_with_site_context(
             fetch POST {                            query, "nculab"
               page_url: hostname               ) → "[使用者瀏覽 nculab 網站] 實驗室成員"
             }                                        │
                                                  agent.graph.invoke(...)
                                                       │
                                                  LLM 看到 site 語境
                                                       │
                                                  webpage_retriever(
                                                    site_id="nculab",
                                                    query="實驗室成員"
                                                  )
                                                       │
                                                  RAGRegistry.get("nculab")
                                                       │
                                                  rag.retrieve(...) → 正確結果
```

### 三種介面的 site_id 來源

| 介面 | site_id 來源 | 改動量 |
|------|-------------|--------|
| **Chrome Extension** | `window.location.hostname` → 後端 `DOMAIN_SITE_MAP` 映射 | content.js + background.js + app.py |
| **CLI** | `--site-id` 手動指定（已有）或 query 帶 site_id 前綴 | 無需改動 |
| **Server API** | 請求參數 `page_url`（可選） | ChatRequest model + mapping |

> 具體的 Extension 改動規格、後端映射設計、query 前綴機制，請參閱 [2026_0826-chrome_extension_site_detection.md](2026_0826-chrome_extension_site_detection.md)。

---

## 7. 風險與注意事項

| # | 風險 | 影響 | 緩解措施 |
|---|------|------|---------|
| 1 | 資料目錄重構影響既有流程 | 既有 `data/webpages/` 下的資料與設定檔路徑全部失效 | 建立 migration 腳本自動搬移；保留 fallback 讀取舊路徑 |
| 2 | 多向量庫占用磁碟空間 | 每個網站的 Milvus DB 約數十 MB~數百 MB | 先以 2-3 個學校試驗，確認规模後再擴展 |
| 3 | 多 RAG 實例記憶體壓力 | 同時載入多個向量庫可能消耗大量 RAM | `RAGRegistry` 採用 LRU 快取策略，超出數量上限時釋放最久未用的實例 |
| 4 | Agent 多站路由準確度 | LLM 可能選錯 site_id 或遺漏相關網站 | 在 system prompt 提供明確的網站描述；Chrome Extension 自動偵測 site_id 輔助路由 |
| 5 | HTML 日期標籤格式不一致 | 不同網站的 `<meta>` 標籤格式差異大 | 建立日期解析器支援多種格式；無效時回落到內容推斷 |
| 6 | Extension hostname 無法映射 | 內網 IP / localhost 等無對應 site_id | `resolve_site_id` 回傳 None → LLM 自行用 `list_knowledge_bases` 確認 |
| 7 | query 前綴 token 佔用 | `"[使用者瀏覽 nculab 網站]"` 佔 ~15 tokens | 可忽略；LLM context window 128K+；或未來改為 per-request system prompt |

---

## 8. 驗證標準

| 里程碑 | 驗證標準 |
|--------|---------|
| **M1：時間擷取** | 爬取新網站後，`results.json` 中 ≥80% 頁面有有效 `published_date`；`MarkdownDateExtractor` 在有 HTML metadata 時正確跳過 |
| **M2：多站基礎建設** | 能為 2+ 個學校網站分別爬取、建庫，目錄與向量庫完全隔離；`--site-id` 參數正常運作 |
| **M3：多站 RAG 檢索** | `webpage_retriever(site_id="nculab", query="...")` 僅從 nculab 知識庫檢索；`RAGRegistry` 快取命中 < 3s；CLI Agent query 帶 site_id 前綴後正確路由 |
| **M4：Extension 站點偵測** | Chrome 開啟 nculab 頁面問答 → 自動路由至 nculab RAG；切換至 csie 頁面 → 自動切換至 ncucsie；Server `resolve_site_id()` 正確映射 |

---

## 9. 結論

四個目標的改造範圍涵蓋從**爬蟲底層**到**Chrome Extension 前端**的完整鏈路：

1. **M1（時間擷取）** 解決 metadata 品質問題，提升檢索精準度。
2. **M2（多站建庫）** 建立多站隔離的基礎設施，是 M3 的必要前置。
3. **M3（多站 RAG 檢索）** 核心改造，讓 RAG 工具從單站升級為多站（`RAGRegistry` + `site_id` 路由）。
4. **M4（Extension 站點偵測）** 結合 Chrome Extension 自動偵測使用者瀏覽的網站，透過後端 domain → site_id 映射與 query 前綴機制，實現無感多站路由。

建議 **M1 與 M2 並行啟動**；M2 完成後推進 M3（可用 CLI Agent 獨立驗證）；M3 完成後進行 M4（Chrome Extension 端到端整合）。
