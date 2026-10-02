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
| C ⚠️ | 現有驗證無法覆蓋（需先補測試），或會改變輸出 | A／B 合併後另行實作（見「C 組」）；不適合清理者移出 |

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

## C 組：已確認決策

原 C 組 10 項依性質重新分類：bug 修正（C2）、先補測試再重構（C1／C4／C6）、改變輸出格式（C5／C8／C10）、移出本計畫（C3／C7／C9）。

| # | 項目 | 決策 |
|---|---|---|
| C1 | `ImageSummarizer` 快取與統計 | 合併成單一快取；**刪除** `cache_download_images`／`cache_image_captions`（現行無作用） |
| C2 | `vlm_max_workers` 未限制 VLM 並行數（**bug**） | 單獨 `fix:` commit；不單獨跑付費測試，由 C4 的付費測試涵蓋 |
| C4 | LLM 供應商路由 | 收斂為一張表；統一為不分大小寫、**未知模型報錯**、缺 key 在建構時報錯 |
| C5 | 來源 dict 共用 | 共用；接受 results.json sources 的 key 順序改變 |
| C6 | runs/ 存檔樣板 | 抽出 `save_run_configs`（不處理 log），不讓 `_copy_single_file` 跳過同一檔案 |
| C8 | `run_rag_query` 的 `config` 與 `except` | **維持現狀**；`except` 為唯一失敗標記，保留 |
| C10 | RAG run_name 的 `-gemini` 特例 | 刪除 |
| C3／C7／C9 | — | 移出本計畫（見「移出項目」） |

### C2：VLM 並行數限制（bug 修正）

- 現況：每頁以 `asyncio.run(_agenerate_image_captions(...))` 為該頁每張圖各建一個 task；`_agenerate_image_caption_task` 在每個 task 內新建 `asyncio.Semaphore(vlm_max_workers)`，每個 semaphore 只有一個使用者，永遠不會阻擋。下載階段的 `ThreadPoolExecutor(max_workers=vlm_max_workers)` 則有正確限制。
- 影響：單頁 VLM 並行數等於該頁圖片數；圖多的頁面可能觸發供應商 rate limit（429）→ `summarize_failure` → 成功率低於門檻 → 指數退避重試，run 變慢且原因誤判為「被擋」。
- 根因：`semaphore` 是 `_agenerate_image_caption_task` 的區域變數，每次呼叫各建一個；N 個 task 各自持有一個 `Semaphore(vlm_max_workers)`，`async with` 永遠不需等待。限制並行須讓同一批 task 共用同一個 semaphore（在 task 外建立、在 task 內使用）。
- 實測：scratchpad 以 fake 取代 VLM 呼叫，`vlm_max_workers=3`、10 張圖，最高並行數 10。
- 實際資料：nculab 單頁最多 17 張（未超過 20）；ncucsie 有 5 頁超過 20 張（52、45、30、30、26），該 run 的 terminal.log 無 `Image summarization failed`（8 張失敗圖皆為下載失敗），目前帳號額度撐得住 52 並行，bug 尚未造成實際損害。

#### 決策

| # | 討論點 | 決策 |
|---|---|---|
| 1 | 並行範圍 | 只修**單頁內**的並行限制；頁面仍依序處理。跨頁並行（所有頁的圖共用一個上限）屬效能優化，記於 todo「平行處理圖片摘要」，後續再調整 |
| 2 | `vlm_max_workers` 同時控制下載執行緒與 VLM 並行 | **(a) 維持共用**，C2 只修 semaphore（C 組合併後的並行實驗結果出來後已推翻，見「後續：拆分 `vlm_max_workers`」） |
| 3 | 預設值 20 | 先實測 OpenAI 並行上限（見「並行上限實驗」），依結果決定是否調整（結果：摘要端改 50，見「後續：拆分 `vlm_max_workers`」） |
| 4 | 時機 | 立即在 `dev-tech-debt` 上進行 |

#### 修法

