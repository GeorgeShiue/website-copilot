# Augmentation 重構與讀取網站文件：實作規劃

> 對應 [todo.md](../../todo.md)「功能進度：讀取網站文件」，並一併處理「效能優化」中圖片摘要的兩項（同頁重複下載、跨頁並行上限）。
> 原規劃為在 crawler 與 image summarizer 之間新增「文件階段」；討論後發現文件流程與圖片摘要同構，改為將 image summarizer 擴充為通用的 **Augmenter**（見「動機」）。

## Context

### 調查結果：ncucsie 的文件檔案

以 `data/raw_webpages/ncucsie/results.json`（149 頁，`max_depth: 2`）的頁面連結統計，共 **91 個文件連結**，無 xlsx／pptx：

| 形式 | 數量 | 格式 | 說明 |
|---|---|---|---|
| 直接帶副檔名（`static/file/13/1013/img/...`） | 66 | pdf 33、odt 19、doc 9、docx 5 | 61 個在 `www.csie.ncu.edu.tw`，5 個在校內其他網域（pdc.adm／course／lib） |
| 下載 API（`app/index.php?Action=downloadfile&file=...`） | 25 | pdf 15、doc 6、docx 4 | URL 無副檔名；`file` 參數經兩次 base64 解碼為 `attach/.../xxx.pdf`；回應為 `application/octet-stream`，檔名在 `Content-Disposition` |

- 主要分布：表單下載頁（`p_412-1013-1096`，odt/doc 空白申請表為主）、修業／選課／畢業辦法頁（`p_412-1013-1154/1155/1157/2099`，pdf 為主，資訊價值最高）、公告頁（`p_406-*`，獎學金、TA、招生公告）。
- 同一文件可能被多頁引用（例：`410/614882835.pdf` 被 12 頁引用）。

### 現況：爬蟲未涵蓋文件

`WebsiteCrawler` 以 crawl4ai `BFSDeepCrawlStrategy` 走訪，FilterChain 只有 `URLPatternFilter` + `DomainFilter`，不分辨文件。91 個文件連結的去向：

| 去向 | 數量 | 原因 |
|---|---|---|
| 被訪問但丟棄 | 45 | Chromium 導航觸發下載，`Page.goto: Download is starting` → `markdown is None` → 記為 `error: no markdown`（佔 `error_no_markdown: 47` 中的 45 筆） |
| 未被訪問 | 41 | 只出現在深度 2 頁面，受 `max_depth` 限制 |
| 被網域過濾 | 5 | 不在 `allowed_domains` |

### 不採用 crawl4ai 內建模組的原因

crawl4ai 0.9.2 實測：

- **瀏覽器下載**（`BrowserConfig(accept_downloads=True)`）：檔案會落盤，但結果一律 `success=False`（只容忍 `net::ERR_ABORTED`，Chromium 丟的是 `Download is starting`）；`downloaded_files` 因非同步存檔與共用清單而掛到錯誤的結果；檔名只取 basename 會互相覆蓋。無法可靠對應「URL → 檔案」。
- **PDF 處理器**（`PDFCrawlerStrategy` + `PDFContentScrapingStrategy`）：文字可正確抽出，但佔位 HTML（33 bytes）被反爬蟲檢查誤判 `success=False`；只支援 PDF（odt 直接 `invalid pdf header`）；下載到暫存檔後刪除，不保留原檔；需額外安裝 `pypdf`；無法與 HTML 深度爬取混用。
- `DocumentExtractionStrategy`（PR #1896）尚未合併，且只提供 hook，不含解析器。
- 官方維護者對「深度爬取遇到 PDF」的建議（Discussion #1190）即為先爬 HTML、收集文件 URL、再另行處理，與本規劃相同。

### 下載工具選型：自寫共用下載器（httpx），不採用現成工具

下載階段的輸入是「已收集的 URL 清單」，不需要第二套爬蟲，評估重點是能否單純作為下載器：

| 工具 | 授權 | 評估 |
|---|---|---|
| Crawlee `FileDownloadCrawler` | Apache-2.0 | 可用（穩定版 1.10.3），但只是薄包裝（158 行）：提供重試、並行控制、請求佇列去重、`user_data`、`failed_request_handler`；存檔、命名、格式判斷仍須自寫。實測問題見下 |
| Scrapy `FilesPipeline` | BSD | 需改寫為 Scrapy 專案；以 URL SHA-1 + URL 副檔名命名（`downloadfile` 無副檔名）；基於 Twisted，與 asyncio／crawl4ai 混用麻煩 |
| Firecrawl／CRW | AGPL-3.0 | 完整爬蟲服務（需另架），等同取代 crawl4ai，授權亦不合適 |
| doc_crawler.py、wget、HTTrack | — | 自帶遞迴爬取或為 CLI，無法取得結構化的「URL → 檔案」與錯誤原因 |

Crawlee `FileDownloadCrawler` 實測：

- ncucsie 的 `downloadfile` 連結在預設設定下回 **404**（curl 為 200）：預設 HTTP client 為 `ImpitHttpClient(browser='firefox')` 瀏覽器偽裝，改 `browser=None` 才正常；偽裝策略需依站點調整。
- 同一 process 內第二次 `run()` 會**靜默略過**已處理過的 URL：即使每個實例各給 `MemoryStorageClient`，預設 request queue 仍為 process 全域共用；逐頁執行或整輪重試的呼叫端須每次開獨立命名的 `RequestQueue`。
- 預設在 cwd 建立 `./storage/`，需改用 `MemoryStorageClient` 以免與 runs/、data/ 衝突；新增約 27 個套件。
- ncucsie 169 張圖片：urllib（8 執行緒）5.6s 與 Crawlee（並行 8）6.1s 結果完全一致（161 成功、6 個 404、2 個 svg），無效能或成功率差異。

結論：現成工具能省下的只有「並行 + 重試 + 逾時」一層，在本專案規模下以 httpx（已在依賴樹中：crawl4ai、langchain 等皆依賴）自寫即可；格式判斷、存檔與來源對應無論用哪個工具都須自寫。若日後遇到需要自動調速、session 輪替或 proxy 的站點，再將共用下載器的實作換成 Crawlee（介面不變）。

