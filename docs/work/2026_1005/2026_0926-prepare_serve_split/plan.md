# Prepare／Serve 兩階段拆分計畫

## Context

從 `docs/work/todo.md`「伺服器啟動獨立於 main workflow 之外」項目出發，目標是把系統拆成兩個獨立執行的階段：

| 階段 | 入口 | 職責 |
|---|---|---|
| Prepare | `src/prepare.py` | 網站爬蟲 → 圖片摘要 → RAG 建置，結果 publish 到 `data/` |
| Serve | `src/serve.py` | 啟動 Chat Server，只讀取 `data/` 已 publish 的向量庫 |

兩階段唯一的介面是 `data/` 目錄。實際執行過程、決策修正與驗證結果記錄於 [dev.md](./dev.md)。

---

## 現況分析

開始時的狀態：

- `src/main.py` 只跑 prepare 三階段，server 啟動程式碼已被註解掉。
- Server 只能從 `src/cli.py server-cli` 啟動，跟開發用子指令混在一起。
- 兩階段已經以 `data/webpages/{site}`、`data/rag/{site}/milvus.db` 交接，方向正確。

**「執行」上已經分開，但「階段邊界」沒有劃清楚**，有 4 個耦合點：

1. **Server 可能在執行期偷做 prepare 的工作**：`RAGRegistry.get()` 呼叫 `build_to_retriever(force_rebuild=False)`，`_should_rebuild()` 在 `milvus.db` 不存在時會直接重建，等於在第一個 request 裡跑 BGE-M3 embedding。
2. **Server 用 prepare 的中間產物判斷站點是否可用**：`_site_exists()`／`list_sites()` 掃描 `data/webpages/`，summarizer 跑完但 RAG 還沒建好的站點也會被列為可用。
3. **Prepare 直接覆寫 server 正在讀的向量庫**：`main.py` 使用 `save=False`，`create_rag` 直接在 `data/rag/{site}/milvus.db` 上 `force_rebuild`；即使走 `save=True`，`publish_vector_store` 也是先 `rmtree` 再 `copytree`，替換過程不是原子的。
4. **兩個階段的 import 綁在一起**：`workflow.py` 在最上層同時 import crawl4ai／Playwright、VLM、uvicorn、agent，server 部署也得裝整套爬蟲依賴。

---

## 步驟 1：入口檔拆分

### 設計

- `src/main.py` 改名為 `src/prepare.py`；`MainCLI`／`MainRunConfig` → `PrepareCLI`／`PrepareRunConfig`；log 標題改為 "Prepare Pipeline"；`log_main_workflow_run_summary` → `log_prepare_workflow_run_summary`；刪除被註解掉的 server 程式碼。
- 新增 `src/serve.py`：搬移 `cli.py` 的 server 分支，吃 `ServeRunConfig`，處理 `KeyboardInterrupt` 並記錄 "Server Stopped"。
- `cli.py` 移除 `ServerCLI`，讓 server 只有一個入口。

### 驗證方式

- 兩個入口與 `cli.py` 的 `--help` 可正常執行；ruff／pyright 通過。

---

## 步驟 2：workflow 模組依階段拆分

### 設計

| 檔案 | 內容 | 使用者 |
|---|---|---|
| `prepare_workflow.py` | `run_website_crawler`、`run_webpage_image_summarizer`、`run_rag_build` | `prepare.py`、`cli.py`、`scripts/multi_site.py` |
| `serve_workflow.py` | `run_app`、`run_agent_build`、`run_agent_query` | `serve.py`、`cli.py` |
| `eval_workflow.py` | `run_rag_query`（查詢評估，兩個階段都不屬於） | `cli.py`、`exp.py` |

- `cli.py` 改在各分支內才 import 對應模組。
- 所有呼叫端與測試的 `patch("app.workflow.workflow.xxx")` 路徑同步更新。

### 驗證方式

- 在獨立 process 中 `import serve` 後檢查 `sys.modules`，確認沒有 `crawl4ai`／`playwright`；反向確認 `import prepare` 不載入 agent／server。

---

## 步驟 3：Server 唯讀

### 設計

- `RAGBuilder` 新增 `load_to_retriever(rag)`：`milvus_uri` 不存在時拋 `FileNotFoundError`，存在時才以 `force_rebuild=False` 載入。
- `RAGRegistry.get()` 改呼叫 `load_to_retriever()`。
- `_site_exists()`／`list_sites()` 改以 `data/rag/{site}/milvus.db` 是否存在判斷，讓「站點可查詢」等同於「prepare 已成功 publish」。

### 驗證方式

- 單元測試：向量庫不存在時拋錯且不觸發建置；只有 webpages 或空 rag 資料夾的站點不列出。

---

## 步驟 4：向量庫原子替換

### 規則（使用者修正後）

`run_rag_build` 在 `save=False` 時不在 `runs/` 留下任何東西；`save` 和 `publish` 都是 `False` 時，執行完不留下任何檔案。原實作違反此規則：`save=False` 時 `create_rag` 退回 config 預設的 `data/rag/{site}/milvus.db` 原地重建，即使 `publish=False` 也會改寫 `data/`。

### 設計

建庫位置改由 `save`／`publish` 決定：

| save | publish | 建庫位置 | 結束後留下的檔案 |
|---|---|---|---|
| True | True | `runs/.../results/milvus.db` | runs/ 保留一份；另外複製到 data/ 再替換 |
| True | False | `runs/.../results/milvus.db` | 只有 runs/ |
| False | True | `data/rag/{site}/.staging-*/milvus.db` | 改名移到正式位置，staging 刪除；只有 data/ |
| False | False | 系統暫存資料夾 | 無（結束時刪除） |

- `publish_vector_store` 改為「先放 `milvus.db.tmp`，舊版改名 `.old`，新版改名 `milvus.db`，再刪 `.old`」；來源是 staging 時直接 rename（同檔案系統），來源是 `runs/` 時複製。
- 暫存資料夾以 `try/finally` 保證刪除；建庫失敗時舊向量庫不受影響。
- 選配（未實作）：替換完成後寫 `data/rag/{site}/manifest.json`，供 registry 判斷可用性與 `/api/health` 回報版本。

### 驗證方式

- 以 `tmp_path` 當工作目錄並 mock 建庫，測四種組合的檔案殘留、替換既有向量庫、建庫失敗與替換中途失敗的回復。
