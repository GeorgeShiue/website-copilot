# winnow-md AB test 擴充任務清單（第二輪）

**日期**：2026-09-19

## 覆蓋矩陣

| Spec Ref | Tasks |
|---|---|
| FR-001 ~ FR-004 | T002 |
| FR-005, FR-006 | T003 |
| FR-007 | T005 |
| FR-008 | T006 |
| US1 | T002 |
| US2 | T003 |
| US3 | T005, T006 |
| US4 | T004, T007, T008 |

---

## Phase 1: 重跑與調查

- [x] T001: 依 `copilot/` 文件重跑一次 AB test（nculab，aggressiveness=0.5）並回報
  - 結果：`runs/20260919_150059/`，Token Reduction 12.2%、保留率 88.9%、排除 2 頁，與上次幾乎一致
  - Depends on: none

- [x] T004: 檢視被排除的 2 頁與 Token Reduction 最高的 5 頁，依 winnow 判定機制評估原因
  - 方式：重爬並輸出逐區塊 keep/drop、分數、原因；閱讀 `decide.py`、`signals/__init__.py`
  - 結果：見 `survey.md` 發現 1、2
  - Depends on: T001

## Phase 2: 報告與參數掃描

- [x] T002: 調整報告輸出 per FR-001 ~ FR-004
  - Files: `scripts/ab_test_winnow.py`
  - 移除 `_INTEGRATION_SUGGESTIONS`；章節順序改為 處理時間 → 排除頁面 → 評估指標 → Diff View；排序；新增 `_diff_block()`、`TOP_DIFF_PAGES = 5`
  - 驗證：`runs/20260919_151248/`
  - Depends on: T001

- [x] T003: 加入 aggressiveness 掃描 per FR-005, FR-006
  - Files: `scripts/ab_test_winnow.py`
  - `AGGRESSIVENESS_SWEEP = [0.1, 0.2, 0.3, 0.4, 0.5]`、`--aggressiveness`；`save_markdown_outputs()` 拆為 `save_baseline_outputs()` 與 `save_winnow_outputs()`；`generate_report()` 新增 `aggressiveness`、`group_dir` 參數；新增 `generate_summary()`
  - 驗證：`runs/20260919_152953/`
  - Depends on: T002

## Phase 3: 輸入公平性

- [x] T009: 釐清 baseline 與 winnow 的輸入是否已被自訂清理邏輯處理過
  - 結果：是。`_filter_crawl_results()` 已對 fit_markdown 呼叫過 `clean_markdown()`；見 `survey.md` 發現 3
  - Depends on: T003

- [x] T005: 改以原始 `crawl_result.markdown.fit_markdown` 為共同輸入 per FR-007
  - Files: `scripts/ab_test_winnow.py`
  - 新增 `_RawCapturingCrawler`；`crawl_nculab()` 回傳原始值；更新 docstring
  - 驗證：`runs/20260919_154116/`，`a0.5/winnow/` 有 18 個檔案仍含空錨點連結，baseline 為 0
  - Depends on: T009

## Phase 4: 跨站台驗證與結論

- [x] T007: 檢查 winnow 輸出的頁面元件文字殘留 per US4/AC1
  - 結果：`Google Sites`、`Report abuse` 在 46 頁殘留；空錨點 68 處；空清單標題 12 處；見 `survey.md` 發現 4
  - Depends on: T005

- [x] T006: 加入 `--config` 並以 ncucsie 跑一遍 per FR-008
  - Files: `scripts/ab_test_winnow.py`
  - `CONFIG_NAME` 改為 `DEFAULT_CONFIG_NAME`；`crawl_nculab()` 改名 `crawl_site(config_name)`；`generate_report()`、`generate_summary()` 新增 `config_name` 參數
  - 驗證：`runs/20260919_155255/`（204 頁）
  - Depends on: T005

- [x] T008: 綜合評估 winnow 能否取代 `exclude_words`，並比較 nculab 與 ncucsie per US4/AC2
  - 結果：不適合全面取代；見 `survey.md` 結論
  - Depends on: T006, T007

## 待辦（尚未執行）

- [ ] T010: 逐頁檢視 ncucsie 上 winnow 額外抓到的雜訊（各組 `report.md` diff view）
- [ ] T011: 評估「winnow 輸出再經 `clean_markdown`」的比較設計
- [ ] T012: 系統性人工比對 nculab 被移除區塊是否為重要內容

---

## 任務依賴圖

```
T001 ─► T004
  └──► T002 ─► T003 ─► T009 ─► T005 ─► T007 ─┐
                                  └──► T006 ──┴─► T008
```
