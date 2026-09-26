"""Serve 階段 workflow：Agent 建置／問答與 Chat Server 啟動。

只讀取 prepare 階段 publish 到 data/ 的向量庫，不 import 爬蟲與 VLM 相關模組。
"""

import asyncio
import uuid

import uvicorn

from app.agent.agent import create_agent
from app.configs.agent_config import AgentConfig
from app.configs.workflow_config import AgentRunConfig, ServeRunConfig
from app.server.app import ChatApp
from app.server.server import ChatServer
from app.workflow.workflow_helper import (
    create_run_no_site_context,
    run_workflow_context,
)
from utils.config_helper import (
    log_config,
    save_module_config_as_toml,
    save_run_config_as_toml,
)
from utils.log_helper import log_session, print_log


def run_agent_build(
    config_name: str = "default",
    run_config: AgentRunConfig | None = None,
    **config_overrides,
) -> None:
    """建構 Agent 並落盤結果。完整包含建立 agent 流程。"""
    config = AgentConfig.from_toml(config_name, **config_overrides)
    run_manager, run_title = create_run_no_site_context(
        module="agent_build",
        config_name=config_name,
    )

    with run_workflow_context(run_title, run_manager=run_manager):
        # ---- 初始化 Agent -----
        log_config(f"{config.__class__.__name__} Loaded from toml", config)
        agent = create_agent(config_name, **config_overrides)

        # ----- 輸出完成訊息 -----
        log_session("Agent Build Completed", style="cyan")

        # ---- 儲存設定 -----
        save_module_config_as_toml(config, run_manager.module_config_toml_path)
        if run_config is not None:
            save_run_config_as_toml(run_config, run_manager.run_config_toml_path)

    agent.close()


def run_agent_query(
    query: str,
    config_name: str = "default",
    thread_id: str | None = None,
    stream: bool = False,
    run_config: AgentRunConfig | None = None,
    **config_overrides,
) -> None:
    """執行 Agent 問答工作流程（建立 run context → 建構 agent → 問答 → 落盤 → 關閉）。

    流程：問答 → 顯示回答與來源 → 落盤 runs/ → 寫 run_config.toml → 關閉 agent。
    agent 的建立與 Tool 生命週期皆在本函式內完成（呼叫端不需持有 agent）。

    Args:
        config_name: AgentConfig 名稱（對應 configs/agent/{name}.toml）。
        query: 使用者問題。
        thread_id: session 識別；None 時自動產生 auto-{uuid}。
        stream: 是否逐 token 串流輸出。
        run_config: RunConfig 實例（可選，用於落盤 run config toml）。
        **config_overrides: AgentConfig 覆寫值（llm_name / system_prompt）。
    """

    run_manager, run_title = create_run_no_site_context(
        module="agent",
        config_name=config_name,
        base_folder="runs",
    )

    with run_workflow_context(run_title, run_manager=run_manager):
        # ---- 初始化 Agent -----
        config = AgentConfig.from_toml(config_name, **config_overrides)
        log_config(f"{config.__class__.__name__} Loaded from toml", config)
        agent = create_agent(config_name, **config_overrides)

        try:
            # ---- Agent 問答 -----
            log_session("Agent Query and Response", style="cyan")
            print_log(f"Query: {query}")
            if stream:
                result = asyncio.run(
                    agent.astream_result(
                        query,
                        thread_id,
                        on_token=lambda token: print(token, end="", flush=True),
                    )
                )
                print()  # 串流 token 結束後換行
            else:
                result = agent.ask(query, thread_id)
            print_log(f"Response: {result['response']}")

            log_session("Sources", style="cyan")
            for i, url in enumerate(result["sources"], 1):
                print_log(f"{i}. {url}")

            # ---- 輸出完成訊息 -----
            log_session("Agent Query Completed", style="cyan")

            # ---- 儲存設定 -----
            save_module_config_as_toml(config, run_manager.module_config_toml_path)
            if run_config is not None:
                save_run_config_as_toml(run_config, run_manager.run_config_toml_path)

            # ---- 儲存結果 -----
            if thread_id is None:
                thread_id = f"auto-{uuid.uuid4().hex[:8]}"
            run_manager.save_agent_results_as_json(
                thread_id=thread_id,
                results=[result],
                agent_config=agent.config,
            )
        except Exception as e:
            log_session("Agent Query Failed", style="red")
            print_log(f"Error: {e}")
            agent.close()
            raise
        finally:
            agent.close()


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
