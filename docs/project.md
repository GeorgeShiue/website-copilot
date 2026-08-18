# 專案簡介

> **針對各類網站提供統一方法建立知識庫，開發專屬特定網站的 AI 助手**

- 自動爬取網站內容，依資料類型分流處理，自動化建立知識庫工作流程。
- 支援自然語言問答，快速取得精確資訊並附上資料來源。
- 整合 AI Agent 強化意圖識別、查詢轉換與對話記憶管理，提升互動性。
- 提供嵌入式互動介面，支援前端與後端 API 串接。
- 優先測試學校入口網站，逐步擴展至企業與政府機關。

# Survey

* 競品分析
  > [docs/survey/competitors.md](survey/competitors.md)
  >
* 痛點分析
  > [docs/survey/pain_point.md](survey/pain_point.md)
  >
* 技術分析
  > [docs/survey/technology.md](survey/technology.md)
  >

# 功能開發

## Phase 1：資訊檢索 (階段性完成)

> [docs/code/phase1/phase1.md](code/phase1/phase1.md)

> **支援多資料類型、改進檢索品質**

- 簡介
  - **資料獲取** — 非同步爬取網站並將網頁轉為結構化內容，支援網域限制、路徑過濾與雜訊清洗。自動從 URL 解析頁面類型（論文、公告、成員等），為後續檢索提供分類標籤。
  - **資料前處理** — 對網頁中的圖片進行 VLM 自動摘要，支援多種模型、可自訂提示詞、自動重試與快取機制，產出含圖片說明的增強內容。
  - **向量索引與混合檢索** — 將處理後的內容建立向量索引，同時以語意比對與關鍵字比對雙軌檢索，再將兩者結果融合排序，補回單一策略的不足。
  - **Metadata 過濾** — 利用爬蟲階段賦予的分類標籤，在檢索前隔離不相關的頁面類型（如查論文時排除公告與人員頁面），減少跨類別雜訊造成的幻覺。
  - **RAG Retriever Tool** — 將檢索能力包裝為可供 Agent 直接呼叫的工具，支援動態調整過濾條件與檢索數量，讓上層應用能靈活運用。
  - **查詢引擎與評估** — 串接 LLM 生成回答，並以忠實度與相關性兩項指標進行自動化成效評估，確保回答品質。
  - **結果落盤** — 每次執行將 query 結果以結構化 JSON（`results.json`）與逐筆 Markdown（`results/query_{index}.md`）保存；RAG 建置可選擇將向量庫存至該次 run 內（`save_vector_store_to_runs`），避免實驗互相覆寫。

## Phase 2/3 MVP（完成）

> [docs/code/phase2_3_mvp/phase2_3_mvp.md](code/phase2_3_mvp/phase2_3_mvp.md)

> **RAG 工具 → Agent → 可嵌入網站的聊天介面 最小驗證**

- 簡介
  - **AI Agent** — 以 LangGraph `create_agent` 包裝 RAG 檢索工具，由 LLM 推理迴圈自行決定呼叫，回答附引用來源 URL；支援多輪記憶（`InMemorySaver` + `thread_id`）與 SSE 逐 token 串流。
  - **聊天伺服器** — FastAPI + SSE（`POST /api/chat`，事件協定 token / done / error）；agent 於 lifespan 建一次、關閉釋放；CORS 可限縮（`allowed_origins`）。
  - **嵌入表面** — iframe / script widget / Chrome Extension 三種方式共用同一後端；widget 以 shadow DOM 隔離樣式並提供 mount factory（transport 抽象），Extension 以 background 代理繞過 CSP/CORS。
  - **對話落盤** — `chats/<ts>/agent/<config>/`，每輪覆寫 `results.json` + 依 thread_id 分檔（`results_<thread_id>.json`）。

## Phase 2：AI Agent

> **加強互動性、強化記憶管理**

- 意圖識別與查詢轉換。
- 答案評分與自我修正。
- 對話記憶管理。

## Phase 3：嵌入式互動介面

> **提供多種嵌入方案**

- 聊天視窗組件開發。
- 前端狀態與後端 API 串接。
- Markdown 與來源渲染。

# 進度報告

## Phase 1：資訊檢索

* 0722

  > [docs/progress_report/2026_0722/2026_0722_discussion.md](progress_report/2026_0722/2026_0722_discussion.md)

  > [docs/progress_report/2026_0722/2026_0722_marp.md](progress_report/2026_0722/2026_0722_marp.md)

* 0629

  > [docs/progress_report/2026_0629/2026_0629_discussion.md](progress_report/2026_0629/2026_0629_discussion.md)

  > [docs/progress_report/2026_0629/2026_0629_marp.md](progress_report/2026_0629/2026_0629_marp.md)

* 0518

  > [docs/progress_report/2026_0518.md](progress_report/2026_0518.md)

## Phase 2/3 MVP
* 0812

  > [docs/progress_report/2026_0812/2026_0812_discussion.md](progress_report/2026_0812/2026_0812_discussion.md)

  > [docs/progress_report/2026_0812/2026_0812_marp.md](progress_report/2026_0812/2026_0812_marp.md)


# 未來規劃

## 網站導航

> - **痛點**：使用者面對複雜的功能選單容易迷失方向，或不願進行繁瑣的點擊與查找操作。
> - **解法**：AI 理解使用者自然語言指令後，直接控制網站介面進行頁面跳轉、資料篩選或功能切換。
> - **應用場景**：使用者說「帶我去看歷屆學長姐做的多智能代理（Multi-Agent）系統展示」，AI 直接將畫面跳轉至該專案的相關頁面，省去在選單中尋找的時間。

## 專責代理

> - **痛點**：通用型回答無法解決個人帳戶的特定問題，且重複填寫複雜表單的流程容易降低使用者操作意願。
> - **解法**：AI 整合使用者身分權限與歷史數據，自動完成表單代填，並透過生成式互動卡片讓使用者一鍵確認執行。
> - **應用場景**：使用者說「幫我預約明天的 RTX 4060 Ti 伺服器算力」，AI 可依學生帳號權限自動填入常借用的時段與設備規格，並彈出確認卡片供使用者檢查後送出。
