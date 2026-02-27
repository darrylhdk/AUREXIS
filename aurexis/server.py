"""
AUREXIS - FastAPI Server + WebSocket
"""
import json, asyncio
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


def create_app(orchestrator) -> FastAPI:
    app = FastAPI(title="AUREXIS Agent OS", version="1.0.0")
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

    templates_path = Path("webui/templates")
    templates = Jinja2Templates(directory=str(templates_path))
    static_path = Path("webui/static")
    if static_path.exists():
        app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

    # ── WebSocket Chat ─────────────────────────────────────
    @app.websocket("/ws/chat")
    async def chat_ws(websocket: WebSocket):
        await websocket.accept()
        try:
            while True:
                data = await websocket.receive_json()
                msg = data.get("message", "")
                stream = data.get("stream", True)
                if stream:
                    async for chunk in orchestrator.process_stream(msg):
                        await websocket.send_json({"type": "chunk", "content": chunk})
                    await websocket.send_json({"type": "done"})
                else:
                    response = await orchestrator.process(msg)
                    await websocket.send_json({"type": "response", "content": response})
        except WebSocketDisconnect:
            pass

    # ── REST API ──────────────────────────────────────────
    class ChatRequest(BaseModel):
        message: str

    class LLMSwitchRequest(BaseModel):
        llm_name: str
        api_key: str = ""

    class ModeSwitchRequest(BaseModel):
        mode: str

    class MCPConnectRequest(BaseModel):
        url: str
        name: str = ""

    class APIKeyRequest(BaseModel):
        provider: str
        key: str

    @app.post("/api/chat")
    async def chat(req: ChatRequest):
        response = await orchestrator.process(req.message)
        return {"response": response, "llm": orchestrator.active_llm, "mode": orchestrator.active_mode}

    @app.get("/api/status")
    async def status():
        return {
            "llm": orchestrator.active_llm,
            "mode": orchestrator.active_mode,
            "mcp_tools": orchestrator.mcp_registry.count(),
            "connectors": orchestrator.get_connector_status()
        }

    @app.get("/api/llms")
    async def list_llms():
        from llm.registry import LLMRegistry
        return LLMRegistry().list_llms()

    @app.post("/api/llm/switch")
    async def switch_llm(req: LLMSwitchRequest):
        if req.api_key:
            from core.auth import KeyVault
            KeyVault().set_key(req.llm_name, req.api_key)
        await orchestrator.set_llm(req.llm_name)
        return {"success": True, "active_llm": orchestrator.active_llm}

    @app.post("/api/mode/switch")
    async def switch_mode(req: ModeSwitchRequest):
        await orchestrator.set_mode(req.mode)
        return {"success": True, "active_mode": orchestrator.active_mode}

    @app.get("/api/mcp/tools")
    async def list_tools():
        return orchestrator.mcp_registry.get_all_tools()

    @app.post("/api/mcp/connect")
    async def connect_mcp(req: MCPConnectRequest):
        result = await orchestrator.mcp_client.connect(req.url, req.name)
        return result

    @app.post("/api/keys")
    async def set_key(req: APIKeyRequest):
        from core.auth import KeyVault
        KeyVault().set_key(req.provider, req.key)
        return {"success": True}

    @app.get("/api/prompts/{name}")
    async def get_prompt(name: str):
        path = Path(f"prompts/{name}.txt")
        if not path.exists():
            raise HTTPException(404, "Prompt not found")
        return {"name": name, "content": path.read_text()}

    @app.put("/api/prompts/{name}")
    async def update_prompt(name: str, body: dict):
        path = Path(f"prompts/{name}.txt")
        path.write_text(body.get("content", ""))
        return {"success": True}

    # ── Web UI ────────────────────────────────────────────
    @app.get("/", response_class=HTMLResponse)
    async def root(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

    # Include webhook connectors
    from connectors.webhook_connector import router as webhook_router, init as webhook_init
    webhook_init(orchestrator)
    app.include_router(webhook_router)

    return app
