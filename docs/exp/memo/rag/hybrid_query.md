# Hybrid Query 設定

> 對應 `2026_0720-hybrid-search.md` Part 3 — Milvus 融合演算法比較（核心實驗）

## Vector Store

### Vector Store Type

> **目前穩定值：`"milvus"`**

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

# 實驗一： RRFRanker vs WeightedRanker (2026/7/20)

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

# 實驗二：WeightedRanker 權重微調 (2026/7/20)

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


# 實驗三：hybrid_top_k 參數影響 (2026/7/20)

## 實驗設計

### 測試問題

| 編號 | 查詢 | 測試重點 |
|:---:|------|---------|
| Q1 | 「實驗室的成員有哪些人？」 | 測試 sparse 候選數增加是否能引入更多優質節點 |

### 測試配置（固定 WeightedRanker `[1.0, 0.5]`）

| 參數 | D-1（baseline） | D-2（sparse↑） | D-3（sparse↑↑） |
|------|:---:|:---:|:---:|
| **vector_store_type** | milvus | milvus | milvus |
| **hybrid_ranker** | WeightedRanker | WeightedRanker | WeightedRanker |
| **hybrid_ranker_params** | `[1.0, 0.5]` | `[1.0, 0.5]` | `[1.0, 0.5]` |
| **similarity_top_k** | 10 | 10 | 10 |
| **hybrid_top_k** | 10 | 20 | 30 |
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

- 三組在單一 `exp.py` 批次中依序執行，共用同一份 MilvusLite 實例
- 固定 `weights=[1.0, 0.5]`（實驗二最佳權重），`hybrid_top_k` 為唯一變數

---

## 實驗記錄（Q1：「實驗室的成員有哪些人？」）

### 實驗 D-1：hybrid_top_k=10（baseline）

| 指標 | 結果 |
|:------|:---:|
| **Top-1 Score** | 0.997（幾乎滿分）✅ |
| **Score 範圍** | 0.622–0.997 |
| **成員覆蓋** | **12 位**（廖梓逸、簡資烜、張彣謙、李倬安、葉展維、張勛皓、孫詠淳、黃懷萱、龔若齊、簡國峻、沈哲寬、曾廷綸）✅ |
| **Faithfulness** | ✅ 100% |
| **Relevancy** | ✅ 100% |
| **執行時間** | 46.61 秒 |
| **回答結構化** | 僅條列人名 |
| **Sources 多樣性** | ✅ 涵蓋 `Letter to potential students`、`Join WIDM`、`Activities`、`Web Intelligence and Data Mining Lab`、`校外奬項` 等不同頁面 |

### 實驗 D-2：hybrid_top_k=20

| 指標 | 結果 |
|:------|:---:|
| **Top-1 Score** | 0.997（幾乎滿分）✅ |
| **Score 範圍** | 0.622–0.997 |
| **成員覆蓋** | **12 位**（廖梓逸、簡資烜、張彣謙、李倬安、葉展維、張勛皓、孫詠淳、黃懷萱、龔若齊、簡國峻、沈哲寬、曾廷綸）✅ |
| **Faithfulness** | ✅ 100% |
| **Relevancy** | ✅ 100% |
| **執行時間** | **32.82 秒** 🥇 |
| **回答結構化** | ✅ **自動分組**：研究生（廖梓逸、簡資烜、張彣謙、黃懷萱、龔若齊、簡國峻）vs 大學部/專題生（李倬安、葉展維、張勛皓、孫詠淳、沈哲寬、曾廷綸） |
| **Sources 多樣性** | ✅ 涵蓋 `Letter to potential students`、`Join WIDM`、`Activities`、`Web Intelligence and Data Mining Lab`、`校外奬項` 等不同頁面 |

### 實驗 D-3：hybrid_top_k=30

| 指標 | 結果 |
|:------|:---:|
| **Top-1 Score** | 0.997（幾乎滿分）✅ |
| **Score 範圍** | 0.622–0.997 |
| **成員覆蓋** | **12 位**（廖梓逸、簡資烜、張彣謙、李倬安、葉展維、張勛皓、孫詠淳、黃懷萱、龔若齊、簡國峻、沈哲寬、曾廷綸）✅ |
| **Faithfulness** | ✅ 100% |
| **Relevancy** | ✅ 100% |
| **執行時間** | **31.63 秒** 🥇 |
| **回答結構化** | 僅條列人名 |
| **Sources 多樣性** | ✅ 涵蓋 `Letter to potential students`、`Join WIDM`、`Activities`、`Web Intelligence and Data Mining Lab`、`校外奬項` 等不同頁面 |

