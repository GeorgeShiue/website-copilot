# winnow-md AB test 擴充實作日誌（第二輪）

## 實作紀錄

### [2026-09-19 15:00] T001：依 copilot 文件重跑 AB test
- 執行：`uv run python scripts/ab_test_winnow.py`（nculab，aggressiveness=0.5）
- 報告：`runs/20260919_150059/ab_test_winnow/report.md`
- 結果：爬到 47 頁（上次 52 頁；8 頁失敗、10 頁重複），45 頁有效、2 頁排除；Token Reduction 12.2%、Content Retention 88.9%、Noise Residual 37.8%；baseline 0.531s、winnow 0.282s
- 偏離 plan：無。指標未達預期（30–40%、>95%），與第一輪一致

### [2026-09-19 15:12] T002：調整報告輸出
- 修改：`scripts/ab_test_winnow.py`
  - 刪除 `_INTEGRATION_SUGGESTIONS` 與其附加程式碼
  - `generate_report()` 章節順序改為 處理時間 → 排除頁面 → 評估指標（Token Reduction 由高到低）→ Diff View
  - 新增 `_diff_block()`（`difflib.unified_diff`）、`TOP_DIFF_PAGES = 5`
  - `Speedup` 行僅在 `winnow_time > 0` 時輸出
- 驗證：`runs/20260919_151248/`，前 5 頁為 `publication_thesisadvised`、`news_校外奬項`、`projects_eventgo`、`publication_publication-by-year`、`publication`，與表格前 5 名一致
- 備註：此次 winnow 耗時（0.293s）與上次不同，判斷為機器負載波動

### [2026-09-19 15:20] T004：調查被排除與被大量清除的頁面
- 方式：重爬並存下逐區塊決策（分數、原因、notes）至 scratchpad；閱讀 winnow 原始碼
- 過程注意：腳本檔名不可命名為 `inspect.py`（遮蔽標準庫，造成循環 import 錯誤）
- 結果：見 `survey.md` 發現 1、2。兩個排除頁是「標題加一個清單」，清單被 `NAV_LINK_LIST` 或 `CITATION_LIST` 判為雜訊，標題再被 `EMPTY_SECTION` 移除；模板記憶在 47 頁中沒有觸發

### [2026-09-19 15:29] T003：加入 aggressiveness 掃描
- 修改：`scripts/ab_test_winnow.py`（見 tasks.md T003）
- 驗證：`runs/20260919_152953/`

  | a | Token Reduction | Content Retention | 排除頁數 |
  |---|---|---|---|
  | 0.1 | 3.9% | 96.5% | 1 |
  | 0.2 | 5.7% | 94.9% | 1 |
  | 0.3 | 5.7% | 94.9% | 1 |
  | 0.4 | 7.5% | 93.0% | 1 |
  | 0.5 | 12.2% | 88.9% | 2 |

- 觀察：只有 0.1 達到保留率 >95%；`news_校內奬項` 在所有組都被排除（`NAV_LINK_LIST` 加 `PAGE_CHROME` 約 0.8，需 aggressiveness <0.1）；`news_碩論口試` 在 ≤0.4 不再被排除，符合門檻推算；`projects_eventgo` 所有組都被清掉約 70%（`FOOTER_ZONE`、`SECTION_JUNK` 不受 aggressiveness 調控）
- 備註：a=0.1 耗時偏高，視為第一組的暖機時間

### [2026-09-19 15:35] T009：釐清輸入是否已被自訂邏輯處理
- 更正先前說法：曾說「crawler 的 fit_markdown 已濾掉共用導覽」，那是從「沒有 `TEMPLATE_REPEAT`」反推的推論，並非實測
- 查看 `website_crawler.py` 後確認：`PruningContentFilter(threshold=0.25)`（第 117–119 行）加 `clean_markdown()`（第 181–184 行）都在 winnow 之前；`labintro` 的輸入開頭已無 Google Sites 頂部選單
- 結論：第一輪實驗的 baseline 是 `clean_markdown` 連跑兩次，winnow 是第三層，比較設計無法回答「能否取代」。詳見 `survey.md` 發現 3
- 未確認：未拿到未經 pruning 的 `raw_markdown`，無法說 pruning 濾掉了多少

### [2026-09-19 15:41] T005：改以原始 fit_markdown 為共同輸入
- 修改：`scripts/ab_test_winnow.py`
  - 新增 `_RawCapturingCrawler(WebsiteCrawler)`：覆寫 `_filter_crawl_results()`，先呼叫 `super()`，再從 `filtered[k]["crawl_result"].markdown.fit_markdown` 記錄原始值
  - `crawl_nculab()` 改用該子類別，回傳 `{dedup_key: {"url", "fit_markdown": 原始值}}`，下游 `baseline_cleanup()`、`winnow_cleanup()` 不必改
  - 更新模組與函式 docstring，移除過時的「代碼整合建議」敘述
- 決策理由：不改 `src/`；沿用 crawler 的 404 排除與去重邏輯
- 驗證：`runs/20260919_154116/`；47 頁；`a0.5/winnow/` 有 18 個檔案仍含空錨點，baseline 為 0

  | a | Token Reduction | Content Retention | 排除頁數 |
  |---|---|---|---|
  | 0.1 | 8.4% | 107.5% | 0 |
  | 0.2 | 8.7% | 107.2% | 0 |
  | 0.3 | 8.7% | 107.2% | 0 |
  | 0.4 | 10.4% | 105.4% | 0 |
  | 0.5 | 10.6% | 105.2% | 0 |

