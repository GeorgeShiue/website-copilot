# 功能進度
- [ ] 重跑完整流程
- [ ] 讀取網站文件
- [ ] 網站知識庫版本控制

# 技術債

## 流程優化
- [x] 優化 main workflow logging
- [x] 優化 main workflow 留檔機制
  - [x] plan 1
    * 運行 main workflow 不儲存結果到 runs 資料夾
  - [x] plan 2
    * data_manager 改為在 run function 中創建，並在 run function 新增 publish to data 參數 (?)
    * website crawler 和 webpage image summarizer 儲存資料路徑拆分
- [ ] run_rag_build() 不建立 query_engine
- [ ] 伺服器啟動獨立於 main workflow 之外

## 測試優化
- [ ] 更新 test_main.py 測試流程
- [ ] 整理 test/dev 中的測試

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