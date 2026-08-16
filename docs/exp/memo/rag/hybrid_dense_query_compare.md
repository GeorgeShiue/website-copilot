# Dense vs Hybrid 橫向比較實驗 (2026/7/20)

> 對應 `2026_0720-dense-vs-hybrid-comparison` — 在相同 Milvus 向量庫上比較 dense-only 與 hybrid (WeightedRanker) 在五種問題類型的表現。

## 實驗動機

先前 Hybrid Query 實驗（實驗四～五）已分別驗證 hybrid search 與 metadata filter 的各自效果，但 **始終缺乏在同一基準下直接比較 dense-only 與 hybrid 的對照實驗**：

- `dense_query.md` 記錄了 Qdrant dense-only 的歷史結果（不同階段、不同設定）
- `hybrid_query.md` 記錄了 Milvus hybrid 的參數調優與五題驗證
- 兩者使用的 vector store 不同、cutoff 設定不同、甚至 rebuild 的資料版本可能不同

本次實驗在 **同一個批次、相同的 47 頁網頁資料、相同的 `text-embedding-3-small` embedding** 下，唯一變數為檢索策略（dense vs hybrid），以消除所有外部干擾。

## 實驗設計

### 測試問題

| 編號 | 查詢 | 類型 | 測試重點 |
|:---:|------|:----:|---------|
| Q1 | 實驗室的成員有哪些人？ | 名單型 | 成員列表完整度 |
| Q2 | 實驗室在 2024 年有哪些活動？ | 時間範圍型（活動） | 活動召回與摘要 |
| Q3 | 加入實驗室需要準備哪些資料？ | 指引型 | 明確資訊的穩定度 |
| Q4 | 如何聯絡研究室指導教授？ | 指引型 | 高確定性查詢 |
| Q5 | 實驗室近三年發表過哪些論文？ | 時間範圍型（論文） | 關鍵瓶頸題 |

### 測試配置

| 參數 | Dense | Hybrid |
|:---|:---:|:---:|
| **vector_store_type** | milvus | milvus |
| **query_mode** | `default` | `hybrid` |
| **hybrid_ranker** | —（不使用） | `WeightedRanker` |
| **hybrid_ranker_params** | — | `[1.0, 0.5]` |
| **similarity_top_k** | 10 | 10 |
| **hybrid_top_k** | — | 10 |
| **cutoff** | **0.4** | **不啟用**（hybrid mode 跳過） |
| **llm_name** | gemini-3.1-flash-lite | gemini-3.1-flash-lite |
| **embedding_name** | text-embedding-3-small | text-embedding-3-small |
| **chunk_size** | 800 | 800 |
| **force_rebuild** | ✅ 是（每題獨立） | ✅ 是（每題獨立） |

### 評斷標準

| 指標 | 目標值 | 優先級 |
|:---|:---|:---:|
| Faithfulness | 100% | P0 |
| Relevancy | 100% | P0 |
| Q5 論文類型改善 | Relevancy > 0%（dense-only 從未突破） | P1 |

### 注意事項

- 每題各自獨立 force-rebuild，DB 路徑完全分離（`milvus_dense_q*.db` vs `milvus_hybrid_q*.db`）
- 在同一次 `python exp.py` 批次中依序執行，共用同一份 `data/webpages/results/` 資料
- 評估模型使用 `gpt-5.4` 作為獨立 evaluator

---

## 實驗記錄（Q1：實驗室的成員有哪些人？）

### Dense（query_mode=default, cutoff=0.4）

| 指標 | 結果 |
|:---|:---:|
| **Top-1 Score** | 0.501（`Letter to potential students`） |
| **Score 範圍** | 0.404–0.501 |
| **成員覆蓋** | 13 位（張嘉惠教授、廖梓逸、簡資烜、張彣謙、李倬安、葉展維、黃懷萱、龔若齊、簡國峻、張勛皓、孫詠淳、沈哲寬、曾廷綸） |
| **Faithfulness** | ✅ 100% |
| **Relevancy** | ✅ 100% |
| **執行時間** | 38.09 秒 |
| **Sources** | Top-4 皆為 `Letter to potential students` 不同 chunk，`Score` 差距極小（0.501→0.471） |

