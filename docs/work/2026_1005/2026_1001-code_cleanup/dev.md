# 程式碼清理與資料儲存重構：實作紀錄

> 計畫見 [plan.md](./plan.md)。只記錄與 plan 不同的決定、過程中的發現與驗證結果。除特別註明外，每項的驗證皆為共同關卡（`check.sh`、`tests/integration -m "not cost"`、7 個 CLI `--help`）通過，括號內為 `check.sh` 的通過測試數。

基準點：A 組 `dc52401`；B 組 `754a8de`（A 組合併 commit）；C 組 `e9f869e`（B 組合併 commit）。

---

# 一、程式碼清理

## A 組

### A1：刪除死碼（375 passed）

除 plan 所列，另做了這些：`KEEP_TITLE_CONTENT_THRESHOLD` 的值 `0.45` 記錄於 `docs/code/phase1/modules/data_collect.md`；`checkpointer` 改為必填（唯一呼叫端 `create_agent` 一定傳入）；`create_run_no_site_context` 移除 `run_name` 參數；`RunManager.__init__` 的 `module_name` 改為必填並刪除 `init_module_run_paths` 中走不到的檢查（保留 `run_name` 檢查，欄位全為 None 時會得到空字串）；`run_rag_query` 的 `except` 內重複的 `rag.close()`；`IndexBuilder.load` 的 `vector_store_type == "milvus"` 判斷與 `_close_vector_store` 的 `isinstance(MilvusVectorStore)` 判斷（型別為單值 `Literal["milvus"]`）。

### A2：簡化 `build_rag`（371 passed）

少 4 個為刪除的測試。`test_build_rag_does_not_modify_config` 補 patch `load_source`。grep `force_rebuild`：src 無結果，tests 只剩「`--run.force-rebuild` 被拒」的 CLI 測試。

### A3：合併重複實作（371 passed）

- `MARKDOWN_IMAGE_PATTERN` 放在 `utils/text_helper.py`，不放在 crawler 內，避免 summarizer 間接 import crawl4ai。
- **與 plan 不同**：plan 寫「保留 `overrides._section_type`、`base_config` 改用」，但 `_section_type` 會接受 `Model | None`，使 `run_name_fields` 可指到可能為 None 的 section（`get_field` 會 `AttributeError`），行為較原本寬。為維持行為不變，`base_config._has_field_path` 仍只接受型別恰為 ConfigModel 子類的 section，`overrides._section_type` 維持原狀。
- `BaseModuleConfig`、`SiteConfig` 改為繼承 `LoadedConfigModel`，共用 `validate_loaded`。
- `publish_crawl_results`／`publish_markdown` 的 log 統一為 `Published {markdown_key} pages to ...`（原本只有後者有 log）。

### A4：結構簡化（371 passed）

`run_workflow_context` 改 `@contextmanager` 的副作用：初始化中途失敗（如 `log_run_paths("init")` 拋錯）時，ExitStack 也會關閉已開啟的 log tee（原本不會）。手動確認區塊內 `return` 與拋例外兩種結束方式：return 時 log 含 complete 路徑表，例外時沒有，兩者皆記錄耗時並還原 stdout。

## B 組

### B1：`storage/data_paths.py`（381 passed）

除 plan 所列函式，另有 `site_id_from_vector_store_name`（`{site_id}.db` → site_id，`.staging-*`／`.db.tmp`／`.db.old`／隱藏檔回傳 None）。src 內不再有 `"vector_db"`／`"aug_webpages"`／`"raw_webpages"` 的路徑字串。新增 10 個測試（佈局、無檔案系統副作用）。

### B2：共用 runs/ 走訪（391 passed）

抽出 `_iter_site_run_folders` 與 `_walk_sorted`；`load_latest_run_path` 的 `site_id` 改必填；刪除 `load_latest_results` 中走不到的 `isfile` 檢查。**重構前先補 9 個特徵測試並在舊程式碼上確認通過**：較新的 run 缺 `results.json`／`results/` 時退回較舊的 run、不退回其他站點、忽略非時間戳資料夾、無任何 run 報錯。

