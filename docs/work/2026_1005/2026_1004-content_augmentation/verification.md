# 驗證紀錄

各階段 commit 前的驗證結果（共通驗證 C1–C7 與獨特驗證，見 [plan.md](plan.md)「驗證機制」）。

## P0：爬蟲排除文件 URL

### 自動化

- `scripts/check.sh`：ruff、pyright 通過；`pytest tests/unit` 475 passed、1 failed。
  - 失敗的 `test_cli.py::test_serve_command` **與 P0 無關**：在未改動的 HEAD（stash 後）同樣失敗，原因是 `f1d573b` 將 `serve` 改名為 `run_serve` 後測試未同步。未在本階段處理。
- 新增 `tests/unit/test_document_rules.py`（36 個測試）：
  - 副檔名大小寫（`.PDF`、`.Docx`）、帶 query／fragment 仍判為文件；
  - `.php`、`pdf.gif%20`、`doc.gif`、`?file=a.pdf`（副檔名只在 query）不被誤判；
  - `downloadfile` 站點樣式只在提供 `url_patterns` 時命中；
  - `SiteDocumentsConfig` 預設 `[]`，ncucsie 為 `["*Action=downloadfile*"]`、nculab 為 `[]`；
  - `WebsiteCrawler._build_filter_chain()`：文件 URL 不通過，一般頁面通過，無站點過濾時仍排除文件；
  - `success=False` 記錄實際 `error_message`、計入 `error_failed`，不再記為 `no markdown`。

### 實跑（ncucsie，`--run.no-publish`，`runs/20261004_170334/`）

| 指標 | 舊（data/raw_webpages） | 新 |
|---|---|---|
| 頁面數 | 149 | 146 |
| `error_no_markdown` | 47 | 0 |
| `error_failed`（新） | — | 3 |
| `error_404` | — | 6 |
| 導航觸發 `Download is starting` | 約 45 | 1 |

頁面集合差異（舊 149 vs 新 146）：

- 舊有新無 5 筆：
  - `p_406-1013-13291,r375.php`、`p_406-1013-13922,r376.php`：新增公告擠掉舊公告，新有 `p_406-1013-14068,r375.php`、`p_406-1013-14070,r376.php`，屬網站內容變動；
  - `static_file_13_1013_img_222010142.png`、`..._143_hackathon_taiwan.jpg`：圖片 URL，舊次被當成空頁面（fit_markdown 長度 0），這次被 anti-bot 檢查判為 `success=False`（`minimal_text`）而略過，無實質內容損失；
  - `~ypcheng`：舊次為 120 字元的外部個人頁，這次未取得，原因未查（疑為網站或連線波動）。
- 新有舊無 2 筆：即上述公告。

`error_failed` 的 3 筆：兩張圖片（anti-bot）與 `static/file/13/1013/img/681518947`（無副檔名的附件，導航時下載，Unexpected error）。

### 已知限制

- 無副檔名且非站點樣式的附件（如 `681518947`）無法由 URL 規則辨識，仍會被導航一次並記為 `error_failed`；P2a 的 DocumentCollector 以內容判斷格式，屆時再評估是否補站點樣式。

### 費用

exclude words 的 LLM 呼叫（小額，未另行統計）。

## P1a：基準快照測試 + 共用下載器

### 自動化

- `scripts/check.sh`：ruff、pyright 通過；`pytest tests/unit` 506 passed；widget 同步通過。
  - 順帶修正 `test_cli.py::test_serve_command` 的過時 patch 目標（`serve` → `run_serve`，P0 時記錄的既有失敗）。
