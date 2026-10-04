# 專案結構重構：實作規劃

## Context

對應 [todo.md](../../todo.md)「技術債 → 專案結構重構」。從 prepare／serve 兩階段拆分開始，依序經過 src layout 重組與四輪調整，最後重整測試，合併於此，實作紀錄見 [dev.md](./dev.md)。

| 階段 | 日期 | 主題 | 狀態 |
|---|---|---|---|
| 0 | 09-26 | Prepare／Serve 兩階段拆分 | ✅ |
| 1 | 09-26 | 改為標準 src layout，依管線階段分模組（Phase A–E） | ✅ |
| 2 | 09-27 | serve 生命週期收斂與開發工具整理 | ✅ |
| 3 | 09-28／29 | agent build 與 server build 分離、統一 agent 建構 | ✅ |
| 4 | 09-29 | 刪除多餘檔案與 ImageSummarizer 更名 | ✅ |
| 5 | 09-29 | 測試新專案結構 | ✅ |

---

## 0. Prepare／Serve 兩階段拆分

目標：把系統拆成兩個獨立執行的階段，唯一介面是 `data/`。

| 階段 | 入口 | 職責 |
|---|---|---|
| Prepare | `src/prepare.py` | 網站爬蟲 → 圖片摘要 → RAG 建置，結果 publish 到 `data/` |
| Serve | `src/serve.py` | 啟動 Chat Server，只讀取 `data/` 已 publish 的向量庫 |

「執行」上已分開，但「階段邊界」有 4 個耦合點：

1. **Server 可能在執行期偷做 prepare 的工作**：`RAGRegistry.get()` 在 `milvus.db` 不存在時會直接重建，等於在第一個 request 跑 BGE-M3 embedding。
2. **Server 用 prepare 的中間產物判斷站點是否可用**：`list_sites()` 掃描 `data/webpages/`，RAG 還沒建好的站點也會被列出。
3. **Prepare 直接覆寫 server 正在讀的向量庫**：`save=False` 時原地 `force_rebuild`；即使 `save=True`，`publish_vector_store` 也是先 `rmtree` 再 `copytree`，不是原子的。
4. **兩個階段的 import 綁在一起**：`workflow.py` 頂層同時 import crawl4ai／Playwright、VLM、uvicorn、agent。

實作順序：步驟 3 → 1 → 4 → 2（先處理語意邊界，再處理結構整理）。

| 步驟 | 設計 |
|---|---|
| 1. 入口拆分 | `main.py` 改名 `prepare.py`（`PrepareCLI`／`PrepareRunConfig`）並刪除註解掉的 server 程式碼；新增 `serve.py`，搬移 `cli.py` 的 server 分支；`cli.py` 移除 `ServerCLI`，server 只有一個入口 |
| 2. workflow 拆分 | `prepare_workflow.py`（crawler、summarizer、`run_rag_build`）、`serve_workflow.py`（`run_app`、`run_agent_build`、`run_agent_query`）、`eval_workflow.py`（`run_rag_query`）；`cli.py` 在各分支內才 import。驗證：獨立 process 中 `import serve` 不載入 crawl4ai／playwright，`import prepare` 不載入 agent／server |
| 3. Server 唯讀 | `RAGBuilder.load_to_retriever()`：`milvus_uri` 不存在時拋 `FileNotFoundError`；`RAGRegistry.get()` 改呼叫它；`_site_exists()`／`list_sites()` 改以 `data/rag/{site}/milvus.db` 是否存在判斷 |
| 4. 向量庫原子替換 | 規則（使用者修正後）：`save=False` 不在 `runs/` 留下任何東西，`save` 與 `publish` 皆 `False` 時不留下任何檔案。建庫位置由 `save`／`publish` 決定（見下表）；`publish_vector_store` 改為 `.tmp` → 舊版改名 `.old` → 新版改名 → 刪 `.old`；暫存以 `try/finally` 保證清除，建庫失敗時舊庫不受影響。選配 `manifest.json` 未實作 |

