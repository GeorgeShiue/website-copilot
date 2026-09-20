# 動態閾值（threshold_type="dynamic"）實作計畫

## Overview

在現有 `PruningContentFilter` 基礎上，新增 `threshold_type` 參數支援 `"fixed"` 與 `"dynamic"` 兩種模式。改動範圍限於設定層（config）與爬蟲引擎（engine），不涉及 Markdown 清洗層或 CLI 框架變更。最後透過 AB test 腳本驗證動態閾值對 nculab 站點的 Markdown 品質影響。

---

## Architecture Decisions

| Decision | Choice | Rationale | Alternatives Considered |
|---|---|---|---|
| 參數傳遞方式 | 直接傳入 `PruningContentFilter` | crawl4ai 原生支援，無需額外包裝 | 自訂演算法（過度設計） |
| 預設值 | `"fixed"` | 向後相容，不影響現有行為 | `"dynamic"`（破壞性變更） |
| CLI 覆寫 | 加入 `WebsiteCrawlerModuleConfig` | 與現有 `max_pages` 模式一致 | 獨立 CLI 參數（破壞一致性） |
| AB test 位置 | `dev/crawl4ai/` 目錄 | 與既有實驗腳本放置慣例一致 | `tests/`（非單元測試） |

---

## Module Structure

```
改動檔案：
├── src/app/configs/website_crawler_config.py   ← FR-001, FR-004, FR-006
├── src/app/engines/website_crawler.py          ← FR-002, FR-003
├── src/app/configs/workflow_config.py          ← FR-007
├── configs/website_crawler/nculab.toml         ← FR-005
└── dev/crawl4ai/ab_test_dynamic_threshold.py   ← FR-008

唯讀參考：
├── src/app/workflow/workflow.py                ← 確認參數傳遞路徑
├── src/cli.py                                  ← 確認 CLI 解析邏輯
└── docs/work/.../dynamic_threshold/spec.md     ← 規格來源
```

---

## Data Models

### WebsiteCrawlerConfig 新增欄位

```python
# website_crawler_config.py

# INIT_KEYS 新增
INIT_KEYS = {
    "site_id",
    "max_depth",
    "max_pages",
    "content_threshold",
    "threshold_type",      # ← 新增
    "light_mode",
    "wait_for_images",
}

# WebsiteCrawlerConfig dataclass 新增
threshold_type: str = "fixed"  # "fixed" 或 "dynamic"
```

### WebsiteCrawlerModuleConfig 新增欄位

```python
# workflow_config.py

@dataclass
class WebsiteCrawlerModuleConfig:
    max_pages: int | None = None
    threshold_type: str | None = None  # ← 新增
```

### WebsiteCrawler.__init__ 新增參數

```python
# website_crawler.py

class WebsiteCrawler:
    def __init__(
        self,
        max_depth: int | None = None,
        max_pages: int | None = None,
        content_threshold: float = KEEP_IMAGE_CONTENT_THRESHOLD,
        threshold_type: str = "fixed",  # ← 新增
        light_mode: bool = True,
        wait_for_images: bool = True,
    ) -> None:
        self.threshold_type = threshold_type
```

---

## API Contracts

### PruningContentFilter 呼叫變更

```python
# Before
pruning_content_filter = PruningContentFilter(
    threshold=self.content_threshold,
)

# After
pruning_content_filter = PruningContentFilter(
    threshold=self.content_threshold,
    threshold_type=self.threshold_type,
)
```

### CLI 覆寫方式

```bash
# 固定閾值（預設）
uv run python -m app.cli WebsiteCrawlerCLI

# 動態閾值（CLI 覆寫）
uv run python -m app.cli WebsiteCrawlerCLI --module.threshold-type dynamic
```

### TOML 設定檔格式

```toml
[init]
site_id = "nculab"
max_depth = 2
content_threshold = 0.25
threshold_type = "fixed"  # ← 新增
```

---

## Three-Tier Boundaries

### Always do（架構不變項）

- 保持 `threshold_type` 預設值為 `"fixed"`，確保向後相容
- `threshold_type` 僅允許 `"fixed"` 或 `"dynamic"` 兩個值
- 所有設定變更必須透過 `WebsiteCrawlerConfig` dataclass
- AB test 必須在相同爬取範圍下比較，確保結果可比較

### Ask first（需人工確認）

- 若 crawl4ai 版本不支援 `threshold_type` 參數，需先升級依賴
- AB test 結果若動態模式劣於固定模式，是否仍合併代碼

### Never do（架構禁區）

- 不修改 `PruningContentFilter` 內部實作
- 不新增 `threshold_type` 以外的過濾參數
- 不改變現有 `exclude_words` 邏輯
- 不在 `_validate_config()` 外的地方驗證 `threshold_type`

---

## Implementation Notes

- **實作日期**: 2026-09-16
- **偏離計畫**: 無
- **所有任務均按計畫執行**：T001–T008 完成，未發現偏離
- **AB Test 結果**: 動態模式在 nculab 站點上與固定模式表現相當（Δ = 0.42%）
- **建議**: 在更多站點進行進一步驗證

---

## Implementation Tasks

### Phase 1: Config Layer（FR-001, FR-004, FR-005, FR-006）

**T001**: `website_crawler_config.py` — 新增 `INIT_KEYS` 與 `WebsiteCrawlerConfig` 欄位

