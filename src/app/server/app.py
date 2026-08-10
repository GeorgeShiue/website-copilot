"""聊天服務層：FastAPI + SSE 串流 endpoint（M3）+ 嵌入表面（M4a）。

提供：
- create_app()：建立 FastAPI app（lifespan 建/關 agent、CORS、路由、static mount）
- POST /api/chat：SSE 串流問答（事件協定：token / done / error）
- GET /api/health：健康檢查
- GET /：redirect 至 /static/demo.html（嵌入示範）
- /static/：chat.html（iframe）、widget.js（script 嵌入）、demo.html
- run_server()：uvicorn 啟動入口（供 cli.py serve 分派）

SSE 事件協定（M3 定案，M4a 前端依此實作）：
- {"type": "token", "content": "..."}：逐 token 串流
- {"type": "done", "response": "...", "thread_id": "..."}：完成
  （引用內容已由 agent 寫入 response 內；sources 僅保留於落盤 result）
- {"type": "error", "message": "..."}：失敗

資源生命週期：agent 於 lifespan 啟動時建立一次、關閉時釋放。
create_rag_agent 每次會重建 vector store 隔離副本（M2.5），
不可 per-request 建立；對話隔離靠 thread_id（InMemorySaver 以 thread_id 為 session key）。
"""

import json
import logging
import time
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.agent.agent import (
    RAGAgent,
    astream_text,
    create_rag_agent,
    extract_sources_from_messages,
    save_conversation_results,
    thread_config,
)
from app.configs.agent_config import AgentConfig
from app.workflow.workflow_manager import RunManager
from utils.log_helper import setup_logging

logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    """POST /api/chat 請求體。"""

    query: str
    thread_id: str | None = None


def _sse(data: dict[str, Any]) -> str:
    """將事件 dict 序列化為 SSE 格式（data: JSON + 空行）。"""
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


async def _event_stream(
    agent: RAGAgent,
    query: str,
    thread_id: str,
) -> AsyncIterator[str]:
    """SSE 事件流：逐 token 串流，最後送 done（含回答全文）。

    引用內容由 agent 直接寫入 response（system prompt 已要求）；
    sources 仍擷取並保留於落盤 result，但不回傳前端。
    """
    chunks: list[str] = []
    try:
        config = thread_config(thread_id)
        async for text in astream_text(agent, query, config):
            chunks.append(text)
            yield _sse({"type": "token", "content": text})
        state = agent.graph.get_state(config)
        messages = state.values.get("messages", []) if state.values else []
        sources = extract_sources_from_messages(messages)
        # 落盤與 CLI 慣例一致：每輪覆寫 results.json（多輪累積留待 M5 依 thread_id 分檔）
        result = {
            "query": query,
            "response": "".join(chunks),
            "sources": sources,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        save_conversation_results(agent, [result])
        yield _sse(
            {
                "type": "done",
                "response": result["response"],
                "thread_id": thread_id,
            }
        )
    except Exception as exc:
        logger.exception("chat stream failed (thread_id=%s)", thread_id)
        yield _sse({"type": "error", "message": str(exc)})


def create_app(
    config_name: str = "default",
    agent: RAGAgent | None = None,
) -> FastAPI:
    """建立 FastAPI app。

    Args:
        config_name: AgentConfig 名稱（對應 configs/agent/{name}.toml）。
        agent: 可注入的 RAGAgent（測試替身）；None 時由 lifespan 建立。

    Returns:
        FastAPI：含 /api/chat（SSE）、/api/health 與 CORS。
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        if agent is None:
            # 與 workflow.run_agent 的呼叫模式對齊：明確指定 chats/ 落盤
            app.state.agent = create_rag_agent(
                config=AgentConfig.from_toml(config_name),
                run_manager=RunManager("agent", base_folder="chats"),
            )
        else:
            app.state.agent = agent
        yield
        app.state.agent.close()

    app = FastAPI(title="Website Copilot Chat", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        # demo 階段全開放；M5 收斂時再限縮至自有網站來源
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # M4a：嵌入表面 static 檔（chat.html / widget.js / demo.html）
    static_dir = Path(__file__).resolve().parent / "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    def get_agent(request: Request) -> RAGAgent:
        return request.app.state.agent

    @app.get("/")
    async def index() -> RedirectResponse:
        """入口：redirect 至嵌入示範頁。"""
        return RedirectResponse(url="/static/demo.html")

    @app.get("/api/health")
    async def health() -> dict[str, str]:
        """健康檢查。"""
        return {"status": "ok"}

    @app.post("/api/chat")
    async def chat(
        req: ChatRequest,
        agent: RAGAgent = Depends(get_agent),
    ) -> StreamingResponse:
        """SSE 串流問答。

        thread_id 為 None 時自動產生（auto-{uuid}）並於 done 事件回傳，
        前端下次帶回即可續接多輪對話。
        """
        if not req.query.strip():
            return StreamingResponse(
                [_sse({"type": "error", "message": "query must not be empty"})],
                media_type="text/event-stream",
            )
        thread_id = req.thread_id or f"auto-{uuid.uuid4().hex[:8]}"
        return StreamingResponse(
            _event_stream(agent, req.query, thread_id),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    return app


def run_server(
    config_name: str = "default",
    host: str = "127.0.0.1",
    port: int = 8000,
) -> None:
    """啟動聊天伺服器（cli.py serve 分派入口，blocking）。

    傳 app 物件給 uvicorn（而非 import string）：避免 reloader 子程序
    的 sys.path 不含 src/ 導致 ModuleNotFoundError。
    """
    setup_logging("debug")
    app = create_app(config_name=config_name)
    uvicorn.run(app, host=host, port=port)