### 解析工具選型：PDF 用 Docling，docx／doc／odt 用 anydoc

以 ncucsie 實際文件實測（7 份 pdf：表格公告、徵才公告附表、英文辦法、含 36 張圖的甄試通知、錄取通知、純掃描檔、62 頁混合檔；2 份 docx 申請表；odt、doc 各 1 份）：

| | MarkItDown | anydoc | pdf-inspector | Docling |
|---|---|---|---|---|
| PDF 內文結構 | 保留原始換行，無標題層級 | 有標題；條列常併成一行；TARA 第 1 頁內文誤判為表格 | 有標題與粗體；條列偶爾併行、URL 偶爾斷開 | **最好**：條列還原為項目、標題分層 |
| PDF 表格 | 欄位錯位 | 好 | 好 | 大多好；複雜表單整張塌成一格 |
| 掃描頁 | 無文字、不報錯 | 任一頁需 OCR 即整份 `NeedsOcrError` | 回報 `pdf_type` 與需 OCR 頁碼，其餘照常 | 整頁當成圖片，OCR 未啟動 |
| PDF 內嵌圖片 | ❌ | ❌ | ❌ | ✅ 版面模型只挑有意義的圖並保留位置 |
| docx | 可用 | **最好** | ❌ | 可用 |
| odt／doc | ❌ | ✅ 兩者皆可，不需 LibreOffice | ❌ | odt 需 `odfdo`、doc 需 LibreOffice |
| 速度 | 0.04–1.1 s | 0.01–1 s | 0.02–0.3 s | GPU 0.5–11 s（首次載入模型 96 s） |
| 依賴 | 輕 | 很輕（Rust） | 很輕（Rust） | 很重（torch、transformers、opencv、rapidocr、模型下載） |
| 授權 | MIT | MIT | MIT | MIT |

- 中文四者皆正確（anydoc 有一處「．．．」被轉成「認認認認」）。
- 結論：PDF 以 Docling 取得最佳結構，並滿足 #7「文件內圖片」需要的「有意義的圖片 + 位置」；docx／doc／odt 以 anydoc 單一套件涵蓋。輕量替代方案（pdf-inspector + pypdf 抽圖 + 規則過濾）圖片只能插在頁尾、規則難以濾乾淨，未採用。

### 動機：圖片與文件流程同構

| 步驟 | 圖片（現行 `ImageSummarizer`） | 文件（新增） |
|---|---|---|
| 1. 篩選 | 頁面 `images` 欄位或 markdown 圖片語法；副檔名黑名單（svg…）先略過 | 頁面連結；副檔名 + 站點下載 API 樣式；`allowed_domains` |
| 2. 下載 | `ThreadPoolExecutor` + `urlopen`，**逐頁**進行 | 共用下載器 |
| 3. 解析 | VLM 產生描述（付費、慢、會被限流） | pdf／docx／doc／odt 本地轉 Markdown（PDF 用 Docling 版面模型） |
| 4. 回寫 | **內嵌回原頁**：`enhanced_markdown` 以描述取代圖片、`images[].caption` | **獨立文件**：`results.json` 新增一筆、自己的 md，記錄引用頁面 |

步驟 1～3 可統一；步驟 4 依資源類型不同。未來的 xlsx／pptx、OCR 也只是新增解析策略或回寫方式。

## 目標

1. 將 `ImageSummarizer` 重構為通用的 `Augmenter`：篩選 → 下載 → 解析 → 回寫，資源類型以策略擴充。
2. 網站連結的文件（首版 pdf／docx／doc／odt）能被下載、保存原檔、轉為 Markdown，並進入向量庫供 Agent 檢索；保留來源資訊（文件 URL、引用頁面與連結文字、格式、檔名）。
3. 圖片處理改為跨頁去重、整批下載與摘要（解決 todo 效能優化兩項），既有圖片摘要的輸出不變。
4. BFS 不再浪費導航在文件 URL 上；不影響既有網頁爬取結果。

## 整體架構

prepare 維持三個階段：**crawler → augmenter → rag**（原 image summarizer 階段改名擴充，不新增階段）。

```
crawl_results（各頁 fit_markdown／images／links）
        │
        ▼
① 篩選  Collector（每種資源一個）→ list[Asset]，跨頁去重
        │   Asset：url、kind（image／document）、refs（引用頁面 + alt／連結文字）
        ▼
② 下載  HttpDownloader（共用，所有頁、所有類型共用並行上限）
        ▼
③ 解析  Processor（依 kind／實際格式選擇）
        │   pdf（Docling）／docx・doc・odt（anydoc）→ Markdown，並抽出內嵌圖片成為新的 image asset
        │   image（頁面圖片 + 文件內嵌圖片）→ VLM 描述
        ▼
④ 回寫  依 kind：頁面圖片描述內嵌回頁面 markdown；文件成為獨立 entry（其內嵌圖片描述插回文件 markdown）
        ▼
enhanced crawl_results → publish 到 data/aug_webpages → RAG 建庫
```

暫定模組佈局：

```
ingestion/augmentation/
  augmenter.py          Augmenter：串起 ①～④，負責快取、整輪退避重試、統計與 log
  assets.py             Asset 資料結構
  collectors.py         ImageCollector／DocumentCollector
  processors/
    image_captioner.py  VLM 描述（現行 ImageSummarizer 的 caption 邏輯）
    pdf_parser.py（Docling，P2b）、office_parser.py（anydoc，P2a）
utils/http_downloader.py 共用下載器
```

### 元件介面

```python
@dataclass
class AssetRef:            # 一次引用
    page_key: str          # 引用頁面的鍵
    text: str              # alt 文字或連結文字
    title: str             # 連結的 title 屬性（圖片無則為空）

@dataclass
class Asset:
    url: str               # 正規化 URL，即去重鍵
    kind: Literal["image", "document"]
    refs: list[AssetRef]   # 依頁面順序，第一筆即「第一個引用頁面」
```