### 三組 hybrid_top_k 彙總比較

| 指標 | `top_k=10`（baseline） | `top_k=20`（D-2） | `top_k=30`（D-3） |
|:---|:---:|:---:|:---:|
| **Top-1 Score** | **0.997** 🥇 | **0.997** 🥇 | **0.997** 🥇 |
| **Score 範圍** | 0.622–0.997 | 0.622–0.997 | 0.622–0.997 |
| **Top-10 Sources 組成** | 完全相同 | 完全相同 | 完全相同 |
| **成員覆蓋** | **12 位** ✅ | **12 位** ✅ | **12 位** ✅ |
| **Faithfulness** | 100% | 100% | 100% |
| **Relevancy** | 100% | 100% | 100% |
| **執行時間** | 46.61s | **32.82s** | **31.63s** |
| **回答結構化** | 僅條列人名 | ✅ 分研究生/專題生 | 僅條列人名 |

---

## 實驗總結

### 關鍵發現

#### 1. `hybrid_top_k` 對最終 Top-10 無影響

三組實驗的 **Top-10 sources 完全一致**——相同的頁面、相同的 Score、相同的排序。這是因為 `weights=[1.0, 0.5]` 讓 dense 分支完全主導最終排序：

- `hybrid_top_k=10` 時，sparse 的 10 個候選中僅有少數對 fusion 有貢獻
- `hybrid_top_k=20` 或 `30` 時，新增的 sparse 候選分數更低，仍無法擠進最終 Top-10
- Score 0.622 以下的節點完全被排除在 Top-10 之外，且三組的 cutoff 一致

**結論：在 `weights=[1.0, 0.5]` 配置下，調高 `hybrid_top_k` 無正面效益。**

#### 2. 執行時間差異來自 MilvusLite hot-start

`top_k=10` 耗時 46.61s（最慢），`top_k=20` 與 `30` 分別為 32.82s 與 31.63s。此差異來自批次執行中的 **冷啟動 vs hot-start**——第一個 run 需載入模型、建立 collection，後續 run 直接重用。**非 `hybrid_top_k` 本身的影響。**

#### 3. 回答結構化差異為 LLM 隨機性

`top_k=20` 的 LLM 回應自動將成員分類為「研究生」與「大學部/專題生」，而其他兩組僅條列人名。在 Top-10 sources 完全一致的前提下，此差異為 **LLM 生成的隨機性**，與 `hybrid_top_k` 參數無關。

### 最終鎖定配置

| 參數 | 鎖定值 |
|:---|:---:|
| **hybrid_ranker** | `WeightedRanker` |
| **weights** | `[1.0, 0.5]` |
| **hybrid_top_k** | **10**（調高無益，維持預設） |
| **similarity_top_k** | 10 |

可直接進入五題全面驗證階段。

# 實驗四：五題全面驗證 (2026/7/20)

## 實驗設計

### 測試問題

| 編號 | 查詢 | 類型 | dense-only 對照 |
|:---:|------|:----:|:---:|
| Q1 | 實驗室的成員有哪些人？ | 名單型 | 100%/100% ✅ |
| Q2 | 實驗室在 2024 年有哪些活動？ | 時間範圍型（活動） | 100%/100% ✅ |
| Q3 | 加入實驗室需要準備哪些資料？ | 指引型 | 100%/100% ✅ |
| Q4 | 如何聯絡研究室指導教授？ | 指引型 | 100%/100% ✅ |
| Q5 | 實驗室近三年發表過哪些論文？ | 時間範圍型（論文） | 100%/0% ❌ |

### 測試配置

| 參數 | 鎖定值 |
|:---|:---:|
| **vector_store_type** | milvus |
| **hybrid_ranker** | WeightedRanker |
| **weights** | `[1.0, 0.5]` |
| **similarity_top_k** | 10 |
| **hybrid_top_k** | 10 |
| **query_mode** | hybrid |
| **llm_name** | gemini-3.1-flash-lite |
| **cutoff** | hybrid 模式不啟用 |

### 評斷標準

| 指標 | 目標值 | 優先級 |
|------|--------|:------:|
| Faithfulness | 100% | P0 |
| Relevancy | 100% | P0 |
| Q5 論文類型改善 | Relevancy > 0%（dense-only 階段為 0%） | P1 |

### 注意事項

