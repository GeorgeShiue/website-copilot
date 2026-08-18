# 多網站 RAG 檢索 (2026/08/18)

## 1. 摘要

| 目標 | 核心問題 | 優先度 |
|------|---------|--------|
| **擷取網頁時間資訊** | 目前時間 metadata 僅靠 `MarkdownDateExtractor` 從內容推斷，頁面無明顯日期時不精確；應在爬蟲階段從 HTML 結構化標籤擷取 | 高 |
| **建置多個不同學校網站知識庫** | 爬蟲設定、資料目錄、向量庫全部指向單一網站（`nculab`），缺乏多網站隔離機制 | 高 |
| **RAG 工具支援檢索不同網站知識庫** | `webpage_retriever` StructuredTool 目前硬綁單一 RAG 實例，無法根據查詢目標切換知識庫 | 高 |

**結論**：三個目標有明確的依賴順序——先完成時間擷取與多站基礎建設（可並行），再改造 RAG 工具支援多站檢索，最後整合 Agent 讓 LLM 自動路由。

---

## 2. 里程碑與執行順序

```
目標 1（時間擷取）         目標 2（多站建庫）           目標 3（多站檢索）
─────────────────         ──────────────────           ──────────────────
1-1 HTML metadata          2-1 目錄重構 ←───────────── 依賴 2-1
1-2 metadata 欄位擴充      2-2 設定檔模板化            3-1 Tool 參數擴充 ←── 依賴 2-4
1-3 降級改進               2-3 向量庫隔離              3-2 多 RAG 實例 ←──── 依賴 2-3
1-4 日期格式驗證           2-4 RAG 設定檔 per site     3-3 動態切換 ←────── 依賴 3-2
1-5 重新處理               2-5 metadata 加入 site_id   3-4 Agent prompt ←── 依賴 3-1
                           2-6 Agent 設定檔            3-5 metadata filter
                           2-7 腳本化建庫              3-6 fallback
```

### 里程碑切分

| 里程碑 | 內容 | 依賴 | 預估工作量 |
|--------|------|------|-----------|
| **M1：時間擷取** | 1-1 → 1-2 → 1-3 → 1-4 → 1-5 | 無 | 中 |
| **M2：多站基礎建設** | 2-1 → 2-2 → 2-3 → 2-5 → 2-7 | 無 | 中 |
| **M3：多站 RAG 檢索** | 2-4 → 2-6 → 3-1 → 3-2 → 3-3 → 3-5 | M2 | 高（核心改造） |
| **M4：Agent 多站整合** | 3-4 → 3-6 → Agent prompt 調校 → 端到端測試 | M3 | 中 |

> **M1 與 M2 可並行**（互不依賴）；M3 必須等 M2 完成後才能開始；M4 為最後收斂。

---

## 3. 目標 1：擷取網頁時間資訊

> **核心問題**：目前時間 metadata 僅靠 `MarkdownDateExtractor` 從 Markdown 內容推斷（四層遞減策略），頁面無明顯日期時萃取不精確。應在**爬蟲階段**就從 HTML 結構化標籤擷取。

### 工作項目

| # | 工作項目 | 涉及模組 | 說明 |
|---|---------|---------|------|
| 1-1 | **爬蟲 HTML metadata 擷取** | `website_crawler.py` | 從 `<meta>` 標籤（`article:published_time`、`og:updated_time`、`date`）、`<time datetime>` 元素、JSON-LD `datePublished` 等結構化標籤擷取發佈日期 |
| 1-2 | **metadata 欄位擴充** | `website_crawler.py` / `_extract_metadata()` | 將擷取到的日期寫入 `crawl_result["metadata"]["published_date"]`（ISO 8601 格式 `YYYY-MM-DD`），供下游直接使用 |
| 1-3 | **MarkdownDateExtractor 降級改進** | `rag.py` / `NodePipelineBuilder` | 當 HTML metadata 有 `published_date` 時直接注入 node metadata，跳過內容推斷；無 HTML metadata 時才走原有四層策略 |
| 1-4 | **日期格式驗證** | `rag_config.py` / `rag_helper.py` | 確保 `published_date` 為有效 ISO 8601，無效則回落到 `MarkdownDateExtractor` |
| 1-5 | **已有資料重新處理** | 爬蟲 pipeline | 對已爬取的 `data/webpages/results/` 重新執行 metadata 擷取（或重新爬取），補齊時間資訊 |

### 建議執行順序

