# 程式碼清理與資料儲存重構：實作規劃

> 對應 [todo.md](../../todo.md)「技術債」。兩部分合併於此，實作紀錄見 [dev.md](./dev.md)。
>
> - **一、程式碼清理**：只處理冗贅程式碼（死碼、重複實作），不改功能（C2 為 bug 修正）。
> - **二、資料儲存重構**：向量庫的建庫、發布與路徑佈局。網站知識庫版本控制不在範圍（見 D2）。

---

# 一、程式碼清理

## Context

`dev-tech-debt` 分支歷經專案重構（plan 1～4）、模組配置重構（Phase A～D）與資料儲存重構（Phase 1～2），每輪都刪除了舊實作，但新舊交接處仍留下三類問題：

1. **死碼**：重構後已無呼叫端的方法、參數與常數。
2. **重複實作**：同一邏輯在多處各寫一份（路徑規則、runs/ 搜尋、config loader、Agent 結果組裝等）。
3. **零碎殘留**：未使用的 logger、空殼類別、「向後相容」的 property 與 context manager。

依「是否明確可改」與「現有驗證機制（`scripts/check.sh`）能否覆蓋」分為三組：

| 組別 | 定義 | 處理方式 |
|---|---|---|
| A | 無需設計取捨、不改變任何輸出，且 `check.sh` 可驗證 | 直接實作 |
| B | 測試可覆蓋，但需先做設計決策 | 決策後實作 |
| C | 現有驗證無法覆蓋（需先補測試），或會改變輸出 | A／B 合併後另行實作；不適合清理者移出 |

純刪除類變更主要由 pyright 把關：被刪除的名稱若仍有引用，型別檢查直接失敗。

## A 組：明確可改且可驗證

### A1：刪除死碼

- 6 個未使用的 `logger`（`config/{agent,rag,image_summarizer,website_crawler}_config.py`、`storage/run_manager.py`、`utils/config_helper.py`）、`KEEP_TITLE_CONTENT_THRESHOLD`。
- `storage/__init__.py` 的 re-export（無人經由套件 import）。
- `DataManager` 的 Discover 方法（`get_vector_store_path`／`list_sites`／`get_webpages_path`／`site_exists`）。
- `save_results_as_md` 的 `save_images` 參數；`Agent.tools` property 與 `checkpointer or InMemorySaver()`；`Tool`／`Agent`／`ChatApp` 的 `__enter__`／`__exit__`。

### A2：簡化 `build_rag` 與 `IndexBuilder`

資料儲存重構 Phase 1 後，`build_rag` 唯一呼叫端為 `run_rag_build`，且固定 `force_rebuild=True, build_query_engine=False`。`build_rag(config, target)` 只做「讀來源 → `IndexBuilder.build()` → `RAG(handle)`」；刪除 `build_or_load()`、`_should_rebuild()`；讀取來源移到 `build_rag`，維持「先讀來源、再清除舊向量庫」的順序。刪除 `TestShouldRebuildMilvus`（測試對象即死碼）。

### A3：合併重複實作

| 項目 | 做法 |
|---|---|
| `MARKDOWN_IMAGE_PATTERN` 兩份 | 保留一份，另一處 import |
| `publish_crawl_results` 與 `publish_markdown` 除資料夾與 markdown key 外相同 | 抽出 `_publish_results(...)`，兩個公開方法保留為一行包裝 |
| `RESULTS_JSON_NAME` 兩份 | 保留一份 |
| 時間戳資料夾判斷兩份 | 抽成 `run_persistence.is_run_folder()` |
| `base_config._is_section`／`_section_model` 與 `overrides._section_type` | 原計畫保留 `_section_type`，實作時偏離（見 dev） |
| `SiteConfig.from_yaml` 與 `BaseModuleConfig.from_yaml` 的 validate 流程 | 抽出 `validate_loaded`，`_source` 移到共用 mixin |

### A4：結構簡化

- `ChatApp` 的 lifespan＋`app.state`＋`Depends` 傳遞 agent／run_manager，改為路由直接使用 closure。
- `_WorkflowContext` 包裝 `ExitStack`，改為 `@contextmanager`；保留「僅成功時印 complete 路徑表」與 `log_path` 參數。

## B 組：已確認決策

