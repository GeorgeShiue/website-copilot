# Main workflow 優化：實作規劃（nculab）

## Context

對應 `docs/work/todo.md`「優化 main workflow」底下三個項目，起點都是 `src/main.py` 的正式流程（`run_website_crawler` → `run_webpage_image_summarizer` → `run_rag_build` → agent server）。三個項目合併於此，實作紀錄見 [dev.md](./dev.md)。

| 部分 | 主題 | 狀態 |
|---|---|---|
| A | Log 優化（三輪） | ✅ 已完成 |
| B | 留檔機制（`save`／`publish`、crawler 與 summarizer 儲存路徑拆分） | ✅ 已完成 |
| C | RAG 建置流程（六項） | ✅ 已完成 |

通用原則：A 只改 logging，不改流程行為；各項的驗證方式見最後一節。

---

## A. Log 優化

目標：讓一次 main workflow 的 log 能一眼看出「每階段做了什麼、花多久、哪裡失敗」，並移除無資訊量的重複與雜訊。慣例：段落標題用 `log_session()`，統計一律用 Rich `Table`。

### A-1：初次雜訊清理（commit `969ca57`，先前工作階段完成）

分析一次完整 nculab 執行的 log（917 行）後確認：

- **error pages 在 debug log 內，main workflow 看不到**：`_filter_crawl_results` 對 404 與 `markdown is None` 只用 `logger.debug`，且兩種原因混算成同一個數字。
- **不需要也不應安裝 `llama-index-readers-file`**：它會把 `.md` 按標題切成多個 Document 並預設移除連結與圖片，改變索引內容；警告每個檔案出現一次是因為 `SimpleDirectoryReader` 每檔都重新嘗試 import。零行為變更的做法是對該 logger 設 `ERROR`。

優化項目：

| 範圍 | 做法 |
|---|---|
| 爬蟲 | `verbose=False`（取捨：爬取期間沒有即時輸出，crawl4ai 的 images timeout 訊息一併消失，已決定不處理）；404／no markdown 改 `logger.info` 帶 URL 與原因，統計表拆成 `error_404`／`error_no_markdown`；重複頁以 info 印一行 `dup <URL> → <dedup_key>` |
| 圖片摘要 | 失敗 URL 單行輸出，結尾彙整「失敗清單：頁面 · URL · 原因」；config 表長字串截斷（共用 helper） |
| RAG build | `setup_logging` 對 `llama_index.core.readers.file.base` 設 ERROR、對 `grpc._server` 設 CRITICAL（milvus-lite 內部無害 traceback）；`HF_HUB_DISABLE_PROGRESS_BARS=1`；模型載入／切 node／建 index 各包 `log_run_time`，並 log 實際載入的 embedding 模型 |
| 共通 | config 表長字串截斷；`main()` 結尾印 summary（各階段耗時、總花費、輸出路徑），花費用 `log_helper` 的簡單累加器（`record_cost`），**不改任何 `run_*` 回傳型別**；Ctrl-C 只印一行訊息，不印 traceback |

依使用者決定從計畫移除：爬蟲 images timeout 訊息、圖片摘要每頁表格與進度條（後來 A-2 推翻）、慢頁辨識、tqdm 與 rich 輸出交錯、Run Paths 表、時間戳。

### A-2：補齊缺漏的 log session

| 項目 | 檔案 | 做法 |
|---|---|---|
| 1. 簡化 Image Summarization log | `webpage_image_summarizer.py` | 原本每頁一個 Rule 加一張 5 列表格（單次 17 張），改為保留逐頁進度條，結尾印**一張**含 Page 欄的合併表（每頁一列加 Total） |
| 2. exclude_words 過程 log | `webpage_markdown_cleaner.py` | `generate_exclude_words()` 開頭加 session，每次 LLM 呼叫成功印一行（第幾次／取樣頁數／提出字數／花費） |
| 3. RAG build session | `workflow.py`、`rag_factory.py` | `run_rag_build()` 加對稱的起始 session；`RAGBuilder` 累積 `_build_stats`，`build_reusable()` 結尾印一張 Stats 表，取代零散的 `Successfully built ...` |
| 4. Agent 建置 log | `agent.py` | 三行 INFO 改成一張表：LLM、Tools、Knowledge bases（`tool._registry.list_sites()`） |
| 5. Server Stop session | `main.py` | Ctrl+C 當下立即印 `Server Stopping`（monkey-patch `server.handle_exit`），`chat_app.close()` 後印 `Server Stopped` |

