# RAG Upgrade (2026/07/21)

## 待辦事項
- [x] 一、 Metadata 擴展與篩選 (Metadata Filter)
- [x] 二、 混合檢索 (Hybrid Search)
- [x] 三、 檢索工具封裝 (RAG Retriever Tool)
- [ ] 四、 Agent 通訊介面 (Agent Communication Interface)
- [ ] 五、 知識圖譜檢索 (Graph RAG)
- [ ] 六、 多步推理代理化 (Agentic RAG)

## 一、 Metadata 擴展與篩選 (Metadata Filter)

**核心目標：** 從資料輸入端建立硬性邊界，消除跨類別（如把公告當作論文）與跨時空（如混淆歷年資料）的 AI 幻覺。

1. **爬蟲端屬性萃取 — URL 路徑解析**：修改 `app/modules/website_crawler.py`，在 `_extract_metadata()` 中解析 URL sub-path 決定 `page_type`（`/news`→`announcement`、`/publication`→`paper`、`/members|/people|/advisor`→`personnel`，其餘為 `general`）。日期萃取經實驗評估後放棄（Google Sites 無標準 meta，LLM 萃取成本過高、覆蓋率僅 54%）。輸出結構重整為三層（`metadata`、`crawl_info`、top-level），圖片萃取拆分為獨立方法 `_extract_images`，頁面標題改為 `crawl_result.metadata.get("title")` 以提升穩定性。爬蟲全量重新執行後 `results.json` 自動更新 page_type 映射。

2. **LlamaIndex Metadata 注入**：修改 `app/modules/rag.py` 的 `_file_metadata()`，從 `results.json` 的巢狀 `metadata` 提取 `page_type` 與 `description`，寫入 `Document` 後經 `IngestionPipeline` 自動繼承給所有 child `Node`。新增 `MarkdownDateExtractor`（前置於 `SentenceSplitter`），以四層遞減策略（heading 年份 → Post date → trailing date → 內容 fallback）補償 `year`/`month`/`day`。`page_type` 保留給 LLM 閱讀（僅 1–3 tokens，對邊界案例有助益），不設 `excluded_llm_metadata_keys`。

3. **Qdrant Pre-filtering**：`build_retriever(filter_dict=...)` 將所有條件以 `EQ` 轉換為 `MetadataFilters` 傳入 `VectorIndexRetriever`，`query()` 不感知 filter 存在。後續擴充支援自訂 `FilterOperator`（tuple 寫法如 `year: (2024, FilterOperator.GTE)` 或 `page_type: (["paper", "announcement"], FilterOperator.IN)`），滿足範圍與多值查詢。經 20 項 pytest（6 類別）全數通過驗證：
   - **Q5 回歸驗證通過** — 加入 `page_type=paper` filter 後徹底隔離獎項頁面混入，Relevancy 判定 **PASSING** ✅
   - **Paper 節點向量相似度偏低**（cosine 僅 0.37–0.38），建議混合檢索階段放寬 `cutoff` 或仰賴 reranker 二次排序，而非一次性向量截斷

4. **孤立驗證與邊界測試** — 6 類別 20 項 pytest（`test/test_metadata_filter.py`）全數通過（32.84s）：

   | 測試類別 | 結果 | 核心驗證 |
   |:---------|:----:|----------|
   | `TestMetadataInjection` | ✅ 6/6 | page_type 傳播、日期萃取四策略、description 完整性 |
   | `TestFilterIsolation` | ✅ 5/5 | 四種 page_type 單一 filter、year 條件、複合條件 |
   | `TestFilterPenetration` | ✅ 2/2 | 雙向穿透，確認 filter 依 metadata 而非語義 |
   | `TestRecallCompleteness` | ✅ 2/2 | Paper 召回需 `cutoff=0.0` 避免誤殺（score 僅 0.37–0.38） |
   | `TestEdgeCases` | ✅ 2/2 | 不存在 page_type→0 筆；None filter→退化正常 |
   | `TestRegression` | ✅ 3/3 | Q5 無 leakage + 有關聯性 → **原始動機驗證通過** |

   **測試重要發現**：
   - **Q5 回歸驗證通過** — 加入 `page_type=paper` 後徹底隔離獎項頁面，Relevancy **PASSING** ✅
   - **日期萃取四層策略皆正確觸發** — heading 年份、Post date、trailing date、內容 fallback 在測試中全數驗證。注意 heading 策略最寬鬆（任何 `### 20xx` 都觸發），可考慮加入數值範圍驗證（侷限 2000–2030）
   - **Crawler URL→page_type mapping 有 gap** — `/advisor` 未列入 mapping，導致被歸為 `general`，已於後續修正