| # | 項目 | 選項 | 決策 |
|---|---|---|---|
| B1 | `vector_db`／`aug_webpages` 路徑規則散落於 `DataManager`、`factory`、`registry` | (a) 由 `DataManager` 提供；(b) 新增無副作用的 `storage/data_paths.py` 純函式模組 | **(b)** |
| B2 | `load_latest_results` 與 `load_latest_run_path` 的走訪迴圈重複 | (a) 抽出共用走訪，兩個公開函式語意不變；(b) 合併成單一函式 | **(a)** |
| B3 | `run_agent_query` 問答**後**才產生 auto thread_id，落盤 id 與實際對話 id 不同；產生邏輯共三份 | (a) 問答前產生；(b) 同 (a)，並新增 `new_thread_id()` 共用；(c) 維持現狀 | **(b)** |
| B4 | `{query, response, sources, timestamp}` 在 `Agent.ask`／`astream_result`／server 各組一次 | (a) 抽模組層級 helper；(b) server 改用 `astream_result`；(c) 維持現狀 | **(a)** |

- **B1 理由**：`DataManager.__init__` 會 `os.makedirs(base_folder)`，serve 階段若改用它查路徑就可能建立 `data/`，違反「serve 只讀」；純函式沒有副作用，且只 import `os`，不違反 `test_imports` 的 serve 路徑限制。
- **B2 理由**：合併會改變邊界行為（有 `results/` 但無 `results.json` 的失敗 run，現行 `load_latest_results` 會跳過改用較舊的 run，合併後會選到該 run 而報錯）。`load_latest_run_path` 的 `site_id` 改為必填。
- **B3 理由**：落盤的 `results_auto-xxx.json` 與實際對話 id 不同，無法以該 id 續接對話。屬行為修正，需跑一次付費整合測試。
- **B4 理由**：server 必須逐 token yield，`astream_result` 的 callback 介面無法沿用；helper 為模組函式、直接接收 `graph`，可讓 `test_agent_server` 的 `_FakeAgent` 不必修改。

## C 組：已確認決策

原 C 組 10 項依性質重新分類：bug 修正（C2）、先補測試再重構（C1／C4／C6）、改變輸出格式（C5／C8／C10）、移出本計畫（C3／C7／C9）。

| # | 項目 | 決策 |
|---|---|---|
| C1 | `ImageSummarizer` 快取與統計 | 合併成單一快取；**刪除** `cache_download_images`／`cache_image_captions` |
| C2 | `vlm_max_workers` 未限制 VLM 並行數（**bug**） | 單獨修正，由 C4 的付費測試涵蓋 |
| C4 | LLM 供應商路由 | 收斂為一張表；統一為不分大小寫、**未知模型報錯**、缺 key 在建構時報錯 |
| C5 | 來源 dict 共用 | 共用；接受 results.json sources 的 key 順序改變 |
| C6 | runs/ 存檔樣板 | 抽出 `save_run_configs`（不處理 log） |
| C8 | `run_rag_query` 的 `config` 與 `except` | **維持現狀**；`config` 為可與舊 run 直接比較的扁平欄位，`except` 的 log 是 terminal.log 中唯一的失敗標記 |
| C10 | RAG run_name 的 `-gemini` 特例 | 刪除 |

### C2：VLM 並行數限制（bug 修正）

- **現況與根因**：每頁以 `asyncio.run(_agenerate_image_captions(...))` 為每張圖建一個 task，`_agenerate_image_caption_task` 在**每個 task 內**新建 `Semaphore(vlm_max_workers)`，每個 semaphore 只有一個使用者，永遠不會阻擋。下載階段的 `ThreadPoolExecutor` 則有正確限制。
- **影響**：單頁 VLM 並行數等於該頁圖片數；圖多的頁面可能觸發 rate limit（429）→ `summarize_failure` → 成功率低於門檻 → 指數退避重試。實測 `vlm_max_workers=3`、10 張圖，最高並行 10。
- **實際資料**：nculab 單頁最多 17 張；ncucsie 有 5 頁超過 20 張（52、45、30、30、26），該 run 無 summarize 失敗，目前帳號額度撐得住，bug 尚未造成實際損害。

| # | 討論點 | 決策 |
|---|---|---|
| 1 | 並行範圍 | 只修**單頁內**的並行限制，頁面仍依序處理；跨頁並行屬效能優化，記於 todo「平行處理圖片摘要」 |
| 2 | `vlm_max_workers` 同時控制下載與 VLM 並行 | 先維持共用（並行實驗後推翻，見「後續：拆分 `vlm_max_workers`」） |
| 3 | 預設值 20 | 先實測並行上限再決定（結果：摘要端改 50） |
| 4 | 時機 | 立即在 `dev-tech-debt` 上進行 |

**修法**：在 `_agenerate_image_captions` 內建立一個 semaphore 以參數傳給 task。不可存為 `self` 屬性跨頁共用：每頁的 `asyncio.run` 建立新 event loop，semaphore 首次使用時綁定 loop，第二頁會拋 `RuntimeError`。

