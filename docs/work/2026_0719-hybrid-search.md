# Hybrid Search (2026/7/19)
> 對應 `2026_0708-RAG_Upgrade.md` 第二部分（二、混合檢索與重排序）

## 前置回顧：Phase 1 對 Phase 2 的關鍵影響

| Phase 1 發現 | Phase 2 策略 |
|---|---|
| Paper 節點 cosine score 僅 0.37–0.38，容易被 `cutoff=0.4` 誤殺 | BM25 關鍵字匹配可補回語意檢索的漏網之魚 |
| Q5 回歸驗證通過（filter 隔離非 paper）但向量分數仍低 | Milvus WeightedRanker 保留 cosine 分數，避免 RRF 誤殺 |
| 日期萃取四層策略驗證通過，`year` metadata 可用於後續過濾 | Hybrid Retriever 可合併使用 metadata filter + hybrid mode |

---

# Part 1 — Qdrant Hybrid Search

## 1.1 概念：Dense vs Sparse 向量

| 向量類型 | 說明 | 範例模型 |
|---|---|---|
| **Dense Vectors**（稠密向量） | 透過嵌入模型將整段文字壓縮為固定長度的數值向量，捕捉語義關聯 | OpenAI Embeddings, BGE, SentenceTransformers |
| **Sparse Vectors**（稀疏向量） | 大部分元素為零的高維向量，每個維度對應詞彙表中的一個詞，擅長關鍵字比對 | TF-IDF, BM25, SPLADE |

Hybrid Search 的核心優勢在於同時利用兩者的互補性：語義理解（dense）用於捕捉同義詞與上下文，關鍵字匹配（sparse）用於確保特定術語不被遺漏。

## 1.2 依賴套件：fastembed

| 套件 | 用途 | 安裝指令 |
|---|---|---|
| `fastembed>=0.6.0` | Qdrant BM25 稀疏向量本地生成，與 `enable_hybrid=True` 無縫整合 | `uv add fastembed` |

`fastembed` 是 Qdrant 官方推薦的稀疏向量生成引擎，可在本機端執行 BM25/SPLADE 模型，不需外部 API。

## 1.3 Config Schema：Hybrid 相關擴充

### RagConfig dataclass — Hybrid 欄位

| Section | 欄位 | 類型 | 預設值 | 說明 |
|---------|------|------|--------|------|
| `[retriever]` | `similarity_top_k` | `int` | `10` | 最終回傳的節點數 + dense 候選數 |
| `[retriever]` | `query_mode` | `str` | `"hybrid"` | `"hybrid"` 或 `"default"` |
| `[retriever]` | `hybrid_top_k` | `int` | `10` | sparse 分支候選數（原 `sparse_top_k`） |
| `[retriever]` | `alpha` | `float` | `0.5` | 稠密/稀疏權重（僅 Qdrant Weighted 有效） |

> **命名演進**：`top_k`→`similarity_top_k`、`sparse_top_k`→`hybrid_top_k`；`enable_hybrid` 與 `fastembed_sparse_model` 已從 config 層移除，改為硬編碼

### Config keys 定義

`RETRIEVER_KEYS` 包含 `similarity_top_k`、`query_mode`、`hybrid_top_k`、`alpha`。`_validate_config()` 新增驗證：`query_mode` 僅接受 `"hybrid"` 或 `"default"`、`alpha` 須介於 0.0~1.0、`similarity_top_k` 與 `hybrid_top_k` 須為正整數。

### 設定檔範例（`configs/rag/test-qdrant.toml`）

於 `[retriever]` 區段設定 `similarity_top_k = 10`、`query_mode = "hybrid"`、`hybrid_top_k = 10`、`alpha = 0.5`。

## 1.4 Vector Store 改造：啟用 Hybrid 索引

**位置**：`app/modules/rag.py` → `build_vector_store()`

