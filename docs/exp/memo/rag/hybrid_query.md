# Hybrid Query 設定

> 對應 `2026_0719-hybrid-search.md` Part 3 — Milvus 融合演算法比較（核心實驗）

## Vector Store

### Hybrid Ranker

> **新增可設定參數：`hybrid_ranker`**

TOML 設定檔透過 `[vector_store]` 區段的 `hybrid_ranker` 切換融合演算法。目前支援兩種類型：

| `hybrid_ranker` | 硬編碼 `hybrid_ranker_params` | 說明 |
|:---|---:|---|
| `"RRFRanker"` | `{"k": 60}` | 排名融合，只看 rank 不看分數 |
| `"WeightedRanker"` | `{"weights": [1.0, 0.3]}` | 線性加權，保留 cosine 原始分數 |

## Retriever

### Similarity Top K

> **目前穩定值：10**

沿用 dense-only 階段的穩定值，本次實驗不做調整。

### Hybrid Top K

> **目前穩定值：10**

本次兩個子實驗皆使用 `hybrid_top_k=10`。文件中建議實驗 B（WeightedRanker）可調高至 20 以讓 sparse 分支有更多優質候選，待後續實驗驗證。

### Query Mode

> **目前穩定值：`"hybrid"`**

Milvus BGE-M3 同時產生 dense + sparse 向量。`query_mode="hybrid"` 時使用 `VectorStoreQueryMode.HYBRID`。若設為 `"default"` 則退化為純稠密檢索。

### Alpha

> **RRF 下無效，WeightedRanker 改用 `weights` 語法**

`alpha=0.5` 僅對 Qdrant Weighted 線性融合有效。RRFRanker 完全忽略此參數；WeightedRanker 使用 `hybrid_ranker_params={"weights": [w_dense, w_sparse]}` 控制融合比例。

## Query Engine

### Hybrid Mode 跳過 SimilarityPostprocessor

> **`cutoff` 在 hybrid 模式下不啟用**

`build_query_engine()` 中，當 `query_mode != "hybrid"` 時才加入 `SimilarityPostprocessor(similarity_cutoff=cutoff)`。hybrid 模式完全依賴融合演算法排序，不使用 cutoff 過濾，避免 RRF 極低分數（~0.01–0.03）被全數誤殺。

### LLM

> **目前穩定值：`gemini-3.1-flash-lite`**

沿用 dense-only 階段的穩定配置。

# 實驗一：融合演算法比較（RRF vs Weighted）

## 實驗設計

### 測試問題

| 編號 | 查詢 | 測試重點 |
|:---:|------|---------|
| Q1 | 「實驗室的成員有哪些人？」 | 成員列表完整度（既有基準，與 dense-only Qdrant 比較） |

### 測試配置

| 參數 | 實驗 A（RRF 基準） | 實驗 B（Weighted 建議） |
|------|:---:|:---:|
| **vector_store_type** | milvus | milvus |
| **hybrid_ranker** | RRFRanker | WeightedRanker |
| **hybrid_ranker_params** | `{"k": 60}` | `{"weights": [1.0, 0.3]}` |
| **similarity_top_k** | 10 | 10 |
| **hybrid_top_k** | 10 | 10 |
| **query_mode** | hybrid | hybrid |
| **llm_name** | gemini-3.1-flash-lite | gemini-3.1-flash-lite |
| **query** | 實驗室的成員有哪些人？ | 實驗室的成員有哪些人？ |

### 評斷標準

| 指標 | 目標值 | 優先級 |
|------|--------|:------:|
| 成員覆蓋 | **≥ 10 位**（接近 Qdrant 12 位） | P0 |
| Top-1 Score | **≥ 0.35**（避免 cutoff 誤殺） | P0 |
| Faithfulness | 100% | P0 |
| Relevancy | 100% | P0 |

### 注意事項

- 每次實驗皆 force-rebuild（Milvus 強制完整重建路徑）
- `hybrid_top_k=10` 統一，暫不調整（文件中建議 WeightedRanker 可調至 20，留待後續實驗）

---

## 實驗記錄（Q1：「實驗室的成員有哪些人？」）

### 實驗 A：RRFRanker（k=60）

| 指標 | 結果 |
|------|:---:|
| **Top-1 Score** | 0.033（RRF 排名分數） |
| **Score 範圍** | 0.015–0.033 |
| **成員覆蓋** | 7 位（廖梓逸、簡資烜、張彣謙、邱威誠、李倬安、葉展維、葉庭） |
| **Faithfulness** | ✅ 100% |
| **Relevancy** | ✅ 100% |
| **執行時間** | 37.40 秒 |
| **Sources 多樣性** | ❌ `Letter to potential students` 佔 4/10、`校內奬項` 等不相關頁面進入 Top-10 |

