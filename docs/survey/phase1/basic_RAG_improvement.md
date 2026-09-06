# 基礎 RAG 檢索優化技術

> 聚焦於**尚未套用於本專案**、且能**直接提升檢索成效**的技術，附帶專案現有基礎作為參考對照

---

## 目錄

**Part I — 專案概覽**
1. [本專案 RAG 管線現況](#1-本專案-rag-管線現況)
2. [技術基礎參考（已實作）](#2-技術基礎參考已實作)

**Part II — 尚未套用的檢索優化技術**
3. [Reranker（重排序）](#3-reranker重排序)
4. [進階 Chunking 策略](#4-進階-chunking-策略)
5. [Metadata 路由與智慧分派](#5-metadata-路由與智慧分派)
6. [Alpha 自動調優](#6-alpha-自動調優)

**Part III — 實作路線圖**
7. [實作優先順序與路線圖](#7-實作優先順序與路線圖)
8. [參考資源](#8-參考資源)
9. [術語表](#9-術語表)

---

# Part I — 專案概覽

## 1. 本專案 RAG 管線現況

### 已完成的管線

```
Website → crawl4ai → Markdown
    → IngestionPipeline (MarkdownNodeParser → SentenceSplitter → HeadingMerge → DateExtractor → ImageExtractor)
    → VectorStoreIndex (Qdrant BM25 或 Milvus BGE-M3, Dense+Sparse Hybrid)
    → VectorIndexRetriever (alpha=0.5, similarity_top_k=10)
    → RetrieverQueryEngine (Gemini/GPT 生成回答)
    → FaithfulnessEvaluator + RelevancyEvaluator
```

### 尚未導入的管線節點

```
查詢 → [混合檢索] → [❌ Reranker] → LLM 生成
               ↑
       [❌ Parent-Child Chunk / 語義 Chunking]
       [❌ Metadata 路由]
       [❌ Alpha 自動調優]
```

### 本文件的聚焦方向

以下 **4 個技術領域** 是本專案尚未實作、且能直接提升檢索品質的方向：

| # | 技術 | 預期效果 | 投入成本 |
|---|---|---|---|
| 1 | Reranker（Cross-Encoder） | 檢索精準度提升 15–30% | ⭐⭐ 低 |
| 2 | Parent-Child / 語義 Chunking | 回答引用更精準 | ⭐⭐⭐ 中 |
| 3 | Metadata 路由 | 依意圖自動過濾，減少跨類別雜訊 | ⭐⭐ 低 |
| 4 | Alpha 自動調優 | 最佳 Dense/Sparse 比例 | ⭐ 低 |

---

## 2. 技術基礎參考（已實作）

> 本節為**快速參考**，不展開實作細節。這些技術已在專案中完成，僅保留核心概念供前後文銜接。

### 2.1 現有 Chunking 管線

```
MarkdownNodeParser（按標題結構切分）
  → MarkdownDateExtractor（萃取日期 metadata）
  → SentenceSplitter（chunk_size=800, overlap=100）
  → MarkdownHeadingMergeParser（合併孤立 heading）
  → MarkdownImageExtractor（提取圖片 metadata）
```

### 2.2 現有混合檢索

| 配置 | Qdrant | Milvus |
|---|---|---|
| Dense | text-embedding-3-small (1536d) | text-embedding-3-small (1536d) |
| Sparse | BM25 (fastembed) | BGE-M3 Sparse |
| 融合 | Relative Score Fusion (預設) | WeightedRanker / RRFRanker |
| alpha | 0.5 | 0.5 |

### 2.3 現有評估

- **FaithfulnessEvaluator**：回答是否被 context 支持
- **RelevancyEvaluator**：回答是否與查詢相關

### 2.4 現有 Metadata 過濾

```python
# 支援的 filter_dict 格式
{"page_type": "paper"}
{"page_type": "paper", "year": (2024, ">=")}
{"page_type": (["paper", "announcement"], "in")}
```

Metadata 來源：`page_type`（URL 路徑解析）、`year/month/day`（MarkdownDateExtractor）、`page_url/page_title/description`（爬蟲注入）

---

# Part II — 尚未套用的檢索優化技術

## 3. Reranker（重排序）

> **投入產出比最高的改善方向**

### 3.1 為什麼需要 Reranker

```
檢索階段（Retrieval）的限制：
  - Dense Search: 用 bi-encoder 分別編碼 query 和 document，無法看到兩者的交互
  - Sparse Search: 只做關鍵詞匹配，忽略語義
  - → 召回率高（找到候選），但精準度有限（排序不一定對）

重排序階段（Reranking）的突破：
  - 用 cross-encoder 同時編碼 query + document
  - 能捕捉 query 與 document 之間的精細語義交互
  - → 在候選集合上重新排序，精準度大幅提升
```

### 3.2 Bi-Encoder vs Cross-Encoder

```
Bi-Encoder（你現有的 embedding 模型）:
  Query  ──→ Encoder ──→ Query Vector ──┐
                                        ├─→ 餘弦相似度 → Score
  Doc    ──→ Encoder ──→ Doc Vector   ──┘

  ✅ 快：document embedding 可以預計算，查詢時只編碼 query
  ❌ 不精：query 和 document 獨立編碼，無法捕捉交互

Cross-Encoder（Reranker）:
  [Query, Doc] ──→ Cross-Encoder ──→ Score

  ✅ 精：同時看到 query 和 document，捕捉精細交互
  ❌ 慢：每個 (query, doc) 對都需要重新編碼，無法預計算
```

### 3.3 Reranker 模型比較

| 模型 | 類型 | 維度 | 中文 | 速度 | 精度 | 備註 |
|---|---|---|---|---|---|---|
| **BAAI/bge-reranker-v2-m3** | Cross-Encoder | 1024 | ✅✅ | 中 | 高 | **推薦首選**，多語言 |
| **BAAI/bge-reranker-v2-gemma** | Cross-Encoder | — | ✅ | 慢 | 極高 | 基於 Gemma，精度最高 |
| **cross-encoder/ms-marco-MiniLM-L-6-v2** | Cross-Encoder | 384 | ❌ | 快 | 中高 | 英文專精，輕量 |
| **Cohere Rerank** | API | — | ✅ | 快 | 高 | SaaS，有免費額度 |
| **ColBERT v2** | Late Interaction | 128×k | ⚠️ | 快 | 中高 | 比 Cross-Encoder 快 |
| **FlashRank** | Cross-Encoder (量化) | 384 | ⚠️ | 極快 | 中 | 輕量級，適合即時 |

### 3.4 Reranker 在管線中的位置

```
混合檢索（top_k=20）
    ↓
Reranker（重新評分 + 排序）
    ↓
精選結果（top_n=5~8）
    ↓
上下文組裝 → LLM 生成回答
```

**關鍵設計決策：** `top_k`（Reranker 的輸入）vs `top_n`（Reranker 的輸出）

| 參數 | 建議範圍 | 說明 |
|---|---|---|
| `top_k`（檢索候選數） | 15–30 | 越多召回越廣，但 Reranker 越慢 |
| `top_n`（精選數） | 3–8 | 越少越精準，但可能丟失資訊 |

### 3.5 LlamaIndex 整合方式

```python
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core.query_engine import RetrieverQueryEngine

# 方式 1: 本地模型（推薦）
reranker = SentenceTransformerRerank(
    model="BAAI/bge-reranker-v2-m3",
    top_n=5,
)

# 方式 2: Cohere API
from llama_index.postprocessor.cohere_rerank import CohereRerank
reranker = CohereRerank(api_key="...", top_n=5)

# 整合到查詢引擎
query_engine = RetrieverQueryEngine(
    retriever=retriever,
    response_synthesizer=response_synthesizer,
    node_postprocessors=[reranker],
)
```

### 3.6 與本專案的整合建議

在 `rag_factory.py` 的 `RAGBuilder.build_query_engine()` 中加入 reranker：

```python
def build_query_engine(self, rag: RAG) -> None:
    # ... 現有 retriever 和 response_synthesizer 建立 ...

    node_postprocessors = []

    # 現有：Similarity cutoff
    if self.config.query_mode != "hybrid":
        node_postprocessors.append(
            SimilarityPostprocessor(similarity_cutoff=self.config.cutoff)
        )

    # 新增：Reranker（建議作為預設行為）
    if self.config.reranker_enabled:
        node_postprocessors.append(
            SentenceTransformerRerank(
                model=self.config.reranker_model,   # e.g. "BAAI/bge-reranker-v2-m3"
                top_n=self.config.reranker_top_n,    # e.g. 5
            )
        )

    rag.query_engine = RetrieverQueryEngine(
        rag.retriever,
        response_synthesizer,
        node_postprocessors=node_postprocessors,
    )
```

**注意：** 加入 Reranker 後，建議將 `similarity_top_k` 從 10 調高至 20，讓 Reranker 有更多候選可以篩選。

### 3.7 效能考量

| 面向 | Bi-Encoder（現有） | + Cross-Encoder Reranker |
|---|---|---|
| 檢索延遲 | ~50ms | +200–500ms（取決於 top_k） |
| 精準度 | 基礎 | 提升 15–30% |
| 記憶體 | embedding 模型 ~500MB | +reranker 模型 ~500MB–1GB |
| 適用場景 | 即時、大量候選 | 品質優先的問答 |

---

## 4. 進階 Chunking 策略

> 你目前的 `SentenceSplitter(chunk_size=800)` 已能勝任多數場景，以下策略可在特定需求下進一步提升品質。

### 4.1 Parent-Child Chunk 策略

#### 核心問題

```
小 chunk（256 tokens）的困境：
  ✅ 檢索精準（語義集中）
  ❌ 回答時缺乏上下文（LLM 看到的片段太碎）

大 chunk（1500 tokens）的困境：
  ✅ 回答時上下文充足
  ❌ 檢索時語義稀釋（相關資訊被不相關內容淹沒）
```

#### 解決方案

```
Parent Chunk (1500 tokens): 完整段落，用於回答生成
    ├── Child Chunk A (256 tokens): 細粒度片段，用於檢索匹配
    ├── Child Chunk B (256 tokens): ...
    └── Child Chunk C (256 tokens): ...

檢索流程：
  Query → 找到 Child Chunk B（最相關）
       → 關聯到 Parent Chunk（包含 B 的完整段落）
       → 用 Parent Chunk 生成回答
```

#### LlamaIndex 實作

```python
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import NodeRelationship, RelatedNodeInfo

class ParentChildSplitter:
    """建立 Parent-Child Chunk 關聯。"""

    def __init__(self, parent_chunk_size=1500, child_chunk_size=256):
        self.parent_parser = SentenceSplitter(
            chunk_size=parent_chunk_size,
            chunk_overlap=200,
        )
        self.child_parser = SentenceSplitter(
            chunk_size=child_chunk_size,
            chunk_overlap=50,
        )

    def build(self, documents):
        all_nodes = []
        for doc in documents:
            # 1. 建立 Parent Chunks
            parent_nodes = self.parent_parser.get_nodes_from_documents([doc])

            for parent in parent_nodes:
                # 2. 在每個 Parent 內建立 Child Chunks
                child_nodes = self.child_parser.get_nodes_from_documents([parent])

                for child in child_nodes:
                    # 3. 建立 Child → Parent 關聯
                    child.relationships[NodeRelationship.PARENT] = (
                        RelatedNodeInfo(node_id=parent.node_id)
                    )
                    all_nodes.append(child)

        return all_nodes
```

#### 檢索時的處理

```python
def retrieve_with_parent(rag, query, top_k=5):
    """用 child chunk 檢索，回傳 parent chunk 內容。"""
    child_nodes = rag.retriever.retrieve(query)

    parent_ids_seen = set()
    parent_results = []

    for child_node in child_nodes:
        parent_id = child_node.node.relationships.get(NodeRelationship.PARENT)
        if parent_id and parent_id.node_id not in parent_ids_seen:
            parent_ids_seen.add(parent_id.node_id)
            parent_node = rag.index.get_node(parent_id.node_id)
            parent_results.append({
                "content": parent_node.get_content(),
                "child_score": child_node.score,
                "url": parent_node.metadata.get("page_url", ""),
            })

    return parent_results[:top_k]
```

### 4.2 語義切分（Semantic Chunking）

#### 核心原理

```
傳統切分：按固定邊界（句子、段落、字元數）切分
  → 可能在語義中間切斷

語義切分：按「語義跳變點」切分
  → 相鄰句子的 embedding 相似度驟降時 = 新段落開始
```

#### 演算法

```
Step 1: 將文件拆成句子
Step 2: 計算每個句子的 embedding
Step 3: 計算相鄰句子的餘弦相似度
Step 4: 設定閾值（如 95th percentile）
Step 5: 相似度低於閾值的點 = 切分邊界
```

#### LlamaIndex 實作

```python
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding

semantic_splitter = SemanticSplitterNodeParser(
    buffer_size=1,                          # 比較窗口（前後各 1 句）
    breakpoint_percentile_threshold=95,    # 語義跳變閾值
    embed_model=OpenAIEmbedding(
        model="text-embedding-3-small",
    ),
)

nodes = semantic_splitter.get_nodes_from_documents(documents)
```

#### 閾值調整指南

| percentile_threshold | 效果 | chunk 平均大小 |
|---|---|---|
| 80% | 容易切分，chunks 較小 | 小 |
| 90% | 中等 | 中 |
| **95%** | **保守，保留較多上下文** | **大（推薦起點）** |
| 99% | 幾乎不切分 | 極大 |

### 4.3 Agentic Chunking（LLM 判斷切分）

用 LLM 判斷「這個句子是否應該和前面的句子放在一起？」，適用於主題切換頻繁的文件。精度最高但成本也最高。

### 4.4 策略選擇決策樹

```
你的文件是什麼類型？
├── 結構化 Markdown（標題層級明確）
│   └── 你目前的做法（MarkdownNodeParser + SentenceSplitter）已足夠
│
├── 長篇文件，主題切換少
│   └── 考慮 Parent-Child Chunk（小 chunk 檢索 + 大 chunk 回答）
│
├── 主題切換頻繁，結構模糊
│   └── 考慮語義切分（Semantic Chunking）
│
└── 最高品質需求，成本不限
    └── 考慮 Agentic Chunking（LLM 判斷）
```

---

## 5. Metadata 路由與智慧分派

> 你目前的 Metadata 過濾是**被動的**（由 Agent 傳入 filter_dict）。進階方向是**主動路由**（系統自動判斷查詢意圖並選擇檢索策略）。

### 5.1 被動過濾 vs 主動路由

```
目前做法（被動過濾）:
  用戶查詢 → Agent 判斷 → 決定 filter_dict → 檢索
  → 依賴 Agent 的意圖識別能力

進階做法（主動路由）:
  用戶查詢 → 意圖分類器 → 自動路由 → 專屬檢索策略
  → 系統層級的意圖識別，不依賴 Agent
```

### 5.2 路由器設計

```python
from enum import Enum
from dataclasses import dataclass

class QueryIntent(Enum):
    PAPER = "paper"           # 查詢論文
    PERSONNEL = "personnel"   # 查詢成員
    ANNOUNCEMENT = "announcement"  # 查詢公告
    GENERAL = "general"       # 一般查詢

@dataclass
class RoutingStrategy:
    intent: QueryIntent
    filter_dict: dict | None
    top_k: int
    alpha: float | None        # None = 使用預設
    reranker_top_n: int

ROUTING_TABLE: dict[QueryIntent, RoutingStrategy] = {
    QueryIntent.PAPER: RoutingStrategy(
        intent=QueryIntent.PAPER,
        filter_dict={"page_type": "paper"},
        top_k=20,
        alpha=0.7,           # 偏向語義（論文標題語義豐富）
        reranker_top_n=5,
    ),
    QueryIntent.PERSONNEL: RoutingStrategy(
        intent=QueryIntent.PERSONNEL,
        filter_dict={"page_type": "personnel"},
        top_k=15,
        alpha=0.3,            # 偏向關鍵詞（人名是精確匹配）
        reranker_top_n=3,
    ),
    QueryIntent.ANNOUNCEMENT: RoutingStrategy(
        intent=QueryIntent.ANNOUNCEMENT,
        filter_dict={"page_type": "announcement"},
        top_k=20,
        alpha=0.5,
        reranker_top_n=5,
    ),
    QueryIntent.GENERAL: RoutingStrategy(
        intent=QueryIntent.GENERAL,
        filter_dict=None,
        top_k=15,
        alpha=0.5,
        reranker_top_n=5,
    ),
}
```

### 5.3 意圖分類器

```python
INTENT_PROMPT = """根據以下使用者查詢，判斷查詢意圖屬於哪一個類別。

查詢: {query}

可選類別:
- paper: 查詢學術論文、研究成果
- personnel: 查詢實驗室成員、指導教授、研究人員
- announcement: 查詢公告、活動、消息
- general: 以上皆非的一般性查詢

只回傳類別名稱（paper/personnel/announcement/general），不需解釋。"""

def classify_intent(llm, query: str) -> QueryIntent:
    """用 LLM 分類查詢意圖。"""
    response = llm.complete(INTENT_PROMPT.format(query=query))
    intent_str = response.text.strip().lower()
    try:
        return QueryIntent(intent_str)
    except ValueError:
        return QueryIntent.GENERAL
```

### 5.4 時間感知路由

```python
def detect_temporal_intent(query: str) -> dict | None:
    """從查詢中偵測時間意圖。"""
    import re

    # "2024 年之後" → {"year": (2024, ">=")}
    year_range = re.search(r"(\d{4})\s*年(?:之後|以後|以來)", query)
    if year_range:
        year = int(year_range.group(1))
        return {"year": (year, ">=")}

    # "最近" → 近一年
    if "最近" in query:
        from datetime import datetime
        current_year = datetime.now().year
        return {"year": (current_year - 1, ">=")}

    return None
```

### 5.5 與 Agent 的整合

```
目前: Agent → 呼叫 webpage_retriever(filter_dict=...)
未來: Agent → 呼叫 webpage_retriever(query=...) → 內部自動路由
```

路由可以在兩層實作：
1. **工具層**：`webpage_retriever` 內部自動判斷意圖並路由
2. **Agent 層**：Agent 的 tool description 引導 LLM 傳入正確的 filter_dict

---

## 6. Alpha 自動調優

> 你目前的 `alpha=0.5` 是硬編碼的靜態值。不同查詢類型可能需要不同的 Dense/Sparse 比例。

### 6.1 為什麼需要動態 Alpha

```
"實驗室成員" → 人名是精確匹配 → alpha 應偏低（偏向 Sparse）
"自然語言處理的研究方向" → 語義豐富 → alpha 應偏高（偏向 Dense）
"2024 年的論文" → 時間 + 類型 → alpha 應居中
```

### 6.2 Alpha 調優方法

#### 方法 1: Grid Search（離線）

```python
def alpha_grid_search(eval_dataset, retriever, alphas=[0.0, 0.1, ..., 1.0]):
    """用評估資料集找最佳 alpha。"""
    results = {}
    for alpha in alphas:
        retriever.alpha = alpha
        metrics = evaluate_rag(eval_dataset, retriever)
        results[alpha] = metrics["context_recall"]  # 以 Recall 為主指標

    best_alpha = max(results, key=results.get)
    return best_alpha, results
```

#### 方法 2: 查詢感知動態 Alpha

```python
def dynamic_alpha(query: str, llm) -> float:
    """根據查詢特性動態決定 alpha。"""
    prompt = f"""Query: {query}
    Should this query use more semantic search (Dense) or keyword search (Sparse)?
    Answer with a number between 0 and 1 (0=pure keyword, 1=pure semantic)."""

    alpha = float(llm.complete(prompt).text.strip())
    return max(0.0, min(1.0, alpha))  # clamp to [0, 1]
```

#### 方法 3: 基於查詢特徵的規則

```python
def rule_based_alpha(query: str) -> float:
    """基於查詢特徵的規則式 alpha。"""
    # 含精確匹配詞（人名、專有名詞）→ 偏 Sparse
    if re.search(r"[A-Z][a-z]+\s[A-Z][a-z]+", query):  # 英文人名
        return 0.3
    if any(name in query for name in ["教授", "老師", "博士"]):
        return 0.3

    # 含語義詞（什麼、如何、為什麼）→ 偏 Dense
    if any(w in query for w in ["什麼", "如何", "為什麼", "原因"]):
        return 0.7

    # 預設平衡
    return 0.5
```

---

# Part III — 實作路線圖

## 7. 實作優先順序與路線圖

### 7.1 推薦實作順序

```
Phase A: 即時提升（1–2 週）
├── [A1] 加入 Reranker（BGE-Reranker-v2-m3）
└── [A2] Alpha Grid Search（找最佳靜態 alpha）

Phase B: 檢索品質提升（2–4 週）
├── [B1] Parent-Child Chunk（小 chunk 檢索 + 大 chunk 回答）
└── [B2] 查詢意圖路由（自動分派 page_type 過濾）

Phase C: 精細調優（4–6 週）
├── [C1] 語義切分（Semantic Chunking）
├── [C2] 動態 Alpha（查詢感知的 Dense/Sparse 比例）
└── [C3] 時間感知路由
```

### 7.2 影響評估

| Phase | 投入 | 預期精準度提升 | 風險 |
|---|---|---|---|
| A | 低 | 15–30% | 低（增量改善） |
| B | 中 | 10–20% | 中（需實驗驗證） |
| C | 中 | 5–15% | 中（調優成本） |

### 7.3 驗證每個 Phase 的方法

```
Phase A 驗證:
  1. 建立 20–30 筆 ground truth 測試集
  2. 比較加入 Reranker 前後的 Context Precision / Context Recall
  3. 測量延遲增量（Reranker 的額外開銷）
  4. Grid Search 找最佳 alpha（0.0–1.0，步長 0.1）

Phase B 驗證:
  1. 比較不同 chunk 策略的 Context Recall
  2. 統計各意圖類型的路由準確率
  3. 測試模糊查詢（< 5 詞）的改善幅度

Phase C 驗證:
  1. 比較語義切分 vs SentenceSplitter 的檢索品質
  2. 比較動態 alpha vs 靜態 alpha 的表現
  3. 統計時間過濾的觸發率與命中率
```

---

## 8. 參考資源

### 官方文件

| 資源 | 用途 |
|---|---|
| [LlamaIndex Retriever Docs](https://developers.llamaindex.ai/python/framework/optimizing/retrieval/retrievers/) | 檢索器 API |
| [LlamaIndex Qdrant Hybrid](https://developers.llamaindex.ai/python/examples/vector_stores/qdrant_hybrid/) | Qdrant 混合檢索範例 |
| [Qdrant Hybrid Search](https://qdrant.tech/documentation/hybrid-search/) | Qdrant 混合搜尋 |
| [BGE-Reranker](https://huggingface.co/BAAI/bge-reranker-v2-m3) | Reranker 模型 |
| [RAGAS](https://docs.ragas.io/) | 檢索品質評估（Context Precision / Recall） |

### 關鍵論文

| 論文 | 核心貢獻 |
|---|---|
| **RAPTOR** (Sarthi et al., 2024) | 層級化 chunk |
| **ColBERT** (Khattab & Zaharia, 2020) | Late Interaction 重排序 |
| **RAGAS** (Es et al., 2024) | 檢索品質評估指標 |

---

## 9. 術語表

| 術語 | 英文 | 說明 |
|---|---|---|
| 交叉編碼器 | Cross-Encoder | 同時處理 query + document 的模型，精度高但慢 |
| 延遲交互 | Late Interaction | ColBERT 使用的中間方案，比 Cross-Encoder 快 |
| 融合演算法 | Fusion Algorithm | 合併多路檢索結果的排序方法 |
| Parent-Child Chunk | — | 小 chunk 檢索、大 chunk 回答的策略 |
| 語義切分 | Semantic Chunking | 按語義邊界而非固定長度切分文件 |
| 意圖路由 | Intent Routing | 根據查詢意圖選擇不同檢索策略 |
| 召回率 | Recall | 相關文件被找到的比例 |
| 精準率 | Precision | 找到的文件中相關文件的比例 |
