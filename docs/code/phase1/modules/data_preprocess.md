# 資料擴充（圖片與文件）

## 模組總覽
此模組（augmenter）處理兩種資源：以 **VLM** 為網頁中的每張圖片生成結構化說明並寫回頁面的 Markdown；網站連結的文件（PDF／docx／doc／odt）轉成 Markdown，成為獨立的知識庫條目，文件內嵌的圖片同樣交給 VLM 描述。圖片流程為整批處理：先從所有頁面收集圖片來源（跨頁去重，並過濾 VLM 不支援的格式），再整批下載、整批摘要，成功率過低時整輪重試，最後把說明寫回各頁的 `enhanced_markdown` 與 `images[].caption`，並輸出統計資訊。

- **模組實作**
	- `src/website_copilot/ingestion/augmentation/augmenter.py`（主流程：串起篩選 → 下載 → 解析 → 回寫，負責**快取**、**重試**、**統計**與 **Markdown 增強**）
	- `src/website_copilot/ingestion/augmentation/assets.py`（`Asset`／`AssetRef`：跨頁去重後的資源與其引用頁面）
	- `src/website_copilot/ingestion/augmentation/collectors.py`（`ImageCollector`：**圖片擷取**、副檔名過濾、跨頁去重）
	- `src/website_copilot/ingestion/augmentation/processors/image_captioner.py`（`ImageCaptioner`：格式白名單與 base64 轉換、整批 **VLM 摘要**）
	- `src/website_copilot/ingestion/augmentation/processors/image_filter.py`（內容 sha1 與圖片尺寸，供**去重**與**小圖門檻**使用，依賴 `Pillow`）
	- `src/website_copilot/ingestion/augmentation/processors/document_parser.py`／`pdf_parser.py`（依實際格式分派：anydoc 與 Docling）
	- `src/website_copilot/utils/http_downloader.py`（`HttpDownloader`：共用下載器，並行上限、單一請求重試、大小上限）
	- `src/website_copilot/config/augmenter_config.py`（**設定載入**、**驗證**、**覆寫**，）
	- `src/website_copilot/utils/log_helper.py`（**日誌**、**進度**與**統計輸出**輔助）

- **模組設定**
	- `./configs/augmenter/{name}.yml`（**摘要設定檔**，只寫與 class 預設值不同的部分，透過 `src/website_copilot/config/augmenter_config.py` 載入）
	- 可在 `AugmenterConfig` 或執行參數中覆寫 `images` 區塊的 **model**、**prompt**、**source**、**max_concurrency**（VLM 並行數）、`download` 區塊的 **timeout**、**max_concurrency**（下載並行數）、`retry` 區塊與 **litellm_kwargs**
	- 開始摘要前以 `utils/llm_provider` 依模型名稱解析供應商（litellm 前綴與 API key 環境變數），並從 `.env` 或系統環境讀取 API key；無法判斷供應商或缺 key 時直接失敗

- **模組環境**
	- `Python >= 3.13`（程式使用現代型別語法如 `dict[str, Any]` 與 `Literal`）
	- **標準函式庫**：`asyncio`、`base64`、`re`、`time`
	- **第三方套件**：`httpx`（**下載**）、`anydoc`（**docx／doc／odt 解析**）、`docling`（**PDF 解析**，依賴很重）、`Pillow`（**圖片尺寸**）、`litellm`（**LLM 呼叫**與**成本計算**）、`rich`（**表格輸出**）

## 文件處理（documents.py）

