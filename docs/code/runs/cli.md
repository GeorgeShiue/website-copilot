# CLI

## 一、主要檔案與角色

- `website-copilot`：單一 CLI 指令（`pyproject.toml` 的 `[project.scripts]` → `website_copilot.cli:main`；也可用 `python -m website_copilot.cli`）。
- `src/website_copilot/cli/__init__.py`：`main()` 以 `tyro` 解析子命令 `prepare | serve | run` 並 dispatch 到對應子命令模組。各子命令模組只在頂層 import 參數 dataclass，執行邏輯在 `main()` 內延遲 import，避免例如 serve 間接載入爬蟲依賴。
- `src/website_copilot/cli/run.py`：單模組執行 `run website-crawler | image-summarizer | rag-build | rag-query | agent`，將 `run`（RunConfig）與 `module`（自動產生的覆寫值）交給對應 pipeline：`run_xxx(command.run, overrides)`。
- `src/website_copilot/cli/{prepare,serve}.py`：兩階段入口的參數定義，分別呼叫 `pipelines.prepare.run_prepare(run_config)`、`pipelines.serve.serve(run_config)`。
- `src/website_copilot/pipelines/{prepare,serve,exp}.py`：實作主要 pipeline（prepare：`run_website_crawler`、`run_image_summarizer`、`run_rag_build`、`run_prepare`；serve：`run_agent_build`、`run_server_build`、`serve`；exp：`run_rag_query`、`run_agent_query`），負責載入 module config、執行流程與落盤結果。`run_agent_query` 為 CLI 問答的完整入口（建立 run context、問答與落盤），`run_agent_build` 為 agent 建構 + 落盤的程式化 API（`serve` 透過它建構 agent 再注入 `run_server_build`；`run_agent_query` 也透過它建構 agent）。
- `src/website_copilot/pipelines/serve.py`：`run_agent_build`（建構 agent）、`run_server_build`（以注入的 agent 建立 ChatApp + ChatServer）與 `serve`（`run_agent_build` → `run_server_build` → `server.run()` → 關閉）。
- [src/website_copilot/config/pipeline_config.py](src/website_copilot/config/pipeline_config.py)：定義 run 相關 dataclass（`BaseRunConfig` 與各 module 的 RunConfig），供 `tyro` 與程式使用。`site` 為必填的位置參數（`Annotated[str, tyro.conf.Positional]`，metavar `SITE`），對應 `configs/sites/{site}.yml`；agent／serve 為多站，沒有 `site`。`config_name` 在 CLI 上為 `--run.config`（`tyro.conf.arg(name="config")`），Python 屬性維持 `config_name`。
- [src/website_copilot/config/overrides.py](src/website_copilot/config/overrides.py)：`make_overrides_model()` 由 module config 自動產生 CLI 覆寫用的 partial model（`{Config}Overrides`），`overrides_to_dict()` 轉成只含已指定欄位的巢狀 dict。
  - `RAGBuildRunConfig` 的 `save`／`publish` 決定向量庫建置位置：`save=True` 時向量庫建在本次 run 的 `results/milvus.db`；`save=False` 時建在暫存資料夾（結束即刪）；`publish=True` 時才原子替換到 `data/rag/<site_id>/milvus.db`（詳見 workflow.md）。
- [src/website_copilot/storage/run_manager.py](src/website_copilot/storage/run_manager.py)：管理 `runs/<timestamp>/<module>/<site_id>/<run>/` 四層路徑，提供結果儲存、module/run config 路徑、log 與路徑顯示功能。
- `src/website_copilot/utils/config_helper.py`：共用設定工具，提供寫出 module_config.yml／run_config.yml 與顯示 config 的 helper 函式。

## 二、CLI 解析與 dispatch 流程

1. `cli/__init__.py` 定義頂層子命令 union：`PrepareCLI | ServeCLI | RunCLI`（以 `tyro.conf.subcommand` 命名為 `prepare` / `serve` / `run`）。
2. `RunCLI` 的 `command` 欄位為第二層子命令 union：`WebsiteCrawlerCLI | ImageSummarizerCLI | RAGBuildCLI | RAGQueryCLI | AgentCLI`（`website-crawler` / `image-summarizer` / `rag-build` / `rag-query` / `agent`）。
   - 每個 dataclass 包含兩個欄位：`run`（RunConfig）與 `module`（`make_overrides_model()` 從對應 module config 產生的 `{Config}Overrides`），命令列參數為 `--run.*` 與 `--module.*`。
   - `--module.*` 的巢狀結構與設定檔相同，如 `--module.retriever.similarity-top-k 20`、`--module.vector-store.hybrid-ranker-params.weights 1.0 0.3`；module config 新增欄位時 CLI 自動跟著產生，不需手動同步。
