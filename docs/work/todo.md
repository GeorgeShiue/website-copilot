# 功能進度

- [x] 讀取網站文件（見 [dev.md](./2026_1005/2026_1004-content_augmentation/dev.md)）
- [ ] 網站知識庫版本控制
- [ ] 站點檔加入顯示名稱與描述，供 list_knowledge_bases 回傳給 LLM

# 技術債

## 模組重構

- [ ] Webpage Markdown Cleaner 獨立成一個模組
- [ ] 包裝 log_helper.py（含約 6 處 Rich「Metric／Value」統計表格，見 code cleanup plan C3）
- [ ] 客製化模組 RunManager

## 效能優化

- [ ] 優化模組 import 策略
- [x] 圖片摘要：同一頁內重複的圖片 URL 會被同時下載多次（P1c 改為跨頁去重、整批下載，每個 URL 只下載一次）
- [x] 平行處理圖片摘要（P1c 改為所有頁的圖共用下載與 VLM 的並行上限）
