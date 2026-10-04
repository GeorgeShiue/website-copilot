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

## P2a：文件骨架（anydoc：docx／doc／odt）

### 自動化

- `scripts/check.sh`：ruff、pyright 通過；`pytest tests/unit` 594 passed。圖片相關的 14 個行為測試與快照**未更動**（逐字一致）。
- 新增 `test_documents.py`（36 個）：
  - 格式判斷：magic bytes 優先於誤導的 Content-Type／副檔名；退回 Content-Disposition > Content-Type > URL 副檔名的優先序；無法判斷回傳 None；Content-Disposition 的 `filename=`（百分比編碼）與 `filename*=`；
  - 收集：Markdown 連結（含圖示圖片的連結文字、title 屬性）、正規化 URL 去重與引用記錄、依副檔名略過未啟用格式（不下載）、無副檔名的下載 API 先收進來、站點樣式只在提供時生效、`allowed_domains`（含子網域）、深度 2 頁面的連結；
  - 標題：通用連結文字判定、最常出現的連結文字、優先序鏈（連結文字 → title 屬性 → 檔名 → heading → URL 檔名）；
  - Augmenter：文件成為獨立 entry（鍵、title、metadata、source_pages、原檔）、doc／odt／docx 皆可解析、格式未啟用不下載、下載後才發現未啟用格式不建 entry 也不算失敗、同內容不同 URL 合併、解析失敗為永久失敗、永久下載錯誤不重試、可恢復失敗重試、**圖片與文件共用一輪重試**、`documents=None` 不處理文件、`images.enabled=false` 不需要 API key 且頁面不變。
  - 其他：`DataManager.publish_markdown` 發布 `files/` 並移除過期檔、沒有文件時清空；`NodePipelineBuilder` 的 `page_title` 取自 `title`、`file_format`／`file_name`、長 `source_pages`（12 頁引用、chunk size 300）在切塊後寫入且排除於 embedding 與 LLM 文字；`run_augmenter` 傳遞文件選項並存／發布原檔；`AugmenterConfig` 的 `documents`／`images.enabled`。
- 解析使用 `tests/fixtures/documents/` 的三個真實小檔（docx／doc／odt），anydoc 在本機執行，不產生費用。

### 實跑（ncucsie，`--module.images.enabled False --run.no-publish`，無 VLM 費用）

輸入為 P0 重爬的 146 頁。

| 項目 | 數量 |
|---|---|
| 收集的不重複文件連結 | 58 |
| 依副檔名略過（pdf 未啟用） | 29 |
| 網域不在 `allowed_domains` | 6 |
| 下載後依內容判斷為 pdf 而略過（`downloadfile`） | 16 |
| 內容相同的 URL 合併 | 9 |
| 解析成功（獨立 entry） | 33（odt 19、doc 9、docx 5） |
| 下載失敗／解析失敗 | 0／0 |

- 全程 1.3 秒；`results.json` 179 筆（146 頁 + 33 文件），`files/` 33 個原檔。
- 標題：33 份皆有可讀標題（如「113研究所新生指導教授確認表」「博士班資格考申請表」）；發現並修正 `**獎學金申請表**` 殘留 Markdown 強調標記。
- RAG 建庫（`run rag-build --run.use-latest-results --run.no-publish`）：977 nodes，建庫約 76 秒。
- **文件檢索問題集**（`tests/integration/test_document_retrieval.py`，`cost`，只查 embedding；以 `DOCUMENT_QUESTIONS_VECTOR_STORE_RUN` 指向 runs/ 的向量庫）：10 題表單類問題全部在 top-10 命中預期文件。

### 備註

- 原檔資料夾放在 run／發布資料夾下與 `results/` **並列**的 `files/`（計畫原文為 `results/files`）：與 aug_webpages 的結構（`results.json` + `results/*.md`）一致，`--run.use-latest-results` 取用的 run 資料夾與 `data/aug_webpages/<site>/` 因此結構相同。
- `source_pages` 的 `title` 為頁面鍵（與頁面的 `page_title` 一致），另附該頁的連結文字 `link_text`；爬取結果沒有保存頁面的人類可讀標題。
- 計畫預估 ncucsie 的文件連結為 91 個；本次爬取（146 頁）共 93 個不重複文件 URL，扣掉網域不符的 6 個與重複，對應上表。

## P2b：PDF 解析（Docling）

### 自動化

- `scripts/check.sh`：ruff、pyright 通過；`pytest tests/unit` 603 passed；免費整合測試 2 passed。
- 新增 `test_pdf_parser.py`（以 fake converter，不載入模型）：佔位符保留、無文字層（空輸出或只有佔位符）視為失敗、轉換錯誤包成解析失敗、converter 延遲建立且只建立一次、6 個執行緒同時呼叫時被鎖序列化（同一時間只有 1 個轉換）、解析器分派（pdf → Docling、odt → anydoc）、PDF 文件流程（entry、標題、原檔、掃描檔記錄為失敗且不重試）。
- `heavy`：`tests/integration/test_pdf_parser_heavy.py` 以真實小 PDF（`tests/fixtures/documents/lecture.pdf`）實際呼叫 Docling，通過（首次含模型載入約 10 秒）。
- 依賴：新增 `docling`，`uv.lock` 新增 39 個套件，**torch 版本不變（2.14.0）**，既有套件只有 `requests` 2.33.1 → 2.34.2；與計畫的實測一致。

### 實跑（ncucsie，`--module.images.enabled False --run.no-publish`）