### 實驗 B：WeightedRanker（weights=[1.0, 0.3]）

| 指標 | 結果 |
|:------|:---:|
| **Top-1 Score** | **0.857**（保留 cosine）✅ |
| **Score 範圍** | 0.622–0.857（健康分佈） |
| **成員覆蓋** | **12 位**（廖梓逸、簡資烜、張彣謙、李倬安、葉展維、張勛皓、孫詠淳、黃懷萱、龔若齊、簡國峻、沈哲寬、曾廷綸）✅ |
| **Faithfulness** | ✅ 100% |
| **Relevancy** | ✅ 100% |
| **執行時間** | 38.06 秒 |
| **Sources 多樣性** | ✅ 涵蓋 `Letter to potential students`、`Join WIDM`、`Activities`、`Web Intelligence and Data Mining Lab`、`校外奬項` 等不同頁面 |

### 成員覆蓋詳細比較

| 成員 | RRFRanker | WeightedRanker |
|------|:---:|:---:|
| 張嘉惠（教授） | ✅ | ✅ |
| 廖梓逸 | ✅ | ✅ |
| 簡資烜 | ✅ | ✅ |
| 張彣謙 | ✅ | ✅ |
| 邱威誠 | ✅ | ❌（未出現在 Top-10） |
| 李倬安 | ✅ | ✅ |
| 葉展維 | ✅ | ✅ |
| 葉庭 | ✅ | ❌（未出現在 Top-10） |
| 張勛皓 | ❌ | ✅ |
| 孫詠淳 | ❌ | ✅ |
| 黃懷萱 | ❌ | ✅ |
| 龔若齊 | ❌ | ✅ |
| 簡國峻 | ❌ | ✅ |
| 沈哲寬 | ❌ | ✅ |
| 曾廷綸 | ❌ | ✅ |
| **總計** | **7 位** | **12 位** ✅ |

---

## 實驗總結

### 關鍵發現

#### 1. WeightedRanker 完勝 RRFRanker

| 面向 | RRFRanker（k=60） | WeightedRanker [1.0, 0.3] | 勝負 |
|------|:---:|:---:|:---:|
| Top-1 Score | 0.033 | **0.857** | Weighted |
| 成員覆蓋 | **7 位**（漏列 5 人） | **12 位** ✅ | Weighted |
| 分數可讀性 | ❌ RRF 排名分數 | ✅ Cosine 原始分數 | Weighted |
| Faithfulness | 100% | 100% | 平手 |
| Relevancy | 100% | 100% | 平手 |
| 執行時間 | 37.40s | 38.06s | 平手（±1%） |

**WeightedRanker 在保持相同執行時間與評估分數的前提下，成員覆蓋從 7 位提升至 12 位，與 dense-only Qdrant 水準一致。**

#### 2. RRFRanker 的稀疏干擾問題

RRF 的 rank-based 機制讓 BGE-M3 中文 sparse 分支過度影響排序，導致：

- 分數極度壓縮在 0.015–0.033 之間，無法區分相關性高低
- `校內奬項`、`WIDM Lab Tutorial 2016` 等不相關頁面進入 Top-10，排擠了含成員資訊的優質節點
- 同一頁面的重複 chunk 佔據多個位置（`Letter to potential students` 佔 4/10），多樣性不足

#### 3. WeightedRanker 保留 dense 主導優勢

`weights=[1.0, 0.3]` 讓 dense cosine score 主導排序：

- 真正與 query 相關的節點（Score 0.6–0.8）自然排在前列
- BGE-M3 中文 sparse 僅在 dense 分數接近時發揮輔助拉抬
- 來源多樣性佳，LLM 能從多個分散頁面 cross-reference 出完整名單

### 與 dense-only Qdrant 比較

| 指標 | dense-only Qdrant（Phase 1） | Milvus WeightedRanker（本次） |
|------|:---:|:---:|
| Top-1 Score | 0.499 | **0.857** |
| 成員覆蓋 | 12 位 | **12 位** |
| Faithfulness | 100% | 100% |
| Relevancy | 100% | 100% |

WeightedRanker 的 Top-1 Score 更高（0.857 vs 0.499），但原因可能包含 dense-only 與 hybrid 的 score 計算方式不同（hybrid 的 dense 分支仍使用 cosine），以及重新 rebuild 後的索引略有差異。功能面上成員覆蓋一致，兩者皆可作為正式配置。

# 實驗二：WeightedRanker 權重微調

## 動機

`[1.0, 0.3]` 初步驗證成功，但稀疏權重仍有調校空間。BGE-M3 是神經稀疏編碼（非純 BM25），對中文支援良好，適度提高 sparse 權重可能有助於關鍵字精確匹配。

