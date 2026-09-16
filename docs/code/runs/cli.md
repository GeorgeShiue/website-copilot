# CLI

## 一、主要檔案與角色

- `src/cli.py`：CLI 入口，使用 `tyro` 解析 dataclass 型態，收集 `run` 與 `module` 參數並 dispatch 到對應 pipeline（`run_config` 以參數傳入，`run_config.toml` 由 pipeline 函式寫出）。
- `[src/app/workflow/workflow.py](src/app/workflow/workflow.py)`：實作主要 pipeline（`run_website_crawler`、`run_webpage_image_summarizer`、`run_rag_build`、`run_rag_query`、`run_agent_build`、`run_agent_query`、`run_app`），負責載入 module config、執行流程與落盤結果。其中 `run_agent_query` / `run_app` 為 CLI 與 server 的完整入口（各自建立 run context、agent 與落盤），`run_agent_build` 為 agent 建構 + 落盤的程式化 API（兩者不經過它）。
- `[src/app/configs/workflow_config.py](src/app/configs/workflow_config.py)`：定義 run 相關 dataclass（`BaseRunConfig` 與各 module 的 RunConfig），供 `tyro` 與程式使用。
  - `RAGBuildRunConfig` 含 `save_vector_store_to_runs`（預設 `False`，CLI 旗標 `--run.save-vector-store-to-runs`）：開啟時向量庫寫入本次 run 的 `results/vector_store/`。
- `[src/app/workflow/run_manager.py](src/app/workflow/run_manager.py)`：管理 `runs/<timestamp>/<module>/<site_id>/<run>/` 四層路徑，提供結果儲存、module/run config 路徑、log 與路徑顯示功能。
- `src/utils/config_helper.py`：共用設定工具，提供載入、覆寫、與寫出 TOML 的 helper 函式。

## 二、CLI 解析與 dispatch 流程

1. `src/cli.py` 定義 union 型別：`WebsiteCrawlerCLI | WebpageImageSummarizerCLI | RAGBuildCLI | RAGQueryCLI | AgentCLI | ServerCLI`。
   - 除 `ServerCLI`（僅 `run` 欄位）外，每個 dataclass 包含兩個欄位：`run`（RunConfig）與 `module`（module-specific overrides dataclass）。
   - `RAGBuildCLI.module` / `RAGQueryCLI.module`（`RAGModuleConfig`）支援以下 hybrid 相關覆寫：
     - `hybrid_ranker` — 切換 `"RRFRanker"` / `"WeightedRanker"`
     - `weights` — `list[float]`，設定 WeightedRanker 權重（`[1.0, 0.5]`；CLI 會轉為 `hybrid_ranker_params={"weights": [...]}`）
     - `similarity_top_k`、`query_mode`、`hybrid_top_k`、`alpha` — retriever 參數
     - `cutoff`、`query` — query engine 參數
2. 使用 `tyro.cli(...)` 解析命令列並回傳對應的 dataclass 實例 `cli_arg`。
3. 非 `ServerCLI` 分支以 `vars(cli_arg.module)` 收集 module 參數，僅保留非 `None` 欄位作為 `module_config_overrides`（`ServerCLI` 無 `module` 欄位，直接跳過）。
4. 根據 `cli_arg` 型別 dispatch 對應的 workflow 入口：
   - 資料 pipeline（crawler / summarizer / rag_build / rag_query）：傳入 `**run_kwargs`（`vars(cli_arg.run)`，剔除 `publish`）、`data_manager`（`publish` 開啟時建立）、`run_config=cli_arg.run` 與 `**module_config_overrides`。
   - Agent / Server 分支：`run_agent_query(...)` / `run_app(...)` 各自負責 agent 的建立與關閉（Agent 分支於 `finally` 呼叫 `agent.close()`；Server 分支以 `try/finally` 呼叫 `chat_app.close()`）；`RunManager` 由各入口函式內部建立，`Agent` 不再持有。
5. `run_*` 會透過對應 Config 的 `from_toml(config_name, **config_overrides)`：
   - 組出 `configs/<module>/{config_name}.toml`，
   - 用 `load_config_from_toml()` 載入 sections，
   - 用 `override_config()` 合併 CLI 傳入的 overrides（依 `sections_to_keys` 過濾），
   - 建構 dataclass 並執行模組內驗證。
6. `run_config.toml` 由各 pipeline 函式在流程中呼叫 `save_run_config_as_toml()` 寫出（CLI 將 `cli_arg.run` 以 `run_config=` 傳入），把 run-level 參數寫入本次 run 的 `run_config.toml`。

### Agent 問答（agent-cli）

- `AgentCLI.run`（`AgentRunConfig`）：`query`（必填）、`config_name`（預設 `default`）、`thread_id`（多輪 session）、`stream`（逐 token 串流）。
- 由 `workflow.run_agent_query` 執行（單一入口負責 agent 生命週期）：建立 run context（`create_run_no_site_context(module="agent", base_folder="runs")`）→ 直接呼叫 `create_agent()` 建立 agent（`Tool` + LLM + 編譯圖，**不經 `run_agent_build()`**）→ 問答（`stream` 決定串流/非串流）→ 顯示回答與來源 → `run_manager.save_agent_results_as_json(thread_id, [result], agent_config=agent.config)` 落盤 `runs/<ts>/agent/<config>/results_{thread_id}.json` → 寫出 `module_config.toml`（與 `run_config.toml`）→ `finally` 呼叫 `agent.close()` 釋放資源。
- 對話結果與實驗共用 `runs/`（module=`agent`）；`thread_id` 未提供時自動產生 `auto-{uuid}`（每次執行獨立）；`run_config.toml` 與 `log_run_paths`（`init` → `complete`）皆於 `run_agent_query` 內寫出。

