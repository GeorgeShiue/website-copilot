from types import FrameType

import uvicorn

from utils.log_helper import log_session


class ChatServer(uvicorn.Server):
    """收到退出訊號時先印一行 log，再交回 uvicorn 原生流程（避免關閉訊息被吃掉/延遲）。"""

    def handle_exit(self, sig: int, frame: FrameType | None) -> None:
        log_session("Server Stopping", style="yellow")
        super().handle_exit(sig, frame)