**測試**：新增 `tests/unit/test_image_summarizer.py`，以 fake 記錄最高並行數，參數化 `(workers=3, images=10) → 3`、`(20, 5) → 5`，以 `==` 斷言同時抓「未限制」與「過度限制」；先確認在現行實作上失敗，再修正，測試與修正同一個 commit。

#### 並行上限實驗（付費，需使用者確認後執行）

目的：找出目前帳號下 `gpt-5.6-luna` 不出現 rate limit 的並行上限，作為預設值的依據。需在付費整合測試通過、使用者確認後執行（共用同一份帳號額度，不可同時跑）。

- **範圍**：頁面依序處理、semaphore 只在單頁內生效，實際並行不超過單頁圖片數；超過約 50 的設定要等跨頁並行實作後才有效果，測到 100 是為該功能預先取得數據。
- **腳本與結果**：`docs/exp/memo/webpage_image_summarizer/vlm_concurrency/`。
- **呼叫路徑**：正式 `ImageSummarizer`，先以空爬取結果呼叫 `summarize_crawl_results_images` 完成 model／API key 解析，再直接呼叫 `_agenerate_image_captions`；模型與 prompt 用正式預設值；圖片取一張可下載的代表性圖，下載一次後重複使用，使每個請求 token 數相近。
- **關閉自動重試**（`max_retries=0`）：OpenAI SDK 預設自動重試 429，會把 rate limit 藏成延遲。
- **量測**：包裝 `acompletion`，記錄每請求的起訖時間、成敗、例外類型與 HTTP status、`completion_cost`，以及 `x-ratelimit-*` header。
- **階梯**：原訂 20～100 每 10 一級，每級送 2N 個請求（持續滿載），級間隔 60 秒；停止條件為出現任何 429 或其他失敗，或完成 100。
- **流程**：先以 fake `acompletion` 乾跑；只跑 N=20 回報成本與 header；使用者確認後再往上。預估全部 9 級約 $1.1、20～25 分鐘。
- **限制**：結果只適用於目前帳號等級與模型，換帳號或改用 Gemini 需重測。

#### 後續：拆分 `vlm_max_workers`（C 組合併後的獨立 commit）

並行實驗顯示 VLM 端到 100 並行都沒有 rate limit，但 `vlm_max_workers` 同時控制下載執行緒數，提高它會對被爬網站開更多連線（下載端未測），故推翻決策 2，拆成兩個參數：

- `download_max_workers`：放 `init` 區塊（建構子參數），預設最初 20，下載並行實驗後改為 **40**。
- `summary_max_workers`：放 `summarize` 區塊，預設 **50**（ncucsie 單頁需要摘要的未快取圖片最多 45 張）。這是唯一改變行為的地方：圖超過 20 張的頁面摘要並行由 20 提高到 50。
- 不保留 `vlm_max_workers` 別名（`ConfigModel` 為 `extra="forbid"`，與刪除 `cache_*` 的作法一致）。CLI 的 `--module.summarize.vlm-max-workers` 由兩個新參數取代。
- 測試：下載與摘要各自受控的並行測試、兩者獨立的測試；先確認在拆分前的實作上失敗。

#### 後續：下載並行上限實驗（ncucsie；拆分 commit 之後）

目的：找出 `download_max_workers` 在 ncucsie（學校系網站伺服器）不被限流的並行上限。

**ncucsie 的實際條件**：

- 149 頁，124 頁有圖片；圖片出現 620 次、不重複 169 張（166 張在 `www.csie.ncu.edu.tw`）；robots.txt 為 `Allow: /`。
- **真正的下載並行需求只有 45**：正式流程有跨頁快取，每頁只下載尚未下載過的圖片，未快取數最多的頁為 45／30／26，其餘 ≤ 8。因此 `download_max_workers` 超過 45 沒有效果，有意義的範圍是 20～45。
- 過去完整執行（並行 20）的 8 個最終失敗皆為固定錯誤（6 個 404、2 個不支援的 svg），與限流無關。排除它們與第三方主機後，剩 160 個確定可下載的 URL，實驗中的失敗即可判定為限流或伺服器壓力。

**決策（使用者）**：

| # | 項目 | 決策 |
|---|---|---|
| 1 | 級距 | 以 20 為基準往上加：**20、30、40、50**；不另設 N=5 基準 |
| 2 | 停止條件 | 對齊 `success_threshold` 0.8：某一級失敗率 **> 20%** 即停止 |
| 3 | 風險 | 接受（學校伺服器，最多 50 並行、共 280 個請求；IP 被暫時封鎖時會連帶影響瀏覽系網站） |
| 4 | 完整驗證 | 實驗沒問題就直接以 ncucsie 做一遍完整驗證 |

**設計**：

