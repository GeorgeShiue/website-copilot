# RAG Refactor (2026/08/02)

## 1. 摘要

| 日期 | 階段 |
|------|------|
| 07/28 | 詳細規劃：現狀分析、4 Phase、測試矩陣、風險緩解 |
| 07/30 | 規劃調整：確立 `Rag`(runtime) + `RagBuilder`(build) 雙類別架構 |
| 08/02 | 實際完成：程式碼變更、SMOKE 驗證、注意事項 |
| 08/02 | 命名決策：RAG 家族類別改全大寫（`RAG*`）、模組檔名維持小寫 |

**結論**：規劃的 4 個 Phase（NodePipelineBuilder → VectorStoreBuilder → RAGBuilder Facade → RAG 輕量化）已全部完成，且實作比規劃更進一步。

---

## 2. 動機（現狀問題）

| 問題 | 描述 | 影響端 |
|------|------|--------|
| **God Class** | `Rag` 管理 7+ 職責（節點、向量儲存、索引、檢索器、查詢引擎、評估、資源清理） | 所有呼叫端 |
| **建構序列重複** | `workflow.py`（2 處）與 `webpage_retriever.py`（1 處）手動重複相同建構步驟 | 3 個呼叫點 |
| **測試需要完整基礎設施** | 需完整 Milvus/Qdrant 才能測試任一環節 | 測試困難 |
| **單一檔案過大** | `rag.py` ~650 行，載入 20+ 第三方匯入，混合 build 與 runtime | 可維護性 |

---

## 3. 最終目標架構

```
rag.py (runtime)                    rag_factory.py (build)
┌──────────────────────────┐        ┌──────────────────────────────────────┐
│ class Rag:                │        │ class NodePipelineBuilder:           │
│   __init__(path)          │        │   build() → list[BaseNode]          │
│   close() / context mgr   │        │   _build_file_metadata()  (取代舊    │
│   query() / retrieve()    │        │     Rag._file_metadata)             │
│   evaluate()              │        │ class VectorStoreBuilder:            │
│   _load_results_json()    │        │   build_qdrant / build_milvus       │
│   _log_sources()          │◄───────┤   clean_qdrant / clean_milvus       │
│   _log_evaluation_result()│ 注入    │ class RagBuilder (Facade):           │
└──────────────────────────┘ 狀態    │   build() → Rag                     │
                                    │   build_to_retriever() → Rag        │
                                    │   build_reusable(rag, force) → bool │
                                    │   build_evaluators(rag)             │
                                    │   build_nodes / build_vector_store  │
                                    │   build_index / load_index          │
                                    │   build_retriever / build_query_engine
                                    └──────────────────────────────────────┘
         注入的狀態欄位：nodes / vector_store / index / retriever /
         query_engine / evaluators（由 RagBuilder 填寫）
                 ┌───────────────────────────────────────────────┐
                 │ utils/rag_helper.py（共用工具）                  │
                 │   build_filters() / create_llm() /            │
                 │   LLM_API_KEY_ENV_VARS                        │
                 └───────────────────────────────────────────────┘
                 ┌───────────────────────────────────────────────┐
                 │ app/modules/rag_eval_prompts.py（評估模板）     │
                 │   FAITHFULNESS_* / RELEVANCY_* 4 個模板       │
                 └───────────────────────────────────────────────┘
```

**關鍵原則**：單向依賴 `rag_factory.py → rag.py`；`rag.py` 不回頭 import `rag_factory.py`。

---

## 4. 實作內容

### 4.1 `Rag` 類別瘦身（僅保留 runtime）

- **刪除**：所有 `build_*` / `clean_*` / `load_index` / `override_init_config` / `_set_embed_model`；static `build_filters` / `create_llm`；`LLM_API_KEY_ENV_VARS` 常數；4 個評估模板。
- **保留**：`query` / `retrieve` / `evaluate` / `close` / context manager / `_load_results_json` / logging helpers。
- **新增** `self.evaluators` 屬性；`close()` 中同步清空。
- `evaluate()` 改為**注入模式**：由 Builder 注入 evaluator，未注入時拋 `RuntimeError("Evaluators have not been built, cannot evaluate")`。

