"""Serve 階段入口：啟動 Chat Server（阻塞至中斷）。

只讀取 prepare 階段（src/prepare.py）publish 到 data/ 的向量庫，不做任何建置；
站點尚未 publish 向量庫時不會出現在可用知識庫列表中。
"""

from dataclasses import dataclass

from website_copilot.config.pipeline_config import ServeRunConfig
from website_copilot.server.bootstrap import run_app
from website_copilot.utils.log_helper import log_session, setup_logging


@dataclass
class ServeCLI:
    run: ServeRunConfig


def main(run_config: ServeRunConfig) -> None:
    setup_logging("info")

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


if __name__ == "__main__":
    import tyro

    cli_arg = tyro.cli(ServeCLI)
    main(cli_arg.run)
