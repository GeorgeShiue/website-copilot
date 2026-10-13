# Python 設計修正：實作規劃

> 對應 [todo.md](../../todo.md)「Python 優化 → 修正」。依檢視結果（誤用、冗餘、不一致）整理，已採用的設計見 [docs/code/python.md](../../../code/python.md)。
>
> 範圍只含「修正」；「新增」（`StrEnum`、`slots=True`、`match` 等）不在本計畫內。

## Context

對既有 Python 設計逐項檢視後，沒有發現嚴重誤用，但有四類可改善的地方：

| 組別 | 內容 | 風險 | 影響 |
|---|---|---|---|
| A | 冗餘程式碼（死變數、空操作、重複邏輯、未使用參數） | 極低 | 可讀性 |
| B | 穩健性與型別一致 | 低 | 正確性 |
| C | 裝飾器（無狀態命名空間類別、缺回傳型別） | 中 | 可讀性、型別 |
| D | 模組 import 策略 | 高 | **唯一可能影響效能**（啟動時間） |

**效能的實際期待**：只有 D 組可能縮短啟動時間（量測：`retrieval.registry` 約 1.3 s、`server.app` 約 2.2 s，來源為 `llama_index`／`agent`）。A～C 對執行效能的影響可忽略，目的是減少維護成本與潛在錯誤。

## 順序與理由

**準備 → A → B → C → D**，風險由低到高。

1. **準備**：量測 import 耗時基準，不改程式，之後才有對照。
2. **A 最先**：純刪除或等價改寫，先清掉雜訊，後續 diff 較乾淨。
3. **B 在 D 之前**：B1、B2 與 D1 都改 `retrieval/registry.py`，先改 B 可避免互相衝突。
4. **C 在 D 之前**：`VectorStoreBuilder` 改完後 `index.py` 的 import 才穩定，再處理 import 較安全。
5. **D 最後**：延遲 import 可能把成本推到第一個請求、碰到循環引用，且測試大量使用 `patch`，目標路徑可能需調整。CI 檢查要在改完後才加，否則一開始就會失敗。

## 執行流程

1. **建分支與基準點**：從 `dev` 切出分支（建議 `chore/python-fixes`）。文件（`plan.md`、`docs/code/python.md`、`docs/work/todo.md`）先以單獨 commit 提交，作為基準點並記錄 commit hash。
2. **準備**：量測 import 耗時基準，只記錄數據，不改程式碼，不產生 commit。
3. **依序處理 A → B → C → D**，每組：
   1. 依組內項目順序實作（需要時先補特徵測試，見「測試先行」）。
   2. 組內項目全部完成後，跑**共同驗證關卡**。
   3. 關卡通過後，**一組一個 commit**（訊息列出該組處理的項目）。
   4. 關卡未通過：在該組內修正並重跑，不提前 commit。
4. **自動進入下一組**：一組 commit 後直接開始下一組，不等待確認。
5. **全部組別完成後**：進行最後驗證（見「驗證（整體完成後）」），結束後把過程寫入 `dev.md`，並向使用者回報。

### 停止條件

除了下列情況，全程不中斷：

- 同一個驗證關卡經合理嘗試仍無法修復。
- 需要計畫外的決定（例如要改公開介面、或改動會明顯改變行為）。
- 發現計畫的前提不成立，繼續做會偏離原意。

遇到時停在該組、保持工作區可還原，並向使用者說明狀況與選項，**不跳過、不硬做**。

### 自動執行時的判斷規則

為了讓流程不被小決定打斷，下列情況事先約定：

- **B4（`on_complete` 保護）**：預設做，放在 B 組最後一項；若實作比預期複雜，略過並在 dev.md 記錄原因。
- **D1**：依準備步驟的量測結果判斷。找不到實際受益的路徑就放棄 D1，並在 dev.md 記錄量測依據；有受益路徑才實作。
- **A1**：維持單獨實作，不等待 log_helper 重構。
- **C3、C4**：不處理。

## 共同驗證關卡

在**每一組完成後**（commit 前）執行：

- `scripts/check.sh`（ruff + pyright、`pytest tests/unit`、widget 檢查）。
- 7 個 CLI 的 `--help` 冒煙測試（import 與 config 相關改動必跑）。
- B、D 組另跑 `pytest tests/integration -m "not cost"`。

**測試先行**：會改變行為或沒有現成測試覆蓋的項目，先補特徵測試並在舊程式碼上確認通過（B2 的測試應在舊程式碼上失敗，證明確實修到問題），再改實作。

---

# 準備：Import 耗時基準

用 `python -X importtime` 量測並記錄於 dev.md，改動前後對照。