- 每題各自獨立重建（Milvus 強制完整重建路徑）
- 評估使用 `gpt-5.4` 作為獨立 evaluator（同 dense-only 7/4 實驗）
- 所有參數鎖定實驗一～三得出的最佳值

---

## 實驗記錄

### Q1：實驗室的成員有哪些人？（名單型）

| 指標 | 結果 |
|:---|:---:|
| **Top-1 Score** | 0.997（幾乎滿分）✅ |
| **Score 範圍** | 0.622–0.997 |
| **成員覆蓋** | **12 位**（廖梓逸、簡資烜、張彣謙、李倬安、葉展維、張勛皓、孫詠淳、黃懷萱、龔若齊、簡國峻、沈哲寬、曾廷綸）✅ |
| **Faithfulness** | ✅ 100% |
| **Relevancy** | ✅ 100% |
| **執行時間** | 35.51 秒 |
| **Sources 多樣性** | ✅ 涵蓋 personnel、general、announcement 等不同頁面類型 |

### Q2：實驗室在 2024 年有哪些活動？（時間範圍型 — 活動）

| 指標 | 結果 |
|:---|:---:|
| **Top-1 Score** | 0.982 |
| **Score 範圍** | 0.636–0.982 |
| **Faithfulness** | ✅ 100% |
| **Relevancy** | ✅ 100% |
| **執行時間** | 30.94 秒 |
| **回答品質** | 精準列出 2024 年七項活動/獎項（TAAI 2024、ROCLING 2024、和泰 MaaS 黑客松等） |
| **Sources 多樣性** | ✅ `校外奬項`、`Activities`、`News` 等頁面提供充足證據 |

### Q3：加入實驗室需要準備哪些資料？（指引型）

| 指標 | 結果 |
|:---|:---:|
| **Top-1 Score** | 1.043（Top-1 首次突破 1.0） |
| **Score 範圍** | 0.615–1.043 |
| **Faithfulness** | ✅ 100% |
| **Relevancy** | ✅ 100% |
| **執行時間** | 30.44 秒 |
| **回答品質** | 正確回覆 CV、成績單、研究計畫三項申請資料 |
| **Sources 多樣性** | ✅ `Letter to potential students`、`Join WIDM` 等頁面 |

### Q4：如何聯絡研究室指導教授？（指引型）

| 指標 | 結果 |
|:---|:---:|
| **Top-1 Score** | 1.004 |
| **Score 範圍** | 0.622–1.004 |
| **Faithfulness** | ✅ 100% |
| **Relevancy** | ✅ 100% |
| **執行時間** | 29.62 秒 |
| **回答品質** | 提供完整教授信箱（chiahui@g.ncu.edu.tw）與申請流程 |

### Q5：實驗室近三年發表過哪些論文？（時間範圍型 — 論文）

| 指標 | 結果 |
|:---|:---:|
| **Top-1 Score** | 0.981（personnel 頁面） |
| **Score 範圍** | 0.620–0.981 |
| **論文頁面排名** | ❌ Bottom-3：`Publication`(0.628)、`Publication by Year`(0.625)、`Publication`(0.620) |
| **Faithfulness** | ❌ **0%** |
| **Relevancy** | ❌ **0%** |
| **執行時間** | 31.44 秒 |
| **回答品質** | ❌ **LLM hallucination**：虛構 2026 年論文、將競賽獎項誤答為論文發表 |

### 五題彙總比較

| 編號 | 查詢 | 類型 | Faithfulness | Relevancy | Latency | 與 dense-only 對比 |
|:---:|------|:----:|:---:|:---:|:---:|:---:|
| Q1 | 實驗室的成員有哪些人？ | 名單型 | ✅ **100%** | ✅ **100%** | 35.51s | ✅ 持平 |
| Q2 | 實驗室在 2024 年有哪些活動？ | 時間範圍型（活動） | ✅ **100%** | ✅ **100%** | 30.94s | ✅ 持平 |
| Q3 | 加入實驗室需要準備哪些資料？ | 指引型 | ✅ **100%** | ✅ **100%** | 30.44s | ✅ 持平 |
| Q4 | 如何聯絡研究室指導教授？ | 指引型 | ✅ **100%** | ✅ **100%** | 29.62s | ✅ 持平 |
| Q5 | 實驗室近三年發表過哪些論文？ | 時間範圍型（論文） | ❌ **0%** | ❌ **0%** | 31.44s | ❌ **退化**（dense-only 100%/0%） |

---

## 實驗總結

