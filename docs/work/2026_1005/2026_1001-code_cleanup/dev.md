# 程式碼清理：實作紀錄

> 計畫見 [plan.md](./plan.md)。A 組基準點：`dc52401`（plan 與 `KEEP_TITLE_CONTENT_THRESHOLD` 文件紀錄）。

## A1：刪除死碼

### 變更

- 刪除 6 個未使用的 `logger`（`config/{agent,rag,image_summarizer,website_crawler}_config.py`、`storage/run_manager.py`、`utils/config_helper.py`）與隨之未使用的 `import logging`。
- 刪除 `KEEP_TITLE_CONTENT_THRESHOLD`；值 `0.45` 記錄於 `docs/code/phase1/modules/data_collect.md` 補充說明。
- `storage/__init__.py` 移除 re-export，只留模組 docstring（全專案無人經由 `website_copilot.storage` 匯入）。
- `DataManager` 刪除 `get_vector_store_path`／`list_sites`／`get_webpages_path`／`site_exists`（整個 Discover 區塊）。
- `save_results_as_md` 移除 `save_images` 參數與其寫入圖片清單的分支。
- `Agent`：刪除 `tools` property、`__enter__`／`__exit__`；`checkpointer` 改為必填（唯一呼叫端 `create_agent` 一定傳入），移除 `or InMemorySaver()`；`Tool`、`ChatApp` 的 `__enter__`／`__exit__` 一併刪除。
- `create_run_no_site_context` 移除 `run_name` 參數；`run_server_build`、`run_agent_query` 移除多餘的 `base_folder="runs"`。
- `RunManager.__init__` 的 `module_name` 改為必填，初始化時直接建立 module 路徑；刪除 `init_module_run_paths` 中走不到的 `module_name` 檢查（保留 `run_name` 檢查：run name 欄位全為 None 時會得到空字串，仍可能觸發）。
- `run_rag_query` 的 `except` 內刪除重複的 `rag.close()`（`finally` 已關閉）。
- `IndexBuilder.load` 移除 `vector_store_type == "milvus"` 判斷、`_close_vector_store` 移除 `isinstance(MilvusVectorStore)` 判斷（`vector_store_type` 為單值 `Literal["milvus"]`）。

### 驗證

- `check.sh`、`tests/integration -m "not cost"`、7 個 CLI `--help`：全部通過（375 passed）。
- grep 被刪除的名稱，src／tests 皆無結果。

## A2：簡化 `build_rag` 與 `IndexBuilder`

### 變更

- `build_rag(config, target)`：移除 `force_rebuild`／`build_query_engine` 參數與 query engine 分支；先 `load_source(target.aug_webpages_dir)` 再 `IndexBuilder.build(source)`，回傳 `RAG(handle)`（來源缺少時在清除既有向量庫前失敗，順序與原本相同）。
- 刪除 `IndexBuilder.build_or_load()`、`_should_rebuild()`；`index.py` 不再 import `load_source`。
- `run_rag_build` 改呼叫 `build_rag(config, target)`。
- 測試：刪除 `TestShouldRebuildMilvus`（4 個）與只服務它的 `_make_builder()`；`test_rebuild_reads_source_before_cleaning` 改呼叫 `build_rag`（斷言不變）；`test_build_rag_does_not_modify_config` 補 patch `load_source`；`test_pipeline_prepare` 的 fake `build_rag` 簽名移除 `**_kwargs`。
- 文件：`docs/code/phase1/modules/data_retrieve.md`、`docs/code/runs/workflow.md` 同步新流程。

### 驗證

- `check.sh`（371 passed，較 A1 少 4 個為刪除的測試）、`tests/integration -m "not cost"`、7 個 CLI `--help`：全部通過。
- grep `force_rebuild`／`build_or_load`／`_should_rebuild`：src 無結果，tests 只剩「`--run.force-rebuild` 被拒」的 CLI 測試。

## A3：合併重複實作

### 變更