### B3：`new_thread_id()`（393 passed）

判斷語意維持各處原樣（`run_agent_query` 以 `is None`、server 以 `or`，空字串視為未提供）。`test_run_agent_query_auto_generates_thread_id` 增加「`ask` 收到的 thread_id 與落盤相同」斷言，已確認在舊程式碼上失敗。付費整合測試待 B 組合併後執行。

### B4：模組層級 helper（397 passed）

欄位與順序不變，落盤格式不變；server 的 `query` 仍是使用者原始問題（非加站點前綴的版本）、仍逐 token yield。新增 4 個測試（`ask`／`astream_result` 原本沒有單元測試），已用重構前的實作確認通過。

## C 組

依使用者指示，C2～C10 全部完成後合併為單一 commit。

### C2：VLM 並行數限制（399 passed）

修正前 `(3, 10)` 失敗（peak 為 10），修正後通過。

### C1：`ImageSummarizer` 快取與統計（409 passed）

- 先補 10 個測試（獨立 commit），以重構前的實作確認通過；重構後只改 `_make_summarizer` 的參數與 `_stats` helper，斷言不變。
- 順帶清除：`_download_image` 改為只回傳 `str | None`（原本的 status 字串只用在永遠為 False 的 `"failure" in download_status` 判斷，`"failed"` 不含 `"failure"`）；`_enhance_markdown` 刪除 `if not self._image_captions` 的提早 return（條件不會成立）。
- `image["caption"]` 只在該圖已有摘要結果時寫入，與原本條件相同；`_agenerate_image_caption_task` 包裝層保留（負責把 url 附在結果上）。

### C6：runs/ 存檔樣板（412 passed）

未改 serve 的三處呼叫（理由見 plan）；serve 測試逐一 mock 這兩個函式。`test_pipeline_rag_query` 的 fixture 改 mock `save_run_configs`。新增 `_assert_run_configs_saved` 測試，先以重構前的實作確認通過。

### C4：LLM 供應商路由（431 passed）

測試先行（獨立 commit，12 個）。`ImageSummarizer` 改在 `summarize_crawl_results_images` 開頭解析一次，每張圖不再重複 `load_dotenv`。行為統一的效果：RAG 缺 key 時於建立 LLM 時報錯（原本把 `None` 傳給 SDK）；ImageSummarizer 的未知模型或缺 key 在開始前失敗（原本在每個 caption task 內拋出，被當作「unexpectedly failed」逐張記 warning）。

### C5、C10（436 passed）

- C5：新增 `test_sources.py`，以 dict 相等斷言先在重構前確認通過，重構後再加 key 順序一致的測試。
- C10：`test_rag_run_name_keeps_gemini_model_name`，舊實作得到 `…query_llm_name-models-2.5-flash`（失敗），修改後為 `…-models-gemini-2.5-flash`。

### 付費整合測試（C 組合併後，含 B3）

- `uv run pytest tests/integration`：7 passed（6 分 53 秒）；`run rag-query nculab --run.config test`：成功（20.5 秒），Faithfulness 1/1、Relevancy 1/1。

通過條件：

1. image_summarizer（兩次）各 57 張成功、0 失敗，格式與舊紀錄（`20261002_135115`：57 成功、cache_reuse 1）相同。✅ 耗時 142.5／122.9 秒（舊紀錄 109.6 秒）；nculab 單頁最多 17 張，未達上限 20，semaphore 不會限速，差異應為 VLM 延遲波動。
2. 所有 run 皆有三個 yml，`module_config.yml` 首行為 `# source: configs/...`，image_summarizer 的 config 無 `cache_*`。✅
3. agent_query 結果檔以自動 id 命名、sources 正常（7 個 URL）。⚠️ **部分驗證**：terminal.log 不印 thread_id，「落盤 id 與對話 id 相同」無法由 log 直接核對（checkpointer 為記憶體內，也無法跨程序續接），由單元測試保證。
4. rag-query results.json 的 sources 10 筆，key 順序與舊 run（`20261001_162920`）相同。✅

