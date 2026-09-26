"""Serve 階段：建立 Chat Server（run_app）並管理其生命週期（serve_forever）。

只讀取 prepare 階段 publish 到 data/ 的向量庫，不 import 爬蟲與 VLM 相關模組。
"""

import uvicorn

from website_copilot.agent.agent import create_agent
from website_copilot.config.agent_config import AgentConfig
from website_copilot.config.pipeline_config import ServeRunConfig
from website_copilot.server.app import ChatApp
from website_copilot.server.server import ChatServer
from website_copilot.storage.run_context import (
    create_run_no_site_context,
    run_workflow_context,
)
from website_copilot.utils.config_helper import (
    log_config,
    save_run_config_as_toml,
)
from website_copilot.utils.log_helper import log_session, print_log


def run_app(
    config_name: str = "default",
    run_config: ServeRunConfig | None = None,
    allowed_origins: list[str] | None = None,
    host: str = "127.0.0.1",
    port: int = 8000,
    **config_overrides,
) -> tuple[uvicorn.Server, ChatApp]:
    """建立 Agent 與 ChatApp（FastAPI app）並回傳 server handle（非阻塞）。

    呼叫端可透過 server.run() 阻塞，或以 asyncio 啟動後透過 server.should_exit=True 關閉。
    agent 資源生命週期由 ChatApp 承接：呼叫端持有回傳的 chat_app 並呼叫 chat_app.close()。

    Args:
        config_name: AgentConfig 名稱（對應 configs/agent/{name}.toml）。
        run_config: ServeRunConfig 實例（可選，用於落盤 run config toml）。
        allowed_origins: CORS 允許來源（None 時全開放）。
        host: 監聽位址，預設 "127.0.0.1"。
        port: 監聽連接埠，預設 8000。
        **config_overrides: AgentConfig 覆寫值（llm_name / system_prompt）。

    Returns:
        (uvicorn.Server, ChatApp)：server 交由呼叫端 run()；chat_app 負責關閉 agent。
    """
    run_manager, run_title = create_run_no_site_context(
        module="agent",
        config_name=config_name,
        base_folder="runs",
    )

    # 標題註明僅為初始化：耗時訊息不應被誤讀成 server 的執行時間
    with run_workflow_context("Server", run_manager=run_manager):
        # --- 初始化 Agent -----
        config = AgentConfig.from_toml(config_name, **config_overrides)
        log_config(f"{config.__class__.__name__} Loaded from toml", config)
        agent = create_agent(config_name, **config_overrides)

        try:
            # --- 初始化 App & Server -----
            chat_app = ChatApp.create(
                agent=agent,
                run_manager=run_manager,
                allowed_origins=allowed_origins,
            )

            # --- 啟動 Server -----
            uvicorn_config = uvicorn.Config(
                chat_app.app, host=host, port=port, log_level="info"
            )
            server = ChatServer(uvicorn_config)

            # ---- 輸出完成訊息 -----
            log_session("Server Initialization Completed", style="cyan")

            # ---- 儲存設定 -----
            if run_config is not None:
                save_run_config_as_toml(run_config, run_manager.run_config_toml_path)
        except Exception as e:
            log_session("Server Initialization Failed", style="red")
            print_log(f"Error: {e}")
            agent.close()
            raise

    return server, chat_app


def serve_forever(run_config: ServeRunConfig) -> None:
    """啟動 Chat Server 並阻塞至中斷，結束時關閉 agent 資源。"""
    server, chat_app = run_app(
        config_name=run_config.config_name,
        run_config=run_config,
        allowed_origins=run_config.allowed_origins,
        host=run_config.host,
        port=run_config.port,
    )

    try:
        server.run()
    except KeyboardInterrupt:
        pass
    finally:
        chat_app.close()
        log_session("Server Stopped", style="cyan")