- 腳本與結果：`docs/exp/memo/webpage_image_summarizer/download_concurrency/`，結構與 `vlm_concurrency/` 一致。
- 呼叫正式的 `ImageSummarizer._download_images`，一次傳入 2N 個 URL 以繞過「每頁各自一個執行緒池」的限制（否則測不到 N=50）；每級開始前重設快取與統計。
- 包裝 `_download_image` 量測完整時間，記錄成敗、失敗原因與位元組數。每級摘要含失敗率、限流類（429／403／503／逾時／連線被重置）與其他的分類、延遲 p50／p95／max、最高並行數、吞吐量。吞吐量（MB／秒）不再增加但延遲上升時，判定為本機頻寬飽和而非對方限流。
- 每級以固定隨機種子從 160 個 URL 取 2N 個；級間隔 60 秒。2N 個請求形成兩波連續下載，比正式流程嚴苛，結果偏保守；伺服器端快取可能使後面的級距偏快，故以失敗與否為主、延遲為輔。
- 成本 $0（下載不呼叫付費 API），約 4～6 分鐘。

**判斷預設值**：

| 結果 | 結論 |
|---|---|
| 各級皆無限流類失敗，且延遲沒有明顯上升（p95 ≤ N=20 的 2 倍） | 預設值取 45 以內的最高級距 |
| 某級出現限流類失敗但失敗率 ≤ 20% | 取前一級並保留餘裕，由使用者確認 |
| 失敗率 > 20% | 停止；取前一級再保留餘裕，由使用者確認 |
| 無失敗但延遲或逾時明顯變差 | 提高並行沒有好處，維持 20 |

**完整驗證**：runs/ 中沒有 ncucsie 的爬蟲結果，改以 Python 腳本載入 `data/aug_webpages/ncucsie/results.json` 當輸入，呼叫 `run_image_summarizer(..., save=True, publish=False)` 並以候選值覆寫 `download_max_workers`；走正式流程，不覆寫 `data/`。預估約 $0.16（先前「約 $0.7」未計入快取）；舊紀錄耗時 422.955 秒。通過條件：

1. 摘要成功數與舊紀錄相同（161），最終失敗仍是同樣 8 張固定錯誤，沒有 429、逾時或新失敗。
2. 沒有 `retrying`：舊紀錄成功率 83%，只高於門檻 3 個百分點，再多約 8 次下載失敗就會觸發退避，這也是實驗要排除固定失敗 URL 的原因。
3. 統計表格欄位與格式不變；耗時不長於舊紀錄。
4. 費用約 $0.16；`data/` 無變動。

**結果與決策**（詳見 `download_concurrency/results.md`）：

- 20／30／40／50 共 280 個請求 0 失敗；吞吐量從 N=20 起固定約 10 MB/s（頻寬飽和），更高並行只增加延遲，下載約占整次執行的 2%。
- 完整驗證（下載 40、摘要 50）：成功 161、同樣 8 張失敗、無 429／逾時／重試；耗時 465.4 秒對 422.9 秒，在自然波動內（通過條件 3 過於樂觀，未達成，如實記錄）。
- **決策（使用者）：`download_max_workers` 預設改為 40**。唯一的行為變動：圖片較多的頁面（ncucsie 3 頁）下載並行由 20 提高到 40。
- 意外發現（既有問題）：頁內重複的圖片 URL 會被同時下載多次，失敗原因可能顯示為 `download failed`；已記入 todo「效能優化」，不在此處理。

### C1：`ImageSummarizer` 快取與統計

- **現況**：`_image_cache[url]`、`_downloaded_images[url]`、`_image_captions[url]` 三份資料，後兩者可由第一份推得。
- **快取旗標無作用**：`ImageSummarizer` 只在 `prepare.py` 建立一次、每個 run 只呼叫一次 `summarize_crawl_results_images`，旗標只決定該方法開頭是否清空快取，而此時快取必為空。快取真正的作用（同一 run 內跨頁共用同一張圖、重試輪次間只重做失敗的圖）與旗標無關。刪除旗標的前提已確認：已發布的 `module_config.yml` 只被讀檔頭，不經 `from_yaml`。
- **做法**：單一 `_image_cache: dict[str, ImageEntry]`（dataclass）；三種統計 dict 改為 dataclass，log 表格欄位與格式不變；刪除兩個旗標與 `prepare.py` 的傳入。
- **先補單元測試**（mock `urlopen`／`acompletion`／`completion_cost`／`time.sleep`），通過現行實作後再重構。涵蓋：同一 url 跨頁只下載與摘要一次、下載失敗不送 VLM、不支援的 content-type 視為下載失敗、成功率低於門檻時重試且只重做失敗的 url、`enhanced_markdown` 的 caption 格式、統計累加。

### C4：LLM 供應商路由

三份實作、兩張相同的對照表，行為不一致：

