# 處理網頁圖片

## 方案 A：摘要網頁圖片資訊
- 原則：呼叫 VLM 為網頁中的每張圖片生成結構化說明，並將結果附加到該頁 Markdown 的末尾。
- 核心實作：`app/webpage_image_summarizer.py`
- 統一 API：LiteLLM
- 支援模型：依 model 名稱可使用 `gpt` 或 `gemini`
- API key 推斷：`get_summarizer_model_api_key` 會從 `.env` 或系統環境載入對應 key

### 實作流程
1. 圖片來源與 URL 解析
   - `image_source="markdown"` 從 `fit_markdown` 的 Markdown 圖片標記擷取 URL
   - `image_source="images"` 從 `crawl_result["images"]` 的 `src` 欄位擷取 URL
2. 圖片下載與 Base64 轉換
   - 使用 `urllib.request.Request` 並帶入標準 `User-Agent` 下載圖片
   - 檢查 Content-Type 是否為 `image/*`
   - 成功後將圖片轉成 base64 data URL 供 VLM 使用
3. 並行處理與工作數上限
   - 使用 `ThreadPoolExecutor(max_workers=vlm_max_workers)` 併行下載圖片
   - 下載完成後呼叫 LiteLLM 的 `acompletion()` 進行圖片摘要
4. 快取與重用
   - 以圖片 URL 做快取鍵，避免重複下載相同圖片
   - 若圖片已成功下載，直接重用 base64 資料
   - Caption 快取邏輯目前在程式碼中註解，以下載快取為主
5. 失敗判斷與重試
   - 若成功率低於 `success_threshold`，會重試下載或摘要失敗的圖片
   - 指數退避等待時間依序為 30s、60s、120s、300s、600s，並加入 ±20% jitter
   - 最多重試 `max_retries` 次
6. Markdown 增強
   - `image_source="markdown"`：在每張圖片下方以 blockquote 形式插入 caption
   - `image_source="images"`：在 Markdown 末尾追加多個 `## Image-i` 段落說明

### 設定與驗證
- `app/webpage_image_summarizer_config.py` 管理下載與摘要參數
- 支援設定：`download_timeout`、`success_threshold`、`max_retries`、`cache_download_images`
- 摘要設定：`model`、`prompt`、`image_source`、`vlm_max_workers`、`litellm_kwargs`
- `_validate_init_config()` 會驗證下載參數型別與範圍
- `_validate_summarize_config()` 會驗證模型、prompt、來源、worker 數與 litellm_kwargs

### 補充說明
- 下載與摘要流程拆分為 `_download_images()` 和 `_generate_image_captions()`
- `_retrieve_retry_context()` 會根據失敗 URL 與成功率決定是否要重試
- `_prepare_retry_urls()` 會根據重試次數計算等待時間並執行 sleep
- `_log_stats()` 會輸出 `cost_usd`、`success`、`failure`、`download_failure`、`summarize_failure` 等統計資訊

## 方案B：保留網頁原始圖片
> 待更新

# 當前進度

- [x] 摘要網頁圖片資訊
  - [x] 呼叫 VLM
  - [x] 平行處理、快取
  - [x] 自動重試
  - [ ] 下載和摘要拆成兩個模組

# 未來規劃
- 處理網頁文件