### 4.2 共用函式搬移至 `utils/rag_helper.py`

- `build_filters()`、`create_llm()`、`LLM_API_KEY_ENV_VARS` 從 `rag.py` 搬入。
- `create_llm(llm_name, usage)` 支援 `query_engine` / `evaluator` 兩種用途，依用途讀取不同 API key 環境變數。

### 4.3 新增 `app/modules/rag_eval_prompts.py`

- 集中管理 4 個評估模板：`FAITHFULNESS_EVAL/REFINE`、`RELEVANCY_EVAL/REFINE`。
- `rag_factory.py` 的 `build_evaluators()` 由此 import，`rag.py` 不再需要。

### 4.4 `RagBuilder` 擴充

- **`build_reusable(rag, force_rebuild=False) -> bool`**：統一編排「重建或載入」流程並回傳是否重建。
- **`_should_rebuild(force_rebuild)`** 決策：

  | 條件 | 是否重建 |
  |------|---------|
  | `vector_store_type == "milvus"` | 一律重建（現有設計限制） |
  | 其他 store + `force_rebuild=True` | 重建 |
  | 其他 store + store 路徑不存在 | 重建 |
  | 其他 store + 路徑存在 | 載入既有 index |

- **`build_evaluators(rag)`**：依 `config.evaluator_llm_name` 建立 Faithfulness / Relevancy evaluator 並注入。

### 4.5 Config 分離 query / evaluator LLM

`llm_name` 拆分為兩個欄位：

| 欄位 | 預設值 | 用途 |
|------|--------|------|
| `query_llm_name` | `gemini-3.1-flash-lite` | query engine 使用 |
| `evaluator_llm_name` | `gpt-5.4` | evaluator 使用 |

- 同步更新 `rag_config.py` 驗證邏輯與四個 `configs/rag/*.toml`。

---

## 5. 檔案變更總覽

| 檔案 | 操作 | 說明 |
|------|------|------|
| `app/modules/rag.py` | 修改 | 刪除建構方法與共用函式，僅保留 runtime；新增 `evaluators` 屬性 |
| `app/modules/rag_factory.py` | 修改 | 新增 `build_reusable` / `_should_rebuild` / `build_evaluators`；改用 `query_llm_name` |
| `app/modules/rag_eval_prompts.py` | **新增** | 4 個評估 Prompt 模板 |
| `utils/rag_helper.py` | 修改 | 新增 `build_filters` / `create_llm` / `LLM_API_KEY_ENV_VARS` |
| `app/configs/rag_config.py` | 修改 | `llm_name` → `query_llm_name` + `evaluator_llm_name` |
| `configs/rag/*.toml` | 修改 | default / milvus / qdrant / test 同步改名 |
| `configs/rag/dense.toml`、`hybrid.toml` | 刪除 | 不再使用 |
| `app/workflow/workflow.py` | 修改 | 兩個呼叫端改用 `RagBuilder` |
| `app/tools/webpage_retriever.py` | 修改 | 改用 `RagBuilder(config).build_to_retriever()` |
| `test/test_rag_refactor.py` | 修改 | 新增群組 4（`build_reusable`）、群組 5（evaluator）測試（檔案已於 08/09 刪除） |
| `docs/code/modules/data_retrieve.md` | 修改 | `evaluate()` 簽名與模板位置更新 |

---

## 6. 呼叫端改寫

**`run_rag_build`（workflow.py）**：

```python
rag = RagBuilder(config).build()
with rag, save_logging_file(...), log_run_time(...):
    rag.query(config.query, log_sources=True)
```

**`run_rag_query`（workflow.py）** — 重建/載入決策收斂到 Builder：

```python
rag = Rag(webpages_data_folder_path=config.webpages_data_folder_path)
builder = RagBuilder(config)
with rag, save_logging_file(...), log_run_time(...):
    rebuild = builder.build_reusable(rag, force_rebuild=force_rebuild)
    builder.build_evaluators(rag)
    # ... query + evaluate loop ...
    if rebuild:
        save_module_config_as_toml(config, module_config_folder_path / "module_config.toml")
```

