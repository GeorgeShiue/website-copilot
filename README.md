# Website Copilot
> 專案目前集中在第 1 階段：資訊檢索。後續規劃涵蓋網站導航與專責代理。

Website Copilot 是一個 Python 專案，將網站內容轉換為可檢索的知識庫。它會爬取網頁、清理並格式化內容、使用視覺語言模型摘要圖片，並建立本地向量索引以供檢索。


## 專案功能

- 爬取網站並匯出已清理的 Markdown 頁面。
- 摘要網頁圖片並將說明附加到 Markdown 輸出中。
- 建立或載入本地 Qdrant 向量索引以進行檢索。
- 使用 Gemini 驅動的查詢引擎處理索引後內容。
- 保存每次執行的輸出 artefacts、日誌和生成的 Markdown。

## 專案流程

1. 爬取目標網站並將結果儲存為 Markdown 和 JSON。
2. 摘要爬取結果中的圖片，生成增強版 Markdown。
3. 將處理後的 Markdown 載入 Qdrant 支援的向量索引。
4. 使用 Gemini 模型查詢索引並檢索有來源的回答。

## 檔案結構

```text
.
├── main.py                      # 協調先爬取網站再執行圖片摘要的流程
├── run.py                       # 執行爬蟲與摘要器的共用輔助函式
├── app/
│   ├── website_crawler.py       # 爬取網站、清理 Markdown，並擷取圖片
│   ├── webpage_image_summarizer.py  # 下載圖片、呼叫 VLM，並寫入增強 Markdown
│   └── rag.py                   # 建立或載入向量索引，並執行示範查詢
├── config/
│   ├── website_crawler/         # 爬蟲執行的 TOML 設定
│   └── webpage_image_summarizer/ # 圖片摘要執行的 TOML 設定
├── data/
│   ├── webpages/                # 用於檢索的已生成 Markdown 頁面
│   └── rag/qdrant_db/           # 向量索引的本地 Qdrant persistence
├── runs/                        # 時間戳執行輸出、設定和日誌
├── docs/                        # 專案筆記、進度文件與模組文件
└── test/                        # 主流程與單一模組的 smoke tests
```

## 需求

- Python 3.13.12 或更新版本，已在 `pyproject.toml` 中宣告。
- 可正常執行的 Playwright / 瀏覽器環境，用於爬取。
- 嵌入、查詢與圖片摘要模型的 API 金鑰。

- 專案依賴已在 `pyproject.toml` 中聲明，包括：
    - `crawl4ai`
    - `playwright`
    - `llama-index` 以及 OpenAI、Google GenAI 和 Qdrant 的 LlamaIndex 整合。
    - `litellm`
    - `rich`
    - `python-dotenv`
    - `mdformat` 和 `mdformat-gfm`

## 安裝

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
playwright install
```

如果你使用不同的環境管理方式，請從 `pyproject.toml` 安裝依賴，並確保在執行爬蟲前已安裝 Playwright 瀏覽器。

## 設定

本專案使用 `config/` 底下的 TOML 檔案，以及從 `.env` 讀取環境變數。

### 爬蟲設定

- `config/website_crawler/*.toml`
- 控制爬取深度、頁面數量限制、內容過濾、URL 模式與允許網域。

### 圖片摘要設定

- `config/webpage_image_summarizer/*.toml`
- 控制圖片下載逾時、重試行為、快取、模型選擇、prompt 文本以及圖片來源模式。

### 環境變數

| Variable | Used by | Purpose |
| --- | --- | --- |
| `OPENAI_RAG_EMBEDDING_API_KEY` | `app/rag.py` | 向量索引的嵌入模型金鑰。 |
| `GEMINI_RAG_QUERY_ENGINE_API_KEY` | `app/rag.py` | 用於回答生成的 Gemini 金鑰。 |
| `OPENAI_WEBPAGE_IAMGE_SUMMARIZER_VLM_API_KEY` | `app/webpage_image_summarizer_config.py` | GPT 圖片摘要金鑰。 |
| `GEMINI_WEBPAGE_IMAGE_SUMMARIZER_VLM_API_KEY` | `app/webpage_image_summarizer_config.py` | Gemini 圖片摘要金鑰。 |

> 目前程式碼庫中 GPT 圖片摘要環境變數拼寫為 `IAMGE`。除非你更新實作，否則請使用上述完整名稱。

## 使用方式

### 執行爬取與圖片摘要流程

```bash
python main.py
```

這會先執行網站爬蟲，然後將爬取結果傳給圖片摘要器。輸出會寫入 `runs/<timestamp>/...`。

### 執行檢索示範

```bash
python -m app.rag
```

檢索示範會載入 `data/webpages/prompt-v3/results`，建立或重用 `data/rag/qdrant_db` 中的本地 Qdrant 索引，並使用 Gemini 執行範例查詢。

### 執行 smoke tests

```bash
pytest
```

`test/` 中的測試會使用 `test` 設定檔，檢查爬蟲與圖片摘要器。

## 輸出

典型的生成 artefacts 包含：

- `runs/<timestamp>/website_crawler/<run_name>/results.json`
- `runs/<timestamp>/website_crawler/<run_name>/results/*.md`
- `runs/<timestamp>/webpage_image_summarizer/<run_name>/results.json`
- `runs/<timestamp>/webpage_image_summarizer/<run_name>/results/*.md`
- `data/rag/qdrant_db/`

## 開發

- 格式化與 lint 透過 `ruff` 與 `prek.toml` 設定。
- `test/test_main.py` 會使用測試設定檔執行完整流程。
- `test/test_module.py` 會獨立執行爬蟲與摘要器。

## 文件

專案的實作筆記與路線圖位於 `docs/`：

- `docs/Project.md`
- `docs/Data_Collect.md`
- `docs/Data_Preprocess.md`
- `docs/Data_Retrieve.md`

## 狀態

目前實作涵蓋：

- 網站爬取與 Markdown 清理
- 圖片摘要與快取/重試邏輯
- 使用 Qdrant 的本地向量檢索
- 以 Gemini 驅動的來源檢索式查詢引擎

後續規劃請參閱 `docs/Project.md`。
