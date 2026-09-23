# Main workflow 留檔機制優化計畫（nculab）

## Context

`src/main.py` 是正式（production）workflow，依序呼叫 `run_website_crawler` → `run_webpage_image_summarizer` → `run_rag_build`。這三個函式原本不論有沒有傳 `data_manager`，都會**無條件**把 `results.json`、markdown 檔、`module_config.toml`、`run_config.toml` 存一份到 `runs/`；只有「額外」在 `data_manager is not None` 時才會再 publish 一份到 `data/`（供 chat server 讀取）。這導致正式流程每次執行都會在 `runs/` 留下一份多餘、之後永遠不會被讀取的複本。

對應 `docs/work/todo.md`「優化 main workflow → 留檔機制」項目，分兩輪進行：

- **Plan 1**：讓 main workflow 可以只做 publish、不留 `runs/` 複本——把「存到 `runs/`」與「publish 到 `data/`」拆成兩個完全獨立、可自由開關的行為。**已完成**。
- **Plan 2**：
  - (a) `RunManager` 目前在每個 `run_*` function 內部自行建立，但 `DataManager` 卻是外部注入——分析這個不一致的根本原因，並統一兩者的建立模式，同時加上 `publish` 參數。
  - (b) crawler 跟 image summarizer 目前發布到 `data/` 的預設路徑完全相同，導致只有 summarizer 的結果會留下來（crawler 的原始輸出被覆寫）——拆分兩者的儲存路徑。

兩輪的實際執行過程、決策修正、以及過程中發現的既有 bug，記錄於 [dev.md](./dev.md)。

---

## Plan 1：`save` — 讓 runs/ 儲存變成可選

### 問題

三個 `run_*` function（[workflow.py](../../../../src/app/workflow/workflow.py)）目前無條件呼叫 `RunManager.for_run(...)` 建立時間戳目錄、無條件寫入 `results.json`/`results/*.md`/`module_config.toml`/`run_config.toml`；`data_manager is not None` 只決定要不要「額外」publish 到 `data/`。main workflow 每次執行都會因此在 `runs/` 留下永遠不會被讀取的複本。

### 設計

1. `run_website_crawler`／`run_webpage_image_summarizer`／`run_rag_build` 新增 `save: bool = True` 參數。
2. **`save=False` 時必須完全不建立 `runs/` 目錄結構**（不只是跳過結果檔案）——`create_run_context`（`workflow_helper.py`）直接改成 `save=False` 時回傳 `(None, run_title)`，完全不呼叫 `RunManager.for_run(...)`，回傳型別改成 `RunManager | None`。`run_workflow_context` 對應在 `run_manager is None` 時跳過 log 檔相關操作（`save_logging_file`/`log_run_paths`）。
3. 每個函式內把「存到 runs/」的所有呼叫（`save_generated_exclude_words`／`save_results_as_json`／`save_results_as_md`／`save_module_config_as_toml`／`save_run_config_as_toml`）合併進**同一個** `if save:` 區塊，放在 `if data_manager is not None:` 之前，讓 Save／Publish 兩個階段在程式碼上明確區分。
4. `DataManager` 的 publish 方法（`publish_crawl_results`／`publish_markdown`／`publish_run_metadata`）原本是「複製 `runs/` 裡已經寫好的檔案」，代表 publish 本來就依賴 runs/ 先寫過一次——這與「不留 runs/ 複本」的目標矛盾，因此一併改成**直接從記憶體中的物件序列化**（`results` dict／`config`／`run_config` 物件），不再依賴任何 runs/ 路徑存在。`publish_module_config`／`publish_run_config`／`publish_log` 三個舊的單一檔案 copy 方法因此變成死碼，一併刪除，邏輯內聯進新版 `publish_run_metadata`。
5. `run_rag_build` 的向量庫本來就是這個階段的「結果」，不再保留獨立的 `save_vector_store_to_runs` 參數，改成統一由 `save` 驅動 `create_rag(save_vector_store_to_runs=save, ...)`——`save=True` 時向量庫建在 `runs/`（現行預設行為），`save=False` 時 `create_rag` 直接把向量庫建在 `data/rag/{site_id}/milvus.db`（`RAGConfig` 的預設值本來就是這個路徑），`DataManager.publish_vector_store` 已有 `realpath` 自我複製防護，成為安全的 no-op copy。
6. `BaseRunConfig`（`workflow_config.py`）新增 `save: bool = True`，取代 `RAGBuildRunConfig` 原本的 `save_vector_store_to_runs` 欄位；`cli.py` 比照既有的 `publish` 欄位處理方式，把 `save` 提前從 `run_kwargs` pop 出來，避免洩漏進 `run_rag_query`/`run_agent_query` 等沒有這個參數的分支。
7. `main.py` 三個呼叫都加上 `save=False`。

