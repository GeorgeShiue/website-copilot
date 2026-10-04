# Main workflow 優化：實作紀錄

> 對應規劃文件：[plan.md](./plan.md)。只記錄與 plan 不同的決定、過程中的討論與發現、遺留事項；設計本身見 plan。

---

## A. Log 優化

### A-1 執行摘要（commit `969ca57`，先前工作階段完成）

建立了後續兩輪的基礎慣例：

- `log_helper.py`：`log_run_time(title, record=True)` 記錄階段耗時；`record_cost()`／`record_elapsed()`／`reset_run_summary()`／`log_run_summary()` 產生統一的 Stage/Elapsed/Cost 彙總表；`NOISY_LOGGER_LEVELS` 在 `setup_logging()` 統一過濾；`disable_model_progress_bars()`；`print_log()` 新增 `soft_wrap`。
- `main.py`：流程包在 `try/finally: log_run_summary()`，提前 return 或例外時仍印出已完成階段的摘要。

### A-2 決策過程

- **Agent 建置表格**：先問使用者「`Tool()`（建立 RAGRegistry）與可用知識庫兩個階段完全沒有 log，是否一併加入？」使用者選兩者都加，初版含 Registry、Knowledge bases、LLM、Checkpointer、Tools 五列；之後要求移除 Checkpointer、再移除 Registry 並把 Knowledge bases 移到 Tools 下方，定案為 **LLM → Tools → Knowledge bases**。
- **Server Stop**：初版在 `except KeyboardInterrupt:` 印 `Server Stopping`，使用者指出這會晚於 uvicorn 自己的關閉訊息（`server.run()` 內部已完成 graceful shutdown 才交還控制權），要求「按下 Ctrl+C 當下就輸出」，因此改為 monkey-patch `server.handle_exit`。

### A-3 發現的 bug：Rich markup 吞掉方括號

進度條描述 `Downloading images... [page_title]` 第一次實測時頁名完全消失。根因是 `TaskCountProgress` 的 `TextColumn("[yellow]{task.description}")` 本身是 markup 模板，代入後整串被當 markup 解析，`[page_title]` 被誤判為不存在的樣式標籤。

第一次修法 `f"... [{escape(self._current_page)}]"` **無效**：方括號是程式碼自己加的字面字元，不在被 escape 的範圍內（`escape('labintro')` 沒有變化）。正確做法是對**整串組好的描述**呼叫 `escape(f"Downloading images... [{self._current_page}]")`，下載與摘要兩處都套用。

### A 驗證

單元測試不足以驗證表格寬度與頁名這類「真實資料才暴露」的問題，因此 A-3 直接用 `run_website_crawler`／`run_webpage_image_summarizer`／`run_rag_build`（跳過需要 Ctrl+C 的 server）對 nculab 跑真實流程三輪：

| 輪次 | 條件 | 結果 |
|---|---|---|
| 1 | 無 TTY（80 欄） | 抓到 markup escape bug |
| 2 | `COLUMNS=150`，escape 修法未正確套用 | bug 依舊，證明不是寬度問題 |
| 3 | `COLUMNS=150`，正確 escape | 全部符合 plan |

非 slow 套件：193 passed。

### A 附帶發現（未在本輪處理）

- `test_run_rag_build_publish.py` 有 2 個既有失敗：`run_rag_build()` 在先前未提交變更中把 `publish_run_metadata(...)` 移到 `save_module_config_as_toml(...)` 之前，導致發布時來源檔案還不存在，屬於 B 的範疇。
- `test_run_agent.py` 對 `mock_rm.module_config_toml_path` 寫死相對路徑，會留下空的 `fake_module_config.toml`，每次驗證後需清掉。
- 完成 A-3 後觀察到 `main.py`、`agent.py`、`webpage_image_summarizer.py` 又有進一步變動（`log_main_workflow_run_summary()`、`"Agent Stats"` 改名、逐頁 `log_session` 疑似重新出現），研判屬後續「包裝 `log_helper.py`」工作，不在此記錄範圍。

---

## B. 留檔機制

### B-1 決策過程

