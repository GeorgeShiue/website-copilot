# CLI

## 一、主要檔案與角色

- `website-copilot`：單一 CLI 指令（`pyproject.toml` 的 `[project.scripts]` → `website_copilot.cli:main`；也可用 `python -m website_copilot.cli`）。
- `src/website_copilot/cli/__init__.py`：`main()` 以 `tyro` 解析子命令 `prepare | serve | run | exp` 並 dispatch 到對應子命令模組。各子命令模組只在頂層 import 參數 dataclass，執行邏輯在 `main()` 內延遲 import，避免例如 serve 間接載入爬蟲依賴。
- `src/website_copilot/cli/run.py`：單模組執行 `run website-crawler | image-summarizer | rag-build | rag-query | agent`，收集 `run` 與 `module` 參數並 dispatch 到對應 pipeline（`run_config` 以參數傳入，`run_config.toml` 由 pipeline 函式寫出）。
- `src/website_copilot/cli/{prepare,serve,exp}.py`：兩階段入口與批次實驗的參數定義，分別呼叫 `pipelines.prepare.run_prepare`、`pipelines.serve.serve`、`pipelines.exp.run_experiment`。
- `src/website_copilot/pipelines/{prepare,serve,exp}.py`：實作主要 pipeline（prepare：`run_website_crawler`、`run_webpage_image_summarizer`、`run_rag_build`、`run_prepare`；serve：`run_agent_build`、`run_server_build`、`serve`；exp：`run_rag_query`、`run_agent_query` 與批次實驗），負責載入 module config、執行流程與落盤結果。`run_agent_query` 為 CLI 問答的完整入口（建立 run context、agent 與落盤），`run_agent_build` 為 agent 建構 + 落盤的程式化 API（`run_server_build` 透過它建構 agent；`run_agent_query` 不經過它）。
- `src/website_copilot/pipelines/serve.py`：`run_server_build`（建立 agent + ChatApp + ChatServer）與 `serve`（`run_server_build` → `server.run()` → 關閉）。
- [src/website_copilot/config/pipeline_config.py](src/website_copilot/config/pipeline_config.py)：定義 run 相關 dataclass（`BaseRunConfig` 與各 module 的 RunConfig），以及 CLI 可覆寫的 module 欄位，供 `tyro` 與程式使用。
  - `RAGBuildRunConfig` 的 `save`／`publish` 決定向量庫建置位置：`save=True` 時向量庫建在本次 run 的 `results/milvus.db`；`save=False` 時建在暫存資料夾（結束即刪）；`publish=True` 時才原子替換到 `data/rag/<site_id>/milvus.db`（詳見 workflow.md）。
- [src/website_copilot/storage/run_manager.py](src/website_copilot/storage/run_manager.py)：管理 `runs/<timestamp>/<module>/<site_id>/<run>/` 四層路徑，提供結果儲存、module/run config 路徑、log 與路徑顯示功能。
- `src/website_copilot/utils/config_helper.py`：共用設定工具，提供載入、覆寫、與寫出 TOML 的 helper 函式。

## 二、CLI 解析與 dispatch 流程

1. `cli/__init__.py` 定義頂層子命令 union：`PrepareCLI | ServeCLI | RunCLI | ExpCLI`（以 `tyro.conf.subcommand` 命名為 `prepare` / `serve` / `run` / `exp`）。
2. `RunCLI` 的 `command` 欄位為第二層子命令 union：`WebsiteCrawlerCLI | WebpageImageSummarizerCLI | RAGBuildCLI | RAGQueryCLI | AgentCLI`（`website-crawler` / `image-summarizer` / `rag-build` / `rag-query` / `agent`）。
   - 每個 dataclass 包含兩個欄位：`run`（RunConfig）與 `module`（module-specific overrides dataclass），命令列參數為 `--run.*` 與 `--module.*`。
   - `RAGBuildCLI.module` / `RAGQueryCLI.module`（`RAGModuleConfig`）支援以下 hybrid 相關覆寫：
     - `hybrid_ranker` — 切換 `"RRFRanker"` / `"WeightedRanker"`
     - `weights` — `list[float]`，設定 WeightedRanker 權重（`--module.weights 1.0 0.5`；CLI 會轉為 `hybrid_ranker_params={"weights": [...]}`）
     - `similarity_top_k`、`query_mode`、`hybrid_top_k`、`alpha` — retriever 參數
     - `cutoff`、`query` — query engine 參數