`build_vector_store()` 中，若 `vector_store_type == "qdrant"`，建立 `QdrantClient` 後以 `QdrantVectorStore` 初始化 collection，其中 `enable_hybrid=True` 與 `fastembed_sparse_model="Qdrant/bm25"` 皆為硬編碼。

### 關鍵考量

- `enable_hybrid=True` 使新 collection 同時包含稠密向量 + BM25 稀疏向量
- `Qdrant/bm25` 為 Qdrant 官方預訓練模型，不需額外訓練
- 既有 collection 若無 sparse vectors 需重建索引（`--run.force-rebuild`）

## 1.5 Retriever 改造：混合檢索 + Metadata Filter 共存

**位置**：`app/modules/rag.py` → `build_retriever()`

`build_retriever()` 接受 `query_mode`、`filter_dict`、`similarity_top_k`、`hybrid_top_k`、`alpha` 等參數，預設 `query_mode="hybrid"`。

內部邏輯：`filter_dict` 轉換為 `MetadataFilters`（邏輯不變）；`query_mode="hybrid"` 時傳入 `VectorStoreQueryMode.HYBRID`，否則退化為純稠密檢索。Metadata filter 與 hybrid mode 可同時作用（Qdrant pre-filter），`alpha` 控制 Weighted 線性融合。

## 1.6 實測成效

在 `query_mode="hybrid"` 下以 Qdrant force-rebuild 測試「實驗室的成員有哪些人？」：

| 指標 | 結果 |
|---|---|
| Top-1 Score | 0.499（cosine similarity） |
| 成員覆蓋 | 12 位 ✅ |
| Faithfulness | 100% ✅ |
| Relevancy | 100% ✅ |
| 執行時間 | ~12 秒 |

## 1.7 已知限制：BM25 中文支援不足

`Qdrant/bm25` 主要針對英文語料，中文 tokenization 效果有限，因此引入 Milvus + BGE-M3（詳見 Part 2）。

---

# Part 2 — Milvus Hybrid Search

## 2.1 動機

Qdrant + BM25 對中文語料的關鍵字匹配效果有限，因此引入 Milvus + BGE-M3 作為替代方案。BGE-M3 是 BAAI 推出的多語言 embedding 模型，原生支援中文稀疏編碼，可同時產生 dense、sparse、ColBERT 三種向量。

## 2.2 依賴套件

| 套件 | 用途 | 安裝指令 |
|---|---|---|
| `llama-index-vector-stores-milvus>=1.1.0` | LlamaIndex Milvus 整合 | `uv add llama-index-vector-stores-milvus` |
| `FlagEmbedding>=1.3.0` | BGE-M3 模型（含 BGEM3FlagModel） | `uv add FlagEmbedding` |

`FlagEmbedding` 首次使用會自動下載 BGE-M3 模型（約 2.2GB）。

## 2.3 Vector Store 改造

**位置**：`app/modules/rag.py` → `build_vector_store()`

若 `vector_store_type == "milvus"`，建立 `MilvusVectorStore` 並傳入 `enable_sparse=True` 與 `sparse_embedding_function=BGEM3SparseEmbeddingFunction()`，同時設定 `output_fields=["_node_content", "_node_type"]`（MilvusLite 須明確指定才能回傳完整節點資料）。

### 關鍵參數

| 參數 | 預設值 | 說明 |
|------|--------|------|
| `enable_sparse` | `True`（硬編碼） | 啟用 sparse 向量欄位 |
| `sparse_embedding_function` | `BGEM3SparseEmbeddingFunction()` | 使用 BGE-M3 產生稀疏編碼 |
| `overwrite` | `True` | 是否清除既有 collection 重建 |
| `output_fields` | `["_node_content", "_node_type"]` | MilvusLite 須明確指定才能回傳完整節點資料 |
| `hybrid_ranker` | `"RRFRanker"` | 融合演算法（詳見 §2.5） |
| `hybrid_ranker_params` | `{}` | ranker 細部參數 |