- 第一版只讓 `save=False` 跳過「寫結果檔」，`RunManager.for_run` 仍會呼叫（`runs/` 還是會有只含空 `results/` 與 `terminal.log` 的時間戳目錄）。使用者明確要求 `save=False` 時**完全不建立 `runs/` 目錄**，才改成回傳 `None`。
- 第一版照抄原始碼順序，`save_module_config_as_toml`／`save_run_config_as_toml` 留在 publish 之後。使用者要求把「儲存結果」與「儲存配置」合併在同一個 `if save:` 底下、放在 publish 前面，才有現在的 Save／Publish 明確分區。
- 參數原名為 `save_to_runs`，後來統一簡化為 `save`。
- `create_run_context` 回傳 `RunManager | None` 後，Pyright 在 `if save:` 區塊內標 `reportOptionalMemberAccess`（看不出布林與 `None` 的關聯），在各區塊開頭加 `assert run_manager is not None` 縮窄型別。

### B-2(a) 決策過程

- 使用者先要求「分析為什麼會有這種差異」再動手（結論見 plan）。接著問能否把 `data_manager` 併入 `create_run_context`，回答不建議（理由見 plan），使用者接受。
- 定案前使用者要求列出模糊點，逐一定案：(1) `DataManager` 無條件建立，選簡單一致，接受 `publish=False` 時多一次 `makedirs("data")` 的無害副作用；(2) 不給 `create_data_manager` 自訂 `base_folder`；(3) `_check_published_files` 簡化成吃 `base_folder: str`；(4) 測試 `test_no_data_manager_does_not_publish` 改名為 `test_publish_false_does_not_publish`。
- 實作並驗證後，使用者指出 `create_data_manager` 只有 `return DataManager()`，要求取消、直接寫在三個函式內，「等後續建立動作變複雜再加回」。測試改成 `patch("app.workflow.workflow.DataManager", ...)`。

### B-2(b) 決策過程

1. **第一版**：crawler 的 markdown 寫到 `data/webpages/{site_id}/crawl_results/` 子資料夾，`results.json` 與 `results/` 不動（RAG 讀的就是 `results/`）。實作並驗證後被使用者推翻，改要求 crawler 存到 `data/raw_webpages/{site_id}`。
2. **澄清 `results.json` 去向**：使用者指示「全部移動過去，但是 RAG 讀取路徑不變」字面上矛盾（`RAG._load_results_json()` 讀 `webpages/results.json`，搬走就得改路徑）。兩輪 AskUserQuestion 提了方案 A（RAG 改成兩處讀）與方案 B（crawler 發布到兩處），使用者最終給出前兩輪都沒問到的第三種設計：「crawler 留一份在 `raw_webpages`，summarizer 再留一份到 `webpages`」，也就是 `webpages/results.json` 由 summarizer 用 `enhanced_results` 重新發布。
3. **可行性前置確認**：讀 `_summarize_crawl_results_images()` 原始碼，確認 `crawl_result["enhanced_markdown"] = ...` 是就地修改並回傳同一物件，所以 `enhanced_results` 含全部原始欄位，`RAG._build_file_metadata()` 依賴的 `url`／`metadata.page_type` 不會遺失。
4. **`runs/` 是否也要改 `raw_webpages`**：查證後不需要。`runs/` 路徑為 `runs/{timestamp}/{module}/{site_id}/{run_name}/`，兩個模組從最上層就是不同目錄樹；`data/` 需要拆分是因為 `DataManager` 有固定的發布分類目的地。**未改動任何檔案**。
5. 實測發現上一輪驗證（`crawl_results/` 版）遺留的 `exclude_words_report.json`／`generated_exclude_words.toml` 在 `data/webpages/nculab/`，手動刪除。

驗證時逐頁比對兩份 `results.json`：`webpages/` 比 `raw_webpages/` 多一個 `enhanced_markdown`，符合設計；`results/*.md` 差異只有 `print()` 產生的尾端換行。

### B 驗證

