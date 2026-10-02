"""Serve 階段：建構 Agent（run_agent_build）、建立 Chat Server（run_server_build）並管理其生命週期（serve）。

run_agent_build 與 run_server_build 各自持有獨立的 run context（RunManager），
由 serve() 依序呼叫並串接：agent 建構後注入 server。
只讀取 prepare 階段 publish 到 data/ 的向量庫，不 import 爬蟲與 VLM 相關模組。
"""

from typing import Any

import uvicorn

from website_copilot.agent.agent import Agent, create_agent
from website_copilot.config.agent_config import AgentConfig
from website_copilot.config.pipeline_config import AgentRunConfig, ServeRunConfig
from website_copilot.server.app import ChatApp
from website_copilot.server.server import ChatServer
from website_copilot.storage.run_context import (
    create_run_no_site_context,
    run_workflow_context,
)
from website_copilot.utils.config_helper import (
    log_config,
    save_module_config,
    save_run_config,
)
from website_copilot.utils.log_helper import log_session, print_log


def run_agent_build(
    run_config: AgentRunConfig | ServeRunConfig,
    overrides: dict[str, Any] | None = None,
) -> Agent:
    """建構 Agent 並落盤設定，回傳 agent（資源由呼叫端負責 close()）。

    一律建立自己的 run context：runs/<ts>/agent_build/<config>/。

    Args:
        run_config: `run agent` 的 AgentRunConfig 或 `serve` 的 ServeRunConfig；
            config_name 對應 configs/agent/{name}.yml。
        overrides: AgentConfig 的巢狀覆寫值（llm_name / system_prompt）。
    """
    config = AgentConfig.from_yaml(run_config.config_name, overrides)

    run_manager, run_title = create_run_no_site_context(
        module="agent_build",
        config_name=run_config.config_name,
    )

    with run_workflow_context(run_title, run_manager=run_manager):
        # ---- 初始化 Agent -----
        log_config(f"{config.__class__.__name__} Loaded from yaml", config)
        agent = create_agent(config)

        try:
            # ----- 輸出完成訊息 -----
            log_session("Agent Build Completed", style="cyan")

            # ---- 儲存設定 -----
            save_module_config(config, run_manager.module_config_path)
            save_run_config(run_config, run_manager.run_config_path)
        except Exception:
            agent.close()
            raise

    return agent


def run_server_build(agent: Agent, run_config: ServeRunConfig) -> ChatServer:
    """以注入的 Agent 建立 ChatApp（FastAPI app）並回傳 ChatServer（非阻塞）。

    建立自己的 run context：runs/<ts>/server/<config>/，對話結果落盤於此。
    呼叫端可透過 server.run() 阻塞，或以 asyncio 啟動後透過 server.should_exit=True 關閉。
    成功回傳後 agent 資源生命週期由 ChatServer 承接：serve 結束時自動呼叫 chat_app.close()；
    ChatApp 可經 server.chat_app 取得。失敗時不關閉 agent，由建立 agent 的呼叫端負責。

    Args:
        agent: 已建構的 Agent（通常來自 run_agent_build()）。
        run_config: ServeRunConfig；host／port 為監聽位址與連接埠，allowed_origins 為
            CORS 允許來源（None 時全開放），並落盤為 run_config.yml。

    Returns:
        ChatServer：交由呼叫端 run() 或 await serve()，結束時自動關閉 agent。
    """
    run_manager, _ = create_run_no_site_context(
        module="server",
        config_name=agent.config.config_name,
    )

    # 標題註明僅為初始化：耗時訊息不應被誤讀成 server 的執行時間
    with run_workflow_context("Server", run_manager=run_manager):
        try:
            # --- 初始化 App & Server -----
            chat_app = ChatApp.create(
                agent=agent,
                run_manager=run_manager,
                allowed_origins=run_config.allowed_origins,
            )

            # --- 啟動 Server -----
            uvicorn_config = uvicorn.Config(
                chat_app.app,
                host=run_config.host,
                port=run_config.port,
                log_level="info",
            )
            server = ChatServer(uvicorn_config, chat_app)

            # ---- 輸出完成訊息 -----
            log_session("Server Initialization Completed", style="cyan")

            # ---- 儲存設定 -----
            save_run_config(run_config, run_manager.run_config_path)
        except Exception as e:
            log_session("Server Initialization Failed", style="red")
            print_log(f"Error: {e}")
            raise

    return server


def serve(run_config: ServeRunConfig) -> None:
    """建構 Agent 後啟動 Chat Server 並阻塞至中斷（agent 資源由 ChatServer 結束時關閉）。"""
    agent = run_agent_build(run_config)

    try:
        server = run_server_build(agent, run_config)
    except Exception:
        agent.close()
        raise

    try:
        server.run()
    except KeyboardInterrupt:
        pass
