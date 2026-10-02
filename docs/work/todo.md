# 功能進度

- [ ] 讀取網站文件
- [ ] 網站知識庫版本控制
- [ ] 站點檔加入顯示名稱與描述，供 list_knowledge_bases 回傳給 LLM

# 技術債

## 模組重構

- [ ] Webpage Markdown Cleaner 獨立成一個模組
- [ ] 包裝 log_helper.py（含約 6 處 Rich「Metric／Value」統計表格，見 code cleanup plan C3）
- [ ] 客製化模組 RunManager

## 效能優化

- [ ] 優化模組 import 策略
- [ ] 圖片摘要：同一頁內重複的圖片 URL 會被同時下載多次（ncucsie 有 10 頁；`_collect_cached_items` 未對頁內 URL 去重），第一個失敗會取走 `_download_failure_reasons`，使 log 的失敗原因可能顯示為 `download failed` 而非實際的 `HTTP Error 404`（見 `docs/exp/memo/webpage_image_summarizer/download_concurrency/results.md`）
- [ ] 平行處理圖片摘要（目前頁面依序處理，VLM 並行上限只在單頁內生效；改為所有頁的圖共用一個上限，見 code cleanup plan C2）