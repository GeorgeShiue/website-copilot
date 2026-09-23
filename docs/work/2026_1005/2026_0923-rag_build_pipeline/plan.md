# RAG 建置流程優化計畫（nculab）

## Context

從 `docs/work/todo.md`「優化 rag 建置流程」項目出發，起點是檢查 `run_rag_build()` 過程是否會建立 query_engine（結果：會，且不需要）。之後沿著同一條「建置流程」逐一往下追，陸續發現並修正五個相關問題，最終涵蓋 todo.md 該分類底下全部六項：

1. **`run_rag_build()` 不建立 query_engine**：只需要向量庫/index，不需要 retriever／query engine。
2. **`save` 與「是否重建向量庫」耦合**：`save=True`（預設）時，向量庫目的地路徑必然是全新的、從未存在過的 run 路徑，導致 `force_rebuild` 參數形同虛設；`run_rag_build()` 因此移除 `force_rebuild` 參數，改為一律重建。
3. **`create_rag()` 支援傳入 `run_manager`**：`run_rag_build()` 與 `create_rag()` 原本各自獨立建立一個 `RunManager`，兩者對 `run_name` 的計算邏輯不一致，導致產物（log／config／milvus.db）可能落在不同的 run 資料夾。
4. **`create_rag()` 支援傳入已建立的 `RAGConfig`**：`run_rag_build()`／`run_rag_query()` 都先自行解析一次 `RAGConfig`，`create_rag()` 內部又重新解析一次，屬於與第 3 點同類型的重複建構問題。
5. **`clean_vector_store()` 與 `build_vector_store(overwrite=True)` 重複**：重建流程先整檔刪除 milvus.db，再用 `overwrite=True` 建立 `MilvusVectorStore`——但整檔刪除後 collection 必然不存在，`overwrite` 參數已無實際作用。
6. **`webpage retriever tool` 不建立 query_engine**：`RAGRegistry.get()`（server 端唯一使用 RAG 的入口）建到 query_engine 層級，但 `webpage_retriever` 工具實際只呼叫 `rag.retrieve()`，全程用不到 `query_engine`。

六項皆已完成。實際執行過程、決策修正、實測驗證記錄於 [dev.md](./dev.md)。

---

## 1. `run_rag_build()` 不建立 query_engine

### 問題

`run_rag_build()` → `create_rag()` → `RAGBuilder.build_reusable()`（舊名）最後一律呼叫 `build_retriever()` + `build_query_engine()`，即使只是要建置/更新向量庫，也會多做一次 `create_llm(query_llm_name)` 與 `RetrieverQueryEngine` 的建置，完全用不到。

### 設計

- `RAGBuilder` 拆分出 `build_to_vector_store()`（只建到 index 層級），`build_to_query_engine()` 改為疊在其上（`build_to_vector_store` → `build_retriever` → `build_query_engine`）。
- `create_rag()` 新增 `build_query_engine: bool = True` 參數，`False` 時只呼叫 `build_to_vector_store()`。
- `run_rag_build()` 呼叫 `create_rag(..., build_query_engine=False, ...)`；`run_rag_query()` 維持預設 `True`（不變）。

### 驗證方式

- `pyright` 型別檢查。
- `test_run_rag_build_publish.py`（mock `create_rag`，確認呼叫參數與 save/publish 流程不受影響）。

---

## 2. `save` 與「是否重建向量庫」耦合

### 問題

`create_rag()` 的 `_should_rebuild(force_rebuild)` 邏輯：`force_rebuild=True` 或目的地路徑不存在時才重建。但 `save=True`（`run_rag_build()` 預設值）會讓 `create_rag()` 把 `milvus_uri` 換成本次 run 專屬的全新路徑（`RunManager` 每次以 timestamp 建立新資料夾），該路徑必然不存在——於是無論外部傳入的 `force_rebuild` 是 `True` 還是 `False`，實際都會重建。`force_rebuild` 在 `save=True` 這條（預設）路徑上形同虛設，只有 `save=False`（如 `main.py` 的正式流程）時才是唯一真正決定是否重建的開關。

### 設計

