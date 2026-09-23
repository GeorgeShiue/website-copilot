# Implementation Log

> 對應規劃文件：[plan.md](./plan.md)

---

## Plan 1 執行紀錄：`save_to_runs`

### 1. `workflow_helper.py::create_run_context` 改成可選建立

- 新增 `save_to_runs: bool = True` 參數，回傳型別從 `tuple[RunManager, str]` 改成 `tuple[RunManager | None, str]`：`save_to_runs=False` 時在 `RunManager.for_run(...)` 之前直接 `return None, run_title`，完全不觸碰檔案系統。
- `run_workflow_context(run_title, run_manager: RunManager | None)`：把 `save_logging_file(run_manager.log_path)` 與 `run_manager.log_run_paths("init")` 包進 `if run_manager is not None:`；`log_run_time`/`log_session` 兩個純 console 輸出維持無條件執行。`_WorkflowContext.__exit__` 本來就已經是 `if self._run_manager is not None and exc_type is None:`，不用改。

**決策過程**：第一版設計原本只打算讓 `save_to_runs=False` 跳過「寫結果檔案」，`RunManager.for_run(...)` 仍然照常呼叫（也就是 `runs/` 底下還是會有一個只含空 `results/` 資料夾跟 `terminal.log` 的時間戳目錄）。使用者明確要求「`save_to_runs=False` 時應該完全不建立 `runs/` 目錄」，因此改成上述「回傳 `None`」的設計。

### 2. `workflow.py` 三個函式加上 `save_to_runs`

- `run_website_crawler`／`run_webpage_image_summarizer`／`run_rag_build` 簽名新增 `save_to_runs: bool = True`，呼叫 `create_run_context(..., save_to_runs=save_to_runs)`。
- 每個函式內把「存到 runs/」的所有呼叫合併進同一個 `if save_to_runs:` 區塊（含 `assert run_manager is not None` 做型別縮窄），放在 `if data_manager is not None:` 之前，並加上 `# ----- Save（存到 runs/） -----` / `# ----- Publish（publish 到 data/） -----` 註解明確分隔兩個階段。

**決策過程**：第一版是照抄原始程式碼的呼叫順序（`save_results_as_json`/`save_results_as_md` 在 publish 之前，但 `save_module_config_as_toml`/`save_run_config_as_toml` 留在 publish **之後**，跟原始碼一致）。使用者要求「把三個 run function 的儲存結果機制和儲存配置機制的程式碼寫在同一個 `if save_to_runs` 底下，並放在 `if data_manager is not None:` 前面，在程式碼上明確區分 save 和 publish」，因此把兩段合併成一個區塊、統一放到 publish 之前。

### 3. `DataManager` publish 方法改成自給自足

**問題**：`publish_crawl_results`／`publish_run_metadata` 原本是「複製 `runs/` 裡已經寫好的檔案」（依賴 `results_json_path`／`module_config_toml_path` 等 runs/ 路徑），這跟 Plan 1「不留 runs/ 複本」的目標矛盾——如果 `save_to_runs=False`，這些 runs/ 檔案根本不存在，publish 就沒東西可複製。

**改法**：

- `publish_crawl_results(site_id, results)`：拿掉 `results_json_path`/`results_folder_path` 兩個路徑參數，直接 `json.dump(results, ...)` + 逐頁寫 markdown（`_write_markdown_files` 共用 helper，`markdown_key="fit_markdown"`）。
- `publish_markdown(site_id, enhanced_results)`：拿掉 `results_folder_path` 參數，改用同一個 `_write_markdown_files`（`markdown_key="enhanced_markdown"`）。
- `publish_run_metadata(site_id, category, config, run_config=None, log_path=None)`：拿掉 `module_config_path`/`run_config_path` 兩個路徑參數，改成直接吃 `config`/`run_config` **物件**，呼叫 `save_module_config_as_toml`/`save_run_config_as_toml`（`utils/config_helper.py`，本身是純函式，只要給路徑就能序列化，不依賴 RunManager）直接寫到 `data/` 目的地。`log_path` 是唯一維持 copy-based 的參數——log 檔是執行期間寫入的實體檔案，沒有記憶體物件可序列化。
- 新增 `publish_generated_exclude_words(site_id, generation_result, raw_pages)`：重用既有的 `save_generated_exclude_words`（`run_persistence.py`）純函式，指向 `data/` 目的地。
- 三個舊的單一檔案 copy 方法 `publish_module_config`/`publish_run_config`/`publish_log`（外部無人直接呼叫，已用 grep 確認）直接刪除，邏輯內聯進新版 `publish_run_metadata`。