5. **後續即時修正** — 根據測試發現當日完成兩項修正：

   - **爬蟲補上 `/advisor` mapping**（`app/modules/website_crawler.py`）：`personnel` 正則從 `r"/members\|/people"` 改為 `r"/members\|/people\|/advisor"`，避免 `personnel` 召回長期缺漏 Advisor 內容
   - **`build_retriever()` 支援自訂 `FilterOperator`**（`app/modules/rag.py`）：`filter_dict` 型別擴充為 `dict[str, str \| int \| tuple]`，value 為 `tuple` 時解包為 `(value, operator)`，純值時自動使用 `FilterOperator.EQ`。範例：
     ```python
     # EQ（純值寫法，向後相容）
     rag.build_retriever(filter_dict={"page_type": "paper"})
     # GTE（tuple 寫法）
     rag.build_retriever(filter_dict={"page_type": "paper", "year": (2024, FilterOperator.GTE)})
     # IN（多值查詢）
     rag.build_retriever(filter_dict={"page_type": (["paper", "announcement"], FilterOperator.IN)})
     ```
     既有 20 項測試全部通過（33.93s），向後相容零破損

## 二、 混合檢索 (Hybrid Search)

**核心目標：** 以稠密＋稀疏雙軌檢索互補，在不依賴 cutoff 和 reranker 的前提下，解決特定關鍵字與語意模糊之間的召回缺口。

1. **Vector Store 切換：Qdrant → Milvus**：Qdrant + BM25（`Qdrant/bm25`，純英文語料）對中文 tokenization 效果有限，**改採 Milvus + BGE-M3**（`BAAI/bge-m3`，多語言神經稀疏編碼）。`build_vector_store()` 傳入 `enable_sparse=True` 與 `BGEM3SparseEmbeddingFunction()`，collection 同時儲存稠密向量與稀疏向量。

2. **融合演算法：WeightedRanker 勝出**：Milvus 支援 RRFRanker（rank-based）與 WeightedRanker（score-based）。經實驗比較，RRFRanker 分數壓縮在 0.015–0.033、sparse 干擾過大、成員覆蓋僅 7 位；**WeightedRanker 保留 cosine 原始分數**，成員覆蓋 12 位。最終鎖定 `WeightedRanker` 搭配 `weights=[1.0, 0.5]`。Hybrid mode 跳過 `SimilarityPostprocessor`，完全依賴融合分數自然排序，**省去 cutoff 調參成本**。

3. **參數實驗**：經三組實驗鎖定最終配置——
   - **權重微調**（`[1.0,0.3]` vs `[1.0,0.5]` vs `[0.9,0.3]`）：`[1.0, 0.5]` 全面勝出，Top-1 Score **0.997**、執行時間最快 **27.92s**
   - **`hybrid_top_k`**（10 vs 20 vs 30）：調高無益，最終 Top-10 sources 完全一致，維持預設 **10**
   - **Dense vs Hybrid 橫向比較**（同 Milvus、同資料、同批次）：Hybrid Score 健康分佈（0.62–1.04 vs dense 0.40–0.57），排序品質顯著優於 dense

4. **五題全面驗證**：最終鎖定 `milvus` + `WeightedRanker [1.0, 0.5]` + `similarity_top_k=10` + `hybrid_top_k=10` + `query_mode=hybrid`（不啟用 cutoff）。Q1–Q4 全數通過（Faithfulness/Relevancy 皆 100%）；**Q5 未通過**（皆 0%），原因為檢索污染（personnel 頁面 Score 0.95–0.98 淹沒 paper 頁面 0.62–0.63）與生成層 LLM hallucination（虛構 2026 年論文）。

5. **Q5 瓶頸與 Metadata Filter 共存驗證**：加入 `filter_dict={"page_type": "paper"}` 後檢索層完全解決（Top-10 100% 為論文頁面），Faithfulness 從 0% 提升至 **100%**；但 Relevancy 仍為 0%（LLM 仍使用外部知識補充 2026 年論文），**瓶頸從檢索層轉移至生成層**。

