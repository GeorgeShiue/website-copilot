# Main workflow log 優化計畫（nculab）

## Context

依實際跑一次 `uv run src/main.py --run.config-name nculab` 產生的完整 log（crawler → image summarizer → RAG build → agent server）分析 main workflow 的 log 雜訊與可觀測性缺口。

目標：讓一次 main workflow 的 log 能一眼看出「每階段做了什麼、花多久、哪裡失敗」，並移除無資訊量的重複與雜訊。**只改 logging，不改流程行為。**

整個優化分三輪進行，對應 `docs/work/todo.md` 的「優化 main workflow → 更新 log」：

- **Plan 1**（commit `969ca57`）：第一次雜訊清理，涵蓋爬蟲 verbose 輸出、第三方 WARNING/traceback 過濾、進度條、config 表過長、結尾 summary、Ctrl-C 處理。**已完成**（此輪之前完成，非本文件所述工作階段的產出）。
- **Plan 2**：比對 Plan 1 之後的真實 log，補齊仍缺漏的 log session（image summarizer 逐頁重複、exclude_words 過程無聲、RAG build 無起始段落、Agent 建置零散 INFO、Server 關閉無段落）。**已完成**。
- **Plan 3**：Plan 2 落地後再次跑真實流程比對，打磨遺留的細節（log 邏輯放錯模組、被拒絕的詞看不清楚、進度條看不出頁面、長頁名壓縮整張表、RAG Build Stats 與上方 config 面板重複）。**已完成**。

三輪的實際執行過程、驗證結果、以及過程中發現的 bug，記錄於 [dev.md](./dev.md)。

---

## Plan 1：初次雜訊清理與可觀測性缺口分析

> 本節為 Plan 1 的原始規劃內容（分析對象：一次完整 nculab 執行的 log，共 917 行）。

### 已確認的兩項檢查

**Error pages 是否在 debug log 內？ → 是，但 main workflow 看不到。**

`_filter_crawl_results`（`website_crawler.py`）對 404 與 `markdown is None` 都只用 `logger.debug` 記錄，且帶 URL。`main.py` 用 `setup_logging("info")`，app logger 為 INFO，所以這些 debug 訊息不會出現；只有 `cli.py`（`setup_logging("debug")`）才看得到。另外 `error_pages` 把 404 與「無 markdown」混算成同一個數字，無法分辨原因。

**是否需要 `llama-index-readers-file`？ → 不需要，且不應安裝。**

- 目前未安裝（`pyproject.toml` 只有 `llama-index` 主套件與 llms/vector-stores；venv 內無 `llama_index.readers`）。
- 該套件為 `.md` 提供 `MarkdownReader`，會**按標題切成多個 Document**，且預設 `remove_hyperlinks=True / remove_images=True`。目前行為是每個 `.md` 檔一份 Document，後面自己的 `MarkdownNodeParser` / `MarkdownImageExtractor` 才負責切分與抓圖；安裝後會改變索引內容並可能吃掉圖片說明。
- 警告出現次數等於檔案數的原因：`SimpleDirectoryReader.load_file` 對**每個檔案**都呼叫 `supported_suffix_fn()`，每次都重新嘗試 import 並失敗。傳入 `file_extractor` 無法避免。
- 結論：對 logger `llama_index.core.readers.file.base` 設 `ERROR`（或加 filter）即可，零行為變更。

### 問題與優化

#### A. 爬蟲（`src/app/engines/website_crawler.py`）

1. **crawl4ai 預設 verbose，每頁印 3 行（`[FETCH]/[SCRAPE]/[COMPLETE]`）**，且長 URL 被截斷。
   → `CrawlerRunConfig(verbose=False)`。正常頁面不逐頁列出，只保留結尾統計表與下面 A2、A3 的錯誤/重複明細。
   → 取捨（已確認）：關閉 verbose 後爬取期間沒有即時輸出；crawl4ai 內部的 `Some images failed to load within timeout` 訊息會一併消失（已決定不處理）。
2. **`error_pages` 沒有明細**。
   → 404 / no markdown 兩條路徑由 `logger.debug` 改 `logger.info`，帶 URL 與原因；統計表拆成 `error_404` / `error_no_markdown`。
