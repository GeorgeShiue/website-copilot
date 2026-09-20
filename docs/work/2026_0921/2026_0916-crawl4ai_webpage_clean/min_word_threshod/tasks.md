# Crawl4AI min_word_threshold Task List

## Coverage Matrix

| Spec Ref | Tasks |
|---|---|
| FR-001 | T005 |
| FR-002 | T001, T002 |
| FR-003 | T004, T005 |
| FR-004 | T001 |
| FR-005 | T008 |
| FR-006 | T009 |
| FR-007 | T006 |
| FR-008 | T003 |
| FR-009 | T010 |
| US1/AC1 | T010 |
| US1/AC2 | T010 |
| US1/AC3 | T008, T009 |
| US1/AC4 | T003 |
| US1/AC5 | T010 |

---

## Phase 1: Config Layer

- [x] **T001**: Add `"min_word_threshold"` to `INIT_KEYS` set per FR-004
  - Files: `src/app/configs/website_crawler_config.py` (line 20–26, `INIT_KEYS` set)
  - Acceptance:
    - `INIT_KEYS` contains the string `"min_word_threshold"`
    - No other keys are removed or reordered
    - Existing tests (if any) that import `INIT_KEYS` still pass
  - Depends on: none

- [x] **T002**: Add `min_word_threshold: int = 10` field to `WebsiteCrawlerConfig` dataclass per FR-002
  - Files: `src/app/configs/website_crawler_config.py` (line 47–48, between `content_threshold` and `light_mode`)
  - Acceptance:
    - Field appears as `min_word_threshold: int = 10` in the `# ----- init config -----` section
    - `WebsiteCrawlerConfig(...)` without `min_word_threshold` compiles without error (backward-compatible default)
    - `WebsiteCrawlerConfig(..., min_word_threshold=20)` assigns `20` to the instance
  - Depends on: T001

- [x] **T003**: Add `min_word_threshold` validation in `_validate_config` per FR-008
  - Files: `src/app/configs/website_crawler_config.py` (after `wait_for_images` validation block, ~line 80–85)
  - Acceptance:
    - When `config["min_word_threshold"]` is `None` → no error (default from dataclass)
    - When `config["min_word_threshold"]` is a non-integer (e.g. `3.5`, `"ten"`) → raises `ConfigValidationError`
    - When `config["min_word_threshold"]` is `< 1` (e.g. `0`, `-5`) → raises `ConfigValidationError`
    - When `config["min_word_threshold"]` is `>= 1` (e.g. `1`, `10`, `100`) → no error
  - Depends on: T002

---

## Phase 2: Engine Layer

- [x] **T004**: Add `min_word_threshold: int = 10` parameter to `WebsiteCrawler.__init__` and store as instance attribute per FR-003
  - Files: `src/app/engines/website_crawler.py` (line 87–96, `__init__` signature and body)
  - Acceptance:
    - Signature reads `min_word_threshold: int = 10` after `content_threshold`
    - Instance body sets `self.min_word_threshold = min_word_threshold`
    - Existing callers that omit `min_word_threshold` still compile (backward-compatible default)
  - Depends on: T002

- [x] **T005**: Pass `min_word_threshold` to `PruningContentFilter` in `_crawl_website_async` per FR-001, FR-003
  - Files: `src/app/engines/website_crawler.py` (line 136–138, `PruningContentFilter(...)` call)
  - Acceptance:
    - `PruningContentFilter(...)` call includes `min_word_threshold=self.min_word_threshold`
    - The `threshold=self.content_threshold` argument remains unchanged
  - Depends on: T004

- [x] **T006**: Add `min_word_threshold` override support in `override_init_config` per FR-007
  - Files: `src/app/engines/website_crawler.py` (line 310–316, `override_init_config` method)
  - Acceptance:
    - A new line `self.min_word_threshold = init_kwargs.get("min_word_threshold", self.min_word_threshold)` exists in `override_init_config`
    - Pattern matches existing lines (e.g. `self.max_depth = init_kwargs.get("max_depth", self.max_depth)`)
  - Depends on: T004

---

## Phase 3: Workflow Layer

- [x] **T007**: Pass `config.min_word_threshold` to `WebsiteCrawler` constructor in `run_website_crawler` per FR-003
  - Files: `src/app/workflow/workflow.py` (line 87–93, `WebsiteCrawler(...)` constructor call)
  - Acceptance:
    - `WebsiteCrawler(...)` call includes `min_word_threshold=config.min_word_threshold` keyword argument
    - The argument is positioned after `wait_for_images=config.wait_for_images` to match signature order
    - No other arguments are removed or reordered
  - Depends on: T004

---

## Phase 4: Configuration Files

- [x] **T008**: Add `min_word_threshold = 10` to `configs/website_crawler/default.toml` per FR-005
  - Files: `configs/website_crawler/default.toml` (after line 6, `wait_for_images = true`)
  - Acceptance:
    - `[init]` section contains `min_word_threshold = 10`
    - Existing keys in `[init]` are not reordered or removed
    - TOML is valid (parseable by `tomllib`)
  - Depends on: T001

- [x] **T009**: Add `min_word_threshold = 10` to `configs/website_crawler/nculab.toml` per FR-006
  - Files: `configs/website_crawler/nculab.toml` (after line 6, `wait_for_images = true`)
  - Acceptance:
    - `[init]` section contains `min_word_threshold = 10`
    - Existing keys in `[init]` are not reordered or removed
    - TOML is valid (parseable by `tomllib`)
  - Depends on: T001

---

## Phase 5: Verification

- [x] **T010**: Execute A/B comparison test per FR-009 / AC5
  - Files: none (execution-only task, results stored in `runs/20260916_171949/ab_test_min_word_threshold/`)
  - Acceptance:
    - **Baseline run** (no `min_word_threshold`): crawl nculab site, save `fit_markdown` output
    - **Experiment run** (`min_word_threshold=10`): crawl nculab site, save `fit_markdown` output
    - **Diff report** produced showing:
      - All removed lines have word count < 10 (confirm short-text noise removal)
      - No main content paragraphs (body text, member descriptions, research directions) are removed
      - Removed items include expected noise: `更多`, `前一頁`, `第一頁`, etc.
    - Report saved to `runs/` directory for manual review
  - Depends on: T005, T007, T008, T009
  - **Result**: ❌ FAIL — `min_word_threshold=10` removes 52% of content (872 main content lines) on Google Sites. Short text noise removal works (60 lines), but HTML block-level filtering is too aggressive for Google Sites DOM structure. See `runs/20260916_171949/ab_test_min_word_threshold/ab_comparison_report.md` for full analysis. Recommendation: keep `min_word_threshold=None` (not enabled) and rely on existing `exclude_words`.
