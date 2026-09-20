# Crawl4AI min_word_threshold 技術實作計畫

## Overview

在 `PruningContentFilter` 新增 `min_word_threshold` 參數，讓 crawl4ai 自動移除低於指定字數門檻的 HTML 區塊。改動涵蓋四個檔案：Config dataclass、Crawler 引擎、TOML 設定檔、Workflow 調用端。全部為向後相容的新增變更。

## Architecture Decisions

| Decision | Choice | Rationale | Alternatives Considered |
|---|---|---|---|
| 參數傳遞方式 | `__init__` 新增可選參數 → 實例屬性 → `_crawl_website_async` 使用 | 與現有 `max_depth`、`max_pages` 等參數的傳遞模式完全一致，零認知負擔 | 直接在 `_crawl_website_async` 硬編碼（放棄可配置性） |
| 預設值 | `10` | 文件中已驗證 10 字可過滤 `更多`、`前一頁` 等短文本，不影響正文段落 | `5`（太寬鬆）、`20`（可能誤刪標題） |
| Config 驗證 | 正整數（≥1） | `min_word_threshold=0` 無意義（等於不過濾），負數無效 | 允許 0（無意義過濾） |

## Module Structure

```
src/app/configs/website_crawler_config.py  ← 新增 min_word_threshold 欄位 + 驗證
src/app/engines/website_crawler.py         ← 新增參數 → PruningContentFilter
src/app/workflow/workflow.py               ← 傳入 config.min_word_threshold
configs/website_crawler/default.toml       ← [init] 新增 min_word_threshold = 10
configs/website_crawler/nculab.toml        ← [init] 新增 min_word_threshold = 10
```

## Data Models

### WebsiteCrawlerConfig（新增欄位）

```python
@dataclass
class WebsiteCrawlerConfig(BaseModuleConfig):
    # ...existing fields...
    min_word_threshold: int = 10  # 新增：低於此字數的 HTML 區塊直接移除
```

### INIT_KEYS（新增成員）

```python
INIT_KEYS = {
    "site_id",
    "max_depth",
    "max_pages",
    "content_threshold",
    "min_word_threshold",  # 新增
    "light_mode",
    "wait_for_images",
}
```

### _validate_config（新增驗證）

```python
min_word_threshold = config.get("min_word_threshold")
if min_word_threshold is not None:
    if not isinstance(min_word_threshold, int):
        raise ConfigValidationError("min_word_threshold 必須是整數")
    if min_word_threshold < 1:
        raise ConfigValidationError("min_word_threshold 必須 >= 1")
```

## API Contracts

### WebsiteCrawler.__init__（新增參數）

```python
def __init__(
    self,
    max_depth: int | None = None,
    max_pages: int | None = None,
    content_threshold: float = KEEP_IMAGE_CONTENT_THRESHOLD,
    min_word_threshold: int = 10,  # 新增
    light_mode: bool = True,
    wait_for_images: bool = True,
) -> None:
    self.min_word_threshold = min_word_threshold  # 新增
```

### _crawl_website_async（傳入 PruningContentFilter）

```python
pruning_content_filter = PruningContentFilter(
    threshold=self.content_threshold,
    min_word_threshold=self.min_word_threshold,  # 新增
)
```

### override_init_config（新增覆寫支援）

```python
def override_init_config(self, **init_kwargs) -> None:
    # ...existing overrides...
    self.min_word_threshold = init_kwargs.get("min_word_threshold", self.min_word_threshold)
```

### workflow.py（傳入 config）

```python
website_crawler = WebsiteCrawler(
    # ...existing args...
    min_word_threshold=config.min_word_threshold,  # 新增
)
```

## Three-Tier Boundaries

- **Always do**: 保持向後相容（所有新增參數皆有預設值）、遵循現有參數傳遞模式
- **Ask first**: 無
- **Never do**: 不修改 `exclude_words` 邏輯、不改變 `PruningContentFilter` 的 `threshold` 行為、不新增 BM25 相關功能

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| `min_word_threshold` 設為 0 導致無意義過濾 | 低 | 低 | 驗證層強制 ≥1 |
| `min_word_threshold` 過高（如 100）誤刪短標題 | 中 | 低 | 預設值 10 經驗證安全；文件說明最佳範圍 |
| crawl4ai 版本不支援 `min_word_threshold` | 高 | 極低 | 已確認 API（Context7 文件佐證） |
| 設定檔缺少 `min_word_threshold` 欄位 | 低 | 中 | dataclass 預設值 10 保證向後相容 |

## Verification Approach

1. **單元驗證**：`_validate_config` 對 `min_word_threshold=0` 拋出 `ConfigValidationError`
2. **整合驗證**：以 `nculab` 設定檔爬取，確認 `fit_markdown` 不含低於 10 字的孤立文本區塊
3. **向後相容驗證**：移除 TOML 中的 `min_word_threshold` 欄位，確認仍使用預設值 10 正常運作
4. **A/B Markdown 比較**：以 nculab 站點分別執行「無 `min_word_threshold`」與「`min_word_threshold=10`」兩次爬取，產出 `fit_markdown` 差異比較報告，驗證短文本雜訊被移除且主要內容保留

## Files to Change

| 檔案 | 改動類型 | 行數（預估） |
|---|---|---|
| `src/app/configs/website_crawler_config.py` | 新增欄位 + 驗證 | ~8 行 |
| `src/app/engines/website_crawler.py` | 新增參數 + 傳入 filter | ~5 行 |
| `src/app/workflow/workflow.py` | 傳入 config 參數 | ~1 行 |
| `configs/website_crawler/default.toml` | 新增設定項 | ~1 行 |
| `configs/website_crawler/nculab.toml` | 新增設定項 | ~1 行 |
