# Hybrid Query 設定

> 對應 `2026_0719-hybrid-search.md` Part 3 — Milvus 融合演算法比較（核心實驗）

## Vector Store

### Hybrid Ranker

> **目前穩定值：`"WeightedRanker"`**

### Hybrid Ranker Params (Weights)
> **目前穩定值：`[1.0, 0.5]`**

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

## 實驗設計

### 測試問題

| 編號 | 查詢 | 測試重點 |
|:---:|------|---------|
| Q1 | 「實驗室的成員有哪些人？」 | 成員列表完整度（與基準權重 `[1.0, 0.3]` 比較） |

### 測試配置

| 參數 | B-1（基準） | B-2（sparse↑） | B-3（dense↓） |
|------|:---:|:---:|:---:|
| **vector_store_type** | milvus | milvus | milvus |
| **hybrid_ranker** | WeightedRanker | WeightedRanker | WeightedRanker |
| **hybrid_ranker_params** | `[1.0, 0.3]` | `[1.0, 0.5]` | `[0.9, 0.3]` |
| **similarity_top_k** | 10 | 10 | 10 |
| **hybrid_top_k** | 10 | 10 | 10 |
| **query_mode** | hybrid | hybrid | hybrid |
| **llm_name** | gemini-3.1-flash-lite | gemini-3.1-flash-lite | gemini-3.1-flash-lite |
| **query** | 實驗室的成員有哪些人？ | 實驗室的成員有哪些人？ | 實驗室的成員有哪些人？ |

### 評斷標準

| 指標 | 目標值 | 優先級 |
|------|--------|:------:|
| 成員覆蓋 | **≥ 10 位** | P0 |
| Top-1 Score | **≥ 0.35** | P0 |
| Faithfulness | 100% | P0 |
| Relevancy | 100% | P0 |

### 注意事項

- 每次實驗皆 force-rebuild（Milvus 強制完整重建路徑）
- 三組權重皆在單一 `exp.py` 批次執行，共用同一份 MilvusLite 實例
- 其他參數（`hybrid_top_k`、`similarity_top_k` 等）統一做為控制變數

---

## 實驗記錄（Q1：「實驗室的成員有哪些人？」）

### 實驗 B-1：weights=[1.0, 0.3]（基準）

| 指標 | 結果 |
|:------|:---:|
| **Top-1 Score** | 0.857（保留 cosine）✅ |
| **Score 範圍** | 0.622–0.857 |
| **成員覆蓋** | **12 位**（廖梓逸、簡資烜、張彣謙、李倬安、葉展維、張勛皓、孫詠淳、黃懷萱、龔若齊、簡國峻、沈哲寬、曾廷綸）✅ |
| **Faithfulness** | ✅ 100% |
| **Relevancy** | ✅ 100% |
| **執行時間** | 35.09 秒 |
| **回答結構化** | 僅條列人名 |
| **Sources 多樣性** | ✅ 涵蓋 `Letter to potential students`、`Join WIDM`、`Activities`、`Web Intelligence and Data Mining Lab`、`校外奬項` 等不同頁面 |

### 實驗 B-2：weights=[1.0, 0.5]

| 指標 | 結果 |
|:------|:---:|
| **Top-1 Score** | **0.997**（幾乎滿分）🥇 |
| **Score 範圍** | 0.622–0.997（上限明顯提升） |
| **成員覆蓋** | **12 位**（廖梓逸、簡資烜、張彣謙、李倬安、葉展維、張勛皓、孫詠淳、黃懷萱、龔若齊、簡國峻、沈哲寬、曾廷綸）✅ |
| **Faithfulness** | ✅ 100% |
| **Relevancy** | ✅ 100% |
| **執行時間** | **27.92 秒** 🥇 |
| **回答結構化** | ✅ **自動分組**：研究生（廖梓逸、簡資烜、張彣謙、黃懷萱、龔若齊、簡國峻）vs 專題生（李倬安、葉展維、張勛皓、孫詠淳、沈哲寬、曾廷綸） |
| **Sources 多樣性** | ✅ 涵蓋 `Letter to potential students`、`Join WIDM`、`Activities`、`Web Intelligence and Data Mining Lab`、`校外奬項` 等不同頁面 |

### 實驗 B-3：weights=[0.9, 0.3]

