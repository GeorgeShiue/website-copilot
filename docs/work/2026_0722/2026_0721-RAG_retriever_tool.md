# RAG Retriever Tool (2026/07/21)

## 待辦事項

- [x] Phase 1: Rag 類別新增 `retrieve()` 方法
- [x] Phase 2: Tool Wrapper 模組
- [x] Phase 3: 工具工廠函數

## 概述

將當前已實作完成的 RAG 系統包裝為 Agent 可呼叫的工具，封裝範圍僅到 retriever 層級（不含 LLM 生成），使下游 Agent 可動態選擇檢索策略與 metadata 過濾條件。

### 對應升級文件

- **父文件**：[`2026_0721-RAG_Upgrade.md`](./2026_0721-RAG_Upgrade.md) §三、檢索工具封裝
- **上游文件**：[`2026_0721-RAG_Upgrade.md`](./2026_0721-RAG_Upgrade.md) §四、Agent 通訊介面（定義了本工具將遵循的 `messages` 協議）
- **下游文件**：[`2026_0721-RAG_Upgrade.md`](./2026_0721-RAG_Upgrade.md) §六、多步推理代理化（本工具為 Agentic RAG 的檢索元件）

### 修改的檔案

| 檔案 | 變更類型 | 說明 |
|------|---------|------|
| `app/modules/rag.py` | **新增方法** | 新增 `retrieve()` 方法 |
| `app/tools/rag_retriever_tool.py` | **新檔案** | Tool wrapper 模組 |
| `app/tools/webpage_retriever.py` | **新增工廠函數** | 新增 `create_webpage_retriever_tool()`，私有化底層包裝 |
| `app/tools/tools.py` | **重寫** | 簡化為 re-export 集中入口 |
| `cli.py` | **可選** | 新增 CLI 入口 |

---

## Phase 1: Rag 類別新增 `retrieve()` 方法

### 修改檔案

`app/modules/rag.py`

### 規劃

**目標**：在既有的 `Rag` 類別中新增一個純檢索方法，包裝 `VectorIndexRetriever.retrieve()` 但不呼叫 LLM 生成，使下游 Agent 工具層可直接取得結構化的檢索結果。

1. **方法定位**：新方法命名為 `retrieve()`，置於 `query()` 之後、`evaluate()` 之前，確保類別內部方法的生命週期順序（build → retrieve/query → evaluate）保持一致。
2. **回傳型別**：使用 `list[dict]` 而非 LlamaIndex 原生的 `list[NodeWithScore]`，避免工具層依賴 LlamaIndex 型別，同時天然可序列化。
3. **執行期參數覆寫**：`retrieve()` 接受可選的 `filter_dict` 與 `similarity_top_k`，當任一參數不為 `None` 時，從既有 retriever 讀取 `query_mode` / `hybrid_top_k` / `alpha` 後呼叫 `build_retriever()` 重建。此設計延續既有的 retriever 建構邏輯，不需要額外維護暫存 retriever 的生命週期。
4. ~~純函數式臨時 retriever~~ — **已評估但未採用**。若每次 `retrieve()` 都建立獨立的臨時 retriever 而不修改 `self.retriever`，可避免副作用但增加複雜度。目前 Agent 多為序列化呼叫，暫不需要。

### 進度

- **`retrieve()` 方法實作完成**（2026/7/21）— 插入 `query()` 之後、`evaluate()` 之前，簽名為 `def retrieve(self, query: str, filter_dict: dict[str, Any] | None = None, similarity_top_k: int | None = None) -> list[dict[str, Any]]`。回傳的每個 dict 包含 `page_title`、`score`、`page_type`、`content`、`url` 五個欄位。
- **無需新增 import** — 所需符號（`VectorStoreQueryMode`、`extract_sources_info`）已在 `rag.py` 頂部引入。
- **執行期參數覆寫機制**—當 `filter_dict` 或 `similarity_top_k` 不為 `None` 時，從既有 retriever 讀取 `query_mode`（hybrid/default）、`hybrid_top_k`、`alpha`，再呼叫 `build_retriever()` 用新參數重建。保留既有 retriever 的其他設定不受影響。
- **參數讀取方式**—`query_mode` 透過 `self.retriever._vector_store_query_mode` 比對 `VectorStoreQueryMode.HYBRID` 判斷；`hybrid_top_k` 與 `alpha` 使用 `getattr(fallback=10/0.5)`，確保非 hybrid mode 的 retriever 也有合理預設值。
- **Qdrant 檢索測試**—5 項案例全數通過：基本檢索回傳 10 筆（預設 top_k）、`filter_dict={"page_type": "paper"}` 全部結果符合、`similarity_top_k=3` 確實回傳 3 筆、無匹配 filter 回傳空列表、dict 欄位完整性驗證通過。
- **Milvus Hybrid Search 測試**—6 項案例全數通過：基本 hybrid 檢索正常、hybrid 模式下 filter 正確隔離、top_k 覆寫正確、無匹配 filter 回傳空列表、有 filter 後接無 filter 仍保留 hybrid mode（但確認了副作用：filter_dict 重建後會覆寫 `self.retriever`，後續不帶參數的呼叫沿用上一組設定）、hybrid 分數分佈落在 0.63–1.00 區間（WeightedRanker 合併 dense cosine 與 sparse BM25-like 分數）。

