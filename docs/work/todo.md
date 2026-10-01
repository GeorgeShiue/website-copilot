# 功能進度

- [ ] 重跑完整流程
- [ ] 讀取網站文件
- [ ] 網站知識庫版本控制
- [ ] 站點檔加入顯示名稱與描述，供 list_knowledge_bases 回傳給 LLM

# 技術債

## 資料儲存

- [ ] 優化 data/rag 儲存路徑
- [ ] `run rag-query` 加 `force_rebuild` 時會直接建庫到 `data/rag/{site_id}/milvus.db`，違反「建庫不直接寫入 data/」原則

## 模組重構

- [ ] Webpage Markdown Cleaner 獨立成一個模組
- [ ] 包裝 log_helper.py
- [ ] 客製化模組 RunManager

## 效能優化

- [ ] 優化模組 import 策略
- [ ] 平行處理圖片摘要