### 4. `run_rag_build` 移除獨立的 `save_vector_store_to_runs`

- 簽名移除 `save_vector_store_to_runs: bool = False`，內部呼叫 `create_rag(..., save_vector_store_to_runs=save_to_runs, ...)`（原本是獨立參數）。
- `BaseRunConfig`（`workflow_config.py`）新增 `save_to_runs: bool = True`；`RAGBuildRunConfig` 移除 `save_vector_store_to_runs` 欄位。
- `cli.py`：`save_to_runs = run_kwargs.pop("save_to_runs", True)`（跟既有的 `publish` pop 同一個模式，避免洩漏進 `run_rag_query`/`run_agent_query` 不接受這個參數的分支）。
- 呼叫端（`scripts/multi_site.py`、`src/test/test_main.py`、`src/test/test_module.py`）移除已刪除的 `save_vector_store_to_runs=True` 關鍵字參數（預設 `save_to_runs=True` 已是相同效果）。

### 5. Pylance/Pyright 型別修正

`create_run_context` 回傳型別從 `RunManager` 改成 `RunManager | None` 後，三個函式裡在 `if save_to_runs:` 區塊內存取 `run_manager.xxx` 全部被 Pyright 標記 `reportOptionalMemberAccess`（因為靜態分析看不出 `save_to_runs` 這個獨立布林變數跟 `run_manager is None` 之間的關聯）。修法：在每個確定 `run_manager` 不會是 `None` 的區塊開頭加 `assert run_manager is not None` 做型別縮窄；`run_rag_query`（沒有開放 `save_to_runs`，永遠會拿到真正的 `RunManager`）在 `create_run_context(...)` 呼叫後也加一行同樣的 assert。`uv run pyright` 確認 0 errors。

### Plan 1 驗證結果

- `test_run_rag_build_publish.py`／`test_runmanager_datamanager.py`／`test_run_agent.py`：36 passed。
- 完整非 slow 套件（`src/test -m "not slow"`）：**195 passed**，1 個既有無關失敗（`test_webpage_markdown_cleaner.py::test_save_generated_exclude_words`，用 `git stash` 確認在此輪改動之前就已失敗，`KeyError: 'Footer text'`）。
- 實際跑 `uv run python src/main.py --run.config-name test`（真實爬蟲 + LLM，花費 $0.0704，226 秒）：
  - `git status` 確認 `runs/` 沒有任何新增目錄／檔案（改動前最新的 runs/ 資料夾時間戳早於此次執行）。
  - `data/webpages/nculab/` 正確更新（`module_config.toml`／`results.json`／`results/*.md` 皆為本次修改，`exclude_words_report.json`／`generated_exclude_words.toml` 為本次新增）。
  - `data/rag/nculab/` 正確更新，log 顯示 `Milvus vector store already at data/rag/nculab/milvus.db, skipping publish`——證明 `save_to_runs=False` → `create_rag` 直接把向量庫建在 `data/` 目的地，`publish_vector_store` 的 self-copy 防護正確跳過多餘複製。

---

## Plan 2(a) 執行紀錄：統一 RunManager／DataManager 建立模式

### 分析（使用者要求先解釋差異再動手）

