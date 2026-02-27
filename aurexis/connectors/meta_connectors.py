"""
AUREXIS - Connectors: WhatsApp & Facebook
Webhooks pour recevoir des messages via les APIs officielles Meta.
Ces webhooks sont enregistrés dans server.py via FastAPI.
"""
from __future__ import annotations
import httpx
from core.orchestrator import Orchestrator
from core.auth import get_api_key


# ─── WhatsApp Business API ────────────────────────────────────────────────────

async def handle_whatsapp_webhook(data: dict) -> str:
    """
    Traite les webhooks entrants de WhatsApp Business API.
    Configure votre webhook sur: https://developers.facebook.com/apps
    """
    try:
        entry = data.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        
        if not messages:
            return "ok"
        
        msg = messages[0]
        from_number = msg.get("from", "")
        text = msg.get("text", {}).get("body", "")
        
        if not text:
            return "ok"
        
        response = await Orchestrator.get().process(text, session_id=f"wa_{from_number}")
        
        # Envoie la réponse via WhatsApp API
        await _send_whatsapp_message(from_number, response, value.get("metadata", {}).get("phone_number_id", ""))
        
    except Exception as e:
        print(f"[WhatsApp] Erreur: {e}")
    
    return "ok"


async def _send_whatsapp_message(to: str, text: str, phone_number_id: str):
    token = get_api_key("whatsapp")
    if not token:
        return
    
    url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
    
    async with httpx.AsyncClient() as client:
        await client.post(url, headers={"Authorization": f"Bearer {token}"}, json={
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text[:4096]},
        })


# ─── Facebook Messenger ───────────────────────────────────────────────────────

async def handle_facebook_webhook(data: dict) -> str:
    """
    Traite les webhooks Facebook Messenger.
    Configure votre webhook sur: https://developers.facebook.com/apps
    """
    try:
        for entry in data.get("entry", []):
            for messaging in entry.get("messaging", []):
                sender_id = messaging.get("sender", {}).get("id", "")
                message = messaging.get("message", {})
                text = message.get("text", "")
                
                if not text or not sender_id:
                    continue
                
                response = await Orchestrator.get().process(text, session_id=f"fb_{sender_id}")
                await _send_facebook_message(sender_id, response)
    
    except Exception as e:
        print(f"[Facebook] Erreur: {e}")
    
    return "ok"


async def _send_facebook_message(recipient_id: str, text: str):
    token = get_api_key("facebook")
    if not token:
        return
    
    url = "https://graph.facebook.com/v18.0/me/messages"
    
    async with httpx.AsyncClient() as client:
        await client.post(url, params={"access_token": token}, json={
            "recipient": {"id": recipient_id},
            "message": {"text": text[:2000]},
        })


def verify_webhook_token(token: str, verify_token: str) -> bool:
    """Vérifie le token de webhook Meta."""
    from config.settings import get_config
    expected = get_config("webhook_verify_token", "aurexis_webhook_secret")
    return token == expected
