# 程式碼清理 plan

> 對應 [todo.md](../../todo.md)「技術債」。本次只處理冗贅程式碼（死碼、重複實作），不改功能。

## Context

`dev-tech-debt` 分支歷經專案重構（plan 1～4）、模組配置重構（Phase A～D）與資料儲存重構（Phase 1～2），每輪都刪除了舊實作，但新舊交接處仍留下：

1. **死碼**：重構後已無呼叫端的方法、參數與常數（如 `DataManager` 的 Discover 方法、`build_rag` 的 `force_rebuild` 分支）。
2. **重複實作**：同一邏輯在多處各寫一份（路徑規則、runs/ 搜尋、config loader、Agent 結果組裝等）。
3. **零碎殘留**：未使用的 logger、空殼類別、「向後相容」的 property 與 context manager。

依「是否明確可改」與「現有驗證機制（`scripts/check.sh`：ruff + pyright + `tests/unit`）能否覆蓋」分為三組：

| 組別 | 定義 | 處理方式 |
|---|---|---|
| A ✅ | 無需設計取捨、不改變任何輸出（落盤檔案格式、runs/ 資料夾名稱、log），且 `check.sh` 可驗證 | 本次實作 |
| B ⚠️ | 測試可覆蓋，但需先做設計決策 | 決策後本次實作（見「待決策」） |
| C ❌ | 現有驗證無法覆蓋，或會改變輸出 | 本次不做；列出前置條件 |

純刪除類變更主要由 pyright 把關：被刪除的名稱若仍有引用，型別檢查直接失敗。

## A 組：明確可改且可驗證

### A1：刪除死碼

| 項目 | 位置 | 驗證 |
|---|---|---|
| 未使用的 `logger`（6 個） | `config/{agent,rag,image_summarizer,website_crawler}_config.py`、`storage/run_manager.py`、`utils/config_helper.py` | ruff、pyright |
| `KEEP_TITLE_CONTENT_THRESHOLD` | `config/website_crawler_config.py` | pyright |
| `storage/__init__.py` 的 re-export（無人經由套件 import） | `storage/__init__.py` | pyright、`test_imports` |
| `DataManager.get_vector_store_path`／`list_sites`／`get_webpages_path`／`site_exists` | `storage/data_manager.py` | pyright（全專案無引用） |
| `save_results_as_md` 的 `save_images` 參數 | `storage/run_persistence.py` | pyright |
| `Agent.tools` property、`checkpointer or InMemorySaver()` | `agent/agent.py` | pyright |
| `Tool`／`Agent`／`ChatApp` 的 `__enter__`／`__exit__` | `agent/tools/tool.py`、`agent/agent.py`、`server/app.py` | pyright（有 `with` 使用時報錯）、`test_chat_app_close_closes_agent` |
| `create_run_no_site_context` 的 `run_name` 參數與呼叫端多餘的 `base_folder="runs"` | `storage/run_context.py`、`pipelines/{serve,exp}.py` | pyright、`test_pipeline_serve`、`test_pipeline_exp` |
| `RunManager.__init__` 的可選 `module_name` 與 `init_module_run_paths` 中走不到的檢查 | `storage/run_manager.py` | `test_run_manager`、`test_pipeline_prepare` |
| `run_rag_query` 的 `except` 中重複的 `rag.close()`（`finally` 已關閉；`RAG.close()` 可重入） | `pipelines/exp.py` | `test_pipeline_rag_query` |
| `IndexBuilder.load` 的 `if vector_store_type == "milvus"`、`_close_vector_store` 的 `isinstance`（`vector_store_type` 為單值 `Literal["milvus"]`） | `ingestion/indexing/index.py` | `test_index_close`（真實 Milvus Lite）、`test_serve_rag_loading` |

### A2：簡化 `build_rag` 與 `IndexBuilder`

資料儲存重構 Phase 1 後，`build_rag` 唯一呼叫端為 `run_rag_build`，且固定 `force_rebuild=True, build_query_engine=False`。

- `build_rag(config, target)`：只做「讀來源 → `IndexBuilder.build()` → `RAG(handle)`」；移除 `force_rebuild`、`build_query_engine` 參數與 query engine 分支。
- 刪除 `IndexBuilder.build_or_load()`、`_should_rebuild()`；讀取來源（`load_source`）移到 `build_rag`，維持「先讀來源、再清除舊向量庫」的順序。
- 測試調整：
  - 刪除 `TestShouldRebuildMilvus`（4 個，測試對象即被刪除的死碼）。
  - `test_rebuild_reads_source_before_cleaning` 改呼叫 `build_rag`，斷言不變（`results.json` 不存在時，`clean` 不被呼叫）。
  - `test_build_rag_does_not_modify_config` 與 `test_pipeline_prepare` 的 fake `build_rag` 改用新簽名。