| 項目 | 數量 |
|---|---|
| 收集的不重複文件連結（扣掉網域不符的 6 個） | 87 |
| 內容相同的 URL 合併 | 15 |
| 解析成功（獨立 entry） | 71（pdf 38、odt 19、doc 9、docx 5） |
| 解析失敗 | 1（掃描版 PDF，`no text layer`，記錄於 Failed Resources 並略過） |
| 下載失敗 | 0 |

- 不重複的 PDF 共 39 份：38 份有輸出、1 份為掃描檔明確記錄略過原因（計畫預估 44 份是以較早的爬取結果估計，本次爬取為 39 份）。
- 耗時 105 秒（含 Docling 載入；GPU 可用，單份約數秒，首份含模型載入與下載約 24 秒）。
- 抽查結構：「碩士班修業辦法」還原為標題（`##`）+ 條列的條文；「論文品質與管考準則」每條成一個條列；「TARA 公告」的條列與表格都保留，表格欄位標題有「群組 - 欄位」前綴（Docling 的多層表頭展平）；PDF 內的圖片以 `<!-- image -->` 佔位（共 80 個，P2c 處理）。
- 模型快取位置：版面／表格模型在 `~/.cache/huggingface/hub`（`models--docling-project--*`）；RapidOCR 模型在 `.venv/lib/python3.13/site-packages/rapidocr/models`（約 62 MB，`uv sync --reinstall` 後需重新下載）。
- RAG 建庫：1271 nodes（P2a 為 977），建庫約 85 秒。
- **文件檢索問題集**擴充 6 題 PDF 題目（修業辦法、論文相似度、博士班畢業辦法、英文版辦法、獎學金一覽表、軟工碩士班），共 16 題，**全部在 top-10 命中**。

## P2c：文件內圖片描述

### 自動化

- `scripts/check.sh`：ruff、pyright 通過；`pytest tests/unit` 620 passed。圖片的快照與 14 個行為測試未更動。
- 新增 `test_document_images.py`（15 個）：
  - anydoc 定位：真實 `.doc`（3 張內嵌圖片）的佔位符落在表格之後、結尾說明之前；未抽圖時沒有佔位符與圖片；沒有內嵌圖片的文件維持原樣；
  - Docling 對位：圖片依佔位符順序編成 PNG、圖片數與佔位符數不一致時不回傳圖片（佔位符移除）、取不到圖片的位置保留順序；
  - 描述插回：佔位符取代為 `> # Image-{n}` 區塊（n 為文件內序號）、小圖／VLM 失敗／格式不支援／取不到的圖片不留佔位符、同一張圖在兩份文件只描述一次、與相同內容的頁面圖片共用描述、VLM 失敗進入共用的整輪重試、`images.enabled=false` 與 `documents.caption_images=false` 時不抽圖也不呼叫 VLM、真實 `.doc` 端到端；
- `heavy`：真實 PDF（報名流程通知，`tests/fixtures/documents/notice_with_images.pdf`）以 Docling 抽出 7 張圖，與 7 個佔位符一一對應，通過。

### 實跑（ncucsie 完整，真實 VLM，`--run.no-publish`，輸入為 P0 重爬的 146 頁）

| 項目 | 數量 |
|---|---|
| 頁面 + 文件 | 217 筆（146 頁 + 71 份文件） |
| 不重複圖片資源 | 248（頁面圖片 170 + 文件內嵌圖片 78） |
| 小圖略過 | 38（頁面 29 + 文件 9） |
| 內容相同、共用描述（頁面圖片） | 5 |
| 下載失敗（頁面圖片）／文件解析失敗 | 4（與 P1d 相同）／1（掃描檔） |
| 送 VLM／成功／失敗 | 201／201／0（頁面 132 + 文件 69） |
| 整輪重試 | 無 |

- 耗時 185.8 秒，花費 **$0.348**（含 P1d 已有的頁面圖片 $0.149）。
- 「115報名與繳費通知單」的 7 張圖（報名流程圖與系統截圖）全部有描述，描述含流程圖上的 OCR 文字與網址；「EMI獎勵系統操作SOP」61 個圖片位置中 56 個有描述（其餘為小圖示）；文件內共 77 個描述區塊，全部文件都沒有殘留 `<!-- image -->`。同一張圖在多份文件中的重複位置只描述一次（69 次 VLM 呼叫對應 77 個描述區塊）。
- RAG 建庫：1643 nodes（P2b 為 1271），約 107 秒。
- **文件檢索問題集**加入 3 題（繳費帳號在哪裡查、三小時後沒顯示已繳費要聯絡哪裡、EMI 系統操作步驟——答案只存在於圖片描述中），共 19 題，**全部在 top-10 命中**。
- P2b 殘留的 80 個 `<!-- image -->` 佔位符現在不是被描述取代，就是被移除。

### 備註

- Docling 以 2 倍解析度裁切圖片，VLM 才看得清截圖中的小字；小圖示（< 100px，如 EMI SOP 的按鈕圖示）依 P1d 的門檻略過。
- 計畫的「甄試通知 7 張截圖」與實測一致（7 張，全部有描述）；「校徽等重複圖只描述一次」由內容雜湊去重實現（資源 URL 為內容 sha1）。
- 全部三個 P2 階段（P2a、P2b、P2c）的最終驗收與 `data/` 的正式發布（獨立資料 commit）尚未執行：本次所有實跑皆為 `--run.no-publish`。
