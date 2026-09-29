# 功能進度

- [ ] 重跑完整流程
- [ ] 讀取網站文件
- [ ] 網站知識庫版本控制

# 技術債

## 檔案結構

- [ ] 專案結構重構
  - [X] plan 1
  - [X] plan 2
    1. server 建置 agent 改為呼叫 run_agent_build()
    2. ChatServer 退出自動清理 ChatApp
    3. 捨棄 makefile 將常見指令整理在 scripts 底下的腳本
    4. 統一所有 gemini api key 環境變數名稱為 GEMINI_API_KEY
    5. pyproject.toml 更新 (dependency, ruff)
  - [X] plan 3
    * run agent bulid 脫離 run server build 直接放在 serve 中
    * run agent bulid 和 run server build 各自持有獨立的 run manager
    * 修正 test_webpage_markdown_cleaner.py 的 pyright 錯誤與失敗測試（check.sh / CI 恢復通過）
    * run_agent_query 改用 run_agent_build() 建構 agent（移除重複的建構與落盤邏輯）
    * 修正 run_agent_query 例外路徑重複呼叫 agent.close()
    * create_agent() 改為接受 AgentConfig，避免 AgentConfig 重複讀取
  - [ ] plan 4
    1. storage/run_context 不依賴 config class（改傳 site_id / run_name）
    2. retrieval/factory 不依賴 RunManager（改傳 milvus.db 路徑）
    3. RunManager 初始化收斂（避免 __init__ 先建目錄、欄位預設空字串的半初始化狀態）
    4. 搭配「優化 site_id 參數設定和讀取」一起處理
  - [ ] 檢查遺漏項目
- [ ] 測試優化
  1. 更新 test_main test_module 測試流程
     * test_main() 拆分為 test_prepare() test_serve()
     * test_module.py 改為每個 run function 都有一個自己的 test function
  2. 更新 -m slow 標記
  3. 整理 test/dev 中的測試
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
