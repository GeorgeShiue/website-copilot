# Website Copilot
> 專案目前集中在第 1 階段：資訊檢索。後續規劃涵蓋網站導航與專責代理。

Website Copilot 是一個 Python 專案，將網站內容轉換為可檢索的知識庫。它會爬取網頁、清理並格式化內容、使用視覺語言模型摘要圖片，並建立本地向量索引以供檢索。


## 專案功能

- 爬取網站並匯出已清理的 Markdown 頁面。
- 摘要網頁圖片並將說明附加到 Markdown 輸出中。
- 建立或載入本地向量索引（Qdrant / Milvus）以進行混合檢索，同步進行語意比對與關鍵字比對。
- 利用爬蟲階段注入的頁面類型標籤，在檢索前隔離跨類別雜訊。
- 將檢索能力包裝為工具，供下游 Agent 動態呼叫與過濾。
- 使用 Gemini / GPT 驅動的查詢引擎處理索引後內容，並自動評估回答品質。
- 保存每次執行的輸出 artefacts、日誌和生成的 Markdown。

## 專案流程

1. 爬取目標網站，從 URL 解析頁面類型，將結果儲存為 Markdown 和 JSON。
2. 摘要爬取結果中的圖片，生成增強版 Markdown。
3. 將處理後的 Markdown 載入向量索引（Qdrant BM25 或 Milvus BGE-M3），同時建立稠密向量與稀疏向量索引。
4. 將檢索能力包裝為工具，支援動態過濾條件供 Agent 呼叫。
5. 執行查詢時以 Dense + Sparse 混合檢索，過濾指定頁面類型，由 LLM 生成有來源的回答。

## 檔案結構

下面範例列出本專案的根目錄與主要子目錄（以實際檔案為準）：

```text
.
├── prek.toml                    # ruff/prek 設定
├── pyproject.toml               # Python 專案設定與依賴
├── README.md
├── uv.lock
├── src/
│   ├── cli.py                   # CLI 入口
│   ├── exp.py                   # 實驗或快速測試入口
│   ├── main.py                  # 協調爬蟲與圖片摘要的主流程
│   ├── app/
│   │   ├── configs/
│   │   │   ├── rag_config.py
│   │   │   ├── webpage_image_summarizer_config.py
│   │   │   └── website_crawler_config.py
│   │   ├── modules/
│   │   │   ├── rag.py
│   │   │   ├── rag_factory.py            # RAG 建構（RAGBuilder / NodePipelineBuilder / VectorStoreBuilder）
│   │   │   ├── rag_eval_prompts.py       # 評估 Prompt 模板
│   │   │   ├── webpage_image_summarizer.py
│   │   │   └── website_crawler.py
│   │   ├── tools/
│   │   │   └── webpage_retriever.py      # RAG retriever → LangChain StructuredTool
│   │   └── workflow/
│   │       ├── workflow.py
│   │       ├── workflow_config.py
│   │       └── workflow_manager.py
│   ├── test/
│   │   ├── test_main.py
│   │   └── test_module.py
│   └── utils/
│       ├── config_helper.py
│       ├── log_helper.py
│       └── rag_helper.py
├── configs/
│   ├── rag/
│   │   ├── default.toml               # 預設設定（Milvus + WeightedRanker hybrid）
│   │   ├── milvus.toml                 # Milvus + WeightedRanker
│   │   ├── qdrant.toml                 # Qdrant BM25 Hybrid
│   │   └── test.toml                   # 測試用（同 default，Milvus hybrid）
│   ├── webpage_image_summarizer/
│   │   ├── default.toml
│   │   ├── test.toml
│   │   └── ...
│   └── website_crawler/
│       ├── default.toml
│       └── test.toml
├── data/
│   ├── rag/
│   │   └── results/                    # 向量資料庫（qdrant_db/ 或 milvus.db）
│   └── webpages/
│       ├── results/                    # 爬蟲與摘要結果
│       ├── results.json                # 結果索引
│       └── module_config.toml          # 模組設定備份
├── dev/
├── docs/
│   ├── project.md                      # 專案總覽與路線圖
│   ├── code/
│   │   └── phase1/
│   │       ├── phase1.md               # Phase 1 實作概覽
│   │       ├── modules/
│   │       │   ├── data_collect.md     # 爬蟲模組文件
│   │       │   ├── data_preprocess.md  # 圖片摘要模組文件
│   │       │   └── data_retrieve.md    # RAG 檢索模組文件
│   │       ├── runs/
│   │       │   ├── cli.md              # CLI 使用方式
│   │       │   ├── config.md           # 設定機制說明
│   │       │   └── workflow.md         # Workflow 流程說明
│   │       └── survey/
│   │           └── data_process_method.md  # 資料處理方法 survey
│   └── progress_report/                # 進度報告
└── runs/                         # 執行輸出（以時間戳資料夾儲存）
```

## 需求

- Python 3.13.12 或更新版本，已在 `pyproject.toml` 中宣告。
- 可正常執行的 Playwright / 瀏覽器環境，用於爬取。
- 嵌入、查詢與圖片摘要模型的 API 金鑰。

專案依賴已在 `pyproject.toml` 中聲明，包含常見的套件（例如 `crawl4ai`, `playwright`,
`llama-index` 與其外部整合、`litellm`, `rich`, `python-dotenv`, `mdformat` 等）。

