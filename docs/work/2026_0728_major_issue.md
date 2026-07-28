# Major 問題修正策略 (2026/07/28)

## Major #4：`DEFALULT_COLLECTION_NAME` 拼寫錯誤

### 📊 問題根源分析

rag_config.py L20 宣告常數時少了一個 `U`：

```
DEFALULT_COLLECTION_NAME  ← 錯誤（缺少 U）
DEFAULT_COLLECTION_NAME   ← 正確
```

受影響的引用處：
| 檔案 | 行號 | 用途 |
|------|------|------|
| rag_config.py | L20 | 常數定義 |
| rag_config.py | L81 | `RagConfig` dataclass 預設值 |
| rag.py | L45 | `from ... import DEFALULT_COLLECTION_NAME` |
| rag.py | L203 | `build_vector_store()` 參數預設值 |

無其他檔案（TOML、workflow 等）引用此常數，改動範圍可控。

### 🛠️ 解決策略

**Step 1：修正 rag_config.py — 重新命名常數，保留舊名別名（選擇性）**

```python
# rag_config.py L20 — 修正拼寫
DEFAULT_COLLECTION_NAME = "webpages"

# 可選擇性地保留舊名作為別名，避免直接破壞尚未更新到的匯入
DEFALULT_COLLECTION_NAME = DEFAULT_COLLECTION_NAME  # 相容性別名
```

如果專案中沒有其他外部依賴引用 `DEFALULT_COLLECTION_NAME`，可以完全不保留別名。

**Step 2：更新 rag_config.py 中所有引用**

```python
# L81
collection_name: str = DEFAULT_COLLECTION_NAME
```

**Step 3：更新 rag.py 中所有引用**

```python
# L45 — import
from app.configs.rag_config import (
    DEFAULT_COLLECTION_NAME,  # 改名
    ...
)

# L203 — 方法參數預設值
collection_name: str = DEFAULT_COLLECTION_NAME,
```

**Step 4：全域搜尋確認無遺漏**

```bash
grep -rn "DEFALULT" website-copilot/
```

若無任何匹配，表示清理完成。

> **設計決策：** 不保留相容性別名。理由：
> - 專案為內部專案，非公開套件
> - 產生器（Copilot）改寫時一次更新所有引用
> - 保留別名只會讓拼寫錯誤繼續散佈

### ✅ 測試驗證方法

| 測試案例 | 類型 | 作法 | 預期結果 |
|---------|------|------|---------|
| **T4.1 常數存在** | Static | `grep -rn "DEFALULT" .` | 無任何匹配 |
| **T4.2 常數取代** | Static | `grep -rn "DEFAULT_COLLECTION_NAME" app/modules/rag.py` | import + 使用處皆為新名稱 |
| **T4.3 匯入不中斷** | Unit | `from app.configs.rag_config import RagConfig; cfg = RagConfig(collection_name="test")` | 不拋 ImportError |
| **T4.4 預設值正確** | Unit | `cfg = RagConfig(); assert cfg.collection_name == "webpages"` | 通過 |

---

## Major #5：`_set_embed_model` 缺少回傳型別註釋

### 📊 問題根源分析

```python
def _set_embed_model(self, embedding_name):  # ← 無回傳型別
    api_key = os.getenv("OPENAI_RAG_EMBEDDING_API_KEY")
    embed_model = OpenAIEmbedding(
        model=embedding_name,
        embed_batch_size=256,
        api_key=api_key,
    )
    return embed_model
```

Pylance／mypy 無法推斷回傳型別，隱藏潛在的 API key 為 `None` 的問題（`os.getenv()` 回傳 `str | None`）。

### 🛠️ 解決策略

```python
def _set_embed_model(self, embedding_name: str) -> OpenAIEmbedding:
    api_key = os.getenv("OPENAI_RAG_EMBEDDING_API_KEY")
    if api_key is None:
        raise ValueError(
            "Environment variable OPENAI_RAG_EMBEDDING_API_KEY is not set"
        )
    embed_model = OpenAIEmbedding(
        model=embedding_name,
        embed_batch_size=256,
        api_key=api_key,
    )
    return embed_model
```

**改善要點：**
- 補上 `-> OpenAIEmbedding` 回傳型別
- 補上 `embedding_name: str` 參數型別
- 順便驗證 `api_key` 不為 `None`（原來會靜默傳入 `None` 給 `OpenAIEmbedding`）

### ✅ 測試驗證方法