### 驗證方式

1. 單元測試：`test_run_rag_build_publish.py`／`test_runmanager_datamanager.py`／`test_run_agent.py` 全過；完整非 slow 套件確認沒有新增回歸。
2. `uv run pyright` 確認型別檢查通過。
3. 實際跑一次 `uv run python src/main.py --run.config-name test`，確認 `runs/` 完全沒有新增任何目錄／檔案，`data/webpages/nculab/`、`data/rag/nculab/` 正確產生且內容正確。

---

## Plan 2(a)：統一 RunManager／DataManager 的建立模式

### 為什麼原本不一致

`RunManager` 在每個 `run_*` function 內部建立，`DataManager` 卻由呼叫端（`main.py`／`cli.py`／`scripts/multi_site.py`）建立後注入。分析後確認這不是隨意造成的，而是反映兩者本質不同：

- **生命週期範圍不同**：`RunManager` 代表「這次呼叫自己的執行紀錄」，`module`／`timestamp` 都在呼叫當下才決定，完全侷限在單次呼叫內；`DataManager` 代表「這個 site 目前已發布的狀態」，`base_folder="data"` 固定不變，語意上橫跨整個 pipeline（main.py 建立一個實例共用給三個階段），甚至還會被呼叫端在 pipeline 結束後拿去做事後驗證（`multi_site.py`）。
- **建立成本不同**：`RunManager.for_run(...)` 建立當下就會 `os.makedirs` 出一整棵時間戳目錄樹，有實體副作用；`DataManager.__init__` 只有 `os.makedirs(base_folder, exist_ok=True)`，建立成本為零。
- **用途也不對稱**：`data_manager` 在 `run_rag_build` 裡不只用來 publish，`create_rag(..., data_manager=data_manager)` 在 `webpages_data_use_latest_results=True` 時還拿它來**讀取**資料來源路徑——這跟「要不要 publish」是兩件獨立的事。

### 設計

1. `DataManager` 改成在三個 `run_*` function 內部直接 `DataManager()` 建立（**不**額外包一層工廠函式——曾經引入 `create_data_manager()`，但因為內容只有 `return DataManager()`，價值不足以獨立成函式，實作後拿掉了；見 dev.md）。
2. 三個函式新增 `publish: bool = False` 參數取代 `data_manager: DataManager | None = None` 參數，語意跟 `save: bool` 對稱。
3. `DataManager` **永遠**建立（不像 `RunManager` 由 `save` 決定生死）——`run_rag_build` 無條件把它傳給 `create_rag(..., data_manager=data_manager, ...)`，讀取（`webpages_data_use_latest_results`）與 publish 兩個用途因此完全解耦；三個函式統一都無條件建立，即使 crawler／summarizer 只有 `publish=True` 時才用得到，換取三個函式建立方式一致、可預期。
4. `main.py`／`cli.py`／`scripts/multi_site.py` 移除手動建構 `DataManager` 的程式碼，改傳 `publish=True`（main workflow／multi_site 腳本永遠要 publish）或 `publish=publish`（cli.py，來源同樣是從 `run_kwargs` pop 出來、跟 `save` 同一個模式）。
5. `scripts/multi_site.py::_check_published_files` 內部其實沒有呼叫任何 `DataManager` 方法、只讀了 `.base_folder` 固定字串，順便簡化成直接吃 `base_folder: str`，不用建構 `DataManager` 實例、也不用 import 這個類別。