### A3：合併重複實作

| 項目 | 做法 | 驗證 |
|---|---|---|
| `MARKDOWN_IMAGE_PATTERN` 兩份（crawler、summarizer） | 保留一份，另一處 import | pyright |
| `publish_crawl_results` 與 `publish_markdown` 除資料夾名稱與 markdown key 外相同 | 抽出 `_publish_results(site_id, category, results, markdown_key)`，兩個公開方法保留為一行包裝（呼叫端不變） | `test_node_pipeline_metadata.test_publish_removes_stale_markdown`（兩個方法皆參數化測試，`9614b38` 新增） |
| `RESULTS_JSON_NAME` 兩份（`run_manager`、`run_persistence`） | 保留一份 | pyright |
| 時間戳資料夾判斷 `startswith("20") and len == 15` 兩份 | 抽成 `run_persistence.is_run_folder()`，`RunManager.find_thread_history_path` 共用 | `test_run_manager`（跨 run 搜尋）、`test_run_persistence`、`test_build_target_uses_latest_summarizer_run_of_same_site` |
| `base_config._is_section`／`_section_model` 與 `overrides._section_type` | 保留 `_section_type`（涵蓋 `Model \| None`），`base_config` 改用 | `test_overrides`、`test_configs` 的 run_name_fields 檢查 |
| `SiteConfig.from_yaml` 與 `BaseModuleConfig.from_yaml` 的「validate → `format_validation_error` → 設 `_source`」 | 抽出共用函式（`base_config.validate_loaded(cls, data, source)`）；`_source`／`source` 移到共用 mixin | `test_site_config`、`test_configs`、`test_config_extends`（錯誤訊息格式皆有斷言） |

### A4：結構簡化

| 項目 | 做法 | 驗證 |
|---|---|---|
| `ChatApp` 以 lifespan + `app.state` + `Depends` 傳遞 agent／run_manager | 路由直接使用 `_build_fastapi_app` closure 中的 agent／run_manager | `test_agent_server`（TestClient 走完整 SSE 流程） |
| `_WorkflowContext` 包裝 `ExitStack` | 改為 `@contextmanager`；保留「僅成功時印 complete 路徑表」的行為與 `log_path` 參數（`9614b38` 新增，供 publish-only 的暫存 log） | 所有 pipeline 測試皆經過 `run_workflow_context`；`test_publish_log` 直接測試 `run_workflow_context` 的 log 內容 |

## B 組：已確認決策

| # | 項目 | 選項 | 決策 |
|---|---|---|---|
| B1 | `vector_db`／`aug_webpages` 路徑規則散落於 `DataManager`、`factory`（`published_target`／`vector_store_run_target`／`build_target`）、`registry` | (a) 由 `DataManager` 提供；(b) 新增無副作用的 `storage/data_paths.py` 純函式模組，`DataManager`／`factory`／`registry` 共用 | **(b)** |
| B2 | `load_latest_results` 與 `load_latest_run_path` 的走訪迴圈重複 | (a) 抽出共用的「由新到舊列出 `runs/<ts>/<module>/<site_id>/`」，兩個公開函式與語意不變；(b) 合併成單一 `find_latest_run_path`，`load_latest_results` 改為讀其 `results.json` | **(a)** |
| B3 | `run_agent_query` 在問答**之後**才產生 auto thread_id，落盤 id 與實際對話 id 不同；auto id 產生邏輯共三份 | (a) 問答前產生並傳入 `ask`／`astream_result`，落盤沿用同一個；(b) 同 (a)，並新增 `new_thread_id()` 供 `thread_config`／exp／server 共用；(c) 維持現狀 | **(b)** |
| B4 | `{query, response, sources, timestamp}` 在 `Agent.ask`／`Agent.astream_result`／server `_event_stream` 各組一次；server 重做「`get_state` → `extract_sources`」 | (a) 抽出模組層級 helper（組 result dict、從 graph state 取 sources），三處共用，server 串流方式不變；(b) server 改用 `astream_result`（需重新設計為可逐 token yield 的介面）；(c) 維持現狀 | **(a)** |

### B1：`storage/data_paths.py`

