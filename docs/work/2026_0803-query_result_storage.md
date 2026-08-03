# Query Result Storage (2026/08/03)

## 1. 摘要

| 日期 | 階段 |
|------|------|
| 08/03 | 規劃：參考 `run_rag_query` log 與 `workflow.py`，制定 query 結果儲存方式 |
| 08/03 | 實作完成：序列化函式 + RunManager 儲存方法 + workflow 整合 + 測試 |
| 08/03 | 驗證：單元測試 12 passed、完整回歸 40 passed、pyright 0 errors、smoke run 成功 |

**結論**：解決 `run_rag_query` 的 `TODO: 制定 Query Response 的儲存方式`。query 結果改為「結構化 JSON + 單一 Markdown report」雙格式落盤。

## 2. 動機（現狀問題）

| 問題 | 描述 |
|------|------|
| **query 結果無落盤** | `run_rag_query` 只印 pass rate，結果僅存於 `terminal.log`，無法程式化分析或比對 |
| **`results.json` 語意綁定爬取** | `RunManager.save_results_as_json` / `load_latest_results_from_json` 專用於爬取結果，複用會誤導 |

## 3. 最終檔案結構

```
runs/<ts>/rag_query/<run_name>/
├── results.json            # 機器可讀（source of truth，沿用 save_results_as_json）
├── results/query_1.md      # 人類可讀（每次 query 與回覆各一份）
├── results/query_2.md
├── module_config.toml
├── run_config.toml
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
| `app/workflow/workflow.py` | 修改 | `run_rag_query` 收集與儲存 query 結果 |
| `test/test_rag_refactor.py` | 修改 | 新增群組 6 `TestQueryResultStorage`：13 項濃縮為 7 項（序列化 + 儲存 + 表格跳脫 + 多 query 分檔） |

## 7. 測試與驗證

| 驗證 | 結果 |
|------|------|
| `uv run pytest test/test_rag_refactor.py -v`（群組 6 涵蓋 query 儲存） | 35 passed |
| `uv run pytest test/ --ignore=test/test_main.py --ignore=test/test_module.py` | 35 passed |
| `uv run pyright`（4 個改動檔案） | 0 errors |
| Smoke：`uv run python cli.py rag-query-cli --run.config-name test --run.query-times 2` | 成功，2/2 pass；`query_results.json` 與 `results/query_report.md` 內容與 log 一致 |

> 註：Smoke run 會因 Milvus 一律重建而更新 `data/rag/results/milvus.db/*`（資料 artifact，非程式碼變更）。

## 8. 設計決策紀錄

| 決策 | 選擇 | 理由 |
|------|------|------|
| 檔名 | `results.json`（沿用 `save_results_as_json`） | 避免多一個專用方法；`load_latest_results_from_json` 只掃 `website_crawler` 子目錄，無衝突 |
| MD 格式 | 每次 query 與回覆各一份 `query_{index}.md` | 單一檔案易檢視單次問答，不受多次 query 混雜影響 |
| sources content | 截斷（預設 800，可參數化） | 避免 JSON 過大；全文可經由爬取階段 `results.json` 回溯 |
| MD 表格 | `\|` 跳脫、score 4 位小數 | 避免破壞 Markdown 表格渲染 |
| 內容片段 | 每行 `> ` blockquote | 多行內容正確呈現為引用區塊 |

## 9. 後續調整（08/03）

依使用者指示修改：

1. **JSON 檔名**：移除 `save_query_results_as_json`，改用既有 `save_results_as_json`，檔名由 `query_results.json` 改為 `results.json`（簽名放寬為 `dict[str, Any]`）。
2. **MD 儲存機制**：`save_query_results_as_md` 由單一 `query_report.md` 改為「一次 query 與回覆一份檔案」（`results/query_{index}.md`）；渲染器改為 `_render_query_result_md(result)`。
3. **MD 表頭**：移除 config 表頭與標題（原 `# RAG Query Report (...)` + `> config: ...`），標題改為 `# Query #{index}: {query}`，不再記錄 config。
4. **schema 重新命名**：`results.json` 的 `meta` 欄位重新命名為 `config`（`workflow.py` 生成處、測試 fixture 同步更新）。
5. **測試整合**：原 `test/test_query_result_storage.py` 的 13 項測試濃縮為 7 項，合併至 `test/test_rag_refactor.py` 群組 6 `TestQueryResultStorage`，並刪除原測試檔。