## 安裝

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
playwright install
```

如果你使用不同的環境管理方式，請從 `pyproject.toml` 安裝依賴，並確保在執行爬蟲前已安裝 Playwright 瀏覽器。

## 設定

本專案使用 `configs/` 底下的 TOML 檔案，以及從 `.env` 讀取環境變數。

### 爬蟲設定

- `configs/website_crawler/*.toml`
- 控制爬取深度、頁面數量限制、內容過濾、URL 模式與允許網域。

### 圖片摘要設定

- `configs/webpage_image_summarizer/*.toml`
- 控制圖片下載逾時、重試行為、快取、模型選擇、prompt 文本以及圖片來源模式。

### 環境變數

| Variable | Used by | Purpose |
| --- | --- | --- |
| `OPENAI_RAG_EMBEDDING_API_KEY` | `app/modules/rag_factory.py` | 向量索引的嵌入模型金鑰。 |
| `GEMINI_RAG_QUERY_ENGINE_API_KEY` | `utils/rag_helper.py` | 用於回答生成的 Gemini 金鑰。 |
| `OPENAI_RAG_QUERY_ENGINE_API_KEY` | `utils/rag_helper.py` | 用於回答生成的 GPT 金鑰。 |
| `GEMINI_RAG_EVALUATOR_API_KEY` | `utils/rag_helper.py` | 回答評估（Gemini）。 |
| `OPENAI_RAG_EVALUATOR_API_KEY` | `utils/rag_helper.py` | 回答評估（GPT）。 |
| `OPENAI_WEBPAGE_IMAGE_SUMMARIZER_VLM_API_KEY` | `app/modules/webpage_image_summarizer.py` | GPT 圖片摘要金鑰。 |
| `GEMINI_WEBPAGE_IMAGE_SUMMARIZER_VLM_API_KEY` | `app/modules/webpage_image_summarizer.py` | Gemini 圖片摘要金鑰。 |

## 使用方式

### 執行爬取與圖片摘要流程

```bash
python main.py
```

這會先執行網站爬蟲，然後將爬取結果傳給圖片摘要器。輸出會寫入 `runs/<timestamp>/...`。

### 執行 RAG 查詢

```bash
# 使用 Milvus + WeightedRanker 執行混合檢索
python cli.py rag-query-cli --run.config-name milvus

# 使用 Qdrant BM25 混合檢索
python cli.py rag-query-cli --run.config-name qdrant

# 自訂 top-k 與過濾條件（透過 CLI 覆寫）
python cli.py rag-query-cli --run.config-name milvus --module.similarity_top_k 10 --module.hybrid_top_k 20
```

也可以透過 `exp.py` 執行批次實驗，例如比較 Dense 與 Hybrid 在多個查詢上的表現。

> **注意**：`exp.py` 內各實驗函式以 `config_name` 對應 `configs/rag/{name}.toml`（例如 `dense`、`hybrid`、`milvus-weight`、`milvus-RRF`、`gemini-3.1-pro` 等實驗用設定檔），這些檔案未收錄於倉庫。執行前需先自行建立對應設定檔，或調整 `exp.py` 中的 `config_name` 清單。

### 執行 smoke tests

```bash
pytest
```

`test/` 中的測試會使用 `test` 設定檔，檢查爬蟲與圖片摘要器。

## 輸出

每次執行會在 `runs/<timestamp>/<module>/<run_name>/` 下產生以下 artefacts：

- `results.json` — 結構化結果（爬取/摘要結果，或 `run_rag_query` 的 query 三層結構）
- `results/*.md` — 每頁的 Markdown 內容（`run_rag_query` 另含每次 query 一份的 `results/query_{index}.md`）
- `module_config.toml` — 本次執行的模組參數備份
- `run_config.toml` — run-level 參數（`cli.py` 與 `main.py` 入口會寫出）
- `terminal.log` — 執行日誌

向量資料庫預設持久化於 `data/rag/results/`：
- `qdrant_db/` — Qdrant 向量儲存
- `milvus.db` — Milvus Lite 向量儲存

`run_rag_build` 可加 `--run.save-vector-store-to-runs`，將向量庫改存至該次 run 的 `results/vector_store/`，避免不同 run 互相覆寫。

## 開發

- 格式化與 lint 透過 `ruff` 與 `prek.toml` 設定。
- `src/test/test_main.py` 會使用測試設定檔執行完整流程。
- `src/test/test_module.py` 會獨立執行爬蟲與摘要器。

## 文件

專案的實作筆記與路線圖位於 `docs/`：

- `docs/project.md` — 專案總覽、階段規劃與路線圖
- `docs/code/phase1/phase1.md` — Phase 1 實作概覽與已知問題
- `docs/code/phase1/modules/data_collect.md` — 爬蟲模組說明
- `docs/code/phase1/modules/data_preprocess.md` — 圖片摘要模組說明
- `docs/code/phase1/modules/data_retrieve.md` — RAG 檢索模組說明
- `docs/code/phase1/runs/cli.md` — CLI 使用方式
- `docs/code/phase1/runs/config.md` — 設定機制說明
- `docs/code/phase1/runs/workflow.md` — Workflow 流程說明
- `docs/code/phase1/survey/data_process_method.md` — 資料處理方法 survey

## 狀態

目前實作涵蓋：

- 網站爬取、Markdown 清理與頁面類型分類
- 圖片摘要與快取/重試邏輯
- 本地向量檢索（Qdrant BM25 / Milvus BGE-M3）
- 稠密 + 稀疏混合檢索（WeightedRanker / RRFRanker）
- Metadata 頁面類型過濾
- RAG Retriever Tool（StructuredTool 封裝，供 Agent 呼叫）
- Gemini / GPT 驅動的來源檢索式查詢引擎
- 自動化回答品質評估（Faithfulness + Relevancy）
- Query 結果落盤（`results.json` + `results/query_{index}.md`）與向量庫可存至 run 內（`save_vector_store_to_runs`）

後續規劃請參閱 `docs/project.md`。