- **Collector**：`collect(crawl_results, site) -> list[Asset]`，每種資源一個，跨頁去重。
- **下載**：圖片與文件**分兩次**呼叫共用下載器（進度條與統計各自獨立），`download` 設定共用。
- **解析**：介面為「`Asset` + `DownloadResult` → 解析結果」；`ImageCaptioner` 為 async（VLM，維持現狀），文件解析器為同步 CPU 工作，以執行緒池執行。
- **回寫**：圖片寫回 `enhanced_markdown` 與 `images[].caption`；文件新增 entry 並寫出原檔。
- **開關**：`images.enabled`、`documents.enabled`，可只跑文件（不產生 VLM 費用，方便開發 P2 各階段）。
- **快取**：現行 `_image_cache`（下載與解析分別記錄成功／失敗）一般化為以 asset URL 為鍵的快取。
- **統計**：圖片維持逐頁統計表（`PageStats`，由 `Asset.refs` 反推每頁數字）；文件另一張摘要表（收集、略過（格式未啟用）、下載失敗、解析失敗、成功）；失敗清單合併為一份並加上類型欄。

### 整輪退避重試（圖片與文件共用）

- 沿用現行機制（成功率 < `success_threshold` 時懷疑被封鎖或限流，依指數退避等待後重做失敗項），在 Augmenter 層運作，與下載器的單一請求重試疊加。
- **圖片與文件共用一套**：一組 `retry` 設定，成功率合併兩種資源計算，重試時兩種資源的可恢復失敗一起重做。
- **只計可恢復的失敗**：
  - 可恢復（計入成功率、進入重試名單）：逾時、連線錯誤、5xx、429、403、VLM 呼叫失敗。
  - 永久（直接列為最終失敗，不計入成功率分母）：404、410 等其他 4xx、格式不符（圖片非 png／jpeg／gif／webp、文件不在 `documents.formats`）、文件解析失敗。
  - 成功率 = 成功 ÷（成功 + 可恢復失敗）。
  - 避免少數壞連結（如 ncucsie 的 `pdf.gif%20`、文件的 404）把成功率拉低而白等多輪退避。

### 共用下載器

圖片與文件共用；只負責「URL 清單 → HTTP 回應」，與格式無關（暫定 `utils/http_downloader.py`）。

```python
@dataclass(frozen=True)
class DownloadResult:
    url: str                    # 請求的 URL
    final_url: str              # 跟隨重新導向後的 URL
    status_code: int | None     # 未取得回應（逾時、連線失敗）時為 None
    headers: dict[str, str]     # 回應標頭（Content-Type、Content-Disposition…）
    content: bytes | None       # 失敗時為 None
    error: str | None           # 失敗原因，如 "HTTP 404"、"timeout"、"exceeds max_bytes"
    attempts: int               # 實際嘗試次數

    @property
    def ok(self) -> bool: ...

class HttpDownloader:
    def __init__(self, *, max_concurrency: int, timeout: float, max_retries: int,
                 max_bytes: int | None, headers: dict[str, str] | None = None) -> None: ...
    async def adownload(self, urls: Iterable[str]) -> dict[str, DownloadResult]: ...
    def download(self, urls: Iterable[str]) -> dict[str, DownloadResult]: ...  # asyncio.run 包裝，供同步呼叫端
```

- **去重**：輸入 URL 先去重（保留順序），同一 URL 只請求一次。
- **並行**：單一 `httpx.AsyncClient` + `asyncio.Semaphore(max_concurrency)`，一次呼叫內所有 URL 共用上限。
- **重試**：只對逾時、連線錯誤、5xx、429 重試（短間隔指數退避）；4xx 直接失敗。屬於單一請求層級，與 Augmenter「整輪退避重試」（對付封鎖）是不同層次，可疊加。
- **大小上限**：串流讀取，超過 `max_bytes` 中止並回報失敗，避免誤抓大檔吃光記憶體。
- **標頭**：預設帶與現行圖片下載相同的 Chrome UA；不做瀏覽器指紋偽裝（Crawlee 實測在 ncucsie 反而導致 404）。
- **不負責**：格式判斷、存檔、log 呈現（失敗原因以 `error` 回傳，由呼叫端彙整），以保持通用。
- **依賴**：httpx 目前只在 dev group，需移到 `[project].dependencies`（版本已由 crawl4ai 等鎖定，不新增套件）。
- **進度**：可選的 callback（每完成一筆呼叫一次），供呼叫端接 `TaskCountProgress`。

## 實作階段

拆成 8 個階段，每個階段只有一種驗收標準；在同一個功能分支上依序實作，**每個階段一個 commit**（commit 前完成「驗證機制」的共通驗證與該階段的獨特驗證，結果記入 [verification.md](verification.md)）。全部完成後另以一個資料 commit 正式發布 `data/`（見「驗證機制 › 正式發布」）。

| 階段 | 內容 | 驗收 | 依賴 |
|---|---|---|---|
| P0 | 爬蟲排除文件 URL | 頁面集合不變；`error_no_markdown` 47 → 約 2 | — |
| P1a | 基準快照測試 + 共用下載器（純新增） | 快照測試在現行程式碼通過；下載器單元測試 | — |
| P1b | 改名 augmenter、config 分段（語意不變） | 現有測試 + 快照測試**逐字一致** | P1a |
| P1c | Augmenter 架構重構（整批、下載器、統計／重試語意、依 URL 對位） | 移植與新增的單元測試 + 快照測試**逐字一致** | P1a、P1b |
| P1d | 圖片過濾（內容去重、尺寸門檻） | 新測試；快照只出現預期差異（審查後更新快照） | P1c |
| P2a | 文件骨架：收集、格式判斷、去重、原檔、標題、回寫、發布；**只用 anydoc（docx／doc／odt）** | ncucsie 文件成為獨立 entry，Agent 可查到表單類文件 | P0、P1c |
| P2b | PDF 解析（Docling，只抽文字、圖片留佔位符） | ncucsie 44 份 PDF 皆有輸出；修業辦法類問題可回答 | P2a |
| P2c | 文件內圖片描述 | 甄試通知 7 張截圖有描述；過濾與重試生效 | P2b、P1d |

拆分理由：