| 位置 | 比對 | 未知模型 | 缺 key | `load_dotenv` |
|---|---|---|---|---|
| `llama_index_helpers.create_llm`（RAG） | 區分大小寫 | `ValueError` | `api_key=None` 傳下去 | 否 |
| `langchain_helper.create_llm`（Agent） | `lower()` | 預設 OpenAI | `ValueError` | 是 |
| `ImageSummarizer._get_api_key`＋litellm 前綴（VLM） | `lower()` | `EnvironmentVariableError` | `EnvironmentVariableError` | 是（每張圖一次） |

做法：新增共用模組，提供 `PROVIDERS`、`resolve_provider(model_name)`（不分大小寫，未知則報錯）、`get_api_key(spec)`；三處改為「resolve → get key → 各自建構 client」，client 參數不變；VLM 改為在 `summarize_crawl_results_images` 開頭取一次 key。**行為改變**：Agent 的未知模型由「預設 OpenAI」改為報錯；所有預設值（`gpt-5.6-*`）與 `configs/` 不受影響。測試先行，行為統一後跑一次付費整合測試。

### C6：runs/ 存檔樣板

「`save_module_config` → `save_site_config` → `save_run_config`」在 prepare（3）、exp（2）、serve（1，無 site）與 `DataManager.write_run_metadata` 各寫一次。不直接改用 `write_run_metadata`：runs/ 存檔時 `log_path` 即 `run_path/terminal.log`，`shutil.copy2` 會拋 `SameFileError`。做法：抽出 `save_run_configs(dest_folder, config, site=None, run_config=None)`，`write_run_metadata` 改為呼叫它再複製 log；檔名常數共用，runs/ 下檔名不變。serve 的 `run_agent_build` 與只存 run_config 的一行呼叫不屬重複樣板，不改。

### C5：來源 dict 共用

`RAG.retrieve` 的 key 順序為 `…, content, url`、不截斷；`extract_sources_list` 為 `…, url, content`、截斷 800 字，docstring 卻稱「形狀一致」。新增 `source_dict(node, max_content_length=None)` 共用，統一為 `url` 在前。統一的順序即 rag-query results.json 原本的順序，results.json 不變；只有不落盤的 `RAG.retrieve` 結果改變，Agent tool 依 key 格式化，LLM 看到的內容不變。

### C10：刪除 RAG run_name 的 `-gemini` 特例

`_post_process_run_name` 在第 2 字元之後出現 `-gemini` 時刪除第一個。預設 `run_name_fields` 不觸發；只有自訂欄位含 `query_llm_name` 時才觸發，且效果是 `…-gemini-2.5-flash` → `…-2.5-flash`，刪掉模型名稱的關鍵部分，應為舊命名規則殘留。只保留 `/` → `-`；現有 runs/ 資料夾名稱不受影響。

### 移出項目

| 項目 | 處理 |
|---|---|
| C3 Rich「Metric／Value」表格抽成 helper（約 6 處） | 併入 todo「包裝 log_helper.py」，與 log API 一起設計 |
| C7 `VectorStoreBuilder.default_hybrid_ranker_params` | 非重複（設定檔寫 `null` 時補內建值），不需處理 |
| C9 空殼 `WebsiteCrawlerRunConfig`／`ImageSummarizerRunConfig` | 設計上保留：每個子命令各有型別，未來加專屬參數不必改簽名 |

## 執行順序與 Commit 策略

| 順序 | 內容 | 依賴 |
|---|---|---|
| 1 | A1 刪除死碼 | — |
| 2 | A2 簡化 `build_rag`／`IndexBuilder` | — |
| 3 | A3 合併重複實作 | — |
| 4 | A4 結構簡化 | A1（`ChatApp` 的 context manager 已刪除） |
| 5 | B1 `data_paths.py` | A1（Discover 方法已刪除） |
| 6 | B2 共用 runs/ 走訪 | A3（`is_run_folder()`） |
| 7 | B3 `new_thread_id()` | — |
| 8 | B4 模組層級 helper | B3（同檔案） |
| 9 | C2 VLM 並行修正；之後並行上限實驗 | — |
| 10 | C1 測試 → 快取合併、刪除旗標 | C2（同檔案） |
| 11 | C6 `save_run_configs` | — |
| 12 | C4 測試 → 供應商路由表 | C1（同檔案） |
| 13 | C5、C10 | — |
| 14 | 拆分 `vlm_max_workers`（commit `7354db5`，含 VLM 並行實驗） | C 組合併 commit |
| 15 | 下載並行上限實驗 → 完整驗證 → 預設值調整 | 14 |

