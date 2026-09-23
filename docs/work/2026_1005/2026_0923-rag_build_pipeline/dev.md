# Implementation Log

> 對應規劃文件：[plan.md](./plan.md)

---

## 起點：確認問題是否存在

在動手前先各自查證，確認每一點都是真實、可證明的問題，而不是臆測：

- **第 1 點**：追蹤 `run_rag_build()` → `create_rag()` → `RAGBuilder.build_reusable()`（舊名），docstring 明寫「最後一律 `build_retriever` → `build_query_engine`」，確認為真。
- **第 2 點**：追蹤 `create_rag()` 的 `save=True` 分支如何覆寫 `milvus_uri`，再追蹤 `RunManager.__init__` 的 `time.strftime(...)`，證明該路徑每次呼叫必為全新、不存在的路徑，`_should_rebuild()` 因此恆為 `True`，與傳入的 `force_rebuild` 值無關。
- **第 3 點**：比對 `create_run_context()` 與 `create_rag()` 內部兩處 `RunManager.for_run(...)` 對 `run_name` 的計算方式，確認在 `run_name_use_config_name=False`（預設）時邏輯不一致。
- **第 6 點**：追蹤 `webpage_retriever.py::_retrieve()` 實際呼叫 `rag.retrieve()` 而非 `rag.query()`，並 grep 全專案確認 `rag.query_engine` 只有 `RAG.query()` 這一個消費者、且只有 `run_rag_query()` 會呼叫它。

---

## 第 2 點：是否該保留 `force_rebuild` 的討論

第 2 點原本的規劃方向是「讓 `save` 只控制落盤位置，不影響是否重建，但仍保留 `force_rebuild` 讓呼叫端決定」。使用者提出更明確的立場：`run_rag_build()` 本身的語意就是「已經確定要重建」（呼叫它就代表想要一份新的向量庫），因此**預設永遠重建才是正確行為**，`force_rebuild` 參數應該整個從 `run_rag_build()` 移除，而非只是調整預設值。

**決策過程**：確認這個立場不會破壞既有需求後採用——`main.py` 唯一需要「強制重建持久化路徑」的正式流程場景，改成在 `run_rag_build()` 內部固定傳 `force_rebuild=True` 給 `create_rag()` 即可滿足，不需要對外暴露這個參數；`create_rag()`／`RAGBuilder`／`run_rag_query()` 的 `force_rebuild` 機制完全不動，因為 `run_rag_query()` 需要「有既有向量庫就重用」的語意，且 CLI 從未對 `run_rag_build()` 開放過 `force_rebuild`（`RAGBuildRunConfig` 本來就沒有這個欄位，只有 `RAGQueryRunConfig` 有），移除參數對 CLI 介面零影響。

同步移除三個呼叫端（`main.py`、`test_main.py`、`test_module.py`）原本顯式傳入、現在已成為非法參數的 `force_rebuild=True`。

---

## 第 5 點：`overwrite` 參數移除前的實測驗證

使用者要求先用實測而非只憑原始碼推論來驗證第 5 點的結論，並特別指出「先前測試直接 overwrite 會有問題因此實作 `clean_vector_store()`」——要求確認移除 `overwrite` 參數是否會重現當初的問題。

**驗證過程**：

1. 讀 `llama_index.vector_stores.milvus.base.MilvusVectorStore.__init__` 原始碼，確認 `overwrite` 只在「client 連上的既有 collection 存在」時才會觸發 `drop_collection`。
2. 寫腳本用真實 `VectorStoreBuilder.build()`（含 hybrid sparse embedding、真實 OpenAI embedding、真實寫入 3 筆資料）測試：
   - 不 clean，直接對已有資料的 collection `overwrite=True` 重建 + 插入——**沒有出錯**。
   - `clean_vector_store()`（整檔刪除）之後用 `overwrite=False`（而非 `True`）重建 + 插入——**也沒有出錯**。
3. **無法重現**當初促成 `clean_vector_store()` 的失敗案例——可能是特定 schema/維度變更或程序異常中止留下鎖定檔案等更少見的情境，這次測試沒有覆蓋到。因此**不移除 `clean_vector_store()`**，只移除已被原始碼邏輯證明多餘的 `overwrite` 參數（`clean_vector_store()` 執行後，collection 必然不存在，`overwrite` 值不影響結果，這點不需要依賴猜測，是可證明的邏輯）。

移除參數後，另外對正式程式碼路徑（而非獨立腳本）做了一次煙霧測試：`RAGBuilder.build_to_vector_store()` 分別測「全新建立」「檔案已存在時 force_rebuild 重建」「load-existing 重用既有 collection」三種情境，皆正常運作，`RAG Build Stats` 輸出符合預期。

---

## 第 6 點：`build_to_retriever()` 的插入位置

`build_to_query_engine()`（第 1 點已從 `build_reusable` 重新命名而來）原本是 `build_to_vector_store()` → `build_retriever()` → `build_query_engine()` 三段直接串接。新增 `build_to_retriever()` 時選擇讓它疊在 `build_to_vector_store()` 之上、`build_to_query_engine()` 再疊在 `build_to_retriever()` 之上（而非三個方法平行各自呼叫底層步驟），避免 `build_to_vector_store()` + `build_retriever()` 這兩步被寫兩次。

