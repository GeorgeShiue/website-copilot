# Development Log

> 對應規劃文件：[plan.md](./plan.md)

---

## 起點：確認問題是否存在

動手前先逐一查證 plan.md 列出的 4 個耦合點：

- **Server 會建庫**：追蹤 `RAGRegistry.get()` → `RAGBuilder.build_to_retriever(force_rebuild=False)` → `build_to_vector_store()` → `_should_rebuild()`，確認 `milvus.db` 不存在時會走 clean → nodes → vector store → index 的完整建置路徑。
- **站點判斷依據**：`_site_exists()`／`list_sites()` 確實掃描 `data/webpages/`，而非向量庫。
- **原地重建**：`create_rag()` 只在 `run_manager` 非 None 時覆寫 `config.milvus_uri`；`main.py` 以 `save=False` 呼叫，`run_manager` 為 None，因此直接在 `rag_config.py::_default_milvus_uri()` 的 `data/rag/{site}/milvus.db` 上 `force_rebuild`。另確認 `milvus.db` 實際上是資料夾（Milvus Lite），`publish_vector_store` 走 `rmtree` + `copytree` 分支。
- **import 綁定**：`workflow.py` 頂層同時 import `WebsiteCrawler`、`WebpageImageSummarizer`、`uvicorn`、`create_agent`、`ChatApp`。

實作順序依建議調整為：步驟 3 → 1 → 4 → 2（先處理語意邊界，再處理結構整理）。

---

## 步驟 3：Server 唯讀

- `RAGBuilder.load_to_retriever()` 疊在 `build_to_retriever(force_rebuild=False)` 之上，只多一道存在性檢查，不另寫一套載入邏輯。
- `list_sites()` 改掃描 `data/rag/`，並以 `_site_exists()`（檢查 `milvus.db`）過濾，所以空的 `data/rag/{site}/` 資料夾不會被列出。
- `test_rag_tools.py` 的 `_make_registry` helper 改為建立 `data/rag/{site}/milvus.db`；cache miss 斷言由 `build_to_retriever` 改為 `load_to_retriever`；新增 `TestLoadToRetriever`（2 個）與「只有 webpages 或空 rag 資料夾不列出」測試。

**驗證**：從 repo 根目錄執行 `RAGRegistry().list_sites()`，現有 `data/` 回傳 `['claudecode', 'ncucsie', 'nculab']`，與原本一致（三個站點都已 publish 向量庫）。注意 `base_folder="data"` 是相對路徑，從 `src/` 執行會得到 `[]`。

---

## 步驟 1：入口拆分

- `git mv src/main.py src/prepare.py`，保留 git 歷史。
- `ServerCLI` 從 `cli.py` 整個移除（而非保留成轉發），原本只為了跳過 `ServerCLI` 而存在的 `isinstance` 判斷一併刪除。
- `serve.py` 沿用既有 `ServerRunConfig`，不新增 config 類別。

---

## 步驟 4：向量庫原子替換

### 規則修正

原規劃在 `save=False` 時一律把向量庫建到 `data/rag/{site}/.staging/`。使用者指出 `run_rag_build` 在 `save=False` 時就不該保存結果，`save` 與 `publish` 皆為 False 時不應留下任何檔案。因此改為：`publish=True` 才用 `data/` 底下的 staging（為了同檔案系統 rename），`publish=False` 改用系統暫存資料夾，結束即刪（等同只驗證建庫流程能跑通）。

### 實作重點

- **建庫位置在 `run_rag_build` 決定**：`run_manager is None`（`save=False`）時先設定 `config.milvus_uri` 再呼叫 `create_rag`；`save=True` 時沿用 `create_rag` 依 `run_manager` 決定 `runs/` 路徑的既有邏輯，`create_rag` 本身不改。
- **`DataManager.create_vector_store_staging()`**：以 `tempfile.mkdtemp(prefix=".staging-", dir=data/rag/{site})` 建立。
- **`publish_vector_store(move=...)`**：
  - 先清掉前次中斷殘留的 `.tmp`／`.old`。
  - `move=True`（來源為 staging）用 `shutil.move`（同檔案系統等同 rename）；`move=False`（來源為 `runs/`）用 `copytree`／`copy2`，保留來源。
  - 替換中途失敗時，若舊版已移成 `.old` 而正式路徑不存在，就把 `.old` 改回原名再 re-raise——這是規劃時沒寫到、實作時補上的回復邏輯。