## 2.4 BGEM3SparseEmbeddingFunction

此為 LlamaIndex 內建類別，封裝 `BGEM3FlagModel("BAAI/bge-m3", use_fp16=False)`，將查詢與文件的稀疏編碼統一透過 `encode_queries()` 路徑生成，回傳 `lexical_weights` 詞彙權重字典。

### 自訂 sparse function

若要調整 `use_fp16` 或改用其他模型，可繼承 `BaseSparseEmbeddingFunction` 自訂。

## 2.5 融合演算法：RRF vs WeightedRanker

Milvus 支援兩種 hybrid 融合策略：

### RRFRanker（預設）

公式為 `score = 1/(k + rank_dense) + 1/(k + rank_sparse)`，只看排名不比分數，分數範圍固定（k=60 時約 0~0.033）。`alpha` 無效，`k` 越小 sparse 影響力越大。初始化時傳入 `hybrid_ranker="RRFRanker"` 與 `hybrid_ranker_params={"k": 60}`。

### WeightedRanker

公式為 `score = w_dense × dense_score + w_sparse × sparse_score`，保留 cosine similarity 特性（0~1），使用 `weights=[w_dense, w_sparse]` 語法。建議實驗值 `[1.0, 0.3]`（dense 為主，sparse 為輔）。初始化時傳入 `hybrid_ranker="WeightedRanker"` 與 `hybrid_ranker_params={"weights": [1.0, 0.3]}`。

## 2.6 Score 特性與 SimilarityPostprocessor

RRF 分數極低（0.01~0.03），若 `build_query_engine()` 使用 `SimilarityPostprocessor(cutoff=0.4)` 會全數誤殺。

**解法**：hybrid 模式跳過 `SimilarityPostprocessor`，僅非 hybrid 模式才加入 `SimilarityPostprocessor(similarity_cutoff=cutoff)`。

## 2.7 Retriever 參數

| 參數 | 預設值 | 說明 | 建議調整 |
|---|---|---|---|
| `similarity_top_k` | `10` | 最終輸出數 + dense 候選數 | 依需求增減 |
| `hybrid_top_k` | `10` | sparse 分支候選數 | **建議 20~30**，讓 sparse 有更多優質候選 |
| `alpha` | `0.5` | ⚠️ **RRF 下無效** | 改用 WeightedRanker 後用 `weights` |

## 2.8 持久化與重用

MilvusLite 使用本機檔案作為儲存後端，有以下注意事項：

| 問題 | 說明 | 解法 |
|---|---|---|
| **`overwrite=True` 清空資料** | 每次呼叫清除 collection | 非重建傳入 `overwrite=False` |
| **`from_vector_store()` index 不完整** | `nodes_dict` 為空，無法解析檢索 | 非重建仍需 `build_nodes()` + `build_index()` |
| **collection released** | 二次載入時停在 `released` 狀態 | `load_index()` 中加入 `client.load_collection()` |

目前 `run_rag_query()` 對 Milvus 強制走完整重建路徑（`build_nodes` → `build_vector_store` → `build_index`）。

## 2.9 實測成效

在 `query_mode="hybrid"` 下以 Milvus force-rebuild 測試「實驗室的成員有哪些人？」：

| 指標 | RRFRanker（預設） | WeightedRanker `[1.0, 0.5]`（估算） |
|---|---|---|
| Top-1 Score | 0.033（RRF 排名分數） | ~0.4~0.5（保留 cosine） |
| 成員覆蓋 | 7 位（漏列多人） | 預期接近 Qdrant 水準 🔍 |
| Faithfulness | 100% ✅ | — |
| Relevancy | 100% ✅ | — |
| 執行時間 | ~34 秒（含模型載入） | 同左 |

> **預設 RRF 下 sparse 干擾過大**，建議改用 `WeightedRanker` 搭配 `weights=[1.0, 0.3]`。