### Hybrid（query_mode=hybrid, WeightedRanker [1.0, 0.5]）

| 指標 | 結果 |
|:---|:---:|
| **Top-1 Score** | **0.997**（`Letter to potential students`） |
| **Score 範圍** | **0.622–0.997** |
| **成員覆蓋** | **13 位**（同上，含張嘉惠教授） |
| **Faithfulness** | ✅ 100% |
| **Relevancy** | ✅ 100% |
| **執行時間** | **31.70 秒** |

### Q1 對比總結

| 指標 | Dense | Hybrid | 勝負 |
|:---|:---:|:---:|:---:|
| **Top-1 Score** | 0.501 | **0.997** | 🏆 Hybrid |
| **Score 範圍** | 0.404–0.501 | **0.622–0.997** | 🏆 Hybrid |
| **成員覆蓋** | 13 位 | 13 位 | 平手 |
| **Faithfulness** | 100% | 100% | 平手 |
| **Relevancy** | 100% | 100% | 平手 |
| **Latency** | 38.09s | **31.70s** | 🏆 Hybrid |

Dense 的 Top-1 Score 僅 0.501，且 Top-4 全部來自同一頁面的不同 chunk，Score 差距不到 0.03。Hybrid 的 BGE-M3 sparse 編碼將「成員」關鍵字匹配後，最相關節點被推至 0.997，同時保持來源多樣性。**最終答案相同，但 hybrid 的排序品質顯著優於 dense。**

---

## 實驗記錄（Q2：實驗室在 2024 年有哪些活動？）

### Dense（query_mode=default, cutoff=0.4）

| 指標 | 結果 |
|:---|:---:|
| **Top-1 Score** | 0.539（`Web Intelligence and Data Mining Lab`） |
| **Score 範圍** | 0.456–0.539 |
| **Faithfulness** | ✅ 100% |
| **Relevancy** | ✅ 100% |
| **執行時間** | 31.73 秒 |
| **回答品質** | 正確列出 2024 年八項活動與獎項（TAAI 2024、ROCLING 2024、和泰 MaaS 黑客松、InnoServe、中技社 AI 創意競賽、法律 x 法遵科技黑客松、Epoch School、AI 論壇） |

### Hybrid（query_mode=hybrid, WeightedRanker [1.0, 0.5]）

| 指標 | 結果 |
|:---|:---:|
| **Top-1 Score** | **0.982**（`Letter to potential students`） |
| **Score 範圍** | **0.636–0.982** |
| **Faithfulness** | ✅ 100% |
| **Relevancy** | ✅ 100% |
| **執行時間** | 32.32 秒 |
| **回答品質** | 同上，正確列出 2024 年七項活動與獎項 |

### Q2 對比總結

| 指標 | Dense | Hybrid | 勝負 |
|:---|:---:|:---:|:---:|
| **Top-1 Score** | 0.539 | **0.982** | 🏆 Hybrid |
| **Score 範圍** | 0.456–0.539 | **0.636–0.982** | 🏆 Hybrid |
| **Faithfulness** | 100% | 100% | 平手 |
| **Relevancy** | 100% | 100% | 平手 |
| **Latency** | 31.73s | 32.32s | 平手 |

兩者皆能正確回答 2024 年活動，hybrid 的 Score 顯著更高。2025 年 NSF HDR 活動雖出現在 sources 中但 LLM 正確過濾。**此題型不構成鑑別點。**

---

## 實驗記錄（Q3：加入實驗室需要準備哪些資料？）

### Dense（query_mode=default, cutoff=0.4）

| 指標 | 結果 |
|:---|:---:|
| **Top-1 Score** | 0.574（`Letter to potential students`） |
| **Score 範圍** | 0.484–0.574 |
| **Sources 數量** | **5**（cutoff=0.4 過濾後） |
| **Faithfulness** | ✅ 100% |
| **Relevancy** | ✅ 100% |
| **執行時間** | 30.55 秒 |
| **回答品質** | 正確回覆 CV、成績單、研究計畫三項申請資料 |

### Hybrid（query_mode=hybrid, WeightedRanker [1.0, 0.5]）