在動手前，先被要求「分析為什麼會有這種差異」。結論見 plan.md 的「為什麼原本不一致」一節（生命週期範圍、建立成本、用途三點不對稱）。使用者接著問「能否把 `data_manager` 的建立也併入 `create_run_context`」——回答：不建議，因為 (1) 兩者建立條件完全獨立（`DataManager` 不受 `save_to_runs` 影響），合併會誤導閱讀者；(2) `create_run_context`/`create_run_no_site_context` 還有 `run_rag_query`/`run_agent_*` 等完全不需要 `DataManager` 的呼叫端；(3) 會讓測試被迫互相耦合（本來只需要假造 `RunManager` 的測試被迫一起假造 `DataManager`）。使用者接受此結論，維持兩個獨立函式。

### 1. 第一版設計：`create_data_manager` 工廠函式

比照 `create_run_context` 的模式，在 `workflow_helper.py` 新增：

```python
def create_data_manager() -> DataManager:
    """建立 DataManager（永遠回傳實例；建立成本為零，不像 RunManager 需要條件式建立）。"""
    return DataManager()
```

三個函式改成 `data_manager = create_data_manager()`（無條件呼叫）+ `publish: bool = False` 參數取代 `data_manager: DataManager | None`；`run_rag_build` 的 `create_rag(..., data_manager=data_manager, ...)` 改成無條件傳入（不再依賴 `publish`，因為 `webpages_data_use_latest_results=True` 需要讀取，這跟要不要 publish 是兩回事）。

測試（`test_run_rag_build_publish.py`）改用 `patch("app.workflow.workflow.create_data_manager", return_value=...)`。

### 2. 最終規劃前的三個最後檢查（使用者要求列出模糊點再問）

規劃定案前被要求「列出目前計畫中模糊或矛盾之處」，逐一問過並定案：

1. **`data_manager` 建立時機**：crawler/summarizer 其實只有 `publish=True` 時才用得到，若無條件建立會導致 `publish=False` 時也多一次 `os.makedirs("data")` 副作用（先前是完全不碰）。使用者選擇「三個函式都無條件建立」（簡單一致優先於這個幾乎無害的 side effect）。
2. **`create_data_manager` 的 `base_folder` 參數**：目前沒有任何呼叫端會用到自訂值。使用者選擇拿掉，簡化成無參數版本。
3. **`multi_site.py::_check_published_files`**：內部其實沒呼叫任何 `DataManager` 方法，只讀 `.base_folder`。使用者選擇順便簡化成直接吃 `base_folder: str`，移除 `DataManager` import。
4. **測試改名**：`test_no_data_manager_does_not_publish` 在新設計下（不再有 `data_manager` 參數）語意不合。使用者確定改名為 `test_publish_false_does_not_publish`。

### 3. 移除 `create_data_manager`（使用者事後要求）

實作完成、驗證通過後，使用者指出「`create_data_manager` 只有直接建立 `DataManager()` 實例，取消此 function 並將建立直接寫在三個 run function 內，等到後續創建 data_manager 的動作變複雜再加回此 function」。改動：

- `workflow_helper.py` 移除 `create_data_manager` 函式與對應的 `DataManager` import。
- `workflow.py`：三處 `data_manager = create_data_manager()` 改回 `data_manager = DataManager()`（`sed` 批次替換），並加回 `from app.workflow.data_manager import DataManager` import。
- 測試改成 `patch("app.workflow.workflow.DataManager", return_value=data_manager)`（直接 patch class 本身，取代 patch 工廠函式）。

### Plan 2(a) 驗證結果

- 第一版（含 `create_data_manager`）：完整非 slow 套件 195 passed（同一個既有無關失敗）；`uv run pyright` 0 errors；實際跑 `main.py --run.config-name test` 驗證通過。
- 移除 `create_data_manager` 後重跑：195 passed（同一個既有無關失敗）；`uv run pyright` 0 errors。