6. **Config Schema 擴充**：`app/configs/rag_config.py` 於 `[vector_store]` 區段新增 `hybrid_ranker`、`hybrid_ranker_params`，於 `[retriever]` 區段新增 `query_mode`、`similarity_top_k`、`hybrid_top_k`。向後相容：`query_mode="default"` 時退化為既有 dense-only 行為。

7. **與原始規劃的差異**：Reranker（BGE Reranker v2-m3）的原始設計（放寬 cutoff → reranker 精準過濾）已被 **Metadata Filter 隔離 + WeightedRanker 健康排序** 取代。當前瓶頸已轉移至生成層，應優先處理 prompt anti-hallucination engineering 與 Agentic RAG self-reflection，而非 reranker。詳細實驗記錄請參考 [`docs/exp/memo/rag/hybrid_query.md`](../exp/memo/rag/hybrid_query.md) 與 [`docs/exp/memo/rag/hybrid_dense_query_compare.md`](../exp/memo/rag/hybrid_dense_query_compare.md)。

## 三、 檢索工具封裝 (RAG Retriever Tool)

**核心目標：** 將當前已實作完成的 RAG 系統包裝為 Agent 可呼叫的工具（retriever 層級，不含 LLM 生成），使下游 LangChain Agent 能動態選擇檢索策略。

- **Rag 類別新增 `retrieve()` 方法**：繞過 `RetrieverQueryEngine`，直接呼叫 `VectorIndexRetriever.retrieve()` 並回傳 `list[dict]`（page_title、score、page_type、content、url），避免外部工具層依賴 LlamaIndex 型別
- **支援執行期 filter_dict 覆寫**：`retrieve()` 接受 `filter_dict` 與 `similarity_top_k` 參數，呼叫時從既有 retriever 讀取 `query_mode` / `hybrid_top_k` / `alpha` 後暫時重建 retriever，讓 Agent 可根據問題動態決定過濾條件（如 `{"page_type": "paper", "year": (2024, FilterOperator.GTE)}`）或調整召回數量
- **注意副作用**：傳入 `filter_dict` 會覆寫 `self.retriever`，影響後續不帶 filter 的呼叫（沿用上一組參數）。未來可改為每次建立臨時 retriever 解決
- **測試涵蓋**：Qdrant 5 項 + Milvus Hybrid 6 項全數通過，含基本檢索、filter 隔離、top_k 覆寫、無匹配 filter、有 filter 後接無 filter（確認副作用保留）
- **Tool Wrapper 模組**：`app/tools/rag_retriever_tool.py` 定義 `RetrieverInput`（Pydantic schema）與 `create_retriever_tool()`，將 `Rag.retrieve()` 包裝為 LangChain `StructuredTool`（name=`webpage_retriever`）。結果格式化為純文字（編號/分數/類型/URL/內容片段），預設 content 截斷 800 chars 避免撐爆 Agent context window
- **改用無截斷版本**：使用者自行修改儲存為 `app/tools/webpage_retriever.py`，移除 content 截斷、tool name 改為 `"webpage_retriever"`、factory 改名為 `create_webpage_retriever_tool()`。此版本為當前主要活躍版本
- **Rag 實例自動綁定**：透過 `object.__setattr__(tool, "rag", rag)` 繞過 Pydantic v2 欄位驗證，將 `Rag` 實例綁定為 tool 屬性。Agent 結束後由呼叫者手動 `tool.rag.close()` 釋放資源
- **`tools.py` 角色重定位**：簡化為所有工具的 re-export 集中入口，未來 Graph RAG Tool 加入時可直接從 `app.tools.tools` 統一 import
- **LangGraph 整合範例**（`create_agent`，新版推薦，非已棄用的 `create_react_agent`）：
  ```python
  from app.tools.webpage_retriever import create_webpage_retriever_tool
  tool = create_webpage_retriever_tool(config_name="milvus")
  agent = create_agent(model, [tool], system_prompt="你是實驗室網站問答助理。")
  result = agent.invoke({"messages": [("human", "實驗室 2024 年後的論文？")]})
  tool.rag.close()
  ```
- **與 Phase 5（Graph RAG）的關係**：此處包裝的是純向量混合檢索工具；Phase 5 的圖譜工具將以相同模式封裝為第二個 `StructuredTool`，Agent 透過 tool description 自主選擇。詳細實作紀錄請參考 [`2026_0721-RAG_retriever_tool.md`](./2026_0721-RAG_retriever_tool.md)

## 四、 Agent 通訊介面 (Agent Communication Interface)