- 偏離 plan：無
- 風險/備註：
  - Content Retention 超過 100%，因為 winnow 保留 baseline 已清掉的標記，此指標已不能當品質指標
  - 排除頁數變 0：`news_校內奬項` 不再輸出空白，改為保留率 9%（仍為嚴重誤刪）
  - 曾誤說「baseline 還有 4 個檔案含空錨點」，那是比對寫法不同；用 `clean_markdown` 自己的 pattern 計算為 0，已更正

### [2026-09-19 15:47] T007：頁面元件文字殘留檢查
- 方式：統計 `exclude_words` 命中行、空錨點、空清單標題在 baseline 與 winnow 輸出中的數量
- 結果（nculab）：baseline 全為 0；winnow a=0.1 為 94、69、12；a=0.5 為 92、68、12。殘留的 `exclude_words` 行只有 `Google Sites` 與 `Report abuse`（46 頁，位於每頁底部），其餘十個詞已在輸出中為 0 次
- 判斷：winnow 抓不到固定頁面元件文字與標記殘渣，調整 aggressiveness 幾乎無影響

### [2026-09-19 15:52] T006：加入 `--config` 並以 ncucsie 執行
- 修改：`scripts/ab_test_winnow.py`
  - 新增 `--config`（預設 `DEFAULT_CONFIG_NAME = "nculab"`）
  - `crawl_nculab()` 改名 `crawl_site(config_name)`
  - `generate_report()`、`generate_summary()` 新增 `config_name` 參數
- 驗證：`runs/20260919_155255/`，204 頁、每組 199 頁有效（a=0.5 為 128 頁）

  | a | Token Reduction | 排除頁數 | winnow 總字元數 |
  |---|---|---|---|
  | 0.1 | 37.8% | 5 | 374,705 |
  | 0.2 | 38.5% | 5 | — |
  | 0.3 | 64.2% | 5 | 218,486 |
  | 0.4 | 64.4% | 5 | — |
  | 0.5 | 47.7% | 76 | 203,180 |

  baseline 總字元數 180,020（a=0.5 那組因排除頁面為 176,105）。
- 觀察：
  - 平均 Content Retention（1440% 等）被 baseline 極短的頁面撐高，無意義，改看總字元數與中位數
  - 5 個 `file_*` 頁 baseline 即為空，所有組都被排除
  - a=0.5 時多出 71 頁被 winnow 清空，多為 `announcement_page_N_category_*`（baseline 約 53 字元）以及 `copyrights`、`students`
  - `exclude_words` 命中行殘留：baseline 0；winnow a=0.1 為 611；a=0.5 為 232（側欄公告連結、頁首 logo、`焦點新聞`、`前一頁`、`第一頁` 等）

### [2026-09-19 15:58] T008：綜合評估
- 結論：不適合以 winnow 全面取代 `exclude_words`／`clean_markdown`
- 依據：
  1. winnow 清不掉固定元件文字與空錨點（nculab、ncucsie 均如此）
  2. nculab 上對清單型正文誤刪；ncucsie 上 a=0.5 清空 71 頁
  3. `exclude_words` 是明確指定、行為可預期；winnow 依形狀猜測
- 例外：ncucsie 有真實跨頁模板，winnow 有實際去雜訊效果（Token Reduction 38–64%），適合作為 `clean_markdown` 之後的可選後處理，aggressiveness 建議 0.1–0.2，並人工檢查被移除的區塊
- 尚未驗證：見 `survey.md`「限制與未驗證項目」及 tasks.md T010–T012

---

## Final Summary

### 完成狀態

| 項目 | 狀態 |
|---|---|
| 報告調整（FR-001 ~ FR-004） | ✅ |
| aggressiveness 掃描（FR-005、FR-006） | ✅ |
| 原始 fit_markdown 為共同輸入（FR-007） | ✅ |
| `--config` 多站台（FR-008） | ✅ |
| nculab 與 ncucsie 對照與結論 | ✅ |
| 待辦 T010 ~ T012 | ⏳ 未執行 |

### 主要發現

1. 第一輪實驗的輸入已被 `clean_markdown` 處理過，比較設計有缺陷；第二輪已修正為共同使用原始 fit_markdown。
2. winnow 在 nculab 上主要誤刪清單型正文，對頁面元件文字與標記殘渣完全無效。
3. winnow 在 ncucsie 上有實際去雜訊效果，但仍不及 `exclude_words`，且 a=0.5 會清空內容稀少的頁面。
4. 現有的 `Content Retention` 與 `Noise Residual` 指標在原始輸入下不可靠。

### 執行紀錄

| 時間 | 目錄 | 內容 |
|---|---|---|
| 15:00 | `runs/20260919_150059/` | nculab a=0.5 重跑 |
| 15:12 | `runs/20260919_151248/` | 報告格式調整驗證 |
| 15:29 | `runs/20260919_152953/` | nculab 掃描（輸入已被清理過） |
| 15:41 | `runs/20260919_154116/` | nculab 掃描（原始輸入） |
| 15:52 | `runs/20260919_155255/` | ncucsie 掃描（原始輸入） |