| 指標 | 結果 |
|:---|:---:|
| **Top-1 Score** | **1.043**（Score 突破 1.0，`Letter to potential students`） |
| **Score 範圍** | 0.615–1.043 |
| **Sources 數量** | **10**（無 cutoff 過濾） |
| **Faithfulness** | ✅ 100% |
| **Relevancy** | ✅ 100% |
| **執行時間** | 31.21 秒 |
| **回答品質** | 同上，正確回覆三項申請資料 |

### Q3 對比總結

| 指標 | Dense | Hybrid | 勝負 |
|:---|:---:|:---:|:---:|
| **Top-1 Score** | 0.574 | **1.043** | 🏆 Hybrid |
| **Sources 數量** | 5 | **10** | 🏆 Hybrid |
| **Faithfulness** | 100% | 100% | 平手 |
| **Relevancy** | 100% | 100% | 平手 |
| **Latency** | **30.55s** | 31.21s | 平手 |

Dense 的 cutoff=0.4 過濾掉 5 個來源，但剩餘 5 個已足夠回答。Hybrid 無 cutoff，帶回 10 個完整 sources。兩者答案一致，但 hybrid 的 sources 多樣性對更複雜的指引型問題可能更具優勢。

> **注意**：Hybrid 的 Top-1 Score 為 1.043，突破 cosine similarity 理論上限 1.0。這是 WeightedRanker 線性加權公式 `score = w_dense × dense_score + w_sparse × sparse_score` 中，dense_score 接近 1.0 且 sparse_score > 0 時的正常現象。

---

## 實驗記錄（Q4：如何聯絡研究室指導教授？）

### Dense（query_mode=default, cutoff=0.4）

| 指標 | 結果 |
|:---|:---:|
| **Top-1 Score** | 0.564（`Letter to potential students`） |
| **Score 範圍** | 0.402–0.564 |
| **Faithfulness** | ✅ 100% |
| **Relevancy** | ✅ 100% |
| **執行時間** | 32.04 秒 |
| **回答品質** | 提供完整教授信箱（chiahui@g.ncu.edu.tw）與申請流程 |

### Hybrid（query_mode=hybrid, WeightedRanker [1.0, 0.5]）

| 指標 | 結果 |
|:---|:---:|
| **Top-1 Score** | **1.004** |
| **Score 範圍** | 0.622–1.004 |
| **Faithfulness** | ✅ 100% |
| **Relevancy** | ✅ 100% |
| **執行時間** | 32.51 秒 |
| **回答品質** | 同上，含信箱與申請流程 |

### Q4 對比總結

| 指標 | Dense | Hybrid | 勝負 |
|:---|:---:|:---:|:---:|
| **Top-1 Score** | 0.564 | **1.004** | 🏆 Hybrid |
| **Score 範圍** | 0.402–0.564 | **0.622–1.004** | 🏆 Hybrid |
| **Faithfulness** | 100% | 100% | 平手 |
| **Relevancy** | 100% | 100% | 平手 |
| **Latency** | 32.04s | 32.51s | 平手 |

此題型檢索難度低，dense 即使 cutoff=0.4 仍能 recall 到 `Advisor` 頁面（score 0.414），兩者皆正確回答。**非鑑別點。**

---

## 實驗記錄（Q5：實驗室近三年發表過哪些論文？）

### Dense（query_mode=default, cutoff=0.4）

| 指標 | 結果 |
|:---|:---:|
| **Top-1 Score** | 0.447（`校外奬項`，type=announcement） |
| **Score 範圍** | 0.412–0.447 |
| **論文頁面數** | **2/9**：`Publication`(0.426, 第 3 名)、`Publication by Year`(0.413, 第 9 名) |
| **非論文污染** | ❌ 前 2 名為 award pages，中間混入 personnel pages |
| **Faithfulness** | ❌ **0%** |
| **Relevancy** | ❌ **0%** |
| **執行時間** | 33.14 秒 |
| **LLM 行為** | ❌ **Hallucination**：虛構 PagePilot ICWSM 2026、Voice-Controlled Text Correction ICASSP 2026 |

### Hybrid（query_mode=hybrid, WeightedRanker [1.0, 0.5]）

