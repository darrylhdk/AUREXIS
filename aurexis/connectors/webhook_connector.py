"""
AUREXIS - Generic Webhook Connector (WhatsApp / Facebook / Custom)
POST /webhook/whatsapp  →  { "message": "...", "from": "..." }
"""
from fastapi import APIRouter, Request
from core.auth import KeyVault

router = APIRouter()
_orchestrator = None


def init(orchestrator):
    global _orchestrator
    _orchestrator = orchestrator


@router.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    """WhatsApp Cloud API webhook"""
    data = await request.json()
    # Extract message from WhatsApp Cloud API format
    try:
        entry = data["entry"][0]["changes"][0]["value"]
        message_text = entry["messages"][0]["text"]["body"]
        from_number = entry["messages"][0]["from"]
    except (KeyError, IndexError):
        return {"status": "no_message"}

    if _orchestrator:
        response = await _orchestrator.process(message_text)
        # Here you'd call Meta's Send API to reply
        return {"status": "processed", "response": response, "to": from_number}
    return {"status": "orchestrator_not_ready"}


@router.post("/webhook/facebook")
async def facebook_webhook(request: Request):
    """Facebook Messenger webhook"""
    data = await request.json()
    try:
        entry = data["entry"][0]["messaging"][0]
        message_text = entry["message"]["text"]
        sender_id = entry["sender"]["id"]
    except (KeyError, IndexError):
        return {"status": "no_message"}

    if _orchestrator:
        response = await _orchestrator.process(message_text)
        return {"status": "processed", "response": response, "to": sender_id}
    return {"status": "orchestrator_not_ready"}


@router.get("/webhook/facebook")
async def facebook_verify(request: Request):
    """Facebook webhook verification"""
    params = dict(request.query_params)
    verify_token = KeyVault().get_key("facebook_verify_token")
    if params.get("hub.verify_token") == verify_token:
        return int(params.get("hub.challenge", 0))
    return {"status": "invalid_token"}
