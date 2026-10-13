# Python 設計新增項目：實作紀錄

> 計畫見 [plan.md](./plan.md)。只記錄與 plan 不同的決定、過程中的發現與驗證結果。

分支 `chore/python-refine`（沿用，原名 `chore/python-fixes`）。

| 階段 | commit | 說明 |
|---|---|---|
| 基準點 | `7b0b032` | 文件 commit（資料夾整理、本計畫、`todo.md` 調整），`check.sh` 633 passed |
| A 組 | `5ce3a69` | `StepStatus`、`frozen`、`first_page`（642 passed） |

---

# 驗證結果

| 項目 | 結果 |
|---|---|
| `scripts/check.sh` | 通過，**642 passed**（import-linter 4 份契約 kept） |
| 9 個 CLI `--help` | 9/9 正常 |
| `pytest tests/integration -m "not cost"` | 5 passed |
| `pytest tests/integration -m cost` | **6 passed**（204 s） |
| 殘留裸字串 `"success"`／`"failed"` | 只剩 `documents.py:339` 的統計欄位鍵與 `status.py` 的定義 |

測試數 633 → 642，共 +9：`test_step_status`（4）、`test_assets`（4），以及 `test_imports.py` 自動為新模組 `status` 多產生的 1 個參數化案例。

**測試先行的確認**：`test_assets` 在舊程式碼上 3 個失敗（兩個 `frozen`、一個 `first_page` 拋 `IndexError` 而非 `ValueError`）、1 個通過，改後全部通過。

**付費測試費用**（僅就輸出中可見的摘要）：`test_prepare` 的 Prepare Pipeline 總計 $0.0666；爬蟲測試的 exclude_words LLM 呼叫另有 $0.0104 與 $0.0115。agent 與 rag query 等測試沒有費用摘要，未統計。全部通過，所以沒有重跑基準點。

---

# 與 plan 不同的地方

## 分支處理的意外

plan 原本寫「從目前分支切出 `chore/python-additions`」，使用者要求改為不另開分支。處理過程中發現兩件事：

- 使用者先前已把 `chore/python-fixes` 改名為 `chore/python-refine`（reflog 可見），我沿用舊名稱寫進文件，所以不能假設分支名。
- 我建立 `chore/python-additions` 並提交文件的指令，在介面顯示為「被拒絕」之後其實仍已執行。更正方式：把 `chore/python-refine` 快轉到該 commit、刪除多開的分支，並以 `--amend` 修正基準點 commit（`1270086` → `7b0b032`，兩者只差 plan 與 `python_fixes/dev.md` 內的分支名稱）。

同時更新了 `python_fixes/dev.md` 的分支說明，並把這個偏好記入記憶（接續工作留在目前分支，動手前先確認分支名）。

## A1 的小調整

- plan 提到 `if not entry.summarize_status`／`if entry.summarize_status:` 因 `PENDING` 為 falsy 而語意不變，可以保留。實作時改成明確比較 `== StepStatus.PENDING`／`!= StepStatus.PENDING`（`augmenter.py` 兩處），因為「讓三態的含意一眼看得出來」正是這項的目的。
- 測試裡的 fake（`FakeVLM` 回傳 `"success"`）因此會讓 `ImageEntry.summarize_status` 暫時持有一般字串，但 `StepStatus.SUCCESS == "success"` 為真，比較仍正確，測試都不需修改。

## 驗證時遇到的小狀況

- 直接執行 `pyright src` 會因沒有使用專案的 venv 而出現 90 個 import 無法解析的誤報；應使用 `scripts/check.sh`（內部為 `uv run pyright`）。
- ruff 的 `B018` 擋下測試裡單獨一行的 `asset.first_page`，改成 `_ = asset.first_page`。
- 第一次套用 `StepStatus` 替換的腳本因 `documents.py` 的 import 錨點寫錯，在斷言處中止；斷言發生在寫檔之前，沒有任何檔案被改到，修正錨點後重跑。

---

# 評估後不做的項目

調查階段決定不做、並已從計畫與 `todo.md` 移除的項目，保留簡短理由：

- **`dataclass(slots=True)`**：pyright 已經擋得住屬性名拼錯（實測），省記憶體也沒有意義（1 萬個 `ImageEntry` 只差約 0.5 MB，單張圖的 base64 就約 0.27 MB）。
- **`lru_cache`／`_representatives()` 的 O(n²)**：問題存在（`is_success` 逐筆呼叫，1000 份文件 73 ms、3000 份 0.9 s、5000 份 4.7 s），但現有資料最多的站點只有 71 份文件（< 1 ms），不值得改；`lru_cache` 本身也不適用（依賴可變狀態、方法上會持有 `self`）。
- **`match`／`case`**：`_fetch_once` 的狀態碼判斷是單一布林式，`overrides.py` 的分流混合 origin 與型別身分判斷，沒有適合的套用點。
- **`itertools.batched`**：`src/` 沒有任何手寫的批次切分。
- **`asyncio.TaskGroup`**：要保留「單一失敗不拖垮整批」就得在每個任務內捕捉所有例外，與現行 `create_task` 加 `as_completed` 等價。

# 後續建議

- `ImageEntry.base64_url` 在整個 run 期間保存每張圖的完整 base64；若日後要降低記憶體，應在描述完成後釋放它。
- 其餘未處理的修正項目（`WebpageMarkdownCleaner` 的 static、計時／重試裝飾器）仍在 `todo.md`。
