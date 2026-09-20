# winnow-md AB test 擴充實作計畫（第二輪）

## Overview

只修改 `scripts/ab_test_winnow.py`，不動 `src/`：調整報告輸出、加入 aggressiveness 掃描、改以原始 fit_markdown 為輸入、支援 `--config`，並以 nculab 與 ncucsie 對照。

## Architecture Decisions

| Decision | Choice | Rationale | Alternatives Considered |
|---|---|---|---|
| 報告 diff 形式 | `difflib.unified_diff`，行級，放在 ```` ```diff ```` 區塊 | 標準庫、Markdown 預覽會紅綠上色 | 並排 HTML、字元級 diff |
| 掃描值 | 0.1–0.5，間隔 0.1 | 使用者指定範圍；門檻公式顯示 ≤0.44 時 `CITATION_LIST` 單獨不會移除 | 0.0–0.7、加入 `use_model`、`languages`、`drop_images` |
| 輸出結構 | 一份 `summary.md` 加各組子目錄 | 只爬一次；baseline 各組相同，只存一份 | 只產總表 |
| 擷取原始 fit_markdown | 腳本內 `_RawCapturingCrawler(WebsiteCrawler)` 覆寫 `_filter_crawl_results()`，呼叫 `super()` 後從 `filtered[k]["crawl_result"]` 記錄 | 沿用 404 排除與 dedup；不改 `src/`；下游函式不需改 | 改 crawler 回傳結構、自行重建爬取流程（會複製 dedup 邏輯） |
| 站台選擇 | `--config` 參數，預設 `nculab`；`crawl_nculab()` 改名 `crawl_site(config_name)` | 同一腳本可跑多站台 | 每站台一支腳本 |

## Module Structure

```
scripts/ab_test_winnow.py          # 唯一修改的檔案

runs/<timestamp>/ab_test_winnow/
├── summary.md                     # 各 aggressiveness 總表
├── baseline/                      # 各組共用
└── a0.1/ … a0.5/
    ├── report.md
    └── winnow/
```

主要函式：`_RawCapturingCrawler`、`crawl_site()`、`baseline_cleanup()`、`winnow_cleanup()`、`save_baseline_outputs()`、`save_winnow_outputs()`、`calculate_metrics()`、`generate_report()`、`generate_summary()`。

## Data Flow

```
crawl_site(config)  ──►  {dedup_key: {url, fit_markdown(原始)}}    只執行一次
        │
        ├─► baseline_cleanup: clean_markdown(原始, exclude_words)   只執行一次
        │
        └─► for a in aggressiveness:
              winnow_cleanup(原始, a) ─► calculate_metrics ─► save_winnow_outputs
                                                            └► generate_report(a<值>/)
        └─► generate_summary
```

## Three-Tier Boundaries

### Always do
- 不修改 `src/`
- baseline 與 winnow 使用同一份原始 fit_markdown
- 每次重新爬取，頁數可能與前次略有差異

### Ask first
- 是否加入 `use_model`、`languages` 等其他 winnow 參數
- 是否新增「winnow 再經 `clean_markdown`」的比較

### Never do
- 不對 winnow 輸入先跑 `clean_markdown`（會回到原實驗設計缺陷）

## Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Content Retention 在原始輸入下超過 100% | 不能當品質指標 | 報告與結論標註，改看殘留雜訊與 diff |
| `Noise Residual` 用字串包含比對，baseline 經 mdformat 重排 | 指標失準 | 判斷時不採用，未改定義 |
| 首組（a=0.1）耗時偏高 | 耗時比較失真 | 視為暖機，不作結論依據 |

## Verification Approach

1. 執行 `uv run python scripts/ab_test_winnow.py`，檢查章節順序、排序、diff view
2. 確認爬取只出現一次、產生 5 組子目錄與 `summary.md`
3. 抽查 `a0.5/winnow/*.md` 仍含空錨點連結，證明輸入為原始版本
4. 以 `--config ncucsie` 重跑
5. 以腳本統計 `exclude_words` 命中行、空錨點、空清單標題在 baseline 與 winnow 的殘留
