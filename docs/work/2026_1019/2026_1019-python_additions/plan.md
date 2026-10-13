# Python 設計新增項目：實作規劃

> 對應 [todo.md](../../todo.md)「Python 優化 → 新增」。前一批修正見 [python_fixes/plan.md](../2026_1019-python_fixes/plan.md)，已採用的設計見 [docs/code/python.md](../../../code/python.md)。
>
> 範圍只含三個項目：`StrEnum` 取代狀態字串、`frozen=True`、`Asset.first_page` 的明確錯誤。**先調查再規劃**：todo 的原寫法與實際程式碼有落差，下方「調查結論」說明每個項目怎麼做、為什麼這樣做。

## Context

todo 的「新增」是從通用的 Python 進階主題比對出來的候選項目，不是從痛點出發。逐項查過程式碼並實測後，留下三項有實際價值的：

- **`StrEnum`**（價值最高）：約 27 處裸字串比較，是目前沒有任何工具防護的缺口。專案歷史上出過實例：上一輪 code cleanup 發現 `"failure" in download_status` 永遠為 False（實際值是 `"failed"`）。
- **`frozen=True`**：把「共用物件不應被修改」從慣例變成保證。
- **`Asset.first_page`**：todo 寫的「建構時驗證」行不通，改成明確的錯誤訊息。

## 調查結論

| todo 項目 | 調查發現 | 結論 |
|---|---|---|
| `StrEnum` 取代狀態字串 | `download_status`／`summarize_status` 共約 27 處字串比較／賦值（`augmenter.py` 約 19、`documents.py` 6、`image_captioner.py` 2）；`ImageEntry` 不會被序列化（`asdict` 只用在統計），沒有相容性問題。pyright（basic）擋得住「把裸字串指派給 enum 欄位」，但擋不住「與拼錯的字串比較」，而後者佔大多數 | **做**（A1） |
| `frozen=True` 候選 | `AssetRef`、`ParsedDocument`、`ParsedImage` 建立後沒有欄位被賦值。`documents.py:254` 把 `AssetRef` 從多個資源收集到同一份清單，`ParsedDocument` 存在 `self._parsed[sha]` 由內容相同的多份文件共用，都是共用物件 | **做**（A2） |
| 建構時保證 `Asset` 不變式 | **前提不成立**：`collectors.py:27,112`、`documents.py:399` 都是 `Asset(url, kind)`（空 `refs`）建立後才立刻 `refs.append(...)`，在 `__post_init__` 檢查非空會讓正常流程失敗 | **改做**：`first_page` 在 `refs` 為空時拋出附 url 的明確錯誤（A3） |

## 順序與理由

單一組別 **A**，內部順序 A1 → A2 → A3：A1 範圍最大、涉及 VLM 與下載路徑，先做；A2、A3 都很小。三項都不改行為，pyright 能協助找出漏改。

**分支**：沿用目前的分支 `chore/python-refine`，不另開分支。兩批修改的檔案有重疊（`augmenter.py`、`documents.py`），接在修正之後可避免衝突。

## 執行流程

1. **基準點**：在 `chore/python-refine` 上，文件（本計畫、資料夾整理、`todo.md` 調整）先以單獨 commit 提交，記錄 hash 作為基準點。基準：`check.sh` 633 passed。
2. **實作 A 組**（A1 → A2 → A3，需要時測試先行）→ 共同驗證關卡 → 通過後**一個 commit**；未通過就在組內修正，不提前 commit。
3. **全部完成後**：最後驗證 → 寫 `dev.md` → 向使用者回報。

### 停止條件

除了下列情況，全程不中斷：

- 同一個驗證關卡經合理嘗試仍無法修復。
- 需要計畫外的決定（例如要改公開介面、或改動會明顯改變行為）。
- 發現計畫的前提不成立，繼續做會偏離原意。

遇到時停下來、保持工作區可還原，並向使用者說明狀況與選項，**不跳過、不硬做**。

### 自動執行時的判斷規則

- **A3**：做最小版本（明確錯誤訊息），不重構 `Asset` 的建構方式。

## 共同驗證關卡

組別完成後（commit 前）：

- `scripts/check.sh`（undersort、ruff、import-linter、pyright、`pytest tests/unit`、widget 檢查）。
- 9 個 CLI `--help` 冒煙測試（頂層、`prepare`、`serve`、`run`，以及 `run` 的 5 個子命令）。本批不動 CLI 與 config，不需要與基準點逐字比對輸出。
- `pytest tests/integration -m "not cost"`。

**測試先行**：會改變行為或沒有現成測試覆蓋的項目，先補測試並在舊程式碼上確認結果，再改實作。

---

# A 組：型別與資料模型

## A1：`StrEnum` 取代狀態字串

**問題**：`summarize_status` 實際上是三態（尚未進行、成功、失敗），卻用裸字串表示，且「尚未進行」是空字串。含意散落在不同寫法裡：`not entry.summarize_status` 表示尚未有結果（`augmenter.py:382`）、`entry.summarize_status`（truthy）表示已有結果不論成敗（:533）、`!= "success"` 同時包含尚未進行與失敗（:594）、重試時設回 `""`（:479）。

**新增** `ingestion/augmentation/status.py`（無相依，避免循環引用）：

```python
class StepStatus(StrEnum):
    PENDING = ""          # 尚未進行
    SUCCESS = "success"
    FAILED = "failed"
```

