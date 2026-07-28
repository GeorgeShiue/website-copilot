# Critical 問題修正策略 (2026/07/27)

## Critical #1：資源洩漏風險（無 Context Manager 協定）

### 📊 問題根源分析

| 面向 | 現狀 |
|------|------|
| `Rag.__init__` | 建立 `QdrantClient`／`MilvusVectorStore`，無自動清理註冊 |
| `run_rag_build`（`workflow.py`） | 正確呼叫 `rag.close()` ✅ |
| `run_rag_query`（`workflow.py`） | 條件式呼叫 — `qdrant + rebuild=False` 時**漏接** ❌ |
| `webpage_retriever.py` | 僅以註解提醒，無強制機制 ❌ |
| Exception 路徑 | 任何 `build_*` 方法拋錯時，`close()` 皆未被確保 ❌ |

根因在於 `Rag` 未提供**呼叫端不可忽略的清理協定**，且 `close()` 本身不具冪等性保護。

### 🛠️ 解決策略

#### Step 1：改造 `rag.py` — 三層清理保障

```python
from typing import Self

class Rag:
    def __init__(self, ...) -> None:
        # ... 既有初始化 ...
        self._closed: bool = False

    # ── 第一層：Context Manager（主要用法）──
    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args) -> None:
        self.close()

    # ── 第二層：GC 安全網（`__del__`）──
    # 即使呼叫端忘記 `with` 或 `close()`，
    # CPython ref-count 歸零時仍會觸發
    def __del__(self) -> None:
        self.close()

    # ── 統一的清理入口，具冪等性 ──
    def close(self) -> None:
        if self._closed:
            return
        self._closed = True

        if self.qdrant_client is not None:
            self.qdrant_client.close()

        if isinstance(self.vector_store, MilvusVectorStore):
            try:
                self.vector_store._milvusclient.close()
            except Exception:
                pass

        self.qdrant_client = None
        self.vector_store = None
        self.index = None
        self.retriever = None
        self.query_engine = None

        import gc
        gc.collect()
```

**設計要點：**
- **冪等性**：`_closed` flag 確保多次呼叫安全
- **`__del__` 而非 `atexit`**：`__del__` 是 object-level 清理，不汙染全域；`atexit` 在嵌入場景（Jupyter、多實例）會造成訂單問題
- **無額外 import**：不需 `atexit` 或 `weakref`

#### Step 2：改造 `workflow.py` — 全面採用 `with` 陳述式

```python
# ── run_rag_build ──
def run_rag_build(...) -> None:
    rag = Rag()
    config = RagConfig.from_toml(config_name, **config_overrides)
    # ...
    with rag:  # ← 取代 rag.close()
        rag.override_init_config(webpages_data_folder_path=...)
        rag.build_nodes(...)
        rag.build_vector_store(...)
        rag.build_index(...)
        rag.build_retriever(...)
        rag.build_query_engine(...)
        rag.query(config.query, log_sources=True)
    # 離開 with 區塊時 __exit__ 自動呼叫 close()
```

```python
# ── run_rag_query ──
def run_rag_query(...) -> None:
    rag = Rag()
    # ...
    with rag:  # ← 統一包裹，不再需要條件式 close
        if rebuild or config.vector_store_type == "milvus":
            rag.build_nodes(...)
            rag.build_vector_store(...)
            rag.build_index(...)
        else:
            rag.build_vector_store(..., overwrite=False)
            rag.load_index(...)

        rag.build_retriever(...)
        rag.build_query_engine(...)
        response = rag.query(config.query, log_sources=True)
    # 自動清理，不再需要 if rebuild or milvus: rag.close()
```

#### Step 3：`webpage_retriever.py` — `__del__` 自動救援

不再需要強制呼叫端 `close()`，`__del__` 會在 CPython 解構時自動釋放。`tool.rag` 仍可保留供呼叫端提前清理。

#### Step 4：`override_init_config` 改為透過 `self.close()` 釋放資源

```python
def override_init_config(self, **init_kwargs) -> None:
    # ... validate-first（詳見 Critical #2）...
    self.close()  # 冪等清理，不再手動管理 qdrant_client/vector_store
    # ... atomic swap ...
```

### ✅ 測試驗證方法

| 測試案例 | 類型 | 作法 | 預期結果 |
|---------|------|------|---------|
| **T1.1 Context Manager** | Unit | `with Rag() as rag: pass` | `rag._closed == True` |
| **T1.2 close() 冪等性** | Unit | `rag.close(); rag.close()` | 第二次不拋錯 |
| **T1.3 `__del__` 安全網** | Unit | `rag = Rag(); del rag` | 不拋錯，資源釋放 |
| **T1.4 workflow 全面 with** | Integration | 執行 `run_rag_build()` | Qdrant 資料夾可被 `shutil.rmtree` 刪除（無檔案鎖） |
| **T1.5 workflow 條件分支** | Integration | `run_rag_query(qdrant, rebuild=False)` | 同上，無鎖殘留 |
| **T1.6 Exception 路徑** | Integration | `build_index()` 前模擬失敗 | `rag._closed == True`（`__exit__` 在 exception 時仍執行） |
| **T1.7 Tool 場景** | Integration | 建立工具後 `del tool` | `rag._closed == True` |