- `_agenerate_image_captions` 內建立 `asyncio.Semaphore(self.vlm_max_workers)`，以參數傳給 `_agenerate_image_caption_task`。
- 不可存為 `self` 屬性跨頁共用：每頁的 `asyncio.run` 建立新 event loop，semaphore 首次使用時綁定 loop，第二頁會拋 `RuntimeError`（... bound to a different event loop）。
- 刪除 `max(1, ...)`（`vlm_max_workers` 為 `PositiveInt`）。
- `_agenerate_image_caption_task` 包裝層的去留留給 C1，C2 的 diff 保持最小。

#### 測試

- 新增 `tests/unit/test_image_summarizer.py`（C1 的測試之後也放這裡）。
- 直接 `asyncio.run(summarizer._agenerate_image_captions(images))`，以 `await asyncio.sleep` 的 fake 取代 `_agenerate_image_caption`，記錄同時進行中的最大數；不走 `_generate_image_captions`（需預先準備 `_image_cache`，屬 C1 範圍）。
- 參數化：`(workers=3, images=10) → peak == 3`、`(workers=20, images=5) → peak == 5`；以 `==` 斷言，同時抓「未限制」與「過度限制」。
- 先確認測試在現行實作上失敗，再修正；測試與修正同一個 commit：`fix: limit concurrent VLM requests to vlm_max_workers`。

#### 並行上限實驗（付費，需使用者確認後執行）

目的：找出目前帳號下 `gpt-5.6-luna` 不出現 rate limit 的並行上限，作為 `vlm_max_workers` 預設值的依據。於付費整合測試通過、使用者確認後執行（兩者共用同一份帳號額度，不可同時跑）。

- 實際效果的範圍：目前頁面依序處理、semaphore 只在單頁內生效，實際並行數不超過單頁圖片數（ncucsie 最多 52 張）；超過約 50 的設定要等跨頁並行（todo「平行處理圖片摘要」）實作後才有效果。測到 100 是為該功能預先取得數據。
- 腳本與結果：`docs/exp/memo/webpage_image_summarizer/vlm_concurrency/`（`probe.py`、`results.md` 摘要表、`raw.jsonl` 每請求一行）。
- 呼叫路徑：使用正式的 `ImageSummarizer`；先以空爬取結果呼叫 `summarize_crawl_results_images` 完成 model／API key 解析，再直接呼叫 `_agenerate_image_captions`，並行數由修正後的 semaphore 控制。
- 模型與 prompt：正式預設值（`gpt-5.6-luna`、`IMAGE_SUMMARY_PROMPT`）。
- 圖片：從 `data/aug_webpages/ncucsie/results.json` 取一張可下載的代表性 png／jpeg，下載一次後重複使用（key 為 `url#i`），讓每個請求的 token 數相近、成本可預估。
- 關閉自動重試：`litellm_kwargs={"max_retries": 0}`；OpenAI SDK 預設會自動重試 429，會把 rate limit 藏成延遲。
- 量測：以包裝函式取代模組的 `acompletion`，記錄每個請求的開始／結束時間、成功或失敗、例外類型與 HTTP status（429 或其他）、`completion_cost`，以及 `response._hidden_params["additional_headers"]` 中的 `x-ratelimit-*`（RPM／TPM 上限與剩餘額度）。
- 階梯：`vlm_max_workers` = 20、30、40、50、60、70、80、90、100；每級送出 2N 個請求（持續滿載），兩級之間間隔 60 秒讓每分鐘額度重置。
- 每級摘要：成功／失敗數、失敗類型、延遲 p50／p95／max、總耗時、實測最高並行數、總成本、header 剩餘額度。
- 停止條件：出現任何 429 或其他失敗，或完成 100。
- 理論上限：若 header 可取得，以 `min(RPM, TPM ÷ 每請求 token) × 平均延遲(秒) ÷ 60` 估算，與實測對照。
- 成本與時間（以每張約 $0.001 估算）：全部 9 級共 1,080 個請求，約 $1.1；約 20～25 分鐘。
- 執行流程：
  1. 以 fake `acompletion` 乾跑，確認流程、紀錄格式與並行量測正確（不花費）。
  2. 只跑 N=20，回報實際成本、延遲與是否取得 rate limit header。
  3. 使用者確認後跑 30～100。
  4. 依結果決定預設值：全部無失敗時可提高到 50～60（ncucsie 圖多的 5 頁不再被限速），或維持 20 保留給低額度帳號的餘裕；出現 429 時取最後一個穩定級距並保留餘裕。預設值調整為獨立 commit。