| 測試案例 | 類型 | 作法 | 預期結果 |
|---------|------|------|---------|
| **T5.1 型別正確** | Static | mypy 檢查 | `_set_embed_model` 回傳 `OpenAIEmbedding` |
| **T5.2 API key 缺失** | Unit | 設 `OPENAI_RAG_EMBEDDING_API_KEY=""` 後呼叫 | `ValueError` 拋出 |
| **T5.3 API key 正常** | Integration | 設有效 API key 後呼叫 | 回傳 `OpenAIEmbedding` 實例 |

---

## Major #6：`build_vector_store` 中 `EMBEDDING_DIM_MAP.get()` 可能回傳 `None`

### 📊 問題根源分析

```python
def build_vector_store(self, ..., embedding_name="text-embedding-3-small", ...):
    # ...
    elif vector_store_type == "milvus":
        dim = EMBEDDING_DIM_MAP.get(embedding_name)  # ← 可能為 None
        # ...
        self.vector_store = MilvusVectorStore(..., dim=dim, ...)
```

`EMBEDDING_DIM_MAP` 目前只包含兩個模型：
```python
EMBEDDING_DIM_MAP = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
}
```

若傳入 `"text-embedding-ada-002"` 或其他不在 map 中的模型，`dim` 為 `None`，`MilvusVectorStore(dim=None)` 的行為未定義。

### 🛠️ 解決策略

在 Milvus 分支的最前方加入驗證：

```python
elif vector_store_type == "milvus":
    dim = EMBEDDING_DIM_MAP.get(embedding_name)
    if dim is None:
        raise ValueError(
            f"Unknown embedding_name '{embedding_name}' for Milvus. "
            f"Supported: {list(EMBEDDING_DIM_MAP.keys())}. "
            "Add the entry to EMBEDDING_DIM_MAP in rag.py."
        )
    # ... 其餘邏輯 ...
```

或者更優雅的做法：將驗證抽取為靜態方法，統一管理 `dim` 查詢。

```python
@staticmethod
def _resolve_embedding_dim(embedding_name: str) -> int:
    """查詢 embedding 維度，若未知則拋錯。"""
    dim = EMBEDDING_DIM_MAP.get(embedding_name)
    if dim is None:
        raise ValueError(
            f"Unknown embedding_name '{embedding_name}'. "
            f"Supported embeddings: {list(EMBEDDING_DIM_MAP.keys())}."
        )
    return dim
```

然後在 `build_vector_store` 中呼叫：

```python
elif vector_store_type == "milvus":
    dim = self._resolve_embedding_dim(embedding_name)
    # ...
```

### ✅ 測試驗證方法

| 測試案例 | 類型 | 作法 | 預期結果 |
|---------|------|------|---------|
| **T6.1 已知 embedding** | Unit | `build_vector_store(vector_store_type="milvus", embedding_name="text-embedding-3-small")` | 成功建立，`dim=1536` |
| **T6.2 未知 embedding** | Unit | `build_vector_store(vector_store_type="milvus", embedding_name="unknown-model")` | `ValueError` 拋出，訊息包含支援列表 |
| **T6.3 Qdrant 不受影響** | Unit | `build_vector_store(vector_store_type="qdrant", embedding_name="unknown-model")` | 成功建立（Qdrant 不依賴 `EMBEDDING_DIM_MAP`） |
| **T6.4 `_resolve_embedding_dim` 靜態** | Unit | `Rag._resolve_embedding_dim("text-embedding-3-large")` | 回傳 `3072` |
| **T6.5 `_resolve_embedding_dim` 拋錯** | Unit | `Rag._resolve_embedding_dim("foo")` | `ValueError` |

---

## Major #7：`hybrid_ranker_params` 預設值邏輯耦合在 Milvus 分支內

### 📊 問題根源分析

```python
def build_vector_store(self, ..., hybrid_ranker="WeightedRanker",
                       hybrid_ranker_params=None):
    if vector_store_type == "qdrant":
        # ... Qdrant 分支 ── 完全忽略 hybrid_ranker_params
        pass
    elif vector_store_type == "milvus":
        # ── Milvus 分支內才處理預設值 ──
        if hybrid_ranker_params is None:
            if hybrid_ranker == "RRFRanker":
                hybrid_ranker_params = {"k": 60}
            elif hybrid_ranker == "WeightedRanker":
                hybrid_ranker_params = {"weights": [1.0, 0.5]}
```

問題：
1. **Qdrant 路徑即使傳入也被靜默忽略** — 造成誤解
2. **Milvus 路徑有獨立的預設值邏輯** — 未來新增 vector store 時需要複製貼上
3. **`else` 分支拋錯僅在 Milvus 分支內** — 若在 Qdrant 模式傳入不支援的 `hybrid_ranker`，不回報錯誤

