# Agent Memory Management 技術

> 聚焦於**尚未套用於本專案**的記憶管理技術，從認知科學基礎到最新研究，說明如何讓 Agent 從「無狀態問答機器」進化為「會學習、會記憶、會適應」的智慧助手

---

## 目錄

**Part I — 專案概覽**
1. [本專案記憶層現況](#1-本專案記憶層現況)
2. [為什麼需要進階記憶管理](#2-為什麼需要進階記憶管理)

**Part II — 記憶分類與研究基礎**
3. [認知科學的記憶分類](#3-認知科學的記憶分類)
4. [LLM Agent 記憶研究演進](#4-llm-agent-記憶研究演進)
5. [統一框架：Forms / Functions / Dynamics](#5-統一框架forms--functions--dynamics)

**Part III — LangGraph 內建記憶機制**
6. [Checkpointer（短期記憶）](#6-checkpointer短期記憶)
7. [Store（長期記憶）](#7-store長期記憶)
8. [Reducer 與 State 更新](#8-reducer-與-state-更新)

**Part IV — 開源記憶管理套件**
9. [LangMem：LangChain 官方記憶 SDK](#9-langmemlangchain-官方記憶-sdk)
10. [Mem0：通用記憶層](#10-mem0通用記憶層)
11. [其他開源方案](#11-其他開源方案)

**Part V — 整合與實作**
12. [與 LangGraph 的整合方式](#12-與-langgraph-的整合方式)
13. [對本專案的適用性分析](#13-對本專案的適用性分析)
14. [實作路線圖](#14-實作路線圖)
15. [參考資源](#15-參考資源)
16. [術語表](#16-術語表)

---

# Part I — 專案概覽

## 1. 本專案記憶層現況

### 已完成的記憶機制

```
Agent 記憶層
├── 短期記憶：InMemorySaver（Checkpointer）
│   ├── thread_config(thread_id) 區分 session
│   ├── graph.invoke() / graph.astream() 自動儲存 State
│   └── 相同 thread_id 保留對話歷史
│
└── 長期記憶：❌ 未實作
    ├── 使用者偏好：❌ 未記憶
    ├── 事實知識：❌ 未跨 session 保留
    └── 行為模式：❌ 未適應
```

### 現有架構的限制

| 面向 | 現狀 | 限制 |
|---|---|---|
| **持久化** | InMemorySaver | Server 重啟丟失所有對話歷史 |
| **跨 session** | ❌ | 不同 thread_id 之間無法共享記憶 |
| **使用者偏好** | ❌ | 每次對話都從零開始 |
| **事實提取** | ❌ | Agent 不會主動記住重要資訊 |
| **行為適應** | ❌ | 不會從經驗中學習改進 |

### 本文件的聚焦方向

| # | 技術方向 | 預期效果 | 投入成本 |
|---|---|---|---|
| 1 | **SqliteSaver** | 對話歷史持久化 | ⭐ 極低 |
| 2 | **LangMem 記憶工具** | Agent 主動記憶使用者偏好 | ⭐⭐ 低 |
| 3 | **LangMem 後台管理** | 自動提取事實知識 | ⭐⭐ 低 |
| 4 | **Store + 長期記憶** | 跨 session 知識共享 | ⭐⭐ 低 |
| 5 | **Prompt 優化** | 行為模式自動改進 | ⭐⭐⭐ 中 |

---

## 2. 為什麼需要進階記憶管理

### 從「問答機器」到「智慧助手」

```
目前的 Agent（無狀態問答機器）：
  用戶：「我喜歡中文回覆」
  Agent：好的，我用中文回覆你。

  （新 session）
  用戶：「查詢論文」
  Agent：Here are the papers...  ← 忘了使用者偏好中文

進階的 Agent（有記憶的智慧助手）：
  用戶：「我喜歡中文回覆」
  Agent：[manage_memory] 儲存偏好 → 好的，我用中文回覆你。

  （新 session）
  用戶：「查詢論文」
  Agent：[search_memory] 找到偏好 → 以下是相關論文...（中文回覆）
```

### 記憶管理的價值

| 面向 | 無記憶 | 有記憶 | 價值 |
|---|---|---|---|
| **使用者體驗** | 每次重來 | 越用越懂你 | 個人化 |
| **回答品質** | 通用回答 | 針對性回答 | 精準度 |
| **效率** | 重複提問 | 記住上下文 | 省時 |
| **學習能力** | 靜態 | 從經驗改進 | 持續優化 |

---

# Part II — 記憶分類與研究基礎

## 3. 認知科學的記憶分類

### Tulving 的記憶分類（1972）

現代 Agent 記憶研究的根基來自認知心理學家 **Endel Tulving** 的記憶分類：

| 記憶類型 | 定義 | 人類範例 | Agent 對應 |
|---|---|---|---|
| **Semantic Memory** | 事實與知識 | "巴黎是法國首都" | 使用者偏好、世界知識 |
| **Episodic Memory** | 個人經驗 | "上次去巴黎很开心" | 對話歷史、任務經驗 |
| **Procedural Memory** | 行為技能 | "如何騎腳踏車" | 工具使用模式、工作流程 |

### CoALA 認知架構（Sumers et al., 2023）

CoALA 將記憶分類正式化為四種類型，是目前 Agent 記憶設計的主流框架：

```
CoALA 記憶模型
┌─────────────────────────────────────────────┐
│           Working Memory（工作記憶）          │
│  Context Window — 有限、短期、當前使用        │
└──────┬──────────────┬──────────────┬────────┘
       │              │              │
┌──────▼─────┐ ┌──────▼─────┐ ┌─────▼────────┐
│  Episodic   │ │  Semantic  │ │ Procedural   │
│  Memory     │ │  Memory    │ │ Memory       │
│ (經驗)       │ │ (知識)     │ │ (技能)       │
│ 自動記錄     │ │ 背景提取   │ │ 有意識學習   │
└────────────┘ └────────────┘ └──────────────┘
```

| 記憶類型 | 寫入方式 | 讀取方式 | 實作技術 |
|---|---|---|---|
| **Working Memory** | 隱式（執行時自動） | 直接存取 | Context Window |
| **Episodic Memory** | 自動記錄（logging） | 語義搜尋 | Vector DB + Embeddings |
| **Semantic Memory** | 背景提取（extraction） | 語義搜尋 | Vector DB / KG |
| **Procedural Memory** | 有意識的學習（promotion） | 直接呼叫 | Code / Prompts / Tools |

---

## 4. LLM Agent 記憶研究演進

### 里程碑論文

```
1972: Tulving — Episodic vs Semantic Memory（認知科學基礎）
  │
1987: SOAR（Newell）— 最早的記憶分層架構
  │
2023: ────── LLM Agent 記憶研究爆發 ──────
  │   Park et al. — Generative Agents（Memory Stream + Reflection）
  │   Sumers et al. — CoALA（認知架構統一框架）
  │   Packer et al. — MemGPT（OS 架構啟發的虛擬記憶管理）
  │
2024-2025: ────── 記憶系統成熟化 ──────
  │   Zhang et al. — A Survey on Memory Mechanism
  │   Xu et al. — A-Mem（Zettelkasten 動態記憶組織）
  │   Mem0 / Zep / LangMem 等開源實作
  │
2025-2026: ────── 統一框架與基準測試 ──────
      Hu et al. — Memory in the Age of AI Agents（47 位共同作者）
      MemBench / MemoryAgentBench / MemoryArena
      Agentic Memory（RL-based 記憶管理）
```

### Generative Agents 的記憶架構（Park et al., 2023）

奠基論文，提出 **Memory Stream + Reflection + Retrieval** 架構：

```
Memory Stream（記憶流）
  ├── 每個時間步記錄觀察、行動、反思
  └── 持續累積的經驗記錄

Reflection（反思機制）
  ├── 定期綜合近期記憶
  └── 產生更高層級的語義洞察

Retrieval（檢索函數）
  ├── score = α·recency + β·relevance + γ·importance
  ├── recency: 時間衰減
  ├── relevance: 語義相似度
  └── importance: LLM 評估的重要性
```

**對 LangMem 的影響**：Reflection 機制對應 `create_memory_store_manager`（背景提取記憶）。

### MemGPT / Letta（Packer et al., 2023）

借鑒 OS 虛擬記憶的概念：

| 作業系統概念 | MemGPT 對應 | 說明 |
|---|---|---|
| Main Memory (RAM) | Context Window | 有限、快速、當前使用 |
| Disk Storage | External Storage | 無限、較慢、持久化 |
| Virtual Memory | Virtual Context | 透過 paging 產生無限記憶的錯覺 |
| Page Fault | Memory Pressure | 當 context 溢位時觸發 |

**對 LangMem 的影響**：Store API（InMemoryStore / PostgresStore）實現了類似的 External Storage 概念。

### A-Mem：Agentic Memory（Xu et al., 2025, NeurIPS）

基於 **Zettelkasten 方法**的動態記憶組織：

- 每個記憶是一個獨立的「卡片」（Note）
- 卡片之間通過**連結**形成知識網路
- 新記憶加入時自動分析並建立連結
- 記憶會隨著新資訊**演化**

**引用數**：1018+

---

## 5. 統一框架：Forms / Functions / Dynamics

**Memory in the Age of AI Agents**（Hu et al., 2025/12，47 位共同作者）提出最全面的統一分類：

### 三維度分類

```
維度一：Forms（記憶載體 — 什麼承載記憶？）
├── Token-level Memory（離散 token）
│   ├── Flat: 純文字序列
│   ├── Planar: 分區文字（如 System Prompt + History）
│   └── Hierarchical: 樹狀結構
├── Parametric Memory（模型權重）
│   ├── Internal: 訓練時編碼
│   └── External: 推理時微調（如 LoRA）
└── Latent Memory（隱藏狀態）
    ├── Generate: 生成新表示
    ├── Reuse: 重用已有表示
    └── Transform: 轉換表示

維度二：Functions（記憶功能 — 為什麼需要記憶？）
├── Factual Memory（事實知識）
│   ├── User Knowledge: 使用者資訊
│   └── Environment Knowledge: 環境知識
├── Experiential Memory（經驗知識）
│   ├── Cases: 具體案例
│   ├── Strategies: 策略
│   └── Skills: 技能
└── Working Memory（工作記憶）
    ├── Single-turn: 單輪任務
    └── Multi-turn: 多輪任務

維度三：Dynamics（記憶動態 — 記憶如何運作？）
├── Formation（形成）
│   ├── Extraction: 從對話提取
│   ├── Compression: 壓縮摘要
│   └── Generation: 生成新記憶
├── Evolution（演化）
│   ├── Consolidation: 巩固（Episodic → Semantic）
│   ├── Decay: 衰減（遺忘曲線）
│   └── Update: 更新（修正錯誤）
└── Retrieval（檢索）
    ├── Explicit: 明確搜尋
    └── Implicit: 隱式喚起
```

### 與你專案的對應

| 維度 | 你專案的實作 | 待導入 |
|---|---|---|
| Forms: Token-level | `messages` in State | Checkpointer 持久化 |
| Functions: Factual | `webpage_retriever` 檢索 | Store + Semantic Memory |
| Functions: Experiential | 未實作 | Episodic Memory |
| Functions: Working | Context Window | Checkpointer + prompt |
| Dynamics: Formation | LLM 生成回答 | `create_memory_manager` |
| Dynamics: Retrieval | `rag.retrieve()` | `create_search_memory_tool` |

---

# Part III — LangGraph 內建記憶機制

## 6. Checkpointer（短期記憶）

### 核心機制

Checkpointer 在每個 **superstep** 儲存完整 State 快照，以 `thread_id` 為 key：

```python
# 你目前的寫法
checkpointer = InMemorySaver()
graph = create_agent(llm, [tool], checkpointer=checkpointer)

config = {"configurable": {"thread_id": "user-123"}}
graph.invoke({"messages": [("human", "你好")]}, config=config)
# 同一 thread_id 繼續對話 → LLM 記得之前說過的話
```

### BaseCheckpointSaver 介面

| 方法 | 功能 |
|---|---|
| `put(config, checkpoint, metadata, new_versions)` | 儲存 checkpoint |
| `get_tuple(config)` | 讀取特定 checkpoint |
| `list(config)` | 列出 thread 的所有 checkpoint |
| `put_writes(config, writes, task_id)` | 儲存 pending writes（節點失敗時） |
| `delete_thread(config)` | 刪除整個 thread 的歷史 |
| `aput` / `aget_tuple` / `alist` | async 版本 |

### Checkpointer 選型

| Checkpointer | 儲存位置 | 持久化 | 併發 | 適用場景 |
|---|---|---|---|---|
| **InMemorySaver** | 記憶體 | ❌ 重啟丟失 | 單執行緒 | 開發/測試（你目前使用） |
| **SqliteSaver** | SQLite 檔案 | ✅ 檔案持久 | 有限 | **建議近期導入** |
| **AsyncSqliteSaver** | SQLite 檔案 | ✅ 檔案持久 | 有限 | async 單機 |
| **PostgresSaver** | PostgreSQL | ✅ DB 持久 | ✅ 高併發 | 生產環境 |
| **AsyncPostgresSaver** | PostgreSQL | ✅ DB 持久 | ✅ 高併發 | async 生產 |

### SqliteSaver 整合（最小改動）

```python
# 替換前（你目前的寫法）
from langgraph.checkpoint.memory import InMemorySaver
checkpointer = InMemorySaver()

# 替換後（只需改 2 行）
from langgraph.checkpoint.sqlite import SqliteSaver
db_path = os.path.join(run_manager.results_folder_path, "conversations.db")
checkpointer = SqliteSaver.from_conn_string(db_path)

# 使用方式完全不變
graph = create_agent(llm, [tool], checkpointer=checkpointer)
config = {"configurable": {"thread_id": "user-123"}}
response = graph.invoke({"messages": [("human", "你好")]}, config=config)
```

### Checkpoint 結構

```python
{
    "v": 4,                          # schema version
    "ts": "2026-08-24T10:00:00Z",    # 時間戳
    "id": "uuid",                    # checkpoint ID
    "channel_values": {              # 當前 State
        "messages": [...],
    },
    "channel_versions": {            # 各 channel 版本號
        "__start__": 2,
        "messages": 5,
    },
    "versions_seen": {               # 各節點已處理的版本
        "model": {"messages": 4},
        "tools": {"messages": 5},
    }
}
```

---

## 7. Store（長期記憶）

### 核心概念

Store 是 LangGraph 的**長期記憶層**，用 namespace 組織，支援向量搜尋：

```python
from langgraph.store.memory import InMemoryStore

store = InMemoryStore(
    index={
        "dims": 1536,
        "embed": "openai:text-embedding-3-small",
    }
)

# 在 Agent 中使用
graph = create_agent(
    llm, [tool],
    checkpointer=InMemorySaver(),  # 短期：thread 級別
    store=store,                    # 長期：跨 thread 共享
)
```

### Namespace 架構

```python
# Namespace 用 tuple 組織，支援動態占位符
("memories",)                                    # 全局記憶
("memories", "{user_id}")                        # 使用者級記憶
("memories", "{user_id}", "preferences")         # 使用者偏好
("chat", "{user_id}", "facts")                   # 對話事實

# 寫入
store.put(
    ("memories", "user-123", "preferences"),
    "language",
    {"value": "zh-TW", "updated_at": "2026-08-24"},
)

# 讀取
item = store.get(("memories", "user-123", "preferences"), "language")

# 向量搜尋（基於語義相似度）
results = store.search(
    ("memories", "user-123"),
    query="使用者喜歡什麼語言",
    limit=5,
)
```

### Store vs Checkpointer

| 維度 | Checkpointer | Store |
|---|---|---|
| **粒度** | 完整 State 快照 | 個別 key-value 項目 |
| **範圍** | 單 thread（session 級） | 跨 thread（使用者/全局級） |
| **查詢** | 按 thread_id + checkpoint_id | 按 namespace + key + 向量搜尋 |
| **用途** | 對話歷史、多輪上下文 | 使用者偏好、事實知識、長期記憶 |
| **自動性** | 每個 superstep 自動儲存 | 需手動或由 memory manager 寫入 |

---

## 8. Reducer 與 State 更新

### add_messages Reducer

```python
from typing import Annotated
from langgraph.graph import add_messages

class AgentState(TypedDict):
    # add_messages reducer：新舊 messages 合併（非覆蓋）
    messages: Annotated[list, add_messages]
```

**`add_messages` 的行為**：
- 新 message 根據 `id` 去重
- 如果 id 相同，更新而非重複
- 這就是多輪對話能累積 messages 的底層機制

---

# Part IV — 開源記憶管理套件

## 9. LangMem：LangChain 官方記憶 SDK

### 概覽

**LangMem** 是 LangChain 官方推出的長期記憶 SDK，專為 LangGraph Agent 設計。

```
LangMem 在 LangGraph 生態系中的位置
┌─────────────────────────────────────────────────┐
│                 LangGraph                        │
│  ┌──────────────┐  ┌──────────────────────────┐ │
│  │ Checkpointer │  │ Store（長期記憶）          │ │
│  │ （短期記憶）   │  │                          │ │
│  └──────────────┘  │  ┌────────────────────┐  │ │
│                     │  │     LangMem        │  │ │
│                     │  │  ┌──────────────┐  │  │ │
│                     │  │  │ Memory Tools │  │  │ │
│                     │  │  │ Memory Mgr   │  │  │ │
│                     │  │  │ Prompt Optim │  │  │ │
│                     │  │  └──────────────┘  │  │ │
│                     │  └────────────────────┘  │ │
│                     └──────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

**安裝**：
```bash
pip install -U langmem
# 或
uv add langmem
```

### 三種記憶類型

#### Semantic Memory（語義記憶）— 事實與知識

```python
from pydantic import BaseModel
from langmem import create_memory_manager

class Triple(BaseModel):
    """以三元組形式儲存事實"""
    subject: str
    predicate: str
    object: str
    context: str | None = None

manager = create_memory_manager(
    "anthropic:claude-3-5-sonnet-latest",
    schemas=[Triple],
    instructions="從對話中提取使用者的偏好和重要事實",
    enable_inserts=True,
    enable_deletes=True,  # 支援記憶更新
)

# 提取記憶
conversation = [
    {"role": "user", "content": "Alice 管理 ML 團隊，Bob 是團隊成員"}
]
memories = manager.invoke({"messages": conversation})
# → Triple(subject="Alice", predicate="manages", object="ML_team")
```

#### Episodic Memory（情景記憶）— 過往經驗

```python
from pydantic import BaseModel, Field

class Episode(BaseModel):
    """從 Agent 視角記錄經驗"""
    observation: str = Field(..., description="情境和背景")
    thoughts: str = Field(..., description="內部推理過程")
    action: str = Field(..., description="採取的行動")
    result: str = Field(..., description="結果和反思")

manager = create_memory_manager(
    "anthropic:claude-3-5-sonnet-latest",
    schemas=[Episode],
    instructions="提取成功的互動經驗，包含完整的推理鏈",
    enable_inserts=True,
)
```

#### Procedural Memory（程序記憶）— 行為模式

```python
from langmem import create_prompt_optimizer

optimizer = create_prompt_optimizer(
    "anthropic:claude-3-5-sonnet-latest",
    kind="metaprompt",
    config={"max_reflection_steps": 3},
)

# 用對話歷史 + feedback 優化 system prompt
trajectories = [
    (
        [
            {"role": "user", "content": "解釋 Python 繼承"},
            {"role": "assistant", "content": "以下是詳細的理論解釋..."},
            {"role": "user", "content": "我想要實作範例"},
        ],
        {"score": 0.3, "comment": "太理論化，需要更多實例"},
    ),
]

optimized_prompt = optimizer.invoke({
    "trajectories": trajectories,
    "prompt": "你是 Python 專家",
})
```

### 整合模式

#### Hot Path（熱路徑）— Agent 主動管理記憶

```python
from langmem import create_manage_memory_tool, create_search_memory_tool
from langgraph.store.memory import InMemoryStore
from langgraph.prebuilt import create_react_agent

store = InMemoryStore(
    index={"dims": 1536, "embed": "openai:text-embedding-3-small"},
)

memory_tools = [
    create_manage_memory_tool(namespace=("memories", "{user_id}")),
    create_search_memory_tool(namespace=("memories", "{user_id}")),
]

def prompt(state):
    store = get_store()
    items = store.search(("memories",), query=state["messages"][-1].content)
    memories = "\n\n".join(str(item) for item in items)
    system_msg = {"role": "system", "content": f"## Memories:\n\n{memories}"}
    return [system_msg] + state["messages"]

agent = create_react_agent(
    "google:gemini-3.1-flash-lite",
    prompt=prompt,
    tools=[webpage_retriever, *memory_tools],
    store=store,
    checkpointer=InMemorySaver(),
)
```

#### Background（背景處理）— 後台自動提取記憶

```python
from langmem import create_memory_store_manager

manager = create_memory_store_manager(
    "anthropic:claude-3-5-sonnet-latest",
    namespace=("chat", "{user_id}", "facts"),
    instructions="從對話中提取使用者的偏好和重要事實",
    enable_inserts=True,
    enable_deletes=True,
)

# 在對話結束後處理（不阻塞主流程）
await manager.ainvoke(
    {"messages": conversation_history},
    config={"configurable": {"user_id": "user-123"}},
)
```

### Prompt 優化器（三種策略）

| 策略 | 說明 | LLM 呼叫次數 | 適用場景 |
|---|---|---|---|
| `prompt_memory` | 單次 LLM 推斷更新 | 1 | 快速優化 |
| `gradient` | 多步驟：提議 → 應用 | 多次 | 迭代優化 |
| `metaprompt` | 分析對話軌跡，建議改進 | 多次 | 深度優化 |

---

## 10. Mem0：通用記憶層

### 概覽

Mem0 是獨立的記憶服務，支援多框架（LangGraph、LangChain、AutoGen、CrewAI）。

**特色**：
- 自動從對話提取事實（不需手定義 schema）
- 支援 user / session / agent 三層記憶
- 自帶 Dashboard 管理介面
- 可自架或用雲端服務

### 整合方式

```python
from mem0 import Memory

memory = Memory()

# 在 LangGraph 節點中使用
def memory_node(state):
    memories = memory.search(
        query=state["messages"][-1].content,
        user_id="user-123",
        limit=5,
    )
    memory_context = "\n".join([m["memory"] for m in memories])
    return {"memory_context": memory_context, "messages": state["messages"]}

# 儲存對話記憶
memory.add(
    messages=conversation_history,
    user_id="user-123",
    metadata={"source": "website_copilot"},
)
```

### OpenMemory（Mem0 的 MCP 版本）

Mem0 的 MCP Server 版本，可以作為 MCP Server 運行，任何 MCP Client 都能連接。適合多工具共享記憶的場景。

---

## 11. 其他開源方案

### 套件比較表

| 套件 | 記憶類型 | LangGraph 整合 | 自架 | 適用場景 |
|---|---|---|---|---|
| **LangMem** | Semantic + Episodic + Procedural | ✅ 原生 | ✅ | **LangGraph 專案首選** |
| **Mem0** | 事實提取 + 圖記憶 | ⚠️ 需適配 | ✅ | 通用記憶層 |
| **Cognee** | 圖記憶 + 向量 | ⚠️ 需適配 | ✅ | 企業級知識管理 |
| **Zep/Graphiti** | 時序知識圖譜 | ⚠️ 需適配 | ✅ | 需要時間維度追蹤 |
| **Letta**（原 MemGPT） | OS 架構記憶管理 | ⚠️ 需適配 | ✅ | 完整記憶基礎設施 |
| **LangGraph Store** | key-value + 向量搜尋 | ✅ 原生 | ✅ | 輕量長期記憶 |

### 各方案詳細說明

#### Cognee（開源自架圖記憶）

- 開源的圖記憶管線，支援知識圖譜 + 向量搜尋
- 自動建立知識圖譜
- 支援多資料來源
- 適合需要複雜知識推理的企業級應用

#### Zep / Graphiti（時序知識圖譜）

- 時序感知：記得「什麼時候」說過什麼
- 知識圖譜：entity-relation 關係
- 適合需要追蹤變化的場景（合約、政策、時間線）
- 限制：資源佔用高，即時性差

#### Letta（原 MemGPT）

- 完整的 Agent 記憶基礎設施
- OS 架構的記憶管理（paging、summarization）
- 適合需要完全控制記憶行為的場景

---

# Part V — 整合與實作

## 12. 與 LangGraph 的整合方式

### 整合架構圖

```
升級後的記憶架構
┌─────────────────────────────────────────────────┐
│                  FastAPI Server                   │
│  ┌─────────────────────────────────────────────┐ │
│  │              Agent                        │ │
│  │  ┌──────────────────────────────────────┐   │ │
│  │  │ SqliteSaver                          │   │ │
│  │  │ conversations.db (短期 + 持久化)      │   │ │
│  │  └──────────────────────────────────────┘   │ │
│  │                                             │ │
│  │  ┌──────────────────────────────────────┐   │ │
│  │  │ LangMem + Store                      │   │ │
│  │  │ (長期：使用者偏好、事實知識)            │   │ │
│  │  │  ├── create_manage_memory_tool       │   │ │
│  │  │  ├── create_search_memory_tool       │   │ │
│  │  │  └── create_memory_store_manager     │   │ │
│  │  └──────────────────────────────────────┘   │ │
│  └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

### 最小改動方案（Hot Path）

```python
# 在 agent.py 中新增約 20 行
from langmem import create_manage_memory_tool, create_search_memory_tool
from langgraph.store.memory import InMemoryStore

def create_agent(config=None, run_manager=None):
    # ... 現有邏輯 ...

    # 新增記憶工具
    memory_tools = [
        create_manage_memory_tool(namespace=("memories",)),
        create_search_memory_tool(namespace=("memories",)),
    ]

    store = InMemoryStore(index={
        "dims": 1536,
        "embed": "openai:text-embedding-3-small",
    })

    graph = create_agent(
        llm,
        [tool, *memory_tools],  # retriever + 記憶工具
        system_prompt=config.system_prompt,
        checkpointer=checkpointer,
        store=store,
    )

    return Agent(graph=graph, tool=tool, ..., store=store)
```

### 進階方案（Background + Profile）

```python
from langmem import create_memory_store_manager
from pydantic import BaseModel

class UserPreference(BaseModel):
    language: str = "zh-TW"
    response_style: str = "簡潔"
    topics_of_interest: list[str] = []

manager = create_memory_store_manager(
    config.llm_name,
    namespace=("users", "{user_id}", "preferences"),
    schemas=[UserPreference],
    enable_inserts=True,
)

def prompt_with_memory(state):
    store = get_store()
    user_id = get_config()["configurable"].get("user_id", "default")
    items = store.search(("users", user_id, "preferences"))
    prefs = items[0].value if items else {}

    system_msg = config.system_prompt
    if prefs:
        system_msg += f"\n\n使用者偏好：{prefs}"

    return [{"role": "system", "content": system_msg}] + state["messages"]
```

---

## 13. 對本專案的適用性分析

### 各技術的適用性

| 技術 | 適用性 | 改動量 | 價值 |
|---|---|---|---|
| **SqliteSaver** | ✅ 強烈建議 | 極低（1 行 import） | 對話持久化 |
| **LangMem Memory Tools** | ✅ 建議 | 低（~20 行） | Agent 主動記憶 |
| **LangMem Background Mgr** | ✅ 建議 | 低（~15 行） | 自動提取事實 |
| **Store + PostgresStore** | ⚠️ 視需求 | 中 | 跨 session 共享 |
| **LangMem Prompt Optimizer** | ⚠️ 視需求 | 中 | 行為自動優化 |
| **Mem0** | ⚠️ 過度設計 | 中→高 | 通用記憶層 |
| **Cognee / Zep** | ❌ 目前不需要 | 高 | 企業級圖記憶 |

### 導入觸發條件

| 條件 | 觸發的技術 |
|---|---|
| Server 重啟丟對話 → 用戶抱怨 | SqliteSaver |
| 使用者要求「記住我的偏好」 | LangMem Memory Tools |
| 需要跨 session 共享知識 | Store + LangMem |
| 需要 Agent 從經驗中學習 | LangMem Prompt Optimizer |
| 多使用者/多實例部署 | PostgresSaver + PostgresStore |

---

## 14. 實作路線圖

### 14.1 推薦實作順序

```
Phase A: 持久化（1 天）
├── [A1] InMemorySaver → SqliteSaver（改 2 行）
└── [A2] 驗證 server 重啟後對話歷史保留

Phase B: Agent 主動記憶（1–2 週）
├── [B1] 加入 create_manage_memory_tool + create_search_memory_tool
├── [B2] 建立 InMemoryStore + prompt 函數
├── [B3] 驗證 Agent 能記住使用者偏好
└── [B4] 驗證新 session 能讀取過往記憶

Phase C: 後台記憶管理（1–2 週）
├── [C1] 加入 create_memory_store_manager
├── [C2] 定義 UserPreference schema
├── [C3] 驗證背景提取不阻塞主對話
└── [C4] 驗證事實知識跨 session 保留

Phase D: 生產升級（長期）
├── [D1] SqliteSaver → PostgresSaver
├── [D2] InMemoryStore → PostgresStore
├── [D3] LangMem Prompt Optimizer（行為優化）
└── [D4] 評估 Mem0 / Cognee（視需求）
```

### 14.2 影響評估

| Phase | 投入 | 預期效果 | 風險 |
|---|---|---|---|
| A | 極低 | 對話歷史持久化 | 極低 |
| B | 低 | 使用者偏好跨 session 記憶 | 低 |
| C | 低 | 事實知識自動提取 | 低 |
| D | 中 | 生產級多使用者 | 中 |

### 14.3 驗證每個 Phase 的方法

```
Phase A 驗證:
  1. 啟動 server → 問答 → 重啟 server → 確認對話歷史保留
  2. 確認 thread_id 正確隔離不同對話

Phase B 驗證:
  1. 說「我喜歡中文回覆」→ 確認 manage_memory 被呼叫
  2. 新 session 問答 → 確認 search_memory 找到偏好
  3. 確認 Agent 用中文回覆

Phase C 驗證:
  1. 對話結束後確認 background manager 觸發
  2. 確認 UserPreference 被正確提取並存入 Store
  3. 新 session 確認偏好被注入 system prompt

Phase D 驗證:
  1. 確認 PostgresSaver 正常運作
  2. 確認多實例共享同一 DB
  3. 確認 Prompt Optimizer 能改善回答品質
```

---

## 15. 參考資源

### 官方文件

| 資源 | 用途 |
|---|---|
| [LangGraph Checkpointer](https://github.com/langchain-ai/langgraph/blob/main/libs/checkpoint/README.md) | Checkpointer 核心介面 |
| [LangGraph Checkpoint SQLite](https://github.com/langchain-ai/langgraph/blob/main/libs/checkpoint-sqlite/README.md) | SQLite 實作 |
| [LangGraph Checkpoint Postgres](https://github.com/langchain-ai/langgraph/blob/main/libs/checkpoint-postgres/README.md) | PostgreSQL 實作 |
| [LangMem 官方文件](https://langchain-ai.github.io/langmem) | LangMem SDK |
| [LangMem GitHub](https://github.com/langchain-ai/langmem) | 原始碼與範例 |
| [Mem0 記憶層](https://mem0.ai/blog/memory-layer-for-open-source-agent-frameworks) | Mem0 整合文件 |

### 關鍵論文

| 論文 | 年份 | 核心貢獻 |
|---|---|---|
| **Generative Agents** (Park et al.) | 2023 | Memory Stream + Reflection 機制 |
| **CoALA** (Sumers et al.) | 2023 | 認知架構統一框架 |
| **MemGPT** (Packer et al.) | 2023 | OS 架構啟發的虛擬記憶管理 |
| **A-Mem** (Xu et al.) | 2025 | Zettelkasten 動態記憶組織（NeurIPS） |
| **Memory in the Age of AI Agents** (Hu et al.) | 2025 | Forms/Functions/Dynamics 統一框架 |
| **A Survey on Memory Mechanism** (Zhang et al.) | 2024 | 記憶機制綜合調查 |

### 比較與評估

| 資源 | 核心觀點 |
|---|---|
| [Best Memory Layer 2026](https://www.stork.ai/blog/best-memory-layer-ai-agents-2026) | 五種記憶套件比較 |
| [AI Agent Memory Frameworks 2026](https://www.graphlit.com/blog/survey-of-ai-agent-memory-frameworks) | 記憶框架綜合調查 |
| [Semantic vs Episodic vs Procedural](https://mem0.ai/blog/semantic-vs-episodic-vs-procedural-memory-in-ai-agents-a-complete-comparison) | 三種記憶類型比較 |

### 專案相關

| 檔案 | 說明 |
|---|---|
| `src/app/agent/agent.py` | Agent 層（InMemorySaver 使用處） |
| `src/app/configs/agent_config.py` | Agent 設定 |
| `docs/code/phase2_3_mvp/survey/mcp_server_survey.md` | MCP Server survey（姊妹文件） |
| `docs/survey/knowledge.md` | 專案知識學習導引 |

---

## 16. 術語表

| 術語 | 英文 | 說明 |
|---|---|---|
| 短期記憶 | Short-term Memory | 當前對話的上下文（Context Window） |
| 長期記憶 | Long-term Memory | 跨 session 持久化的記憶 |
| 工作記憶 | Working Memory | 當前任務的活躍工作區 |
| 語義記憶 | Semantic Memory | 事實與知識（使用者偏好、世界知識） |
| 情景記憶 | Episodic Memory | 個人經驗（對話歷史、任務經驗） |
| 程序記憶 | Procedural Memory | 行為技能（工具使用模式、工作流程） |
| Checkpointer | — | LangGraph 的短期記憶儲存機制 |
| Store | — | LangGraph 的長期記憶儲存機制 |
| Reducer | — | State 更新的合併策略（如 add_messages） |
| Superstep | — | LangGraph 執行的基本單位（一個節點的執行） |
| Thread | — | 一組 checkpoint 的集合（= 一個對話 session） |
| Namespace | — | Store 中記憶的組織層級（如 user_id） |
| Consolidation | — | 從 Episodic → Semantic 的巩固定期 |
| Reflection | — | 綜合近期記憶產生更高層級洞察 |
| Hot Path | — | Agent 在對話中主動管理記憶 |
| Background Processing | — | 後台自動提取記憶（不阻塞主流程） |
| Zettelkasten | — | 一種知識管理方法（卡片 + 連結） |
| LangMem | — | LangChain 官方的長期記憶 SDK |
| Mem0 | — | 通用記憶層服務 |
| InMemorySaver | — | 記憶體 Checkpointer（你目前使用） |
| SqliteSaver | — | SQLite 持久化 Checkpointer（建議導入） |
