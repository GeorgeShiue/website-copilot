"""聊天服務層：FastAPI + SSE 串流 endpoint（M3）+ 嵌入表面（M4a）。

提供：
- ChatApp：聊天服務應用（create() 工廠方法、close() 資源釋放、context manager）
- _build_fastapi_app()：建立 FastAPI app（lifespan 綁定 agent / run_manager、CORS、路由、static mount）
- POST /api/chat：SSE 串流問答（事件協定：token / done / error）
- GET /api/health：健康檢查
- GET /：redirect 至 /static/demo.html（嵌入示範）
- /static/：chat.html（iframe）、widget.js（script 嵌入）、demo.html

SSE 事件協定（M3 定案，M4a 前端依此實作）：
- {"type": "token", "content": "..."}：逐 token 串流
- {"type": "done", "response": "...", "thread_id": "..."}：完成
  （引用內容已由 agent 寫入 response 內；sources 僅保留於落盤 result）
- {"type": "error", "message": "..."}：失敗

資源生命週期：agent 與 run_manager 皆由呼叫端建立後透過 ChatApp.create() 注入，
lifespan 啟動時綁定至 app.state；ChatApp.close() 僅釋放 agent（run_manager 無需釋放資源）。
"""

import json
import logging
import time
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.agent.agent import Agent
from app.workflow.run_manager import RunManager
from utils.langchain_helper import extract_sources_from_messages, thread_config

logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    """POST /api/chat 請求體。"""

    query: str
    thread_id: str | None = None
    page_url: str | None = None


DOMAIN_SITE_MAP: dict[str, str] = {
    "nculab.csie.ncu.edu.tw": "nculab",
    "csie.ncu.edu.tw": "ncucsie",
}


def resolve_site_id(page_url: str | None) -> str | None:
    """從 hostname 解析 site_id。

    支援精確匹配與子域名 suffix 匹配。
    """
    if not page_url:
        return None
    hostname = page_url.strip().lower()
    if hostname in DOMAIN_SITE_MAP:
        return DOMAIN_SITE_MAP[hostname]
    for domain, site_id in DOMAIN_SITE_MAP.items():
        if hostname.endswith("." + domain):
            return site_id
    return None


def _enrich_query_with_site_context(query: str, site_id: str | None) -> str:
    """將 site_id 前綴至 query，供 LLM 感知當前站點。"""
    if not site_id:
        return query
    return f"[使用者瀏覽 {site_id} 網站] {query}"


def _sse(data: dict[str, Any]) -> str:
    """將事件 dict 序列化為 SSE 格式（data: JSON + 空行）。"""
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


async def _event_stream(
    agent: Agent,
    run_manager: RunManager,
    query: str,
    thread_id: str,
    site_id: str | None = None,
) -> AsyncIterator[str]:
    """SSE 事件流：逐 token 串流，最後送 done（含回答全文）。

    引用內容由 agent 直接寫入 response（system prompt 已要求）；
    sources 仍擷取並保留於落盤 result，但不回傳前端。
    """
    chunks: list[str] = []
    enriched_query = _enrich_query_with_site_context(query, site_id)
    try:
        config = thread_config(thread_id)
        async for text in agent.astream_text(enriched_query, config):
            chunks.append(text)
            yield _sse({"type": "token", "content": text})
        state = agent.graph.get_state(config)
        messages = state.values.get("messages", []) if state.values else []
        sources = extract_sources_from_messages(messages)
        # 落盤：以 thread_id 分檔保留完整多輪對話歷史
        result = {
            "query": query,
            "response": "".join(chunks),
            "sources": sources,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        run_manager.save_agent_results_as_json(
            thread_id=thread_id,
            results=[result],
            agent_config=agent.config,
        )
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


class ChatApp:
    """統一管理 Agent + FastAPI 的生命週期。

    Attributes:
        agent: 注入的 Agent 實例。
        run_manager: 注入的 RunManager 實例（落盤由本物件負責，無需釋放）。
        app: FastAPI 應用程式（/api/chat、/api/health、CORS、static mount）。
    """

    def __init__(self, agent: Agent, run_manager: RunManager, app: FastAPI) -> None:
        self.agent = agent
        self.run_manager = run_manager
        self.app = app

    @classmethod
    def create(
        cls,
        agent: Agent,
        run_manager: RunManager,
        allowed_origins: list[str] | None = None,
    ) -> "ChatApp":
        """工廠方法：建立 FastAPI app 並綁定 agent 與 run_manager。"""
        fastapi_app = _build_fastapi_app(agent, run_manager, allowed_origins)
        return cls(agent=agent, run_manager=run_manager, app=fastapi_app)

    def close(self) -> None:
        """釋放 Agent 資源（run_manager 無需釋放）。"""
        self.agent.close()

    def __enter__(self) -> "ChatApp":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


def _build_fastapi_app(
    agent: Agent,
    run_manager: RunManager,
    allowed_origins: list[str] | None = None,
) -> FastAPI:
    """建立 FastAPI 應用程式，注入 Agent 與 RunManager 到 lifespan（內部函式）。

    一般由 ChatApp.create() 呼叫；直接使用時呼叫端需自行管理資源生命週期。

    Args:
        agent: Agent 實例（必填）。
        run_manager: RunManager 實例（必填，供 /api/chat 落盤）。
        allowed_origins: CORS 允許的來源列表；None 時預設 ["*"]（demo 全開放）。

    Returns:
        FastAPI：含 /api/chat（SSE）、/api/health 與 CORS。
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.agent = agent
        app.state.run_manager = run_manager
        yield

    app = FastAPI(title="Website Copilot Chat", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        # 預設 demo 全開放；自有網站部署時可限縮（如 ["https://lab.example.edu.tw"]）
        allow_origins=allowed_origins if allowed_origins is not None else ["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # M4a：嵌入表面 static 檔（chat.html / widget.js / demo.html）
    static_dir = Path(__file__).resolve().parent / "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    def get_agent(request: Request) -> Agent:
        return request.app.state.agent

    def get_run_manager(request: Request) -> RunManager:
        return request.app.state.run_manager

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
        agent: Agent = Depends(get_agent),
        run_manager: RunManager = Depends(get_run_manager),
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
        site_id = resolve_site_id(req.page_url)
        return StreamingResponse(
            _event_stream(agent, run_manager, req.query, thread_id, site_id=site_id),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    return app
