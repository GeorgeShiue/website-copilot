# 功能進度
- [ ] 重跑完整流程
- [ ] 讀取網站文件
- [ ] 網站知識庫版本控制

# 技術債

## 檔案結構
- [ ] app 改名為 core
- [ ] rag 從 engines 移動到 core
- [ ] engines 改名為 prepare

## 測試優化
- [ ] 更新 test_main.py 測試流程
- [ ] 整理 test/dev 中的測試

## 模組配置
- [ ] 優化 site_id 參數設定和讀取
- [ ] run config 永遠儲存
- [ ] yml 配置檔
- [ ] configs 改用 pydantic 參數驗證
- [ ] config class 引入巢狀 class 分類
- [ ] cli module config 移除中介層

## 模組重構
- [ ] 包裝 log_helper.py
- [ ] Webpage Markdown Cleaner 獨立成一個模組
- [ ] 客製化模組 RunManager

## 效能優化
- [ ] 優化模組 import 策略
- [ ] 平行處理圖片摘要