3. `tyro.cli(...)` 解析命令列並回傳對應的 dataclass 實例，`main()` 依型別 dispatch 到子命令模組的 `main()`。
4. `run` 子命令：以 `overrides_to_dict(command.module)` 取得只含已指定欄位的巢狀 dict（未指定的欄位與 section 不會出現），連同 `command.run` 傳給對應 pipeline：`run_xxx(command.run, overrides)`。
   - `config_name`、`save`、`publish` 等一律由 pipeline 從 `run_config` 讀取，不再展開傳遞。
   - Agent 分支：`run_agent_query(run_config, overrides)` 負責 agent 的建立與關閉（於 `finally` 呼叫 `agent.close()`）。
5. pipeline 以 `SiteConfig.from_yaml(run_config.site)` 載入站點，並以 `Config.from_yaml(run_config.config_name, overrides)` 載入模組設定：讀取 `configs/<module>/{config_name}.yml` 並展開 `extends`，overrides 以同一個 deep merge 疊在最上層（父檔 < 子檔 < overrides），最後以 pydantic 驗證一次（失敗時拋出含設定檔路徑的 `ConfigValidationError`，來源標示 `+ overrides`）。
6. `run_config` 為必填，pipeline 一律呼叫 `save_run_config()` 寫出 `run_config.yml`。

### Agent 問答（`run agent`）

- `AgentCLI.run`（`AgentRunConfig`）：`query`（必填）、`config_name`（`--run.config`，預設 `default`）、`thread_id`（多輪 session）、`stream`（逐 token 串流）。
- 由 `pipelines.exp.run_agent_query` 執行（單一入口負責 agent 生命週期）：`run_agent_build()` 建構 agent（`Tool` + LLM + 編譯圖；獨立的 `runs/<ts>/agent_build/<config>/`，寫出 `module_config.yml` 與 `run_config.yml`）→ 建立 run context（`create_run_no_site_context(module="agent", base_folder="runs")`）→ 問答（`stream` 決定串流/非串流）→ 顯示回答與來源 → `run_manager.save_agent_results_as_json(thread_id, [result], agent_config=agent.config)` 落盤 `runs/<ts>/agent/<config>/results_{thread_id}.json` → 寫出 `run_config.yml`（不寫 `module_config.yml`）→ `finally` 呼叫一次 `agent.close()` 釋放資源。
- 對話結果與實驗共用 `runs/`（module=`agent`）；`thread_id` 未提供時自動產生 `auto-{uuid}`（每次執行獨立）；`run_config.yml` 與 `log_run_paths`（`init` → `complete`）皆於 `run_agent_query` 內寫出。

```bash
uv run website-copilot run agent --run.query "實驗室的成員有哪些人？"
uv run website-copilot run agent --run.query "..." --run.thread-id demo --run.stream
```

### 聊天伺服器（`serve`）

- `ServeCLI.run`（`ServeRunConfig`）：`config_name`（`--run.config`，預設 `default`）、`host`、`port`、`allowed_origins`（CORS 限縮，預設 None 全開放）。
- 由 `pipelines.serve.serve(run_config)` 啟動：以同一個 `ServeRunConfig` 先呼叫 `run_agent_build(run_config)`（自己的 run context `runs/<ts>/agent_build/<config>/`，寫出 `module_config.yml`）建構 agent → 注入 `run_server_build(agent, run_config)`（自己的 run context `runs/<ts>/server/<config>/`，建立 `ChatApp.create(agent, run_manager, allowed_origins)` + `uvicorn.Config` → 回傳持有 `chat_app` 的非阻塞 `ChatServer`；失敗時由 `serve` 關閉 agent）→ `server.run()` 阻塞 → `ChatServer.serve()` 結束時於 `finally` 呼叫 `chat_app.close()` 關閉 agent。`run_config.yml` 由 `run_server_build` 寫出（server 目錄不寫 `module_config.yml`；傳 app 物件而非 import string，避免 reloader sys.path 問題）。
- agent 於啟動前建立一次後注入 app（lifespan 僅綁定，不重建；不可 per-request 建立）。
- 啟動後瀏覽器開啟 `http://localhost:8000/`（redirect 至 `/static/demo.html` 嵌入示範）。

```bash
uv run website-copilot serve --run.port 8000
uv run website-copilot serve --run.allowed-origins https://lab.example.edu.tw
```

## 三、參數覆寫規則要點