三輪皆為非 slow 套件 195 passed、1 個既有失敗（`test_webpage_markdown_cleaner.py::test_save_generated_exclude_words`，`git stash` 確認改動前即存在）、pyright 0 errors，並各跑一次 `main.py --run.config-name test`（真實爬蟲加 LLM 加 RAG 建庫，花費 $0.0704、226 秒）。B-1 實測確認 `runs/` 無新增，log 顯示 `Milvus vector store already at data/rag/nculab/milvus.db, skipping publish`。

---

## C. RAG 建置流程

### 起點：先確認問題是否真實存在

動手前逐點查證，不憑臆測：第 1 點追蹤 `build_reusable()` docstring（最後一律建 retriever 與 query_engine）；第 2 點追蹤 `save=True` 如何覆寫 `milvus_uri`，加上 `RunManager.__init__` 的 `time.strftime`，證明路徑必為全新，`_should_rebuild()` 恆為 `True`；第 3 點比對兩處 `run_name` 計算；第 6 點 grep 確認 `rag.query_engine` 只有 `RAG.query()` 一個消費者。

### 第 2 點：是否保留 `force_rebuild`

原規劃是「`save` 只控制落盤位置，仍保留 `force_rebuild` 讓呼叫端決定」。使用者提出更明確的立場：`run_rag_build()` 的語意就是已確定要重建，應整個移除參數而非調整預設值。確認不破壞需求後採用：CLI 的 `RAGBuildRunConfig` 本來就沒有此欄位，移除對 CLI 零影響。同步移除 `main.py`、`test_main.py`、`test_module.py` 的 `force_rebuild=True`。

### 第 5 點：`overwrite` 移除前的實測

使用者要求用實測而非只憑原始碼推論，並指出「先前直接 overwrite 會出問題才實作 `clean_vector_store()`」。

- 讀 `MilvusVectorStore.__init__` 確認 `overwrite` 只在既有 collection 存在時才 `drop_collection`。
- 用真實 `VectorStoreBuilder.build()`（hybrid sparse embedding、真實 OpenAI embedding、寫入 3 筆）測：不 clean 直接 `overwrite=True` 重建不出錯；`clean_vector_store()` 後 `overwrite=False` 重建也不出錯。
- **無法重現**當初促成 `clean_vector_store()` 的失敗案例，因此保留該函式，只移除可由邏輯證明多餘的 `overwrite`。
- 移除後再對正式程式碼路徑煙霧測試三種情境（全新建立、檔案已存在時重建、load-existing 重用），皆正常。

### 第 6 點：`build_to_retriever()` 的位置

讓它疊在 `build_to_vector_store()` 之上、`build_to_query_engine()` 再疊在它之上，而不是三個方法平行呼叫底層步驟，避免 `build_to_vector_store()` 加 `build_retriever()` 寫兩次。同時發現 `test_rag_tools.py::TestGetCacheMiss` 的 mock 斷言還停留在更早的舊方法名 `build_reusable`，一併修為 `build_to_retriever`。

### C 驗證

非 slow 套件 195 passed；`test_module.py::test_rag -m slow` passed（33.77s），產物落在單一 `runs/{timestamp}/rag_build/nculab/...`（驗證第 3 點）；`test_main.py -m slow` passed（3m55s），log 顯示只建到「Index nodes: loaded from existing vector store」，沒有 query_engine 設定（驗證第 6 點）。

---

## 遺留事項

| 類別 | 說明 |
|---|---|
| `clean_vector_store()` 根本原因未釐清 | 無法重現當初的失敗案例，保留作為安全網；若想進一步簡化，需先補上能重現的情境（如 embedding 維度變更、程序異常中止留下鎖定檔） |
| `run_rag_query`／`run_agent_*` 未納入 `save`／`publish` | 本來就沒有 publish 機制，也不在 main workflow 範圍，刻意不動 |
| 驗證產生的真實資料 | 真實跑流程會更新 `data/rag/nculab/milvus.db` 並在 `runs/` 留下紀錄，是正常產物；`data/` 有被 git 追蹤，可用 `git checkout -- data/` 復原 |
| 伺服器啟動獨立於 main workflow | todo.md「流程優化」下一個獨立項目，不在範圍內 |