- **收集**：`DocumentCollector` 從所有已爬頁面（含深度 2、不受 `max_depth` 限制）的 Markdown 連結收集文件；規則見 `utils/document_rules.py`（通用副檔名 + 站點設定 `documents.url_patterns`），網域沿用 `allowed_domains`，依正規化 URL 去重，`refs` 記錄所有引用頁面、連結文字與 title 屬性。
- **下載與格式**：共用下載器下載；格式依優先序判斷：檔頭 magic bytes（anydoc）> `Content-Disposition` 檔名 > `Content-Type` > URL 副檔名。格式不在 `documents.formats` 者只記統計與 log。
- **去重與鍵**：內容 sha1 相同的不同 URL 只建一筆 entry（鍵取第一個 URL）。entry 鍵為 `doc_` + 正規化 URL sha1 前 12 碼。
- **解析**（執行緒池）：docx／doc／odt 以 anydoc 轉 Markdown；PDF 以 Docling（`processors/pdf_parser.py`）：版面模型還原標題層級、條列與表格，圖片保留 `<!-- image -->` 佔位符，OCR 維持 Docling 預設（開啟）。Docling 延遲到第一份 PDF 才載入，converter 只建立一次、呼叫以鎖序列化（共用 GPU）；首次會下載版面／表格模型（HuggingFace 快取）與 RapidOCR 模型（存於 site-packages 的 `rapidocr/models`）。掃描版 PDF（沒有文字層、整頁是一張圖）抽不到文字，記錄為解析失敗並略過（OCR 另案）。解析失敗（損毀、無文字）為永久失敗，不重試。
- **標題**（規則，不用 LLM）：連結文字（排除通用字，取最常出現者）→ 連結 `title` 屬性 → 非純數字的原始檔名 → 內文第一個 heading → URL 檔名；不採用文件內嵌的 metadata 標題。
- **回寫**：每份文件成為 `results.json` 的獨立 entry（`url`、`title`、`enhanced_markdown`、`images: []`、`metadata`：`page_type: "document"`、`file_format`、`file_name`、`file_size`、`content_type`、`downloaded_at`、`file_path`、`alternate_urls`、`source_pages`）；頁面的 Markdown 不變。原檔由 `Augmenter.document_files` 提供，存到 `files/<key>.<ext>`。
- **進 RAG**：`NodePipelineBuilder` 以 entry 的 `title` 作為 `page_title`，並附上 `file_format`／`file_name`；`source_pages` 在切塊之後才寫入 node（避免 metadata 超過 chunk size），並排除於 embedding 與 LLM 文字之外。`published_date` 不設定，由 `MarkdownDateExtractor` 從內文推斷。
- **文件內嵌圖片**（`documents.caption_images` 且 `images.enabled`）：PDF 由 Docling 版面模型挑出有意義的圖片（含整頁底圖的雜訊圖不會被選到）並與 `<!-- image -->` 佔位符一一對應；docx／doc／odt 由 anydoc 文件模型找出圖片所在的 block，以該 block 的第一段文字為錨點定位並插入佔位符（圖片在表格中時放在整個表格之後）。每張圖成為 `kind="image"` 的資源（URL 為 `doc-image:<內容 sha1>`，不需下載），與頁面圖片一起送 `ImageCaptioner`，套用相同的過濾（小圖門檻、內容去重，同一張圖在多份文件或與頁面圖片相同時只描述一次）與整輪重試；描述以與頁面圖片相同的格式（`> # Image-{n}`，n 為文件內圖片序號）取代佔位符，沒有描述（小圖、失敗、格式不支援）者移除佔位符。流程順序：收集 → 下載（頁面圖片、文件）→ 解析文件（產生內嵌圖片資源）→ 圖片描述 → 回寫。不設單份文件圖片數上限。
- 與圖片共用整輪退避重試：成功率合併兩種資源計算，重試時可恢復的失敗（逾時、連線錯誤、5xx、429、403）一起重做。

## augmenter.py

### 1. 圖片來源擷取（`ImageCollector`）
- `images.source="markdown"` 時，從 `fit_markdown` 的 Markdown 圖片標記擷取 URL。
- `images.source="images"` 時，從 `crawl_result["images"]` 的 `url` 欄位擷取 URL。
- 擷取到的 URL 先依副檔名（`.svg`／`.avif`／`.bmp`／`.ico`／`.tif`／`.tiff`）過濾掉 VLM 不支援的格式。
- 跨頁去重：每個不重複的 URL 是一個 `Asset`，`refs` 依頁面順序記錄所有引用（第一筆即第一個引用頁面）。
- 沒有可處理圖片的頁面，`enhanced_markdown` 保留原始 Markdown。