- 免費整合測試 `pytest tests/integration -m "not cost and not network and not heavy"`：2 passed。
- **基準快照**（`tests/unit/test_augmentation_snapshot.py`，fixture 在 `tests/fixtures/augmentation_snapshot/`）：
  - 輸入：nculab 真實爬取結果（47 頁、74 個圖片引用），加上注入圖片（跨頁共用成功／404 各三頁、Content-Type 不符、svg）。
  - fake 下載與 VLM 的行為由 URL 的 sha1 決定：404、Content-Type 不符、首次逾時（重試後成功）、VLM 失敗、正常；與實作無關，重構時只替換 fake 掛入位置，期望值不變。
  - 以現行 `ImageSummarizer` 產生基準（`expected/results.json` + `expected/results/*.md` 共 47 份）。
  - 涵蓋情境：下載失敗、格式不符、svg 略過、跨頁快取、VLM 失敗、無圖片頁面、整輪重試（`time.sleep` 以 fake 取代；基準產生時跑滿 3 輪）。
  - 另有「連跑兩次輸出相同」「情境覆蓋檢查」「輸入 fixture 不被改動」三個測試。
  - 注入的 svg 排在頁面最後一張，避免觸發 P1c 才修正的描述對位 bug（見 plan P1c 行為變更表）。
  - 更新快照：`UPDATE_SNAPSHOT=1 pytest tests/unit/test_augmentation_snapshot.py`（僅限有意的輸出變更，如 P1d）。
- **共用下載器**（`utils/http_downloader.py`，`tests/unit/test_http_downloader.py` 25 個測試，`httpx.MockTransport`）：結果欄位、輸入去重與順序、同時連線數 ≤ 上限（跨所有 URL）、5xx／429／逾時／連線錯誤重試而 4xx 不重試、重試用盡回報最後錯誤與嘗試次數、`max_bytes`（串流超限與 Content-Length 預檢，皆不重試）、重新導向 `final_url`、預設／自訂標頭、`on_complete` 每個不重複 URL 一次、無效協定不重試、單一失敗不影響其他。
- httpx 由 dev group 移到 `[project].dependencies`（版本不變，`uv.lock` 只更新依賴宣告）；pytest 新增 `network`、`heavy` marker。

### 實跑

- `network` 測試（`tests/integration/test_http_downloader_network.py`，免費）：下載 ncucsie 的 `downloadfile` 連結，回 200、帶 `Content-Disposition`、內容為 PDF（`%PDF`）。

## P1b：改名 augmenter、config 分段（語意不變）

### 自動化

- `scripts/check.sh`：ruff、pyright 通過；`pytest tests/unit` 506 passed。
- **基準快照測試逐字一致**：`test_augmentation_snapshot.py` 的期望值（`expected/`）未更動，改名與 config 分段後仍通過。
- 現有 `test_image_summarizer.py` 改名為 `test_augmenter.py`，斷言未改（只有類別與模組名稱）。
- config 測試改用新欄位：`retry.max_retries`（數字字串被拒）、`download.timeout`（int 收為 float）、`images.prompt`（保留前後空白）、overrides 模型含 `images` 區塊。
- `test_pipeline_prepare.py`、`test_rag_tools.py` 的 `aug_webpages_data_use_latest_results` 改為 `use_latest_results`；`test_run_persistence.py`、`test_pipeline_prepare.py` 的 runs 資料夾改為 `augmenter`。

### 驗證項目

- `grep -rIn "image_summarizer|ImageSummarizer|image-summarizer|aug_webpages_data_use|aug-webpages-data"`（`src/`、`configs/`、`tests/`、`README.md`、`docs/code/`）：無結果。歷史工作文件（`docs/work/`）與已發布的 `data/` 紀錄依計畫保留舊名稱。
- `run augmenter --help`：可執行，列出 `module.download`／`module.retry`／`module.images` 區塊；`run image-summarizer`：已移除（exit 2）。
- runs/ 模組資料夾名稱為 `augmenter`（`create_run_context(module="augmenter")`，由 `test_augmenter_save_writes_results_and_run_configs` 驗證路徑 `*/augmenter/<site>/r1`）；`retrieval/factory.py` 找最新結果處同步修改。
- `docs/exp/memo/webpage_image_summarizer/` 的 3 支實驗腳本（pyright 會檢查）同步改為新的模組與 config 路徑；目錄與結果文件名稱不動。
- 文件同步：`README.md`、`configs/README.md`、`docs/code/runs/{cli,config,workflow}.md`、`docs/code/phase1/modules/data_preprocess.md`。

### 備註

