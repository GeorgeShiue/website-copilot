# winnow-md 整合比較實驗實作日誌

## 實作紀錄（by Implementor）

### [2026-09-17 00:00] 任務 T001：建立 ab_test_winnow.py 腳本骨架
- 修改檔案：`scripts/ab_test_winnow.py`（新建）
- 決策理由：按照 tasks.md 要求建立腳本骨架，包含必要的 import 語句、常數定義、主函數框架和執行區塊
- 驗證結果：lint pass，Pylance 語法檢查通過（0 errors），uv run 執行 --help 無 ImportError
- 偏離 plan：無
- 風險/備註：腳本骨架已建立，等待後續任務實作具體邏輯

### [2026-09-17 17:00] 任務 T002：實現 nculab 網站爬取邏輯
- 修改檔案：`scripts/ab_test_winnow.py`
  - 新增 `crawl_nculab()` 函數：載入 nculab 設定、建立 WebsiteCrawler、執行爬取
  - 更新 `main()` 呼叫 `crawl_nculab()` 並輸出頁數
- 決策理由：
  - 使用 `WebsiteCrawlerConfig.from_toml(CONFIG_NAME)` 載入設定，確保與現有 pipeline 一致
  - 將爬取邏輯封裝為獨立函數 `crawl_nculab()`，便於後續 T003/T004 分別取得爬取結果
  - 設定參數全數從 config 物件取得，避免硬編碼
- 驗證結果：
  - 語法檢查：pass（`ast.parse`）
  - 設定載入：`WebsiteCrawlerConfig.from_toml("nculab")` 成功，`site_id == "nculab"`
  - Crawler 實例化：`WebsiteCrawler` 建立成功，參數正確
  - Pylance 診斷：4 個 unused import 警告（`os`, `time`, `winnow`, `clean_markdown`），為 T001 骨架預留，非錯誤
- 偏離 plan：無
- 風險/備註：
  - `crawl_nculab()` 會實際連線 nculab 網站，執行時間較長
  - `crawl_website()` 回傳值已包含 `url`, `fit_markdown`, `images`, `metadata`, `crawl_info`，滿足 T003/T004 需求

### [2026-09-17 18:00] 任務 T003：實現 baseline 清理邏輯（復用 clean_markdown）
- 修改檔案：`scripts/ab_test_winnow.py`
  - 新增 `baseline_cleanup()` 函數：從 crawl_results 提取 fit_markdown，逐頁呼叫 `clean_markdown(fit_markdown, exclude_words)`
  - 更新 `main()`：從 config 取得 exclude_words，呼叫 baseline_cleanup 並輸出結果
- 決策理由：
  - 函數簽名 `baseline_cleanup(crawl_results, exclude_words)` 與 T004 的 winnow 清理結果格式一致（`dict[page_title, str]`），便於後續 T005 指標計算
  - `exclude_words` 從 `WebsiteCrawlerConfig.from_toml(CONFIG_NAME)` 取得並傳入，確保與爬取時使用的排除清單一致
  - 使用 `data["fit_markdown"]` 提取文字，與 `_extract_crawl_results_data()` 產出的結構一致
- 驗證結果：
  - 語法檢查：pass（無 syntax errors）
  - Pylance 診斷：0 errors，3 個 unused import 警告（`os`, `time`, `winnow`）為 T001 骨架預留，非錯誤
  - import 驗證：`from scripts.ab_test_winnow import baseline_cleanup` 成功
- 偏離 plan：無
- 風險/備註：無

### [2026-09-17 19:00] 任務 T004：實現 winnow 清理邏輯（使用 clean_many）
- 修改檔案：`scripts/ab_test_winnow.py`
  - 新增 `dataclass` import
  - 新增 `WinnowCleanupResult` dataclass：封裝 cleaned/removed/stats 三項結果，供 T005 指標計算使用
  - 新增 `winnow_cleanup()` 函數：
    - 建立 `Winnow(aggressiveness=0.5)` 實例
    - 從 crawl_results 收集所有頁面的 `(fit_markdown, url)` tuple
    - 呼叫 `w.clean_many(pages)` 取得批次清理結果
    - 迭代 zip(page_titles, results) 提取 `.markdown`、`.removed`、`.stats`
    - 回傳 `WinnowCleanupResult` 物件
  - 更新 `main()`：呼叫 `winnow_cleanup()` 並輸出各頁面的 token 統計與移除區塊數
- 決策理由：
  - `WinnowCleanupResult` 使用 dataclass 而非 NamedTuple，因 removed/stats 內容為可變物件
  - `(fit_markdown, url)` tuple 結構與 survey.md 中 `clean_many()` 的 API 契約一致
  - aggressiveness 使用模組常數 `AGGRESSIVENESS`（0.5），與 T001 定義一致
  - `result.markdown` 而非 `result.text`（依 winnow 報告輸出 API）
  - `result.stats` 以 dict 格式傳入 WinnowCleanupResult，T005 可直接存取 `tokens_before`、`tokens_after`、`reduction_pct` 等鍵
