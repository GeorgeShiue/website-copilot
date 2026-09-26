"""Agent 單模組流程（建置／問答，實驗與除錯用，不屬於 serve 階段的常駐服務）。

只讀取 prepare 階段 publish 到 data/ 的向量庫，不 import 爬蟲與 VLM 相關模組。
"""

import asyncio
import uuid

from website_copilot.agent.agent import create_agent
from website_copilot.config.agent_config import AgentConfig
from website_copilot.config.pipeline_config import AgentRunConfig
from website_copilot.storage.run_context import (
    create_run_no_site_context,
    run_workflow_context,
)
from website_copilot.utils.config_helper import (
    log_config,
    save_module_config_as_toml,
    save_run_config_as_toml,
)
from website_copilot.utils.log_helper import log_session, print_log


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
