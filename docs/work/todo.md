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

## 效能優化

- [ ] 優化模組 import 策略