| 入口 | 現況（單次量測） |
|---|---|
| `website_copilot.cli` | 約 0.16 s |
| `website_copilot.retrieval.registry` | 約 1.3 s |
| `website_copilot.server.app` | 約 2.2 s |

- 數字受檔案快取影響，只看相對大小；正式基準至少各量 3 次取中位數。
- 另加：`website-copilot --help`、`website-copilot serve` 啟動到可服務的時間。
- 用 `-X importtime` 輸出找出**各入口的最大單一邊**（哪個 import 拖進 `llama_index`），供 D1 決定切點。

---

# A 組：冗餘程式碼

## A1：`utils/log_helper.py`

- 刪除未被讀取的全域 `_logging_path`（宣告、`global` 宣告與賦值三處）。
- `_setup_logging_file` 內的 `_disable_logging_file()` 呼叫是空操作：走到該行時 `_tee_depth > 0` 的情況已提前 `return`，深度必為 0，而 `_disable_logging_file` 開頭即 `if _tee_depth == 0: return`。移除。
- **先補測試**：巢狀 `save_logging_file`（內層結束保留外層 tee、最外層結束才還原 `sys.stdout`／`sys.stderr` 並關檔）。目前 `tests/` 沒有直接涵蓋此行為。
- **與「包裝 log_helper.py」重構的關係**：若該重構近期要做，A1 併入而不單獨改一次。

## A2：`ingestion/augmentation/titles.py`

- `_most_common` 改為 `Counter(usable).most_common(1)[0][0]`。
- 已用 20000 組隨機資料驗證與現行邏輯結果一致（並列時取最早出現者）。
- 現有 `test_title_prefers_most_common_non_generic_link_text` 之外，補「並列取最早出現」的明確測試。

## A3：`config/overrides.py`

- `_section_type` 與 `_strip_optional` 各自過濾 `NoneType` 並遞迴，抽出共用 helper（剝掉單一 `X | None`，回傳 X 或 None）。
- **限制**：不與 `base_config._has_field_path` 合併。2026_1001 code_cleanup 的 A3 已決定兩者保持分開：`_section_type` 接受 `Model | None`，合併會讓 `run_name_fields` 能指到可能為 None 的 section，行為變寬。
- `prune_empty` 的 `value is None` 分支保留：`overrides_to_dict` 路徑不會觸發，但 `test_overrides.py` 直接呼叫它。
- 驗證：`tests/unit/test_overrides.py`、各 CLI `--help`（`--help` 的預設值顯示由此模組產生）。

## A4：殘留的小型冗餘

由 ruff 擴大規則集（`ARG`、`RET`、`UP015`、`B007`、`RUF100`）與 AST 檢查找出。檢查範圍內沒有未引用的定義、未使用的 import、註解掉的程式碼，也沒有重複的函式本體。

1. **未使用的參數 `raw_pages`**：`run_persistence.save_generated_exclude_words(result, raw_pages, run_path)` 的函式本體沒有使用它。移除該參數，並同步修改 `DataManager.publish_generated_exclude_words`（參數與 docstring）以及 `pipelines/prepare.py` 的兩個呼叫端。`WebsiteCrawler.raw_pages` 屬性仍被爬蟲使用，不能刪。
2. **未使用的參數 `site_id`**：`DataManager.create_vector_store_staging(self, site_id)` 沒有使用它，移除並修改唯一的呼叫端（`prepare.py`）。
3. **迴圈未使用的變數**：`documents.py` 的 `for sha, (_, entry) in self._representatives().items()` 改為 `for sha in self._representatives():`。
4. **多餘的暫存變數（RET504，4 處）**：改為直接 `return`。位置：`agent/tools/webpage_retriever.py`（2 處）、`ingestion/crawling/markdown_cleaner.py`、`ingestion/indexing/transforms.py`。
5. **多餘的 `open(..., "r")`（3 處）**：`"r"` 為預設值，省略。位置：`ingestion/indexing/source.py`、`storage/run_manager.py`、`storage/run_persistence.py`。
6. ~~**沒有作用的 `# noqa` 改為一般註解**~~ **取消**：執行時發現前提不成立。原本以為專案 ruff 用預設規則（`E4/E7/E9/F`），`BLE001`、`DTZ007`、`SIM115` 未啟用；實際上 ruff 0.16 的預設規則包含它們，移除後 `ruff check` 立即報 5 個錯誤。先前是用 `--select` 覆蓋了專案設定才誤判。這 5 處 `noqa` 都有作用，維持原狀，`docs/code/python.md` 也不需修改。