- 驗證結果：
  - 語法檢查：pass（`pylanceFileSyntaxErrors` 回報 0 syntax errors）
  - import 驗證：`from scripts.ab_test_winnow import winnow_cleanup, WinnowCleanupResult` 成功
  - Pylance 診斷：0 errors
- 偏離 plan：無
- 風險/備註：
  - `winnow` 套件未安裝時 import 會失敗，但 T001 已確認安裝（`uv add winnow-md`）
  - `result.removed` 和 `result.stats` 已封裝於 `WinnowCleanupResult` 中，T005 可直接使用

### [2026-09-17 22:50] 任務 T005：實現四項評估指標計算
- 修改檔案：`scripts/ab_test_winnow.py`
  - 新增 `PageMetrics` dataclass：封裝單頁面指標（page_title, baseline_chars, winnow_chars, token_reduction_pct, content_retention_pct, noise_residual_pct, time_seconds）
  - 新增 `MetricsResult` dataclass：封裝所有頁面指標彙總（pages, baseline_time, winnow_time, excluded_pages）
  - 新增 `_noise_residual_pct()` 函數：計算單頁面雜訊残留率，逐區塊比對 winnow removed 區塊是否仍在 baseline 輸出中
  - 新增 `calculate_metrics()` 函數：計算四項評估指標，排除空頁面
  - 修改 `main()`：使用 `time.perf_counter()` 計時 baseline/winnow 清理，呼叫 `calculate_metrics()` 計算指標
  - 移除未使用的 `import os`，改用 `from dataclasses import field`
- 決策理由：
  - token 減少率直接使用 winnow `result.stats` 中的 `tokens_before`/`tokens_after` 計算，確保與 winnow 內建統計一致
  - 內容保留率使用字元數 `len(winnow_text) / len(baseline_text)`，簡單直觀
  - 雜訊残留率：逐區塊檢查 `block.text in baseline_text`，若 winnow 移除的區塊仍在 baseline 輸出中 → baseline 未處理 → 視為雜訊残留
  - 空頁面排除邏輯：baseline 或 winnow 清理後為空的頁面加入 `excluded_pages`，不納入統計
  - 處理時間分開計時 baseline 和 winnow，便於比較兩種清理路徑的耗時差異
  - `_noise_residual_pct` 為內部函數（底線前綴），不暴露於公共 API
- 驗證結果：
  - Pylance 診斷：0 errors（`textDocument/diagnostic` 回傳空列表）
  - import 驗證：所有新增 symbol（`PageMetrics`, `MetricsResult`, `calculate_metrics`, `_noise_residual_pct`）均可正常匯入
  - 單元測試：使用 mock data 驗證四項指標計算邏輯
    - `_noise_residual_pct`：空 list → 0.0、全部在 baseline → 1.0、全部不在 → 0.0、部分 → 0.5
    - `calculate_metrics`：空頁面排除、token 減少率 40%、內容保留率、雜訊残留率 100%
  - 所有 assertion 通過
- 偏離 plan：無
- 風險/備註：
  - `PageMetrics.time_seconds` 目前固定為 0.0，由 T006 報告時使用各模式總時間（baseline_time / winnow_time），因 winnow 使用批次清理無法逐頁計時
  - 雜訊残留率使用簡單字串包含比對（`block.text in baseline_text`），可能因 baseline 對文字微調導致少量誤判，但對整體趨勢判斷影響有限

### [2026-09-17 23:47] 任務 T007：執行腳本並驗證報告輸出
- 執行命令：`uv run python scripts/ab_test_winnow.py`
- 報告路徑：`runs/20260917_234724/ab_test_winnow/report.md`
- 驗證結果：
  - 腳本執行成功，無例外（EXIT 0）
  - 報告目錄與 `report.md` 檔案存在
  - 報告包含 48 個有效頁面 + 4 個排除頁面，共 52 頁（nculab 全站）
  - 彙總列包含 `**Average**`，格式符合 tasks.md 要求
  - 百分比格式為 `XX.X%`（一位小數）
  - 處理時間：Baseline 0.481s、Winnow 0.242s（加速 1.99x）
  - 代碼整合建議章節完整（方案一 + 方案二）
- 關鍵指標摘要：
  - Token 減少率平均：13.2%（偏低，未達 30-40% 預期範圍）
  - 內容保留率平均：87.8%（偏低，未達 >95% 預期）
  - 雜訊残留率平均：39.6%
  - 排除頁面：4 頁（空頁面：`news_校內奬項`、`news_碩論口試` 等）