**關鍵驗證腳本（T1.4）：**

```python
def test_no_file_lock_after_with_block() -> None:
    """驗證 with 區塊結束後 Qdrant 資料夾可被刪除。"""
    run_manager = RunManager("rag_build_test")
    run_rag_build(run_manager=run_manager, config_name="test")

    qdrant_path = os.path.join(run_manager.results_folder_path, "qdrant_db")
    assert os.path.exists(qdrant_path)
    shutil.rmtree(qdrant_path)  # 若有檔案鎖，此處拋 PermissionError
    assert not os.path.exists(qdrant_path)
```

---

## Critical #2：`override_init_config` 重入（Re-entrancy）風險

### 📊 問題根源分析

```
目前執行順序：
  1. self.webpages_data_folder_path = new_path       ← 已變更
  2. self.md_docs_folder_path = new_md_path          ← 已變更
  3. self.results_json_path = new_json_path          ← 已變更
  4. 關閉舊的 qdrant_client / vector_store          ← 舊資源已釋放
  5. self.* = None                                   ← 重要狀態已清空
  6. self.results_json = self._load_results_json()   ← 若失敗，全部遺失！
```

若步驟 6 拋出 `FileNotFoundError` 或 `json.JSONDecodeError`，物件無法復原。

### 🛠️ 解決策略

#### 核心原則：**Validate First, Then Swap（先驗證，再交換）**

```python
def override_init_config(self, **init_kwargs) -> None:
    # ── Phase 1：Compute & Validate（純計算，無副作用）──
    new_webpages_data_folder_path = init_kwargs.get(
        "webpages_data_folder_path", self.webpages_data_folder_path
    )
    new_md_docs_folder_path = os.path.join(new_webpages_data_folder_path, "results")
    new_results_json_path = os.path.join(
        new_webpages_data_folder_path, "results.json"
    )

    # 提前驗證 JSON 可讀取 — 若失敗，self 完全不受影響
    if not os.path.exists(new_results_json_path):
        raise FileNotFoundError(
            f"Results JSON file not found at {new_results_json_path}"
        )
    with open(new_results_json_path, "r", encoding="utf-8") as f:
        new_results_json = json.load(f)

    # ── Phase 2：Release old resources（冪等清理）──
    self.close()  # 現在是冪等的（見 Critical #1）

    # ── Phase 3：Atomic swap（無風險的賦值）──
    self.webpages_data_folder_path = new_webpages_data_folder_path
    self.md_docs_folder_path = new_md_docs_folder_path
    self.results_json_path = new_results_json_path
    self.results_json = new_results_json
    # self.qdrant_client / vector_store 等已在 self.close() 中設為 None
```

**改善要點：**
- JSON 檔案在關閉任何資源**之前**驗證，任何例外都不破壞現有狀態
- `self.close()` 統一處理舊資源釋放，避免重複的關閉邏輯
- Phase 3 只有純賦值操作，不可能失敗

### ✅ 測試驗證方法

| 測試案例 | 類型 | 作法 | 預期結果 |
|---------|------|------|---------|
| **T2.1 正常 override** | Unit | 提供有效的 `webpages_data_folder_path` | 所有路徑與 JSON 正確更新 |
| **T2.2 無效路徑** | Unit | 提供不存在的資料夾路徑 | `FileNotFoundError` 拋出，`self` 所有屬性維持原值 |
| **T2.3 損毀 JSON** | Unit | 提供存在但內容為無效 JSON 的路徑 | `json.JSONDecodeError` 拋出，`self` 所有屬性維持原值 |
| **T2.4 連續 override** | Unit | 連續呼叫兩次 `override_init_config` | 第二次成功後，所有屬性指向新路徑，無記憶體洩漏 |
| **T2.5 override → build 序列** | Integration | `rag.override_init_config(...)` → `rag.build_nodes(...)` | 新路徑資料被正確載入 |
| **T2.6 錯誤復原後可用** | Unit | 先以無效路徑呼叫（預期拋錯），再以有效路徑呼叫 | 第二次成功，物件完全可用 |

**關鍵驗證腳本：**