### A-3：打磨 A-2 的成果

1. **exclude_words 統計 log 搬到 `webpage_markdown_cleaner.py`**：結果統計原本留在 `run_persistence.py::save_generated_exclude_words()`，與過程 log 分在兩個模組，且落盤與呈現職責混雜。搬移後 `save_generated_exclude_words()` 只負責寫檔。
2. **kept／rejected 合併成一張表**：原本被剔除的詞擠成一行文字、看不到 Hit lines。使用者從三個選項中選了「合併成一張表」，表格列出所有候選詞，新增 `Status`（Kept／Rejected）欄。
3. **進度條補上頁面名稱**：`Downloading images... [page]`、`Generating captions... [page]`；`_collapse_adjacent_progress_lines()` 用字首比對，不受影響。
4. **長頁名截斷**：`Page` 欄用 `no_wrap`，長頁名會把其餘統計欄全部壓成 `…`。新增 `_truncate_page_title(title, max_len=40)`，只影響顯示。
5. **RAG Build Stats 去重複**：移除 Vector store／Retriever／Query engine 三列（與上方 config 面板重複），只留 Documents loaded／Nodes produced／Index nodes。

---

## B. 留檔機制

### B-1：`save`——讓 `runs/` 儲存變成可選

**問題**：三個 `run_*` 函式無條件寫 `runs/`（`results.json`、markdown、`module_config.toml`、`run_config.toml`），`data_manager is not None` 只決定要不要「額外」publish 到 `data/`，所以 main workflow 每次都在 `runs/` 留下永遠不會被讀取的複本。

**設計**：

1. 三個函式新增 `save: bool = True`。
2. `save=False` 時**完全不建立 `runs/` 目錄**（不只是跳過結果檔）：`create_run_context` 回傳 `(None, run_title)`，型別改成 `RunManager | None`；`run_workflow_context` 在 `run_manager is None` 時跳過 log 檔操作。
3. 所有「存到 runs/」的呼叫合併進同一個 `if save:` 區塊，放在 publish 之前，讓 Save／Publish 兩階段在程式碼上明確區分。
4. `DataManager` 的 publish 方法原本是複製 `runs/` 已寫好的檔案，與「不留複本」矛盾，改為**直接從記憶體物件序列化**（`results`／`config`／`run_config`），並刪除變成死碼的 `publish_module_config`／`publish_run_config`／`publish_log`。
5. `run_rag_build` 移除獨立的 `save_vector_store_to_runs`，統一由 `save` 驅動：`save=True` 向量庫建在 `runs/`，`save=False` 直接建在 `data/rag/{site_id}/milvus.db`，`publish_vector_store` 的 `realpath` 自我複製防護使 publish 成為 no-op。
6. `BaseRunConfig` 新增 `save`；`cli.py` 比照 `publish` 把它從 `run_kwargs` pop 出來，避免洩漏進沒有此參數的分支。
7. `main.py` 三個呼叫都加 `save=False`。

### B-2(a)：統一 RunManager／DataManager 的建立模式

兩者不一致的原因不是偶然，而是本質不同：

- **生命週期**：`RunManager` 是單次呼叫自己的執行紀錄；`DataManager` 代表 site 已發布的狀態，橫跨整個 pipeline。
- **建立成本**：`RunManager.for_run` 會建立整棵時間戳目錄樹；`DataManager()` 只 `makedirs("data")`。
- **用途不對稱**：`run_rag_build` 中 `data_manager` 在 `webpages_data_use_latest_results=True` 時還用來**讀取**資料來源路徑，與是否 publish 無關。

**設計**：

1. 三個函式內直接 `DataManager()` 建立，**不**包工廠函式（曾引入 `create_data_manager()`，因內容只有一行而拿掉）。
2. `data_manager` 參數改為 `publish: bool = False`，與 `save` 對稱。
3. `DataManager` 永遠建立，讀取與 publish 因此解耦。
4. `main.py`／`cli.py`／`scripts/multi_site.py` 移除手動建構，傳 `publish=True`（cli 為 `publish=publish`）。
5. `multi_site.py::_check_published_files` 實際只讀 `.base_folder`，簡化成吃 `base_folder: str`。

不建議把 `DataManager` 建立併入 `create_run_context`：兩者建立條件獨立，且 `run_rag_query`／`run_agent_*` 等呼叫端不需要 `DataManager`，合併還會讓測試互相耦合。

### B-2(b)：crawler 與 summarizer 儲存路徑拆分