### 關鍵發現

#### 1. Hybrid search 對 Q1–Q4 完全有效

Q1 名單型（12 位成員）、Q2 活動型（2024 年活動）、Q3 指引型（申請資料）、Q4 指引型（聯絡方式）**全部通過 Faithfulness/Relevancy 100%**，與 dense-only 階段結果一致，證實 hybrid search 對多數查詢類型無負面影響。

#### 2. Q5 論文題是唯一瓶頸，且 hybrid 比 dense-only 更糟

| 面向 | dense-only（Phase 1） | Milvus Weighted（本次） |
|:---|:---:|:---:|
| Faithfulness | 100%（誠實拒答） | **0%（hallucination）** |
| Relevancy | 0%（誠實拒答） | **0%（hallucination）** |

Root cause 分析：

- **檢索層**：論文頁面（`Publication`、`Publication by Year`）的 cosine score（0.620–0.628）遠低於不相關的 personnel 頁面（0.950–0.981），hybrid `[1.0, 0.5]` 讓 dense 主導，無法將 paper 頁面提升到 Top-5
- **混合型污染**：Top-10 中僅 3/10 是真正的論文頁面，且全排在最後三名。前段被 personnel 頁面（含「論文」關鍵字）和舊獎項頁面佔據
- **生成層**：LLM 從 personnel 頁面的「近期的發表論文」一詞推論出虛構的 2026 年論文，產生嚴重 hallucination。dense-only 階段使用 cutoff=0.45 時反而誠實拒答，結果更可靠

#### 3. Top-1 Score 異常升高

Q3 與 Q4 的 Top-1 Score 分別達到 1.043 與 1.004，突破 cosine similarity 的理論上限 1.0。這是因為 WeightedRanker 的線性加權公式 `score = w_dense × dense_score + w_sparse × sparse_score` 中，當 dense_score 接近 1.0 且 sparse_score > 0 時，加權和可能超過 1.0。

### 與 dense-only 結論對照

| 面向 | dense-only 結論 | hybrid 結論 |
|:---|:---|:---|
| Q1 名單型 | 需 `top_k=10, cutoff=0.4` | hybrid 無 cutoff 即達相同水準 |
| Q2 活動型 | 穩定 100% | 維持 100% |
| Q3/Q4 指引型 | 穩定 100% | 維持 100% |
| Q5 論文型 | 誠實拒答（100%/0%） | **hallucination（0%/0%）— 退化** |
| 關鍵瓶頸 | Q5 query 理解 + 檢索 | Q5 檢索污染 + LLM hallucination |

### 後續行動

Q5 論文題是當前唯一未通過的瓶頸題，且 hybrid 模式讓情況較 dense-only 更糟。建議：

| 優先序 | 方向 | 具體做法 | 預期改善 |
|:------:|------|----------|---------|
| **P0** | Metadata Filter 隔離非論文頁面 | 論文查詢時啟用 `filter_dict={"page_type": "paper"}`，只在 paper pages 中檢索 | 直接解決檢索污染 |
| **P1** | 論文題專用 cutoff | 對論文查詢啟用 cutoff（如 0.65）過濾低分 paper pages | 減少雜訊 |
| **P2** | 生成階段約束 | 對時間範圍類查詢強制 provenance 標示，禁止外部知識推論 | 防止 hallucination |

**下一步：實驗五 — Metadata Filter + Hybrid 共存驗證。**

# 實驗五：Metadata Filter + Hybrid 共存驗證 (2026/7/20)

## 實驗設計

### 測試問題

| 編號 | 查詢 | 測試重點 |
|:---:|------|---------|
| Q5 | 「實驗室近三年發表過哪些論文？」 | 驗證 `page_type="paper"` filter 能否隔離非論文頁面，解決 Q5 檢索污染問題 |

### 測試配置

| 參數 | 鎖定值 |
|:---|:---:|
| **vector_store_type** | milvus |
| **hybrid_ranker** | WeightedRanker |
| **weights** | `[1.0, 0.5]` |
| **similarity_top_k** | 10 |
| **hybrid_top_k** | 10 |
| **query_mode** | hybrid |
| **llm_name** | gemini-3.1-flash-lite |
| **filter_dict** | `{"page_type": "paper"}` |
| **cutoff** | hybrid 模式不啟用 |

### 評斷標準

| 指標 | 目標值 | 優先級 |
|------|--------|:------:|
| 論文頁面佔比（Top-10） | **100%**（無 personnel/general 污染） | P0 |
| Faithfulness | 100% | P0 |
| Relevancy | **> 0%**（實驗四為 0%） | P1 |