### 2. 下載與摘要處理
- 所有頁面的圖片一次交給 `HttpDownloader.download()`：單一 `httpx.AsyncClient`，同時請求數受 `download.max_concurrency` 限制（跨頁共用）；逾時、連線錯誤、5xx、429 依 `download.max_retries` 重試，超過 `download.max_bytes` 即失敗。
- 下載後檢查 `Content-Type` 是否屬於 `SUPPORTED_IMAGE_CONTENT_TYPES`（`image/png`／`image/jpeg`／`image/gif`／`image/webp`），非此範圍視為（永久）失敗，再轉成 base64 data URL。
- 下載後、送 VLM 前過濾（`processors/image_filter.py`，設計為所有圖片共用）：長邊小於 `images.min_size`（預設 100px，圖示、表情符號、1×1 透明 gif 等）的圖片略過，不送 VLM、不產生描述（沒有 `caption` 欄位，比照被副檔名略過的 svg）；內容 sha1 相同的不同 URL 只描述一次，共用代表圖片（第一個下載到該內容者）的描述。尺寸先於內容去重；無法解碼尺寸的圖片不依尺寸過濾。
- 通過過濾、下載成功的圖片整批交給 `ImageCaptioner`，以 `LiteLLM` 的 `acompletion()` 產生摘要；同時呼叫數受 `images.max_concurrency` 限制（跨頁共用）。

### 3. 快取、重試與輸出
- 以圖片 URL 作為快取鍵（`_image_cache`，`url → ImageEntry`），同一 URL 只下載、摘要一次；每筆記錄失敗原因與是否可恢復。
- 失敗分兩類：**可恢復**（逾時、連線錯誤、5xx、429、403、VLM 呼叫失敗）與**永久**（404 等其他 4xx、格式不符、超過大小上限）。成功率 = 成功 ÷（成功 + 可恢復失敗），以不重複資源計算；低於 `retry.success_threshold` 時，依指數退避與 jitter 整輪重做可恢復的失敗項目（下載已成功只重做摘要），永久錯誤直接列為最終失敗。
- 最終依每張 markdown 圖片自己的 URL 查描述，回寫 `enhanced_markdown`（`Image-{n}` 為頁內圖片序號）與 `images[].caption`，並輸出逐頁統計表與失敗清單。

## augmenter_config.py

### 1. 設定載入來源
- 從 `./configs/augmenter/{name}.yml` 載入設定（支援 `extends`；站點資訊不在此，由 `configs/sites/{site}.yml` 提供）。
- `download` 區塊管理下載參數，`retry` 區塊管理整輪重試，`images` 區塊管理 VLM 模型與摘要參數，`litellm_kwargs` 區塊管理傳給 `LiteLLM` 的額外參數。
- `from_yaml(config_name, overrides=None)` 會在建立物件時載入、疊上 overrides 並以 pydantic 驗證一次。

### 2. 可驗證設定
- 驗證 `download.timeout`、`download.max_concurrency`、`retry.success_threshold`、`retry.max_retries`。
- 驗證 `images.model`、`images.prompt`、`images.source`、`images.max_concurrency`、`litellm_kwargs`。
- 覆寫值（CLI `--module.*`）為巢狀 dict，與設定檔同一個 deep merge 合併後統一驗證。

### 3. API key 與 run name
- 供應商對照表 `utils/llm_provider.PROVIDERS` 依模型名稱（不分大小寫，含 `gpt` / `gemini` 關鍵字）對應 API key 環境變數與 litellm 前綴，RAG、Agent 共用。
- `run_name` 會依 YAML 的 `run_name_fields` 組成（未寫時為 class 預設 `images.model`），方便區分不同實驗設定。
- 預設提示詞由 `config/prompts.py` 的 `IMAGE_SUMMARY_PROMPT` 提供，內容聚焦在可檢索、可驗證的圖片摘要。

## 補充說明
- 統計以 `PageStats`（逐頁：`cost_usd`、`success`、`download_failure`、`summarize_failure`、`skipped`（小圖略過）、`cache_reuse`）與 `RoundStats`（跨輪：`cost_usd`、`success`、`failure`、`retries`）記錄並輸出成表格：每個不重複資源只計一次，成功／失敗／略過記在第一個引用頁面，其餘引用記 `cache_reuse`；內容與其他圖片相同而共用描述者也記 `cache_reuse`。
- 整輪重試的 `retry.max_retries` 為最大輪數（含第一輪）；與下載器的單一請求重試（`download.max_retries`）是不同層次，可疊加。
