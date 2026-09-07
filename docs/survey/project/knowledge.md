# Website Copilot 專案知識學習導引

> 根據專案目標與實作方向，建議深入了解的知識領域

---

## 專案全貌

**Website Copilot** 本質上是一條「網站 → 知識庫 → AI 助手」的管線，分三階段：

| 階段 | 核心 | 狀態 |
|---|---|---|
| **Phase 1** 資訊檢索 | 爬蟲 → 圖片摘要 → 向量索引 → 混合檢索 → 查詢引擎評估 | ✅ 完成 |
| **Phase 2** AI Agent | LangGraph Agent + RAG 工具 + 多輪記憶 + SSE 串流 | ✅ MVP 完成 |
| **Phase 3** 嵌入介面 | iframe / widget / Chrome Extension | ✅ MVP 完成 |
| **未來** 網站導航 + 專責代理 | 意圖控制 + 表單代填 | 📋 規劃中 |

技術棧：`crawl4ai` + `llama-index` + `LangGraph` + `FastAPI` + `Qdrant/Milvus` + `Gemini/GPT`

---

## 建議深入了解的知識領域

### 1. 🧠 RAG 進階（最高優先）

你目前已有完整的 RAG 管線，以下主題值得深入：

| 主題 | 為什麼重要 | 建議方向 |
|---|---|---|
| **混合檢索（Hybrid Search）** | 你已用 Dense + Sparse，這是業界最佳實踐 | 研究 RRF 融合排序、Cross-Encoder Reranker |
| **Chunking 策略** | `rag_factory.py` 用 `SentenceSplitter`，chunk_size=800 | 研究 RecursiveCharacterSplitter、Semantic Chunking、Parent-Child Chunk |
| **Metadata Filter 設計** | 你有 `page_type` 分類過濾，這是減少雜訊的關鍵 | 研究多欄位過濾的最佳實踐 |
| **RAG 評估框架** | 你已有 Faithfulness + Relevancy 兩項指標 | 了解 RAGAS 框架的完整評估維度 |

### 2. 🤖 LangGraph Agent 架構

你的 Agent 層用 `langchain.agents.create_agent`，這是較簡化的 API。值得深入了解：

- **LangGraph 狀態機**：理解 `CompiledStateGraph`、條件邊、節點路由機制——未來做「意圖識別 + 查詢轉換」時，你需要自訂節點
- **Tool Calling 模式**：你的 `RetrieverInputSchema` 已有設計，未來做「專責代理」時需要更多工具
- **多輪記憶管理**：目前用 `InMemorySaver`，未來做「對話記憶管理 + 上下文壓縮」時需要更進階的方案

### 3. 🌐 Web 爬蟲與內容處理

`website_crawler.py` 用 `crawl4ai` + `Playwright`，以下方向值得深入：

- **動態內容爬取**：研究 Playwright 的 `page.wait_for_selector` 與 `networkidle` 策略
- **頁面類型辨識**：`PAGE_TYPE_PATTERIONS` 目前用 URL 正則，未來可研究基於 DOM 結構或 LLM 的分類
- **Markdown 清洗**：`markdown_cleaner.py` + `mdformat`，研究如何保留表格、程式碼區塊等結構化內容

### 4. 🔌 前端嵌入與 SSE 架構

你的 Phase 3 有三種嵌入方式：

- **SSE 事件串流**：`app.py` 的 token/done/error 協定，研究 SSE 與 WebSocket 的取捨
- **Shadow DOM 隔離**：`widget.js` 的設計模式，研究 Web Component 標準
- **Chrome Extension MV3**：`manifest.json` 的 background proxy 架構，理解 Service Worker 生命週期

### 5. 📐 系統架構與工程品質

你已有良好的分層架構（`engines/` → `workflow/` → `agent/` → `server/`），值得深化：

- **`DataManager` vs `RunManager` 的職責分離**：你已做到，這是好的設計模式
- **多站點隔離**：`site_id` 的四層路徑結構，未來做「多站點 RAG」時需研究向量庫的 namespace 隔離
- **配置管理**：你用 TOML 配置 + `config_helper.py`，可研究 Pydantic Settings 的進階用法

### 6. 🚀 未來規劃方向的前置知識

| 未來功能 | 需要前置知識 |
|---|---|
| **網站導航** | Playwright 自動化操控 + DOM 互動 + 視覺定位 |
| **專責代理** | OAuth/Session 認證整合 + 表單自動填寫 + MCP 協定 |
| **上下文壓縮** | 對話摘要演算法 + Token 經濟 + 進階 Prompt Engineering |

---

## 推薦學習路徑

```
1. RAG 評估（RAGAS）＋ Chunking 策略    ←  最快提升回答品質
2. LangGraph 狀態機進階用法              ←  為 Phase 2 的意圖識別做準備
3. 混合檢索 + Reranker                  ←  提升檢索精度
4. MCP 協定 + Tool Calling              ←  為「專責代理」做準備
5. Playwright 進階 + DOM 操控            ←  為「網站導航」做準備
6. SSE + Web Component                  ←  強化前端嵌入品質
```