- **驗收標準不混用**：「逐字一致」（P1b、P1c）與「只有預期差異」（P1d）分開，快照比對結果可直接下結論。
- **重構在新檔名上進行**：改名先在 P1b 完成，P1c 的 diff 只有邏輯變動（改名與重寫混在一起時 git 會視為整檔刪除 + 新增）。
- **高風險依賴隔離**：Docling（重依賴、模型下載、GPU）單獨在 P2b；P2a 先以輕量的 anydoc 驗證收集、存檔、發布、RAG metadata 整條流程。
- **無依賴的先做**：P0、P1a 可先完成，P0 完成後 ncucsie 的爬取 log 即乾淨。

### P0：爬蟲排除文件 URL

1. **文件規則**（爬蟲與 P2a 的 Collector 共用）：
   - 通用副檔名清單（pdf、doc、docx、odt、xls、xlsx、ppt、pptx…）為程式常數。
   - 站點專屬樣式放站點設定：`configs/sites/ncucsie.yml` 新增 `documents.url_patterns: ["*Action=downloadfile*"]`（`SiteConfig` 新增對應欄位，預設空）。
   - 「要解析哪些格式」為 augmenter 設定 `documents.formats`（首版 `[pdf, docx, doc, odt]`）。
2. **爬蟲調整**：FilterChain 加入 `URLPatternFilter(patterns=[文件規則], reverse=True)`，排除所有文件型 URL（含不解析的格式，瀏覽器本就無法開啟），BFS 不再導航到文件 URL；`_filter_crawl_results` 對 `success=False` 記錄 `error_message`，不再誤記為 `no markdown`。
3. **驗收**：ncucsie 重爬，頁面集合不變（網站本身變動除外）、log 中不再出現文件 URL 的導航；`error_no_markdown` 由 47 降至約 2（剩餘為非文件的失敗）；`success=False` 的頁面記錄實際錯誤訊息。

### P1a：基準快照測試 + 共用下載器

純新增，不改變任何現有行為。

1. **基準快照測試**（必須在 P1b 前、以現行程式碼建立）：
   - 輸入：nculab 真實爬取結果（47 頁、74 個圖片引用；複製為測試 fixture）。
   - 下載與 VLM 以確定性 fake 取代（沿用 `test_image_summarizer.py` 的作法：圖片內容 = URL、caption = `caption of <url>`），不連網、不產生費用。
   - 以現行 `ImageSummarizer` 產生 `results.json` 與 `results/*.md` 存為基準；測試斷言輸出與基準逐字一致。
   - 原因：VLM 輸出不確定，「重構前後各實跑一次再比對」無法證明一致；真實 VLM 只在 P1c 實跑一次確認流程可運作，不比對內容。
2. **共用下載器**：新增 `utils/http_downloader.py`（規格見「共用下載器」）與單元測試（去重、並行上限、重試條件、`max_bytes`、錯誤訊息）；httpx 移到 `[project].dependencies`。此階段尚無呼叫端。

### P1b：改名與 config 分段

只改名稱與設定結構，行為不變。

1. **改名**：

   | 原名 | 新名 |
   |---|---|
   | `ingestion/augmentation/image_summarizer.py`、`ImageSummarizer` | `ingestion/augmentation/augmenter.py`、`Augmenter` |
   | `config/image_summarizer_config.py`、`ImageSummarizerConfig` | `config/augmenter_config.py`、`AugmenterConfig` |
   | `configs/image_summarizer/` | `configs/augmenter/` |
   | `run_image_summarizer`、`ImageSummarizerRunConfig` | `run_augmenter`、`AugmenterRunConfig` |
   | CLI `run image-summarizer` | `run augmenter` |
   | runs/ 模組資料夾 `image_summarizer` | `augmenter`（`retrieval/factory.py` 找最新結果處同步修改） |
   | `RAGBuildRunConfig.aug_webpages_data_use_latest_results`、CLI `--run.aug-webpages-data-use-latest-results`、`build_target()` 同名參數 | `use_latest_results`、`--run.use-latest-results` |

   既有 `runs/<ts>/image_summarizer/` 紀錄**不相容、不遷移**（舊紀錄的 `module_config.yml` 為舊 config 結構，本就無法原樣重現）。唯一受影響的是手動執行 `run rag-build --run.use-latest-results`：改名後須先執行一次 `run augmenter`，否則 `FileNotFoundError`。`prepare --run.no-publish` 同次執行會先產生 augmenter 紀錄，不受影響。已發布的 `data/vector_db/*/meta/run_config.yml` 保留舊欄位名（紀錄性質，不回讀）。

   另需同步：`log_helper.py` 的 logger 名稱、`prompts.py` 註解、`README.md`、`configs/README.md`、`docs/code/runs/{cli,config,workflow}.md`。`data/aug_webpages` 不改名。
2. **Config 分段**：舊欄位搬入新段落，**語意不變**（`download.max_concurrency` 仍為每頁各自計算，P1c 才改為跨頁共用）：

   | 舊欄位 | 新欄位 |
   |---|---|
   | `init.download_timeout` | `download.timeout` |
   | `init.download_max_workers` | `download.max_concurrency` |
   | `init.success_threshold` | `retry.success_threshold` |
   | `init.max_retries` | `retry.max_retries` |
   | `summarize.model`／`prompt`／`image_source` | `images.model`／`prompt`／`source` |
   | `summarize.summary_max_workers` | `images.max_concurrency` |
   | `litellm_kwargs` | `litellm_kwargs` |

   `run_name_fields` 預設由 `summarize.model` 改為 `images.model`。
3. **驗收**：現有單元測試（測試檔隨之改名為 `test_augmenter.py`）與快照測試全部通過、輸出逐字一致；`test_pipeline_prepare.py`、`test_rag_tools.py` 的參數改名。

### P1c：Augmenter 架構重構

輸出不變（快照逐字一致），以下行為**有意變更**（皆不影響落盤檔案）：