3. **重複頁面靜默**（`?authuser=0` 等 URL 變體）。
   → 統計表保留；每個重複頁以 `logger.info` 印一行 `dup <URL> → <dedup_key>`（原為 debug）。

#### B. 圖片摘要（`src/app/engines/webpage_image_summarizer.py`）

4. **失敗訊息可讀性差**：403 的 URL 在 WARNING 裡折成多行，總表 `failure` 數字沒有指回是哪頁。
   → 失敗 URL 單行輸出；最後彙整「失敗清單：頁面 · URL · 原因」。
5. **`prompt` 設定表過長**，還被截斷、資訊不完整。
   → config 表對長字串截斷（共用 helper）。

#### C. RAG build（`src/app/engines/rag/rag_factory.py`）

6. **大量 `llama-index-readers-file package not found` WARNING**（每個 `.md` 檔一次）。
   → `setup_logging` 對 `llama_index.core.readers.file.base` 設 ERROR（理由見上方「檢查」）。**不安裝套件**，過濾統一放在 `setup_logging`（`main.py`、`cli.py`、測試三個入口一併生效）。
7. **gRPC `AllocTimestamp: Method not implemented!` traceback**（milvus-lite 內部，無害但看起來像失敗）。
   → 同樣在 `setup_logging` 對 `grpc._server` logger 設 CRITICAL。
8. **HF_TOKEN 警告 + 下載/載入進度條**。
   → `HF_HUB_DISABLE_PROGRESS_BARS=1`（`setup_logging` 以 `os.environ.setdefault` 設定）；HF 警告過濾。
9. **RAG build 耗時中大部分時間無可見輸出**（推測模型載入）。
   → 對「載入模型 / 切 node / 建 index」各包 `log_run_time`；並 log 實際載入的 embedding 模型（避免與 config 顯示的模型混淆）。

#### D. 共通（`src/utils/log_helper.py`、`src/main.py`）

10. **Config 表過長**：agent `system_prompt` 整段、RAG build 顯示用不到的欄位。
    → 長字串截斷（與 B5 共用 helper）；完整 config 已在 `module_config.toml`。
11. **結尾無總結、用詞誤導**：agent 初始化被印成 `Completed`；階段標題格式不一。
    → `main()` 結尾印 summary（各階段耗時、總花費、輸出路徑）；agent 初始化那行改為明確用詞。
    → 花費取得方式（已確認）：`log_helper` 新增簡單累加器（`record_cost` / 階段耗時），各 engine 在印統計表時順便登記；**不改任何 `run_*` 回傳型別**。
12. **Ctrl-C 印 `CancelledError` + `KeyboardInterrupt` traceback**。
    → `try: server.run() except KeyboardInterrupt:` 印一行訊息（`finally: chat_app.close()` 保留）。

### 已從計畫移除（依使用者決定）

- 爬蟲 `Some images failed to load within timeout`（不處理）
- 圖片摘要每頁表格與進度條（保持現狀——此決定後續在 Plan 2 被推翻，詳見下方）
- 圖片摘要慢頁辨識（保持現狀）
- tqdm 與 rich 輸出交錯（保持現狀，`show_progress` 不動）
- Run Paths 表（顯示、截斷、共用 run 目錄皆不動）
- 時間戳（不加，靠階段耗時行定位）

### 建議實作順序

1. 純雜訊消除：C6、C7、C8、D12。
2. 爬蟲：A1–A3。
3. 圖片摘要與 config 表：B4、B5、D10。
4. 耗時可觀測性：C9、D11。

### 關鍵檔案

- `src/utils/log_helper.py`：`setup_logging`（logger level / filter / HF 環境變數）、`log_run_time`、`print_log`；長字串截斷 helper 與花費累加器放這裡。
- `src/app/engines/website_crawler.py`：`_crawl_website_async`、`_filter_crawl_results`、統計表。
- `src/app/engines/webpage_image_summarizer.py`：下載失敗 WARNING、config 表。
- `src/app/engines/rag/rag_factory.py`：`SimpleDirectoryReader` 附近與模型載入段落。
- `src/main.py`：`main()` 結尾 summary 與 `KeyboardInterrupt` 處理。

### 驗證方式