| 指標 | 結果 |
|:---|:---:|
| **Top-1 Score** | **0.981**（`Letter to potential students`，type=personnel） |
| **Score 範圍** | 0.620–0.981 |
| **論文頁面數** | **3/10**：`Publication`(0.628, 第 5 名)、`Publication`(0.620, 第 9 名)、`Publication by Year`(0.625, 第 10 名) |
| **非論文污染** | ❌ Top-4 皆為 personnel/general 頁面 |
| **Faithfulness** | ❌ **0%** |
| **Relevancy** | ❌ **0%** |
| **執行時間** | 31.60 秒 |
| **LLM 行為** | ❌ **Hallucination**：同上——虛構 2026 論文、將競賽獎項誤答為論文發表 |

### Q5 對比總結

| 指標 | Dense | Hybrid | 勝負 |
|:---|:---:|:---:|:---:|
| **Top-1 Score** | 0.447 | **0.981** | 🏆 Hybrid |
| **論文頁面數** | **2/9** | **3/10** | 🏆 Hybrid |
| **論文頁面 Score** | 0.426, 0.413 | **0.628, 0.625, 0.620** | 🏆 Hybrid |
| **Faithfulness** | 0% | 0% | 平手（皆失敗） |
| **Relevancy** | 0% | 0% | 平手（皆失敗） |
| **Latency** | 33.14s | **31.60s** | 平手 |

### Q5 關鍵診斷

**這是五題中唯一的瓶頸題，且兩種策略皆無法解決。** 核心問題不在檢索策略切換（dense → hybrid），而在以下兩層：

#### 檢索層：Paper pages 永遠被淹沒

| 策略 | Paper pages 最高分 | Personnel 最高分 | 差距 |
|:---|:---:|:---:|:---:|
| Dense | **0.426**（第 3 名） | 0.447（第 1 名） | ❌ paper 在後 |
| Hybrid | **0.628**（第 5 名） | 0.981（第 1 名） | ❌ paper 被推到更後面 |

Hybrid 雖然提升了 paper pages 的絕對分數（0.413→0.628），但 **personnel 頁面的提升幅度更大**（0.447→0.981），導致 paper pages 的排名從 dense 的第 3 名後退到 hybrid 的第 5 名。

#### 生成層：LLM 對「論文」query 的 hallucination

兩者都產生了完全相同的虛構論文：
- **PagePilot: web assistant based on natural language**（聲稱 ICWSM 2026）
- **Voice-Controlled Text Correction System for Chinese ASR Errors**（聲稱 ICASSP 2026）

這些資訊**不存在於任何檢索到的 sources 中**。LLM 從 `Letter to potential students` 中的「近期的發表論文」一詞自行推論生成。dense 在早期實驗（cutoff=0.45, top_k=5）曾因檢索更差而誠實拒答（Faithfulness 100%），但換到 top_k=10 後反而 hallucination——**更多 sources 不等於更正確的答案，尤其是當 sources 不包含真正需要的資訊時**。

---

## 五題彙總比較

| 題號 | 類型 | Dense Faith | Dense Rel | Hybrid Faith | Hybrid Rel | 勝負 |
|:---:|:----:|:----------:|:--------:|:-----------:|:---------:|:----:|
| **Q1** | 名單型 | ✅ 100% | ✅ 100% | ✅ 100% | ✅ 100% | 平手 |
| **Q2** | 時間範圍型（活動） | ✅ 100% | ✅ 100% | ✅ 100% | ✅ 100% | 平手 |
| **Q3** | 指引型 | ✅ 100% | ✅ 100% | ✅ 100% | ✅ 100% | 平手 |
| **Q4** | 指引型 | ✅ 100% | ✅ 100% | ✅ 100% | ✅ 100% | 平手 |
| **Q5** | 時間範圍型（論文） | ❌ 0% | ❌ 0% | ❌ 0% | ❌ 0% | 平手（皆失敗） |

### 量化指標對照

