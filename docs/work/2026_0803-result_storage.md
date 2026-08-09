# Result Storage (2026/08/03)

## 1. 摘要

| 日期 | 階段 |
|------|------|
| 08/03 | 規劃：參考 `run_rag_query` log 與 `workflow.py`，制定 query 結果儲存方式 |
| 08/03 | 實作完成：序列化函式 + RunManager 儲存方法 + workflow 整合 + 測試 |
| 08/03 | 驗證：單元測試 12 passed、完整回歸 40 passed、pyright 0 errors、smoke run 成功 |
| 08/03 | 規劃/實作/驗證：`run_rag_build` 新增 `save_vector_store_to_runs`，向量庫可改存至該次 run 的 `results/vector_store/` |

**結論**：本篇涵蓋兩項「結果落盤」機制：
1. **Query 結果**：解決 `run_rag_query` 的 `TODO: 制定 Query Response 的儲存方式`，改為「結構化 JSON + 每次 query 一份 Markdown」雙格式落盤。
2. **向量庫儲存**：解決 `run_rag_build` 向量庫固定寫入 `data/rag/results/` 導致測試/實驗互相覆寫，新增 `save_vector_store_to_runs` 旗標控制儲存位置。

## 2. 動機（現狀問題）

| 問題 | 描述 |
|------|------|
| **query 結果無落盤** | `run_rag_query` 只印 pass rate，結果僅存於 `terminal.log`，無法程式化分析或比對 |
| **`results.json` 語意綁定爬取** | `RunManager.save_results_as_json` / `load_latest_results_from_json` 專用於爬取結果，複用會誤導 |
| **向量庫固定位置** | `run_rag_build` 一律把向量庫寫入 config 預設位置（`data/rag/results/qdrant_db` / `milvus.db`），不同 run 互相覆寫 |
| **測試污染 artifact** | smoke 測試（`config_name="test"`）會改動 `data/rag/results/milvus.db/*`（資料 artifact） |

## 3. 最終檔案結構

### 3.1 Query 結果（`rag_query`）

```
runs/<ts>/rag_query/<run_name>/
├── results.json            # 機器可讀（source of truth，沿用 save_results_as_json）
├── results/query_1.md      # 人類可讀（每次 query 與回覆各一份）
├── results/query_2.md
├── module_config.toml
├── run_config.toml
└── terminal.log
```

### 3.2 向量庫（`rag_build`，旗標開啟時）

```
runs/<ts>/rag_build/<run_name>/
├── results/
│   └── vector_store/
│       ├── qdrant_db/   # vector_store_type = "qdrant"
│       └── milvus.db    # vector_store_type = "milvus"
├── module_config.toml   # 記錄覆寫後的實際向量庫路徑
└── terminal.log
```

## 4. 實作內容

### 4.1 `utils/rag_helper.py`（序列化函式）

- `extract_sources_list(source_nodes, max_content_length=800)`：來源節點 → `list[dict]`，欄位 `page_title / score / page_type / url / content`（與 `Rag.retrieve()` 形狀一致；`max_content_length=None` 表示不截斷）。
- `evaluation_result_to_dict(result)`：`EvaluationResult` → `{passing, score, feedback}`（`getattr` 保守取值，score 可能為 None）。
- `response_to_dict(query, response, faithfulness_result, relevancy_result, index, timestamp, max_content_length=800)`：組裝單筆 query 結果，未傳評估結果時不包含 `evaluation` 欄位。

### 4.2 `app/workflow/workflow_manager.py`（RunManager）

- 沿用 `save_results_as_json(results)` 寫 `run_path/results.json`（`ensure_ascii=False, indent=4`；簽名放寬為 `dict[str, Any]`）。
- `save_query_results_as_md(results)`：依 `results` 逐筆渲染，每次 query 與回覆寫成 `results/query_{index}.md`。
- 私有渲染器 `_render_query_result_md(meta, result)` + 格式 helper（`_format_score` / `_escape_md_cell` / `_to_blockquote`）。

### 4.3 `app/workflow/workflow.py`（整合）

- `run_rag_query` 迴圈內以 `response_to_dict` 收集 `query_results`，迴圈後組 `meta` / `summary` / `results` 三層結構，`save_results_as_json` 寫 `results.json`，並由 `save_query_results_as_md` 逐筆寫 MD。
- `summary` 含 `query_times` / 各評估 pass count 與 pass rate。

### 4.4 向量庫儲存（`save_vector_store_to_runs`）

- `app/workflow/workflow_config.py`：`RAGBuildRunConfig` 新增 `save_vector_store_to_runs: bool = False`（CLI 自動產生 `--run.save-vector-store-to-runs`）。
- `app/workflow/workflow.py`：`run_rag_build` 新增同參數；為 `True` 時在 `RAGBuilder(config).build()` 前，依 `vector_store_type` 將 `config.qdrant_db_folder_path` / `config.milvus_uri` 覆寫為 `<run_manager.results_folder_path>/vector_store/{qdrant_db | milvus.db}`。
- `app/modules/rag_factory.py`：
  - `VectorStoreBuilder.build_milvus`：本地路徑（不含 `://`）自動建立父目錄，milvus-lite 連線才不會因目錄不存在而失敗。
  - `clean_qdrant` / `clean_milvus` 簽名放寬為 `str | None`（配合測試刻意傳 `None` 驗證 no-op）。

## 5. JSON schema（重點）