- 限制：結果只適用於目前的帳號等級與模型（`results.md` 記錄由 header 推得的額度與測試日期）；換帳號或改用 Gemini 需重測。

#### 後續：拆分 `vlm_max_workers`（C 組合併後的獨立 commit）

並行實驗（`docs/exp/memo/webpage_image_summarizer/vlm_concurrency/results.md`）顯示 VLM 端到 100 並行都沒有 rate limit，但 `vlm_max_workers` 同時控制下載執行緒數，提高它會對被爬網站開更多連線（下載端未測），故推翻決策 2，拆成兩個參數：

- `download_max_workers`：放 `init` 區塊（與 `download_timeout` 同組，建構子參數），預設最初為 20（行為不變），並行實驗後改為 **40**（見「後續：下載並行上限實驗」）。
- `summary_max_workers`：放 `summarize` 區塊，預設 **50**（ncucsie 單頁實際需要摘要的圖片＝未快取圖片數，最多 45 張，見「後續：下載並行上限實驗」；50 已涵蓋，再高要等跨頁並行才有效果）。這是唯一改變行為的地方：圖超過 20 張的頁面（ncucsie 5 頁）摘要並行數由 20 提高到 50。
- 不保留 `vlm_max_workers` 別名（`ConfigModel` 為 `extra="forbid"`，與刪除 `cache_*` 旗標的作法一致）；`configs/` 沒有檔案使用它，`data/` 中已發布的 `module_config.yml` 只被讀檔頭，不經 `from_yaml`。
- CLI：`--module.summarize.vlm-max-workers` 由 `--module.init.download-max-workers` 與 `--module.summarize.summary-max-workers` 取代。
- 測試：下載與摘要各自受控的並行測試、兩者獨立（下載 2、摘要 5）的測試；先確認在拆分前的實作上失敗。
- 此 commit 同時收入並行實驗的腳本與結果（`probe.py`、`results.md`、`raw.jsonl`、`summary.jsonl`）。

#### 後續：下載並行上限實驗（ncucsie；拆分 commit 之後）

目的：找出 `download_max_workers` 在 ncucsie（學校系網站伺服器）不被限流的並行上限，作為其預設值（目前 20）的依據。拆分後 `download_max_workers` 只控制對被爬網站的連線數，可獨立於 VLM 端調整。

**ncucsie 的實際條件**（來自 `data/aug_webpages/ncucsie/results.json` 與其 terminal.log）：

- 149 頁，124 頁有圖片；圖片出現 620 次、不重複 169 張（166 張在 `www.csie.ncu.edu.tw`，另有 `placehold.co` 2 張、`fbcdn.net` 1 張）；robots.txt 為 `Allow: /`。
- **真正的下載並行需求只有 45**：正式流程有跨頁快取，每頁只下載「尚未下載過的圖片」。依爬取順序，未快取數最多的是 `p_412-1013-1849`（45）、`-1901`（30）、`-1096`（26），其餘 ≤ 8；單頁圖片總數最多的 `-2076`（52 張）只有 7 張未快取。因此 `download_max_workers` 超過 45 在 ncucsie 沒有效果，有意義的範圍是 20～45。
- 過去的完整執行（下載並行 20）：8 個最終失敗皆為固定錯誤，與限流無關——6 個 `HTTP 404`（`pdf.gif%20`、`doc.gif%20`、「請替換」資料夾下 4 張地圖）、2 個 `image/svg+xml`（`placehold.co`，不支援格式）；沒有 429、403 或逾時。20 以上是未測過的區間。
- 可用於實驗的 URL：排除上述 8 個固定失敗與第三方主機後，剩 **160 個確定可下載的不重複 URL**（`www.csie.ncu.edu.tw`），實驗中的失敗即可判定為限流或伺服器壓力，而非圖片本身問題。