**`webpage_retriever.py`**：

```python
rag = RagBuilder(config).build_to_retriever()
```

---

## 7. 測試與驗證

### 7.1 測試結構（`test/test_rag_refactor.py`，依元件職責分群組）——⚠️ 檔案已於 08/09 刪除，本節僅保留作歷史紀錄

| 群組 | 測試類別 | 涵蓋 |
|------|---------|------|
| 1 | `TestNodePipelineBuilder` | 空/單檔、chunk_size、heading merge、圖片提取、不存在的資料夾 |
| 2 | `TestVectorStoreBuilder` | embedding 維度解析、hybrid ranker 參數、build/clean、不支援型別 |
| 3 | `TestRagBuilder` | 完整建構、`build_to_retriever`、context manager |
| 4 | `TestRagBuilderReusable` | 路徑不存在→重建、路徑存在→載入、`force_rebuild` 覆寫、Milvus 一律重建 |
| 5 | `TestRagBuilderEvaluators` | evaluator 注入、未注入時 `evaluate()` 拋錯、使用注入實例 |

> 註：07/28 規劃的獨立測試檔（`test_node_pipeline_builder.py` 等）未建立，測試統一集中在 `test_rag_refactor.py`（該檔已於 08/09 刪除）。

### 7.2 驗證結果（SMOKE 測試，Exit Code 0）

- ✅ `Rag` 已無 `create_llm` / `build_filters` static。
- ✅ `rag.py` 已無 `LLM_API_KEY_ENV_VARS`。
- ✅ `rag_helper` 提供 `build_filters` / `create_llm` / `LLM_API_KEY_ENV_VARS`。
- ✅ `RagBuilder` 正常 import，且與 `rag_helper` 共用同一實作（`rf.create_llm is rh.create_llm`）。
- ✅ `rag.py` 僅剩 runtime 方法。

### 7.3 建議回歸命令

```bash
# ⚠️ test_rag_refactor.py 已於 08/09 刪除，前兩條命令僅保留作歷史紀錄
uv run pytest test/test_rag_refactor.py -v
uv run pytest test/ -v --ignore=test/test_main.py --ignore=test/test_module.py
uv run pyright app/modules/rag.py app/modules/rag_factory.py utils/rag_helper.py
```

---

## 8. 與先前規劃的對照

| 規劃內容 | 0728 規劃 | 0730 規劃 | 0802 實際完成 |
|---------|-----------|-----------|--------------|
| 建構類別放置位置 | `rag_refactor.py`（新檔） | `rag_factory.py` | ✅ `rag_factory.py`（既有檔擴充） |
| `build_filters` / `create_llm` 去向 | 移至 `RagRetriever` 或保留 | 保留在 `Rag` 當 static | **改放 `utils/rag_helper.py`** |
| 評估模板去向 | 留在 rag.py | 留在 rag.py | **抽出為 `rag_eval_prompts.py`** |
| Evaluator 建立 | 在 `evaluate()` 內 | 在 `evaluate()` 內 | **移至 `RagBuilder.build_evaluators()` 注入** |
| 重建/載入決策 | `build_to_index()` 方案 A | Builder 個別步驟 | **新增 `build_reusable()` / `_should_rebuild()`** |
| query / evaluator LLM | 單一 `llm_name` | 單一 `llm_name` | **拆分 `query_llm_name` / `evaluator_llm_name`** |
| 過渡期委派橋接 | 保留 `Rag.build_*` 委派 | — | **直接刪除**（一次性改寫呼叫端） |

---

## 9. 注意事項與開放問題