- 重跑完整流程，比對總行數、`WARNING`/`ERROR` 行數、各區段行數是否明顯下降。
- 資訊不可流失：error 與 repeat 頁面都能在 INFO 層級找到 URL 與原因；每階段耗時與總花費都在結尾 summary。
- RAG 結果不變：載入文件數、產生 node 數不受影響（證明未改變 reader 行為）。
- 既有測試（`src/test/dev`）不因統計表鍵名拆分而壞掉（例如依賴 `_crawl_stats["repeat_pages"]` 的測試需保留鍵名不變）。

---

## Plan 2：補齊缺漏的 log session

### Context

Plan 1 已經建立 `log_helper.py` 的核心慣例：`log_session()` 印出 Rich `Rule` 作為段落標題、統計一律用 `Table` 搭配 `log_session(..., style="green")`、`log_run_time` / `record_cost` 累積最終的 Main Workflow Summary。

比對 Plan 1 落地後的真實 nculab log，發現幾處仍未套用這個慣例、或是慣例套用得太細（太多重複段落）。

### 1. 簡化 Image Summarization log

**檔案**：`src/app/engines/webpage_image_summarizer.py`

**問題**：`_summarize_crawl_results_images()` 對**每一個頁面**都呼叫一次 `log_session("Summarizing Images in [page]", style="blue")` + `_log_stats(self._page_stats)`，單次執行就印出 17 個幾乎重複的 5 列表格（cost_usd/success/download_failure/summarize_failure/cache_reuse），是當時最冗長的部分。

**改法**：
- 移除逐頁的 `log_session(...)` Rule 與逐頁的表格呼叫。
- 保留逐頁的下載/摘要進度條，維持即時進度可見性。
- 在迴圈中把每頁的 `_page_stats` 連同 `page_title` 累積進 `_page_stats_by_page`。
- 結束時改印**一張**含 Page 欄位的合併表格（每頁一列 + Total 一列），取代「17 個小表格 + 1 個彙總表格」。

**改動後 log 示意**：

```
──────────────────────────────────────────────────── Image Summarization ────────────────────────────────────────────────────
Downloading images... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 5/5 0.037s
Generating captions... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 5/5 6.974s
...（其餘頁面的進度條，逐頁跑但不再插入 Rule/表格）...
───────────────────────────────────────────────────── All Image Summarize Stats ─────────────────────────────────────────────
┃ Page                              ┃ cost_usd  ┃ success ┃ download_failure┃ summarize_fail  ┃ cache_reuse ┃
│ labintro                          │ $0.003412 │ 5       │ 0               │ 0               │ 0           │
│ ...（每頁一列）...                 │ ...       │ ...     │ ...             │ ...             │ ...         │
│ Total                             │ $0.092123 │ 73      │ 0               │ 0               │ 1           │
```

### 2. 新增 LLM Generated exclude_words 過程 log

**檔案**：`src/app/engines/webpage_markdown_cleaner.py`，`generate_exclude_words()`

**問題**：對 `repeat`（預設 5）次 LLM 呼叫完全沒有過程 log，只有失敗時的 `logger.warning`；成功的過程完全無聲，直到最終彙總表格才看得到結果。

**改法**：
- 函式開頭加 `log_session("Generating exclude_words", style="cyan")`。
- 每次 `_propose_words()` 成功後印一行過程訊息：第幾次（`i+1/repeat`）、取樣頁數、提出字數、花費。
- 失敗分支的 `logger.warning` 維持不變。

**改動後 log 示意**：

```
──────────────────────────────────────────────── Generating exclude_words ────────────────────────────────────────────────────
Run 1/5: sampled 5 pages, proposed 6 exclude_words (cost $0.0018)
Run 2/5: sampled 5 pages, proposed 7 exclude_words (cost $0.0019)
...
```

### 3. 新增 RAG build log session

**檔案**：`src/app/workflow/workflow.py`（`run_rag_build()`）與 `src/app/engines/rag/rag_factory.py`（`RAGBuilder.build_reusable()` 及其子步驟）

