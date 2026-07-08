# RAG Upgrade (2026/07/01)

## 待辦事項
- [x] 一、 Metadata 擴展與資料庫預篩選 (Metadata Filter)
- [ ] 二、 混合檢索與重排序 (Hybrid Search + Node Re-ranking)
- [ ] 三、 知識圖譜檢索 (Graph RAG)
- [ ] 四、 多步推理代理化 (Agentic RAG)

## 一、 Metadata 擴展與資料庫預篩選 (Metadata Filter)

**核心目標：** 從資料輸入端建立硬性邊界，消除跨類別（如把公告當作論文）與跨時空（如混淆歷年資料）的 AI 幻覺。

1. **爬蟲端屬性萃取 — URL 路徑解析**：修改 `app/modules/website_crawler.py`，在 `_extract_metadata()` 中解析 URL sub-path 決定 `page_type`（`/news`→`announcement`、`/publication`→`paper`、`/members`→`personnel`，其餘為 `general`）。日期萃取經實驗評估後放棄（Google Sites 無標準 meta，LLM 萃取成本過高、覆蓋率僅 54%）。
2. **LlamaIndex Metadata 注入**：修改 `app/modules/rag.py` 的 `_file_metadata()`，從 `results.json` 的巢狀 metadata 子物件提取 `page_type` 與 `description`，寫入 `Document` 後經 `IngestionPipeline` 自動繼承給所有 child `Node`。另新增 `MarkdownDateExtractor`（`utils/rag_helper.py`），以四層遞減策略從 Markdown 內容補償 `year`/`month`/`day`，置於 `SentenceSplitter` 之前確保 chunk 繼承。
3. **Qdrant Pre-filtering**：在 `build_retriever()` 中新增 `filter_dict: dict[str, str | int]` 參數，自動轉換為 LlamaIndex `MetadataFilters` 傳入 `VectorIndexRetriever`。所有條件採 `EQ` 比對；範圍查詢（`year >= 2024`）需直接操作底層 API，標註為已知侷限。經 20 項 pytest 驗證，Q5 論文查詢混入獎項的問題已解決。

## 二、 混合檢索與重排序 (Hybrid Search + Node Re-ranking)

**核心目標：** 在第一階段畫出的「安全範圍」內，解決特定名詞、人名或法規查無資料的召回率瓶頸，並萃取最高純度的上下文。

1. **啟用 Qdrant 雙軌混合檢索 (Hybrid Retriever)**：在初始化 `QdrantVectorStore` 時啟用 `enable_hybrid=True`。讓系統同時建立稠密向量（語意）與稀疏向量（BM25 關鍵字）索引，並透過調整 `alpha` 值來平衡兩者的搜尋權重。
2. **放寬召回與精準重排序 (Cross-Encoder Reranker)**：將 Retriever 的初步撈取量（`similarity_top_k`）大幅放寬至 15~20 筆。接著，在管線中掛載 `NodePostprocessor`，使用如 `CohereRerank` 或開源的 BGE-Reranker 針對這 20 筆資料進行交叉比對與重新計分，精準截斷保留最相關的 Top-5 筆。
3. **Prompt 生成約束與防幻覺**：覆寫 `rag_config.py` 中的 `text_qa_template`。加入嚴格溯源指令（「只能使用 Context 回答，若名單不全必須明確告知，絕不允許外推」），並要求模型在生成事實時必須附上來源連結。將此管線封裝為 `HybridQueryEngine`。

## 三、 知識圖譜檢索 (Graph RAG)

**核心目標：** 建立全局知識圖譜，專注解決跨實體的多跳推理與全域脈絡統整，並將檢索能力轉換為標準工具。

1. **建構圖譜引擎 (PropertyGraphIndex)**：利用 LlamaIndex 的知識萃取工具與 LLM，閱讀網頁純文本並自主抓取「專案」、「教授」、「技術能力」等實體與其關聯（Triplets），存入圖資料庫中。將此封裝為 `GraphQueryEngine`。
2. **跨框架工具封裝 (Tool Abstraction)**：透過 LlamaIndex 提供的橋接功能，將 `HybridQueryEngine` 與 `GraphQueryEngine` 轉換為 LangChain 認得的 `StructuredTool`。
3. **定義高精度工具說明書 (Tool Description)**：在工具的 Description 參數中嚴格寫明觸發條件。明確定義單純細節查詢使用 Hybrid 工具，跨實體邏輯或宏觀統整使用 Graph 工具，作為下一階段 Agent 決策的唯一依據。

## 四、 多步推理代理化 (Agentic RAG)

**核心目標：** 透過 LangGraph 建立具備「思考、行動、驗證、防呆」的全自動迴圈，賦予系統自主查證能力。

1. **定義全局狀態 (State Graph)**：在 LangGraph 中宣告 `AgentState`。除了問題與檢索文本外，必須加入 `retry_count`（重試次數）欄位，作為防止無限迴圈的強制終止條件。
2. **建立自主控制節點 (Nodes)**：
* **規劃與執行節點 (Planner & Action)**：由 LLM 評估問題，自動選擇呼叫混合工具（帶或不帶 Metadata 過濾）或圖譜工具，並將檢索結果寫入狀態。
* **自我驗證節點 (Self-Reflection / Grader)**：強制驗證點。由評估模型判斷抓到的資料是否足以完美回答使用者問題。
3. **編織條件控制流 (Conditional Edges)**：根據驗證結果進行路由。資料不足且未達重試上限時，導回規劃節點重新檢索；資料充足或達重試上限時，則進入最終生成節點產出解答。