改動點：
- `INIT_KEYS` 集合新增 `"threshold_type"`
- `WebsiteCrawlerConfig` dataclass 新增 `threshold_type: str = "fixed"` 欄位
- `_validate_config()` 新增 `threshold_type` 驗證邏輯

驗證方式：`uv run pytest src/test/dev/ -v`

---

**T002**: `configs/website_crawler/nculab.toml` — 新增 `threshold_type` 設定

改動點：
- `[init]` section 新增 `threshold_type = "fixed"`

驗證方式：確認 TOML 載入後 `threshold_type` 值正確

---

### Phase 2: Engine Layer（FR-002, FR-003）

**T003**: `website_crawler.py` — 新增 `threshold_type` 參數

改動點：
- `WebsiteCrawler.__init__()` 新增 `threshold_type: str = "fixed"` 參數
- `self.threshold_type = threshold_type` 賦值

驗證方式：確認 `WebsiteCrawler()` 實例化時可傳入 `threshold_type`

---

**T004**: `website_crawler.py` — 傳入 `PruningContentFilter`

改動點：
- `_crawl_website_async()` 中 `PruningContentFilter(...)` 新增 `threshold_type=self.threshold_type`

驗證方式：確認爬取時使用指定的 `threshold_type`

---

### Phase 3: CLI Layer（FR-007）

**T005**: `workflow_config.py` — 新增 CLI 覆寫欄位

改動點：
- `WebsiteCrawlerModuleConfig` 新增 `threshold_type: str | None = None`

驗證方式：確認 CLI 參數 `--module.threshold-type dynamic` 可正確解析

---

### Phase 4: Workflow Integration

**T006**: `workflow.py` — 傳遞 `threshold_type` 至 `WebsiteCrawler`

改動點：
- `run_website_crawler()` 中 `WebsiteCrawler(...)` 呼叫新增 `threshold_type=config.threshold_type`

驗證方式：確認 workflow 完整執行時 `threshold_type` 正確傳遞

---

### Phase 5: AB Test（FR-008）

**T007**: `dev/crawl4ai/ab_test_dynamic_threshold.py` — 建立 AB test 腳本

功能需求：
- 使用 `WebsiteCrawlerConfig.from_toml("nculab")` 載入設定
- 分別以 `threshold_type="fixed"` 與 `threshold_type="dynamic"` 執行爬取
- 比較兩組結果的 `fit_markdown` 長度、頁面數量
- **找出內容有差異的 webpage markdown 檔案**（逐頁比較 `fit_markdown` 內容）
- 輸出對比表格至 `runs/{timestamp}/ab_test_dynamic_threshold/`
- 產生 `ab_comparison_report.md` 報告（含差異頁面清單）

---

**T008**: 執行 AB test 並記錄結果

執行方式：
```bash
uv run python dev/crawl4ai/ab_test_dynamic_threshold.py
```

產出：
- `runs/{timestamp}/ab_test_dynamic_threshold/fixed/` — 固定閾值結果
- `runs/{timestamp}/ab_test_dynamic_threshold/dynamic/` — 動態閾值結果
- `runs/{timestamp}/ab_test_dynamic_threshold/diff_pages.json` — 內容有差異的頁面清單
- `runs/{timestamp}/ab_test_dynamic_threshold/ab_comparison_report.md` — 對比報告

---

**T009**: Verifier Agent 閱讀差異頁面並分析

由 Verifier Agent 親自閱讀 T008 產出的差異頁面 markdown 檔案，分析：
- 哪些頁面的 `fit_markdown` 內容不同
- 差異的具體內容（哪些段落被移除或保留）
- 判斷動態閾值是否有效改善雜訊過濾或內容保留

產出：
- `runs/{timestamp}/ab_test_dynamic_threshold/verifier_analysis.md` — 差異分析報告

---

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| crawl4ai 版本不支援 `threshold_type` | 高（功能無法實作） | 低 | 已確認 crawl4ai 文件支援此參數 |
| 動態閾值導致內容大量遺漏 | 中（Markdown 品質下降） | 中 | AB test 比較內容保留率，若劣於固定模式則不合併 |
| CLI 參數命名衝突 | 低（解析錯誤） | 低 | 使用 `threshold-type` 命名，與現有參數無衝突 |
| TOML 載入失敗 | 中（設定無法讀取） | 低 | `_validate_config()` 驗證值域 |

---

## Verification Approach

### 單元驗證（Phase 1-4）

- **Config 驗證**：`_validate_config()` 正確接受 `"fixed"` / `"dynamic"`，拒絕其他值
- **TOML 載入**：`WebsiteCrawlerConfig.from_toml("nculab")` 正確讀取 `threshold_type`
- **Engine 傳遞**：`PruningContentFilter` 收到正確的 `threshold_type` 參數
- **CLI 覆寫**：`--module.threshold-type dynamic` 正確覆寫 TOML 設定

### 整合驗證（Phase 5）

- **AB test 比較**：固定閾值 vs 動態閾值的爬取結果對比
- **差異頁面分析**：找出內容有差異的 webpage markdown 檔案，由 Verifier Agent 親自閱讀分析
- **回歸測試**：確認 `threshold_type="fixed"` 行為與改動前完全一致
- **品質指標**：內容保留率、雜訊殘留率符合 spec 成功標準

---

## Open Questions

無（所有問題已在 spec 澄清階段解決）
