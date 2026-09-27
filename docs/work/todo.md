# 功能進度
- [ ] 重跑完整流程
- [ ] 讀取網站文件
- [ ] 網站知識庫版本控制

# 技術債

## 檔案結構
- [ ] 專案結構重構
  - [x] plan 1
  - [x] plan 2
    1. server 建置 agent 改為呼叫 run_agent_build()
    2. ChatServer 退出自動清理 ChatApp
    3. 捨棄 makefile 將常見指令整理在 scripts 底下的腳本
    4. 統一所有 gemini api key 環境變數名稱為 GEMINI_API_KEY
    5. pyproject.toml 更新 (dependency, ruff)
- [ ] 測試優化
  - [ ] 更新 test_main.py 測試流程
  - [ ] 更新 -m slow 標記
  - [ ] 整理 test/dev 中的測試
- [ ] 測試新專案結構

## 模組配置
- [ ] 優化 site_id 參數設定和讀取
- [ ] run config 永遠儲存
- [ ] yml 配置檔
- [ ] configs 改用 pydantic 參數驗證
- [ ] config class 引入巢狀 class 分類
- [ ] cli module config **移除中介層**

## 模組重構
- [ ] 包裝 log_helper.py
- [ ] Webpage Markdown Cleaner 獨立成一個模組
- [ ] 客製化模組 RunManager

## 效能優化
- [ ] 優化模組 import 策略
- [ ] 平行處理圖片摘要