**核心目標：** 定義 Agent 與外部系統之間的標準通訊協議，統一輸入輸出格式、串流模式與多輪對話機制，作為 Phase 5 自訂 StateGraph 的基礎。

- **統一通訊協定 — `messages` 列表**：整個 LangChain 生態系的標準介面，輸入與輸出皆為 `list[Message]`（`HumanMessage`、`AIMessage`、`ToolMessage`）。所有 Agent 工具（retriever、graph 等）皆遵循此協議，Agent 根據 `AIMessage.tool_calls` 決定是否呼叫工具
- **基本呼叫 `.invoke()`**：
  ```python
  response = agent.invoke({"messages": [{"role": "user", "content": "查詢論文"}]})
  for msg in response["messages"]:
      msg.pretty_print()
  ```
- **串流輸出 `.stream()`**：支援四種 `stream_mode`——`"values"`（完整狀態，適合除錯）、`"updates"`（增量變更，適合前端）、`"messages"`（僅 messages 變更，適合聊天 UI）、`"custom"`（工具內自訂資料，適合進度條/中間結果）
- **事件串流 `.stream_events()`**：逐 token 串流 LLM 生成內容，適用於即時顯示回應，`version="v3"` 為最新協議版本
- **多輪對話（需 checkpointer）**：透過 `MemorySaver` 或 `RedisSaver` 啟用對話記憶，以 `thread_id` 區分不同 session，Agent 自動累積對話歷史
  ```python
  config = {"configurable": {"thread_id": "session-001"}}
  agent.invoke({"messages": [{"role": "user", "content": "我叫小明"}]}, config=config)
  agent.invoke({"messages": [{"role": "user", "content": "我叫什麼名字？"}]}, config=config)
  ```
- **部署後遠端呼叫（LangGraph SDK）**：透過 `langgraph_sdk.get_sync_client()` 連接部署後的 Agent 服務，以 `runs.stream()` 串流結果，輸入格式與本地 `.invoke()` 完全一致
- **`create_agent` 完整參數**：`model`（字串或 `BaseChatModel`）、`tools`（`BaseTool` 列表）、`system_prompt`、`middleware`（`ToolRetryMiddleware`、`HumanInTheLoopMiddleware` 等）、`checkpointer`、`store`（長期記憶）、`context_schema`（tool 內可透過 `ToolRuntime` 存取執行期上下文）
- **版本注意**：LangGraph v1.0 已棄用 `create_react_agent`，官方遷移路徑為 `from langchain.agents import create_agent`。LangGraph 的 `create_agent` 回傳 `CompiledStateGraph`，與 `create_react_agent` 行為相容但支援更多 middleware 與狀態自訂

## 五、 知識圖譜檢索 (Graph RAG)

**核心目標：** 建立全局知識圖譜，專注解決跨實體的多跳推理與全域脈絡統整，並將檢索能力轉換為標準工具。

- **建構圖譜引擎 (PropertyGraphIndex)**：利用 LlamaIndex 的知識萃取工具與 LLM，閱讀網頁純文本並自主抓取「專案」、「教授」、「技術能力」等實體與其關聯（Triplets），存入圖資料庫中，封裝為 `GraphQueryEngine`
- **跨框架工具封裝 (Tool Abstraction)**：透過 LlamaIndex 橋接功能，將 `HybridQueryEngine` 與 `GraphQueryEngine` 轉換為 LangChain `StructuredTool`
- **定義高精度工具說明書 (Tool Description)**：在 Description 中嚴格寫明觸發條件——單純細節查詢使用 Hybrid 工具，跨實體邏輯或宏觀統整使用 Graph 工具

## 六、 多步推理代理化 (Agentic RAG)

**核心目標：** 透過 LangGraph 建立具備「思考、行動、驗證、防呆」的全自動迴圈，賦予系統自主查證能力。

- **定義全局狀態 (State Graph)**：在 LangGraph 中宣告 `AgentState`，除問題與檢索文本外，加入 `retry_count` 欄位作為無限迴圈強制終止條件
- **規劃與執行節點 (Planner & Action)**：LLM 評估問題，自動選擇呼叫混合工具（帶或不帶 Metadata 過濾）或圖譜工具，將檢索結果寫入狀態
- **自我驗證節點 (Self-Reflection / Grader)**：強制驗證點，由評估模型判斷檢索資料是否足以回答問題
- **條件控制流 (Conditional Edges)**：資料不足且未達重試上限 → 導回規劃節點；資料充足或已達上限 → 進入最終生成節點產出解答