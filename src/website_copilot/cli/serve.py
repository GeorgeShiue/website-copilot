"""`website-copilot serve`：啟動 Chat Server（阻塞至中斷），只讀取已 publish 的向量庫。"""

from dataclasses import dataclass

from website_copilot.config.pipeline_config import ServeRunConfig


@dataclass
class ServeCLI:
    run: ServeRunConfig


def main(cli: ServeCLI) -> None:
    # 延遲載入：pipeline 會帶入 agent／RAG 等重依賴，--help 與參數解析不需要它們
    from website_copilot.pipelines.serve import run_serve
    from website_copilot.utils.log_helper import setup_logging

    setup_logging("info")
    run_serve(cli.run)