3. `tyro.cli(...)` 解析命令列並回傳對應的 dataclass 實例，`main()` 依型別 dispatch 到子命令模組的 `main()`。
4. `run` 子命令：
   - 以 `vars(command.module)` 收集 module 參數，僅保留非 `None` 欄位作為 `module_config_overrides`。
   - 複製 `vars(command.run)` 後拆出 `save`／`publish`（不修改 `command.run` 本身，`run_config.toml` 會完整記錄這兩個參數）。
   - 資料 pipeline（crawler / summarizer / rag_build）：傳入 `**run_kwargs`、`save`、`publish`、`run_config=command.run` 與 `**module_config_overrides`；rag_query 不接受 `save`／`publish`。
   - Agent 分支：`run_agent_query(...)` 負責 agent 的建立與關閉（於 `finally` 呼叫 `agent.close()`）；`RunManager` 由入口函式內部建立，`Agent` 不持有。
5. `run_*` 會透過對應 Config 的 `from_toml(config_name, **config_overrides)`：
   - 組出 `configs/<module>/{config_name}.toml`，
   - 用 `load_config_from_toml()` 載入 sections，
   - 用 `override_config()` 合併 CLI 傳入的 overrides（依 `sections_to_keys` 過濾），
   - 建構 dataclass 並執行模組內驗證。
6. `run_config.toml` 由各 pipeline 函式在流程中呼叫 `save_run_config_as_toml()` 寫出（CLI 將 `command.run` 以 `run_config=` 傳入），把 run-level 參數寫入本次 run 的 `run_config.toml`。

### Agent 問答（`run agent`）

- `AgentCLI.run`（`AgentRunConfig`）：`query`（必填）、`config_name`（預設 `default`）、`thread_id`（多輪 session）、`stream`（逐 token 串流）。
- 由 `pipelines.exp.run_agent_query` 執行（單一入口負責 agent 生命週期）：建立 run context（`create_run_no_site_context(module="agent", base_folder="runs")`）→ 直接呼叫 `create_agent()` 建立 agent（`Tool` + LLM + 編譯圖，**不經 `run_agent_build()`**）→ 問答（`stream` 決定串流/非串流）→ 顯示回答與來源 → `run_manager.save_agent_results_as_json(thread_id, [result], agent_config=agent.config)` 落盤 `runs/<ts>/agent/<config>/results_{thread_id}.json` → 寫出 `module_config.toml`（與 `run_config.toml`）→ `finally` 呼叫 `agent.close()` 釋放資源。
- 對話結果與實驗共用 `runs/`（module=`agent`）；`thread_id` 未提供時自動產生 `auto-{uuid}`（每次執行獨立）；`run_config.toml` 與 `log_run_paths`（`init` → `complete`）皆於 `run_agent_query` 內寫出。

```bash
uv run website-copilot run agent --run.query "實驗室的成員有哪些人？"
uv run website-copilot run agent --run.query "..." --run.thread-id demo --run.stream
```

### 聊天伺服器（`serve`）

- `ServeCLI.run`（`ServeRunConfig`）：`config_name`（預設 `default`）、`host`、`port`、`allowed_origins`（CORS 限縮，預設 None 全開放）。
- 由 `pipelines.serve.serve` 啟動：呼叫 `run_server_build`（函式內建立 run context，並以 `run_agent_build(run_manager=...)` 在同一 context 內建構 agent → 建立 `ChatApp.create(agent, run_manager, allowed_origins)` + `uvicorn.Config` → 回傳持有 `chat_app` 的非阻塞 `ChatServer`）→ `server.run()` 阻塞 → `ChatServer.serve()` 結束時於 `finally` 呼叫 `chat_app.close()` 關閉 agent。`run_config.toml` 由 `run_server_build` 寫出、`module_config.toml` 由 `run_agent_build` 寫出（傳 app 物件而非 import string，避免 reloader sys.path 問題）。
- agent 於啟動前建立一次後注入 app（lifespan 僅綁定，不重建；不可 per-request 建立）。
- 啟動後瀏覽器開啟 `http://localhost:8000/`（redirect 至 `/static/demo.html` 嵌入示範）。