| 項目 | 現行（逐頁） | 重構後（整批） |
|---|---|---|
| 統計單位 | 每次出現計一次：下載失敗不視為快取，後續頁面重新下載並再計一次失敗；同頁重複 URL 各下載一次 | 每張不重複資源計一次；成功／失敗記在第一個引用頁面，其餘頁面記 `cache_reuse` |
| 重試判斷 | 成功率以出現次數計算 | 成功率以不重複資源計算 |
| log | 每頁標題 + 下載／摘要兩條進度條；VLM 呼叫依頁面順序 | 整站兩條進度條；VLM 呼叫跨頁交錯；逐頁統計表保留 |
| 失敗清單的頁面 | 最後一個失敗的頁面 | 第一個引用頁面 |
| 重試計算的失敗類型 | 所有失敗（含 404、格式不符） | 只計可恢復的失敗（逾時、連線錯誤、5xx、429、403、VLM 失敗）；404 等永久錯誤直接列為最終失敗 |
| 描述對位 | 依「過濾後的 URL 清單」順序對位 markdown 中的**所有**圖片：被略過的圖片（svg 等）若排在其他圖片前面，後續描述會插錯位置（bug；ncucsie／nculab 現有資料未觸發） | 依每張 markdown 圖片自己的 URL 查描述；`Image-{n}` 編號為頁內圖片序號（現有資料輸出不變） |

ncucsie 模擬（假設 VLM 全成功）：現行下載 206 次、success 173／failure 33、成功率 **84.0%**（`success_threshold` 0.8，只剩 4 個百分點；33 次失敗中 25 次來自 `pdf.gif%20`（15 頁）與 `doc.gif%20`（10 頁）的重複計數）；整批 + 去重為下載 169 次、161／8、**95.3%**。現行計算方式容易把少數壞圖誤判為封鎖而觸發 30 秒以上的退避，屬於 bug，順勢修正。

1. **元件**：`Asset`、`ImageCollector`、`ImageCaptioner`、圖片回寫（介面見「元件介面」）；`ImageSummarizer` 的邏輯搬入對應元件：
   - 篩選：`_retrieve_crawl_result_content`（`image_source`、副檔名黑名單）→ `ImageCollector`。
   - 下載：`_download_images`／`_download_image` → `HttpDownloader`；格式白名單與 base64 轉換留在圖片處理。
   - 解析：`_generate_image_captions`／`_agenerate_image_caption*` → `ImageCaptioner`。
   - 回寫：`_enhance_markdown` 與 `images[].caption` → 圖片回寫（依 URL 對位）。
   - 處理順序由「逐頁：下載 → 摘要」改為「全部收集 → 整批下載 → 整批摘要」。
2. **Config**：`download` 新增 `max_retries`、`max_bytes`（下載器參數）；`download.max_concurrency`、`images.max_concurrency` 改為跨頁共用。
3. **驗收**：
   - 14 個行為測試移植後斷言不變（快取、下載失敗不送 VLM、格式白名單、黑名單、重試只重做失敗項、重試上限、markdown 插入、統計）；fake 對象由 `urlopen` 改為 `HttpDownloader`。
   - 「每頁各自計算」的並行測試改為斷言跨頁共用上限。
   - 新增：同頁重複圖片 URL 只下載一次；失敗資源跨多頁出現時只下載一次、只計一次失敗；成功率以不重複資源計算。
   - 新增：404／格式不符不觸發重試、不進入重試名單；逾時／5xx／VLM 失敗會觸發。
   - 新增：被略過的圖片（svg 等）排在前面時，後續描述仍插在正確位置。
   - 快照測試逐字一致；以 nculab 實跑一次真實 VLM，確認流程正常完成。

### P1d：圖片過濾

以下為**有意的輸出變更**：

| 項目 | 現行（逐頁） | 重構後（整批） |
|---|---|---|
| **輸出變更**：尺寸門檻 | 所有支援格式的圖片都送 VLM | 長邊小於 `images.min_size`（預設 100px）的圖片不送 VLM、不產生描述（比照現行略過的 svg） |
| **輸出變更**：內容去重 | 以 URL 去重 | 下載後再以內容 sha1 去重，內容相同的圖片只描述一次、共用同一段描述 |

ncucsie 網頁圖片（161 張可解碼）：長邊 < 100px 有 28 張，全為圖示、表情符號與 1×1 透明 gif；若改用「任一邊 < 100px」會多排除 2 張有意義的縮圖（實驗室照片 100×71、人物照 100×87），故採長邊規則。按內容去重後為 133 張（28 張為同一張圖的不同 URL），可少 28 次 VLM 呼叫。

1. **過濾**：下載後、送 VLM 前，依內容 sha1 去重並套用尺寸門檻（需解碼圖片尺寸，Pillow 已在依賴樹中）；設計為所有圖片共用（P2c 的文件內圖片沿用）。
2. **Config**：`images.min_size: 100`（長邊小於此值的圖片不送 VLM）。
3. **驗收**：
   - 新增測試：長邊 < `min_size` 的圖片不送 VLM、不產生描述；內容相同、URL 不同的圖片只描述一次並共用描述。
   - 快照測試：fake 下載改為依 fixture 產生指定尺寸的圖片，使門檻與去重可在快照中觸發；差異只能來自上述兩項，逐項審查後更新快照。

### P2a：文件骨架（anydoc：docx／doc／odt）

建立完整的文件流程，PDF 暫不解析（`documents.formats` 先不含 pdf）。

1. **DocumentCollector**：
   - 來源：所有已爬頁面（含深度 2）的連結，不受 `max_depth` 限制。
   - 規則：上述文件規則；網域沿用 `allowed_domains`。
   - URL 副檔名可判斷且不在 `documents.formats` 的（如 P2a 階段的 `.pdf`、或 xls 等未啟用格式）不下載，記入統計（略過數）與 log。
   - 去重鍵：正規化後的文件 URL；`refs` 記錄所有引用頁面與連結文字（ncucsie 檔名多為數字，連結文字是標題候選）。
2. **格式判斷**：檔頭 magic bytes > `Content-Disposition` 檔名 > `Content-Type` > URL 副檔名（`downloadfile` 回 `application/octet-stream`，必須靠前兩者）。下載後才判斷出不在 `documents.formats` 的（如 P2a 階段 `downloadfile` 下載後才發現是 pdf），不存檔、不建 entry，同樣記入統計與 log。
3. **鍵與保存原檔**：
   - 文件 entry 的鍵（即 md 檔名）為 `doc_` + 正規化文件 URL 的 sha1 前 12 碼（如 `doc_3f9a1c2e7b4d`）：穩定、不撞名、與頁面鍵可區分。頁面鍵規則 `_resolve_dedup_key` 會丟棄 query，25 個 `downloadfile` 連結都會變成 `app_index.php`，故不沿用。
   - 原檔存為 `results/files/<key>.<ext>`（runs/），publish 時隨 aug_webpages 一起發布到 `data/aug_webpages/{site_id}/files/`：原檔與解析結果同一發布單位、同一版本，不重新下載即可重新解析。`DataManager` 的發布需同步 `files/`（含移除過期檔案，比照現行 md 的處理）。
   - 記錄原始檔名、大小、Content-Type、下載時間。
   - **內容去重**：同一檔案可能有多個 URL（例：TARA 公告同時以 `downloadfile` 與 `static/file` 連結，內容相同）。下載後以內容 sha1 再去重一次，同內容只建一筆 entry（鍵取第一個 URL），`refs`／`source_pages` 合併所有 URL 的引用。