**決策（使用者）**：

| # | 項目 | 決策 |
|---|---|---|
| 1 | 級距 | 以 20 為基準往上加：**20、30、40、50**（上限 50；45 為實際需求上限，50 用來看多餘並行有無壞處）；不另設 N=5 基準 |
| 2 | 停止條件 | 容許失敗，對齊 `success_threshold` 預設值 0.8：某一級的失敗率 **> 20%**（成功率 < 80%）即停止，不再往上加 |
| 3 | 風險 | 接受（學校伺服器，最多 50 並行、共 280 個請求；IP 被暫時封鎖時會連帶影響瀏覽系網站） |
| 4 | 完整驗證 | 若實驗沒有問題，直接以 ncucsie 做一遍完整驗證（見下方） |

**設計**：

- 腳本與結果：`docs/exp/memo/webpage_image_summarizer/download_concurrency/`（`probe.py`、`results.md`、`raw.jsonl`、`summary.jsonl`），結構與 `vlm_concurrency/` 一致。
- 呼叫路徑：正式的 `ImageSummarizer._download_images`，一次傳入 2N 個 URL 以繞過「每頁各自一個執行緒池」的限制（正式流程單頁最多 45 條，不繞過就無法測到 N=50；nculab 單頁最多 17 張，故不採用）。每級開始前重設 `_image_cache`／`_failed_images`／`_download_failure_reasons`／`_page_stats`。
- 量測：包裝 `_download_image`（量得到含讀取內容的完整時間），每個請求記錄開始／結束時間、成功或失敗、失敗原因（取自 `_download_failure_reasons`，如 `HTTP Error 429`、`timed out`）、下載位元組數。
- 每級摘要：成功／失敗數與失敗率、失敗原因統計（區分限流類：429／403／503／逾時／連線被重置，與其他）、延遲 p50／p95／max、總耗時、實測最高並行數、吞吐量（張／秒、MB／秒）。吞吐量（MB／秒）不再增加但延遲上升時，判定為本機頻寬飽和而非對方限流。
- URL：從 160 個可用 URL 中每級以固定隨機種子打亂後取 2N 個；同一級內不重複（最大 2N=100 < 160），不同級之間會重複，伺服器端快取可能使後面的級距偏快，故以失敗與否為主要判斷、延遲為輔。
- 級距間隔 60 秒；2N 個請求會形成兩波連續下載，比正式流程（單頁一波）嚴苛，結果偏保守。
- 成本與時間：下載不呼叫付費 API，$0；耗時約 4～6 分鐘（4 級＋3 個間隔）。資料量依 7 張樣本估計 40～130 MB，以實測位元組數為準。

**執行流程**：

1. 以假的 `_download_image` 乾跑（不連網，輸出到暫存資料夾）：確認紀錄格式與並行量測。
2. 正式跑 20→50（使用者已接受風險，不再逐級暫停）；遇到停止條件（失敗率 > 20%）即停止，不進入完整驗證，回報後再決定。
3. 判斷預設值：

   | 結果 | 結論 |
   |---|---|
   | 各級皆無限流類失敗，且延遲沒有明顯上升（p95 ≤ 20 並行的 2 倍） | 伺服器承受得住；預設值取到 45 以內的最高級距 |
   | 某級出現限流類失敗但失敗率 ≤ 20% | 列出結果，預設值取前一級並保留餘裕，由使用者確認 |
   | 失敗率 > 20% | 停止；預設值取前一級再保留餘裕（約一半到八成），由使用者確認 |
   | 無失敗但延遲或逾時明顯變差 | 提高並行沒有好處，維持 20 |

4. 預設值若要調整，原規劃為獨立 commit；實際結果見下方「結果與決策」。

**完整驗證（實驗沒有問題時）**：

