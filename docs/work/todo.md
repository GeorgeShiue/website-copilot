# 功能進度
- [ ] 讀取網站文件
- [ ] 網站知識庫版本控制

# 技術債

## 流程優化
- [x] 優化 main workflow logging
- [ ] 運行 main workflow 不儲存結果到 runs 資料夾
- [ ] run_rag_build() 不建立 query_engine
- [ ] 伺服器啟動獨立於 main workflow 之外

## 模組重構
- [ ] 包裝 log_helper.py
- [ ] Webpage Markdown Cleaner 獨立成一個模組
- [ ] 客製化模組 RunManager

## 模組配置
- [ ] 優化 site_id 參數設定和讀取
- [ ] yml 配置檔
- [ ] configs 改用 pydantic 參數驗證

## 檔案結構
- [ ] app 改名為 core
- [ ] rag 從 engines 移動到 core
- [ ] engines 改名為 prepare

## 效能優化
- [ ] 優化模組 import 策略
- [ ] 平行處理圖片摘要