| 面向 | Dense | Hybrid | 勝負 |
|:---|:---:|:---:|:---:|
| **平均 Top-1 Score** | 0.525 | **0.969** | 🏆 Hybrid |
| **Q1 Score 範圍** | 0.404–0.501 | **0.622–0.997** | 🏆 Hybrid |
| **Q2 Score 範圍** | 0.456–0.539 | **0.636–0.982** | 🏆 Hybrid |
| **Q3 Score 範圍** | 0.484–0.574 | **0.615–1.043** | 🏆 Hybrid |
| **Q4 Score 範圍** | 0.402–0.564 | **0.622–1.004** | 🏆 Hybrid |
| **Q5 Score 範圍** | 0.412–0.447 | **0.620–0.981** | 🏆 Hybrid |
| **平均 Latency** | 33.11s | **31.87s** | 🏆 Hybrid |
| **cutoff 調參需求** | ✅ 需手動調 | ❌ 無需 | 🏆 Hybrid |
| **Q5 論文題** | ❌ 未解決 | ❌ 未解決 | 平手 |

---

## 實驗總結

### 關鍵發現

#### 1. Evaluation 面上兩者完全打平

在五題的 Faithfulness / Relevancy 上，dense 和 hybrid 沒有任何差異。兩者都在 Q1–Q4 取得 100%，都在 Q5 取得 0%。**若只看評估分數，無法區分兩者優劣。**

#### 2. Score 品質 hybrid 明顯優於 dense

| 面向 | Dense | Hybrid |
|:---|:---:|:---:|
| **Top-1 Score 型態** | 扁平（0.4–0.6） | **尖銳（0.9–1.0）** |
| **相關/不相關區分度** | 模糊（Score 差距 < 0.1） | **明確（Score 差距 > 0.3）** |
| **來源排序** | cutoff 後勉強排序 | fusion 演算法自動排序 |

Dense 的 Score 範圍極度壓縮（0.40–0.57），最高分與最低分之間的差距不到 0.2，cutoff 參數微調就會大幅影響結果。Hybrid 的 Score 健康分布在 0.62–1.04，最高分與最低分差距達 0.4，排序信賴度更高。

#### 3. Q5 論文題是唯一真正的瓶頸

**無論 dense 或 hybrid，Q5 都失敗。** Hybrid 甚至因為 Top-1 Score 極高（0.981）的 personnel 頁面排擠了 paper pages 的排名，讓 paper pages 從 dense 的第 3 名退到 hybrid 的第 5 名。

| 策略 | Paper 最高 Score | Paper 最佳排名 | 結果 |
|:---|:---:|:---:|:---:|
| Dense (cutoff=0.4) | 0.426 | 🥉 第 3 名 | ❌ Hallucination |
| Hybrid (Weighted [1.0, 0.5]) | 0.628 | 🏅 第 5 名 | ❌ Hallucination |
| **Hybrid + Metadata Filter (實驗五)** | **0.909** | **🥇 第 1 名** | ✅ Faith 100%, Rel 0% |

實驗五（`hybrid_query.md`）已經證明 Metadata Filter 能解決檢索污染（paper pages 回到第 1 名、Faithfulness 100%），但生成層的 hallucination 仍需獨立處理。

#### 4. hybrid 無 cutoff 的優勢

Dense 的 cutoff=0.4 是經驗值，需要大量實驗調參才能在「召回不足」和「雜訊過多」之間取得平衡。Hybrid 完全不使用 cutoff，依賴 `WeightedRanker` 的融合分數自然排序，**省去一個維度的調參成本**。

### 綜合建議

| 優先序 | 建議 | 理由 |
|:------:|------|------|
| **P0** | **採用 Hybrid 作為預設檢索策略** | Q1–Q4 持平，但 Score 品質、來源多樣性、無 cutoff 調參煩惱皆優於 dense |
| **P1** | **Q5 需專項處理，非策略切換可解** | 檢索層改用 Metadata Filter（實驗五已验证）；生成層需 prompt engineering 約束 LLM 禁止外部知識推論 |

### 最終鎖定配置

| 參數 | 值 |
|:---|:---:|
| **vector_store_type** | milvus |
| **hybrid_ranker** | WeightedRanker |
| **weights** | `[1.0, 0.5]` |
| **similarity_top_k** | 10 |
| **hybrid_top_k** | 10 |
| **query_mode** | hybrid |
| **cutoff** | 不啟用 |
| **llm_name** | gemini-3.1-flash-lite |
| **embedding_name** | text-embedding-3-small |
| **chunk_size** | 800 |