## 2.10 Qdrant vs Milvus 比較

| 面向 | Qdrant (BM25 + Weighted) | Milvus (BGE-M3 + RRF) |
|---|---|---|
| **Sparse model** | `Qdrant/bm25`（純 BM25） | `BAAI/bge-m3`（神經稀疏編碼） |
| **中文支援** | ⚠️ 有限 | ✅ **原生支援** |
| **融合演算法** | Weighted: `alpha × dense + (1-alpha) × sparse` | RRF: rank-based（預設） |
| **Score 可讀性** | ✅ Cosine 0.4~0.5 | ❌ RRF 0.01~0.03 |
| **Sparse 實際影響** | 較低（dense 主導） | 較高（RRF 只看排名） |
| **執行時間** | ~12 秒（無模型載入） | ~34 秒（含 BGE-M3 載入） |
| **持久化** | ✅ 支援 Qdrant 本機檔案 | ⚠️ MilvusLite 有限 |
| **`alpha` 參數** | ✅ 有效 | ❌ 無效（需改用 `weights`） |

### 適用場景建議

| 場景 | 建議 |
|---|---|
| 快速穩定，中英文混合 | **Qdrant + hybrid default** |
| 中文為主，需進階 sparse 匹配 | **Milvus + WeightedRanker** |
| 實驗與調參 | 兩者皆保留，切換 `vector_store_type` |

# Part 3 — Milvus Vector Store 優化

## 3.1 實驗設計總覽

Milvus Hybrid Search 效能高度依賴融合演算法與檢索參數的搭配，建議依以下階段逐步測試。

### 測試查詢集

| 編號 | 查詢 | 測試重點 |
|------|------|---------|
| Q1 | 「實驗室的成員有哪些人？」 | 成員列表完整度（既有基準） |
| Q2 | 「M 先生的論文有哪些？」 | Paper + filter 混合情境 |
| Q3 | 「實驗室的最新研究方向？」 | 中文關鍵字匹配 |
| Q4 | 「2024 年發表的論文有哪些？」 | Metadata filter + hybrid 共存 |
| Q5 | 回歸查詢（既有測試） | 確保不破壞既有結果 |

### 評斷標準

| 指標 | 目標值 | 優先級 |
|------|--------|--------|
| Q1 成員覆蓋 | **≥ 10 位**（接近 Qdrant 12 位） | P0 |
| Top-1 Score | **≥ 0.35**（避免 cutoff 誤殺） | P0 |
| Faithfulness | 100% | P0 |
| Q5 回歸通過 | 與既有結果一致 | P1 |
| 執行時間 | **≤ 35 秒**（含首次模型載入） | P2 |

## 3.2 初始環境驗證

| 項目 | 檢查內容 | 驗證方式 |
|------|---------|---------|
| 依賴安裝 | `FlagEmbedding>=1.3.0`、`llama-index-vector-stores-milvus>=1.1.0` | `uv pip list` 確認 |
| BGE-M3 模型下載 | 首次執行自動下載 ~2.2GB | 觀察首次建索引是否成功 |
| `output_fields` | 設定 `["_node_content", "_node_type"]` | 檢索結果 `node.text` 非空 |
| `load_collection()` | `load_index()` 中呼叫 `client.load_collection()` | 第二次查詢不報錯 |
| 設定檔 | `configs/rag/test-milvus.toml` | 確認 `[retriever]` section 完整 |

## 3.3 融合演算法比較（核心實驗）

依序測試三種配置：

### 實驗 A：RRFRanker（預設基準）

```toml
[vector_store]
type = "milvus"
hybrid_ranker = "RRFRanker"
hybrid_ranker_params = { k = 60 }

[retriever]
similarity_top_k = 10
query_mode = "hybrid"
hybrid_top_k = 10
```

預期結果：Top-1 Score ~0.033（RRF 排名分數），成員覆蓋 ~7 位（文件實測）。