| save | publish | 建庫位置 | 結束後留下 |
|---|---|---|---|
| True | True | `runs/.../results/milvus.db` | runs/ 一份；複製到 data/ 並替換 |
| True | False | `runs/.../results/milvus.db` | 只有 runs/ |
| False | True | `data/rag/{site}/.staging-*/milvus.db` | rename 到正式位置，只有 data/ |
| False | False | 系統暫存資料夾 | 無 |

---

## 1. 標準 src layout（plan 1）

### 背景與決策

原本 `src/` 下有兩個頂層套件 `app`、`utils`，入口檔散落在根目錄，要靠 `pythonpath = ["src"]` 才能 import；模組依技術角色命名，造成 `rag_factory.py` 同時負責建庫與 serve 載入、RAG 反向依賴 `workflow/`、storage 依賴 cleaner 型別、兩份 `widget.js` 分岔。

**除一項刻意變更外，執行行為不變**（config 路徑、`data/`、`runs/` 不動）；刻意變更是 serve 不再需要 `data/webpages/`。

- 套件改名 `src/website_copilot/`，一輪完成全部模組重組。
- `ingestion/` 下分 `crawling/`、`augmentation/`、`indexing/`；凡建置或載入 index 的程式碼放 `indexing/`；`retrieval/factory.py` 提供 `build_rag`（建置）與 `load_rag`（serve 載入）。
- RAG 容器改為**回傳式建構**，builder 回傳物件，不再從外部寫入欄位。
- `workflow/` 改名 `pipelines/`，server 啟動移到 `server/`；`DataManager`／`RunManager`／run context 移到 `storage/`；跨層共用型別放 `schemas.py`。
- 單一 CLI `website-copilot`（`cli/` 子套件、tyro 子命令），`scripts/` 只放一次性腳本。
- `data/` 維持在版控；`widget.js` 以 `server/static/` 為唯一來源，用 sync 腳本同步並由 CI 比對。
- 刪除 `dev/legacy`、`dev/crawl4ai`、`dev/llama_index`；`dev/marp` 只保留 `2026_0518_marp_v3.md`，改名為 `docs/progress_report/2026_0518/2026_0518_marp.md`。
- 測試分 `tests/unit`、`tests/integration`；新增 `.env.example`。
- 每個 phase 一個 commit，完成並通過檢查後先暫停回報，使用者確認才進下一個 phase。

### 目標結構

```text
src/website_copilot/
├── schemas.py        # 跨層共用型別（GenerationResult）
├── cli/              # prepare / serve / run / exp 子命令（只解析參數）
├── config/           # ← app/configs；workflow_config → pipeline_config
├── ingestion/
│   ├── crawling/     # website_crawler、markdown_cleaner、html_date_extractor
│   ├── augmentation/ # image_summarizer
│   └── indexing/     # source、transforms、node_pipeline、vector_store、index
├── retrieval/        # rag、factory、evaluation、registry、llama_index_helpers
├── agent/            # agent、langchain_helper、tools/
├── storage/          # data_manager、run_manager、run_persistence、run_context
├── server/           # app、static/
├── pipelines/        # prepare、agent、exp
└── utils/            # log_helper、config_helper
tests/{unit,integration}
```

**依賴方向**：`cli` → `pipelines`／`server` → `agent` → `retrieval` → `indexing` → `augmentation` → `crawling` → `storage` → `config`／`utils`／`schemas`。`storage` 不依賴任何 `ingestion`；`indexing` 不 import `retrieval`（回傳式建構）；`__init__.py` 只做輕量重新匯出，避免 serve 間接載入 crawl4ai／playwright。

### 執行步驟

原則：**搬移與邏輯變更絕不放在同一個 commit**。Phase B 只做搬移（`git show -M --stat` 應顯示高相似度 rename），邏輯變更集中在 C、D。大量 import 替換以腳本完成，並把指令寫進 commit message，方便重做。