**問題**：`publish_crawl_results` 與 `publish_markdown` 原本都寫到 `data/webpages/{site_id}/results/`，crawler 的原始輸出（`fit_markdown`）被 summarizer 的 `enhanced_markdown` 覆蓋。`runs/` 沒有此問題（路徑本來就含 module 名稱與各自的時間戳），不需調整。

**設計（最終定案）**：

- `data/raw_webpages/{site_id}/`：crawler 專屬，存 `results.json`（僅原始欄位）、`results/*.md`（`fit_markdown`）、`module_config.toml`／`run_config.toml`／`terminal.log`／`generated_exclude_words.toml`／`exclude_words_report.json`。
- `data/webpages/{site_id}/`：結構與路徑不變，改由 summarizer 完整發布，`publish_markdown` 除 `results/*.md`（`enhanced_markdown`）外也寫 `results.json`。可行是因為 summarizer 是**就地**在 `crawl_results` 每頁 dict 疊加 `enhanced_markdown` 再回傳同一個物件。
- RAG 完全不用改。

順便修正既有 bug：`multi_site.py::run_site_pipeline` 傳給 `_check_published_files` 的是 config 名稱（如 `test_nculab`），實際 `site_id` 是 `nculab`，驗證一直在檢查錯誤目錄，改傳 `site_label`。

---

## C. RAG 建置流程

沿著「建置流程」逐一往下追，涵蓋 todo.md 該分類全部六項：

| # | 問題 | 設計 |
|---|---|---|
| 1 | `run_rag_build()` 不需要 query_engine，卻會多建一次 LLM 與 `RetrieverQueryEngine` | `RAGBuilder` 拆出 `build_to_vector_store()`，`build_to_query_engine()` 疊在其上；`create_rag()` 新增 `build_query_engine: bool = True`，`run_rag_build()` 傳 `False` |
| 2 | `save=True` 時向量庫路徑必為全新路徑，`force_rebuild` 形同虛設 | `run_rag_build()` 的語意本來就是「確定要重建」，移除 `force_rebuild` 參數、內部固定傳 `True`；`save` 只管落盤位置。`create_rag`／`RAGBuilder`／`run_rag_query` 不動（`run_rag_query` 需要「有既有向量庫就重用」） |
| 3 | `run_rag_build()` 與 `create_rag()` 各自建 `RunManager`，`run_name` 計算不一致，產物可能落在不同 run 資料夾 | `create_rag()` 的 `save` 參數改為 `run_manager: RunManager \| None`，直接用傳入物件決定 `milvus_uri` |
| 4 | `run_rag_build`／`run_rag_query` 與 `create_rag()` 內部重複解析 `RAGConfig` | `create_rag()` 新增 `config: RAGConfig \| None`，傳入時沿用 |
| 5 | 整檔刪除 milvus.db 後 collection 必不存在，`build_vector_store(overwrite=True)` 的 `overwrite` 已無作用 | 移除 `overwrite` 參數（固定 `False`），**保留** `clean_vector_store()` |
| 6 | `webpage_retriever` 只用 `rag.retrieve()`，但 `RAGRegistry.get()` 建到 query_engine 層級 | 新增 `build_to_retriever()`，`build_to_query_engine()` 疊在其上，`RAGRegistry.get()` 改呼叫前者 |

---

## 驗證方式

共同：`ruff check src`、`pyright`（需指定 venv 的 python）、非 slow 測試套件。

- **A**：實際跑一次完整流程（headless 預設 80 欄寬度無法暴露表格問題，需用 `COLUMNS=150` 模擬真實終端），將產出 log 與預期逐項比對。資訊不可流失：error 與 repeat 頁面能在 INFO 層找到 URL 與原因；RAG 載入文件數與 node 數不受影響。
- **B**：`runs/` 完全沒有新增目錄或檔案；`data/raw_webpages/{site_id}/results.json` 每頁只有 `fit_markdown`，`data/webpages/{site_id}/results.json` 每頁同時有 `fit_markdown` 與 `enhanced_markdown`；兩邊 `results/*.md` 內容分別對應各自 JSON 欄位。
- **C**：`test_rag_tools.py`、`test_run_rag_build_publish.py`；`pytest src/test/test_module.py::test_rag -m slow`（確認 log／config／milvus.db 落在同一個 run 資料夾）；`test_main.py -m slow`（完整流程，確認 agent 觸發 `RAGRegistry` cache miss 時只建到 index 層級）。第 5 項另用真實 `VectorStoreBuilder.build()` 實測三種情境。
