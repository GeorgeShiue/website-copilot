# Survey
- [ ] 產品定位

# 功能進度

- [ ] 網站知識庫版本控制
- [ ] 站點檔加入顯示名稱與描述，供 list_knowledge_bases 回傳給 LLM

# 技術債

## 模組重構

- [ ] Webpage Markdown Cleaner 獨立成一個模組
- [ ] 包裝 log_helper.py（含約 6 處 Rich「Metric／Value」統計表格，見 code cleanup plan C3）
- [ ] 客製化模組 RunManager

## Python 優化

已採用的設計見 `docs/code/python.md`。

### 修正

#### 裝飾器

- [ ] `WebpageMarkdownCleaner` 的 8 個公開 `@staticmethod` 是純函式且以寫死的類別名互相呼叫：改成模組函式（需多型則改 `@classmethod`），與「Webpage Markdown Cleaner 獨立成一個模組」一併處理
- [ ] 計時／重試的裝飾器版本：`log_run_time` 目前只有 context manager 形式