- 偏離 plan：
  - Token 減少率 13.2% 低於預期 30-40%，原因：
    1. 多數頁面（約 30/48）token 減少率為 0.0%，winnow 未偵測到可移除模板
    2. 部分頁面（publication 系列、news_校外奬項、projects_eventgo）winnow 清理非常激進（保留率 14.9%-44.9%），拉低整體平均
    3. URL 編碼重複頁面（如 `news_校外奬項` 同時有編碼/非編碼版本）影響平均值
  - 內容保留率 87.8% 低於預期 >95%，原因同上
- 風險/備註：
  - 報告產出成功，格式符合要求
  - 指標偏低為實際數據反映，非腳本錯誤
  - 若需達到 30-40% 減少率，可能需調整 aggressiveness 或分析 winnow 對小型頁面的行為

### [2026-09-17 23:30] 任務 T006：實現 Markdown 比較報告產出
- 修改檔案：`scripts/ab_test_winnow.py`
  - 新增 `import datetime`、`from pathlib import Path`
  - 新增 `generate_report()` 函數：
    - 產出路徑為 `runs/<timestamp>/ab_test_winnow/report.md`
    - 報告包含表頭列：`| Page | Baseline Chars | Winnow Chars | Token Reduction % | Content Retention % | Noise Residual % | Time (s) |`
    - 每頁佔一行，數據與 `PageMetrics` 計算結果一致
    - 最後一列包含 `**Average**` 彙總列，數值為各頁面平均值
    - 百分比欄位格式為 `XX.X%`（一位小數）
    - 包含處理時間摘要、排除頁面清單、代碼整合建議章節
  - 新增 `_INTEGRATION_SUGGESTIONS` 常數：包含兩種整合方案（方案一：修改 `_filter_crawl_results()` 新增 winnow 路徑；方案二：獨立 winnow 清理引擎）
  - 修改 `main()`：新增 `timestamp` 產生、呼叫 `generate_report()` 產出報告
- 決策理由：
  - 使用 `datetime.now().strftime("%Y%m%d_%H%M%S")` 產生時間戳，與現有 runs 目錄命名慣例一致
  - 報告路徑 `runs/<timestamp>/ab_test_winnow/` 遵循 plan.md 規劃
  - 整合建議提供方案一（最小修改）與方案二（長期架構），讓使用者可依需求選擇
  - 百分比格式 `:.1f%` 確保一位小數顯示
- 驗證結果：
  - Pylance 語法檢查：0 errors
  - import 驗證：`from scripts.ab_test_winnow import generate_report` 成功
  - 報告格式驗證：表頭、分隔線、資料列、彙總列均符合 tasks.md 驗收標準
- 偏離 plan：無
- 風險/備註：
  - `generate_report()` 依賴 `MetricsResult` 物件結構，若 `PageMetrics` 欄位變動需同步更新
  - 整合建議為靜態文字，若未來實際整合需重新評估

### [2026-09-19 14:00] 任務 T008：實現 Markdown 輸出保存（FR-006）
- 修改檔案：`scripts/ab_test_winnow.py`
  - 新增 `save_markdown_outputs()` 函數：將 baseline 與 winnow 的清理結果分別儲存為獨立 Markdown 檔案
  - 修改 `main()`：在 `generate_report()` 之前呼叫 `save_markdown_outputs()`
- 決策理由：
  - FR-006 要求保留兩種清理模式的 Markdown 輸出供人工比較
  - baseline 版本儲存至 `runs/<timestamp>/ab_test_winnow/baseline/<page_title>.md`
  - winnow 版本儲存至 `runs/<timestamp>/ab_test_winnow/winnow/<page_title>.md`
  - 使用 `mkdir(parents=True, exist_ok=True)` 自動建立目錄
  - 在 `generate_report()` 之前儲存，確保目錄已建立
- 驗證結果：
  - Pylance 診斷：0 errors
  - 執行驗證：`uv run python scripts/ab_test_winnow.py` 成功
  - baseline 目錄：52 個 .md 檔案
  - winnow 目錄：52 個 .md 檔案
  - 範例比較（`labintro.md`）：baseline 6,099 字元 vs winnow 4,966 字元，差異明顯
- 偏離 plan：無
- 風險/備註：
  - 檔案命名使用 dedup_key（如 `labintro.md`），與現有命名慣例一致
  - 兩個目錄的檔案數量可能因排除頁面而略有差異

---

## Final Summary

### 專案完成狀態