- **Phase A 安全網**：記錄 `pytest` 通過數與 `pyright` 錯誤數作為基線；新增 import 冒煙測試；新增 serve 載入的特性測試（鎖定 `RAGRegistry.get()` 走載入路徑、向量庫不存在時的錯誤訊息），此測試在 C3 才改寫。
- **Phase B 純搬移**：B1 測試搬家；B2 套件改名 `app`＋`utils` → `website_copilot`；B3 抽出 `schemas.py`；B4 `workflow/` 拆成 `storage/`＋`pipelines/`、`configs` → `config`；B5 `engines/` 拆成 `ingestion/{crawling,augmentation}`；B6 RAG 與 tools 整檔搬移（indexing 暫時仍 import retrieval，C3 消除）。結束時做里程碑檢查。
- **Phase C RAG 重構**：C1 抽出 helper 模組（簽名不變）；C2 拆 `RAGBuilder`（仍 mutate 模式）為 `IndexBuilder` 與 retrieval 端 `RAGBuilder`，`create_rag` 改名 `build_rag`；C3 回傳式建構（`IndexHandle`、`RAG(index_handle, retriever, query_engine)`、`load_rag(config)`）並移除 `webpages` 依賴，這是唯一的行為變更。
- **Phase D 入口**：D1 邏輯下移到 `pipelines`／`server`，舊入口暫留為薄包裝；D2 新增 `cli/` 與 `[project.scripts] website-copilot`，`pipelines/eval.py` 改名 `exp.py`，`run` 子命令改為複製 run config 後再拆出 `save`／`publish`（修正舊 `src/cli.py` 直接 pop 物件屬性的問題），刪除舊入口與 `pythonpath`。完整 `prepare` 會 publish 覆寫版控中的 `data/`，需使用者同意才執行。
- **Phase E 雜項**：E1 widget 同步；E2 清理 `dev/` 並移除 ruff／pyright 對 `dev/**` 的排除；E3 `.env.example` 與開發指令；E4 README 與 `docs/code/**` 的舊路徑、舊指令全數改新。

---

## 2. serve 生命週期收斂與開發工具整理（plan 2）

起點：使用者先調整 pipelines 分組（`server/bootstrap.py` → `pipelines/serve.py`，`run_app` → `run_server_build`、`serve_forever` → `serve`；刪除 `pipelines/agent.py`，`run_agent_build` 併入 serve、`run_agent_query` 併入 exp；刪除 `scripts/multi_site.py`）。

**刻意的行為變更只有兩項**：server 的 run 目錄多寫 `module_config.toml`（plan 3 撤銷）；`run_server_build()` 只回傳 `ChatServer`。

五點與決策：

| 點 | 決策（未採用的選項） |
|---|---|
| 1. server 建置 agent 改呼叫 `run_agent_build()` | 新增可選 `run_manager` 共用呼叫端 context（不採：各自獨立 context、抽 `_build_agent()`）；回傳未關閉的 `Agent` 由呼叫端 `close()`，只改 server |
| 2. `ChatServer` 退出自動清理 `ChatApp` | 只回傳 `ChatServer`，`ChatApp` 經 `server.chat_app` 取得；覆寫 `serve()` 以 `try/finally` 關閉 |
| 3. 捨棄 Makefile，改 `scripts/` | 一個指令一支 bash（不採：單一分派腳本、Python 腳本）；`check`、`format`、`sync-widget` 做腳本，`install`、`serve` 在 README 寫 `uv` 指令。使用者追加：`check.sh` 拆成 `lint.sh`、`test.sh`、`check-widget.sh`；`format.sh` 併入 `lint.sh --fix`，預設只檢查。清理 runs 腳本：只刪名稱符合 `YYYYMMDD_HHMMSS` 且日期早於今天的資料夾 |
| 4. 統一 `GEMINI_API_KEY` | 三個 Gemini 變數合併為一個；`create_llm()` 失去作用的 `usage` 參數一併移除 |
| 5. `pyproject.toml` | 依賴只移除沒用到的（結果：無可移除）；ruff `exclude` 改 `extend-exclude`；規則組維持預設。使用者追加：prek 的 ruff 改 local hook（版本由 uv.lock 決定），CI 改用 `scripts/lint.sh`、`scripts/check-widget.sh` |

---

## 3. agent build 與 server build 分離（plan 3）

留下的問題：`run_server_build()` 同時建構 agent 與 server；`run_agent_build()` 為共用 context 多了參數與分支；`run_agent_query()` 自行載入 config 並建 agent，與 `run_agent_build()` 重複，且例外路徑關閉兩次；`AgentConfig` 被讀兩次；`check.sh` 因基線錯誤從 plan 1 起就不會通過。