- 方式：runs/ 中**沒有** ncucsie 的爬蟲結果（`runs/*/website_crawler/ncucsie` 不存在），`run image-summarizer ncucsie` 會因找不到最新爬蟲結果而失敗；改以 Python 腳本載入 `data/aug_webpages/ncucsie/results.json`（含 `fit_markdown`、`images`，結構同爬蟲結果）當輸入，呼叫 `run_image_summarizer(ImageSummarizerRunConfig(site="ncucsie", config_name="default", save=True, publish=False), overrides={"init": {"download_max_workers": X}}, crawl_results=...)`，X 為實驗得出的候選值（驗證不依賴是否已 commit 預設值）。走正式流程（跨頁快取、單頁並行、統計表格），含 ncucsie 的 45／30／26 張大頁；`save=True`、`publish=False`：只寫入 runs/，不覆寫 `data/`。
- 費用與耗時：圖片出現 620 次但不重複僅 169 張（快取去重），舊紀錄 161 張摘要成功、$0.1569，估計約 **$0.16**（先前「約 $0.7」的估算未計入快取，偏高）；舊紀錄耗時 422.955 秒。
- 通過條件：
  1. 摘要成功數與舊紀錄相同（161）；最終失敗的圖片仍是同樣 8 張固定錯誤（6 個 404、2 個 svg），沒有 429、逾時或其他新失敗。
  2. 沒有出現 `retrying`（重試退避）：舊紀錄成功率為 161／(161＋33)＝83%，只高於 `success_threshold` 0.8 約 3 個百分點（8 個固定失敗 URL 在多頁重複出現而被累計 33 次），再多約 8 次下載失敗就會觸發 30 秒以上的退避；這也是實驗要排除固定失敗 URL 的原因。
  3. 統計表格欄位與格式不變；耗時不長於舊紀錄（圖多的頁面摘要並行由 20 提高到 50）。
  4. 摘要費用約 $0.16；`data/` 未被修改（`git status` 無變動）。
- 結果記錄於 `dev.md`。

**結果與決策**（詳見 `docs/exp/memo/webpage_image_summarizer/download_concurrency/results.md`）：

- 實驗 20／30／40／50 共 280 個請求 0 失敗，無限流類錯誤，p95 皆在 N=20 的 2 倍內；吞吐量從 N=20 起固定約 10 MB/s（頻寬飽和），更高並行只增加延遲，對耗時沒有可量測的好處（下載約占整次執行的 2%）。
- 完整驗證（下載 40、摘要 50）：摘要成功 161、同樣 8 張最終失敗、無 429／逾時／重試；耗時 465.4 秒對舊紀錄 422.9 秒，差異在單次執行的自然波動內（通過條件 3「耗時不長於舊紀錄」過於樂觀，未達成，如實記錄）。
- **決策（使用者）：`download_max_workers` 預設改為 40**（依 plan 判斷規則：45 以內的最高級距；實驗與完整驗證皆在 40 通過）。這是唯一的行為變動：圖片較多的頁面（ncucsie 3 頁未快取下載數為 45／30／26）下載並行數由 20 提高到 40，頁面較小者不受影響。
- 意外發現（既有問題）：頁內重複的圖片 URL 會被同時下載多次，失敗原因文字可能顯示為 `download failed`；已記入 todo「效能優化」，不在本次處理。

### C1：`ImageSummarizer` 快取與統計