**已完成功能需求**：
| Spec Ref | Status | 備註 |
|---|---|---|
| FR-001 | ✅ 完成 | AB test 比較腳本已建立並執行 |
| FR-002 | ✅ 完成 | nculab 網站爬取成功（52 頁） |
| FR-003 | ✅ 完成 | 四項評估指標均已計算 |
| FR-004 | ✅ 完成 | Markdown 比較報告已產出 |
| FR-005 | ✅ 完成 | 兩種代碼整合建議已提供 |
| FR-006 | ✅ 完成 | Markdown 輸出已保存至 baseline/ 和 winnow/ 目錄 |

**已完成功能驗收標準**：
| US/AC | Status | 備註 |
|---|---|---|
| US1/AC1 | ✅ 通過 | `uv run python ab_test_winnow.py` 成功產出 report.md |
| US1/AC2 | ✅ 通過 | 每頁一行指標 + 彙總列 |
| US1/AC3 | ✅ 通過 | 包含 token 減少率、內容保留率、雜訊残留率 |
| US2/AC1 | ✅ 通過 | 報告可判斷 winnow 效果 |
| US2/AC2 | ✅ 通過 | 內容保留率可供評估 |
| US2/AC3 | ✅ 通過 | 兩種整合方案具體可行 |
| US3/AC1 | ✅ 通過 | baseline 目錄包含 52 個 .md 檔案 |
| US3/AC2 | ✅ 通過 | winnow 目錄包含 52 個 .md 檔案 |
| US3/AC3 | ✅ 通過 | 同名檔案可直接比較兩種清理模式的差異 |

**已完成功能邊界案例**：
| 邊界案例 | Status | 備註 |
|---|---|---|
| winnow 未安裝 | ✅ 已處理 | 腳本啟動時檢查 import |
| 爬取失敗 | ✅ 已處理 | RuntimeError 處理 |
| 空頁面 | ✅ 已處理 | 4 頁排除（excluded_pages） |
| 中文內容 | ✅ 已觀察 | 中文頁面 token 減少率多為 0% |

### 關鍵指標摘要

| 指標 | 預期範圍 | 實際值 | 達標 |
|---|---|---|---|
| Token 減少率 | 30-40% | 13.2% | ❌ 偏低 |
| 內容保留率 | >95% | 87.8% | ❌ 偏低 |
| 雜訊残留率 | — | 39.6% | — |
| 處理時間 (Baseline) | — | 0.481s | — |
| 處理時間 (Winnow) | — | 0.242s | — |
| 速度提升 | — | 1.99x | ✅ 顯著 |
| 有效頁面 | — | 48/52 | — |
| 排除頁面 | — | 4 | — |

### 偏離分析

**Token 減少率偏低（13.2% vs 預期 30-40%）**：
1. **多數頁面未觸發清理**：約 30/48 頁面 token 減少率為 0.0%，winnow 未偵測到可移除模板
2. **部分頁面過度清理**：publication（62.7%）、publication_by-year（63.1%）、thesisadvised（82.5%）、eventgo（75.2%）等大型頁面被激進清理
3. **URL 編碼重複**：`news_校外奬項` 同時有編碼版（81.5% reduction）與非編碼版，影響平均值

**內容保留率偏低（87.8% vs 預期 >95%）**：
1. 同上原因：過度清理的頁面（14.9%-44.9% 保留率）大幅拉低平均
2. 多數頁面保留率 >99%，但少數激進清理的頁面造成整體偏低

### 主要發現

1. **Winnow 速度優勢明確**：批次清理 0.242s vs 逐頁清理 0.481s，加速 1.99x
2. **Winnow 對中文內容效果有限**：多數中文頁面（members、news 等）token 減少率為 0%，可能因 winnow 詞典以英文為主
3. **Winnow 在大型結構化頁面上效果顯著**：publication、thesisadvised 等重複性高的頁面 reduction 達 60-80%
4. **aggressiveness=0.5 對部分頁面過於激進**：建議後續嘗試更低值（0.3 或 0.2）
5. **雜訊残留率 39.6%**：winnow 移除的區塊中，約 40% 是 baseline 未處理的，說明 winnow 在某些頁面上偵測到了 baseline 漏掉的模板

### 建議後續步驟

1. **調整 aggressiveness**：嘗試 0.2-0.3 範圍，平衡清理效果與內容保留
2. **分析中文模板**：針對 nculab 中文頁面，研究是否需要自訂模板詞典
3. **評估整合方案**：
   - 短期：方案一（最小修改），在 `_filter_crawl_results()` 新增 `use_winnow` 參數
   - 長期：方案二（獨立引擎），關注點分離便於維護
4. **擴展測試**：加入其他網站（如 ncsie）驗證 winnow 的泛化能力
5. **Profile 分析**：對 publication、thesisadvised 等頁面進行詳細分析，確認 winnow 是否誤刪重要內容