### 實驗 B：WeightedRanker（建議方案）

```toml
[vector_store]
type = "milvus"
hybrid_ranker = "WeightedRanker"
hybrid_ranker_params = { weights = [1.0, 0.3] }

[retriever]
similarity_top_k = 10
query_mode = "hybrid"
hybrid_top_k = 20
```

預期改善：Top-1 Score → ~0.4~0.5，成員覆蓋 → 接近 Qdrant 水準（12 位）。

### 實驗 C：RRFRanker 調 k 值（備選方案）

```toml
[vector_store]
type = "milvus"
hybrid_ranker = "RRFRanker"
hybrid_ranker_params = { k = 100 }

[retriever]
similarity_top_k = 10
query_mode = "hybrid"
hybrid_top_k = 20
```

預期：k 值調高 → sparse 權重降低 → 減少干擾但保留 keyword 輔助效果。

## 3.4 精細調參

### WeightedRanker 權重網格搜尋

| `weights` | 預期特性 | 適用場景 |
|-----------|---------|---------|
| `[1.0, 0.1]` | sparse 幾乎無影響，近似 dense-only | dense 已足夠的查詢 |
| `[1.0, 0.3]` | dense 主導，sparse 輕量輔助 | **建議起點** |
| `[1.0, 0.5]` | sparse 影響適中 | 中文關鍵字查詢 |
| `[0.7, 0.3]` | 降低 dense 權重，給 sparse 更多空間 | dense 分數偏低的論文查詢 |

### RRFRanker k 值網格搜尋

| `k` | sparse 影響力 | 說明 |
|-----|-------------|------|
| `60` | 預設 | 文件實測 sparse 干擾過強 |
| `80` | 中等 | 建議先試 |
| `100` | 較低 | 保留 keyword 輔助但不主導 |
| `120` | 最低 | 接近 dense-only |

### 其他參數

| 參數 | 建議測試值 | 影響 |
|------|-----------|------|
| `hybrid_top_k` | `10`、`20`、`30` | sparse 帶入的新節點數 |
| `similarity_top_k` | `10`、`15`、`20` | LLM context 長度與品質 |
| `cutoff` | `0.0`（跳過）、`0.3`、`0.4` | hybrid 模式建議跳過 |

### 參數交互關係

```
hybrid_top_k ↑     → sparse 候選越多 → 多樣性 ↑ → recall 可能 ↑
RRF k ↓           → sparse 權重 ↑   → 關鍵字更有影響力
Weighted w ↑sparse → sparse 權重 ↑   → 同 alpha 效果（但用 weights 語法）
similarity_top_k ↑ → 最終輸出 ↑     → LLM context 更長
```

## 3.5 持久化與重建驗證

| 情境 | 測試步驟 | 預期結果 |
|------|---------|---------|
| 首次建立索引 | `run_rag_build()` 搭配 `force_rebuild=true` | BGE-M3 下載 + collection 建置成功 |
| 第二次查詢（非重建） | `run_rag_query()` 不重建 | `load_collection()` 後查詢成功 |
| `overwrite=False` | 手動設定 `overwrite=False` 後查詢 | 既有資料保留，查詢正常 |
| 既有 collection 無 sparse | 模擬升級情境 | 自動偵測並提示 force-rebuild |

## 3.6 退化模式測試

| 情境 | 設定 | 預期行為 |
|------|------|---------|
| dense-only | `query_mode = "default"` | 使用傳統稠密檢索 |

## 3.7 建議執行順序

```
Step 1: 安裝依賴 + 建立 test-milvus.toml
  ↓
Step 2: 執行實驗 A（RRF 基準）→ 記錄成員覆蓋率
  ↓
Step 3: 執行實驗 B（WeightedRanker 建議方案）
  ↓       └── 若成員覆蓋 ≥ 10 → 鎖定此配置
  ↓       └── 若仍不理想 → Step 4
Step 4: 參數網格搜尋（調整 weights + hybrid_top_k）
  ↓
Step 5: 執行實驗 C（RRF k 值調校，備選）
  ↓
Step 6: 驗證持久化（二次查詢、overwrite=False）
  ↓
Step 7: 跑 Q5 回歸測試確認不破壞既有結果
```

