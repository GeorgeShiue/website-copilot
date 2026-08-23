# `engines/` 重構計畫 (2026/08/19)

> 本文檔分析 `src/app/engines/` 現有結構的問題，並提出重構方案：
> 1. 純函數工具移至 `src/utils/`
> 2. RAG domain 建立子資料夾
> 3. 評估是否需要改名

---

## 1. 背景與動機

### 現有問題

`src/app/engines/` 目前承擔了三種不同性質的程式碼（有狀態業務類別、純函數工具、純常數定義），缺乏一致的組織原則：

| 問題 | 說明 |
|------|------|
| **純函數混在引擎類別中** | `html_date_extractor.py` 和 `markdown_cleaner.py` 是無狀態的純函數，與有狀態的 `WebsiteCrawler` / `RAG` 等業務類別放在同一層級 |
| **RAG domain 三檔案過度分散** | `rag.py` + `rag_factory.py` + `rag_eval_prompts.py` 形成緊密的 domain cluster，但無子資料夾聚合 |
| **engines/ 語義模糊** | 「引擎」可指任何東西，但目前已被專案慣例定義為「核心引擎層」（見 `src_layout.md`） |

### 目標

在不破壞現有流程的前提下，改善 `engines/` 的組織結構，讓：
- 純函數工具歸屬 `utils/`（與其他工具同層）
- RAG domain 聚合在一起（domain cohesion）
- 最小化 import 變更量

---

## 2. 核心決策

### 2.1 純函數搬移至 `utils/`

| 決策 | 理由 |
|------|------|
| `html_date_extractor.py` → `utils/` | 純函數、無類別狀態、不依賴任何 engine；是文字處理工具而非引擎 |
| `markdown_cleaner.py` → `utils/` | 純函數、無類別狀態、僅做正則 + mdformat；是文字處理工具而非引擎 |

**不搬的檔案**：

| 檔案 | 理由 |
|------|------|
| `rag.py` | 核心業務類別，有完整的生命週期管理（context manager） |
| `rag_factory.py` | 核心建置流程，含 3 個 builder 類別 |
| `website_crawler.py` | 核心業務類別，有 crawl4ai 狀態管理 |
| `webpage_image_summarizer.py` | 核心業務類別，有 VLM 呼叫狀態 |

**`rag_eval_prompts.py` 的兩難**：

- **搬的理由**：純常數、無邏輯 → 符合 utils 定義
- **不搬的理由**：只有 `rag_factory.py` 用；搬到 utils 後 RAG 評估相關的 3 個檔案分散在兩處，違反 domain cohesion
- **決定**：留在 `engines/rag/` 子資料夾，與 `rag.py`、`rag_factory.py` 同層

### 2.2 子資料夾策略

| Domain | 檔案 | 決定 |
|--------|------|------|
| **RAG** | `rag.py` + `rag_factory.py` + `rag_eval_prompts.py` | ✅ 建立 `rag/` 子資料夾（3 個檔案形成緊密 cluster，合計 ~740 行） |
| **Crawler** | `website_crawler.py` | ❌ 不建子資料夾（只有 1 個檔案、只有 1 個 consumer） |
| **Summarizer** | `webpage_image_summarizer.py` | ❌ 不建子資料夾（只有 1 個檔案、只有 1 個 consumer） |

### 2.3 `engines/` 是否改名

| 名稱 | 優點 | 缺點 | 適合度 |
|------|------|------|--------|
| `engines/`（維持） | 已沿用、團隊熟悉、git history 乾淨 | 語義模糊 | ⭐⭐⭐ |
| `processors/` | 精確描述「資料處理」語義 | 與 workflow 中的 "processing" 概念可能混淆 | ⭐⭐⭐ |
| `core/` | 通用慣例 | 太泛、與 app/ 本身語義重疊 | ⭐⭐ |
| `pipeline/` | 呼應 pipeline 流程 | RAG 和 crawler 並非同一 pipeline 的步驟 | ⭐⭐ |
| `services/` | 常見 MVC 慣例 | 暗示有狀態長期服務，不適合 batch job | ⭐⭐ |

**決定：維持 `engines/`**