**問題**：`run_website_crawler()` / `run_webpage_image_summarizer()` 開始前都有對稱的 cyan 起始 Rule，但 `run_rag_build()` 沒有，只有內部較低層級的 `log_session("Building RAG", ...)`。同時，`build_reusable()` 的子步驟（clean/build_nodes/build_vector_store/build_index/build_retriever/build_query_engine）都是零散的 `logger.info`，沒有整合成表格。

**改法**：
- `run_rag_build()` 於呼叫 `create_rag(...)` 之前加上 `log_session("RAG Build", style="cyan")`，與結尾的 `"RAG Build Completed"` 對稱。
- `RAGBuilder` 新增 `self._build_stats` dict，各子步驟寫入一列，`build_reusable()` 結尾統一印出 `log_session("RAG Build Stats", style="green")` + Table，取代散落的 `"Successfully built ..."` 系列訊息。

**改動後 log 示意**：

```
──────────────────────────────────────────────────────── RAG Build ──────────────────────────────────────────────────────────   ← 新增
─────────────────────────────────────────────────────── Building RAG ────────────────────────────────────────────────────────
INFO     Clean vector store Completed in 0.000 seconds
INFO     Build nodes Completed in 1.201 seconds
INFO     Build vector store Completed in 9.841 seconds
INFO     Build index Completed in 24.668 seconds
──────────────────────────────────────────────────────── RAG Build Stats ────────────────────────────────────────────────────  ← 新增
┃ Metric             ┃ Value                                   ┃
│ Documents loaded   │ 47                                      │
│ Nodes produced     │ 279                                     │
│ Vector store       │ text-embedding-3-small, WeightedRanker  │
│ Index nodes        │ 279                                     │
│ Retriever          │ query_mode=hybrid                       │
──────────────────────────────────────────────────── RAG Build Completed ─────────────────────────────────────────────────────
```

### 4. 修改 Agent 建置過程 log

**檔案**：`src/app/agent/agent.py`，`create_agent()`

**問題**：`create_agent()` 內三個建置步驟（LLM、Checkpointer、Agent graph）各自用 `logger.info(...)` 分行輸出，不符合「session + table」慣例。

**改法**：
- 移除三行 `logger.info(...)`。
- 組裝完 `agent` 後新增一張 Table（2 欄 Config/Value），內容經與使用者確認後定案：
  - **LLM**（`config.llm_name`）
  - **Tools**（`[t.name for t in tool.tools]`）
  - **Knowledge bases**（`tool._registry.list_sites()`，plan 2 討論時發現這是完全沒有 log 的階段，一併補上）
  - （曾提出的 Registry 設定、Checkpointer 兩欄，使用者確認後決定不放入表格）

**改動後 log 示意**：

```
───────────────────────────────────────────────────── Agent Initialization ──────────────────────────────────────────────────
┃ Config          ┃ Value                                                                       ┃
│ LLM             │ gpt-5.6-luna                                                                │
│ Tools           │ ['list_knowledge_bases', 'webpage_retriever']                               │
│ Knowledge bases │ ['nculab']                                                                  │
```

### 5. 新增 Server Stop 之後的 log session

**檔案**：`src/main.py`

**問題**：server 關閉只有一行 `logger.info("Shutting down (KeyboardInterrupt)")`，且這行會晚於 uvicorn 自己印的關閉訊息才出現——因為 `uvicorn.Server.run()` 會先在內部完成 graceful shutdown 才把控制權交還。

**改法**（依使用者要求，改成按下 Ctrl+C 當下立即輸出，包住 uvicorn 自己的關閉訊息）：
- 在呼叫 `server.run()` 前 monkey-patch `server.handle_exit`（uvicorn 收到 SIGINT 時第一個呼叫的方法）：包一層 wrapper，先印 `log_session("Server Stopping", style="cyan")` 再呼叫原本的 `handle_exit`。
- `except KeyboardInterrupt:` 分支不再需要 log，改為 `pass`。
- `finally` 區塊 `chat_app.close()` 完成後印 `log_session("Server Stopped", style="cyan")` 收尾。

**改動後 log 示意**：

```
^C
────────────────────────────────────────────────────────── Server Stopping ──────────────────────────────────────────────────  ← 按下 Ctrl+C 當下立即輸出
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO     MilvusLite server stopped for .../milvus.db (port 36205)
────────────────────────────────────────────────────────── Server Stopped ───────────────────────────────────────────────────
```