### 🛠️ 解決策略

**Step 1：抽取模組等級的輔助函式**

```python
def _default_hybrid_ranker_params(
    hybrid_ranker: str,
) -> dict[str, Any]:
    """回傳指定 ranker 的預設參數。"""
    if hybrid_ranker == "RRFRanker":
        return {"k": 60}
    elif hybrid_ranker == "WeightedRanker":
        return {"weights": [1.0, 0.5]}
    else:
        raise ValueError(
            f"Unsupported hybrid_ranker: '{hybrid_ranker}'. "
            f"Supported: 'RRFRanker', 'WeightedRanker'."
        )
```

**Step 2：在 `build_vector_store` 開頭統一處理（與 `vector_store_type` 解耦）**

```python
def build_vector_store(self, ..., hybrid_ranker="WeightedRanker",
                       hybrid_ranker_params=None):
    # ── 統一處理 hybrid_ranker_params 預設值（與 vector_store_type 無關）──
    if hybrid_ranker_params is None:
        hybrid_ranker_params = _default_hybrid_ranker_params(hybrid_ranker)

    if vector_store_type == "qdrant":
        # Qdrant 不使用 hybrid_ranker_params，但允許傳入（不拋錯）
        logger.debug(
            f"Qdrant does not use hybrid_ranker_params, "
            f"ignoring: {hybrid_ranker_params}"
        )
        # ...
    elif vector_store_type == "milvus":
        # Milvus 使用 hybrid_ranker_params（已處理預設值）
        # ...
        self.vector_store = MilvusVectorStore(
            ...,
            hybrid_ranker=hybrid_ranker,
            hybrid_ranker_params=hybrid_ranker_params,
        )
```

> **⚠️ 注意：** 函式放在模組層級（非 class method），因為它不依賴 `self`。

### ✅ 測試驗證方法

| 測試案例 | 類型 | 作法 | 預期結果 |
|---------|------|------|---------|
| **T7.1 RRFRanker 預設值** | Unit | `_default_hybrid_ranker_params("RRFRanker")` | 回傳 `{"k": 60}` |
| **T7.2 WeightedRanker 預設值** | Unit | `_default_hybrid_ranker_params("WeightedRanker")` | 回傳 `{"weights": [1.0, 0.5]}` |
| **T7.3 不支援 ranker** | Unit | `_default_hybrid_ranker_params("UnknownRanker")` | `ValueError` 拋出 |
| **T7.4 Qdrant 傳入 params** | Unit | `build_vector_store(type="qdrant", hybrid_ranker="RRFRanker", hybrid_ranker_params={"k": 100})` | 不拋錯，`hybrid_ranker_params` 被忽略但記錄 debug log |
| **T7.5 Milvus 不傳 params** | Integration | `build_vector_store(type="milvus", hybrid_ranker="WeightedRanker")` | 自動套用 `{"weights": [1.0, 0.5]}` |
| **T7.6 不支援 ranker（Qdrant）** | Unit | `build_vector_store(type="qdrant", hybrid_ranker="Unknown")` | 即使在 Qdrant 路徑也應拋錯（預設值解析在前） |

---

## Major #8：`SimilarityPostprocessor` 僅在非 hybrid 模式使用

### 📊 問題根源分析

```python
node_postprocessors = []
if query_mode != "hybrid":
    node_postprocessors.append(SimilarityPostprocessor(similarity_cutoff=cutoff))
```

當前邏輯的假設：hybrid 模式的 dense + sparse 融合分數不適合用 `SimilarityPostprocessor` 過濾。但這有兩個問題：
1. hybrid 檢索仍可能回傳低分結果，特別是 `alpha` 權重傾斜時
2. 此假設沒有在任何文件或註解中說明

### 🛠️ 解決策略

**方案 A（推薦 — 最小風險）：保留行為 + 明確註解**

加入說明，讓未來維護者知道為什麼 hybrid 模式下略過 `SimilarityPostprocessor`：

```python
node_postprocessors: list[BaseNodePostprocessor] = []

if query_mode != "hybrid":
    # 僅在 dense-only（default）模式下啟用 similarity cutoff。
    # Hybrid 模式下 dense + sparse 融合分數的 scale 不一致，
    # SimilarityPostprocessor 的 cutoff 可能不適用。
    # 若 hybrid 模式也需要 cutoff，請改用自訂 node postprocessor 處理。
    node_postprocessors.append(SimilarityPostprocessor(similarity_cutoff=cutoff))
```