- 理由：`DataManager.__init__` 會 `os.makedirs(base_folder)`；若 serve 階段的 `RAGRegistry` 改用 `DataManager`，查路徑就可能建立 `data/`，違反「serve 只讀」。純函式沒有副作用。
- 內容：`VECTOR_DB_FOLDER`、`AUG_WEBPAGES_FOLDER` 常數，`vector_store_path(site_id, data_folder="data")`、`aug_webpages_path(site_id, data_folder="data")`、`vector_db_folder(data_folder="data")`。
- 改用者：`DataManager`（`vector_store_path`、`create_vector_store_staging`、`publish_*`）、`factory.published_target`／`vector_store_run_target`／`build_target`、`RAGRegistry._site_exists`／`list_sites`。
- 只 import `os`，不違反 `test_imports` 的 serve 路徑限制。
- 驗證：`test_published_target`、`test_build_target_defaults_to_published_webpages`、`test_vector_store_path`、`TestListSites`、`test_serve_rag_loading`、`test_pipeline_prepare`。

### B2：共用 runs/ 走訪

- 理由：合併會改變邊界行為（有 `results/` 但無 `results.json` 的失敗 run：現行 `load_latest_results` 會跳過、改用較舊的 run；合併後會選到該 run 而報錯）。
- 抽出 `_iter_module_site_folders(base_folder, module_name, site_id)`：由新到舊 yield `runs/<ts>/<module>/<site_id>/`（使用 A3 的 `is_run_folder()`）；兩個公開函式只保留各自的判斷。
- `load_latest_run_path` 的 `site_id` 改為必填（唯一呼叫端 `build_target` 一定會傳）。
- 驗證：`test_run_persistence`、`test_build_target_uses_latest_summarizer_run_of_same_site`、`test_image_summarizer_loads_latest_results_of_same_site`。

### B3：`new_thread_id()`

- 理由：落盤的 `results_auto-xxx.json` 與實際對話 id 不同，無法以該 id 續接對話。單輪問答輸出不變，只是落盤 id 變正確。
- `agent/langchain_helper.py` 新增 `new_thread_id() -> str`（`auto-{uuid8}`）；`thread_config(None)`、`run_agent_query`、server `chat` 共用。
- `run_agent_query`：`thread_id = run_config.thread_id or new_thread_id()` 移到問答前，傳給 `ask`／`astream_result` 與落盤。
- 測試：`test_run_agent_query_auto_generates_thread_id` 增加斷言「`ask` 收到的 thread_id 與落盤的相同」；`test_chat_sse_streams_tokens_and_done` 不修改即通過。
- 屬行為修正（落盤 id），完成後需跑一次付費整合測試 `test_agent_query`。

### B4：模組層級 helper

- 理由：server 必須逐 token yield，`astream_result` 的 callback 介面無法直接沿用；改為模組函式（直接接收 `graph`）可讓 `test_agent_server` 的 `_FakeAgent`（只有 `graph`／`config`／`astream_text`）不必修改。
- `agent/agent.py` 新增：
  - `build_result(query, response, messages) -> dict`：組 `{query, response, sources, timestamp}`（`sources` 由 `extract_sources_from_messages` 取得）。
  - `state_messages(graph, config) -> list`：`graph.get_state(config)` 後取 `messages`（state 為空時回傳 `[]`）。
- `Agent.ask`、`Agent.astream_result`、server `_event_stream` 改用上述兩者；dict 欄位與順序不變（`save_agent_results_as_json` 落盤格式不變）。
- 驗證：`test_agent_server`、`test_pipeline_exp` 不修改即通過。

## C 組：本次不做