4. **解析（anydoc）**：docx／doc／odt 以 anydoc `to_document()` 取得 blocks 再轉 Markdown（內嵌圖片暫不處理，P2c 再接）；空白表單不特別處理，照常解析（欄位名稱有時也能回答「申請要填什麼」）。新增依賴 `firecrawl-anydoc`。
5. **標題**（規則產生，不用 LLM）：
   1. 連結文字：排除通用字（「按我取得詳細資訊」「附件」「下載」…）後，取各引用處最常出現者；
   2. 連結的 `title` 屬性；
   3. 非純數字的 `Content-Disposition` 檔名或 URL 檔名；
   4. 內文第一個 heading；
   5. URL 檔名。

   PDF 內嵌 metadata 標題不採用（實測 TARA 公告 PDF 的內嵌標題為多年前的舊範本「國立中央大學八十七學年度第一學期研究生獎、助學金申請學生名冊」）。ncucsie 站內 86 個文件連結：83 個有可用連結文字，其餘 3 個由 `title` 屬性補足。
6. **回寫**：文件成為 `results.json` 的獨立 entry 與 `results/<key>.md`，欄位與頁面 entry 對齊（`url`、`enhanced_markdown`、`images: []`、`metadata`），另加：
   - `title`：上述規則產生的標題；`NodePipelineBuilder._build_file_metadata` 改為優先使用 entry 的 `title` 作為 `page_title`（否則 Agent 與 embedding 只看到 `doc_3f9a...`）。
   - `metadata.page_type: "document"`、`page_url` 為文件 URL。
   - 文件專屬 metadata：`file_format`、`file_name`（原始檔名）、`source_pages`（引用頁面的 URL 與標題）。`source_pages` 可能很長（一份文件最多被 12 頁引用），排除於 embedding 文字之外（`excluded_embed_metadata_keys`），並注意 llama-index 的 metadata 長度不可超過 chunk size。
   - 不設定 `published_date`，交給現有 `MarkdownDateExtractor` 從內文推斷。
   - 頁面的 markdown 不變動（不加註、不內嵌文件內容）。
   - `NodePipelineBuilder` 沿用現有切塊流程。
7. **Config**：augmenter 新增 `documents.enabled`、`documents.formats`（P2a 預設 `[docx, doc, odt]`）；新增 `images.enabled`（可只跑文件，不產生 VLM 費用）。
8. **驗收**：單元測試（規則比對、格式判斷優先序、URL 與內容去重、鍵產生、標題優先序、未啟用格式略過、`files/` 發布與過期清除、`page_title` 取自 `title`）；ncucsie 實跑（`images.enabled: false`），文件 entry 與原檔正確發布，RAG 建庫後 Agent 可查到表單類文件並回傳文件 URL。

### P2b：PDF 解析（Docling）

1. **解析**：
   - PDF → Docling（`DocumentConverter`）：版面模型還原標題層級與條列；圖片先保留 `<!-- image -->` 佔位符（P2c 再描述）。
   - 掃描版 PDF（無文字層）首版抽不到文字：記錄並略過，OCR 另案（Docling 預設把整頁掃描當成一張圖，OCR 未啟動）。
   - Docling 的 OCR 維持預設開啟：混合檔可多抽出部分文字（62 頁混合檔多約 400 字）。
2. **依賴**：新增 `docling`；實測與專案現有依賴可共同解析，torch 版本不變，新增 40 個套件（含 anydoc），既有套件只有 `requests` 2.33.1 → 2.34.2。首次執行會下載版面／表格模型（需快取位置與網路），有 GPU 時使用 GPU。
3. **Config**：`documents.formats` 預設改為 `[pdf, docx, doc, odt]`。
4. **驗收**：ncucsie 44 份 PDF 皆有輸出或明確記錄略過原因（掃描檔）；抽查表格公告與修業辦法的 Markdown 結構；Agent 可回答修業辦法類問題。

### P2c：文件內圖片描述

1. **抽取**：
   - PDF：Docling 開啟 `generate_picture_images`，以版面模型挑選圖片並對應佔位符位置（甄試通知 PDF：pypdf 直接抽出 36 張，含整頁校徽底圖、全白遮罩、重複圖；Docling 只辨識出 7 張有意義的系統截圖）。
   - docx／doc／odt：anydoc 的 assets，位置取自 blocks 中的圖片引用。
   - 每張成為 `kind="image"` 的 asset（不需下載），鍵為圖片內容 sha1（同一個 logo 在多份文件中只描述一次）。
2. **描述與回寫**：與頁面圖片一起送 `ImageCaptioner`，套用 P1d 的過濾，描述以與頁面圖片相同的格式插回文件 markdown；VLM 失敗進入共用的整輪重試。流程順序為：收集 → 下載（頁面圖片、文件）→ 解析文件（產生內嵌圖片 asset）→ 圖片描述（頁面圖片 + 文件圖片）→ 回寫。不設單份文件圖片數上限。
3. **Config**：`documents.caption_images`（預設 true）。
4. **驗收**：單元測試（文件圖片插回位置、與頁面圖片共用快取與過濾、VLM 失敗進入重試）；ncucsie 實跑，甄試通知的系統截圖有描述，校徽等重複圖只描述一次。

## 驗證機制

### 前提