**方案 B（進階）：讓 cutoff 對 hybrid 也可選**

```python
# 新增參數 hybrid_cutoff
def build_query_engine(
    self,
    llm_name: str = "gemini-3.1-flash-lite",
    cutoff: float = 0.0,
    query_mode: str = "hybrid",
    hybrid_cutoff: float | None = None,  # None 表示不啟用
) -> None:
    node_postprocessors: list[BaseNodePostprocessor] = []

    if query_mode == "hybrid" and hybrid_cutoff is not None:
        node_postprocessors.append(SimilarityPostprocessor(similarity_cutoff=hybrid_cutoff))
    elif query_mode != "hybrid" and cutoff > 0:
        node_postprocessors.append(SimilarityPostprocessor(similarity_cutoff=cutoff))
```

**建議採用方案 A**，因為：
- 行為不變，無回歸風險
- 加入註解即可解決「隱含假設」的問題
- 方案 B 增加了 API 複雜度，且目前無實際使用場景

### ✅ 測試驗證方法

| 測試案例 | 類型 | 作法 | 預期結果 |
|---------|------|------|---------|
| **T8.1 hybrid 無 postprocessor** | Unit | `build_query_engine(query_mode="hybrid")` | `node_postprocessors` 為空列表 |
| **T8.2 default 有 postprocessor** | Unit | `build_query_engine(query_mode="default", cutoff=0.3)` | `SimilarityPostprocessor` 存在 |
| **T8.3 註解存在** | Static | 搜尋 `SimilarityPostprocessor` 前方註解 | 含 hybrid 說明 |

---

## Major #10：`_log_page_node_info` 偵錯方法遺留

### 📊 問題根源分析

```python
# L341 ── 呼叫處已被註解（dead code 的證據）
# self._log_page_node_info(self.nodes, page_title="Prospective_Students")

# L344-356 ── 方法定義仍保留
@staticmethod
def _log_page_node_info(nodes: Sequence[BaseNode], page_title: str) -> None:
    counter = 0
    for node in nodes:
        if node.metadata.get("page_title") == page_title:
            counter += 1
            logger.debug("Node content:")
            logger.debug(node.get_content())
            logger.debug("")
            logger.debug("Node metadata:")
            logger.debug(node.get_metadata_str())
            logger.debug("-" * 90)
    logger.debug(f"Found {counter} nodes from {page_title}")
```

### 🛠️ 解決策略

直接移除整個方法與被註解的呼叫行。理由：

| 保留的理由 | 評估 |
|-----------|------|
| 未來可能再用 | 可從 git history 還原 |
| 不影響執行 | 但增加維護負擔（lint、refactor 時需跳過） |
| 可以包在 `if __debug__` | 但方法內已是 `logger.debug()`，不需要額外防護 |

```python
# 移除 L341 的註解行
# (原行) # self._log_page_node_info(self.nodes, page_title="Prospective_Students") # debug

# 移除 L344-356 的整個方法定義
```

### ✅ 測試驗證方法

| 測試案例 | 類型 | 作法 | 預期結果 |
|---------|------|------|---------|
| **T10.1 方法不存在** | Static | `grep -rn "_log_page_node_info" app/` | 無匹配 |
| **T10.2 索引建立正常** | Integration | 完整執行 `build_nodes()` | 不拋 `AttributeError` |
| **T10.3 git 可還原** | Static | `git log --oneline -5` | 確認移除 commit 存在 |

---

## 📋 實作路徑圖

```
Phase 1 ─ 無腦機械式修改（無風險，可批次執行）
  ├── Step A: Major #5 — 補 `_set_embed_model` 回傳型別
  ├── Step B: Major #10 — 移除 `_log_page_node_info`
  └── Step C: Major #4 — 重新命名 `DEFALULT_COLLECTION_NAME`

Phase 2 ─ 程式碼提取與重構（需 review）
  ├── Step D: Major #7 — 抽取 `_default_hybrid_ranker_params()` 函式
  └── Step E: Major #6 — 抽取 `_resolve_embedding_dim()` 或內聯驗證

Phase 3 ─ API 設計調整（影響呼叫端）
  └── Step F: Major #8 — 加入 hybrid cutoff 註解或擴充參數

Phase 4 ─ 測試補強
  └── Step H: 撰寫上述所有測試案例
```

> **建議 Phase 1 合併為一個 PR**（純機械式修改，無行為變化）。
> **Phase 2 可與 Phase 1 合併**（程式碼提取，行為不變）。
> **Phase 3 建議另開 PR**（涉及 API 簽章變更，需要更新呼叫端）。