### Plan 2 驗證方式

1. 對每個檔案改動執行對應的既有單元測試，確認沒有因為移除欄位或改變函式簽名而壞掉。
2. 實際執行完整流程，人工比對新的 log 與上述各節「改動後 log 示意」逐項吻合。

---

## Plan 3：打磨 Plan 2 的成果

### Context

Plan 2 落地後，再次跑真實 nculab 流程比對輸出，發現以下 5 個可以再打磨的細節，對應 `docs/work/todo.md` 已列出的 plan 3 項目。這一輪聚焦「把 log 邏輯放在正確的模組」「讓表格在真實終端寬度下可讀」「補齊還缺的上下文（頁面名稱）」「移除與上方 config 面板重複的資訊」。

### 1. generate_exclude_words() stats log 移動到 webpage_markdown_cleaner.py

**檔案**：`src/app/workflow/run_persistence.py`（`save_generated_exclude_words()`）→ `src/app/engines/webpage_markdown_cleaner.py`（`generate_exclude_words()`）

**問題**：exclude_words 的「過程 log」（Plan 2 新增，逐次 LLM 呼叫）在 `webpage_markdown_cleaner.py` 裡，但「結果統計 log」卻留在 `run_persistence.py::save_generated_exclude_words()`（該函式現在只該負責落盤 `generated_exclude_words.toml` / `exclude_words_report.json`）。同一件事的 log 被拆成兩個模組，且 `run_persistence.py` 混雜了「落盤」與「呈現」兩種職責，不利於未來「Webpage Markdown Cleaner 獨立成一個模組」。

**改法**：
- 把 `run_persistence.py` 現有的 `log_session("... Stats", ...)` 到最後 `print_log(table)` 整段移入 `generate_exclude_words()`，接在 `validate_words()` 之後、`return GenerationResult(...)` 之前。
- 順便處理下一點（合併 kept/rejected 成一張表）。
- `save_generated_exclude_words()` 之後只保留兩個檔案的寫入，移除不再需要的 `log_session` / `Table` / `print_log` / `escape` import；`hits` 計算保留（JSON 報告仍需要）。
- `workflow.py` 呼叫端不用改，函式簽名不變。

### 2.（併入上一點）優化 coverage validation log：kept/rejected 合併成一張表

**問題**：驗證通過的詞列在表格裡（Word/Votes/Hit lines/Low-occ ratio），被剔除的詞則用一行文字擠在一起印出（`Rejected by coverage validation: 'only0' (100.0%)`），詞一多這行會很長很難讀，也看不到被剔除詞的 Hit lines。

**與使用者確認的方向**：提出三個選項——(a) 合併成一張表、(b) 被剔除的詞另開一張小表、(c) 只在訊息裡加閥值數字——使用者選擇 (a)。

**改法**：
- 表格改列出 `ranked`（所有候選詞，依票數排序，含 kept 與 rejected）而非只列 `result.words`（kept）。
- 新增一欄 `Status`，值為 `Kept` 或 `Rejected`。
- 移除原本單獨一行的 `Rejected by coverage validation:` 文字。
- `hits` 改用 `self.count_word_hits(pages, ranked)`。

**改動後 log 示意**：

```
────────────────────────────────────────────────── Generating exclude_words Stats ───────────────────────────────────────────────────
Total 5 calls, cost: $0.0145
┃ Word                 ┃ Votes ┃ Hit lines ┃ Low-occ ratio ┃ Status   ┃
│ Search this site     │ 5     │ 47        │ 0.0%          │ Kept     │
│ Embedded Files       │ 5     │ 47        │ 0.0%          │ Kept     │
│ only0                │ 1     │ 3         │ 100.0%        │ Rejected │
```

### 3. download / generate image log 補上正在處理哪個頁面

**檔案**：`src/app/engines/webpage_image_summarizer.py`（`_download_images()`、`_agenerate_image_captions()`）

**問題**：Plan 2 移除逐頁 Rule 後，`Downloading images...` / `Generating captions...` 進度條變成一長串完全看不出目前在處理哪個頁面。