`RAGRegistry.get()` 是全專案唯一呼叫 `build_to_query_engine()`（現在改呼叫 `build_to_retriever()`）的地方，改動後同步發現 `src/test/dev/test_rag_tools.py::TestGetCacheMiss::test_builds_rag_on_first_call` 的 mock 斷言還停留在更早一次重構前的舊方法名 `build_reusable`（早於本次工作階段），一併修正為 `build_to_retriever`。

---

## Final Summary

### 變更檔案總表

| 檔案 | 變更內容 |
|------|---------|
| `src/app/engines/rag/rag_factory.py` | `VectorStoreBuilder.build()`／`RAGBuilder.build_vector_store()` 移除 `overwrite` 參數（固定 `overwrite=False`）；`build_to_vector_store()`／`build_to_query_engine()` 重新命名與重構（`build_reusable` → 拆出 `build_to_vector_store`）；新增 `build_to_retriever()`；`create_rag()` 新增 `run_manager: RunManager \| None`、`config: RAGConfig \| None` 參數，`build_query_engine: bool` 參數保留 |
| `src/app/workflow/workflow.py` | `run_rag_build()` 移除 `force_rebuild` 參數（固定傳 `force_rebuild=True`）；`run_rag_build()`／`run_rag_query()` 改傳 `config=config`／`run_manager=run_manager` 給 `create_rag()`，不再各自重複 `RAGConfig.from_toml()` |
| `src/app/tools/rag_registry.py` | `RAGRegistry.get()` 改呼叫 `build_to_retriever()`（原 `build_to_query_engine()`） |
| `src/main.py` | 移除 `run_rag_build(force_rebuild=True, ...)` 中已失效的 `force_rebuild=True` |
| `src/test/test_main.py`、`src/test/test_module.py` | 同步移除已移除的 `force_rebuild=True` 關鍵字參數 |
| `src/test/dev/test_rag_tools.py` | `TestGetCacheMiss` mock 斷言方法名修正為 `build_to_retriever`（順便修正早於本次工作階段就已過時的 `build_reusable`） |
| `docs/work/todo.md` | 「優化 rag 建置流程」六項全數勾選並記錄簡短結論 |

### 測試結果

依序執行：

1. `ruff check src` — 全過。
2. `pyright`（需指定 venv 的 python 才能正確解析套件，否則會出現一大批與本次改動無關的 import 解析錯誤）— 剩餘 4 個既有錯誤全在未改動的 `test_webpage_markdown_cleaner.py`。
3. `pytest src/test/dev/test_rag_tools.py -v` — 33 passed。
4. `pytest src/test/dev/test_run_rag_build_publish.py -v` — 3 passed。
5. `pytest src/test -m "not slow" -v` — **195 passed**，1 個既有無關失敗（`test_webpage_markdown_cleaner.py::test_save_generated_exclude_words`，`KeyError: 'Footer text'`，發生在 `run_persistence.py`，本次完全沒有改動這兩個檔案）。
6. `pytest src/test/test_module.py::test_rag -m slow -v`（真實爬蟲已完成的前提下，真實跑一次 `run_rag_build()` 完整重建 nculab 向量庫）— passed（33.77s）。產物正確落在單一 `runs/{timestamp}/rag_build/nculab/...` 資料夾（驗證第 3 點），`RAG Build Stats` 只到 index 層級、無 retriever/query_engine（驗證第 1 點）。
7. `pytest src/test/test_main.py -m slow -v`（完整 crawler → image summarizer → rag build → agent query）— passed（3m55s）。agent 透過 `webpage_retriever` 工具查詢時觸發 `RAGRegistry` cache miss，log 顯示只建到「Index nodes: loaded from existing vector store」，**沒有**印出 query_engine 相關設定（驗證第 6 點），agent 最終給出正確、附來源的回答。

### 已知限制 / 未處理事項

| 類別 | 說明 |
|------|------|
| **`clean_vector_store()` 保留但未釐清根本原因** | 無法重現當初「只靠 `overwrite=True` 不整檔刪除」失敗的案例，因此保留 `clean_vector_store()` 作為安全網，但沒有實際確認過它防的是哪一種具體失敗模式；若之後想進一步簡化，需要先補上能重現該失敗的情境（例如 embedding 維度變更、程序異常中止留下鎖定檔案）。 |
| **驗證過程產生的真實資料** | 第 6、7 步驟因為真實跑 `run_rag_build()`／主流程，對 `data/rag/nculab/milvus.db`（持久化路徑）做了實際重建/寫入，並在 `runs/` 底下留下新的執行紀錄資料夾——這是正常產物，未特別清理。 |
| **`todo.md` 下一層「伺服器啟動獨立於 main workflow 之外」未處理** | 屬於「流程優化」分類下一個獨立項目，不在本次「優化 rag 建置流程」範圍內。 |