- `data/` 受版本控制（如 `data/aug_webpages/ncucsie/results.json`），驗證時的實跑若 publish 會改動 commit 內容；`runs/` 不受版本控制。
- RAG 建庫與查詢的 embedding 為 OpenAI `text-embedding-3-small`（非本地），建庫與檢索皆有少量費用。
- 現有工具：`scripts/check.sh`（ruff、pyright、`pytest tests/unit`、widget 同步）、prek hooks（commit 時執行）、`tests/integration`（各 run function 只驗證不拋例外，花錢者標記 `cost`）、`run rag-query`（可指定 `vector_store_run` 查詢 runs/ 中的向量庫）。

### 共通驗證（每個階段 commit 前）

| # | 項目 | 做法 |
|---|---|---|
| C1 | 靜態檢查與單元測試 | `scripts/check.sh` 全過；P1a 起基準快照測試位於 unit tests，每階段自動執行 |
| C2 | 免費整合測試 | `pytest tests/integration -m "not cost and not network and not heavy"`（agent build、serve） |
| C3 | 新行為皆有單元測試 | 每個新行為至少一個測試；下載與 VLM 以 fake 取代，不連網、不花錢 |
| C4 | 實跑不 publish | 一律 `--run.no-publish`（只寫 runs/）；需建庫時 `--run.use-latest-results`，查詢以 `vector_store_run` 指定 runs/ 的向量庫；`data/` 不被驗證改動 |
| C5 | 文件同步 | 名稱、CLI、config、資料格式變更時同步 `README.md`、`configs/README.md`、`docs/code/runs/*.md` |
| C6 | 驗證紀錄 | 於 [verification.md](verification.md) 該階段一節記錄：執行的驗證、數字結果、實際費用、發現的問題與處置；commit message 只寫摘要 |
| C7 | commit 範圍 | 一階段一 commit，只含該階段的程式碼、測試、文件與 verification.md；不含 `data/` 與 runs/ 產物 |

### 測試分類（pytest marker）

| marker | 意義 | 位置 | check.sh |
|---|---|---|---|
| （無） | 不連網、不花錢、快速 | `tests/unit` | 執行 |
| `network`（新增） | 連真實網站，不花錢 | `tests/integration` | 不執行 |
| `heavy`（新增） | 載入 Docling 模型，慢 | `tests/integration` | 不執行 |
| `cost`（既有） | 呼叫 LLM／VLM／embedding，產生費用 | `tests/integration` | 不執行 |

### 獨特驗證

| 階段 | 自動化 | 實跑（費用） |
|---|---|---|
| P0 | 文件 URL 規則：副檔名大小寫、帶 query、`downloadfile` 樣式；`.php`、`pdf.gif%20` 等非文件不被排除；FilterChain 組合；`success=False` 記錄錯誤訊息；`SiteConfig.documents.url_patterns` 預設值 | ncucsie 重爬（exclude words 的 LLM，小額）：頁面鍵集合與 `data/raw_webpages/ncucsie` 比對（差異須可由網站變動解釋）；log 無文件 URL 導航；`error_no_markdown` 約 2 |
| P1a | 快照連跑兩次相同；fake 下載依固定規則注入失敗，使快照涵蓋下載失敗、格式不符、svg 略過、跨頁快取、整輪重試（patch `time.sleep`）；下載器以 `httpx.MockTransport` 測去重、同時連線數 ≤ 上限、5xx／429／逾時重試而 4xx 不重試、`max_bytes`、重新導向 `final_url`、錯誤字串 | 下載器實抓 ncucsie `downloadfile` 連結（`network`，免費），確認回 200 與 `Content-Disposition` |
| P1b | 快照逐字一致；新 config 載入與 `run_name_fields`；`src/`、`configs/`、`tests/`、`README.md` 中 `grep image_summarizer` 無結果（歷史工作文件除外） | `run augmenter --help` 可執行、舊指令已移除；runs/ 模組資料夾為 `augmenter` |
| P1c | 快照逐字一致 + P1c 列出的新測試（跨頁並行上限、跨頁失敗只計一次、永久錯誤不重試、依 URL 對位） | nculab 真實 VLM 實跑（`cost`）：流程完成、統計數字與不重複資源數一致；記錄耗時並與重構前比較 |
| P1d | 新測試（尺寸門檻、內容去重）；以腳本比對新舊快照，**每處差異都須歸類**為「小圖略過」或「共用描述」，否則不通過 | ncucsie 實跑（`cost`）：VLM 呼叫數約 161 → 約 105，記錄費用 |
| P2a | 規則、格式判斷優先序、URL 與內容去重、鍵、標題優先序、未啟用格式略過、`files/` 發布與過期清除、`page_title` 取自 `title`；頁面 entry 不受影響（快照不變） | ncucsie 實跑 `images.enabled: false`（無 VLM 費用）→ 建庫（embedding 小額）→ **文件檢索問題集** |
| P2b | 解析器介面以 fake converter 測試；以極小 PDF fixture 實際呼叫 Docling（`heavy`） | 44 份 PDF 逐份報告（成功或略過原因）；抽查 TARA 表格、修業辦法、英文辦法；`uv.lock` 只多出預期套件；記錄模型快取位置與耗時；問題集加入 PDF 題目 |
| P2c | 文件圖片插回位置；與頁面圖片共用快取與過濾；VLM 失敗進入重試 | ncucsie 完整實跑（`cost`）：甄試通知 7 張截圖有描述、校徽只描述一次；記錄費用；完整問題集 |

### 文件檢索問題集

- P2a 建立，P2b、P2c 擴充；`tests/integration` 中標記 `cost` 的 pytest 測試，問題集為 YAML fixture（問題 → 預期出現的文件 URL）。
- 只呼叫 retriever（不經 Agent 的 LLM），斷言預期文件出現在 top-k；失敗時列出未命中的題目與實際排名。費用僅查詢的 embedding。
- 例：「論文指導確認表要去哪裡下載？」→ 確認表 entry；「碩士班修業辦法對學分有什麼規定？」→ 修業辦法 PDF（P2b 起）；「甄試報名的繳費帳號在哪裡查？」→ 甄試通知中截圖的描述（P2c 起）。

### 正式發布

- P2c 完成後，以新程式碼重跑 `prepare`（ncucsie、nculab，publish），將新的 `data/` 以**獨立的資料 commit** 提交，與程式碼 commit 分開。
- 發布後執行完整問題集與 `pytest tests/integration -m cost` 作為最終驗收，結果記入 verification.md。