- 現況：`_image_cache[url]`（`{base_64_url, download_status, caption, summarize_status}`）、`_downloaded_images[url]`、`_image_captions[url]` 三份資料，後兩者可由第一份推得；`_collect_cached_items` 主要在同步三者。
- 快取旗標無作用：`ImageSummarizer` 只在 `prepare.py` 建立一次、每個 run 只呼叫一次 `summarize_crawl_results_images`；旗標只決定該方法開頭是否清空快取，而此時快取必為空。原用途「同一批網頁重複實驗」（同一 instance 多次呼叫）在 CLI 已不存在。快取真正的作用（同一 run 內跨頁共用同一張圖、重試輪次間只重做失敗的圖）與旗標無關。
- 刪除旗標的前提已確認：已發布的 `data/aug_webpages/*/module_config.yml` 只有 `factory._read_config_source` 讀檔頭 `# source:`，沒有經過 `from_yaml`（`ConfigModel` 為 `extra="forbid"`，經由 `from_yaml` 讀回才會失敗）。
- 做法：
  - 單一 `_image_cache: dict[str, ImageEntry]`（dataclass：`base64_url`、`download_status`、`caption`、`summarize_status`）；`_downloaded_images`／`_image_captions` 改為由此讀取。
  - 三種統計 dict 改為 dataclass，log 表格欄位與格式不變。
  - 刪除 `SummarizerInitConfig.cache_download_images`／`cache_image_captions`、`ImageSummarizer` 對應參數與 `prepare.py` 的傳入；更新 `docs/code/phase1/modules/data_preprocess.md`、`docs/code/runs/config.md`。
- 先補單元測試（mock `urlopen`／`acompletion`／`completion_cost`／`time.sleep`），通過現行實作後再重構：
  1. 同一 url 出現在多頁時只下載、摘要各一次。
  2. 下載失敗的圖不送 VLM，caption 為空，記錄在 `_failed_images`。
  3. 不支援的 content-type 視為下載失敗，原因字串正確。
  4. 成功率低於門檻時重試，只重做失敗的 url；重試成功後從 `_failed_images` 移除。
  5. `enhanced_markdown` 的 caption 插入格式（`> # Image-N`）。
  6. success／download_failure／summarize_failure／cache_reuse／cost 的累加。

### C4：LLM 供應商路由

- 現況：三份實作、兩張相同的對照表（`LLM_API_KEY_ENV_VARS`、`VLM_MODEL_TO_API_KEY`），行為不一致：

  | 位置 | 比對 | 未知模型 | 缺 key | `load_dotenv` |
  |---|---|---|---|---|
  | `llama_index_helpers.create_llm`（RAG query／評估） | 區分大小寫 | `ValueError` | `api_key=None` 傳下去 | 否 |
  | `langchain_helper.create_llm`（Agent） | `lower()` | 預設 OpenAI | `ValueError` | 是 |
  | `ImageSummarizer._get_api_key` + litellm 前綴（VLM） | `lower()` | `EnvironmentVariableError` | `EnvironmentVariableError` | 是（每張圖一次） |

- 做法：新增共用模組，提供 `PROVIDERS`（`gemini`／`gpt` → `env_var`、`litellm_prefix`）、`resolve_provider(model_name)`（不分大小寫，未知則報錯）、`get_api_key(spec)`（呼叫 `load_dotenv`，缺 key 則報錯）。三處改為「`resolve_provider` → `get_api_key` → 各自建構 client」，client 建構參數不變；VLM 改為在 `summarize_crawl_results_images` 開頭取一次 key。
- 行為改變：Agent 的未知模型由「預設 OpenAI」改為報錯。已確認所有預設值（`gpt-5.6-luna`／`gpt-5.6-terra`）與 `configs/` 皆不受影響。
- 測試：`resolve_provider`（大小寫、未知模型）、`get_api_key`（monkeypatch 環境變數）。
- 行為統一後跑一次付費整合測試（涵蓋 rag-query、agent、image-summarizer，也一併驗證 C2）。

### C6：runs/ 存檔樣板

- 現況：「`save_module_config` → `save_site_config` → `save_run_config`」在 prepare（3）、exp（2）、serve（1，無 site）與 `DataManager.write_run_metadata` 各寫一次。
- 不直接改用 `write_run_metadata` 的原因：runs/ 存檔時 `dest` 為 `run_path`，`log_path` 即 `run_path/terminal.log`，`shutil.copy2` 會拋 `SameFileError`；runs/ 存檔本來就不需要複製 log。
- 做法：抽出 `save_run_configs(dest_folder, config, site=None, run_config=None)`；`write_run_metadata` 改為呼叫它再複製 log。檔名常數與 `RunManager` 的 `module_config_path` 等共用，確保 runs/ 下的檔名不變。
- 範圍（實作時確定）：prepare 3 處、`run_rag_query`、`write_run_metadata`；serve 的 `run_agent_build`（module＋run 兩行、無 site）與只存 run_config 的一行呼叫不屬重複樣板，不改。
- 測試：`test_pipeline_prepare` 補「save=True 時 crawler／summarizer／rag-build 在 run_path 下的三個 yml 皆存在」；exp、serve 同。