- 實作期間每項一個 commit，方便逐項審核；各組全部完成並審核後，以 `git reset --soft <組基準點>` 合併成單一 commit（A：`refactor: remove dead code and merge duplicates (code cleanup A)`；B：`refactor: centralize data paths, share runs/ lookup and agent result helpers (code cleanup B)`；C：`refactor: fix VLM concurrency, unify image summarizer cache, LLM provider routing and run config saving (code cleanup C)`）。合併後再跑共同關卡，確認 `git diff <合併前 commit> HEAD` 為空。
- C1／C4 各分「補測試」與「重構」兩個 commit（測試 commit 須通過現行實作）；依使用者指示 C2 一併合併進 C 組。
- C 組之後：拆分 `vlm_max_workers` 為獨立 commit；下載並行實驗的紀錄另一個 commit，`download_max_workers` 預設值調整依使用者指示併入該 commit（amend，尚未推送）。
- 不使用 `git rebase -i`；合併前不 push，若已 push 須先與使用者確認。

---

# 二、資料儲存重構

## Context

1. **`rag-query --force-rebuild` 直接重建正式向量庫**：`run_rag_query` 以 `published_target(site_id)` 呼叫 `build_rag(..., force_rebuild=...)`，會清掉並重建 `data/rag/{site_id}/milvus.db`，違反「建庫不直接寫入 data/」，也繞過 `publish_vector_store` 的原子替換；重建中途失敗時正式向量庫會損毀。
2. **向量庫內部路徑過深且有重複片段**：`milvus.db` 是目錄（Milvus Lite），parquet 位於 `data/rag/nculab/milvus.db/collections/nculab/partitions/_default/data/*.parquet`，`nculab` 出現兩次（站點資料夾、collection 名稱）。
3. **載入向量庫會寫入 data/**：Milvus Lite 載入 collection 時會在 `collections/{collection}/partitions/_default/indexes/` 建立索引檔（已實測，`close()` 後仍保留）。此行為與 rag-query／serve 無關，任何載入向量庫的程式都會觸發，所以跑完整合測試後 git 工作樹會出現未追蹤檔案。

## 已確認決策

| # | 問題 | 決策 |
|---|---|---|
| Q1／D4 | `rag-query --force-rebuild` | **移除 `run_rag_query` 的 `force_rebuild`**，建庫邏輯只留在 `run_rag_build`（原方案 A「重建到 run 的 `results/`」被取代） |
| D1 | 向量庫目錄佈局 | **兩項都做**：collection 名稱固定為 `chunks`；去掉 `milvus.db/` 這一層，Milvus 資料夾直接以 `{site_id}.db` 命名，設定紀錄移到其中的 `meta/` |
| D2／D3 | 版本控制、webpages 是否版本化 | **移出本次規劃**：日後一次在所有模組的儲存機制引入，本次不為此預留結構 |
| D5 | 載入時寫入 data/ | **暫時採 `.gitignore` 忽略 `indexes/`**（`data/rag/**/indexes/`） |
| D6 | 向量庫是否進 git | 暫時保留 |
| D7 | 既有向量庫的遷移 | 方案 b：從 `data/webpages/{site}` 只重跑建庫階段（`run rag-build` + publish），不重爬、不重跑圖片摘要 |
| D8 | `meta/` 放在 Milvus 資料夾內 | 已驗證可行，並發現資料夾須以 `.db` 結尾 |
| D9 | 查詢 runs/ 中的實驗向量庫 | 方案 b：`rag-query` 新增 `--run.vector-store-run <run 路徑>`，本次一併實作 |
| D10 | 受 `.db` 限制的佈局 | **採 (i)**：`data/rag/{site_id}.db/` 為 Milvus 資料夾，`meta/` 放在其中，publish 以整個資料夾原子替換，向量庫與紀錄同版（代價：與 `data/webpages/{site}` 命名不一致） |
| D11 | `vector_store_run` 是否核對建置參數 | 不比對（與已發布向量庫一致），只在 log 印出建庫 run 的 `source` |

**D1／D10 的佈局**：`data/rag/nculab.db/` 內含 Milvus Lite 的 `collections/chunks/partitions/_default/data/*.parquet` 與 `databases/`、`LOCK`，另有 `meta/`（`module_config.yml`、`run_config.yml`、`site_config.yml`、`terminal.log`），與向量庫同一次原子替換。parquet 路徑由 `data/rag/nculab/milvus.db/collections/nculab/…` 縮短為 `data/rag/nculab.db/collections/chunks/…`；`collections/…/partitions/_default/data/` 是 Milvus Lite 內部結構，無法移除。站點資訊仍保留在 node metadata 的 `site_id`，不受 collection 改名影響。

**D5：索引檔的用途**：parquet 是資料本體；`indexes/` 下的 `.idx` 是 Milvus Lite 載入時依 `manifest.json` 的 `index_specs` 由 parquet 建出的檢索索引。已實測刪除後再次載入會重新產生，因此不需版控。限制：載入仍會改動 `data/`，若日後 `data/` 掛載為唯讀會失敗，屆時再改為載入前複製到暫存。實測只觀察到 dense 的 `.idx`，sparse 索引是否也落地未確認。

**D8 驗證結果**（在 `data/rag/nculab` 複本上實測）：

| 項目 | 結果 |
|---|---|
| Milvus 資料夾內放額外的 `meta/` | 可行，載入、查詢、關閉都正常 |
| 整個資料夾 `os.replace` 改名後重新載入 | 可行 |
| 資料夾名稱 | **必須以 `.db` 結尾**，否則 `MilvusClient` 報 `uri ... is illegal`，因此「站點資料夾直接作為 Milvus 資料夾」無法照原樣實現，改採 D10 |
| `rename_collection` | 可行，表示 D7 方案 c（改名遷移）技術上可行；已依決策採方案 b |

## 變更範圍

### Phase 1：移除 `run_rag_query` 的 `force_rebuild`（D4）

- `RAGQueryRunConfig` 刪除 `force_rebuild`；`run_rag_query` 只以 `published_target` 載入查詢，向量庫不存在時報錯並提示先 `prepare` 或 `run rag-build`。`build_rag` 的 `force_rebuild` 參數保留（`run_prepare` 仍使用）。
- `.gitignore` 加入 `data/rag/**/indexes/`（D5）。
- **D9：`--run.vector-store-run <run 路徑>`**：新增 `vector_store_run: str | None`，指向 `rag-build` 的 run 資料夾，向量庫位置為 `<路徑>/results/milvus.db`；未指定時查詢已發布向量庫。查詢用的 `RAGConfig` 仍由 `--run.config` 與 `--module.*` 決定（可對同一份向量庫試不同 retriever／query engine 參數）；向量庫的建置參數需與建庫時一致，載入時不比對，只在 log 印出建庫 run 的 `source`（D11）。路徑不存在或缺向量庫時報錯；站點以 `<路徑>/site_config.yml` 的 `site_id` 核對，不一致時報錯。此模式完全唯讀。

### Phase 2：向量庫路徑重整（D1、D10）

- collection 名稱改為常數 `chunks`；`RAGTarget.milvus_uri` 在 data/ 為 `data/rag/{site_id}.db`，在 runs/ 維持 `results/milvus.db`（皆以 `.db` 結尾）。
- **publish 流程**：staging 改為 `data/rag/.staging-*.db`（Milvus 資料夾本身）→ 建庫 → 將 `meta/` 寫入 staging → 以 `os.replace` 整個資料夾換成 `{site_id}.db`（先 `.old` 備份、失敗還原，沿用現行邏輯）。`publish_run_metadata` 的 rag 部分改為寫入 staging 的 `meta/`。
- 讀取端（`RAGRegistry` 與站點列表）改以 `*.db` 資料夾判斷，忽略 `.staging-*`／`.old`／`.tmp`。
- 既有 `data/rag/{nculab,ncucsie,claudecode}` 以 `run rag-build` + publish 重建（D7 方案 b，需 embedding 費用，執行前先向使用者確認），舊資料夾隨重建刪除。Phase 2 動工前先以舊程式產生遷移前基準（collection 筆數、每筆 `text` hash 與 metadata 排序清單、`du -sh`；embedding 向量不比對）。

---

# 驗證

## 共同關卡（兩部分的每個 commit／Phase，含合併後的 commit，都必須通過）

1. `scripts/check.sh` exit 0（ruff、pyright、`tests/unit`、widget 同步）。
2. `uv run pytest tests/integration -m "not cost"` 通過。
3. CLI 冒煙：`website-copilot prepare --help`、`serve --help`、`run {website-crawler,image-summarizer,rag-build,rag-query,agent} --help` 皆 exit 0。
4. 測試前後 `git status --short` 無新增未追蹤檔（驗證 `indexes/` 已被忽略、測試不會弄髒 `data/`）。
5. 結果記錄在 `dev.md`。

## 程式碼清理

- A1：grep 被刪除的名稱，只剩文件中的歷史紀錄。A2：grep `force_rebuild`、`build_or_load`、`_should_rebuild`，src／tests 皆無結果。A3：`test_configs`、`test_site_config` 的錯誤訊息斷言不修改即通過。A4：`test_agent_server` 不修改即通過。
- 重構前先補特徵測試並在舊程式碼上確認通過（B2、C1、C4、C6 等），新測試要先確認在舊實作上失敗（bug 修正與行為變更）。
- **付費整合測試**：A 組與 B1／B2／B4 不改變行為，不需要。B3 修正了落盤 thread_id，C 組合併後跑一次（涵蓋 B3），於並行上限實驗之前、需使用者確認：

  | 改動 | 涵蓋的測試 |
  |---|---|
  | C2、C1、C4 的 VLM 路由 | `test_image_summarizer`、`test_prepare` |
  | C6 | `test_website_crawler`、`test_image_summarizer`、`test_rag_build`（save=True） |
  | C4 Agent 路由、C5 `RAG.retrieve`、B3 | `test_agent_query` |
  | C4 RAG 路由、C5 `extract_sources_list` | 手動 `rag-query`（整合測試未涵蓋） |

  步驟：確認 `.env` 有 `OPENAI_API_KEY`；`uv run pytest tests/integration`；`uv run website-copilot run rag-query nculab --run.config test`。皆 `publish=False`，只寫入 runs/；估計約 $0.15～0.20、6～8 分鐘。通過條件：
  1. image_summarizer 成功數與舊紀錄相近（nculab 57 張、0 失敗），無 `task failed unexpectedly`，統計表格格式不變。
  2. 各 run 資料夾皆有三個 yml，`module_config.yml` 檔頭有 `# source:`，image_summarizer 的 config 不含兩個快取旗標。
  3. agent_query 的 `results_<thread_id>.json` id 與實際對話 id 相同（B3），sources 正常。
  4. rag-query results.json 的 sources key 順序為 `page_title, score, page_type, url, content`。