---

## Plan 2(b) 執行紀錄：crawler／summarizer 儲存路徑拆分

### 第一版設計：`data/webpages/{site_id}/crawl_results/` 子資料夾

最初分析認定問題只出在 `data/`（`runs/` 天生已用 `module` 名稱分開，不會碰撞），提出把 crawler 的 markdown 輸出改成寫到 `data/webpages/{site_id}/crawl_results/` 子資料夾，`results.json` 與 `results/`（summarizer 用）維持原位不動——因為 `RAG.md_docs_folder_path` 讀的就是 `data/webpages/{site_id}/results/`，這是 RAG 建庫實際消費的最終版本，不能動。

實作並驗證（195 passed、pyright 0 errors、實測 `main.py` 確認 `crawl_results/*.md` 為原始 `fit_markdown`、`results/*.md` 維持 `enhanced_markdown`）後，使用者要求改成「將 crawler 的儲存結果改為存在 `data/raw_webpages/{site_id}`」——更大幅度的頂層目錄拆分，而非子資料夾改名。

### 澄清 `results.json` 該不該一起搬（兩輪 AskUserQuestion）

使用者原始指示「全部移動過去，但是 RAG 讀取路徑不變」字面上互相矛盾：`results.json` 若整個搬到 `raw_webpages/`，`RAG._load_results_json()`（讀 `webpages_data_folder_path/results.json`）勢必要跟著改路徑才找得到檔案，不可能「完全不變」。

第一輪提問列出兩個維度（`results.json` 要不要跟著搬、其他 metadata 檔要不要跟著搬）分別問，但使用者的回答（「全部移動過去，但是 RAG 讀取路徑不變」）仍是字面矛盾的組合，因此發起第二輪、用具體目錄樹列出兩種可能設計逼近使用者真正的意圖：

- 方案 A：RAG 改成從兩個位置分別讀取（改 `rag.py`/`rag_config.py`/`rag_factory.py`）。
- 方案 B：crawler 同時發布到兩個位置（`raw_webpages/` 當真正歸檔，`webpages/results.json` 留一份複本給 RAG 用，RAG 完全不用改）。

使用者的最終答案是**第三個、前兩輪都沒問到的設計**：「crawler 留一份在 `data/raw_webpages` 後，summarizer 會再留一份到 `data/webpages`，因此不影響 RAG 讀取」——也就是 `webpages/results.json` 不是 crawler 複製過去的靜態副本，而是由 **summarizer** 用它自己手上的 `enhanced_results`（已經是 crawl_results 疊加 `enhanced_markdown` 的完整結果）重新發布，形成 plan.md 定案的最終設計。

**驗證這個設計可行的前置確認**：讀了 `webpage_image_summarizer.py::_summarize_crawl_results_images()` 原始碼，確認 `crawl_result["enhanced_markdown"] = ...` 是**就地**修改傳入的 `crawl_results` 每頁 dict 並回傳同一個物件（非建立新 dict、非只回傳部分欄位）——所以 `enhanced_results` 保證含有 `url`/`images`/`metadata`/`crawl_info`/`fit_markdown` 等全部原始欄位，`publish_markdown` 可以安全地把它整包寫成 `results.json`，`RAG._build_file_metadata()` 依賴的 `page_info.get("url")`/`metadata.get("page_type")` 等欄位不會遺失。

### 實作

