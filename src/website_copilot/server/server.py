"""ChatServer：uvicorn.Server 子類，由 pipelines.serve.run_server_build 建立。"""

import socket
from types import FrameType

import uvicorn

from website_copilot.server.app import ChatApp
from website_copilot.utils.log_helper import log_session


class ChatServer(uvicorn.Server):
    """持有 ChatApp 的 uvicorn Server：退出時自動關閉 ChatApp（釋放 agent 資源）。

    收到退出訊號時先印一行 log，再交回 uvicorn 原生流程（避免關閉訊息被吃掉/延遲）。
    """

    def __init__(self, config: uvicorn.Config, chat_app: ChatApp) -> None:
        super().__init__(config)
        self.chat_app = chat_app

    def handle_exit(self, sig: int, frame: FrameType | None) -> None:
        log_session("Server Stopping", style="yellow")
        super().handle_exit(sig, frame)

    async def serve(self, sockets: list[socket.socket] | None = None) -> None:
        """執行 uvicorn serve；不論正常結束、中斷或例外，結束時皆關閉 ChatApp。

        run() 內部即 asyncio.run(self.serve())，故阻塞與 asyncio 兩種啟動方式皆涵蓋。
        """
        try:
            await super().serve(sockets)
        finally:
            self.chat_app.close()
            log_session("Server Stopped", style="cyan")