### 邊界處理

| 情境 | 行為 |
|------|------|
| `self.retriever is None` | 拋出 `RuntimeError` |
| `filter_dict=None` 且 `similarity_top_k=None` | 直接呼叫既有 retriever，不重建 |
| `filter_dict=None` 但 `similarity_top_k=20` | 重建 retriever，沿用既有 filter 行為 |
| `filter_dict={}` | 等同於 None，不重建 |
| `filter_dict={"page_type": "nonexistent"}` | 回傳空列表 `[]` |
| 節點缺少 `page_url` metadata | 該欄位回傳空字串 `""` |

### 設計決策紀錄

| 決策 | 選項 | 選擇理由 |
|------|------|---------|
| 回傳型別 | `list[dict]` vs `list[NodeWithScore]` | 避免外部工具層依賴 LlamaIndex 型別，方便序列化 |
| filter_dict 覆寫策略 | 修改 `self.retriever` vs 每次建立臨時 retriever | 簡潔且 Agent 多為序列化呼叫；未來若需純函數式可改為臨時 retriever |
| 重建時參數來源 | 從既有 retriever 讀取 vs 從 config 讀取 | 確保執行期覆寫不意外變更未指定的參數 |

### 已知限制

| 限制 | 影響 | 解決方案 / 改善方向 |
|------|------|-------------------|
| **retriever 副作用** | `retrieve()` 傳入 `filter_dict` 會覆寫 `self.retriever`，影響後續不帶 filter 的呼叫 | 改為每次建立臨時 retriever；或在呼叫前備份、呼叫後還原 |

---

## Phase 2: Tool Wrapper 模組

### 修改檔案

`app/tools/rag_retriever_tool.py`（新檔案）
`app/tools/__init__.py`（新檔案）

### 規劃

**目標**：將 `Rag.retrieve()` 包裝為 LangChain `StructuredTool`，使 Agent（如 LangChain `create_agent()`）可透過標準工具介面動態呼叫向量檢索，並讓 LLM 根據問題類型決定檢索參數（filter、top_k）。

1. **目錄結構**：新增 `app/tools/` 目錄，集中放置所有 Agent 工具。目錄內含 `__init__.py` 使其成為 Python 套件，未來 Phase 4 的 Graph RAG Tool 也將放置於此。
2. **輸入 Schema**：使用 Pydantic `BaseModel` 定義 `RetrieverInput`，包含三個欄位：`query`（必要）、`filter_dict`（可選）、`similarity_top_k`（可選）。`Field(description=...)` 的內容會直接成為 LLM 決定工具參數時的指引。
3. **結果格式化**：`format_retrieval_results()` 將 `retrieve()` 回傳的 `list[dict]` 轉為附編號的純文字，每個結果包含標題、分數、類型、URL、內容片段。內容片段限制 800 字元，防止撐爆 Agent context。
4. ~~無截斷方案~~ — **已評估但未採用**。完整內容保留可讓 LLM 取得更多細節，但對 context 有限的 Agent 模型可能造成溢出。`webpage_retriever.py` 中使用者修改的版本即使用無截斷策略，可依使用場景切換。
5. **Rag 實例綁定**：`create_retriever_tool()` 為工廠函數，接收已建好 retriever 的 `Rag` 實例，回傳 `StructuredTool`。因 `StructuredTool` 為 Pydantic v2 模型，動態綁定 `tool.rag = rag` 須使用 `object.__setattr__()` 繞過欄位驗證，讓外部可在 Agent 結束後透過 `tool.rag.close()` 釋放資源。

### 進度

- **目錄與套件初始化**（2026/7/21）— 建立 `app/tools/__init__.py`（空檔案），使目錄成為 Python 套件。相依套件 `langchain-core` 1.3.2 與 `pydantic` 2.12.5 已存在於專案中。
- **模組實作完成**（2026/7/21）— `app/tools/rag_retriever_tool.py` 包含三個元件：
  - `RetrieverInput`：Pydantic schema，三個欄位皆附 LLM 友善的 `description`
  - `format_retrieval_results()`：格式化檢索結果，內容截斷 800 chars
  - `create_retriever_tool()`：工廠函數，回傳 `StructuredTool(name="webpage_retriever")`