成本：log 有記錄的部分（crawler 與 summarizer）約 $0.143；agent_query、rag-query、embedding 未記錄，估計數美分，總計約 $0.15～0.20，與估算相符。

### C2：並行上限實驗

腳本與結果在 `docs/exp/memo/webpage_image_summarizer/vlm_concurrency/`，先 `--dry-run` 確認流程。N=20 後 rate limit header 顯示 RPM 30,000／TPM 1.8 億（理論可承受並行約 4,000），依使用者決定只再跑 60、100（plan 原訂 20～100 每 10 一級）。結果：20／60／100 共 360 個請求、0 失敗，實測最高並行等於 N；延遲 p50 7.95 → 9.39 秒，吞吐量 1.54 → 5.24 req/s；成本 $0.402。結論：VLM 端不是瓶頸，提高預設值的風險在下載端（未涵蓋）。

### 拆分 `vlm_max_workers`

新測試先以舊實作確認失敗。注意 `fakes` fixture 會把全域 `time.sleep` 換成 no-op，下載端測試改用 `threading.Event().wait()` 製造延遲。並行實驗的 `probe.py` 改用新參數名，`results.md` 註記實驗當時的舊名稱。

### 下載並行上限實驗（ncucsie）與完整驗證

- 腳本與結果在 `docs/exp/memo/webpage_image_summarizer/download_concurrency/`。先 `--dry-run`（含模擬限流時在失敗率 > 20% 的級距停止）；正式跑 20／30／40／50 共 280 個請求，**0 失敗**；吞吐量從 N=20 起固定約 10 MB/s，更高並行只讓延遲變長（p50 ×1.00／1.67／2.19／2.62）。
- 完整驗證（下載 40、摘要 50，`save=True`／`publish=False`，`data/` 無變動）：
  1. 摘要成功 161、同樣 8 張失敗，無 429／逾時。✅
  2. 無 `retrying`（下載失敗累計 33，成功率 83%，仍高於 0.8）。✅
  3. 統計表格格式不變 ✅；耗時 465.4 秒，**未達「不長於舊紀錄 422.9 秒」** ⚠️：差異在自然波動內（nculab 相同設定三次為 109.6／142.5／122.9 秒），預期並行增益（3 個大頁，合計估計 < 40 秒）小於雜訊，此條件過於樂觀。
  4. 費用 $0.1676（估計 $0.16）。✅
- 預設值：機械套用規則為 40，但吞吐量在 20 並行即飽和，我建議維持 20；**使用者決定改為 40**，與實驗紀錄一併 amend 到同一個 commit。
- 意外發現（既有問題）：同一頁內重複的圖片 URL（全站 10 頁）會被同時下載多次，失敗原因可能顯示為 `download failed` 而非 `HTTP Error 404`（`doc.gif%20`）。未修正，已新增 todo「圖片摘要：同一頁內重複的圖片 URL 會被同時下載多次」。

---

# 二、資料儲存重構

## Phase 1：移除 `run_rag_query` 的 `force_rebuild`、新增 `--run.vector-store-run`

### 與 plan 不同或補充

- `load_rag(config, target, build_query_engine=False)` 新增 `build_query_engine`，供 rag-query 使用。
- `run_rag_query` 由 `build_rag(..., force_rebuild=...)` 改為 `load_rag(..., build_query_engine=True)`。連帶修正既有行為：原本向量庫不存在時 `build_or_load` 會自動建庫到 `data/rag/{site}/milvus.db`，現在報錯。
- `run_rag_build` save 時補存 `site_config.yml`（驗證時發現 rag-build 的 run 資料夾原本沒有，`vector_store_run` 無法核對站點）。
- 新增 `test_pipeline_rag_query.py`、CLI 測試（`--run.force-rebuild` 被拒）等。

### 驗證

`check.sh`：352 passed；integration 免費部分 2 passed。**付費實測**（使用者已確認）：

