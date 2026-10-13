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

#### 裝飾器

- [ ] `WebpageMarkdownCleaner` 的 8 個公開 `@staticmethod` 是純函式且以寫死的類別名互相呼叫：改成模組函式（需多型則改 `@classmethod`），與「Webpage Markdown Cleaner 獨立成一個模組」一併處理
- [ ] 計時／重試的裝飾器版本：`log_run_time` 目前只有 context manager 形式

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