```python
def test_override_init_config_preserves_state_on_failure() -> None:
    """驗證 override_init_config 失敗時原始狀態不受影響。"""
    rag = Rag(webpages_data_folder_path="data/webpages")
    original_path = rag.webpages_data_folder_path
    original_json = rag.results_json

    # 嘗試無效路徑
    with pytest.raises(FileNotFoundError):
        rag.override_init_config(webpages_data_folder_path="/nonexistent/path")

    assert rag.webpages_data_folder_path == original_path
    assert rag.results_json == original_json
    assert rag.qdrant_client is None  # 未建立過，應保持 None

    # 嘗試有效路徑 — 物件仍可用
    rag.override_init_config(webpages_data_folder_path="data/webpages")
    assert rag.webpages_data_folder_path == "data/webpages"
```

---

## Critical #3：`retrieve()` 每次呼叫都重建 retriever

### 📊 問題根源分析

```python
def retrieve(self, query, filter_dict=None, similarity_top_k=None):
    if filter_dict is not None or similarity_top_k is not None:
        self.build_retriever(...)  # ← 每次建新的 VectorIndexRetriever！
    nodes = self.retriever.retrieve(query)
```

`build_retriever()` 的內部成本：

| 操作 | 成本 |
|------|------|
| `MetadataFilter` 串列建立 | 低（純 Python，無 I/O） |
| `VectorIndexRetriever(...)` 實例化 | 中（Pydantic 校驗 + filters 處理） |
| Agent 連續 1000 次呼叫 | ~1-5s 浪費 |

更嚴重的問題是**狀態汙染（state leakage）**：

1. `retrieve(q1, filter_dict={"page_type": "paper"})` → retriever 重建，filters 設為 paper
2. `retrieve(q2)` → 不傳 filter_dict，條件為 False → **不重建** → filters 仍是 paper！

第一次的 filter 會**洩漏**到第二次查詢，這是一個隱藏 bug。

### 🛠️ 解決策略

#### Step 1：抽取 `_build_filters()` 為靜態方法

```python
@staticmethod
def _build_filters(
    filter_dict: dict[str, Any] | None,
) -> MetadataFilters | None:
    """將 filter_dict dict 轉換為 LlamaIndex MetadataFilters。"""
    if filter_dict is None:
        return None
    filter_list = []
    for key, entry in filter_dict.items():
        if isinstance(entry, tuple):
            value, operator = entry
        else:
            value, operator = entry, FilterOperator.EQ
        filter_list.append(
            MetadataFilter(key=key, value=value, operator=operator)
        )
    return MetadataFilters(filters=filter_list)
```

#### Step 2：改造 `retrieve()` — 直接覆寫 + 狀態還原

```python
def retrieve(
    self,
    query: str,
    filter_dict: dict[str, Any] | None = None,
    similarity_top_k: int | None = None,
) -> list[dict[str, Any]]:
    if self.retriever is None:
        raise RuntimeError("Retriever has not been built, cannot retrieve")

    # ── 儲存原始值（用於呼叫結束後還原）──
    original_filters = getattr(self.retriever, "filters", None)
    original_top_k = self.retriever.similarity_top_k

    try:
        # ── 直接覆寫 retriever 內部屬性，不重建 ──
        if filter_dict is not None:
            self.retriever.filters = self._build_filters(filter_dict)
        if similarity_top_k is not None:
            self.retriever.similarity_top_k = similarity_top_k

        nodes = self.retriever.retrieve(query)
    finally:
        # ── 還原原始值，防止狀態汙染 ──
        self.retriever.filters = original_filters
        self.retriever.similarity_top_k = original_top_k

    # ── 格式化結果（與原邏輯相同）──
    results = []
    for node in nodes:
        page_title, score, page_type = extract_sources_info(node)
        results.append({
            "page_title": page_title,
            "score": score,
            "page_type": page_type,
            "content": node.node.get_content(),
            "url": node.node.metadata.get("page_url", ""),
        })
    return results
```

**關鍵設計決策：**

1. **`try/finally` 確保還原**：無論 `retrieve()` 內部是否拋錯，filter/top_k 都回到原始值
2. **直接覆寫內部屬性**：`VectorIndexRetriever` 使用 Pydantic，`filters` 與 `similarity_top_k` 是 public field（程式碼已確認 `self.retriever.similarity_top_k` 可讀取）
3. **`getattr(self.retriever, "filters", None)`**：若實際屬性名為 `_filters`（private），可改為 `getattr(self.retriever, "_filters", None)` ➜ 請依 LlamaIndex 版本確認

> **⚠️ 實作前建議：**
> ```python
> # 在 REPL 中確認屬性名稱
> r = VectorIndexRetriever(index=index, similarity_top_k=10, filters=None)
> r.similarity_top_k    # 應為 10
> r.filters             # 或用 r._filters
> ```

#### Step 3：移除 `workflow.py` 中對 `build_retriever` 的 filter_dict 註解

`run_rag_query` 中原有：

```python
# rag.build_retriever(
#     ...,
#     filter_dict=filter_dict,  # * 留給 agent 工具參數
# )
```

