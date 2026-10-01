# 功能進度

- [ ] 重跑完整流程
- [ ] 讀取網站文件
- [ ] 網站知識庫版本控制
- [ ] 站點檔加入顯示名稱與描述，供 list_knowledge_bases 回傳給 LLM

# 技術債

## 資料儲存

> 計畫見 [2026_1001-data_storage/plan.md](./2026_1005/2026_1001-data_storage/plan.md)

- [ ] 優化 data/rag 儲存路徑：collection 名稱固定為 `chunks`、Milvus 資料夾改為 `data/rag/{site}.db/` 並將設定紀錄放入其中的 `meta/`（解決 parquet 路徑過深且 site_id 重複）
- [ ] 移除 `run rag-query` 的 `force_rebuild`（會直接建庫到 `data/rag/{site_id}/milvus.db`，違反「建庫不直接寫入 data/」原則），建庫邏輯只留在 `run rag-build`；新增 `--run.vector-store-run` 查詢 runs/ 中的實驗向量庫
- [ ] `.gitignore` 忽略 `data/rag/**/indexes/`（Milvus Lite 載入時會寫入可重建的索引檔）
- [ ] 所有模組的儲存機制一次引入版本控制（含 data/rag、data/webpages；本次資料儲存重構不處理）

## 模組重構

- [ ] Webpage Markdown Cleaner 獨立成一個模組
- [ ] 包裝 log_helper.py
- [ ] 客製化模組 RunManager

## 效能優化

- [ ] 優化模組 import 策略
- [ ] 平行處理圖片摘要