- 確認 `run_rag_build()` 的呼叫語意本來就是「已經確定要重建」（唯一例外 `main.py` 用 `save=False, force_rebuild=True` 顯式強制重建持久化路徑），因此讓 `run_rag_build()` **一律重建**，不再對外開放 `force_rebuild` 參數：
  - `run_rag_build()` 簽名移除 `force_rebuild`，呼叫 `create_rag(..., force_rebuild=True, ...)` 固定傳 `True`。
  - `save` 只保留「向量庫／module_config／run_config 是否落盤到 `runs/`」的職責，不再間接影響是否重建。
- `create_rag()`／`RAGBuilder`／`run_rag_query()` 不改動：`force_rebuild` 繼續是 `run_rag_query()` 的「有既有向量庫就重用」語意的唯一入口。
- 同步移除三個呼叫端（`main.py`、`test_main.py`、`test_module.py`）多餘的 `force_rebuild=True` 關鍵字參數。

### 驗證方式

- `pyright`。
- 三個呼叫端語法檢查 + grep 確認無殘留的 `force_rebuild` 傳遞。
- 實測 `pytest src/test/test_module.py::test_rag -m slow`（真實跑一次 `run_rag_build()`）。

---

## 3. `create_rag()` 支援傳入 `run_manager`

### 問題

`run_rag_build()`（經 `create_run_context()`）與 `create_rag()` 內部各自獨立呼叫 `RunManager.for_run(module="rag_build", site_id=..., run_name=...)`。兩處對 `run_name` 的計算方式不一致：`run_rag_build()` 用 `config.config_name if run_name_use_config_name else config.run_name`，`create_rag()` 內部永遠用 `config.config_name`。當 `run_name_use_config_name=False`（預設）且 `config.run_name != config.config_name` 時，兩個 `RunManager` 會落在不同資料夾；即使 `run_name` 剛好相同，`RunManager.__init__` 每次都用 `time.strftime(...)` 產生新的頂層 timestamp 資料夾，跨秒執行也會落在不同目錄。結果是 log／module_config.toml／run_config.toml 存在第一個 run 資料夾，實際建出的 `milvus.db` 卻存在第二個不同的 run 資料夾。

### 設計

- `create_rag()` 的 `save: bool` 參數改為 `run_manager: RunManager | None = None`：傳入時直接用 `run_manager.results_folder_path` 決定 `milvus_uri`，不再自行建立 `RunManager`。
- `run_rag_build()` 改傳入自己已建立的 `run_manager`（`save=False` 時本來就是 `None`，行為自然對齊，不需要額外判斷）。
- `run_rag_query()` 不傳 `run_manager`，維持使用 config 的預設持久化路徑，行為不變。

### 驗證方式

- `pyright`。
- 實測 `pytest src/test/test_module.py::test_rag -m slow`：確認 log／module_config.toml／run_config.toml／milvus.db 全部落在同一個 run 資料夾。

---

## 4. `create_rag()` 支援傳入已建立的 `RAGConfig`

### 問題

與第 3 點同類型：`run_rag_build()`／`run_rag_query()` 都先自行 `RAGConfig.from_toml(config_name, **config_overrides)` 解析一次（供 `create_run_context()` 取得 `site_id`/`run_name`），`create_rag()` 內部又用完全相同的 `config_name`/`config_overrides` 重新解析一次。`run_rag_query()` 額外用外層的 `config` 建 evaluators（`RAGBuilder(config).build_evaluators(...)`），與內部建 RAG 用的另一份 `config` 物件是兩個獨立實例。目前尚未觀察到像第 3 點那樣的實際不一致 bug（兩邊 `config_name`/`overrides` 完全相同），但屬於同一種「重複建構、未來容易因為某處加了非純函式邏輯而分裂」的技術債。

### 設計

- `create_rag()` 新增 `config: RAGConfig | None = None` 參數；`None` 時才用 `config_name`/`**config_overrides` 解析，傳入時直接沿用（忽略 `config_name`/`config_overrides`）。
- `run_rag_build()`／`run_rag_query()` 改傳 `config=config`（呼叫端已解析好的物件），不再重複傳 `config_name`/`**config_overrides`。
- `run_rag_query()` 的 evaluators 與實際建 RAG 現在保證用同一個 `config` 實例。

### 驗證方式

- `pyright`。
- `pytest src/test/dev/test_run_rag_build_publish.py`（mock 層級不受影響）。

---

## 5. `clean_vector_store()` 與 `build_vector_store(overwrite=True)` 重複