- Augmenter 建構子與 `summarize_crawl_results_images` 的參數名稱本階段不變（P1c 重構時一併處理）；config 到參數的對應在 `run_augmenter`。
- 舊 `runs/<ts>/image_summarizer/` 紀錄不相容、不遷移；手動執行 `run rag-build --run.use-latest-results` 前須先執行一次 `run augmenter`。

## P1c：Augmenter 架構重構

### 自動化

- `scripts/check.sh`：ruff、pyright 通過；`pytest tests/unit` 532 passed。免費整合測試 2 passed。
- **基準快照逐字一致**：`expected/` 未更動（`git status` 無變更），新架構（整批下載、單一 VLM semaphore、依 URL 對位）輸出與 P1a 以舊實作產生的基準完全相同。快照測試只替換 fake 掛入的位置（`urlopen` → 下載器 fake、`module.acompletion` → `image_captioner.acompletion`）。
- **14 個行為測試移植**（`test_augmenter.py`）：斷言不變，fake 由 `urlopen` 改為 `FakeDownloader`；「每頁各自計算」的兩個並行測試改為斷言跨頁共用上限（真實 `HttpDownloader` + `httpx.MockTransport`；VLM 上限同樣跨頁）。
- **新增測試**：
  - 同頁重複 URL 只下載與摘要一次；
  - 失敗資源跨三頁：只下載一次、只計一次失敗（記在第一個引用頁面，其餘 `cache_reuse`）；
  - 成功率以不重複資源計算（壞圖出現在 5 頁 + 4 張好圖 = 80%，不重試）；
  - 404／410／400、超過大小、無效 URL、Content-Type 不符：不重試、直接列為最終失敗；
  - 逾時、連線錯誤、500、503、429、403 觸發整輪重試；VLM 失敗觸發重試且不重新下載；
  - svg 排在前面時描述仍插在正確位置，`Image-{n}` 為頁內圖片序號；
  - `ImageCollector`（`test_collectors.py`）：兩種來源、跨頁去重與引用順序、副檔名過濾（不分大小寫、忽略 query）。
- 設定：`download` 新增 `max_retries`（預設 2）、`max_bytes`（預設 50 MiB），`download.max_concurrency`／`images.max_concurrency` 改為跨頁共用；`Augmenter` 改為注入下載器、以 `augment()` 為入口（`ImageCaptioner` 在開始時建立，無法判斷供應商或缺 key 仍在下載前失敗）。

### 實跑（nculab 真實 VLM，`runs/20261004_173501/`）

- 先前 `data/raw_webpages/nculab` 的圖片網址為 Google Sites 簽名連結，已過期（全部 403），無法重用；改以 `run website-crawler nculab --run.no-publish` 重爬（47 頁，`error_failed` 0）作為輸入。
- 新版：`run augmenter nculab --run.config test --run.no-publish`，73 個不重複圖片全部成功（下載失敗 0、摘要失敗 0、`cache_reuse` 1 = 唯一的跨頁重複），無重試，**耗時 27.3 秒**，統計與不重複資源數（74 個引用 − 1 個重複 = 73）一致。
- 重構前（P1a commit 的程式碼，同一份爬取結果）：**耗時 194.5 秒**，同樣 73 張成功。整批下載與跨頁共用 VLM 上限使耗時約降為 1/7。
- 兩者輸出結構一致：47 頁的 `url`／`metadata`／`crawl_info` 相同；`images[]` 的 URL 與 caption 欄位有無相同；移除描述區塊後的 `enhanced_markdown` 逐頁相同；`Image-{n}` 標題序列相同；內容差異只在 VLM 描述文字（模型輸出不確定，本就不比對內容）。
- 費用：兩次實跑各 73 次 VLM 呼叫（gpt-5.6-luna）；log 表格的費用欄因欄寬被截斷（顯示 `$0.0…`），未取得精確數字。

### 備註