**不處理**：
- `transforms.py` 的 `show_progress`、`**kwargs` 是 LlamaIndex 要求的簽章，ruff 的 `ARG002` 為誤報。
- `try/except/pass` 改 `contextlib.suppress`：`log_helper.py` 兩處把「為何可忽略」寫在 `except` 內，改了會失去位置，維持原狀。
- `vector_store.py` 的 `elif` 跟在 `return` 後面：C2 會重寫該檔，屬於 C2。

**驗證**：`tests/` 沒有引用 1、2 項涉及的三個函式，不需要改測試。完成後 `ruff check src --select RET504,UP015,B007,ARG001` 應只剩框架簽章的誤報；其餘照共同驗證關卡。

---

# B 組：穩健性與型別一致

## B1：`RAGRegistry.__exit__` 型別

- 回傳型別改為 `-> None`，與 `RAG.__exit__` 一致（目前 `-> bool` 且恆回 `False`，型別檢查器會假設例外可能被吞掉）。
- 驗證：pyright。

## B2：`RAGRegistry.close()`

- 問題：迴圈中某個 `rag.close()` 丟例外，後面的不會關閉，`_cache.clear()` 也不會執行。
- 做法：每個都嘗試關閉，失敗以 `logger.exception` 記錄後繼續，最後（`finally`）清空快取。
- **測試先行**：fake RAG 其中一個 `close()` 丟例外，斷言其餘都被關閉、快取為空；此測試在舊程式碼上應失敗。
- **已決定**：只記錄、不重新拋出。釋放資源屬盡力而為，且 `close()` 會被 `__exit__` 呼叫，區塊內已有例外時再拋出會蓋住原本的錯誤。

## B3：`PageStats.__add__`

- 遇到非 `PageStats` 回傳 `NotImplemented`，讓 Python 產生標準 `TypeError`。
- 測試：`PageStats() + 1` 拋 `TypeError`；`sum(..., PageStats())` 仍正常（現有用法）。

## B4：`utils/http_downloader.py` 的 `on_complete`

- `on_complete` 丟例外會經 `gather` 讓整批失敗。包 `try/except Exception`，記 warning 後繼續。
- 目前回呼只更新進度條，風險低，列為本組最後、可選。
- 測試：回呼丟例外時，`adownload` 仍回傳完整結果。

---

# C 組：裝飾器

## C1：`@contextmanager` 補回傳型別

- `save_logging_file`、`log_run_time` 加 `-> Iterator[None]`（`collections.abc`），與 `publish_log_file`、`run_workflow_context` 一致。
- 驗證：pyright。

## C2：`VectorStoreBuilder` 改模組函式

- `ingestion/indexing/vector_store.py`：三個 `@staticmethod`（`resolve_embedding_dim`、`default_hybrid_ranker_params`、`build`）無狀態、無 `__init__`，改成模組層級函式（`build` 建議更名為 `build_vector_store`）。
- 同步修改 `ingestion/indexing/index.py` 的呼叫端，以及 `tests/unit/test_serve_rag_loading.py` 中的引用；改前再 `grep` 確認 patch 目標是否指向舊類別路徑。
- 驗證：`scripts/check.sh`；`pytest tests/integration -m "not cost"` 確認建庫流程。

## C3：`WebpageMarkdownCleaner` 的 static（移交，不在本計畫實作）

- 8 個公開 `@staticmethod` 是純函式，且以寫死的類別名互相呼叫。
- 應與 todo「模組重構」的「Webpage Markdown Cleaner 獨立成一個模組」一併處理，單獨改會動兩次。需多型才改 `@classmethod`，否則改模組函式。

## C4：計時／重試裝飾器（本批不做）

- 屬新增功能而非修正，且會多一層函式呼叫。待 A～D 完成、確認確有重複樣板後再評估。

---

# D 組：模組 import 策略

## D1：重依賴延遲載入

- 目標：不需要 `llama_index`／`agent` 的路徑（`--help`、設定驗證、僅 `list_sites()`、測試收集）不載入它們。
- **先看準備步驟的量測，再決定切點**。已知 `registry` → `retrieval.factory` → `ingestion.indexing.index` → `llama_index.core`（約 0.54 s），`server.app` → `agent.agent`（約 2.0 s）。優先切「單一最大邊」，不要全面改。
- **已知風險一：patch 目標會失效**。`tests/unit/test_rag_tools.py` 多處使用 `@patch("website_copilot.retrieval.registry.load_rag")`；把 `load_rag` 的 import 移進 `RAGRegistry.get()` 後，`registry` 模組不再有這個屬性，`patch` 會失敗。需改 patch 目標（如 `...retrieval.factory.load_rag`），或改切上游邊、保留 `registry` 的頂層 import。
- **已知風險二：成本轉移**。`serve` 最終仍需要這些依賴，延遲只是把成本從啟動搬到第一次請求，可能讓首個請求變慢。若不可接受，在 `run_serve` 啟動後預先載入。
- **go/no-go**：若量測顯示沒有任何實際受益的路徑（`cli` 已在 `main()` 內延遲 import），則只做 D2～D4，不動 D1。