- **`module_config.toml` 的 `milvus_uri`**：發布到 `data/rag/{site}/` 的 `module_config.toml` 會序列化 `milvus_uri`（現有檔案可見 `milvus_uri = "data/rag/nculab/milvus.db"`）。若不處理，會記錄 staging 或 `runs/` 路徑，因此 publish 向量庫後把 `config.milvus_uri` 改為正式路徑再寫 metadata。`runs/` 的 `module_config.toml` 在此之前寫出，仍記錄 `runs/` 路徑。

### 測試

`test_run_rag_build_publish.py` 改寫：fake `create_rag` 依 `config.milvus_uri`／`run_manager` 實際寫出假向量庫，並以 `monkeypatch` 把 `tempfile.tempdir` 導向 `tmp_path`，才能驗證系統暫存資料夾有被清掉。共 8 個測試：

- 四種 `save`／`publish` 組合的檔案殘留（含發布的 `milvus_uri` 為正式路徑）。
- 替換已存在的舊向量庫。
- 建庫失敗：舊庫保留、staging 清除。
- 替換中途失敗（patch `os.replace` 在 `.tmp` → `milvus.db` 時拋錯）：舊庫還原、不留 `.tmp`／`.old`。
- 沒有產出向量庫時仍 publish metadata。

### 順帶修正

`scripts/multi_site.py` 呼叫 `run_rag_build(force_rebuild=True, ...)`，但 `run_rag_build` 早已移除該參數（見 [2026_0923-rag_build_pipeline](../2026_0923-rag_build_pipeline/dev.md)），它會被當成 config override 丟掉。一併移除，並刪除已不適用的 self-copy 註解。

---

## 步驟 2：workflow 拆分

- 以腳本依函式行號切出三個模組，各自只保留需要的 import，再 `git rm` 原 `workflow.py`（呼叫端在同一次變更內全數更新，不保留 re-export）。ruff 通過即代表各模組沒有遺漏或多餘的 import。
- `cli.py` 各分支內才 import 對應模組。
- 測試 patch 路徑：`test_run_agent.py` → `serve_workflow`，`test_run_rag_build_publish.py` → `prepare_workflow`。

**踩到的問題**：用 `sed 's/app\.workflow\.workflow/.../'` 批次替換時，同時把 `app.workflow.workflow_helper` 改成了 `serve_workflow_helper`／`prepare_workflow_helper`，造成 17 個測試失敗（`module 'app.workflow' has no attribute 'serve_workflow_helper'`）。已修正；之後批次替換模組路徑時應加上字尾邊界。

### import 隔離驗證

在獨立 process 中 import 後檢查 `sys.modules`：

| 入口 | 檢查項目 | 結果 |
|---|---|---|
| `import serve` | `crawl4ai`、`playwright`、`app.engines.website_crawler`、`app.engines.webpage_image_summarizer` | 皆未載入 |
| `import prepare` | `uvicorn`、`app.agent.agent`、`app.server.app`、`langgraph` | 皆未載入 |

`import prepare` 會載入 `fastapi`，以 `python -X importtime` 追查是 `litellm.integrations` 內部經由 `starlette` 引入，屬第三方依賴，不是本專案的 server。

---

## 文件與註解同步