- `MARKDOWN_IMAGE_PATTERN` 只定義於 `utils/text_helper.py`，`website_crawler`、`image_summarizer` 改為 import（不放在 crawler 內，避免 summarizer 間接 import crawl4ai）。
- `RESULTS_JSON_NAME` 只定義於 `storage/run_persistence.py`，`run_manager` 改為 import。
- 新增 `run_persistence.is_run_folder(name)`，`_filter_run_folders` 與 `RunManager.find_thread_history_path` 共用。
- 刪除 `base_config._is_section`／`_section_model`，`_has_field_path` 直接判斷欄位型別。**與 plan 不同**：plan 寫「保留 `overrides._section_type`、`base_config` 改用」，但 `_section_type` 會接受 `Model | None`，使 `run_name_fields` 可指到可能為 None 的 section（`get_field` 會 AttributeError），行為較原本寬；為維持行為不變，`_has_field_path` 仍只接受型別恰為 ConfigModel 子類的 section。`overrides._section_type` 維持原狀。
- 新增 `base_config.validate_loaded(cls, data, source)`（validate → `ConfigValidationError` 帶來源）與 `LoadedConfigModel`（持有 `_source` 與 `source` property）；`BaseModuleConfig`、`SiteConfig` 改為繼承 `LoadedConfigModel`，兩者的 `from_yaml` 共用 `validate_loaded`。
- `DataManager.publish_crawl_results`／`publish_markdown` 保留為一行包裝，共用 `_publish_results(site_id, category, results, markdown_key)`；兩者的 log 統一為 `Published {markdown_key} pages to ...`（原本只有 `publish_markdown` 有 log）。

### 驗證

- `check.sh`（371 passed）、`tests/integration -m "not cost"`、7 個 CLI `--help`：全部通過。
- `test_publish_removes_stale_markdown`（兩個 publisher 皆參數化）、`test_configs`／`test_site_config`／`test_config_extends` 的錯誤訊息斷言不修改即通過。

## A4：結構簡化

### 變更

- `server/app.py`：移除 lifespan、`app.state` 與 `Depends`（`get_agent`／`get_run_manager`），`/api/chat` 路由直接使用 `_build_fastapi_app` closure 中的 `agent`／`run_manager`；同步更新模組與函式 docstring。
- `storage/run_context.py`：刪除 `_WorkflowContext`，`run_workflow_context` 改為 `@contextmanager`（`with ExitStack()` 內進入 log／計時 context、印標題與 Run Paths、`yield`，區塊正常結束才印 complete 路徑表）。保留 `log_path` 參數。副作用：初始化中途失敗（如 `log_run_paths("init")` 拋錯）時，ExitStack 也會關閉已開啟的 log tee（原本不會）。

### 驗證

- `check.sh`（371 passed）、`tests/integration -m "not cost"`、7 個 CLI `--help`：全部通過。
- 手動確認 `run_workflow_context`：區塊內 `return`、區塊內拋例外兩種結束方式——return 時 log 含 complete 路徑表、例外時沒有，兩者皆記錄耗時並還原 stdout。

---

# B 組

> B 組基準點：`754a8de`（A 組合併 commit；與先前的 `0ea5012` 內容相同，僅 commit 訊息被改寫）。

## B1：`storage/data_paths.py`

### 變更

- 新增 `storage/data_paths.py`（只 import `os`，不存取檔案系統）：`RAW_WEBPAGES`／`AUG_WEBPAGES`／`VECTOR_DB` 常數，`site_data_path`、`aug_webpages_path`、`vector_db_folder`、`vector_store_name`、`vector_store_path`、`site_id_from_vector_store_name`（`{site_id}.db` → site_id，`.staging-*`／`.db.tmp`／`.db.old`／隱藏檔回傳 None）。
- `DataManager`、`retrieval.factory`（`published_target`／`vector_store_run_target`／`build_target`）、`RAGRegistry`（`_site_exists`／`list_sites`）、`pipelines/prepare`（`category` 常數與 staging 內的 `{site_id}.db`）改用上述函式與常數；src 內不再有 `"vector_db"`／`"aug_webpages"`／`"raw_webpages"` 的路徑字串。
- 新增 `tests/unit/test_data_paths.py`（10 個）：佈局、無檔案系統副作用、`site_id_from_vector_store_name` 各種名稱。
- README 檔案結構補上 `data_paths`。

### 驗證

- `check.sh`（381 passed，較 A 組多 10 個新測試）、`tests/integration -m "not cost"`、7 個 CLI `--help`：全部通過。
- `test_published_target`、`test_vector_store_path`、`TestListSites`、`test_serve_rag_loading`、`test_pipeline_prepare`、`test_imports`（serve 路徑不載入爬蟲）不修改即通過。