- `docs/exp/memo/webpage_image_summarizer/` 的實驗腳本依賴舊版逐頁實作的內部方法（`_download_image`、`_download_failure_reasons` 等），P1c 後不再對應；改為不納入 pyright 檢查（`pyproject.toml`），腳本與結果文件保留作歷史紀錄。
- 原 `_failed_images`（最終失敗清單）保留，並改記第一個引用頁面與下載器回報的錯誤字串（如 `HTTP 404`、`timeout`）。

## P1d：圖片過濾（內容去重、尺寸門檻）

### 自動化

- `scripts/check.sh`：ruff、pyright 通過；`pytest tests/unit` 545 passed。
- 新增測試（`test_augmenter.py`）：
  - 長邊 < `min_size` 不送 VLM、沒有 `caption` 欄位、markdown 不變、統計記 `skipped`；邊界：長邊剛好等於門檻（100×40、40×100）不略過、99×99 與 1×1 略過、`min_size=0` 不過濾；
  - 小圖跨三頁：只下載一次、`skipped` 只計一次（第一個引用頁面），不觸發重試；
  - 內容相同、URL 不同（跨頁）只描述一次並共用描述，花費只計一次，共用者記 `cache_reuse`；
  - 代表圖片 VLM 失敗後重試成功，內容相同者跟著得到描述；代表持續失敗時兩者皆無描述、失敗清單只列代表；
  - 尺寸門檻先於內容去重（內容相同的兩張小圖皆略過）；無法解碼尺寸的圖片不依尺寸過濾。
- **快照差異審查**：
  - 快照 fake 改為回傳真實 PNG（依 URL 雜湊決定尺寸，涵蓋長邊 1／16／99 的小圖、剛好 100 的邊界、4 組內容相同的共用圖片），並以 `UPDATE_SNAPSHOT=1` 更新（9 個檔案：`results.json` 與 8 個 md）。
  - 以腳本（`classify_diff.py`，暫存於 scratchpad，未納入 repo）比對 P1c 基準與新快照：兩者的 `url`／`metadata`／`crawl_info` 與圖片 URL 清單相同；移除描述區塊後的 `enhanced_markdown` 逐頁相同。差異歸類結果：
    - **小圖略過 10 處**：舊有描述（含空描述）、新無 `caption` 欄位，且圖片長邊 < 100px 且下載成功；
    - **共用描述 5 處**：圖片屬於內容相同的群組，新描述等於該群組共用描述（或代表失敗時為空）；
    - markdown 描述區塊的差異共 15 處，逐一對應到上述已歸類的圖片；
    - **未歸類 0 處**；其餘 67 張圖片的輸出不變。
  - 快照測試另斷言兩項過濾皆在快照中被觸發（有小圖被略過、有多個 URL 共用同一段描述）。

### 實跑（ncucsie 真實 VLM，`--run.no-publish`，`runs/20261004_174606/`，輸入為 P0 重爬的 146 頁）

| 項目 | 數量 |
|---|---|
| 不重複圖片 | 170 |
| 下載失敗 | 4（`pdf.gif%20`、`doc.gif%20` 各 404；2 個 `placehold.co` 回傳 svg，格式不符） |
| 小圖略過（長邊 < 100px） | 29 |
| 內容相同、共用描述 | 5 |
| 送 VLM／成功／失敗 | 132／132／0 |
| 整輪重試 | 無（成功率 100%） |

- 耗時 34.9 秒，花費 **$0.149**（132 次 VLM 呼叫）。
- 過濾前（P1c）會送 VLM 的圖片為 170 − 4 = 166 張，P1d 後為 132 張，減少 34 次（約 20%）；若以單次呼叫約 $0.0011 估算，過濾前約 $0.19（推估，未實測）。
- 與計畫的估計不同：計畫預估 VLM 呼叫約 161 → 約 105，是將「小圖 28 張」與「內容相同 28 張」視為彼此獨立相減；實測兩者幾乎重疊（內容相同的主要就是那些圖示本身，小圖先被略過），故實際為 166 → 132。這是估計方法的差異，不是實作缺陷：29 張小圖與 5 張共用描述與計畫調查的數字（小圖 28 張）相符。
- 依賴：`pillow` 由依賴樹成員提升為 `[project].dependencies`（版本不變，`uv.lock` 只更新依賴宣告）。