- **Rag 實例綁定** — 透過 `object.__setattr__(tool, "rag", rag)` 將 Rag 實例綁定為 tool 屬性，解決 Pydantic v2 禁止動態屬性的限制。
- **另存 `webpage_retriever.py` 變體**（使用者自行修改）— 內容與 `rag_retriever_tool.py` 基本相同，差異為無 content 截斷、tool name 改為 `"webpage_retriever"`。

### 測試

- **基本功能驗證**—6 項全數通過：Import 與 schema 欄位正確、空結果回傳格式化字串、content 正確截斷 800 chars、`create_retriever_tool(rag)` 回傳 `StructuredTool(name="webpage_retriever")`、`tool.rag` 屬性成功綁定、retriever 未建立時 invoke 拋出 `RuntimeError`。

- **Qdrant 整合測試**—6 項全數通過：基本 invoke 回傳 10 筆格式化結果、`filter_dict={"page_type": "paper"}` 正確隔離、`similarity_top_k=3` 確切回傳 3 筆、無匹配 filter 回傳空結果字串、連續調用無 crash、`tool.rag.close()` 資源釋放正常。

- **Milvus Hybrid Search 整合測試**—6 項全數通過：基本 hybrid 檢索回傳 10 筆（WeightedRanker scores max=1.003）、`filter_dict` 正確隔離、top_k 覆寫正確、無匹配 filter 回傳空結果、filter → 無 filter 後 hybrid mode 保留（但確認 top_k 副作用殘留）、hybrid 分數分佈 0.63–1.00（dense + sparse 合併正常現象）。

### 設計決策紀錄

| 決策 | 選擇 | 理由 |
|------|------|------|
| `StructuredTool` vs `@tool` | `StructuredTool` | 工具需攜帶狀態（`Rag` 實例），無法用 `@tool` 表達 |
| description 風格 | 自然語言段落 | LLM 讀取 description 決定工具選擇，應清晰描述用途與參數 |
| content 截斷長度 | 800 chars | 防止撐爆 Agent context；若使用長 context 模型可調大 |
| 回傳格式 | 純文字 | Agent 可直接讀取，不需額外解析；`ToolMessage.content` 即為字串 |
| Rag 實例存取方式 | `object.__setattr__` | Pydantic v2 禁止動態屬性，須繞過 `__setattr__` 以將 `rag` 綁定為 tool 屬性 |

### 已知限制

| 限制 | 影響 | 解決方案 / 改善方向 |
|------|------|-------------------|
| **content 固定截斷** | 結果 content 固定截斷 800 字元，長文件可能遺失細節 | 改為動態截斷（依 token 數），或分段回傳；或使用無截斷變體 `webpage_retriever` |

---

## Phase 3: 工具工廠函數

### 修改檔案

`app/tools/webpage_retriever.py`（新增工廠函數）
`app/tools/tools.py`（重寫為 re-export 入口）

### 規劃

**目標**：將高層的工具工廠函數移至工具定義所在的模組，使工具的包裝（wrap Rag）與建立（pipeline + wrap）都集中在同一個檔案中。`tools.py` 簡化為純 re-export 入口，讓外部可透過 `app.tools.tools.create_webpage_retriever_tool` 統一取得所有工具。

1. **搬移方向**：高層工廠函數從 `tools.py` 移至 `webpage_retriever.py`，與底層包裝函數 `_webpage_RAG_to_retriever_tool()` 並存。外部使用時可選擇從 `webpage_retriever` 直接 import，或從 `tools` 集中入口 import。
2. **私有化底層包裝**：`webpage_RAG_to_retriever_tool()` 改名為 `_webpage_RAG_to_retriever_tool()`，標記為內部函數。外部不應直接呼叫此函數，而應使用 `create_webpage_retriever_tool()` 統一取得已建好 pipeline 的工具。
3. **`tools.py` 角色重定位**：原本 `tools.py` 包含了完整的工廠實作，改為只做 re-export。當未來有其他工具模組（如 Graph RAG Tool）加入時，`tools.py` 就是它們的匯總出口。
4. **函數簽名調整**：`config_name` 預設值改為 `"milvus"`（暫時），因為測試顯示 milvus hybrid 表現優於 qdrant default。~~待 `default.toml` 更新後改回 `"default"`~~。**已於 2026/8/9 改回 `"default"`**（`default.toml` 已更新為 Milvus hybrid，行為不變）。

### 進度

**今日搬移與重構**（2026/7/21）：