```bash
uv run website-copilot serve --run.port 8000
uv run website-copilot serve --run.allowed-origins https://lab.example.edu.tw
```

### 批次實驗（`exp`）

- `ExpCLI.name`（位置參數，預設 `rag_dense_vs_hybrid`）對應 `pipelines.exp.EXPERIMENTS` 的名稱；CLI 端的名稱清單由測試比對，確保與 `EXPERIMENTS` 一致。

```bash
uv run website-copilot exp rag_hybrid_top_k
```

## 三、參數覆寫規則要點

- CLI 的 module-level overrides 由 `vars(command.module)` 收集，並透過 `utils.config_helper.override_config()` 做 allowed-keys 過濾；未列在 `sections_to_keys` 的欄位會被忽略並記 warning。
- 若某 section 的 allowed-keys 為空集合（例如 `litellm_kwargs`），helper 會允許該 section 的任意 key，使延伸參數能直接以 `**config.litellm_kwargs` 傳入 runtime 呼叫。

## 四、`run_config.toml` 與 `module_config.toml` 的差異與產生時機

- `module_config.toml`：由 pipeline（`run_*`）呼叫 `save_module_config_as_toml(config, run_manager.module_config_toml_path)` 產生，內容以 `sections_to_keys` 為準分 section 寫出；若存在 residual section（section keys 為空），未消耗欄位會寫入該 residual section。
- `run_config.toml`：由 pipeline 函式在 `run_config` 非 None 時呼叫 `save_run_config_as_toml(...)` 寫出（僅包含非 `None` 欄位，含 `save`／`publish`）。`website-copilot run` 與 `serve` 會傳入 run 參數（`website-copilot prepare` 目前不寫出）。

## 五、執行範例

```bash
# 範例：rag query 並覆寫 module 的 similarity_top_k（強制重建向量庫）
uv run website-copilot run rag-query --run.config-name test --run.force-rebuild --module.similarity-top-k 10

# 範例：切換至 WeightedRanker 並自訂權重
uv run website-copilot run rag-query --run.config-name milvus --module.hybrid-ranker WeightedRanker --module.weights 1.0 0.5

# 範例：設定 hybrid 檢索參數（test 與 default 皆為 Milvus hybrid；此處示範 CLI 覆寫）
uv run website-copilot run rag-query --run.config-name test --module.query-mode hybrid --module.hybrid-top-k 20 --module.alpha 0.7

# 範例：RAG 建置（向量庫存在本次 run 的 results/），並原子替換發布到 data/rag/
uv run website-copilot run rag-build --run.config-name default --run.publish
```

## 六、注意事項與建議

- 若需讓更多欄位能由 CLI 覆寫，請在 `config/pipeline_config.py` 的對應 ModuleConfig 加欄位，並確認 `src/website_copilot/config/*_config.py` 的 `sections_to_keys` 包含該欄位。
- 自行呼叫 pipeline 函式時，將 `run_config`（對應 RunConfig 實例）傳入即可寫出 `run_config.toml`；函式內會呼叫 `utils.config_helper.save_run_config_as_toml()` 並以 `RunManager.run_config_toml_path` 為目標路徑。

## 七、參考與證據

- `src/website_copilot/cli/`
- `src/website_copilot/pipelines/prepare.py`
- `src/website_copilot/pipelines/serve.py`
- `src/website_copilot/pipelines/exp.py`
- [src/website_copilot/config/pipeline_config.py](src/website_copilot/config/pipeline_config.py)
- [src/website_copilot/storage/run_manager.py](src/website_copilot/storage/run_manager.py)
- [src/website_copilot/storage/data_manager.py](src/website_copilot/storage/data_manager.py)
- `src/website_copilot/utils/config_helper.py`