### C5：來源 dict 共用

- 現況：`RAG.retrieve`（Agent retriever tool）的 key 順序為 `page_title, score, page_type, content, url`，content 不截斷；`evaluation.extract_sources_list`（rag-query results.json）的順序為 `..., url, content`，截斷 800 字。docstring 稱兩者「形狀一致」，實際順序不同。
- 做法：新增 `source_dict(node, max_content_length=None)`，兩處共用，統一為 `url` 在前、`content` 在後；截斷長度保留為參數。
- 實作前確認 Agent retriever tool（`agent/tools/webpage_retriever.py`）依 key 取值格式化，順序改變不影響 LLM 看到的內容。
- 輸出變動（實作後確認）：統一的順序即 rag-query results.json 原本的順序，results.json 不變；只有不落盤的 `RAG.retrieve` 結果由 `content, url` 改為 `url, content`。

### C10：刪除 RAG run_name 的 `-gemini` 特例

- 現況：`RAGConfig._post_process_run_name` 在 run_name 第 2 字元之後出現 `-gemini` 時刪除第一個 `-gemini`。
- 預設 run_name_fields 為 `[vector_store.vector_store_type]`（固定為 `vector_store_type-milvus`），`configs/rag` 未覆寫，特例目前不會觸發；只有自訂 run_name_fields 含 `query_engine.query_llm_name` 時才觸發，且效果是 `query_llm_name-gemini-2.5-flash` → `query_llm_name-2.5-flash`，刪掉了模型名稱的關鍵部分。應為舊命名規則的殘留。
- 做法：只保留 `/` → `-`（與 `ImageSummarizerConfig` 一致）；`test_run_name` 補 gemini 參數化案例。
- 輸出變動：現有 runs/ 資料夾名稱皆不受影響。

### C8：維持現狀

- `config` 欄位：手動挑選的扁平欄位可與舊 run 直接比較；完整設定已在同資料夾的 `module_config.yml`。
- `except`：`run_workflow_context` 在例外時不印任何失敗訊息，`log_session("RAG Query Failed")` 是 terminal.log 中唯一的失敗標記，保留（`run_agent_query` 同）。

### 移出項目

| 項目 | 處理 |
|---|---|
| C3 Rich「Metric／Value」表格抽成 helper（約 6 處） | 併入 todo「包裝 log_helper.py」，與 log API 一起設計 |
| C7 `VectorStoreBuilder.default_hybrid_ranker_params` | 非重複（設定檔寫 `null` 時補內建值），不需處理 |
| C9 空殼 `WebsiteCrawlerRunConfig`／`ImageSummarizerRunConfig` | 設計上保留：每個子命令各有型別，未來加專屬參數不必改簽名（如 `RAGBuildRunConfig`） |

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
| 9 | C2 VLM 並行數修正（含測試）；之後執行並行上限實驗，依結果調整預設值 | — |
| 10 | C1 `ImageSummarizer` 測試 → 快取合併、刪除旗標 | C2（同檔案；C1 的測試以修正後的並行行為為準） |
| 11 | C6 `save_run_configs` | — |
| 12 | C4 測試 → LLM 供應商路由表 | C1（同檔案 `image_summarizer.py`；C4 改動 `_get_api_key` 時有 C1 的測試保護） |
| 13 | C5 來源 dict 共用、C10 刪除 `-gemini` 特例 | — |
| 14 | 拆分 `vlm_max_workers`（已完成，獨立 commit `7354db5`，含 VLM 並行實驗） | C 組合併 commit |
| 15 | 下載並行上限實驗（ncucsie）→ 完整驗證 → 預設值調整（若需要） | 14 |