| 指標 | 結果 |
|:------|:---:|
| **Top-1 Score** | 0.792（較基準略降） |
| **Score 範圍** | 0.560–0.792（整體下修） |
| **成員覆蓋** | **12 位**（廖梓逸、簡資烜、張彣謙、李倬安、葉展維、張勛皓、孫詠淳、黃懷萱、龔若齊、簡國峻、沈哲寬、曾廷綸）✅ |
| **Faithfulness** | ✅ 100% |
| **Relevancy** | ✅ 100% |
| **執行時間** | 28.04 秒 🥈 |
| **回答結構化** | 僅條列人名 |
| **Sources 多樣性** | ✅ 涵蓋 `Letter to potential students`、`Join WIDM`、`Activities`、`Web Intelligence and Data Mining Lab`、`校外奬項` 等不同頁面 |

### 三種權重彙總比較

| 指標 | `[1.0, 0.3]`（基準） | `[1.0, 0.5]`（B-2） | `[0.9, 0.3]`（B-3） |
|:---|:---:|:---:|:---:|
| **Top-1 Score** | 0.857 | **0.997** 🥇 | 0.792 |
| **Score 範圍** | 0.622–0.857 | 0.622–**0.997** | 0.560–0.792 |
| **成員覆蓋** | **12 位** ✅ | **12 位** ✅ | **12 位** ✅ |
| **Faithfulness** | 100% | 100% | 100% |
| **Relevancy** | 100% | 100% | 100% |
| **執行時間** | 35.09s | **27.92s** 🥇 | 28.04s 🥈 |
| **回答結構化** | 僅條列人名 | ✅ 自動分研究生/專題生 | 僅條列人名 |

---

## 實驗總結

### 關鍵發現

#### 1. `[1.0, 0.5]` 全面勝出

所有量化指標上 `[1.0, 0.5]` 皆優於或持平其他兩組：

- **Top-1 Score 0.997**，幾乎滿分，表示適度提高 sparse 權重讓 BGE-M3 中文稀疏編碼有效輔助了 dense 檢索，將最相關節點推至首位
- **執行時間最快（27.92s）**，比基準快 7 秒
- **回答品質最佳**：LLM 自動將成員分類為「研究生」與「專題生」，隱含 dense 分數更高的節點提供了更豐富的上下文脈絡

#### 2. `[0.9, 0.3]` 反效果

降低 dense 權重（0.9）等同比例縮小了所有節點的 cosine 貢獻：

- Top-1 Score 從 0.857 降至 0.792，Score 上限從 0.857 降至 0.792
- 在 sparse 權重不變的前提下，減少 dense 貢獻只會讓整體分數下修，無正面效果
- 成員覆蓋雖維持 12 位，但分數緊縮意味著對邊界 case 的容忍度降低

#### 3. BGE-M3 sparse 的實際影響

對比三組結果，BGE-M3 中文稀疏編碼在 `weights=0.5` 時展現了正向貢獻：

- 中文關鍵字匹配（BGE-M3 神經稀疏編碼 vs Qdrant BM25）確實能補充 dense 檢索的不足
- 權重 0.3 時 sparse 貢獻幾乎無感（B-1 vs B-3 差異主要由 dense 權重變化造成）
- 權重 0.5 時 sparse 開始顯著拉抬 Top-1 Score，但未引入雜訊（Sources 多樣性不變）

### 三組權重性價比評分

| 面向 | `[1.0, 0.3]`（基準） | `[1.0, 0.5]`（B-2） | `[0.9, 0.3]`（B-3） |
|:---|:---:|:---:|:---:|
| 檢索品質 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 執行效率 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 回答品質 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **綜合評價** | **良好** | **最佳** 🏆 | **普通** |

`[1.0, 0.5]` 在所有面向取得最佳平衡，建議作為新的預設權重。`[0.9, 0.3]` 表現最差，不建議使用。


# 實驗三：hybrid_top_k 參數影響

## 動機

當前 `hybrid_top_k=10`，實驗 B 的 Top-1 Score 已達 0.857，但稀疏分支的候選數可能仍受限。調高 `hybrid_top_k` 可讓 sparse 分支貢獻更多優質候選。

## 測試配置（固定 WeightedRanker `[1.0, 0.5]`）

| 實驗 | `hybrid_top_k` | `similarity_top_k` | 預期影響 |
|:----:|:---:|:---:|---------|
| D-1 | 10 | 10 | ✅ 已完成 |
| D-2 | 20 | 10 | sparse 候選倍增，多樣性可能再提升 |
| D-3 | 30 | 10 | 極大化 sparse 貢獻 |

---

# 實驗四：五題全面驗證

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
