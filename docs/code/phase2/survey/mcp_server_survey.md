# MCP Server 與工具包裝協定

> 聚焦於**尚未套用於本專案**的工具包裝協定，說明 MCP 與其他方案的差異、對本專案未來方向的適用性，以及與 LangGraph 的整合方式

---

## 目錄

**Part I — 專案概覽**
1. [本專案工具層現況](#1-本專案工具層現況)
2. [工具包裝協定總覽](#2-工具包裝協定總覽)

**Part II — MCP 協定深入**
3. [MCP 架構與核心概念](#3-mcp-架構與核心概念)
4. [MCP 傳輸層](#4-mcp-傳輸層)
5. [MCP 的三大原語：Tools / Resources / Prompts](#5-mcp-的三大原語tools--resources--prompts)
6. [MCP Server 實作方式](#6-mcp-server-實作方式)
7. [MCP 與其他協定的比較](#7-mcp-與其他協定的比較)

**Part III — 整合與實作**
8. [MCP 與 LangGraph 整合](#8-mcp-與-langgraph-整合)
9. [對本專案的適用性分析](#9-對本專案的適用性分析)
10. [實作路線圖](#10-實作路線圖)
11. [參考資源](#11-參考資源)
12. [術語表](#12-術語表)

---

# Part I — 專案概覽

## 1. 本專案工具層現況

### 已完成的工具

```
Agent 工具層
└── webpage_retriever (StructuredTool)
    ├── Schema: RetrieverInputSchema (query, filter_dict, similarity_top_k)
    ├── 實作: _webpage_retriever_to_tool() 閉包綁定 RAG 實例
    ├── 資源綁定: tool.rag (RAG 實例，結束後 tool.rag.close() 釋放)
    └── 整合: create_agent(llm, [tool], ...)
```

### 未來規劃的工具

| 工具 | 用途 | 狀態 |
|---|---|---|
| `webpage_retriever` | 向量混合檢索 | ✅ 已完成 |
| `graph_retriever` | 知識圖譜檢索 | 📋 規劃中（Graph RAG survey） |
| `site_navigator` | 網站導航 + 頁面跳轉 | 📋 規劃中 |
| `form_filler` | 表單自動填寫 | 📋 規劃中 |
| 外部 API 工具 | 搜尋引擎、知識庫等 | 📋 規劃中 |

### 本文件的聚焦方向

| # | 技術方向 | 說明 | 投入成本 |
|---|---|---|---|
| 1 | **MCP 協定** | 開放標準、跨框架、跨語言 | ⭐⭐ 低（有官方適配器） |
| 2 | **LangChain Tools** | 現有方式，最簡單 | $0（已使用） |
| 3 | **OpenAI/Anthropic FC** | LLM 提供商格式，已由 LangChain 處理 | $0（已處理） |

---

## 2. 工具包裝協定總覽

### 協定光譜

```
簡單                                              複雜
├──────────────────────────────────────────────────┤
│ LangChain     OpenAI/Anthropic     MCP           │
│ Tools         Function Calling     Protocol      │
│                                                  │
│ 你目前在此    已由 LangChain 處理    建議未來導入   │
```

### 三大協定對照

| 面向 | LangChain Tools | OpenAI/Anthropic FC | MCP |
|---|---|---|---|
| **定義方式** | Python 函數 + Schema | JSON Schema | JSON Schema + 協定 |
| **執行** | 同進程直接呼叫 | LLM 產生參數，你的程式執行 | 獨立進程/伺服器 |
| **跨框架** | ❌ 綁定 LangChain | ❌ 綁定特定 LLM | ✅ 跨框架、跨語言 |
| **跨進程** | ❌ 同進程 | ❌ 同進程 | ✅ 支援遠端伺服器 |
| **運行時發現** | ❌ 需預先定義 | ❌ 需預先定義 | ✅ 自動查詢 Server 能力 |
| **多 Server 管理** | ❌ 手動管理 | ❌ 手動管理 | ✅ MultiServerMCPClient |
| **你的專案** | ✅ 已使用 | ✅ 已由 LangChain 處理 | 🔜 建議中期導入 |

---

# Part II — MCP 協定深入

## 3. MCP 架構與核心概念

### 什麼是 MCP

MCP（Model Context Protocol）是 Anthropic 發起的**開放標準協定**，被比喻為「AI 應用的 USB-C」——提供一個標準化的方式讓 AI 應用連接外部系統。

```
MCP 架構
┌─────────────────────────────────────────────────┐
│                  MCP Host（你的 Agent）            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │MCP Client│  │MCP Client│  │MCP Client│      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
└───────┼──────────────┼──────────────┼────────────┘
        │ stdio        │ HTTP/SSE     │ stdio
   ┌────▼─────┐  ┌────▼─────┐  ┌────▼─────┐
   │MCP Server│  │MCP Server│  │MCP Server│
   │ 檔案系統  │  │ 資料庫    │  │ 網站爬蟲  │
   └──────────┘  └──────────┘  └──────────┘
```

### 三個核心角色

| 角色 | 說明 | 你的專案對應 |
|---|---|---|
| **MCP Host** | AI 應用程式，協調管理多個 Client | `agent.py` 中的 `Agent` |
| **MCP Client** | 與特定 Server 維持連接的元件 | `MultiServerMCPClient` |
| **MCP Server** | 提供工具/資源/提示的程式 | 你的 `webpage_retriever` 可包成 Server |

### 兩個核心層

```
MCP 協定分層
┌──────────────────────────────────────┐
│           Data Layer                  │
│  JSON-RPC 2.0 通訊協定               │
│  定義 Tools / Resources / Prompts    │
│  定義 Discovery / 呼叫 / 通知         │
└──────────────────────────────────────┘
┌──────────────────────────────────────┐
│         Transport Layer              │
│  stdio / SSE / Streamable HTTP       │
│  處理連線、訊息框架、認證              │
└──────────────────────────────────────┘
```

### MCP 的狀態模型

MCP 是**無狀態協定**：每個請求都攜帶完整的協定版本和能力資訊，伺服器不依賴之前的請求狀態。這使得：
- 多實例部署變得簡單（任何實例都能處理任何請求）
- 伺服器重啟不會丟失狀態

---

## 4. MCP 傳輸層

### 四種傳輸方式

| 傳輸 | 說明 | 延遲 | 適用場景 |
|---|---|---|---|
| **stdio** | 標準輸入/輸出，本地子行程 | 極低 | 開發/測試/本地工具 |
| **SSE** | HTTP 長輪詢 | 低 | 舊版遠端連接 |
| **Streamable HTTP** | HTTP POST + SSE 串流 | 低 | 生產環境遠端伺服器 |
| **WebSocket** | 雙向持久連接 | 極低 | 即時雙向通訊 |

### 傳輸選擇決策

```
你的部署場景是什麼？
├── 本地開發/測試
│   └── stdio（最簡單，零網路開銷）
│
├── 單機部署（Agent + Server 同機器）
│   └── stdio 或 Streamable HTTP
│
├── 分散式部署（Agent + Server 不同機器）
│   └── Streamable HTTP（生產推薦）
│
└── 即時雙向通訊需求
    └── WebSocket
```

### 認證機制

Streamable HTTP 和 SSE 傳輸支援：
- **Bearer Token**：OAuth 2.0 取得的 token
- **API Key**：自訂 header
- **自訂 Header**：任何 HTTP header

```python
# 在 MultiServerMCPClient 中傳入認證 header
client = MultiServerMCPClient({
    "remote_api": {
        "url": "https://api.example.com/mcp",
        "transport": "http",
        "headers": {
            "Authorization": "Bearer ${MCP_API_TOKEN}",
        },
    },
})
```

---

## 5. MCP 的三大原語：Tools / Resources / Prompts

### Tools（工具）

LLM 可以呼叫的可執行函數，是 MCP 最常用的原語。

```python
# MCP Server 定義 Tool
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("WebpageRetriever")

@mcp.tool()
def retrieve(
    query: str,
    filter_dict: dict | None = None,
    similarity_top_k: int | None = None,
) -> str:
    """檢索網站網頁中與查詢相關的內容。

    Args:
        query: 搜尋查詢字串
        filter_dict: 可選的 metadata 過濾條件
        similarity_top_k: 回傳的 top-k 數量
    """
    results = rag.retrieve(query=query, filter_dict=filter_dict, similarity_top_k=similarity_top_k)
    return _format_retrieval_results(results)
```

**Tool 的 JSON Schema 自動從 Python 函數產生**：FastMCP 的 `@mcp.tool()` 裝飾器會自動解析函數簽名和 docstring，生成 MCP 所需的 `inputSchema`。

### Resources（資源）

提供上下文資料給 AI 應用，類似唯讀的資料來源。

```python
@mcp.resource("rag://documents/{doc_id}")
def get_document(doc_id: str) -> str:
    """提供特定文件的完整內容。"""
    return load_document(doc_id)
```

### Prompts（互動模板）

可重用的提示模板，幫助結構化互動。

```python
@mcp.prompt()
def research_assistant(domain: str) -> str:
    """建立研究助理的系統提示。"""
    return f"你是 {domain} 領域的研究助理，專注於提供準確的學術資訊。"
```

### 三者的差異

| 原語 | 誰呼叫 | 用途 | 類比 |
|---|---|---|---|
| **Tools** | LLM（自動決定） | 執行動作 | API endpoint |
| **Resources** | 使用者/應用 | 提供資料 | GET endpoint |
| **Prompts** | 使用者/應用 | 定義行為 | 模板 |

---

## 6. MCP Server 實作方式

### FastMCP（推薦）

```python
# server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("WebsiteCopilot")

@mcp.tool()
def webpage_retriever(
    query: str,
    filter_dict: dict | None = None,
    similarity_top_k: int | None = None,
) -> str:
    """檢索網站網頁中與查詢相關的內容。

    Args:
        query: 搜尋查詢字串
        filter_dict: 可選的 metadata 過濾條件
        similarity_top_k: 回傳的 top-k 數量
    """
    # 內部使用你的 RAG 實例
    results = rag.retrieve(
        query=query,
        filter_dict=filter_dict,
        similarity_top_k=similarity_top_k,
    )
    return _format_retrieval_results(results)

if __name__ == "__main__":
    mcp.run(transport="stdio")  # 本地開發
    # mcp.run(transport="http", port=8001)  # 遠端部署
```

### MCP Server 的目錄結構

```
mcp_servers/
├── webpage_retriever/
│   ├── server.py          # MCP Server 主程式
│   ├── rag_config.py      # RAG 設定
│   └── requirements.txt   # 依賴
├── site_navigator/
│   ├── server.py          # 未來：網站導航 Server
│   └── ...
└── form_filler/
    ├── server.py          # 未來：表單填寫 Server
    └── ...
```

### Discovery 機制

MCP Client 啟動時會自動查詢 Server 的能力：

```python
# Client 端的 Discovery 過程（自動發生）
# 1. Client 發送 server/discover 請求
# 2. Server 回傳支援的版本和能力
# 3. Client 發送 tools/list 取得所有工具
# 4. Client 將工具轉為 LangChain tools

client = MultiServerMCPClient({
    "retriever": {
        "command": "python",
        "args": ["mcp_servers/webpage_retriever/server.py"],
        "transport": "stdio",
    },
})

# 自動 Discovery + 取得工具
tools = await client.get_tools()
# → tools 包含 webpage_retriever tool（已轉為 LangChain StructuredTool）
```

---

## 7. MCP 與其他協定的比較

### MCP vs LangChain Tools

| 面向 | LangChain Tools（現有） | MCP |
|---|---|---|
| **工具生命週期** | 隨 Agent 啟動建立，關閉釋放 | 獨立進程，可獨立部署 |
| **資源隔離** | 同進程（tool.rag 綁定） | 跨進程（Server 獨立管理資源） |
| **新增工具** | 需改 Agent 程式碼 | Server 端新增，Client 自動發現 |
| **跨語言** | ❌ Python 專用 | ✅ 任何語言的 MCP SDK |
| **多 Agent 共享** | ❌ 每個 Agent 需各自建立 | ✅ 多個 Host 共用同一 Server |
| **效能** | 極快（同進程） | 有 IPC/網路開銷 |
| **複雜度** | 極低 | 中等 |

### MCP vs OpenAI Function Calling

| 面向 | OpenAI/Anthropic FC | MCP |
|---|---|---|
| **本質** | LLM API 特性 | 獨立協定 |
| **工具定義** | JSON Schema（各家格式不同） | JSON Schema（統一格式） |
| **執行位置** | 你的程式碼攔截並執行 | Server 端執行 |
| **發現機制** | ❌ 需預先定義 | ✅ 運行時自動查詢 |
| **生態系** | 綁定特定 LLM 提供商 | 跨 LLM、跨框架 |

### MCP vs OpenAPI/Swagger

| 面向 | OpenAPI | MCP |
|---|---|---|
| **用途** | REST API 文件 | AI 應用的工具協定 |
| **目標使用者** | 程式碼 | LLM Agent |
| **發現** | Swagger 文件 | 運行時 Discovery |
| **工具描述** | API 端點 | LLM 可理解的自然語言描述 |

---

# Part III — 整合與實作

## 8. MCP 與 LangGraph 整合

### 整合架構

```
┌─────────────────────────────────────────────────┐
│                  LangGraph Agent                  │
│  ┌─────────────────────────────────────────────┐ │
│  │          StateGraph                          │ │
│  │  ┌───────────┐  ┌──────────────────────┐   │ │
│  │  │   model   │──│   ToolNode           │   │ │
│  │  │ (Gemini)  │◄─│ (LangChain tools)    │   │ │
│  │  └───────────┘  └──────────┬───────────┘   │ │
│  └────────────────────────────┼───────────────┘ │
│                                │                  │
│  ┌────────────────────────────▼───────────────┐ │
│  │  MultiServerMCPClient                      │ │
│  │  MCP tools ──→ LangChain tools 轉換        │ │
│  └──┬─────────────┬─────────────┬────────────┘ │
│     │             │             │               │
│  stdio         HTTP          stdio              │
└─────┼─────────────┼─────────────┼───────────────┘
      │             │             │
┌─────▼─────┐ ┌────▼──────┐ ┌────▼─────┐
│Retriever  │ │Navigator  │ │FormFiller│
│Server     │ │Server     │ │Server    │
└───────────┘ └───────────┘ └──────────┘
```

### langchain-mcp-adapters

LangChain 官方提供 `langchain-mcp-adapters` 套件（Benchmark Score: 89.24），核心功能：

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

# 1. 定義多個 MCP Server 連接
client = MultiServerMCPClient({
    "retriever": {
        "command": "python",
        "args": ["mcp_servers/webpage_retriever/server.py"],
        "transport": "stdio",
    },
    "navigator": {
        "url": "http://localhost:8001/mcp",
        "transport": "http",
    },
})

# 2. 取得所有 MCP tools（自動轉為 LangChain tools）
tools = await client.get_tools()

# 3. 建立 Agent（與現有 create_agent 用法完全相同）
agent = create_react_agent(
    "google:gemini-3.1-flash-lite",
    tools=tools,
    checkpointer=checkpointer,
)

# 4. 使用（完全不變）
response = await agent.ainvoke({
    "messages": [("user", "查詢 NCULab 的論文")],
})
```

### 關鍵轉換

`MultiServerMCPClient.get_tools()` 回傳 `list[BaseTool]`（LangChain tools），所以 LangGraph 的 `create_agent` / `ToolNode` **完全不需要改**。

### 支援的功能

| 功能 | 說明 |
|---|---|
| **Multi-Server** | 同時連接多個 MCP Server |
| **Tool Name Prefix** | 可加前綴避免工具名衝突 |
| **Tool Interceptors** | 中間件模式（快取、重試、限流） |
| **Error Handling** | 區分工具執行錯誤 vs 協定錯誤 |
| **Callbacks** | 日誌、監控回呼 |
| **Runtime Headers** | 認證 token 動態注入 |

---

## 9. 對本專案的適用性分析

### 未來路線圖回顧

| 未來功能 | 需要的能力 | MCP 的價值 |
|---|---|---|
| **意圖識別 + 查詢轉換** | 自訂路由、多節點圖 | ⚠️ 不直接相關（StateGraph 問題） |
| **專責代理（多工具）** | 多工具統一管理 | ✅ MultiServerMCPClient |
| **網站導航** | Playwright 操控 | ✅ 獨立 Server 隔離 |
| **表單填寫** | OAuth + DOM 操控 | ✅ 獨立 Server + 認證 |
| **多站點 RAG** | 多個 RAG 資源隔離 | ✅ 每個站點一個 Server |
| **多 Agent 分工** | 工具在 Agent 間共享 | ✅ Server 共享 |

### 適用性評估

| 階段 | 工具數量 | MCP 適用性 | 建議 |
|---|---|---|---|
| **現階段（MVP）** | 1 個 | ❌ 過度設計 | 繼續用 StructuredTool |
| **近期（多工具）** | 2–3 個 | ⚠️ 可選 | 評估是否需要跨進程 |
| **中期（專責代理）** | 3+ 個 | ✅ 強烈建議 | 導入 MCP |
| **長期（多 Agent）** | 多組工具 | ✅ 必要 | 全面 MCP |

### 具體建議

**現階段不導入的理由**：
1. 只有 1 個工具，MCP 的多 Server 管理無用武之地
2. 單機部署，不需要跨進程通訊
3. `create_agent` 原生支援 StructuredTool，零改動

**中期導入的觸發條件**：
1. 工具數量 ≥ 3（retriever + navigator + form_filler）
2. 需要跨進程/跨語言共享工具
3. 需要多 Agent 共用同一工具 Server
4. 需要運行時動態發現新工具

### 務實的導入路徑

```
Phase 1（現在）: StructuredTool 直接整合
    └── 你已有：webpage_retriever
    └── 未來新增：navigator、form_filler（都用 StructuredTool）

Phase 2（中期）: 核心工具保持 StructuredTool，外部服務用 MCP
    └── retriever: 繼續 StructuredTool（效能最佳）
    └── 外部 API（如搜尋引擎）: 用 MCP Server 包裝
    └── langchain-mcp-adapters 轉換後一起傳入 create_agent

Phase 3（遠期）: 全面 MCP
    └── 所有工具都包成 MCP Server
    └── 支援多 Agent 分工
    └── 工具可在團隊/專案間共享
```

---

## 10. 實作路線圖

### 10.1 推薦實作順序

```
Phase A: 評估與原型（1–2 週）
├── [A1] 用 FastMCP 將 webpage_retriever 包成 MCP Server（原型）
├── [A2] 用 MultiServerMCPClient 連接並驗證工具可用
└── [A3] 比較 StructuredTool vs MCP 的效能差異

Phase B: 多工具 MCP Server（2–3 週）
├── [B1] 將 webpage_retriever 正式包裝為 MCP Server
├── [B2] 建立 graph_retriever MCP Server（Graph RAG survey 完成後）
└── [B3] 建立 site_navigator MCP Server（Playwright 操控）

Phase C: Agent 整合（2–3 週）
├── [C1] 用 langchain-mcp-adapters 整合所有 MCP tools
├── [C2] 驗證 Agent 能自主選擇正確的工具
└── [C3] 效能基準測試（延遲、吞吐量）

Phase D: 生產部署（長期）
├── [D1] MCP Server 遠端部署（Streamable HTTP）
├── [D2] 認證機制（OAuth / API Key）
└── [D3] 多 Agent 分工架構
```

### 10.2 效能考量

| 面向 | StructuredTool（現有） | MCP stdio | MCP HTTP |
|---|---|---|---|
| 呼叫延遲 | ~1ms | ~10–50ms | ~50–200ms |
| 資源隔離 | 同進程 | 獨立行程 | 獨立伺服器 |
| 部署複雜度 | 極低 | 低 | 中 |
| 適用場景 | 單機、低延遲 | 本地多工具 | 遠端、多實例 |

### 10.3 驗證每個 Phase 的方法

```
Phase A 驗證:
  1. 確認 MCP Server 能正常啟動並回應 tools/list
  2. 確認 MultiServerMCPClient 能取得工具並執行
  3. 比較 MCP vs StructuredTool 的端到端延遲

Phase B 驗證:
  1. 確認多個 MCP Server 能同時運作
  2. 確認工具名稱無衝突（使用 tool_name_prefix）
  3. 確認 Server 重啟後 Client 能自動重連

Phase C 驗證:
  1. 確認 Agent 能根據 tool description 選擇正確工具
  2. 測試跨 Server 的工具呼叫序列
  3. 測試錯誤處理（Server 崩潰、超時）

Phase D 驗證:
  1. 確認遠端 MCP Server 能正常連接
  2. 測試認證機制
  3. 測試多 Agent 共用同一 Server
```

---

## 11. 參考資源

### 官方文件

| 資源 | 用途 |
|---|---|
| [MCP 官方規格](https://modelcontextprotocol.io/specification/latest) | MCP 協定規格 |
| [MCP 架構文件](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture) | 架構概述 |
| [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) | Server/Client SDK |
| [LangChain MCP Adapters](https://github.com/langchain-ai/langchain-mcp-adapters) | LangGraph 整合適配器 |
| [FastMCP](https://github.com/modelcontextprotocol/python-sdk/tree/main/src/mcp/server/fastmcp) | 快速 Server 實作 |

### 關鍵論文與比較

| 資源 | 核心觀點 |
|---|---|
| [MCP vs Function Calling vs OpenAPI](https://www.marktechpost.com/2025/10/08/model-context-protocol-mcp-vs-function-calling-vs-openapi-tools-when-to-use-each) | 三種協定的使用場景比較 |
| [MCP vs Tool Calls for AI Agents](https://nango.dev/blog/mcp-vs-tool-calls-for-ai-agents) | MCP vs 自訂 tool calls 的實務比較 |
| [Mem0 vs MCP 整合](https://mem0.ai/blog/memory-layer-for-open-source-agent-frameworks) | MCP 作為記憶層的整合方式 |

### 專案相關

| 檔案 | 說明 |
|---|---|
| `src/app/agent/agent.py` | Agent 層（create_agent 整合） |
| `src/app/tools/webpage_retriever.py` | 現有工具實作 |
| `src/app/server/app.py` | SSE 伺服器（M3） |
| `docs/code/phase2_3_mvp/survey/memory_management_survey.md` | 記憶管理 survey（姊妹文件） |

---

## 12. 術語表

| 術語 | 英文 | 說明 |
|---|---|---|
| 模型上下文協定 | Model Context Protocol (MCP) | AI 應用連接外部系統的開放標準 |
| MCP Host | — | AI 應用程式（如 Claude Desktop、你的 Agent） |
| MCP Client | — | 與 Server 維持連接的元件 |
| MCP Server | — | 提供工具/資源/提示的程式 |
| FastMCP | — | MCP Server 的快速實作框架 |
| 原語 | Primitives | MCP 定義的核心能力（Tools / Resources / Prompts） |
| Discovery | — | Client 啟動時自動查詢 Server 能力的機制 |
| Transport | — | Client 和 Server 之間的通訊方式 |
| stdio | Standard I/O | 標準輸入/輸出傳輸（本地子行程） |
| Streamable HTTP | — | HTTP POST + SSE 串流（生產用遠端傳輸） |
| StructuredTool | — | LangChain 的工具包裝格式（你目前使用） |
| MultiServerMCPClient | — | 同時連接多個 MCP Server 的客戶端 |
| ToolCallInterceptor | — | MCP 工具呼叫的中間件（快取、重試、限流） |
| JSON-RPC 2.0 | — | MCP 資料層使用的 RPC 協定格式 |