## B2：共用 runs/ 走訪

### 變更

- `storage/run_persistence.py` 新增 `_iter_site_run_folders(base_folder, module_name, site_id)`（由新到舊 yield 存在的 `runs/<ts>/<module>/<site_id>/`，沒有任何時間戳資料夾時報 `FileNotFoundError`）與 `_walk_sorted(folder)`（排序後由上而下走訪）；`load_latest_results`、`load_latest_run_path` 只保留各自的判斷（找 `results.json`／找 `results/` 資料夾），找到即回傳。
- `load_latest_run_path` 的 `site_id` 改為必填（`module_name` 因而也改為必填；唯一呼叫端 `build_target` 本來就傳 `"image_summarizer"` 與 `site_id`）；刪除「`site_id is None` 時不限站點」分支。
- 刪除 `load_latest_results` 中走不到的 `if not os.path.isfile(...)` 檢查（路徑來自 `os.walk` 的檔名清單）。
- 測試：重構前先補特徵測試並在舊程式碼上確認通過，再重構（新增 9 個，`test_run_persistence.py` 共 12 個）：較新的 run 缺 `results.json`／`results/` 時退回較舊的 run、不退回其他站點、忽略非時間戳資料夾、無任何 run 資料夾報錯、`is_run_folder`。

### 驗證

- `check.sh`（391 passed）、`tests/integration -m "not cost"`、7 個 CLI `--help`：全部通過。
- `test_build_target_uses_latest_summarizer_run_of_same_site`、`test_image_summarizer_loads_latest_results_of_same_site` 不修改即通過。

## B3：`new_thread_id()`

### 變更

- `agent/langchain_helper.py` 新增 `new_thread_id()`（`auto-{uuid 前 8 碼}`）；`thread_config(None)`、`run_agent_query`、server `/api/chat` 共用，`exp.py`／`app.py` 不再各自 `import uuid`。
- `run_agent_query` 改為問答**前**決定 thread_id（`run_config.thread_id` 為 None 時才產生），同一個 id 傳給 `ask`／`astream_result` 並用於落盤。原本是問答後才另外產生，落盤檔 `results_auto-xxx.json` 的 id 與實際對話 id 不同，無法以該 id 續接對話。
- 判斷語意維持各處原樣：`run_agent_query` 以 `is None` 判斷、server 以 `or`（空字串視為未提供）。
- 測試：`test_run_agent_query_auto_generates_thread_id` 增加斷言「`ask` 收到的 thread_id 與落盤的相同」（已確認在舊程式碼上失敗）；`test_agent_server` 新增 `new_thread_id`／`thread_config` 測試（2 個）。

### 驗證

- `check.sh`（393 passed）、`tests/integration -m "not cost"`、7 個 CLI `--help`：全部通過。
- `test_chat_sse_streams_tokens_and_done` 不修改即通過。
- 此項為行為修正（落盤 id），付費整合測試待 B 組合併後執行。

## B4：模組層級 helper

### 變更

- `agent/agent.py` 新增模組函式 `state_messages(graph, config)`（`graph.get_state` 取 messages，無 state 時為 `[]`）與 `build_result(query, response, messages)`（組 `{query, response, sources, timestamp}`）。
- `Agent.ask`、`Agent.astream_result`、server `_event_stream` 改用上述兩者；欄位與順序不變（`save_agent_results_as_json` 落盤格式不變），server 的 `query` 仍是使用者原始問題（非加站點前綴的版本）、仍逐 token yield。`app.py` 不再直接使用 `extract_sources_from_messages`、`time`。
- 因 helper 是模組函式、直接接收 `graph`，`test_agent_server` 的 `_FakeAgent`（只有 `graph`／`config`／`astream_text`）不必修改。
- 測試：新增 `build_result`、`state_messages`（含空 state）、`Agent.ask`、`Agent.astream_result` 共 4 個（`ask`／`astream_result` 原本沒有單元測試）；這兩個測試已用重構前的實作確認通過（結果欄位與順序相同）。

### 驗證

- `check.sh`（397 passed）、`tests/integration -m "not cost"`、7 個 CLI `--help`：全部通過。
- `test_chat_sse_streams_tokens_and_done`、`test_chat_delegates_save_to_run_manager_with_agent_config`、`test_pipeline_exp` 不修改即通過。