- **`create_webpage_retriever_tool()` 移至 `webpage_retriever.py`** — 原先在 `tools.py` 中的 `webpage_retriever_tool()` 被移至 `webpage_retriever.py` 並改名為 `create_webpage_retriever_tool()`，與 `RetrieverInput`、`format_retrieval_results()`、`_webpage_RAG_to_retriever_tool()` 三個元件放在同一個檔案中。至此，工具 schema、格式化、包裝、工廠全部集中在 `webpage_retriever.py`。
- **`_webpage_RAG_to_retriever_tool()` 私有化** — 底層的包裝函數改名為私有，外部只需透過 `create_webpage_retriever_tool()` 取得工具。
- **`tools.py` 簡化為 re-export** — 內容從 106 行降為 4 行：`from app.tools.webpage_retriever import create_webpage_retriever_tool`，並透過 `__all__` 宣告公開 API。

**測試結果：**

| 測試案例 | 結果 |
|---------|------|
| 從 `webpage_retriever` direct import `create_webpage_retriever_tool` | ✅ |
| 從 `tools` re-export import `create_webpage_retriever_tool` | ✅ |
| 兩個 import 路徑指向同一函數（`assert direct is tools_factory`） | ✅ |
| 建立工具（direct 路徑）→ invoke 基本（10 筆） + filter/top_k（3 筆） | ✅ |
| 建立工具（re-export 路徑）→ invoke + `tool.rag.close()` 資源釋放 | ✅ |

### `rag.close()` 的生命週期

`create_webpage_retriever_tool()` 內部**不呼叫** `rag.close()`，因為 `_webpage_RAG_to_retriever_tool()` 在建立工具時已透過 `object.__setattr__(tool, "rag", rag)` 自動綁定 `Rag` 實例。正確生命週期：

```python
# 1. 建立工具（內部建立 Rag 實例，自動綁定為 tool.rag）
from app.tools.webpage_retriever import create_webpage_retriever_tool
tool = create_webpage_retriever_tool()  # config_name 預設 "default"（Milvus hybrid）

# 2. Agent 使用工具進行多次檢索
agent = create_agent(model, tools=[tool])
agent.invoke({"messages": [...]})
agent.invoke({"messages": [...]})

# 3. Agent 結束後，透過 tool.rag.close() 釋放資源
tool.rag.close()
```

---

## 驗證清單

### 單元測試建議

在 `test/` 目錄下新增 `test_rag_retriever_tool.py`，至少涵蓋以下案例：

| 測試類別 | 測試案例 | 預期結果 |
|---------|---------|---------|
| `TestRetrieveMethod` | 呼叫 `retrieve(query)` 回傳 dict 列表 | `len(results) > 0` 且 `type == list[dict]` |
| | 呼叫 `retrieve(query, filter_dict={"page_type": "paper"})` | 全部 result 的 `page_type == "paper"` |
| | 呼叫 `retrieve(query, similarity_top_k=20)` | `len(results) == 20` |
| | retriever 未建立時呼叫 | 拋出 `RuntimeError` |
| `TestFormatResults` | 空結果列表 | 回傳「未檢索到相關結果。」 |
| | 單筆結果 | 包含 page_title、score、URL、content |
| | content 超過 800 字 | 截斷至 800 字元 |
| `TestToolWrapper` | `create_retriever_tool(rag)` 回傳型別 | `StructuredTool` |
| | tool name | `"webpage_retriever"` |
| | tool 可被 invoke | `tool.func(query)` 回傳字串 |

### 整合測試建議

| 測試 | 方法 | 預期結果 |
|------|------|---------|
| `run_rag_retriever_tool()` 正常建立 | `tool = run_rag_retriever_tool(config_name="test")` | 回傳 `StructuredTool` |
| `create_agent()` 接受工具 | `agent = create_agent(model, tools=[tool])` | 不拋錯 |
| Agent invoke 正常 | `agent.invoke({"messages": [HumanMessage("...")]})` | 回傳含 `AIMessage` 的 dict |

---

## 已知限制

| 限制 | 影響 | 解決方案 / 改善方向 |
|------|------|-------------------|
| **執行緒不安全** | `Rag` 實例非執行緒安全，不支援多 Agent 平行呼叫同一個 tool | 每個 Agent 建立獨立 `Rag` 實例；或將向量儲存改用遠端服務（Milvus Cluster / Qdrant Cloud） |
| **retriever 副作用** | `retrieve()` 傳入 `filter_dict` 會覆寫 `self.retriever`，影響後續不帶 filter 的呼叫 | 改為每次建立臨時 retriever；或在呼叫前備份、呼叫後還原 |
| **content 固定截斷** | 結果 content 固定截斷 800 字元，長文件可能遺失細節 | 改為動態截斷（依 token 數），或分段回傳 |
| **LLM 無生成能力** | tool 只回傳檢索結果，不含 LLM 摘要 | 應由 Agent 的 LLM 負責摘要；若需獨立摘要能力可包裝成第二個 tool |
| **`rag.close()` 不可達** | tool 內部封裝的 `Rag` 實例無法從外部 close | 在 `create_retriever_tool()` 中將 `rag` 綁定為 tool 屬性（`tool.rag = rag`）|