### 驗證方式

同 Plan 1；額外用 `patch("app.workflow.workflow.DataManager", return_value=...)` 取代舊的 `data_manager=` 參數注入方式改寫 `test_run_rag_build_publish.py`。

---

## Plan 2(b)：website crawler 與 webpage image summarizer 儲存路徑拆分

### 問題

`run_rag_build` 需要的 markdown 是 image summarizer 增強後的版本（`RAG.md_docs_folder_path` 讀的是 `data/webpages/{site_id}/results/`），但 crawler 的 `publish_crawl_results` 跟 summarizer 的 `publish_markdown` 原本都寫到同一個 `data/webpages/{site_id}/results/` 資料夾、用同樣的檔名，pipeline 跑完後 crawler 自己的原始輸出（`fit_markdown`）完全被 summarizer 的 `enhanced_markdown` 覆蓋、無法單獨檢視。

（`runs/` 沒有這個問題：`RunManager` 的路徑本來就含有 `module` 名稱與各自獨立的時間戳，`runs/{ts}/website_crawler/...` 與 `runs/{ts2}/webpage_image_summarizer/...` 天生就是不同目錄，不需要也沒有東西可以拆分。）

### 設計（最終定案，過程中的兩次修正見 dev.md）

- **`data/raw_webpages/{site_id}/`**：crawler 專屬、完全獨立的頂層目錄，存放 `results.json`（僅含 `fit_markdown` 等原始欄位）、`results/*.md`（`fit_markdown`）、`module_config.toml`／`run_config.toml`／`terminal.log`／`generated_exclude_words.toml`／`exclude_words_report.json`。
- **`data/webpages/{site_id}/`**：維持原本結構跟路徑不變，但改由 summarizer 完整發布——`publish_markdown` 除了 `results/*.md`（`enhanced_markdown`）之外，**也一併寫 `results.json`**。這行得通是因為 `webpage_image_summarizer.summarize_crawl_results_images()` 是**就地**在 `crawl_results` 的每頁 dict 上疊加 `enhanced_markdown` 欄位再回傳（同一個物件），所以 `enhanced_results` 本身就是「原始欄位（url／images／metadata／crawl_info／fit_markdown）+ enhanced_markdown」的完整結果，不需要額外合併資料。
- **RAG 完全不用改**：`data/webpages/{site_id}/` 的目錄結構（`results.json` + `results/`）跟改動前一模一樣，`rag.py`／`rag_config.py`／`rag_factory.py` 零改動。

### 順便修正的既有 bug

`scripts/multi_site.py::run_site_pipeline` 呼叫 `_check_published_files(site_label, "data", rag_config, cat)` 時，第三個參數傳的是 `rag_config`（config **名稱**，例如 `"test_nculab"`），但實際的 `site_id` 是 config 內部欄位（例如 `"nculab"`），兩者不同——這是驗證邏輯一直在檢查錯誤目錄的既有 bug，跟這次路徑拆分無關，但因為正好改到同一段程式碼，順手一併修正為傳 `site_label`。

### 驗證方式

1. 單元測試：`test_publish_crawl_results` 改為斷言 `data/raw_webpages/{site_id}/` 底下的結果。
2. 完整非 slow 套件、`uv run pyright`。
3. 實際跑一次 `uv run python src/main.py --run.config-name test`，比對：
   - `data/raw_webpages/nculab/results.json` 每頁只有 `fit_markdown`（無 `enhanced_markdown`）。
   - `data/webpages/nculab/results.json` 每頁同時有 `fit_markdown` 與 `enhanced_markdown`。
   - 兩邊 `results/*.md` 內容分別對應各自 `results.json` 裡的 `fit_markdown`／`enhanced_markdown` 欄位。
   - `runs/` 無新增。
