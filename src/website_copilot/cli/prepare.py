"""`website-copilot prepare`：網站爬蟲 → augmenter（圖片摘要、文件）→ RAG 建置，結果 publish 到 data/。"""

from dataclasses import dataclass

from website_copilot.config.pipeline_config import PrepareRunConfig


@dataclass
class PrepareCLI:
    run: PrepareRunConfig


def main(cli: PrepareCLI) -> None:
    from website_copilot.pipelines.prepare import run_prepare
    from website_copilot.utils.log_helper import setup_logging

    setup_logging("info")
    run_prepare(cli.run)
