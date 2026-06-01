# 圖片處理

## 模組總覽
此模組以 **VLM** 為網頁中的每張圖片生成結構化說明，並將結果附加到對應頁面的 Markdown 末尾。流程會先從爬取結果收集圖片來源，再進行下載、快取、摘要與重試，最後產生包含圖片說明的 `enhanced_markdown` 與統計資訊。

- **模組實作**
	- `app/modules/webpage_image_summarizer.py`（主流程，包含**圖片擷取**、**下載**、**摘要**、**快取**、**重試**與 **Markdown 增強**）
	- `app/configs/webpage_image_summarizer_config.py`（**設定載入**、**驗證**、**覆寫**與 **API key 推斷**）
	- `utils/log_helper.py`（**日誌**、**進度**與**統計輸出**輔助）

- **模組設定**
	- `./configs/webpage_image_summarizer/{name}.toml`（**摘要設定檔**，透過 `app/configs/webpage_image_summarizer_config.py` 載入）
	- 可在 `WebpageImageSummarizerConfig` 或執行參數中覆寫 **model**、**prompt**、**image_source**、**vlm_max_workers** 與 **litellm_kwargs**
	- `get_summarizer_model_api_key()` 會依模型名稱推斷對應的環境變數，並從 `.env` 或系統環境讀取

- **模組環境**
	- `Python >= 3.10`（程式使用現代型別語法如 `dict[str, Any]` 與 `Literal`）
	- **標準函式庫**：`asyncio`、`base64`、`re`、`time`、`urllib.request`、`concurrent.futures`
	- **第三方套件**：`litellm`（**LLM 呼叫**與**成本計算**）、`rich`（**表格輸出**）

## webpage_image_summarizer.py

### 1. 圖片來源擷取
- `image_source="markdown"` 時，從 `fit_markdown` 的 Markdown 圖片標記擷取 URL。
- `image_source="images"` 時，從 `crawl_result["images"]` 的 `url` 欄位擷取 URL。
- 若結果內沒有可處理圖片，會保留原始 Markdown，不進一步摘要。

### 2. 下載與摘要處理
- 使用 `ThreadPoolExecutor(max_workers=vlm_max_workers)` 併行下載圖片。
- 下載時會檢查 `Content-Type` 是否為 `image/*`，再轉成 base64 data URL。
- 下載完成後呼叫 `LiteLLM` 的 `acompletion()` 產生圖片摘要與 caption。

### 3. 快取、重試與輸出
- 以圖片 URL 作為快取鍵，避免重複下載或重複摘要。
- 當成功率低於 `success_threshold` 時，會對失敗項目重試，並使用指數退避與 jitter。
- 最終會回寫 `enhanced_markdown`、更新圖片 caption，並輸出 `cost_usd`、`success`、`failure` 等統計。

## webpage_image_summarizer_config.py

### 1. 設定載入來源
- 從 `./config/webpage_image_summarizer/{name}.toml` 載入設定。
- `init` 區塊管理下載與快取參數，`summarize` 區塊管理模型與摘要參數，`litellm_kwargs` 區塊管理傳給 `LiteLLM` 的額外參數。
- `from_toml()` 會在建立物件時立即載入並驗證設定。

### 2. 可驗證設定
- 驗證 `download_timeout`、`success_threshold`、`max_retries`、`cache_download_images`、`cache_image_captions`。
- 驗證 `model`、`prompt`、`image_source`、`vlm_max_workers`、`litellm_kwargs`。
- `override_init_config()` 與 `override_summarize_config()` 會先套用覆寫，再重新驗證。

### 3. API key 與 run name
- `get_summarizer_model_api_key()` 會依模型名稱推斷 `gpt` 或 `gemini` 對應的環境變數。
- `run_name` 會依 TOML 中註解標記的欄位組合而成，方便區分不同實驗設定。
- 預設提示詞由 `DEFAULT_PROMPT` 提供，內容聚焦在可檢索、可驗證的圖片摘要。

## 補充說明
- 下載與摘要流程拆分為 `_download_images()` 與 `_generate_image_captions()`。
- `_collect_cached_items()` 會先復用可用快取，再補做缺漏項目。
- `_retrieve_retry_context()` 會根據失敗數量與成功率決定是否重試。
- `_log_stats()` 會輸出 `cost_usd`、`success`、`failure`、`download_failure`、`summarize_failure` 等統計資訊。