- `DataManager.publish_crawl_results`：目的地從 `data/webpages/{site_id}/` 改成 `data/raw_webpages/{site_id}/`（`results.json` + `results/*.md`，皆為 crawler 原始欄位）。
- `DataManager.publish_generated_exclude_words`：目的地同樣改成 `data/raw_webpages/{site_id}/`。
- `DataManager.publish_markdown`：新增 `results.json` 寫入（用 `enhanced_results` 整包 `json.dump`），markdown 部分維持原邏輯不變，目的地仍是 `data/webpages/{site_id}/`。
- `workflow.py::run_website_crawler` 的 `publish_run_metadata` 呼叫：`category` 參數從 `"webpages"` 改成 `"raw_webpages"`。
- `test_runmanager_datamanager.py::test_publish_crawl_results`：斷言路徑改成 `data/raw_webpages/nculab/`，markdown 子資料夾名稱改回 `results`（不再需要 `crawl_results` 這個中繼命名——因為現在跟 `webpages/` 已經是完全不同的頂層目錄，不會撞名）。
- `README.md`：`data/` 目錄樹說明同步更新，新增 `raw_webpages/` 區塊並註明 `webpages/results.json` 現在含 `enhanced_markdown`。

### 順便修正的既有 bug：`multi_site.py` 誤用 config 名稱當 site_id

修改 `_check_published_files` 呼叫（加入 `"raw_webpages"` 到驗證的 category 迴圈）時發現：原本呼叫 `_check_published_files(site_label, "data", rag_config, cat)` 的第三個參數傳的是 `rag_config`（例如 `"test_nculab"`，crawler config **名稱**），但實際發布路徑用的 `site_id` 是 config 內部欄位（`"nculab"`，兩者不同——`configs/rag/test_nculab.toml` 的 `site_id = "nculab"`）。這是一直存在、跟本次改動無關的既有 bug（驗證邏輯一直在檢查錯誤的目錄），因為正好改到同一行程式碼，一併修正為傳 `site_label`（就是 `site["crawler"].replace("test_", "")` 算出來的正確 site_id）。

### Plan 2(b) 驗證結果

實際跑 `uv run python src/main.py --run.config-name test`：

- `git status` 顯示 `data/raw_webpages/` 為全新目錄（`??`），`data/webpages/nculab/` 正常更新（`module_config.toml`/`results.json`/`results/*.md` 皆為 `M`）。
- 檢查發現兩個從**上一輪驗證**（改用 `crawl_results/` 子資料夾那版、被使用者推翻前）遺留在 `data/webpages/nculab/` 的殘留檔案（`exclude_words_report.json`/`generated_exclude_words.toml`，mtime 早於本次執行）——手動刪除清理。
- 逐頁比對兩份 `results.json`：
  ```
  data/webpages/nculab/results.json     → labintro 頁欄位: crawl_info, enhanced_markdown, fit_markdown, images, metadata, url
  data/raw_webpages/nculab/results.json → labintro 頁欄位: crawl_info, fit_markdown, images, metadata, url
  ```
  `webpages/` 比 `raw_webpages/` 多一個 `enhanced_markdown`，符合設計。
- `diff` 比對 `results/labintro.md` 內容分別對應各自 `results.json` 裡的 `enhanced_markdown`／`fit_markdown` 欄位，內容一致（唯一差異是 `print()` 產生的尾端換行，非真實內容差異）。
- 完整非 slow 套件重跑：195 passed（同一個既有無關失敗）；`uv run pyright` 0 errors。

### 額外確認：`runs/` 不需要對應調整

使用者接著問「`runs/` 的儲存路徑是否也一併更改為 `raw_webpages`」。查證：`run_manager.py`/`run_persistence.py`/`workflow_helper.py` 全文 grep 找不到任何 `"webpages"` 字串——`runs/` 的路徑結構是 `runs/{timestamp}/{module}/{site_id}/{run_name}/`，`module` 直接就是 `website_crawler`/`webpage_image_summarizer` 模組自己的名稱，且每次呼叫都是新的 `timestamp`，兩者從最頂層就已經是不同目錄樹（實際列出 `runs/` 驗證：`runs/20260922_121936/website_crawler` vs `runs/20260922_153534/webpage_image_summarizer`，時間戳跟模組名都不同）。`data/` 需要拆分是因為 `DataManager` 有固定的「發布分類」目的地（不管誰發布都是同一個 `data/webpages/{site_id}/`），`RunManager` 沒有這種設計，不需要也沒有東西可以改名成 `raw_webpages`。**未改動任何檔案**。