## 測試配置

| 實驗 | `weights` | 預期特性 |
|:----:|:---------:|---------|
| B-1 | `[1.0, 0.3]` | ✅ 已完成（dense 主導，sparse 輕量輔助） |
| B-2 | `[1.0, 0.5]` | sparse 影響適中，中文關鍵字查詢可能受益 |
| B-3 | `[0.9, 0.3]` | 略降 dense 權重，等同比例放大 sparse 貢獻 |

## 測試查詢

- Q1：「實驗室的成員有哪些人？」（成員覆蓋數）
- Q2：「M 先生的論文有哪些？」（Paper + filter 混合情境）

## 評斷標準

| 指標 | 目標值 |
|------|--------|
| 成員覆蓋（Q1） | ≥ 10 位 |
| Top-1 Score | ≥ 0.35 |
| Faithfulness / Relevancy | 100% |

---

# 實驗三：RRFRanker k 值調校（備選方案）

## 動機

若後續發現 WeightedRanker 在某些查詢仍有 sparse 干擾問題，RRFRanker 調高 k 值可以降低 sparse 權重，作為備選方案。

| 實驗 | `k` | sparse 影響力 | 說明 |
|:----:|:---:|:-------------:|------|
| C-1 | `60` | ❌ 高 | 已驗證，sparse 干擾過強 |
| C-2 | `100` | 中低 | 建議先試 |
| C-3 | `120` | 低 | 接近 dense-only |

## 搭配調整

將 `hybrid_top_k` 從 10 提升至 20，讓 sparse 有更多候選空間但不主導排序。

---

# 實驗四：hybrid_top_k 參數影響

## 動機

當前 `hybrid_top_k=10`，實驗 B 的 Top-1 Score 已達 0.857，但稀疏分支的候選數可能仍受限。調高 `hybrid_top_k` 可讓 sparse 分支貢獻更多優質候選。

## 測試配置（固定 WeightedRanker `[1.0, 0.3]`）

| 實驗 | `hybrid_top_k` | `similarity_top_k` | 預期影響 |
|:----:|:---:|:---:|---------|
| D-1 | 10 | 10 | ✅ 已完成 |
| D-2 | 20 | 10 | sparse 候選倍增，多樣性可能再提升 |
| D-3 | 30 | 10 | 極大化 sparse 貢獻 |

---

# 實驗五：五題全面驗證

## 動機

當前僅以 Q1（名單型）驗證成效。需以 dense-only 階段的五題全面測試，確認 hybrid search 不破壞既有成果。

## 測試問題

| 編號 | 查詢 | 類型 |
|:---:|------|:----:|
| Q1 | 實驗室的成員有哪些人？ | 名單型 ✅（已測） |
| Q2 | 實驗室在 2024 年有哪些活動？ | 時間範圍型 |
| Q3 | 加入實驗室需要準備哪些資料？ | 指引型 |
| Q4 | 如何聯絡研究室指導教授？ | 指引型 |
| Q5 | 實驗室近三年發表過哪些論文？ | 時間範圍型（論文） |

## 測試次數

每題 **1 次 query**（快速驗證參數組合效果，同 dense-only 7/4 實驗設計）。

## 評估方式

FaithfulnessEvaluator + RelevancyEvaluator（使用 `gpt-5.4` 作為獨立 evaluator）。

---

# 實驗六：Metadata Filter + Hybrid 共存驗證

## 動機

確認 metadata filter（如 `page_type="paper"`）與 hybrid mode 同時作用時不互相干擾。

## 測試配置

固定 `WeightedRanker [1.0, 0.3]`、`hybrid_top_k=20`，加入：

```python
filter_dict = {"page_type": "paper"}
```

## 測試查詢

- Q2：「M 先生的論文有哪些？」
- Q5：「實驗室近三年發表過哪些論文？」
- Q5 回歸：「實驗室發表的論文有哪些？」（確保不破壞既有通過條件）

---

# 建議執行順序

```
Step 1: ✅ 實驗一（RRF vs Weighted）— 已完成，WeightedRanker 勝出
  ↓
Step 2: 實驗二（Weighted 權重微調）— 確認 [1.0, 0.3] 是否最優
  ↓
Step 3: 實驗四（hybrid_top_k 影響）— 調高後觀察多樣性變化
  ↓
Step 4: 實驗五（五題全面驗證）— 確認不破壞既有成果
  ↓
Step 5: 實驗六（Metadata Filter 共存）— 驗證 filter + hybrid 同時作用
  ↓
Step 6: 實驗三（RRF k 值調校，備選）— 僅當 Weighted 有問題時啟用
```