1. **`build()` / `build_to_retriever()` 不會建立 evaluator**：僅 `run_rag_query` 呼叫 `build_evaluators(rag)`。其他呼叫端需要 `evaluate()` 時必須自行注入，否則拋 `RuntimeError`。
2. **`data/rag/results/milvus.db/...` 被納入暫存**：parquet / manifest / schema 等執行產物被 `git add`，建議加入 `.gitignore`。
3. **Milvus 一律重建**：`_should_rebuild` 中 Milvus 分支固定回傳 `True`，現階段無法載入既有 index（已知限制）。
4. **`run_rag_query` 的 TODO**：仍標註「改用 regas 或 deepeval 評估」與「制定 Query Response 的儲存方式」。
5. **07/28 規劃的 Minor 問題（#11–#15）** 暫緩，未納入本次範圍。

---

## 10. 後續建議

- 決定 `milvus.db` 資料檔是否加入 `.gitignore` 並 `git reset` 排除。
- 完成 `run_rag_query` 的評估框架替換（regas / deepeval）與 Response 儲存設計。
- 若需支援 Milvus 載入既有 index，重新設計 `_should_rebuild` 的 Milvus 分支。

---

## 11. RAG 家族命名決策（已執行：類別全大寫、檔名小寫）

### 11.1 背景與最終決策

RAG 為縮寫（Retrieval-Augmented Generation），曾評估將**類別**與**模組檔名**改為全大寫。最終**實際執行「類別符號全大寫 `RAG*`、模組檔名維持小寫」**的雙軌方案：只改類別符號，不改檔名。

### 11.2 執行後現況

| 項目 | 現況 | 考量 |
|------|------|------|
| 模組檔名 | `rag.py` / `rag_config.py` / `rag_factory.py` / `rag_eval_prompts.py`（維持全小寫） | PEP 8 規定 module 名稱應全小寫；macOS 預設 APFS case-insensitive，避免 `RAG.py`/`rag.py` 碰撞與 Git case-only rename 風險 |
| 類別名稱 | `RAG`、`RAGConfig`、`RAGBuilder`、`RAGBuildRunConfig`、`RAGQueryRunConfig`、`RAGConfigCLI`（全大寫） | 縮寫慣例全大寫；`RAG*` 家族在程式碼／測試／docs 全面一致 |
| logger name | `utils/log_helper.py` L76 維持 `app.modules.rag` | 對應小寫檔名，log 過濾正常 |

### 11.3 執行影響範圍

| 層級 | 狀態 | 說明 |
|------|------|------|
| 類別符號（9 個 .py） | ✅ 已執行 | `rag.py`、`rag_factory.py`、`rag_config.py`、`webpage_retriever.py`、`workflow.py`、`workflow_config.py`、`cli.py`、`main.py`、`test/test_rag_refactor.py`（檔案已於 08/09 刪除） |
| 模組檔名（4 個 .py） | ❌ 未執行（維持小寫） | 避免 macOS case-insensitive 碰撞與 Git case-only rename；`utils/log_helper.py` L76 logger name 不變 |
| 文件 | ✅ 已同步 | `README.md`、`docs/code/modules/*`、`docs/code/runs/*` 已更新為 `RAG*` 命名 |

### 11.4 決策理由

1. **類別符號全大寫**：RAG 為縮寫，`RAG` / `RAGBuilder` / `RAGConfig` 等符合縮寫慣例且家族一致；目前 ruff 未啟用 pep8-naming（N801），全大寫不會被 lint 擋。
2. **模組檔名維持小寫**：符合 PEP 8 module 命名（全小寫）；macOS 預設 APFS case-insensitive，`RAG.py`/`rag.py` 有碰撞與 Git case-only rename 風險。
3. **logger name 不變**：`app.modules.rag` 對應小寫檔名，log 過濾不失效。

### 11.5 驗證與未來方向

- 讀檔確認（08/02）：類別已為全大寫 `RAG*`（`RAG` / `RAGBuilder` / `RAGConfig` / `RAGConfigCLI` / `RAGBuildRunConfig` / `RAGQueryRunConfig`），模組檔名與 logger name 仍為小寫。
- 若未來要連模組檔名一併改為全大寫：須一次改齊 import 端，並同步更新 `utils/log_helper.py` L76 的 logger name 與 README/docs。
