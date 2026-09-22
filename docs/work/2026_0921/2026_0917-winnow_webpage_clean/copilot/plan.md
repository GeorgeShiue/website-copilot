# winnow-md 整合比較實驗實作計畫

## Overview

建立 AB test 腳本比較 `winnow-md` 的 `clean_many()` 批次清理與現有 `clean_markdown()` 的清理效果差異。以 nculab 網站為測試目標，評估 token 減少量、內容保留率、雜訊残留率及處理時間，產出比較報告與代碼整合建議。

## Architecture Decisions

| Decision | Choice | Rationale | Alternatives Considered |
|---|---|---|---|
| AB test 腳本位置 | `scripts/ab_test_winnow.py` | 與 `scripts/multi_site.py` 同層，便於重複執行；結果仍產出至 `runs/<timestamp>/` | `runs/<timestamp>/` (腳本與結果混在一起) |
| 比較模式 | 兩階段：baseline vs winnow | 直接比較兩種清理路徑的差異，符合 spec 要求 | 三階段串接（但 spec 要求比較差異） |
| Token 計算方式 | winnow 內建統計（需安裝 `winnow[tokens]` extra） | user 選擇，winnow 已內建 token 計算 | 簡單字數統計（但 user 選擇 winnow 內建） |
| aggressiveness | 預設 0.5 | user 選擇，survey.md 建議 | 測試多個值（但 user 選擇僅用預設） |
| 雜訊残留率計算 | 比對 winnow removed 與 baseline 輸出 | 定義明確：winnow 多移除的 = baseline 未處理的 | 人工標註（不可擴展） |

## Module Structure

```
scripts/
└── ab_test_winnow.py      # 主腳本：爬取 + 比較 + 報告

runs/<timestamp>/ab_test_winnow/
├── report.md              # 比較報告（腳本自動產出）
├── baseline/              # baseline 清理結果（FR-006）
│   ├── labintro.md
│   ├── advisor.md
│   └── ...
└── winnow/                # winnow 清理結果（FR-006）
    ├── labintro.md
    ├── advisor.md
    └── ...
```

**不建立獨立模組**：本實驗為一次性比較腳本，不修改 `src/` 下的生產代碼。腳本直接匯入現有模組：

- `src/app/engines/website_crawler.py` → `WebsiteCrawler`
- `src/utils/markdown_cleaner.py` → `clean_markdown`
- `winnow` → `Winnow.clean_many()`

## Data Flow

```
1. 爬取 nculab 網站
   └─> crawl_results: list[CrawlResult]
   └─> 使用 WebsiteCrawlerConfig("nculab") 載入設定

2. Baseline 路徑（現有行為）
   └─> 逐頁呼叫 clean_markdown(fit_markdown, exclude_words)
   └─> baseline_results: dict[page_title, str]

3. Winnow 路徑（新行為）
   └─> 收集所有 fit_markdown → list[tuple[str, str]]
   └─> Winnow(aggressiveness=0.5).clean_many(pages)
   └─> winnow_results: dict[page_title, str]

4. 指標計算（逐頁 + 彙總）
   └─> token 減少率: winnow.stats["reduction_pct"]
   └─> 內容保留率: len(winnow_text) / len(baseline_text)
   └─> 雜訊残留率: winnow.removed 中 baseline 未處理的比例
   └─> 處理時間: time.perf_counter() 差值

5. Markdown 輸出保存（FR-006）
   └─> baseline/<page_title>.md: baseline 清理後的 Markdown
   └─> winnow/<page_title>.md: winnow 清理後的 Markdown

6. 報告產出
   └─> report.md: 每頁一行指標 + 彙總列
```

## API Contracts

### 輸入

- 爬取目標：nculab 網站（`configs/website_crawler/nculab.toml`）
- 設定檔路徑：`configs/website_crawler/nculab.toml`

### 輸出

- `report.md`：Markdown 格式比較報告
- `baseline/<page_title>.md`：baseline 清理後的 Markdown（FR-006）
- `winnow/<page_title>.md`：winnow 清理後的 Markdown（FR-006）
- 指標表格格式：

```markdown
| Page | Baseline Chars | Winnow Chars | Token Reduction % | Content Retention % | Noise Residual % | Time (s) |
|------|----------------|--------------|-------------------|---------------------|------------------|----------|
| page1 | 5000 | 3200 | 36.0% | 99.5% | 2.1% | 0.12 |
| ... | ... | ... | ... | ... | ... | ... |
| **Average** | **4756** | **3043** | **36.0%** | **99.3%** | **1.8%** | **0.11** |
```