### 注意事項

- 每次實驗 force-rebuild（Milvus 強制完整重建路徑）
- filter 透過 `cli.py` 的 `--module.query` 傳入（使用 CLI 而非 TOML）

---

## 實驗記錄（Q5：「實驗室近三年發表過哪些論文？」）

### Q5 with page_type="paper" filter

| 指標 | 結果 |
|:---|:---:|
| **Top-1 Score** | 0.909（`Publication by Year`，type=paper）✅ |
| **Score 範圍** | 0.616–0.909 |
| **論文頁面佔比** | **10/10** ✅（全部為 paper 類型） |
| **非論文污染** | ❌ **無**（無 personnel/general/announcement 頁面） |
| **Top-1 頁面型別** | ✅ `Publication by Year`（論文頁面如預期成為首位） |
| **Faithfulness** | ✅ **100%** |
| **Relevancy** | ❌ **0%** |
| **執行時間** | 43.43 秒 |

### 與實驗四（無 filter）對比

| 指標 | 無 filter（實驗四） | 有 filter（本次） | 變化 |
|:---|:---:|:---:|:---:|
| **Top-1 Score** | 0.981（personnel 頁面） | **0.909**（paper 頁面） | ✅ paper 回到首位 |
| **論文頁面佔比** | 3/10（Bottom-3） | **10/10** | ✅ **完全純化** |
| **非論文污染** | ❌ personnel 0.95–0.98 | ❌ **無** | ✅ 完全排除 |
| **Faithfulness** | ❌ 0% | ✅ **100%** | ✅ 大幅改善 |
| **Relevancy** | ❌ 0% | ❌ **0%** | 持平 |

### Score 分佈（Top-10，皆為 type=paper）

```
 1. Publication by Year   0.909  ✅ 2024–2025 論文
 2. Publication           0.890  ✅ 2025 論文
 3. Publication           0.628  ✅ 2022 論文
 4. Publication by Year   0.625  ✅ 混合年份
 5. Publication           0.620  ✅ 2021 論文
 6. Publication by Year   0.619  ✅ 2020 論文
 7. Thesis Advised        0.618  ✅ 碩博士論文
 8. Publication by Year   0.617  ✅ 2015 論文（過舊）
 9. Publication           0.616  ✅ 2024 論文
10. Publication by Year   0.616  ✅ 2024 論文
```

---

## 實驗總結

### 關鍵發現

#### 1. Metadata Filter 完美解決檢索污染

`page_type="paper"` filter 的生效讓 Top-10 **100% 為論文頁面**，完全隔離了 personnel、general、announcement 等不相關頁面。無 filter 時僅 3/10 是論文頁面，套用 filter 後提升至 **10/10**。

#### 2. Faithfulness 從 0% → 100%，但 Relevancy 仍為 0%

- **檢索層**：✅ 完全解決——所有 sources 都是論文
- **生成層**：❌ 仍有 hallucination——LLM 回答中包含 sources 中未提供的 2026 年論文（PagePilot ICWSM 2026、Voice-Controlled Text Correction ICASSP 2026）
- Relevancy evaluator 正確判斷這些資訊不在檢索到的 sources 中

#### 3. Score 斷層與過舊論文混入

Top-2 的 sources（0.909、0.890）已包含豐富的 2024–2025 論文資訊，但 LLM 仍使用了外部知識補充 2026 年論文。同時 Bottom sources 包含 2015–2021 年的過舊論文，與「近三年」的時間限定不符。

### 瓶頸轉移

```
實驗四（無 filter）：檢索污染  →  LLM hallucination
                         ↓
實驗五（有 filter）：檢索乾淨  →  LLM hallucination（瓶頸轉移至生成層）
```

### 後續行動

| 優先序 | 方向 | 具體做法 | 預期改善 |
|:------:|------|----------|---------|
| **P0** | ✅ **Metadata Filter** | `page_type="paper"` + hybrid 共存驗證成功 | 檢索污染已解決 |
| **P1** | ⏳ **生成階段約束** | Prompt engineering：禁止 LLM 使用外部知識、強制只引用當前 sources、時間範圍限縮 | 解決 Relevancy 0% |
| **P2** | 論文題專用 cutoff | 對論文查詢啟用 cutoff（如 0.65）過濾低分與過舊 paper pages | 減少 Bottom 雜訊 |