| 項目 | 不做的原因 | 前置條件 |
|---|---|---|
| `ImageSummarizer` 三份快取（`_image_cache`／`_downloaded_images`／`_image_captions`）與三種統計 dict 合併 | 模組無單元測試 | 先補單元測試（mock `urlopen`／`acompletion`） |
| `ImageSummarizer._agenerate_image_caption_task` 每個 task 各建一個 `Semaphore`（**bug**：`vlm_max_workers` 無法限制並行數） | 屬修正而非清理；無測試 | 補並行數測試後單獨一個 commit 修正 |
| Rich「Metric／Value」表格抽成 `log_helper` helper（約 6 處） | 無 log 輸出測試，只能目測 | 併入 todo「包裝 log_helper.py」 |
| LLM 供應商路由（關鍵字 → API key 環境變數 → litellm 前綴）收斂為一張表 | 兩個 `create_llm` 與 `_get_api_key` 無測試 | 先補單元測試 |
| `evaluation.extract_sources_list` 與 `RAG.retrieve` 的來源 dict 共用 | 無測試；key 順序不同，合併會改變 results.json 欄位順序 | 確認可接受格式變動 |
| prepare pipeline 樣板（`save_*_config` 三行 ×4）改用 `write_run_metadata`（`log_path` 三元式已由 `9614b38` 的 `publish_log_file` 取代） | crawler／summarizer 的 save 路徑無單元測試；且 `RunManager.log_path` 即 `run_path/terminal.log`，`shutil.copy2` 複製到同一檔案會拋 `SameFileError`，不能直接替換 | 補測試，`write_run_metadata` 處理同檔案情況 |
| `VectorStoreBuilder.default_hybrid_ranker_params` | 非真正重複：設定檔寫 `null` 時依此補內建值 | — |
| `run_rag_query` 結果的 `config` 改用 `model_dump()`、移除只 log 後 re-raise 的 `except` | 改變 results.json 格式與失敗 log | 確認可接受格式變動 |
| 刪除空殼 `WebsiteCrawlerRunConfig`／`ImageSummarizerRunConfig` | 影響 tyro `--help` 與 `run_config.yml`；13 處測試引用 | — |
| `RAGConfig._post_process_run_name` 的 `-gemini` 特例 | 改變 runs/ 資料夾名稱；`test_run_name` 未涵蓋 gemini | 確認可接受命名變動 |

## 執行順序

依序執行（commit 的切分與合併見「Commit 策略」）：

| 順序 | 內容 | 依賴 |
|---|---|---|
| 1 | A1 刪除死碼 | — |
| 2 | A2 簡化 `build_rag`／`IndexBuilder` | — |
| 3 | A3 合併重複實作 | — |
| 4 | A4 結構簡化 | A1（`ChatApp` 的 context manager 已刪除） |
| 5 | B1 `storage/data_paths.py` | A1（Discover 方法已刪除） |
| 6 | B2 共用 runs/ 走訪 | A3（`is_run_folder()`） |
| 7 | B3 `new_thread_id()` | — |
| 8 | B4 模組層級 helper | B3（同檔案，避免衝突） |

## Commit 策略

實作期間每項一個 commit（A1～A4、B1～B4），方便逐項審核與定位問題；各組全部完成並審核後，再合併成一個 commit：

1. **A 組**：開始前記下基準點（`git rev-parse HEAD`，即 A1 之前的 commit）。A1～A4 依序各自 commit，每個都通過共同關卡。
2. A 組全部審核通過後，以 `git reset --soft <A 組基準點>` 收回 A1～A4，再重新 commit 成單一 commit：`refactor: remove dead code and merge duplicates (code cleanup A)`；訊息內文逐行列出 A1～A4 的內容。
3. 合併後再跑一次共同關卡（確認內容與合併前的 A4 commit 相同：`git diff <A4 commit> HEAD` 應為空）。
4. **B 組**：以合併後的 A commit 為基準點，B1～B4 依序各自 commit，流程同 1～3；合併後的訊息為 `refactor: centralize data paths, share runs/ lookup and agent result helpers (code cleanup B)`。
5. 付費整合測試於 B 組合併後執行一次（見「付費整合測試」）。

注意：

- 不使用 `git rebase -i`（環境不支援互動式指令）；以 `git reset --soft` 合併。
- 合併前不 push；若已 push 到遠端，合併會改寫歷史，須先與使用者確認。
- 各項的實作紀錄寫在 `dev.md`，以 A1～A4／B1～B4 分節，合併 commit 後不受影響。

## 驗證

### 共同關卡（每個 commit，含合併後的 commit，都必須通過）

- `scripts/check.sh` exit 0（ruff、pyright、`tests/unit`、widget 同步）。
- `uv run pytest tests/integration -m "not cost"` 通過。
- CLI 冒煙：`website-copilot prepare --help`、`serve --help`、`run {website-crawler,image-summarizer,rag-build,rag-query,agent} --help` 皆 exit 0。

### 額外檢查

- A1：grep 被刪除的名稱，確認只剩文件中的歷史紀錄。
- A2：grep `force_rebuild`、`build_or_load`、`_should_rebuild`，src／tests 皆無結果。
- A3：`test_configs`、`test_site_config` 的錯誤訊息斷言不修改即通過（訊息格式不變）。
- A4：`test_agent_server` 不修改即通過。

### 付費整合測試

A 組與 B1／B2／B4 不改變行為，不需要付費測試。B3 修正了落盤的 thread_id，全部完成後跑一次 `uv run pytest tests/integration`（需使用者確認），涵蓋 `test_agent_query` 與 `test_serve`。