**改法**：
- `_current_page` 已經在 `_summarize_crawl_results_images()` 裡於呼叫下載/摘要前設定好，兩個進度條方法都是同一 instance 的方法，可直接讀取。
- `progress.add_task(...)` 的描述文字改為 `f"Downloading images... [{self._current_page}]"` / `f"Generating captions... [{self._current_page}]"`。
- 注意：`log_helper.py::_collapse_adjacent_progress_lines()` 用 `PROGRESS_LINE_PREFIXES` 做字首比對來摺疊寫入檔案時的連續進度列；加上頁面名稱後字首不變，摺疊邏輯不受影響。

**改動後 log 示意**：

```
Downloading images... [labintro] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 5/5 0.047s
Generating captions... [labintro] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 5/5 6.458s
```

### 4. All Image Summarize Stats 裁剪太長的 Page 名稱

**檔案**：`src/app/engines/webpage_image_summarizer.py`（`_log_page_stats_table()`）

**問題**：`Page` 欄位用 `no_wrap=True`，遇到長頁名（如 `news_校外奬項_賀邱威誠同學獲科技部108年度產學合作計畫成果發表暨績效考評會產學成果海報展示優良獎`）時，Rich 會把其餘 5 個統計欄位全部壓縮成 `…`，表格整個失去可讀性。

**改法**：
- 新增 `_truncate_page_title(title, max_len=40)`，超過 40 字元裁剪並加 `…` 後綴。
- 僅影響表格顯示，不影響 `_page_stats_by_page` 內儲存的原始 key。

**改動後 log 示意**：

```
# 改動前（其餘欄位全被壓成 …）
┃ Page                                                                                                         ┃ … ┃ … ┃ … ┃ … ┃ c… ┃

# 改動後
┃ Page                                     ┃ cost_usd  ┃ success ┃ download_failure ┃ summarize_failure ┃ cache_reuse ┃
│ news_校外奬項_賀邱威誠同學獲科技部108年…  │ $0.007040 │ 4       │ 0                │ 0                 │ 0           │
```

### 5. RAG Build Stats 移除 vector store / retriever / query_engine 的 log

**檔案**：`src/app/engines/rag/rag_factory.py`（`RAGBuilder.build_vector_store()` / `build_retriever()` / `build_query_engine()`）

**問題**：`RAG Build Stats` 表格裡的 `Vector store`、`Retriever`、`Query engine` 三列，內容跟同一次 run 上方已印過的 `RAGConfig Loaded from toml` 面板完全重複，純粹是雜訊。

**改法**：移除三個子步驟裡對應的 `self._build_stats[...]` 賦值，表格只留 `Documents loaded` / `Nodes produced` / `Index nodes`（真正的「這次建置產出了什麼」，而非「用了什麼設定」）。

**改動後 log 示意**：

```
────────────────────────────────────────────────────────── RAG Build Stats ──────────────────────────────────────────────────────────
┃ Metric           ┃ Value ┃
│ Documents loaded │ 47    │
│ Nodes produced   │ 277   │
│ Index nodes      │ 277   │
```

### Plan 3 驗證方式

1. 執行現有單元測試：`test_webpage_markdown_cleaner.py`（含 `save_generated_exclude_words` 相關測試）、`test_rag_tools.py`、`test_image_failure_summary.py`、`test_log_helper.py`。
2. 由實作者自行執行一次完整流程（crawler → image summarizer → RAG build），將產出的 log 與本文件各節「改動後 log 示意」逐項比對；若不符直接修正後重跑，不用等使用者確認。

---

## 總覽：三輪計畫對應 todo.md 項目

| 輪次 | todo.md 項目 | 狀態 |
|------|-------------|------|
| Plan 1 | 更新 log — plan 1 | ✅ 已完成（commit `969ca57`） |
| Plan 2 | 簡化 Image Summarization log / 新增 exclude_words 過程 log / 新增 RAG build log session / 修改 Agent 建置過程 log / 新增 Server Stop log session | ✅ 已完成 |
| Plan 3 | log 搬移到正確模組 / kept-rejected 合併表 / 進度條補頁面 / 長頁名截斷 / RAG Build Stats 去重複 | ✅ 已完成 |
| Plan 4（後續，不在本文件範圍） | 包裝 `log_helper.py` | 進行中，另行記錄 |
