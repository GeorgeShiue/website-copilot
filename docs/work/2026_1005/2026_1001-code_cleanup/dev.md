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