## Commit 策略

實作期間每項一個 commit（A1～A4、B1～B4），方便逐項審核與定位問題；各組全部完成並審核後，再合併成一個 commit：

1. **A 組**：開始前記下基準點（`git rev-parse HEAD`，即 A1 之前的 commit）。A1～A4 依序各自 commit，每個都通過共同關卡。
2. A 組全部審核通過後，以 `git reset --soft <A 組基準點>` 收回 A1～A4，再重新 commit 成單一 commit：`refactor: remove dead code and merge duplicates (code cleanup A)`；訊息內文逐行列出 A1～A4 的內容。
3. 合併後再跑一次共同關卡（確認內容與合併前的 A4 commit 相同：`git diff <A4 commit> HEAD` 應為空）。
4. **B 組**：以合併後的 A commit 為基準點，B1～B4 依序各自 commit，流程同 1～3；合併後的訊息為 `refactor: centralize data paths, share runs/ lookup and agent result helpers (code cleanup B)`。
5. 付費整合測試於 B 組合併後執行一次（見「付費整合測試」）。
6. **C 組**：C1／C4 各分「補測試」與「重構」兩個 commit（測試 commit 須通過現行實作）。依使用者指示，C2（bug 修正）也一併合併：C2～C10 全部完成後以 `git reset --soft <B 組合併 commit>` 合併為單一 commit `refactor: fix VLM concurrency, unify image summarizer cache, LLM provider routing and run config saving (code cleanup C)`。

7. **C 組之後**：拆分 `vlm_max_workers`（連同 VLM 並行實驗）為獨立 commit，不併入 C 組合併 commit；下載並行實驗的紀錄（腳本、結果、plan／dev）另一個 commit；`download_max_workers` 預設值調整原規劃為再一個 commit，依使用者指示併入下載並行實驗的 commit（amend，尚未推送）。

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

C 組合併後跑一次（同時涵蓋 B3），於並行上限實驗之前執行：

| C 組改動 | 涵蓋的測試 |
|---|---|
| C2 並行修正、C1 快取與統計、C4 的 VLM 路由 | `test_image_summarizer`、`test_prepare` |
| C6 runs/ 存檔 | `test_website_crawler`、`test_image_summarizer`、`test_rag_build`（save=True） |
| C4 Agent 路由、C5 `RAG.retrieve`、B3 thread_id | `test_agent_query` |
| C4 RAG 路由（llama_index `create_llm`）、C5 `extract_sources_list` | 手動 rag-query（`tests/integration` 未涵蓋：rag-build 不建立 LLM） |

步驟：

1. 確認 `.env` 有 `OPENAI_API_KEY`。
2. `uv run pytest tests/integration`（保留 `test_prepare`：與 `test_module` 前三項重複，但多驗證各階段在記憶體中傳遞結果的路徑）。
3. `uv run website-copilot run rag-query nculab --run.config test`（查詢 data/ 中已發布的 nculab 向量庫，使用站點的 sample_query）。

整合測試皆為 `publish=False`，只寫入 runs/，不覆寫 data/。估計約 $0.15～0.20、6～8 分鐘。

通過條件（除不拋例外外）：

1. image_summarizer 的 terminal.log：成功數與舊紀錄相近（nculab 57 張、0 失敗），無 `task failed unexpectedly`，統計表格欄位與格式不變。
2. crawler／summarizer／rag_build 的 run 資料夾皆有三個 yml，`module_config.yml` 檔頭有 `# source:`；image_summarizer 的 config 不含兩個快取旗標。
3. agent_query：`results_<thread_id>.json` 的 id 與 log 中實際對話的 thread_id 相同（B3），sources 正常。
4. rag-query 的 results.json：sources 的 key 順序為 `page_title, score, page_type, url, content`（與舊 run 相同）。

結果記錄於 `dev.md`「付費整合測試」。
