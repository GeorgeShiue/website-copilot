# CLI

## 一、主要檔案與角色

- `src/cli.py`：CLI 入口，使用 `tyro` 解析 dataclass 型態，收集 `run` 與 `module` 參數並 dispatch 到對應 pipeline，結束時寫入 `run_config.toml`。
- `[src/app/workflow/workflow.py](src/app/workflow/workflow.py)`：實作主要 pipeline（`run_website_crawler`、`run_webpage_image_summarizer`、`run_rag_build`、`run_rag_query`），負責載入 module config、執行流程、寫入 `module_config.toml` 與結果。
- `[src/app/workflow/workflow_config.py](src/app/workflow/workflow_config.py)`：定義 run 相關 dataclass（`BaseRunConfig` 與各 module 的 RunConfig），供 `tyro` 與程式使用。
  - `RAGBuildRunConfig` 含 `save_vector_store_to_runs`（預設 `False`，CLI 旗標 `--run.save-vector-store-to-runs`）：開啟時向量庫寫入本次 run 的 `results/vector_store/`。
- `[src/app/workflow/workflow_manager.py](src/app/workflow/workflow_manager.py)`：管理 `runs/<timestamp>/<module>/<run>/` 路徑，提供結果儲存、module/run config 路徑、log 與路徑顯示功能。
- `src/utils/config_helper.py`：共用設定工具，提供載入、覆寫、與寫出 TOML 的 helper 函式。

## 二、CLI 解析與 dispatch 流程

1. `src/cli.py` 定義 union 型別：`WebsiteCrawlerCLI | WebpageImageSummarizerCLI | RagBuildCLI | RagQueryCLI | AgentCLI | ServerCLI`。
   - 每個 dataclass 包含兩個欄位：`run`（RunConfig）與 `module`（module-specific overrides dataclass）。
   - `RAGConfigCLI.module` 支援以下 hybrid 相關覆寫：
     - `hybrid_ranker` — 切換 `"RRFRanker"` / `"WeightedRanker"`
     - `weights` — `list[float]`，設定 WeightedRanker 權重（`[1.0, 0.5]`）
     - `similarity_top_k`、`query_mode`、`hybrid_top_k`、`alpha` — retriever 參數
     - `cutoff`、`query` — query engine 參數
2. 使用 `tyro.cli(...)` 解析命令列並回傳對應的 dataclass 實例 `cli_arg`。
3. 以 `vars(cli_arg.module)` 收集 module 參數，僅保留非 `None` 欄位作為 `module_config_overrides`。
4. 根據 `cli_arg` 型別，呼叫 `RunManager.set_module_path(<module>)`，再呼叫相對應的 `run_*` 函式，並傳入：
   - `run_manager`，
   - `**vars(cli_arg.run)`（如 `config_name`, `run_name_use_config_name`, `force_rebuild`, `save_vector_store_to_runs` 等），
   - `**module_config_overrides`（僅 CLI 明確提供的 module-level 覆寫）。
5. `run_*` 會透過對應 Config 的 `from_toml(config_name, **config_overrides)`：
   - 組出 `configs/<module>/{config_name}.toml`，
   - 用 `load_config_from_toml()` 載入 sections，
   - 用 `override_config()` 合併 CLI 傳入的 overrides（依 `sections_to_keys` 過濾），
   - 建構 dataclass 並執行模組內驗證。
6. CLI 主流程結束時，`src/cli.py` 呼叫 `save_run_config_as_toml(cli_arg.run, run_manager.run_config_toml_path)`，把 run-level 參數寫入 `run_config.toml`。

### Agent 問答（agent-cli）

- `AgentCLI.run`（`AgentRunConfig`）：`query`（必填）、`config_name`（預設 `default`）、`thread_id`（多輪 session）、`stream`（逐 token 串流）。
- 由 `workflow.run_agent` 執行：建立 agent（`create_agent`）→ 問答（stream 決定串流/非串流）→ 顯示回答與來源 → 落盤 `chats/<ts>/agent/<config>/` → `agent.close()` 釋放資源。
- 聊天記錄與實驗分離：使用獨立 `RunManager(base_folder="chats")`，`save_run_config_as_toml` 與 `log_run_paths("complete")` 於 CLI 分支執行。

```bash
uv run python src/cli.py agent-cli --run.query "實驗室的成員有哪些人？"
uv run python src/cli.py agent-cli --run.query "..." --run.thread-id demo --run.stream
```

### 聊天伺服器（server-cli）

- `ServerCLI.run`（`ServerRunConfig`）：`config_name`（預設 `default`）、`host`、`port`、`allowed_origins`（CORS 限縮，預設 None 全開放）。
- 呼叫 `server.app.run_server`（常駐服務，不落盤 run config）：`setup_logging` → `create_app` → `uvicorn.run`（傳 app 物件而非 import string，避免 reloader sys.path 問題）。
- agent 於 FastAPI lifespan 啟動時建立一次、關閉時釋放（`create_agent` 每次會重建向量庫隔離副本，不可 per-request 建立）。
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
- `run_config.toml`：由呼叫端在流程結束時呼叫 `save_run_config_as_toml(...)` 寫出（僅包含非 `None` 欄位）。目前 `src/cli.py` 與 `src/main.py` 都會寫出；直接呼叫 `[src/app/workflow/workflow.py](src/app/workflow/workflow.py)` 的 workflow 函式則不會自動寫入。

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
- 若自行呼叫 workflow 函式（非 CLI / 非 src/main.py 入口）也希望寫出 `run_config.toml`，可在呼叫端於 pipeline 執行完後顯式呼叫 `utils.config_helper.save_run_config_as_toml()` 並以 `RunManager.run_config_toml_path` 為目標路徑。

## 七、參考與證據

- `src/cli.py`
- `[src/app/workflow/workflow.py](src/app/workflow/workflow.py)`
- `[src/app/workflow/workflow_config.py](src/app/workflow/workflow_config.py)`
- `[src/app/workflow/workflow_manager.py](src/app/workflow/workflow_manager.py)`
- `src/utils/config_helper.py`