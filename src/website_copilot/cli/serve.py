"""`website-copilot serve`：啟動 Chat Server（阻塞至中斷），只讀取已 publish 的向量庫。"""

from dataclasses import dataclass

from website_copilot.config.pipeline_config import ServeRunConfig


@dataclass
class ServeCLI:
    run: ServeRunConfig


def main(cli: ServeCLI) -> None:
    from website_copilot.server.bootstrap import serve_forever
    from website_copilot.utils.log_helper import setup_logging

    setup_logging("info")
    serve_forever(cli.run)