## D2：統一延遲 import 的寫法

- 原則：延遲 import 只用於「重依賴＋非必經路徑」；一般模組維持頂層 import。
- 盤點 `src/` 約 23 處函式內 import，每處以註解標明原因（例如 `# 延遲載入：docling 模型很大，沒處理 PDF 時不載入`）。
- 規則寫進 [docs/code/python.md](../../../code/python.md)。

## D3：以 import-linter 固化依賴方向

- 取代 `RAGRegistry` docstring 中「避免 `tool.py` ↔ `site_discovery`／`webpage_retriever` 循環」的註解約定。
- 契約草案：`retrieval` 不可 import `agent`、`server`；`ingestion` 不可 import `agent`、`server`。
- 已同意新增 `import-linter` 為 dev 依賴（`uv add --dev import-linter`），並納入 `scripts/lint.sh`。
- 實作時先在現有程式碼上跑契約，確認目前沒有違規（有違規則先判斷是契約過嚴或程式碼需修）。

## D4：CI import 耗時回歸檢查

- 腳本量測 `python -X importtime` 的 `website-copilot --help` 累計耗時，超過門檻時警告。
- 先以警告模式上線，累積幾次數據後再決定是否改為失敗；門檻依準備步驟的基準設定（含餘裕）。
- 加入既有 CI 的 quality-check job。

---

# 決定事項

| 項目 | 問題 | 決定 |
|---|---|---|
| A1 | 是否併入「包裝 log_helper.py」重構？ | 維持原規劃：單獨實作；若執行時該重構已在進行，再併入 |
| B2 | `close()` 全部關完後是否重新拋出例外？ | 只記錄不拋出 |
| B4 | 是否做 `on_complete` 保護？ | 可選，排在 B 組最後；其餘項目完成後視情況再做 |
| D1 | 量測後無受益路徑時是否放棄？ | 放棄 D1，保留 D2～D4 |
| D3 | 是否新增 `import-linter` 為 dev 依賴？ | 同意 |
| A4-6 | 沒有作用的 `# noqa` 怎麼處理？ | ~~改為一般註解~~ 取消：執行時發現這些 `noqa` 有作用（見 A4-6），維持原狀 |

目前沒有尚待決定的項目。

# 不在範圍

- 「新增」段落的項目（`StrEnum`、`dataclass(slots=True)`、`match`、`lru_cache`、`itertools.batched`、`TaskGroup`）。
- 「沒有新欄位的子類加 `@dataclass`」：檢視後決定不處理。
- C3、C4（見上）。

# 驗證（整體完成後）

1. `scripts/check.sh` 通過、7 個 CLI `--help` 正常。
2. `pytest tests/integration -m "not cost"` 通過。
3. 重新量測 import 耗時，與基準對照。
4. 付費整合測試：`pytest tests/integration -m cost`，**只在全部組別完成後跑一次**（各組驗證關卡不跑，控制費用）。
   - 前置條件：需要有效的 API 金鑰與網路。缺金鑰或無網路時，記錄為「未執行」並在回報中說明，不視為失敗。
   - 失敗時先判斷原因：對失敗的測試在基準點（`dev` 上的文件 commit）重跑一次。基準點也失敗代表是既有問題或外部因素（API 額度、網路），記錄但不阻擋；只有基準點通過、改動後失敗才算回歸，依停止條件處理。
   - 記錄測試輸出中的費用摘要（若有）。

# 完成後：dev.md 與回報

驗證結束後，寫 `docs/work/2026_1019/2026_1019-python_fixes/dev.md`（格式參考 `2026_1005/2026_1001-code_cleanup/dev.md`：只記錄與 plan 不同的決定、過程中的發現與驗證結果）：

- 基準點與各組 commit hash。
- 每組的驗證結果（`check.sh` 通過的測試數）。
- import 耗時：基準與完成後的對照，以及 D1 的 go/no-go 依據。
- 付費整合測試的結果（通過數、失敗或未執行的原因、費用摘要）。
- 與 plan 不同的決定、B4 是否實作、過程中發現的問題。
- 未處理項目（C3、C4）與後續建議。

最後向使用者回報：完成的組別與 commit、驗證結果、效能對照、與 plan 的差異，以及需要使用者決定的事項（例如是否合併）。