目標：`run_agent_build()` 脫離 `run_server_build()`、改由 `serve()` 呼叫，兩個 build 各自持有 `RunManager`；所有 agent 建構都經過 `run_agent_build()`、`AgentConfig` 只讀一次；`check.sh` 全部通過。

| 問題 | 決策（未採用的選項） |
|---|---|
| 兩個 build 各建 `RunManager`，產生兩個時間戳目錄 | 暫時接受（不採：讓 `RunManager` 可傳入 timestamp） |
| server 的 run module 名稱 | 改為 `server` |
| server 目錄是否保留 `module_config.toml` | 不保留，agent 設定只寫在 `agent_build/` |
| `run_server_build()` 取得 agent | 注入：接收 `agent`，`config_name` 由 `agent.config.config_name` 取得 |
| `run_server_build()` 失敗時誰關閉 agent | 建立者（`serve()`）關閉；成功回傳後所有權轉交 `ChatServer` |
| `run agent` 的 run 目錄 | 比照 server：`agent_build/` 放 `module_config.toml`，`agent/` 放對話結果與 `run_config.toml` |
| `create_agent()` 簽名 | 直接替換為 `create_agent(config: AgentConfig)` |
| 檢查基線修正方向 | 只改測試，程式行為不變 |

**Part A（serve 拆分）**：`run_agent_build()` 移除 `run_manager` 與 `nullcontext()` 分支；`run_server_build(agent, ...)`；`serve()` 串接兩個 build。**Part B（統一 agent 建構）**：B1 修正檢查基線（測試補 `hits`、加 `assert result is not None`）；B2 `create_agent(config)`；B3 `run_agent_query()` 改用 `run_agent_build()`，關閉只做一次。

**行為變更**：

1. `serve` 一次啟動產生兩個 run 目錄：`agent_build/<config>/` 與 `server/<config>/`，時間戳可能不同。
2. server 的 run 目錄由 `agent/` 改為 `server/`，不再寫 `module_config.toml`。
3. **對話歷史跨 run 查找範圍改變**：`find_thread_history_path` 以 module 搜尋，server 改用 `server` 後不再讀到舊的 `runs/*/agent/` 歷史；`run_agent_query()` 仍用 `agent`。
4. `run agent` 同樣產生兩個 run 目錄。
5. `run_server_build()` 第一個參數改為 `agent` 且失敗時不關閉；`create_agent()` 改簽名。

---

## 4. 刪除多餘檔案與 ImageSummarizer 更名（plan 4）

盤點方式：`vulture` 與 `ruff --select F401,F841,F811` 找未使用定義，`grep` 確認引用；`git ls-files` 逐目錄檢查檔案。逐項審核後的決策：

- **刪除**：`DEFAULT_INIT_CONFIG_FOLDER_PATH`、兩個 `override_init_config()`、`configs/rag/milvus.toml`（與 `default.toml` 相同）、`tests/unit/_helpers.py`、`2026_0629_outline.md`（已被 v2 取代）、`.aiexclude`、`docs/exp/records/`（3.1M）；docstring 中的 `chats/`；測試中未使用的參數。
- **保留**：`KEEP_TITLE_CONTENT_THRESHOLD`（嘗試過的數值紀錄）、`data/` 中的舊 `run_config.toml`／`LOCK`／`manifest.json.prev`、`ci-test.yml`、`configs/*/test_{site}.toml`、marp pdf、`.mmd` 產生的圖、winnow 兩套計畫、`data/*/*/terminal.log`。
- **未追蹤目錄**（根目錄 `__pycache__/`、`chats/`、`.claude/`、`runs/20260928_135728`）：刪除後無法還原，由使用者手動執行。
- **確認不是多餘（掃描誤報）**：`retrieval/evaluation.py`、`transforms.py` 的 `aextract`／`class_name`、FastAPI 路由、autouse fixture、`extension/widget.js`。

