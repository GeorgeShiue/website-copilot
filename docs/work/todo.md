# Survey
- [ ] 產品定位

# 功能進度

- [ ] 網站知識庫版本控制
- [ ] 站點檔加入顯示名稱與描述，供 list_knowledge_bases 回傳給 LLM

# 技術債

## 模組重構

- [ ] Webpage Markdown Cleaner 獨立成一個模組
- [ ] 包裝 log_helper.py（含約 6 處 Rich「Metric／Value」統計表格，見 code cleanup plan C3）
- [ ] 客製化模組 RunManager

## Python 優化

已採用的設計見 `docs/code/python.md`。

### 修正

#### 模組 import

> 先用 `python -X importtime` 建立量測基準（現況 `cli` 約 0.16 s、`retrieval.registry` 約 1.3 s、`server.app` 約 2.2 s，主要是 `llama_index`／`agent`）
- [ ] 重依賴（`llama_index`、`agent`）只在實際用到時才 import，例如 `RAGRegistry.get()` 內才載入 `load_rag`，`--help` 與設定驗證不載入
- [ ] 延遲 import 只用於「重依賴＋非必經路徑」，並統一寫法與註明原因（目前 `src/` 約 23 處）；一般模組維持頂層 import
- [ ] 以 import-linter 固化依賴方向，取代靠註解避免 `tool.py` ↔ `site_discovery`／`webpage_retriever` 循環
- [ ] CI 加入 import 耗時回歸檢查（如 `--help` 超過門檻即警告）

#### 裝飾器

- [ ] `VectorStoreBuilder`（`vector_store.py`）全是 `@staticmethod` 的無狀態命名空間類別，改成模組層級函式
- [ ] `WebpageMarkdownCleaner` 的 8 個公開 `@staticmethod` 是純函式且以寫死的類別名互相呼叫：改成模組函式（需多型則改 `@classmethod`），與「Webpage Markdown Cleaner 獨立成一個模組」一併處理
- [ ] `@contextmanager` 補回傳型別：`save_logging_file`、`log_run_time` 加 `-> Iterator[None]`，與 `publish_log_file`、`run_workflow_context` 一致
- [ ] 計時／重試的裝飾器版本：`log_run_time` 目前只有 context manager 形式


#### 穩健性與型別一致

- [ ] `RAGRegistry.__exit__` 回傳型別改為 `-> None`（或 `Literal[False]`），與 `RAG.__exit__` 一致
- [ ] `RAGRegistry.close()`：單一 `rag.close()` 失敗時，其餘仍須關閉且快取要清空（`try/finally` 或收集例外）
- [ ] `PageStats.__add__`：遇到非 `PageStats` 回傳 `NotImplemented`
- [ ] `http_downloader`：`on_complete` 回呼丟例外會讓整批下載失敗，評估加保護（目前僅更新進度條，風險低）

#### 冗餘程式碼

- [ ] `log_helper.py`：刪除未被讀取的全域 `_logging_path`
- [ ] `log_helper.py`：`_setup_logging_file` 內的 `_disable_logging_file()` 呼叫是空操作（此時深度必為 0），移除或改成斷言
- [ ] `titles.py`：`_most_common` 改用 `Counter(usable).most_common(1)[0][0]`（已用隨機資料驗證結果一致）
- [ ] `overrides.py`：`_section_type` 與 `_strip_optional` 重複 Optional 解包邏輯，抽出共用 helper

### 新增

#### 型別與資料模型

- [ ] `StrEnum` 取代狀態字串：`ImageEntry` 的 `download_status`／`summarize_status`（`"success"`／`"failed"`／`""`），避免拼錯不報錯
- [ ] `dataclass(slots=True)`：`ImageEntry` 等大量實例的快取物件，省記憶體並擋住欄位名拼錯
- [ ] 建構時保證不變式：`Asset.first_page` 在 `refs` 為空時會 `IndexError`，改在建構時驗證
- [ ] `frozen=True` 候選：`AssetRef`、`ParsedDocument`（以欄位名粗略比對，改前需確認無人修改）；CLI dataclass 由 tyro 建立，不動

#### 語法與標準庫

- [ ] `match`／`case`：`_fetch_once` 的狀態碼分流、`overrides.py` 的註解型別分流
- [ ] `functools.cache`／`lru_cache`：`_representatives()` 等重複計算的純函式（`RAGRegistry` 需主動 `close()`，維持手寫 LRU）
- [ ] `itertools.batched`：VLM／embedding 的批次切分
- [ ] `asyncio.TaskGroup`：`image_captioner` 目前「單一失敗不拖垮整批」，改用時須保留此語意，優先度低