```jsonc
{
  "meta": { "config_name", "run_name", "query", "query_llm_name",
            "evaluator_llm_name", "vector_store_type", "collection_name",
            "query_mode", "similarity_top_k", "hybrid_top_k", "alpha",
            "cutoff", "query_times" },
  "summary": { "query_times", "faithfulness_pass_count", "faithfulness_pass_rate",
               "relevancy_pass_count", "relevancy_pass_rate" },
  "results": [
    { "index", "timestamp", "query", "response",
      "sources": [ {"page_title","score","page_type","url","content"} ],
      "evaluation": { "faithfulness": {"passing","score","feedback"},
                      "relevancy":   {"passing","score","feedback"} } }
  ]
}
```

## 6. 檔案變更總覽

| 檔案 | 操作 | 說明 |
|------|------|------|
| `utils/rag_helper.py` | 修改 | 新增 3 個序列化函式；修正 `MarkdownDateExtractor` docstring 逸出序列警告 |
| `app/workflow/workflow_manager.py` | 修改 | 新增 2 個 save 方法與 MD 渲染 helper |
| `app/workflow/workflow.py` | 修改 | `run_rag_query` 收集與儲存 query 結果；`run_rag_build` 新增 `save_vector_store_to_runs` 旗標與路徑覆寫邏輯 |
| `app/workflow/workflow_config.py` | 修改 | `RAGBuildRunConfig` 新增 `save_vector_store_to_runs` |
| `app/modules/rag_factory.py` | 修改 | `build_milvus` 建立父目錄；clean 簽名放寬為 `str | None` |
| `test/test_main.py` | 修改 | `run_rag_build` 傳入 `save_vector_store_to_runs=True` |
| `test/test_module.py` | 修改 | `run_rag_build(config_name="test", save_vector_store_to_runs=True)` |
| `test/test_rag_refactor.py` | 修改 | 新增群組 6 `TestQueryResultStorage`（13 項濃縮為 7 項：序列化 + 儲存 + 表格跳脫 + 多 query 分檔）與群組 3b `TestRunRagBuildSaveVectorStore`（3 項，patch builder 確定性測試）（檔案已於 08/09 刪除） |

## 7. 測試與驗證

| 驗證 | 結果 |
|------|------|
| `uv run pytest test/test_rag_refactor.py -v`（群組 6 + 群組 3b）⚠️ 檔案已於 08/09 刪除 | 38 passed |
| `uv run pytest test/ --ignore=test/test_main.py --ignore=test/test_module.py` ⚠️ 同上 | 38 passed |
| `uv run pyright` | 0 errors |
| 端對端：`run_rag_build(config_name="test", save_vector_store_to_runs=True)` | `milvus.db` 落於 `runs/<ts>/rag_build/query_mode-hybrid/results/vector_store/`；`data/rag/results/` 未被改動；`module_config.toml` 記錄覆寫路徑 |
| Smoke：`uv run python cli.py rag-query-cli --run.config-name test --run.query-times 2` | 成功，2/2 pass；`results.json` 與 `results/query_{index}.md` 內容與 log 一致 |

> 註：Smoke run 會因 Milvus 一律重建而更新 `data/rag/results/milvus.db/*`（資料 artifact，非程式碼變更）。

## 8. 設計決策紀錄

| 決策 | 選擇 | 理由 |
|------|------|------|
| 檔名 | `results.json`（沿用 `save_results_as_json`） | 避免多一個專用方法；`load_latest_results_from_json` 只掃 `website_crawler` 子目錄，無衝突 |
| MD 格式 | 每次 query 與回覆各一份 `query_{index}.md` | 單一檔案易檢視單次問答，不受多次 query 混雜影響 |
| sources content | 截斷（預設 800，可參數化） | 避免 JSON 過大；全文可經由爬取階段 `results.json` 回溯 |
| MD 表格 | `\|` 跳脫、score 4 位小數 | 避免破壞 Markdown 表格渲染 |
| 內容片段 | 每行 `> ` blockquote | 多行內容正確呈現為引用區塊 |
| 旗標名稱 | `save_vector_store_to_runs`（預設 `False`） | 與 `webpages_data_use_latest_results` 對稱；預設向後相容 |
| 目錄結構 | `results/vector_store/{qdrant_db \| milvus.db}` | 與未來 `results/*.md` / `results.json` 隔離，鏡射預設結構 |
| 測試隔離 | `test_main` / `test_module` 傳入 `True` | 避免測試覆寫既有固定 `data/rag/results/` artifact |
| run 隔離 | 每次 run 因 timestamp 全新路徑、必然重建 | 符合 `_should_rebuild` 對不存在路徑的判斷 |

> 註：run-scoped 向量庫不會被 `run_rag_query` 自動沿用（它讀 toml 預設路徑），需手動傳路徑 override 或日後擴充同旗標。

## 9. 後續調整

依使用者指示修改：

1. **JSON 檔名**：移除 `save_query_results_as_json`，改用既有 `save_results_as_json`，檔名由 `query_results.json` 改為 `results.json`（簽名放寬為 `dict[str, Any]`）。
2. **MD 儲存機制**：`save_query_results_as_md` 由單一 `query_report.md` 改為「一次 query 與回覆一份檔案」（`results/query_{index}.md`）；渲染器改為 `_render_query_result_md(result)`。
3. **MD 表頭**：移除 config 表頭與標題（原 `# RAG Query Report (...)` + `> config: ...`），標題改為 `# Query #{index}: {query}`，不再記錄 config。
4. **schema 重新命名**：`results.json` 的 `meta` 欄位重新命名為 `config`（`workflow.py` 生成處、測試 fixture 同步更新）。
5. **測試整合**：原 `test/test_query_result_storage.py` 的 13 項測試濃縮為 7 項，合併至 `test/test_rag_refactor.py` 群組 6 `TestQueryResultStorage`，並刪除原測試檔。（`test_rag_refactor.py` 已於 08/09 刪除）