理由：
1. 最小變更原則：改名涉及 12+ 處 import 變更
2. 已建立慣例：`src_layout.md` 明確記載 `engines/` 取代舊 `modules/`，是 08/09 定案
3. 專案內部語義清晰：`engines` 在此專案中已被定義為「核心引擎層」
4. ROI 不高：改名的語義收益不足以抵消 import 變更 + git blame 干擾 + 文件更新成本

---

## 3. 目標結構

```
src/
├── app/
│   ├── configs/                          # 不變
│   ├── engines/
│   │   ├── __init__.py                   # 新增（匯出頂層 symbol）
│   │   ├── rag/
│   │   │   ├── __init__.py               # 匯出 RAG / RAGBuilder / prompts
│   │   │   ├── rag.py                    # RAG 類別
│   │   │   ├── rag_factory.py            # RAGBuilder / NodePipelineBuilder / VectorStoreBuilder
│   │   │   └── rag_eval_prompts.py       # 評估 Prompt 常數
│   │   ├── website_crawler.py            # 留在 engines/ 根目錄
│   │   └── webpage_image_summarizer.py   # 留在 engines/ 根目錄
│   ├── tools/                            # 不變
│   ├── workflow/                         # 不變
│   └── agent/                            # 不變
├── utils/
│   ├── config_helper.py                  # 不變
│   ├── log_helper.py                     # 不變
│   ├── rag_helper.py                     # 不變
│   ├── html_date_extractor.py            # ← 從 engines/ 移入
│   └── markdown_cleaner.py               # ← 從 engines/ 移入
└── test/
    ├── test_html_date_extraction.py      # 更新 import
    └── ...
```

### Import 路徑變化

| 原路徑 | 新路徑 | 說明 |
|--------|--------|------|
| `app.engines.html_date_extractor` | `utils.html_date_extractor` | 搬至 utils |
| `app.engines.markdown_cleaner` | `utils.markdown_cleaner` | 搬至 utils |
| `app.engines.rag.RAG` | `app.engines.rag.RAG` | 不變（`__init__.py` 匯出） |
| `app.engines.rag_factory.RAGBuilder` | `app.engines.rag.RAGBuilder` | 由 `rag/__init__.py` 匯出 |
| `app.engines.rag_eval_prompts.*` | `app.engines.rag.rag_eval_prompts.*` | 移至 rag 子資料夾 |

### 受影響的 Consumer

| 檔案 | Import 變更 |
|------|-----------|
| `website_crawler.py` | `html_date_extractor` + `markdown_cleaner`（2 處） |
| `app/workflow/workflow.py` | `rag_factory` → `rag`（1 處） |
| `app/tools/webpage_retriever.py` | `rag_factory` → `rag`（1 處） |
| `test/test_html_date_extraction.py` | `html_date_extractor`（1 處） |
| `engines/rag_factory.py`（內部） | `rag_eval_prompts` → 相對 import（1 處） |

**合計 ~6 處 import 變更**

---

## 4. 實作 Phase

```
Phase 1：純函數搬移（獨立、低風險）
├── 移動 html_date_extractor.py → utils/
├── 移動 markdown_cleaner.py → utils/
├── 更新 website_crawler.py import
└── 更新 test/test_html_date_extraction.py import

Phase 2：RAG 子資料夾建立
├── 建立 engines/rag/ + __init__.py
├── 移動 rag.py → engines/rag/
├── 移動 rag_factory.py → engines/rag/（含 relative import 更新）
├── 移動 rag_eval_prompts.py → engines/rag/
└── 建立 engines/__init__.py（匯出頂層 symbol）

Phase 3：Consumer 更新 + 驗證
├── 更新 workflow.py import
├── 更新 tools/webpage_retriever.py import
├── uv run pytest src/test/ -v
├── CLI smoke test（rag-build / rag-query / crawl / summarize --help）
├── 更新 README.md 目錄樹
└── 更新 docs/code/ 相關文件
```

---

## 5. 驗證標準

| Phase | 驗證標準 |
|-------|---------|
| **Phase 1** | `uv run pytest` 通過；`from utils.html_date_extractor import ...` 可正常 import |
| **Phase 2** | `from app.engines.rag import RAG, RAGBuilder` 可正常 import；`rag_factory.py` 內部 import 正確 |
| **Phase 3** | 所有 pytest 通過；所有 CLI `--help` 正常輸出；`README.md` 目錄樹與實際一致 |