- `run rag-build nculab --run.config test` 的 run 資料夾含 `site_config.yml`。
- `rag-query nculab --run.vector-store-run <該 run>`：exit 0，log 印出 `建庫設定 configs/rag/test.yml`；`rag-query nculab`（已發布）：exit 0。
- `rag-query ncucsie --run.vector-store-run <nculab 的 run>`：`ValueError: 站點不一致`；`--run.vector-store-run runs/nope`：`FileNotFoundError`。
- `data/rag`、`data/webpages`（排除 `indexes/`）所有檔案的 sha256 清單於查詢前後完全相同。

驗證小插曲：第一版 tree-hash 腳本用 `sorted(os.walk())` 先走完整棵樹，`indexes` 的剪枝無效，導致誤報 data/ 有變動；改為逐檔 sha256 清單（`find -prune`）後確認無變動。

## Phase 2：向量庫路徑重整

### 與 plan 不同或補充

- `publish_vector_store(site_id, source_path, move, write_meta)`：放到 `{site_id}.db.tmp` → 呼叫 `write_meta(<tmp>/meta)` → `os.replace` 整個資料夾；來源不是資料夾報 `NotADirectoryError`。`publish_run_metadata` 拆出 `write_run_metadata(dest_folder, ...)` 供 meta 寫入共用。
- `run_rag_build`：建庫無產出時略過 publish 並印出訊息（紀錄隨向量庫發布，沒有向量庫就沒有地方放）。
- **Milvus Lite server 未停止的 bug（驗證中發現並修正）**：`_close_vector_store` 只關 client，in-process 的 Milvus Lite server 要到程式結束才 flush。publish 搬移資料夾後，結束時的 flush 寫回原 staging 路徑（重新產生 `.staging-*/…db` 殘骸），已發布的向量庫則只剩未 flush 的 WAL（claudecode 的 WAL 達 82MB、沒有 parquet）。現在 `_close_vector_store(vector_store, milvus_uri)` 一併呼叫 `server_manager_instance.release_server()`；新增 `test_index_close.py` 以真實 Milvus Lite 驗證 close 後已有 parquet、搬移後原路徑不會被重建。
- 既有三個站點以 `run rag-build <site> --run.no-save --run.publish` 重建並發布（D7 方案 b，實際執行兩輪：第一輪發現上述 bug，清掉後重跑）。
- 新增 `test_published_layout.py`：repo 內已發布向量庫的 collection 為 `chunks`、parquet 路徑 site_id 只出現一次且無 `milvus.db`、`meta/` 內容、`data/rag` 無殘留。

### 驗證

`check.sh`：370 passed；`tests/integration`（含 cost）：7 passed，455 秒；三站 `rag-query` 皆 exit 0，結果中 `collection_name` 為 `chunks`。**遷移前基準與遷移後比較**：

| 站點 | 筆數 舊 → 新 | 頁面集合 | top-k url（sample_query） | 體積（不含 `indexes/`） |
|---|---|---|---|---|
| nculab | 277 → 274 | 相同（47 頁） | 重疊 5/6 | 1.5M（舊 3.2M 含 indexes） |
| ncucsie | 737 → 723 | 相同（192 頁） | 重疊 8/9 | 3.1M（舊 3.3M） |
| claudecode | 6465 → 6463 | 相同（193 頁） | 5/5，順序相同 | 29M（舊 29M） |

筆數與 text hash **不完全相同**，已逐一檢視：目前 `data/webpages/` 的 markdown 與舊向量庫建庫時的版本有空白差異（舊 chunk 為 `**圖片摘要：**  \n> …`，行尾有兩個空格，現在沒有），使個別頁面的 chunk 邊界偏移、少 1 個 chunk（例：nculab 的 `projects` 9 → 8）。以「空白正規化後的行」比較，各站只有 0～65 行（總計 1300～34042 行）不見於對方，為 chunk 邊界切開所致。此差異來自資料來源而非本次改動：`IndexBuilder.build_nodes` 與 chunk 參數（800／100）未變。新向量庫 node metadata 的 `site_id` 皆正確。

**未做**：`prepare nculab --run.config test` 的完整 publish 流程——它會以 `max_pages=40` 的測試資料覆寫已提交的 `data/webpages` 與 `data/rag` 內 nculab 資料；publish 位置與 `meta/` 已由單元測試與三站的實際 `rag-build --run.publish` 覆蓋。
