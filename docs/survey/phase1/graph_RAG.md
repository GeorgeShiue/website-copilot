# Graph RAG 檢索技術

> 聚焦於**尚未套用於本專案**、且能**補足向量 RAG 盲區**的知識圖譜技術，分為**結構圖**與**語義圖**兩大方向

---

## 目錄

**Part I — 專案概覽**
1. [本專案 RAG 管線現況](#1-本專案-rag-管線現況)
2. [為什麼需要 Graph RAG](#2-為什麼需要-graph-rag)

**Part II — 結構圖（從網站結構建圖）**
3. [結構圖的核心概念](#3-結構圖的核心概念)
4. [從爬取結果建圖](#4-從爬取結果建圖)
5. [結構圖的檢索能力](#5-結構圖的檢索能力)
6. [Microsoft GraphRAG BYOG 整合](#6-microsoft-graphrag-byog-整合)

**Part III — 語義圖（從內容建圖）**
7. [語義圖的核心概念](#7-語義圖的核心概念)
8. [LLM 實體抽取](#8-llm-實體抽取)
9. [社區偵測與摘要](#9-社區偵測與摘要)
10. [語義圖的檢索能力](#10-語義圖的檢索能力)

**Part IV — 兩圖整合與實作**
11. [結構圖 vs 語義圖對照](#11-結構圖-vs-語義圖對照)
12. [兩圖合併策略](#12-兩圖合併策略)
13. [與現有 Agent 架構的整合](#13-與現有-agent-架構的整合)
14. [實作路線圖](#14-實作路線圖)
15. [參考資源](#15-參考資源)
16. [術語表](#16-術語表)

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

### 爬蟲已收集的建圖原料

你的爬蟲已經在收集建構知識圖譜所需的結構資料：

```python
# website_crawler.py — _extract_crawl_info()
crawl_info = {
    "depth": raw_metadata.get("depth"),        # 圖的層級深度
    "parent_url": raw_metadata.get("parent_url"),  # 邊：父→子
}

# website_crawler.py — _extract_metadata()
metadata = {
    "page_type": "paper",       # 節點類型（從 URL 路徑解析）
    "description": "...",       # 節點描述
    "published_date": "...",    # 節點屬性
}

# results.json — 每個頁面的完整資訊
{
    "頁面標題": {
        "url": "https://...",           # 節點 ID
        "metadata": { ... },            # 節點屬性
        "crawl_info": { ... },          # 結構資訊
    }
}
```

### 尚未導入的管線

```
查詢 → [混合檢索] → LLM 生成        ← 現有 Vector RAG
               ↓
         [❌ 知識圖譜檢索]            ← 本文件的聚焦方向
```

### 本文件的聚焦方向

| # | 技術方向 | 建圖來源 | 建圖成本 | 檢索能力 |
|---|---|---|---|---|
| 1 | **結構圖** | URL 結構、超連結、導覽列 | **$0**（不需要 LLM） | 頁面間關係、層級瀏覽 |
| 2 | **語義圖** | Markdown 正文 | 需要 LLM 呼叫 | 實體間語義關係 |
| 3 | **兩圖合併** | 結構 + 語義 | 兩者之和 | 完整的結構 + 語義關係 |

---

## 2. 為什麼需要 Graph RAG

### Vector RAG 的盲區

```
用戶問：「張三發表了哪些論文？」

Vector RAG：
  搜尋「張三 論文」→ 返回文字相似的 chunks
  → 知道張三是教授、論文 A 做混合檢索
  → ❌ 不知道張三「發表了」論文 A
  → 因為「發表」關係不存在於任何文字中
     它存在於「張三頁面有一條連結指向論文 A 頁面」
```

### 結構圖捕捉「文字中沒有的關係」

```
你的 Markdown 內容：
  張三頁面: "張三，教授，專長NLP..."
  論文 A 頁面: "提出混合檢索方法..."

向量 RAG：找到「文字相似」的 chunk
  → 不知道兩者的結構關係

結構圖：從超連結建圖
  張三頁面 ──引用──→ 論文 A 頁面
  → ✅ 直接知道兩者的關係
```

### 語義圖捕捉「跨文件的實體關係」

```
Markdown 內容：
  "張三教授指導李四同學，李四發表了論文 A"
  "論文 A 提出基於混合檢索的方法"

語義圖：
  張三 --指導--> 李四 --發表--> 論文 A --屬於--> NLP
  → ✅ 實體間的關係鏈一目了然
```

---

# Part II — 結構圖（從網站結構建圖）

## 3. 結構圖的核心概念

### 什麼是結構圖

```
結構圖 = 從網站的 URL 結構和超連結關係建立的知識圖譜

不需要 LLM，不需要分析文字內容
純粹利用「頁面之間怎麼連接」這個事實
```

### 結構圖捕捉的三種關係

```
關係 1：導覽關係（Navigation）
  從 URL 路徑推導的父子關係
  /members/professor_zhang → 父頁面是 /members
  → 「導覽子頁面」邊

關係 2：引用關係（Reference）
  從 Markdown 內的超連結提取
  [論文 A](https://.../paper_a) → 引用了論文 A 頁面
  → 「引用」邊

關係 3：類別關係（Category）
  從 URL 路徑的結構推導
  /publication/2024/ → 屬於「論文/2024」類別
  → 「屬於」邊
```

### 結構圖 vs 純 URL 過濾

| 面向 | 純 URL 過濾（你現在做的） | 結構圖 |
|---|---|---|
| 做法 | 從 URL 正則匹配 page_type | 建立完整的節點-邊圖 |
| 資訊 | 只有「這個頁面是什麼類型」 | 有「頁面之間的完整關係網路」 |
| 查詢 | 只能過濾，不能 traversal | 可以沿著邊遍歷 |
| 例子 | `page_type=paper` | 「張三頁面的所有子頁面中，哪些是論文？」 |

---

## 4. 從爬取結果建圖

### 4.1 節點（Entities）

```
你的 results.json 中的每個頁面 = 圖的一個節點

節點屬性：
  id          — 頁面標題（去副檔名的 MD 檔名）
  title       — 頁面標題
  url         — 原始 URL
  page_type   — 頁面類型（paper / personnel / announcement / general）
  description — 頁面描述
  depth       — 在爬取樹中的深度
```

### 4.2 邊（Relationships）

```
邊 1：導覽關係（從 URL 結構）
  父頁面 URL ──導覽子頁面──→ 子頁面 URL
  weight = 1.0

邊 2：引用關係（從 Markdown 超連結）
  引用頁面 ──引用──→ 被引用頁面
  weight = 0.8（引用強度）

邊 3：類別關係（從 URL 路徑）
  子頁面 ──屬於──→ 類別頁面
  weight = 0.9
```

### 4.3 建圖程式碼思路

```python
import json
from urllib.parse import urlparse

def build_graph_from_results(results_json_path: str):
    """從 results.json 建立結構圖。"""
    with open(results_json_path) as f:
        results = json.load(f)

    entities = []
    relationships = []
    entity_id = 0
    rel_id = 0
    url_to_id = {}

    # Step 1: 每個頁面 = 一個節點
    for page_title, page_data in results.items():
        entity_id += 1
        url = page_data["url"]
        metadata = page_data.get("metadata", {})
        crawl_info = page_data.get("crawl_info", {})

        entities.append({
            "id": entity_id,
            "title": page_title,
            "description": metadata.get("description", ""),
            "page_type": metadata.get("page_type", "general"),
            "url": url,
            "depth": crawl_info.get("depth", 0),
            "text_unit_ids": [],  # 之後對應 Markdown chunks
        })
        url_to_id[url] = entity_id

    # Step 2: 從 URL 結構建立「導覽」邊
    for page_title, page_data in results.items():
        url = page_data["url"]
        path = urlparse(url).path

        # 從 URL 路徑推導父子關係
        # /members/professor_zhang → 父頁面是 /members
        parent_path = "/".join(path.strip("/").split("/")[:-1])
        if parent_path:
            parent_url = (
                f"{urlparse(url).scheme}://{urlparse(url).netloc}/{parent_path}"
            )
            if parent_url in url_to_id:
                rel_id += 1
                relationships.append({
                    "id": rel_id,
                    "source": url_to_id[parent_url],
                    "target": url_to_id[url],
                    "description": "導覽子頁面",
                    "weight": 1.0,
                    "text_unit_ids": [],
                })

    return entities, relationships
```

---

## 5. 結構圖的檢索能力

### 5.1 跨頁面關係查詢

```
用戶問：「張三發表了哪些論文？」

結構圖：
  從「張三頁面」節點出發 → traversal 找所有「引用」邊指向的頁面
  → 精準找到張三頁面連結到的所有論文頁面
  → 零幻覺
```

### 5.2 層級式瀏覽（Overview → Detail）

```
用戶問：「實驗室有哪些研究方向？」

結構圖：
  首頁節點 → 層級遍歷子頁面
  → 看到完整的導覽結構：成員 | 論文 | 公告 | 研究
  → 知道「研究」下有 NLP、CV、RAG 三個子方向
  → 完整且有組織
```

### 5.3 隱含的類別關係

```
網站導覽結構：
  首頁
  ├── 成員
  │   ├── 教授
  │   ├── 研究生
  │   └── 專題生
  ├── 論文
  │   ├── 2024
  │   ├── 2023
  │   └── 2022
  └── 公告

結構圖自動知道：
  「張三」在「成員/教授」下 → 他是教授
  「論文 A」在「論文/2024」下 → 它是 2024 年的論文
  → 這些資訊來自 URL 結構，不需要從文字中提取
```

### 5.4 補足向量檢索的盲區

```
用戶問：「做 NLP 的成員有哪些？」

向量 RAG：
  搜尋「NLP 成員」→ 可能找到「NLP」相關的論文頁面
  → 但找不到「成員」頁面（因為成員頁面的文字不含「NLP」）

結構圖：
  「NLP」節點 ←隸屬─ 「成員頁面」
  從「NLP」traversal → 找到所有隸屬的成員頁面
  → 補足了向量檢索的盲區
```

### 5.5 查詢路由的結構線索

```
用戶問：「最近的公告？」

結構圖知道：
  「公告」是一個頁面類別（從 URL 結構 /news 得知）
  → 自動路由到 page_type=announcement 的頁面群
  → 不需要 LLM 猜測意圖
```

---

## 6. Microsoft GraphRAG BYOG 整合

### 6.1 Bring Your Own Graph

Microsoft GraphRAG 支援直接匯入你自己的預建圖，不需要 LLM 抽取。

你需要提供三個 Parquet 檔案：

```
output/
├── entities.parquet      # 必須：圖的節點
├── relationships.parquet # 必須：圖的邊
└── text_units.parquet    # 選擇：原始文字 chunks（Local Search 需要）
```

### 6.2 Entities 表格式

```
| id | title | description | text_unit_ids |
|----|-------|-------------|---------------|
| 1  | 首頁  | 國立中央大學智慧與資料探勘實驗室... | [1, 2] |
| 2  | 成員頁面 | 實驗室成員列表... | [3] |
| 3  | 張三  | 教授，專長NLP... | [4, 5] |
| 4  | 論文A | 提出混合檢索方法... | [6] |
```

### 6.3 Relationships 表格式

```
| id | source | target | description | weight | text_unit_ids |
|----|--------|--------|-------------|--------|---------------|
| 1  | 首頁   | 成員頁面 | 導覽連結 | 1.0 | [] |
| 2  | 成員頁面 | 張三 | 列為成員 | 1.0 | [3] |
| 3  | 張三   | 論文A | 發表 | 0.9 | [4] |
| 4  | 論文A  | 論文B | 引用 | 0.8 | [6] |
```

### 6.4 設定檔

```yaml
# settings.yaml — 結構圖模式（不需要 LLM 抽取）
workflows: [create_communities, create_community_reports]
# 跳過 extract_entities 和 extract_graph（因為你已經有了）
```

### 6.5 查詢模式

```
Global Search：用社區摘要回答概覽性問題
  「實驗室的研究方向有哪些？」→ 搜尋所有 Community Summary

Local Search：從特定節點 traversal 找關聯
  「張三發表了什麼？」→ 從「張三」節點出發，沿著邊找
```

---

# Part III — 語義圖（從內容建圖）

## 7. 語義圖的核心概念

### 什麼是語義圖

```
語義圖 = 從文字內容中用 LLM 自動抽取實體和關係建立的知識圖譜

需要 LLM 呼叫（每個文字片段都要跑 Entity Extraction）
成本較高，但能捕捉結構圖無法捕捉的語義關係
```

### 語義圖捕捉的關係類型

```
關係 1：人物關係
  張三 --指導--> 李四
  張三 --任職於--> 實驗室

關係 2：研究成果關係
  李四 --發表--> 論文 A
  論文 A --屬於--> NLP 領域
  論文 A --引用--> 論文 B

關係 3：組織關係
  實驗室 --隸屬--> 國立中央大學
  NLP 領域 --研究--> 自然語言處理
```

### 語義圖 vs 結構圖

| 面向 | 結構圖 | 語義圖 |
|---|---|---|
| 資料來源 | URL、超連結、導覽列 | Markdown 正文 |
| 建圖成本 | **$0**（不需要 LLM） | 需要 LLM 呼叫 |
| 捕捉的關係 | 頁面間的導覽、引用、層級 | 實體間的語義關係（發表、指導） |
| 適合的查詢 | 「哪些頁面互相連結？」 | 「這兩個人有什麼關係？」 |
| 精準度 | 結構上精準（連結 = 確定的關係） | 語義上可能有幻覺 |

---

## 8. LLM 實體抽取

### 8.1 抽取流程

```
原始 Markdown：
  "張三教授是國立中央大學資訊工程學系的教授，
   專長為自然語言處理與資訊檢索，
   他指導的李四同學發表了論文 A。"

LLM 抽取出：
  實體：
    - 張三（Person, Professor）
    - 國立中央大學資訊工程學系（Organization）
    - 自然語言處理（Research Field）
    - 資訊檢索（Research Field）
    - 李四（Person, Student）
    - 論文 A（Publication）

  關係：
    - 張三 --任職於--> 國立中央大學資訊工程學系
    - 張三 --專長--> 自然語言處理
    - 張三 --指導--> 李四
    - 李四 --發表--> 論文 A
```

### 8.2 Microsoft GraphRAG 的抽取流程

```
Step 1: 切分為 TextUnits（可分析的最小單位）
Step 2: LLM 提取實體（Entities）和關係（Relationships）
Step 3: 建立 Knowledge Graph（實體為節點，關係為邊）
Step 4: Leiden 演算法做社區聚類（Community Detection）
Step 5: 為每個社區生成摘要報告（Community Summary）
Step 6: 將所有內容向量化（Embedding）存入向量資料庫
```

### 8.3 實體抽取的 Prompt 設計

```
Extract all entities and relationships from the following text.

Entity types: Person, Organization, ResearchField, Publication, Event
Relationship types: authored, supervised, affiliated_with, researches, cites

Text:
{chunk}

Output format:
Entities: [(entity_name, entity_type), ...]
Relationships: [(source, relationship, target), ...]
```

### 8.4 成本預估

```
假設 100 個 Markdown 文件，平均每文件 2000 tokens：
  Entity Extraction: ~200K tokens → ~$0.5–2（取決於模型）
  Community Summary: ~50 個社區 × 2000 tokens → ~$0.1–0.5
  總計：約 $1–3（一次性成本）

Query 成本：
  Local Search: 與一般 RAG 相當
  Global Search: 較高（需要處理所有社區摘要）
```

---

## 9. 社區偵測與摘要

### 9.1 Leiden 社區偵測

```
完整圖：
  張三 --指導--> 李四 --發表--> 論文 A --屬於--> NLP
  張三 --指導--> 王五 --發表--> 論文 B --屬於--> NLP
  趙六 --專長--> CV --發表--> 論文 C

Leiden 聚類結果：
  Community 1（NLP 群）: {張三, 李四, 王五, NLP, 論文 A, 論文 B}
  Community 2（CV 群）:   {趙六, CV, 論文 C}
```

### 9.2 社區摘要

```
Community 1 摘要：
  "NLP 研究群由張三教授領導，成員包括李四和王五。
   研究方向為自然語言處理，已發表論文 A 和論文 B。
   論文 A 關注混合檢索方法，論文 B 關注知識圖譜增強。"

Community 2 摘要：
  "電腦視覺研究群由趙六教授負責，專注於影像辨識與目標偵測。"
```

### 9.3 社區摘要的檢索價值

```
Global Search 的威力：
  用戶問：「實驗室的研究方向有哪些？」
  → 不需要找到具體文件
  → Community Summary 直接回答完整概覽
  → 這是一般 Vector RAG 做不到的
```

---

## 10. 語義圖的檢索能力

### 10.1 多跳推理（Multi-hop Reasoning）

```
用戶問：「做 NLP 的成員發表了什麼論文？」

語義圖 traversal：
  「NLP」→ 找到所有研究 NLP 的成員 → 找到他們發表的論文
  → 張三 --研究--> NLP --發表--> 論文 A, 論文 B
  → 李四 --研究--> NLP --發表--> 論文 C
  → ✅ 一次 traversal 找到完整答案
```

### 10.2 全域概覽（Global Understanding）

```
用戶問：「實驗室的研究方向有哪些？」

語義圖：
  Community Summary 直接回答：
  "NLP 研究群、電腦視覺研究群、資料探勘研究群..."
  → 不需要找到具體文件就能回答
  → 這是一般 Vector RAG 做不到的
```

### 10.3 實體消歧（Entity Disambiguation）

```
用戶問：「張三和李四有什麼關係？」

語義圖：
  張三 --指導--> 李四（指導關係）
  張三 --合作--> 李四（合作關係）
  → 明確知道兩人的關係類型
  → Vector RAG 只能返回「他們的文字相似」
```

---

# Part IV — 兩圖整合與實作

## 11. 結構圖 vs 語義圖對照

| 面向 | 結構圖 | 語義圖 |
|---|---|---|
| **資料來源** | URL、超連結、導覽列 | Markdown 正文 |
| **建圖成本** | **$0**（不需要 LLM） | 需要 LLM 呼叫（$1–3/100 頁） |
| **建圖速度** | 極快（純程式邏輯） | 較慢（LLM 呼叫） |
| **捕捉的關係** | 頁面間的導覽、引用、層級 | 實體間的語義關係 |
| **精準度** | 結構上精準（連結 = 確定的關係） | 語義上可能有幻覺 |
| **維護成本** | 低（網站更新時重新爬取即可） | 中（內容更新時需重新抽取） |
| **適合的查詢** | 「哪些頁面互相連結？」 | 「這兩個人有什麼關係？」 |
| **查詢模式** | Local Search（ traversal） | Global + Local Search |

---

## 12. 兩圖合併策略

### 12.1 合併架構

```
                 你的爬蟲產出
                      │
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
   URL 結構        page_type     Markdown 內容
   parent_url      metadata      正文文字
        │             │             │
        ↓             ↓             ↓
   ┌─────────┐  ┌──────────┐  ┌──────────┐
   │ 結構圖   │  │ 節點屬性  │  │ 語義圖   │
   │(不需要   │  │(不需要   │  │(需要     │
   │ LLM)    │  │ LLM)     │  │ LLM)     │
   └────┬────┘  └────┬─────┘  └────┬─────┘
        │             │             │
        └─────────────┼─────────────┘
                      ↓
              合併為完整知識圖譜
```

### 12.2 合併後的圖

```
完整圖：
  結構關係（零成本）：
    首頁 ──導覽──→ 成員頁面 ──導覽──→ 張三頁面
    張三頁面 ──引用──→ 論文 A 頁面

  語義關係（LLM 成本）：
    張三 ──指導──→ 李四
    李四 ──發表──→ 論文 A
    論文 A ──屬於──→ NLP

  兩者結合：
    「張三頁面」 ──導覽──→ 「論文 A 頁面」
         │                      │
         └──發表──→ 張三 ──發表──→ 論文 A

    結構關係 + 語義關係 = 最完整的圖
```

### 12.3 合併的好處

```
查詢：「張三發表了哪些論文？」

只有結構圖：
  從「張三頁面」traversal → 找到所有引用的論文頁面
  → 結構上精準，但不知道「發表」這個語義關係

只有語義圖：
  從「張三」節點 traversal → 找到所有「發表」邊指向的論文
  → 語義上精準，但可能有抽取遺漏

兩圖合併：
  結構圖先找到所有相關頁面（高召回）
  語義圖再用語義關係排序（高精準）
  → 兼具結構精準和語義完整
```

---

## 13. 與現有 Agent 架構的整合

### 13.1 工具層整合

```
目前的 Agent 工具層：
  ┌─────────────────────────┐
  │ webpage_retriever tool  │ ← 向量混合檢索
  │ (StructuredTool)        │
  └─────────────────────────┘

整合後：
  ┌─────────────────────────┐
  │ webpage_retriever tool  │ ← 向量混合檢索（已有）
  │ (StructuredTool)        │
  ├─────────────────────────┤
  │ graph_retriever tool    │ ← 知識圖譜檢索（新增）
  │ (StructuredTool)        │
  └─────────────────────────┘
         ↓
    Agent 根據 tool description 自主選擇
```

### 13.2 Agent 選擇邏輯

```
Agent 的 tool description：

webpage_retriever:
  "搜尋網站中的網頁內容。適用於根據文字相似度查找相關段落。"

graph_retriever:
  "搜尋網站中的實體關係。適用於查找人物、論文、組織之間的關聯，
   或瀏覽網站的完整導覽結構。"

Agent 自動選擇：
  「實驗室有哪些研究方向？」→ graph_retriever（結構圖 traversal）
  「混合檢索的方法論？」→ webpage_retriever（向量搜尋）
  「張三發表了什麼？」→ graph_retriever（語義圖 traversal）
  「最新的公告？」→ webpage_retriever + filter_dict
```

### 13.3 與專案規劃的一致性

你的 `2026_0721-RAG_Upgrade.md` 已經規劃了這個架構：

> 「Phase 5 的圖譜工具將以相同模式封裝為第二個 StructuredTool，Agent 透過 tool description 自主選擇。」

你的 `data_retrieve.md` 也明確提到：

> 「與此並行的尚有**知識圖譜檢索（網站結構）**、**資料庫檢索（多欄位資料）**兩條策略路徑，依資料類型分流選用。」

---

## 14. 實作路線圖

### 14.1 推薦實作順序

```
Phase A: 結構圖原型（1–2 週）
├── [A1] 從 results.json 建立 entities + relationships Parquet
├── [A2] 用 Microsoft GraphRAG BYOG 匯入
└── [A3] 用 Global Search 驗證「研究方向概覽」查詢

Phase B: 結構圖完善（2–3 週）
├── [B1] 從 Markdown 超連結提取引用關係
├── [B2] 封裝為 graph_retriever StructuredTool
└── [B3] 與 webpage_retriever 並列，Agent 自主選擇

Phase C: 語義圖導入（4–6 週）
├── [C1] 用 LLM 從 Markdown 抽取實體/關係
├── [C2] 與結構圖合併
└── [C3] 建立 Local + Global 查詢模式

Phase D: 精細調優（長期）
├── [D1] 社區摘要品質調優
├── [D2] 實體抽取 prompt 優化
└── [D3] 整合「網站導航」功能（圖譜驅動的頁面跳轉）
```

### 14.2 影響評估

| Phase | 投入 | 預期效果 | 風險 |
|---|---|---|---|
| A | 低 | 結構關係查詢從 0 → 有 | 低（增量改善） |
| B | 中 | Agent 可自主選擇向量/圖譜 | 中（需驗證 tool description） |
| C | 高 | 語義關係查詢從 0 → 有 | 高（LLM 抽取品質） |
| D | 中 | 持續優化 | 低（迭代改善） |

### 14.3 驗證每個 Phase 的方法

```
Phase A 驗證:
  1. 確認 entities.parquet 和 relationships.parquet 正確建立
  2. 用 Global Search 查詢「實驗室的研究方向有哪些？」
  3. 驗證社區摘要是否準確反映網站結構

Phase B 驗證:
  1. 確認引用關係從 Markdown 正確提取
  2. 用 Local Search 查詢「張三發表了什麼？」
  3. 驗證 Agent 是否能自主選擇正確的工具

Phase C 驗證:
  1. 確認實體抽取的精度和召回率
  2. 用多跳查詢驗證「做 NLP 的成員發表了什麼？」
  3. 比較結構圖 + 語義圖 vs 單獨使用的效果

Phase D 驗證:
  1. 比較不同 community summary 策略的效果
  2. 統計各查詢類型的路由準確率
  3. 測試「網站導航」功能的使用者體驗
```

---

## 15. 參考資源

### 官方文件

| 資源 | 用途 |
|---|---|
| [Microsoft GraphRAG](https://microsoft.github.io/graphrag/) | GraphRAG 核心框架 |
| [GraphRAG BYOG](https://microsoft.github.io/graphrag/index/byog/) | 匯入自己的圖 |
| [GraphRAG Query](https://microsoft.github.io/graphrag/query/overview/) | 查詢引擎（Local/Global/DRIFT） |
| [LlamaIndex PropertyGraphIndex](https://docs.llamaindex.ai/en/stable/examples/property_graph/property_graph_index/) | LlamaIndex 的圖譜整合 |

### 關鍵論文

| 論文 | 核心貢獻 |
|---|---|
| **GraphRAG** (Edge et al., 2024) | 圖譜 + 社區摘要的 RAG 架構 |
| **Automatic Sitemaps Generation** (2011) | 網站超連結結構 = 基礎本體論 |
| **Closed Sequential Pattern Mining for Sitemap** (2021) | 從頁面結構 + 超連結自動建 sitemap |
| **Web Data Commons Hyperlink Graph** (2014) | 大規模超連結圖的實證研究 |
| **Representing Web Apps As Knowledge Graphs** (2024) | Web 應用 = 有向圖 |

### 相關研究

| 研究 | 核心論點 |
|---|---|
| **DOM Graph RAG** (2024) | DOM 結構直接建圖，保留原始結構關係 |
| **KGC-RAG** (2024) | URL 路徑名稱作為語義線索 |
| **Hierarchical Knowledge Graphs** | 層級化知識圖譜的建構方法論 |

---

## 16. 術語表

| 術語 | 英文 | 說明 |
|---|---|---|
| 知識圖譜 | Knowledge Graph | 以實體為節點、關係為邊的結構化知識表示 |
| 結構圖 | Structure Graph | 從網站 URL 結構和超連結建立的圖 |
| 語義圖 | Semantic Graph | 從文字內容用 LLM 抽取實體/關係建立的圖 |
| 社區偵測 | Community Detection | 將緊密關聯的實體聚成群組的演算法 |
| 社區摘要 | Community Summary | 為每個社區群組生成的文字摘要 |
| Traversal | — | 沿著圖的邊遍歷節點 |
| Multi-hop Reasoning | — | 透過多條邊的跳躍進行推理 |
| Global Search | — | 用社區摘要回答全域概覽性問題 |
| Local Search | — | 從特定節點出發，沿著邊找關聯 |
| BYOG | Bring Your Own Graph | 匯入預建圖而非用 LLM 抽取 |
| TextUnit | — | 圖譜中對應原始文字的最小單位 |
| Leiden Algorithm | — | 社區偵測演算法，用於圖的聚類 |