- **README**：新增兩階段對照表與 `prepare.py`／`serve.py` 用法、目錄樹（三個 workflow 模組）、建庫位置規則表；移除不存在的 `--run.save-vector-store-to-runs` 說明。
- **docs/code/runs/**（`workflow.md`、`cli.md`、`config.md`）：入口、模組拆分、`run_rag_build` 建庫規則與原子替換流程；原本就已過時的 `save_vector_store_to_runs` 描述一併改正。
- **docs/code/phase1、phase2_3_mvp、docs/project.md**：`RAGRegistry` 改為「lazy 載入、唯讀」，`registry.get()` 流程改為 `load_to_retriever()`；`data_retrieve.md` 的 `RAGBuilder` 方法樹仍是更早的 `build_reusable()`，一併更新為現行的 `build_to_*`／`load_to_retriever()`；歷史進度清單保留原文，只加註目前的做法。
- **程式碼註解**：`workflow_helper.py`、`rag_registry.py`、`site_discovery.py` 的 docstring；`rag_factory.py` 與 `log_helper.py` 中的 "main workflow"／已不存在的 `log_run_summary` 參照。
- **docs/work/todo.md**：勾選「伺服器啟動獨立於 main workflow 之外」並列出子項；新增兩個後續待辦。

---

## 驗證結果

- `ruff check`、`ruff format --check`：通過。
- `pyright`：4 個錯誤，皆在 `test_webpage_markdown_cleaner.py`（本次未修改，原本就存在）。
- `pytest src/test/dev -m "not slow"`：203 passed、1 failed。失敗的 `test_webpage_markdown_cleaner.py::test_save_generated_exclude_words` 以 `git stash` 確認在修改前就已失敗。
- `pytest --collect-only`：210 個測試可正常收集（含 `test_main.py`、`test_module.py` 的新 import）。
- **未執行**：標記為 `slow` 的端對端測試（真實爬蟲／LLM／建庫），以及實際啟動 server 或完整跑一次 prepare。

---

## Final Summary

### 變更檔案總表

| 檔案 | 變更內容 |
|------|---------|
| `src/main.py` → `src/prepare.py` | 改名；`PrepareCLI`／`PrepareRunConfig`；移除註解掉的 server 程式碼 |
| `src/serve.py` | 新增，serve 階段入口 |
| `src/cli.py` | 移除 `ServerCLI`；各分支內 lazy import 對應 workflow 模組 |
| `src/app/workflow/workflow.py` | 刪除，拆分為下列三個模組 |
| `src/app/workflow/prepare_workflow.py` | 新增；`run_rag_build` 依 `save`／`publish` 決定建庫位置並清理暫存 |
| `src/app/workflow/serve_workflow.py` | 新增；Agent 與 server 相關 workflow |
| `src/app/workflow/eval_workflow.py` | 新增；`run_rag_query` |
| `src/app/workflow/data_manager.py` | 新增 `create_vector_store_staging()`；`publish_vector_store()` 改為原子替換並支援 `move` |
| `src/app/engines/rag/rag_factory.py` | 新增 `RAGBuilder.load_to_retriever()` |
| `src/app/tools/rag_registry.py` | `get()` 改為唯讀載入；`list_sites()`／`_site_exists()` 改以向量庫判斷 |
| `src/app/configs/workflow_config.py` | `MainRunConfig` → `PrepareRunConfig` |
| `src/utils/log_helper.py` | `log_main_workflow_run_summary` → `log_prepare_workflow_run_summary` |
| `src/exp.py`、`scripts/multi_site.py`、`src/test/test_main.py`、`src/test/test_module.py` | import 更新；`multi_site.py` 移除無效的 `force_rebuild` |
| `src/test/dev/test_rag_tools.py` | registry 唯讀與 `load_to_retriever` 測試 |
| `src/test/dev/test_run_rag_build_publish.py` | 改寫為建庫位置／原子替換的 8 個測試 |
| `src/test/dev/test_run_agent.py`、`test_log_helper.py` | patch 路徑與函式名更新 |

### 行為改變

- 啟動 server 不再自動補建向量庫；`data/rag/{site}/milvus.db` 不存在的站點不可用，需先執行 `prepare.py`。
- `cli.py server-cli` 已移除，改用 `serve.py`。
- `run_rag_build(save=False, publish=False)` 不再改寫 `data/`。

### 後續待辦

- prepare 重新 publish 後，已在執行的 server 仍使用舊向量庫（Linux 上已開啟的檔案不受 rename 影響），需重啟才會載入新版；可考慮以 manifest mtime 讓 registry 自動 evict。
- `run_rag_query --run.force-rebuild` 仍於 `data/rag/` 原地重建（評估工具，本次未改）。
- `test_main.py` 拆分為 prepare／serve 兩個測試（todo.md「更新 test_main.py 測試流程」）。
- 選配：`data/rag/{site}/manifest.json`。