## 決策紀錄

✅ 為已決定項目。

| # | 議題 | 選項 | 決定／初步建議 |
|---|---|---|---|
| 1 | 模組定位 | (a) 併入 `WebsiteCrawler`；(b) 獨立的文件階段；(c) 擴充 image summarizer 為通用 Augmenter | ✅ **(c)**（原決定 (b)，因流程同構而改） |
| 2 | 解析工具 | MarkItDown、Docling、anydoc、pdf-inspector（實測見「解析工具選型」） | ✅ **PDF 用 Docling；docx／doc／odt 用 anydoc** |
| 3 | 格式範圍 | pdf + docx／擴大為 pdf + docx + doc + odt | ✅ **pdf、docx、doc、odt**（原決定 pdf + docx；anydoc 可直接處理 doc／odt，不需 LibreOffice，故擴大） |
| 4 | 網域範圍 | 沿用 `allowed_domains` 或允許站外文件 | ✅ **沿用 `allowed_domains`** |
| 5 | 資料佈局 | 原檔：隨 aug_webpages 發布／`data/raw_documents/`／只留 runs/；鍵：hash／可讀名 + hash／沿用路徑規則 | ✅ **原檔隨 aug_webpages 發布（`files/<key>.<ext>`）；鍵為 `doc_` + URL sha1 前 12 碼** |
| 6 | 文件標題 | 規則（連結文字…）／加上 LLM 產生 | ✅ **規則**：連結文字 → `title` 屬性 → 可讀檔名 → 內文第一個 heading → URL 檔名；不用 PDF 內嵌標題 |
| 6a | 頁面與文件的關聯 | 只寫在文件 metadata／頁面連結加註／文件摘要內嵌回頁面 | ✅ **只寫在文件 metadata**（`source_pages`），頁面 markdown 不變 |
| 6b | 文件日期 | 引用頁面最早日期／PDF 建立日期／不設定 | ✅ **不設定**，由 `MarkdownDateExtractor` 從內文推斷 |
| 7 | 文件內圖片 | 首版不處理／首版就處理 | ✅ **首版就處理**：解析器抽出內嵌圖片，交給 `ImageCaptioner`，描述插回文件 markdown（見 P2c） |
| 8 | 低價值文件 | 未啟用格式：略過／空殼 entry／保存原檔不解析；空白表單：照常／偵測排除 | ✅ **未啟用格式略過，只記統計與 log；空白表單照常解析** |
| 9 | 下載工具 | Crawlee、Scrapy、Firecrawl、自寫 | ✅ **自寫共用下載器（httpx）**，圖片與文件共用 |
| 10 | 實作順序 | 先重構圖片／先做文件／一次完成 | ✅ **先重構圖片、再加入文件**（細分見 #21） |
| 11 | 命名 | 改名 augmenter／保留 image_summarizer | ✅ **改名 augmenter**（`data/aug_webpages` 不變） |
| 12 | 下載器記憶體 | `content: bytes` + `max_bytes`／另提供串流寫檔 | ✅ **首版讀進記憶體**；遇到大檔需求再加 `dest_path` |
| 13 | 統計與重試單位 | 以出現次數（現行）／以不重複資源 | ✅ **以不重複資源**（修正壞圖跨頁重複計數，見 P1c 行為變更） |
| 14 | 舊 runs/ 紀錄 | 不相容／同時搜尋新舊名稱／遷移腳本 | ✅ **不相容**，並將參數簡化為 `use_latest_results`（`--run.use-latest-results`） |
| 15 | 文件規則位置 | 站點樣式放站點設定 + 副檔名常數／全放 augmenter 設定／全放站點設定 | ✅ **站點樣式放站點設定、通用副檔名為程式常數、解析格式放 augmenter 設定** |
| 16 | 整輪重試範圍 | 只用在圖片／圖片與文件一起算／文件獨立一套 | ✅ **圖片與文件共用一套**（一組 `retry` 設定、合併計算成功率） |
| 17 | 永久錯誤 | 圖片與文件都排除／只排除文件／都不排除 | ✅ **都排除**：只有可恢復的失敗計入成功率與重試名單 |
| 18 | Docling OCR | 關閉／維持預設開啟 | ✅ **維持預設開啟** |
| 19 | 送 VLM 前的圖片過濾 | 內容去重、尺寸門檻、單份文件圖片數上限；只用於文件圖片／也用於網頁圖片 | ✅ **內容 sha1 去重 + 長邊 < 100px 不送**，網頁圖片與文件圖片共用，**屬於 Phase 1**，排在重構驗收之後的 P1d（快照只出現這兩項造成的差異）；不設圖片數上限 |
| 20 | 描述對位 bug | — | ✅ P1c 改為依 URL 對位（現有資料未觸發，輸出不變） |
| 21 | 實作階段拆分 | Phase 1／2 兩階段；細拆 8 階段；6 階段 | ✅ **細拆 8 階段**（P0、P1a～P1d、P2a～P2c），見「實作階段」 |
| 22 | 程式碼管理 | 每階段一分支一 PR／同一分支每階段一 commit／每個 Phase 一分支 | ✅ **同一功能分支，每階段一個 commit** |
| 23 | 重構驗收方式 | 重構前後實跑比對／基準快照測試 | ✅ **基準快照測試**（nculab fixture + 確定性 fake，P1a 以現行程式碼建立）；VLM 輸出不確定，實跑只確認流程可完成 |
| 24 | 驗證紀錄位置 | 新增 verification.md／plan.md 各階段底下／commit message | ✅ **新增 [verification.md](verification.md)**，commit message 只寫摘要 |
| 25 | data/ 正式發布 | P2c 後獨立資料 commit／每個改變輸出的階段各自發布 | ✅ **P2c 後獨立資料 commit**；各階段驗證一律不 publish |
| 26 | 文件檢索問題集 | `cost` pytest 測試／獨立腳本／人工查詢 | ✅ **`cost` pytest 測試**（YAML fixture，只呼叫 retriever） |
| 27 | pytest marker | 新增 `network`、`heavy`／全部用 `cost` | ✅ **新增 `network`、`heavy`** |