### 問題

重建分支流程：`clean_vector_store()`（整檔刪除 `milvus_uri`）→ `build_vector_store()`（預設 `overwrite=True`，建立 `MilvusVectorStore`）。`MilvusVectorStore.__init__` 原始碼顯示 `overwrite` 只在 `collection_name in self.client.list_collections()` 為真時才會 `drop_collection`——但整檔刪除後，新建立的 client 上該 collection 必然不存在，因此 `overwrite=True`／`False` 在這個時間點結果保證相同（可從原始碼邏輯直接證明，不只是猜測）。歷史上曾經「只靠 `overwrite=True`（不整檔刪除）」出過問題才改用 `clean_vector_store()`；但無法重現該失敗案例，因此不移除 `clean_vector_store()` 本身，只移除已確認多餘的 `overwrite` 參數。

### 設計

- `VectorStoreBuilder.build()` 移除 `overwrite` 參數，`MilvusVectorStore(..., overwrite=False)` 固定寫死，並加註解說明「若要重建，呼叫端須先以 `clean_milvus()` 整檔刪除」。
- `RAGBuilder.build_vector_store()` 同步移除 `overwrite` 參數；`build_to_vector_store()` 的 load-existing 分支呼叫點同步更新。
- 不動 `clean_vector_store()`（保留作為重建前唯一的清空機制）。

### 驗證方式

- 用真實 `VectorStoreBuilder.build()`（含 hybrid sparse embedding、真實 OpenAI embedding）手動驗證三種情境：
  1. 不 clean，直接對已有資料的 collection `overwrite=True` 重建——不出錯。
  2. `clean_vector_store()` 之後 `overwrite=False` 重建——不出錯。
  3. （正式程式碼路徑煙霧測試）全新建立 / 檔案已存在時 rebuild / load-existing 重用既有 collection 三種路徑皆正常。
- `pytest src/test/test_module.py::test_rag -m slow`。

---

## 6. `webpage retriever tool` 不建立 query_engine

### 問題

`webpage_retriever` 工具（`_retrieve()`）呼叫 `rag.retrieve()`，內部只用 `rag.retriever`（`VectorIndexRetriever`），從未碰 `rag.query_engine`。`rag.query_engine` 全專案只有 `RAG.query()` 會用到，而 `RAG.query()` 只有 `run_rag_query()` 呼叫（經 `create_rag()` 自建的 RAG，不經 `RAGRegistry`）。但 `RAGRegistry.get()`（server 端唯一使用 RAG 的入口）cache miss 時呼叫的是 `build_to_query_engine()`，多建了一個永遠用不到的 `query_engine`（含一個閒置的 LLM client）。

### 設計

- `RAGBuilder` 新增 `build_to_retriever()`：`build_to_vector_store()` + `build_retriever()`，不含 `build_query_engine()`。
- `build_to_query_engine()` 重構成疊在 `build_to_retriever()` 之上，避免重複程式碼。
- `RAGRegistry.get()` 改呼叫 `build_to_retriever()`。
- `create_rag()` 的 `build_query_engine` 參數與 `run_rag_build`/`run_rag_query` 兩種既有情境不受影響，不需要新增第三種分支。

### 驗證方式

- `pytest src/test/dev/test_rag_tools.py`（`TestGetCacheMiss` 斷言呼叫的方法名）。
- `pytest src/test/test_main.py -m slow`：真實跑完整流程，確認 agent 透過 `webpage_retriever` 觸發 `RAGRegistry` cache miss 時，log 只顯示建到 index 層級，不再印出 query_engine 設定；agent 仍能正確回答並附上來源。

---

## 總覽：對應 todo.md 項目

| 項目 | todo.md | 狀態 |
|------|---------|------|
| 1 | run_rag_build() 不建立 query_engine | ✅ 已完成 |
| 2 | save 與「是否重建向量庫」耦合 | ✅ 已完成 |
| 3 | create_rag() 支援傳入 run_manager 參數 | ✅ 已完成 |
| 4 | create_rag() 支援傳入已建立的 RAGConfig | ✅ 已完成 |
| 5 | clean_vector_store() 與 build_vector_store(overwrite=True) 重複 | ✅ 已完成 |
| 6 | webpage retriever tool 不建立 query_engine | ✅ 已完成 |
