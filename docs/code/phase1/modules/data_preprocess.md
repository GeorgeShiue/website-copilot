# 圖片處理

## 模組總覽
此模組以 **VLM** 為網頁中的每張圖片生成結構化說明，並將結果附加到對應頁面的 Markdown 末尾。流程會先從爬取結果收集圖片來源並過濾 VLM 不支援的格式，再進行下載、快取、摘要與重試，最後產生包含圖片說明的 `enhanced_markdown` 與統計資訊。

- **模組實作**
	- `src/website_copilot/ingestion/augmentation/image_summarizer.py`（主流程，包含**圖片擷取**、**下載**、**摘要**、**快取**、**重試**與 **Markdown 增強**）
	- `src/website_copilot/config/image_summarizer_config.py`（**設定載入**、**驗證**、**覆寫**，）
	- `src/website_copilot/utils/log_helper.py`（**日誌**、**進度**與**統計輸出**輔助）

- **模組設定**
	- `./configs/image_summarizer/{name}.yml`（**摘要設定檔**，只寫與 class 預設值不同的部分，透過 `src/website_copilot/config/image_summarizer_config.py` 載入）
	- 可在 `ImageSummarizerConfig` 或執行參數中覆寫 **model**、**prompt**、**image_source**、**vlm_max_workers** 與 **litellm_kwargs**
	- 開始摘要前以 `utils/llm_provider` 依模型名稱解析供應商（litellm 前綴與 API key 環境變數），並從 `.env` 或系統環境讀取 API key；無法判斷供應商或缺 key 時直接失敗

- **模組環境**
	- `Python >= 3.13`（程式使用現代型別語法如 `dict[str, Any]` 與 `Literal`）
	- **標準函式庫**：`asyncio`、`base64`、`re`、`time`、`urllib.request`、`concurrent.futures`
	- **第三方套件**：`litellm`（**LLM 呼叫**與**成本計算**）、`rich`（**表格輸出**）

## image_summarizer.py

### 1. 圖片來源擷取
- `image_source="markdown"` 時，從 `fit_markdown` 的 Markdown 圖片標記擷取 URL。
- `image_source="images"` 時，從 `crawl_result["images"]` 的 `url` 欄位擷取 URL。
- 若結果內沒有可處理圖片，會保留原始 Markdown，不進一步摘要。

### 2. 下載與摘要處理
- 擷取到的圖片 URL 會先依副檔名（`.svg`／`.avif`／`.bmp`／`.ico`／`.tif`／`.tiff`）過濾掉 VLM 不支援的格式，再進入下載流程。
- 使用 `ThreadPoolExecutor(max_workers=vlm_max_workers)` 併行下載圖片。
- 下載時會檢查 `Content-Type` 是否屬於 `SUPPORTED_IMAGE_CONTENT_TYPES`（`image/png`／`image/jpeg`／`image/gif`／`image/webp`），非此範圍一律視為下載失敗，再轉成 base64 data URL。
- 下載完成後呼叫 `LiteLLM` 的 `acompletion()` 產生圖片摘要與 caption。

### 3. 快取、重試與輸出
- 以圖片 URL 作為快取鍵，避免重複下載或重複摘要。
- 當成功率低於 `success_threshold` 時，會對失敗項目重試，並使用指數退避與 jitter。
- 最終會回寫 `enhanced_markdown`、更新圖片 caption，並輸出 `cost_usd`、`success`、`failure` 等統計。

## image_summarizer_config.py

### 1. 設定載入來源
- 從 `./configs/image_summarizer/{name}.yml` 載入設定（支援 `extends`；站點資訊不在此，由 `configs/sites/{site}.yml` 提供）。
- `init` 區塊管理下載與重試參數，`summarize` 區塊管理模型與摘要參數，`litellm_kwargs` 區塊管理傳給 `LiteLLM` 的額外參數。
- `from_yaml(config_name, overrides=None)` 會在建立物件時載入、疊上 overrides 並以 pydantic 驗證一次。

### 2. 可驗證設定
- 驗證 `download_timeout`、`success_threshold`、`max_retries`。
- 驗證 `model`、`prompt`、`image_source`、`vlm_max_workers`、`litellm_kwargs`。
- 覆寫值（CLI `--module.*`）為巢狀 dict，與設定檔同一個 deep merge 合併後統一驗證。

### 3. API key 與 run name
- 供應商對照表 `utils/llm_provider.PROVIDERS` 依模型名稱（不分大小寫，含 `gpt` / `gemini` 關鍵字）對應 API key 環境變數與 litellm 前綴，RAG、Agent 共用。
- `run_name` 會依 YAML 的 `run_name_fields` 組成（未寫時為 class 預設 `summarize.model`），方便區分不同實驗設定。
- 預設提示詞由 `config/prompts.py` 的 `IMAGE_SUMMARY_PROMPT` 提供，內容聚焦在可檢索、可驗證的圖片摘要。

## 補充說明
- 下載與摘要流程拆分為 `_download_images()` 與 `_generate_image_captions()`。
- 每張圖片的下載與摘要結果存於單一快取 `_image_cache`（`url → ImageEntry`），同一 run 內跨頁共用；`_collect_cached_items()` 會先復用可用快取，再補做缺漏項目。
- `_retrieve_retry_context()` 會根據失敗數量與成功率決定是否重試。
- 統計以 `PageStats`（逐頁：`cost_usd`、`success`、`download_failure`、`summarize_failure`、`cache_reuse`）與 `RoundStats`（跨輪：`cost_usd`、`success`、`failure`、`retries`）記錄並輸出成表格。