**範圍**：
- `ImageEntry.download_status`／`summarize_status`（`augmenter.py`）、`DocumentEntry.download_status`（`documents.py`）的型別與預設值（`StepStatus.PENDING`）。
- 所有字串比較與賦值改用 `StepStatus.*`（約 27 處）。
- `image_captioner` 的 `_agenerate_image_caption` 與批次結果 tuple 的型別改為 `StepStatus`。

**已驗證的行為**（小實驗）：
- `StepStatus.PENDING` 的值是 `""`，仍為 falsy，所以現有的 `if not entry.summarize_status`、`if entry.summarize_status:` 語意不變。
- `StepStatus.SUCCESS == "success"` 為真，`{"success": 1}[StepStatus.SUCCESS]` 可查，所以測試裡的 fake（`FakeVLM` 回傳 `"success"`）與 `test_llm_provider` 的斷言 `== ("caption", "success")` **不需修改**。
- `StepStatus("x")` 拋 `ValueError`，可擋住不合法的狀態值。

**陷阱，不要動**：
- `documents.py` 的統計 dict 鍵 `"success": stats.success`，以及 `PageStats.success`、測試裡的統計 dict 鍵 `"success"`，是**統計欄位名稱**，不是狀態值。
- `ImageEntry` 沒有被序列化（`asdict` 只用在 `RoundStats`／`PageStats`），所以沒有檔案格式相容問題。

**限制**：pyright（basic）不會擋掉「留下的裸字串比較」，所以驗證要靠 `grep`。

**測試**：新增 `test_step_status.py`：與 `str` 相等、`PENDING` 為 falsy、非法值拋 `ValueError`。
**驗證**：改完後 pyright 會抓出仍把裸字串指派給 `StepStatus` 欄位的地方；再 `grep '"success"\|"failed"'`，剩下的應只有統計欄位名稱。

## A2：`frozen=True`

**問題**：有些物件被多處共用，但沒有機制保證它們不被修改。`documents.py:254` 的 `refs = [ref for member in members for ref in member.refs]` 把 `AssetRef` 收集到同一份清單；`ParsedDocument` 存在 `self._parsed[sha]`，內容相同的多份文件共用同一個物件。目前沒人修改它們，所以沒有 bug；日後若有人改了共用物件，影響會悄悄擴散到其他文件。

**範圍**：`AssetRef`（`assets.py`）、`ParsedDocument`（`document_parser.py`）、`ParsedImage`（`images.py`）。

**依據**：建立後沒有欄位被賦值（grep 確認）；pyright 本來就會擋住 frozen 欄位的賦值，新增的是執行期保證與表達意圖。
**不處理**：CLI 的 dataclass（由 tyro 建立）、繼承非 frozen 基底的 `*RunConfig`。
**注意**：`ParsedDocument.images` 是 list，`frozen` 只防止重新指派，不防止 `append`；`frozen` 會讓 `__hash__` 依欄位產生，含 list 的物件不可雜湊，但專案沒有把它們放進 set 或當 dict 鍵。
**測試**：對 `AssetRef` 賦值拋 `FrozenInstanceError`。

## A3：`Asset.first_page` 的明確錯誤

**問題**：`refs` 為空時，`first_page` 拋 `IndexError: list index out of range`，沒有任何上下文。它被用在**回報失敗**的路徑上（`documents.py:317,321`、`augmenter.py:555`）：若哪天 collector 有 bug 造成空 `refs`，這個錯誤會發生在回報失敗的時候，蓋掉真正的失敗原因，而且那時 VLM 費用已經花掉。目前沒有已知的 bug，屬於預防。

**為什麼不能在建構時驗證**：`Asset(url, kind)` 以空 `refs` 建立後立刻 `refs.append(...)`（`collectors.py`、`documents.py` 共 3 處），所以 `__post_init__` 檢查非空行不通。

**做法（最小）**：`first_page` 在 `refs` 為空時拋 `ValueError`，訊息包含 `url`，說明「資源尚未有任何引用」。
**不做**：重構 `Asset` 的建構方式（`setdefault` 加 `append`），影響 3 個呼叫端且收益小。
**測試**：`Asset(url=..., kind="image").first_page` 拋 `ValueError`，訊息含 url；有引用時行為不變。

---

# 完成後同步 todo.md

三項都完成後，從 `todo.md` 刪除對應項目。

# 驗證（整體完成後）

1. `scripts/check.sh` 通過、9 個 CLI `--help` 正常。
2. `pytest tests/integration -m "not cost"` 通過。
3. 付費整合測試 `pytest tests/integration -m cost`：**只跑一次**（A1 讓狀態值流經真實的 VLM 與下載路徑，值得用真實流程驗證）。
   - 缺金鑰或無網路時，記錄為「未執行」並在回報中說明，不視為失敗。
   - 失敗時先在基準點重跑失敗的測試；基準點也失敗代表是既有問題或外部因素，記錄但不阻擋，只有基準點通過、改動後失敗才算回歸。
   - 記錄測試輸出中的費用摘要。
4. 與基準對照：測試數（633 起）、`grep '"success"\|"failed"'` 的殘留清單。

# 完成後：dev.md 與回報

驗證結束後，寫 `docs/work/2026_1019/2026_1019-python_additions/dev.md`（格式同 `python_fixes/dev.md`：只記錄與 plan 不同的決定、過程中的發現與驗證結果）：

- 基準點與 commit hash。
- 驗證結果（`check.sh` 通過的測試數）。
- 與 plan 不同的決定、過程中發現的問題。
- 付費整合測試的結果（通過數、失敗或未執行的原因、費用摘要）。

最後向使用者回報：完成的項目與 commit、驗證結果、與 plan 的差異，以及需要使用者決定的事項（例如是否合併）。