**更名**：`WebpageImageSummarizer*` → `ImageSummarizer*`，`run_webpage_image_summarizer()` → `run_image_summarizer()`，設定檔與 `configs/` 資料夾、runs 模組資料夾、實驗名稱同步；CLI 子命令原本就是 `image-summarizer`。`docs/work/`、`docs/progress_report/` 為歷史紀錄，保留舊名。

---

## 5. 測試新專案結構

規劃在對話中與使用者逐項確認，沒有另外寫計畫，決策如下：

| 項目 | 決定 |
|---|---|
| integration 測試分工 | `test_module.py`：每個 run function 一個測試；`test_pipeline.py`（原 `test_main.py`）：`test_prepare`、`test_serve` |
| `test_server` | 移到 `test_pipeline.py`，改名 `test_serve` |
| 標記 | `slow` 改為 `cost`，只標會呼叫 LLM／VLM／embedding API 的測試，逐個加標記 |
| `scripts/test.sh` | 只跑 `tests/unit`，不再用 `-m` 過濾 |
| CI | 維持只跑 integration，路徑改為整個 `tests/integration`（含 `cost`，每次執行會產生 API 費用） |
| integration 斷言 | 暫不加，只驗證不拋例外 |
| unit 測試範圍 | 只保留核心、易出錯程式的測試，其餘刪除（需要時從 `0c3dbda` 取回） |
| `test_prepare` 不寫 `data/` | `run_prepare(config_name, publish=True)` 加 `publish` 參數，測試傳 `False`，此時三階段皆 `save=True, publish=False`，rag build 另傳 `webpages_data_use_latest_results=True` |

unit 測試依 `pipelines/` 重新分檔（`test_pipeline_prepare|serve|exp.py`、`test_run_manager.py`、`test_data_manager.py`），並依「出錯後果」與「出錯機率」分 S／A／B／C 四級，刪除 B、C 級。

**`webpages_data_use_latest_results` 回歸修正**：此參數原本讀 `runs/` 最新的 image summarizer 結果，拆出 DataManager 後被改成 `data/webpages/<site>`（等於預設值），參數實際沒有作用。修正為以 `load_latest_run_path(runs, "image_summarizer", site_id=...)` 取得路徑，`load_latest_run_path` 新增 `site_id` 參數以避免讀到其他 site 的 run，`build_rag` 移除不再使用的 `data_manager` 參數。

---

## 驗證

**每步檢查**（每個 phase／點／步驟完成後執行，commit 前必須通過；`scripts/check.sh` 可用後以它執行）：

1. `uv run ruff check . && uv run ruff format --check .`
2. `uv run pyright`：錯誤數不得高於基線（基線 4 errors 於 plan 3 B1 修正為 0）。
3. 單元測試通過數不少於基線，包含 import 冒煙測試。
4. 重構 Phase C3 之後：`import website_copilot.retrieval.registry` 不應載入 `crawl4ai` 或 `ingestion.crawling`。

**里程碑檢查**（Phase B6、C3、D2 結束時）：

- serve 端到端：啟動 serve 並讀取既有 `data/rag/*`，呼叫 `/api/chat` 取得 SSE，`/static/demo.html` 正常。
- prepare：以 test config 的 `run rag-build` 跑小規模建庫，確認 `runs/` 與 publish 行為不變（需要 API key）。

**個別驗證**：

- plan 2 第 2 點：以真實 `ChatServer` 搭配假 `ChatApp` 送 SIGINT，確認 `ChatApp` 被關閉；第 3 點：各腳本單獨執行，`clean-runs.sh` 只在假目錄實際刪除；第 5 點：`ruff check --show-settings`、`prek validate-config`。
- plan 3：實際執行 `serve` 與 `run agent`，確認 `agent_build/`、`server/`、`agent/` 目錄內容符合預期。

**完成後**：`grep` 確認舊路徑、舊名稱（`from app.`、`pipelines.agent`、`server.bootstrap`、`serve_forever`、`make `、舊 Gemini 變數名、`webpage_image_summarizer` 等）在 `src`、`tests`、`.github`、README、`docs/code` 中無殘留；`docs/work/` 的歷程紀錄不改。可選：`uv run pytest tests/integration`（真實爬蟲與付費 API，需使用者同意）。