```
1-1 爬蟲 HTML metadata 擷取
 → 1-2 metadata 欄位擴充（寫入 crawl_result）
 → 1-3 MarkdownDateExtractor 降級改進（優先使用 HTML metadata）
 → 1-4 日期格式驗證（ISO 8601 校驗）
 → 1-5 重新處理已有資料
```

---

## 4. 目標 2：建置多個不同學校網站知識庫

> **核心問題**：目前爬蟲設定、資料目錄、向量庫全部指向單一網站（`nculab`），缺乏多網站隔離機制。

### 工作項目

| # | 工作項目 | 涉及模組 | 說明 |
|---|---------|---------|------|
| 2-1 | **資料目錄結構重構** | 專案根目錄 | 改為 `data/webpages/{site_id}/` 結構，每個網站獨立 `results.json` + `results/` 目錄 |
| 2-2 | **爬蟲設定檔模板化** | `configs/website_crawler/` | 建立 `{site_id}.toml` 模板（`url`、`url_patterns`、`allowed_domains`、`exclude_words` 可調），方便為新網站快速建立設定 |
| 2-3 | **向量庫隔離** | `rag_config.py` | 每個網站獨立 `collection_name`（如 `webpages_nculab`、`webpages_nctu`）或獨立 Milvus DB 檔案 |
| 2-4 | **RAG 設定檔 per site** | `configs/rag/` | 建立 `{site_id}.toml`，指定對應的 `webpages_data_folder_path` 與 `collection_name` |
| 2-5 | **metadata 加入 site_id** | 爬蟲 + RAG pipeline | 所有 node 的 metadata 注入 `site_id` 欄位，作為跨網站檢索的過濾條件 |
| 2-6 | **Agent 設定檔多 site 支援** | `configs/agent/` | `AgentConfig` 可指定或多個 `rag_config_names`，讓 Agent 知道可呼叫哪些知識庫 |
| 2-7 | **腳本化建庫流程** | `scripts/` | 建立一鍵腳本：爬取 → 圖片摘要 → 建索引，支援 `--site-id` 參數 |

### 建議執行順序

```
2-1 資料目錄結構重構
 → 2-2 爬蟲設定檔模板化
 → 2-3 向量庫隔離
 → 2-5 metadata 加入 site_id
 → 2-7 腳本化建庫流程
 → (後續) 2-4 RAG 設定檔 per site → 2-6 Agent 設定檔
```

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

### 設定檔結構（重構後）

```toml
# configs/rag/nculab.toml
[init]
webpages_data_folder_path = "data/webpages/nculab"

[vector_store]
vector_store_type = "milvus"
milvus_uri = "data/rag/nculab/milvus.db"
collection_name = "webpages_nculab"
# ...其餘設定同 default
```

```toml
# configs/website_crawler/nculab.toml
[init]
max_depth = 2
content_threshold = 0.25

[crawl]
url = "https://sites.google.com/site/nculab/labintro"
url_patterns = ["*nculab*"]
allowed_domains = ["sites.google.com"]
exclude_words = ["..."]
```

---

## 5. 目標 3：RAG 工具支援檢索不同網站知識庫

> **核心問題**：`webpage_retriever` StructuredTool 目前硬綁單一 RAG 實例，無法根據查詢目標切換知識庫。

### 工作項目

| # | 工作項目 | 涉及模組 | 說明 |
|---|---------|---------|------|
| 3-1 | **Tool 參數擴充** | `webpage_retriever.py` | 加入 `site_id: str` 參數，Agent 可根據使用者問題選擇目標網站 |
| 3-2 | **多 RAG 實例管理** | `webpage_retriever.py` / `rag_factory.py` | 建立 `RAGRegistry` 或類似機制，依 `site_id` 載入/快取對應的 RAG 實例（避免每次查詢重建向量庫） |
| 3-3 | **向量庫動態切換** | `RAGBuilder.build_retriever()` | 支援執行期切換 `vector_store` / `collection_name`，或預建多個 retriever 按 site_id 路由 |
| 3-4 | **Agent tool calling 設計** | Agent system prompt | 在 system prompt 中告知 Agent 可用的 `site_id` 列表與對應網站名稱，讓 LLM 自動判斷該查哪個知識庫 |
| 3-5 | **metadata filter 跨網站** | `retrieve()` / `build_filters()` | 支援 `{"site_id": "nculab"}` 過濾條件，確保檢索範圍正確 |
| 3-6 | **fallback：跨網站搜尋** | Agent 邏輯 | 當 Agent 不確定目標網站時，可先搜尋所有知識庫再合併排序（或提示使用者指定） |

