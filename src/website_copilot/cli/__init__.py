"""`website-copilot` 單一 CLI：prepare / serve / run <module> / exp。

各子命令模組只在頂層 import 參數用的 dataclass，執行邏輯在 main() 內延遲 import，
避免例如 serve 間接載入爬蟲相關依賴。
"""

from typing import Annotated

import tyro

from website_copilot.cli.exp import ExpCLI
from website_copilot.cli.prepare import PrepareCLI
from website_copilot.cli.run import RunCLI
from website_copilot.cli.serve import ServeCLI

Command = (
    Annotated[PrepareCLI, tyro.conf.subcommand("prepare")]
    | Annotated[ServeCLI, tyro.conf.subcommand("serve")]
    | Annotated[RunCLI, tyro.conf.subcommand("run")]
    | Annotated[ExpCLI, tyro.conf.subcommand("exp")]
)


def main(args: list[str] | None = None) -> None:
    command = tyro.cli(
        Command,  # type: ignore[arg-type]
        args=args,
        prog="website-copilot",
        config=(tyro.conf.OmitSubcommandPrefixes,),
    )
    if isinstance(command, PrepareCLI):
        from website_copilot.cli import prepare

        prepare.main(command)
    elif isinstance(command, ServeCLI):
        from website_copilot.cli import serve

        serve.main(command)
    elif isinstance(command, RunCLI):
        from website_copilot.cli import run

        run.main(command)
    elif isinstance(command, ExpCLI):
        from website_copilot.cli import exp

        exp.main(command)