## 資料儲存重構

**驗證 `data/` 不被寫入**：單元測試以 `tmp_path` 作為 data 資料夾，比對執行前後整個目錄樹（檔名＋內容 hash）；實測對真實 `data/rag/{site}` 計算「排除 `indexes/` 的逐檔 sha256 清單」，執行 `rag-query`（已發布與 `--run.vector-store-run` 兩種模式）前後比對相同。

**Phase 1**：

- CLI：`--run.force-rebuild` 被 tyro 拒絕；`rag-query --help` 顯示 `--run.vector-store-run`。
- `vector_store_run` 單元測試：target 的 `milvus_uri` 與 `site_id`；路徑不存在、缺向量庫、`site_config.yml` 與 `run_config.site` 不一致都報錯且訊息含路徑；未指定時使用 `published_target`；log 印出建庫 run 的 `source`。
- `.gitignore`：`git check-ignore` 命中 `indexes/*.idx`，`*.parquet` 等其他路徑不被誤忽略。
- grep `force_rebuild`：只剩 `build_rag`／`run_prepare`／`IndexBuilder` 內部使用。
- **付費實測**（每次先向使用者確認）：`run rag-build nculab --run.config test` 建出實驗向量庫 → `rag-query --run.vector-store-run <該路徑>` → `rag-query`（已發布）；確認兩種模式皆成功、`module_config.yml` 與 log 正確、data/ 目錄樹 hash 前後相同。