- `{Config}Overrides` 的產生規則（`config/overrides.py`）：
  - 巢狀 section（含 `hybrid_ranker_params` 這類 `Model | None` 的可選 section）→ 巢狀 partial model，以預設實例作為預設值。
  - 葉欄位 → `X | None = None`，`None` 代表「未指定」；`Literal` 欄位保留選項清單，`Field(description=...)` 帶入 `--help`。
  - `--help` 以 `(default: X)` 顯示 config class 的預設值（長字串截斷；可選 section 如 `hybrid_ranker_params` 取上層預設實例的值），沒有預設值的欄位標示「(必填，來自設定檔)」（目前模組 config 皆有預設值）；以 metavar 隱藏 `None` 選項（顯示 `INT`、`{hybrid,default}`、`FLOAT [FLOAT ...]`）。實際執行時 `--run.config` 設定檔的值優先於此預設。
  - `dict[str, Any]` 欄位（`litellm_kwargs`）tyro 無法處理，排除在 CLI 之外，只能寫在設定檔。
- CLI 無法把欄位設為 `null`（`None` 即「未指定」）；需要時另寫 extends 設定檔。
- 型別錯誤（如 `--module.retriever.similarity-top-k abc`、不在 `Literal` 內的值）由 tyro 擋下；範圍與跨欄位規則在 `from_yaml()` 合併後由 pydantic 驗證（如只改 `--module.vector-store.hybrid-ranker RRFRanker` 時，`hybrid_ranker_params` 仍為預設的 `weights`，會被跨欄位規則擋下；需同時指定 `--module.vector-store.hybrid-ranker-params.k 60`）。
- bool 欄位以值指定：`--module.init.light-mode False`。

## 四、`run_config.yml` 與 `module_config.yml` 的差異與產生時機

- `module_config.yml`：由 pipeline（`run_*`）呼叫 `save_module_config(config, run_manager.module_config_path)` 產生，內容為 extends 展開後的完整 config（`model_dump()`，`None` 寫成 `null`），檔頭註解記錄來源設定檔與 `run_name_fields`。
- `run_config.yml`：`run_config` 為必填，所有 pipeline 函式都以 `save_run_config(...)` 寫出（包含所有欄位，`None` 寫成 `null`，含 `save`／`publish`）。`website-copilot prepare` 由 `run_prepare` 以同一個 config 名稱建立各階段的 RunConfig，因此各階段（含 publish 到 data/）都會寫出。
- `module_config.yml` 檔頭的 `source` 在有 CLI 覆寫時結尾為 `+ overrides`，實際覆寫值已包含在檔案內容中。

## 五、執行範例

```bash
# 範例：rag query 並覆寫 retriever 的 similarity_top_k（強制重建向量庫）
uv run website-copilot run rag-query nculab --run.config test --run.force-rebuild --module.retriever.similarity-top-k 10

# 範例：指定查詢問題（未指定時使用站點的 sample_query）
uv run website-copilot run rag-query ncucsie --run.query "介紹資工系課程"

# 範例：自訂 WeightedRanker 權重
uv run website-copilot run rag-query nculab --module.vector-store.hybrid-ranker-params.weights 1.0 0.3

# 範例：設定 hybrid 檢索參數
uv run website-copilot run rag-query nculab --module.retriever.hybrid-top-k 20 --module.retriever.alpha 0.7

# 範例：限制爬取頁數
uv run website-copilot run website-crawler nculab --module.init.max-pages 10

# 範例：RAG 建置（向量庫存在本次 run 的 results/），並原子替換發布到 data/rag/
uv run website-copilot run rag-build nculab --run.publish

# 範例：prepare（站點為位置參數；--run.no-publish 只存 runs/）
uv run website-copilot prepare ncucsie --run.config test --run.no-publish
```

## 六、注意事項與建議

- module config 新增欄位時不需修改 CLI：`--module.*` 由 `make_overrides_model()` 自動產生（`dict` 欄位除外）。
- 自行呼叫 pipeline 函式時傳入 RunConfig 與巢狀 overrides，如 `run_rag_query(RAGQueryRunConfig(config_name="test"), {"retriever": {"similarity_top_k": 20}})`、`run_prepare(PrepareRunConfig(config_name="test", publish=False))`。

## 七、參考與證據

- `src/website_copilot/cli/`
- [src/website_copilot/config/overrides.py](src/website_copilot/config/overrides.py)
- `src/website_copilot/pipelines/prepare.py`
- `src/website_copilot/pipelines/serve.py`
- `src/website_copilot/pipelines/exp.py`
- [src/website_copilot/config/pipeline_config.py](src/website_copilot/config/pipeline_config.py)
- [src/website_copilot/storage/run_manager.py](src/website_copilot/storage/run_manager.py)
- [src/website_copilot/storage/data_manager.py](src/website_copilot/storage/data_manager.py)
- `src/website_copilot/utils/config_helper.py`
