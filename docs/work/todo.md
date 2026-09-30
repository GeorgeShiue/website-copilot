# 功能進度

- [ ] 重跑完整流程
- [ ] 讀取網站文件
- [ ] 網站知識庫版本控制
- [ ] 站點檔加入顯示名稱與描述，供 list_knowledge_bases 回傳給 LLM

# 技術債

## 模組配置

- [ ] 優化 site_id 參數設定和讀取
- [ ] yml 配置檔
- [ ] configs 改用 pydantic 參數驗證
- [ ] config class 引入巢狀 class 分類
- [ ] cli module config移除中介層

## 資料安全

- [ ] `run rag-query` 加 `force_rebuild` 時會直接建庫到 `data/rag/{site_id}/milvus.db`，違反「建庫不直接寫入 data/」原則

## 模組重構

- [ ] 包裝 log_helper.py
- [ ] Webpage Markdown Cleaner 獨立成一個模組
- [ ] 客製化模組 RunManager

## 效能優化

- [ ] 優化模組 import 策略
- [ ] 平行處理圖片摘要
