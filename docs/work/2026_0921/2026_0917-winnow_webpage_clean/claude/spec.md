# winnow-md AB test 擴充規格（第二輪）

## Overview

在 `copilot/` 第一輪 AB test 的基礎上擴充 `scripts/ab_test_winnow.py`：調整報告輸出以利人工判斷、支援多組 aggressiveness 掃描、以未清理的原始 fit_markdown 為共同輸入、支援指定站台設定，並用 nculab 與 ncucsie 對照，評估 winnow 是否能取代 `exclude_words`。

## Functional Requirements

- FR-001: 報告移除「代碼整合建議」章節
- FR-002: 報告章節順序為 處理時間 → 排除頁面 → 評估指標 → Diff View
- FR-003: 評估指標表依 Token Reduction 由高到低排序，`**Average**` 列保持在表尾
- FR-004: 報告最下方附 Token Reduction 最高 5 頁的 baseline → winnow unified diff view
- FR-005: 支援 aggressiveness 掃描，預設 `[0.1, 0.2, 0.3, 0.4, 0.5]`，可用 `--aggressiveness` 覆寫；網站只爬取一次
- FR-006: 輸出結構為 `runs/<timestamp>/ab_test_winnow/`：`baseline/`（各組共用）、`a<值>/{report.md, winnow/}`、`summary.md`（每組一行：平均 Token Reduction、平均 Content Retention、排除頁數、winnow 耗時）
- FR-007: baseline 與 winnow 的共同輸入為 `crawl_result.markdown.fit_markdown` 原始值（未經 `clean_markdown`）
  - baseline：`clean_markdown(raw_fit_markdown, exclude_words)`
  - winnow：`Winnow.clean_many(raw_fit_markdown)`，不先經過 `clean_markdown`
  - 404 排除與 dedup_key 去重沿用 `WebsiteCrawler` 正式流程
- FR-008: 支援 `--config <站台名稱>` 指定 `configs/website_crawler/` 下的設定，預設 `nculab`

## User Stories

### US1: 開發者從報告快速看出誤刪

作為開發者，我希望報告一開頭就看到耗時與被排除頁面，表格依減少率排序，並在最下方直接看到差異最大頁面的 diff，以判斷 winnow 是清了雜訊還是刪了正文。

**驗收標準：**
- AC1: Given 報告產出，Then 無整合建議章節，章節順序符合 FR-002
- AC2: Given 報告產出，Then 表格 Token Reduction 由高到低，最下方有前 5 頁 diff，且與表格前 5 名一致

### US2: 開發者比較不同 aggressiveness

**驗收標準：**
- AC1: Given 執行腳本，Then 爬取只發生一次，並產出每組 `a<值>/` 與 `summary.md`
- AC2: Given `summary.md`，Then 可一眼比較各組的平均減少率、保留率與排除頁數

### US3: 開發者做公平的取代性比較

**驗收標準：**
- AC1: Given 執行腳本，Then winnow 輸出仍含 `clean_markdown` 才會清掉的標記（如空錨點連結），證明其輸入為原始版本
- AC2: Given `--config ncucsie`，Then 腳本可在該站台完成同樣流程

### US4: 開發者判斷是否以 winnow 取代 `exclude_words`

**驗收標準：**
- AC1: Given 測試結果，Then 能量化 `exclude_words` 命中行、空錨點、空清單標題在 baseline 與 winnow 輸出中的殘留
- AC2: Given nculab 與 ncucsie 兩份結果，Then 能說明差異與結論

## Edge Cases

- 空頁面：baseline 或 winnow 輸出為空的頁面不納入統計，並列於排除頁面
- 內容稀少頁面：baseline 已被 `exclude_words` 濾到只剩數十字元時，winnow 可能整頁清空（ncucsie a=0.5 共 71 頁）
- ncucsie 的 `file_*` 附件頁 baseline 即為空，所有組都被排除

## Out of Scope

- 修改 `src/` 生產代碼（以 `_RawCapturingCrawler` 子類別在腳本內擷取原始值）
- `use_model`、`languages`、`drop_images` 參數掃描
- aggressiveness 低於 0.1 或高於 0.5 的測試
- 系統性人工標註被移除內容是否為雜訊

## Assumptions

- nculab 與 ncucsie 可正常連線爬取
- `PruningContentFilter` 屬於 fit_markdown 產生過程，兩條路徑共同承受，不在比較範圍

## Open Questions

- ncucsie 上 winnow 額外抓到、`exclude_words` 沒抓到的雜訊有多少？（需逐頁 diff）
- 要不要新增「winnow 輸出再經 `clean_markdown`」的比較，以抹平格式差異、讓 Content Retention 回到有意義的範圍？
- 若引入 winnow 作為可選後處理，是否設定站台層級開關？

## Implementation Status

**Date**: 2026-09-19

| Spec Ref | Status | 備註 |
|---|---|---|
| FR-001 ~ FR-004 | ✅ 完成 | 已在 `runs/20260919_151248/` 驗證 |
| FR-005, FR-006 | ✅ 完成 | 已在 `runs/20260919_152953/` 驗證 |
| FR-007 | ✅ 完成 | `runs/20260919_154116/`，`a0.5/winnow/` 有 18 個檔案仍含空錨點，baseline 為 0 |
| FR-008 | ✅ 完成 | `runs/20260919_155255/`（ncucsie） |

結論詳見 `survey.md` 與 `dev.md`。