```bash
uv run python src/cli.py agent-cli --run.query "實驗室的成員有哪些人？"
uv run python src/cli.py agent-cli --run.query "..." --run.thread-id demo --run.stream
```

### 聊天伺服器（server-cli）

- `ServerCLI.run`（`ServerRunConfig`）：`config_name`（預設 `default`）、`host`、`port`、`allowed_origins`（CORS 限縮，預設 None 全開放）。
- 由 `workflow.run_app` 啟動：函式內建立 run context 與直接呼叫 `create_agent()`（建立 agent，**不經 `run_agent_build()`**）→ 建立 `ChatApp.create(agent, run_manager, allowed_origins)` + `uvicorn.Config` → 回傳 `(server, chat_app)`（server 為非阻塞 `uvicorn.Server`）→ 呼叫端 `server.run()` 阻塞，並以 `try/finally` 呼叫 `chat_app.close()` 關閉 agent。`run_config.toml` 由 `run_app` 寫出（不寫 `module_config.toml`；傳 app 物件而非 import string，避免 reloader sys.path 問題）。
- agent 由 CLI 於啟動前建立一次後注入 app（lifespan 僅綁定，不重建；`create_agent` 每次會重建向量庫隔離副本，不可 per-request 建立）。
- 啟動後瀏覽器開啟 `http://localhost:8000/`（redirect 至 `/static/demo.html` 嵌入示範）。

```bash
uv run python src/cli.py server-cli --run.port 8000
uv run python src/cli.py server-cli --run.allowed-origins https://lab.example.edu.tw
```

## 三、參數覆寫規則要點

- CLI 的 module-level overrides 由 `vars(cli_arg.module)` 收集，並透過 `utils.config_helper.override_config()` 做 allowed-keys 過濾；未列在 `sections_to_keys` 的欄位會被忽略並記 warning。
- 若某 section 的 allowed-keys 為空集合（例如 `litellm_kwargs`），helper 會允許該 section 的任意 key，使延伸參數能直接以 `**config.litellm_kwargs` 傳入 runtime 呼叫。

## 四、`run_config.toml` 與 `module_config.toml` 的差異與產生時機

- `module_config.toml`：由 pipeline（`run_*`）呼叫 `save_module_config_as_toml(config, run_manager.module_config_toml_path)` 產生，內容以 `sections_to_keys` 為準分 section 寫出；若存在 residual section（section keys 為空），未消耗欄位會寫入該 residual section。
- `run_config.toml`：由 workflow 函式在 `run_config` 非 None 時呼叫 `save_run_config_as_toml(...)` 寫出（僅包含非 `None` 欄位）。`src/cli.py` 會傳入 run 參數（`src/main.py` 目前不寫出）。

## 五、執行範例

```bash
# 範例：使用 rag query CLI 並覆寫 module 的 similarity_top_k 與 hybrid_ranker
python src/cli.py rag-query-cli --run.config-name test --run.force-rebuild --module.similarity_top_k 10

# 範例：切換至 WeightedRanker 並自訂權重
python src/cli.py rag-query-cli --run.config-name milvus --module.hybrid_ranker WeightedRanker --module.weights "[1.0, 0.5]"

# 範例：設定 hybrid 檢索參數（test 與 default 皆為 Milvus hybrid；此處示範 CLI 覆寫）
python src/cli.py rag-query-cli --run.config-name test --module.query_mode hybrid --module.hybrid_top_k 20 --module.alpha 0.7

# 範例：RAG 建置時把向量庫存至本次 run 的 results/vector_store/
python src/cli.py rag-build-cli --run.config-name default --run.save-vector-store-to-runs
```

（備註：開發環境常見 wrapper：`uv run python src/cli.py ...`，依環境而定）

## 六、注意事項與建議

- 若需讓更多欄位能由 CLI 覆寫，請在對應 `src/app/configs/*_config.py` 中擴充 `sections_to_keys`。
- 自行呼叫 workflow 函式時，將 `run_config`（對應 RunConfig 實例）傳入即可寫出 `run_config.toml`；函式內會呼叫 `utils.config_helper.save_run_config_as_toml()` 並以 `RunManager.run_config_toml_path` 為目標路徑。

## 七、參考與證據

- `src/cli.py`
- `[src/app/workflow/workflow.py](src/app/workflow/workflow.py)`
- `[src/app/configs/workflow_config.py](src/app/configs/workflow_config.py)`
- `[src/app/workflow/run_manager.py](src/app/workflow/run_manager.py)`
- `[src/app/workflow/data_manager.py](src/app/workflow/data_manager.py)`
- `src/utils/config_helper.py`