### 建議執行順序

```
3-1 Tool 參數擴充
 → 3-2 多 RAG 實例管理（RAGRegistry）
 → 3-3 向量庫動態切換
 → 3-5 metadata filter 跨網站
 → 3-4 Agent tool calling 設計（system prompt）
 → 3-6 fallback 跨網站搜尋
```

### RAGRegistry 設計概念

```python
class RAGRegistry:
    """依 site_id 管理多個 RAG 實例，避免重複建立向量庫。"""

    def __init__(self, config_names: dict[str, str]):
        """config_names: {"nculab": "rag_nculab", "nctu": "rag_nctu"}"""
        self._configs = config_names
        self._instances: dict[str, Rag] = {}

    def get(self, site_id: str) -> Rag:
        if site_id not in self._instances:
            config = RagConfig.from_toml(self._configs[site_id])
            self._instances[site_id] = RAGBuilder(config).build_reusable()
        return self._instances[site_id]

    def list_sites(self) -> list[str]:
        return list(self._configs.keys())

    def close(self):
        for rag in self._instances.values():
            rag.close()
```

### Tool 簽名（擴充後）

```python
webpage_retriever = StructuredTool.from_function(
    func=retrieve,
    name="webpage_retriever",
    description="從指定網站的知識庫檢索相關網頁內容",
    args_schema=WebpageRetrieverInput,  # 加入 site_id 欄位
)
```

```python
class WebpageRetrieverInput(BaseModel):
    query: str
    site_id: str  # 新增：目標網站（如 "nculab"、"nctu"）
    filter_dict: dict | None = None
    top_k: int = 10
```

---

## 6. 風險與注意事項

| # | 風險 | 影響 | 緩解措施 |
|---|------|------|---------|
| 1 | 資料目錄重構影響既有流程 | 既有 `data/webpages/` 下的資料與設定檔路徑全部失效 | 建立 migration 腳本自動搬移；保留 fallback 讀取舊路徑 |
| 2 | 多向量庫占用磁碟空間 | 每個網站的 Milvus DB 約數十 MB~數百 MB | 先以 2-3 個學校試驗，確認规模後再擴展 |
| 3 | 多 RAG 實例記憶體壓力 | 同時載入多個向量庫可能消耗大量 RAM | `RAGRegistry` 採用 LRU 快取策略，超出數量上限時釋放最久未用的實例 |
| 4 | Agent 多站路由準確度 | LLM 可能選錯 site_id 或遺漏相關網站 | 在 system prompt 提供明確的網站描述；加入 fallback 機制 |
| 5 | HTML 日期標籤格式不一致 | 不同網站的 `<meta>` 標籤格式差異大 | 建立日期解析器支援多種格式；無效時回落到內容推斷 |

---

## 7. 驗證標準

| 里程碑 | 驗證標準 |
|--------|---------|
| **M1：時間擷取** | 爬取新網站後，`results.json` 中 ≥80% 頁面有有效 `published_date`；`MarkdownDateExtractor` 在有 HTML metadata 時正確跳過 |
| **M2：多站基礎建設** | 能為 2+ 個學校網站分別爬取、建庫，目錄與向量庫完全隔離；`--site-id` 參數正常運作 |
| **M3：多站 RAG 檢索** | `webpage_retriever(site_id="nculab", query="...")` 僅從 nculab 知識庫檢索；`site_id="nctu"` 僅從 nculab 知識庫檢索；`RAGRegistry` 快取正常 |
| **M4：Agent 多站整合** | Agent 收到「中央大學的成員有哪些」自動路由至對應 site_id；收到「所有學校的論文」觸發跨站搜尋 |

---

## 8. 結論

三個目標的改造範圍涵蓋從**爬蟲底層**到**Agent 上層**的完整鏈路：

1. **M1（時間擷取）** 解決 metadata 品質問題，提升檢索精準度。
2. **M2（多站建庫）** 建立多站隔離的基礎設施，是 M3 的必要前置。
3. **M3（多站 RAG 檢索）** 核心改造，讓 RAG 工具從單站升級為多站。
4. **M4（Agent 整合）** 收斂端到端體驗，讓 LLM 自動路由至正確知識庫。

建議 **M1 與 M2 並行啟動**，預計 M1 完成後立即可提升現有檢索品質；M2 完成後再推進 M3、M4，逐步擴展至更多學校網站。