重構後，初始 `build_retriever` 不傳 `filter_dict`，Agent 透過 `rag.retrieve(filter_dict=...)` 動態指定。

#### 效能對比

| 場景 | 改造前 | 改造後 | 改善 |
|------|--------|--------|------|
| 無 overrides（最常見） | `build_retriever` 略過 ✅ | 無條件略過 ✅ | 相同 |
| 有 filter_dict | 新建 `VectorIndexRetriever` | 直接覆寫 `retriever.filters` | **~50–200x** |
| 有 similarity_top_k | 同上 | 直接覆寫屬性 | **~50–200x** |
| Agent 連續 1000 次 | 1000 次重建 = ~1-5s | 0 次重建 | 節省 ~1-5s |

### ✅ 測試驗證方法

| 測試案例 | 類型 | 作法 | 預期結果 |
|---------|------|------|---------|
| **T3.1 基本檢索** | Unit | `rag.retrieve("query")` | 回傳非空 list |
| **T3.2 filter 過濾** | Unit | `retrieve("query", filter_dict={"page_type": "paper"})` | 所有結果的 `page_type` 皆為 `"paper"` |
| **T3.3 similarity_top_k** | Unit | `retrieve("query", similarity_top_k=3)` | `len(results) <= 3` |
| **T3.4 無狀態汙染** | Unit | 1. `retrieve(q1, filter_dict={"page_type": "paper"})`<br>2. `retrieve(q2)`（不傳 filter） | 第二次結果包含非 paper 頁面 |
| **T3.5 無狀態汙染（top_k）** | Unit | 1. `retrieve(q1, similarity_top_k=3)`<br>2. `retrieve(q2)`（不傳 top_k） | 第二次結果數為初始值（預設 10） |
| **T3.6 Exception 後復原** | Unit | 在自訂 retriever 中模擬 `retrieve()` 拋錯 | 後續正常呼叫不受影響 |
| **T3.7 效能基準** | Benchmark | `for _ in range(100): rag.retrieve(q)` | 總耗時 < 重建 100 次的 5% |
| **T3.8 不觸發 build_retriever** | Unit | mock `rag.build_retriever` → `retrieve(q, filter_dict=...)` | `build_retriever` 未被呼叫 |

**關鍵驗證腳本：**

```python
def test_retrieve_no_filter_leakage(rag_with_built_retriever: Rag) -> None:
    """驗證 filter 不會從一次呼叫洩漏到下一次。"""
    # ── 第一次：帶 filter ──
    results_1 = rag_with_built_retriever.retrieve(
        "research", filter_dict={"page_type": "paper"}
    )
    assert all(r["page_type"] == "paper" for r in results_1)

    # ── 第二次：不帶 filter ──
    results_2 = rag_with_built_retriever.retrieve("research")
    page_types_2 = {r["page_type"] for r in results_2}
    assert len(page_types_2) > 1, (
        f"Expected multiple page types, got: {page_types_2}"
    )


def test_retrieve_does_not_rebuild(monkeypatch: pytest.MonkeyPatch) -> None:
    """驗證 retrieve() 不觸發 build_retriever。"""
    rag = Rag()
    # ... 完整建構至 retriever ...

    build_call_count = 0
    original_build = rag.build_retriever

    def tracking_build(**kwargs):
        nonlocal build_call_count
        build_call_count += 1
        return original_build(**kwargs)

    monkeypatch.setattr(rag, "build_retriever", tracking_build)

    rag.retrieve("query1", filter_dict={"page_type": "paper"})
    rag.retrieve("query2")
    rag.retrieve("query3", similarity_top_k=5)

    assert build_call_count == 0, (
        f"build_retriever was called {build_call_count} times (expected 0)"
    )
```

---

## 📋 實作路徑圖（建議順序）

```
Phase 1 ─ 基礎改造（不影響外部 API）
  ├── Step A: close() 冪等性（Critical #1）
  └── Step B: 抽取 _build_filters() 靜態方法（Critical #3 前置）

Phase 2 ─ 核心行為修正
  ├── Step C: override_init_config validate-first（Critical #2）
  └── Step D: retrieve() 直接覆寫 + 狀態還原（Critical #3）

Phase 3 ─ 清理協定強化
  ├── Step E: __enter__ / __exit__ / __del__（Critical #1）
  └── Step F: workflow.py 全面改用 with rag:

Phase 4 ─ 測試補強
  ├── Step G: 撰寫以上所有測試案例
  └── Step H: 執行完整測試套件確認無回歸
```

> **建議合併策略：** Phase 1+2 在同一個 PR 中完成（Step B 是 Step D 的前置條件）。Phase 3（`with` 改寫）涉及呼叫端變更，建議另開一個 PR 以降低 review 負擔。