## Integration Points

### winnow-md 整合

```python
import winnow

# 建立 Winnow 實例（Template Memory 跨頁面學習）
w = winnow.Winnow(aggressiveness=0.5)

# 收集所有頁面的 fit_markdown
pages = [(fit_markdown, url) for url, fit_markdown in ...]

# 批次清理
results = w.clean_many(pages)

# 存取結果
for page_title, result in zip(page_titles, results):
    cleaned_text = result.markdown
    removed_blocks = result.removed
    stats = result.stats
```

### 現有 clean_markdown 整合

```python
from utils.markdown_cleaner import clean_markdown

# 逐頁清理（baseline）
cleaned = clean_markdown(fit_markdown, exclude_words=exclude_words)
```

## Three-Tier Boundaries

### Always do（架構不變式）

- 使用 `uv run python scripts/ab_test_winnow.py` 執行腳本
- 報告產出至 `runs/<timestamp>/ab_test_winnow/report.md`
- Markdown 輸出保存至 `runs/<timestamp>/ab_test_winnow/baseline/` 和 `runs/<timestamp>/ab_test_winnow/winnow/`（FR-006）
- 使用 nculab 設定檔（`configs/website_crawler/nculab.toml`）
- winnow 僅使用 heuristics 模式（不安裝 model extra）
- aggressiveness 使用預設值 0.5

### Ask first（需人工決策）

- 若 winnow 對中文效果差，是否調整 aggressiveness？
- 若雜訊残留率過高，是否進一步優化？

### Never do（架構禁止）

- 不修改 `src/` 下的生產代碼
- 不安裝 winnow model extra
- 不使用串流清理（僅批次處理）
- 不測試其他網站（僅 nculab）

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| winnow 對中文效果差 | 雜訊残留率指標失真 | Medium | 觀察雜訊残留率，報告中特別標註中文頁面 |
| 爬取失敗 | 無法執行比較 | Low | 腳本檢查網路連線，使用現有 fallback 設定 |
| Token 計算不一致 | 指標不可比 | Low | 使用 winnow 內建統計，確保一致性 |
| winnow 未安裝 | 腳本無法執行 | Low | 腳本啟動時檢查，提示安裝指令 |
| 空頁面 | 指標計算錯誤 | Medium | 排除清理後為空的頁面 |

## Verification Approach

1. **功能驗證**：執行 `uv run python scripts/ab_test_winnow.py`，確認產出 `runs/<timestamp>/ab_test_winnow/report.md`
2. **指標驗證**：檢查報告中四項指標是否合理（token 減少率 30-40%、內容保留率 >95%）
3. **邊界驗證**：檢查空頁面是否正確排除、winnow 未安裝時是否提示安裝
4. **整合驗證**：根據報告中的整合建議，評估是否值得整合至生產環境

## Implementation Steps

1. 安裝 winnow-md：`uv add winnow-md`
2. 建立 `scripts/ab_test_winnow.py`
3. 實現爬取邏輯（復用 WebsiteCrawler）
4. 實現 baseline 清理（復用 clean_markdown）
5. 實現 winnow 清理（使用 clean_many）
6. 實現指標計算（token 減少率、內容保留率、雜訊残留率、處理時間）
7. 實現 Markdown 輸出保存（FR-006）：將 baseline 和 winnow 的清理結果分別儲存至 `baseline/` 和 `winnow/` 目錄
8. 實現報告產出（Markdown 格式，產出至 `runs/<timestamp>/ab_test_winnow/report.md`）
9. 執行腳本並產出報告

## Implementation Notes

**Completion Date**: 2026-09-17

### 執行結果

- 報告路徑：`runs/20260917_234724/ab_test_winnow/report.md`
- 有效頁面：48/52（4 頁排除）
- Baseline 耗時：0.481s
- Winnow 耗時：0.242s（1.99x 加速）

### 指標偏離

| 指標 | 預期 | 實際 | 偏離原因 |
|---|---|---|---|
| Token 減少率 | 30-40% | 13.2% | 多數頁面（~30/48）未觸發清理；部分頁面被過度清理 |
| 內容保留率 | >95% | 87.8% | publication、thesisadvised 等頁面被激進清理（14.9%-44.9% 保留率） |

### 無偏離 plan

- 腳本結構、報告格式、整合建議均符合 plan.md 規劃
- 唯一偏離為實驗結果指標低於預期，但為實際數據反映，非腳本錯誤