**Phase 2**：

- **結構**：每站 `data/rag/{site}.db/` 存在、`list_collections()` 恰為 `['chunks']`、`meta/` 含三個 config 與 `terminal.log`、舊 `data/rag/{site}/` 不存在；所有 parquet 路徑中 `site_id` 只出現一次且無 `milvus.db` 目錄層（單元測試以 regex 斷言）；node metadata 的 `site_id` 仍存在。
- **publish 原子性**（單元測試，`tmp_path` 假 data 資料夾）：成功時舊版被取代、`meta/` 與向量庫同一次建置、無殘留；失敗注入（`os.replace` 前後各丟例外）時正式資料夾維持舊版、staging 被刪除；前次殘留的 `.old`／`.tmp` 被清掉；已開啟舊版的 reader 在 publish 期間不報錯。
- **讀取端**：`RAGRegistry.has` 與列出站點只認 `*.db` 資料夾，放入 `.staging-*`／`.old`／`.tmp` 干擾確認不被列為站點；repo 內三個已發布向量庫皆能以 site_id 載入。
- **遷移後比對**（付費，先向使用者確認）：筆數與 text hash、metadata 排序清單與基準相同（資料來源未變，建庫結果應一致），不同者逐一檢視原因；每站以 `sample_query` 比對 top-k url 集合；`du -sh data/rag/*` 與基準比較，git 差異不應有 `indexes/` 檔案。
- grep `milvus.db`：只剩 runs/ 的 `results/milvus.db`（含 `vector_store_run`）與刻意保留者。
- 整合測試（含 cost）全數通過。
- **付費測試安排**：Phase 1 完成後一次（驗證 D9），Phase 2 遷移與完整整合測試一次；每次執行前先向使用者確認，結果與花費記錄在 `dev.md`。每個 Phase 一個 commit。