---

# 跨領域共用章節

## Workflow Pipeline 更新

### `run_rag_build()` — 將新參數傳入對應方法

| 呼叫方法 | 傳入的新參數 |
|---------|-------------|
| `build_vector_store()` | `vector_store_type`、`overwrite`、`enable_sparse`（硬編碼） |
| `build_retriever()` | `config.similarity_top_k`、`config.query_mode`、`config.hybrid_top_k`、`config.alpha` |
| `build_query_engine()` | `config.cutoff`、`config.query_mode` |

### `run_rag_query()` — 重建策略

| 情境 | 策略 |
|---|---|
| Qdrant + `force_rebuild` 或路徑不存在 | `clean_vector_store()` + 完整重建 |
| Qdrant + 路徑存在 + `overwrite=False` | `build_nodes()` + `build_vector_store(overwrite=False)` + `load_index()` |
| Milvus（任何情況） | 強制完整重建（因 `from_vector_store()` 無法建立完整 index struct） |

## 向後相容策略

| 場景 | 處理方式 |
|---|---|
| 既有 collection 無 sparse vectors | 偵測後自動 clean + rebuild，或提示使用者執行 `--run.force-rebuild` |
| `query_mode="default"` | 使用傳統 dense-only 檢索 |
| 舊 config TOML 無 hybrid section | 透過 `RagConfig` 預設值自動補齊 |
| 舊 config 使用 `top_k` / `sparse_top_k` | 需手動更新為 `similarity_top_k` / `hybrid_top_k` |

## 測試計畫

### 測試檔：`test/test_hybrid_rerank.py`

| 測試類別 | 所屬 | 數量 | 核心驗證 |
|---------|------|------|---------|
| `TestQdrantHybridRetrieval` | Part 1 | 3 | Qdrant hybrid mode 召回率 > dense-only |
| `TestMilvusHybridRetrieval` | Part 2 | 3 | Milvus hybrid mode 召回率 > dense-only |
| `TestFilterCompatibility` | Part 1+2 | 2 | Metadata filter + hybrid mode 同時運作 |
| `TestRegression` | 共同 | 2 | Hybrid + filter 不破壞既有通過條件 |
| `TestEdgeCases` | 共同 | 1 | 退化模式：`query_mode="default"` |

### 預期評估指標

| 指標 | Phase 1 (dense-only) | Part 1+2 (hybrid) |
|------|---------------------|-------------------|
| Q5 Relevancy | ✅ | ✅（維持） |
| Paper 節點召回 | 需 `cutoff=0.0` | BM25/BGE-M3 自然召回 |
| Faithfulness | 100% | 維持 100% |
| Sources 多樣性 | 僅語意相近 | 語意 + 關鍵字補充 |
| Top-N 相關性 | 向量分數排序 | Weighted 分數排序 |

## 成果價值鏈

```
Phase 1 Metadata Filter (隔離非論文)
    ↓
Part 1: Qdrant BM25 稀疏檢索 (英文關鍵字補回)
  OR Part 2: Milvus BGE-M3 神經稀疏編碼 (中文關鍵字補回)
    ↓
Part 1+2: Metadata Filter + Hybrid 同時作用 (分類 + 檢索)
    ↓
Part 3: Milvus 融合演算法調校 (WeightedRanker / RRF 調參)
    ↓
LLM Response (高品質、有來源引用)
```

最終目標：**讓論文查詢不僅 filter 隔離了非論文內容，還透過 hybrid search 找回被 cutoff 誤殺的節點，並透過 Milvus 融合演算法調校保留分數可讀性，產生高品質且有來源引用的回答。**