---

## Final Summary

### 變更檔案總表

| 檔案 | Plan 1 | Plan 2(a) | Plan 2(b) |
|------|--------|-----------|-----------|
| `src/app/workflow/workflow_helper.py` | `create_run_context` 改可選建立（`save_to_runs`）；`run_workflow_context` 對應調整 | 曾新增又移除 `create_data_manager` | — |
| `src/app/workflow/workflow.py` | 三個 `run_*` 函式新增 `save_to_runs`，Save/Publish 區塊合併重排；`run_rag_build` 移除獨立 `save_vector_store_to_runs` | 三個函式 `data_manager` 參數 → `publish` 參數，直接 `DataManager()` 建立 | crawler 的 `publish_run_metadata` category 改 `"raw_webpages"` |
| `src/app/workflow/data_manager.py` | `publish_crawl_results`/`publish_markdown`/`publish_run_metadata` 改自給自足序列化；新增 `publish_generated_exclude_words`；刪除 `publish_module_config`/`publish_run_config`/`publish_log` | — | `publish_crawl_results`/`publish_generated_exclude_words` 目的地改 `raw_webpages/`；`publish_markdown` 新增 `results.json` 寫入 |
| `src/app/configs/workflow_config.py` | `BaseRunConfig` 新增 `save_to_runs`；`RAGBuildRunConfig` 移除 `save_vector_store_to_runs` | — | — |
| `src/cli.py` | pop 並轉傳 `save_to_runs` | pop 並轉傳 `publish`（取代建構 `DataManager`） | — |
| `src/main.py` | 三個呼叫加 `save_to_runs=False` | 移除手動建構 `DataManager`，改用 `publish=True` | — |
| `scripts/multi_site.py` | 移除已刪除的 `save_vector_store_to_runs=True` | 移除 `DataManager` 建構；`_check_published_files` 改吃 `base_folder: str` | 驗證迴圈加入 `"raw_webpages"`；修正誤用 config 名稱當 site_id 的既有 bug |
| `src/test/dev/test_run_rag_build_publish.py` | fixture／測試改用新的 publish 序列化邏輯 | `data_manager=` 改 `publish=True`；patch 目標從 `create_run_context` 延伸到 `DataManager` | — |
| `src/test/dev/test_runmanager_datamanager.py` | `test_publish_crawl_results` 改用新簽名 | — | 斷言路徑改 `data/raw_webpages/` |
| `src/test/test_main.py`、`src/test/test_module.py` | 移除已刪除的 `save_vector_store_to_runs=True` | — | — |
| `README.md` | — | — | `data/` 目錄樹說明更新 |

### 測試結果

三輪皆為：完整非 slow 套件 **195 passed**，1 個既有無關失敗（`test_webpage_markdown_cleaner.py::test_save_generated_exclude_words`，已用 `git stash` 確認改動前即存在）；`uv run pyright` 均為 0 errors。每輪都實際跑過一次 `uv run python src/main.py --run.config-name test`（真實爬蟲 + LLM + RAG 建庫）驗證行為正確。

### 已知限制 / 未處理事項

| 類別 | 說明 |
|------|------|
| **`run_rag_query`/`run_agent_*` 未納入 `save_to_runs`/`publish`** | 這幾個函式本來就沒有 publish 機制、也不在 main workflow 使用範圍內，本輪刻意不動（見 plan.md 範圍界定） |
| **驗證過程殘留檔案** | 過程中因為第一版設計（`crawl_results/` 子資料夾）跑過真實流程，被使用者推翻後這批殘留檔案（`data/webpages/nculab/exclude_words_report.json`/`generated_exclude_words.toml`）手動清理過；`data/` 本身有被 git 追蹤，之後如需要可用 `git checkout -- data/` 復原到本輪改動前的版本 |
