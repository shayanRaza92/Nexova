from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from .chat_engine import chat_engine
import os
import requests

router = APIRouter()

# Whapi Configuration
WHAPI_TOKEN = os.getenv("WHAPI_TOKEN", "")
WHAPI_API_URL = os.getenv("WHAPI_API_URL", "https://gate.whapi.cloud")


class ChatRequest(BaseModel):
    message: str


class WhatsAppChatRequest(BaseModel):
    phone: str
    message: str


@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Website chatbox endpoint (local simulator)"""
    response = await chat_engine.get_response(request.message)
    return {"response": response}


@router.post("/chat-whatsapp")
async def chat_whatsapp_endpoint(request: WhatsAppChatRequest):
    """
    Website chatbox → WhatsApp handoff.
    Customer enters their phone + query on the website,
    then the AI response is sent to their WhatsApp.
    """
    # 1. Get AI Response
    ai_response = await chat_engine.get_response(request.message)

    # 2. Format phone number (ensure it has no + or spaces)
    phone = request.phone.strip().replace("+", "").replace(" ", "").replace("-", "")

    # 3. Send to WhatsApp via Whapi
    send_result = send_whatsapp_message(phone, ai_response)

    if send_result["success"]:
        return {
            "status": "sent",
            "response": ai_response,
            "message": "Response sent to your WhatsApp!"
        }
    else:
        return {
            "status": "error",
            "response": ai_response,
            "message": f"AI responded but WhatsApp delivery failed: {send_result['error']}"
        }


def send_whatsapp_message(to_number: str, text: str) -> dict:
    """Send a text message via Whapi.cloud API"""
    if not WHAPI_TOKEN:
        print("Error: WHAPI_TOKEN is missing in .env")
        return {"success": False, "error": "Missing Whapi API token"}

    url = f"{WHAPI_API_URL}/messages/text"
    headers = {
        "Authorization": f"Bearer {WHAPI_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "to": to_number,
        "body": text
    }

    try:
        print(f"SENDING TO WHAPI: url={url} | to={to_number} | body_len={len(text)}")
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        print(f"Whapi Send Status: {response.status_code} | Full Response: {result}")

        if response.status_code in [200, 201]:
            return {"success": True, "data": result}
        else:
            # Whapi wraps errors as {"error": {"code": 400, "message": "..."}}
            error_msg = result.get("error", {}).get("message", "") or result.get("message", "") or str(result)
            return {"success": False, "error": error_msg}

    except Exception as e:
        print(f"Failed to send WhatsApp message: {e}")
        return {"success": False, "error": str(e)}


# ─── Webhook: Receive incoming WhatsApp messages via Whapi ───

@router.post("/webhook")
async def webhook_handler(request: Request, background_tasks: BackgroundTasks):
    """
    Receive incoming WhatsApp messages from Whapi webhook.
    When a customer replies on WhatsApp, the bot auto-responds.
    """
    body = await request.json()

    # DEBUG: Log everything we receive
    import json
    print("=" * 50)
    print("WEBHOOK RECEIVED:")
    print(json.dumps(body, indent=2, default=str))
    print("=" * 50)

    # Whapi can send messages in different formats
    messages = []

    # Format 1: { "messages": [...] }
    if "messages" in body:
        messages = body["messages"]
    # Format 2: Direct message object with "id", "type", etc.
    elif "id" in body and "type" in body:
        messages = [body]
    # Format 3: Array at root level
    elif isinstance(body, list):
        messages = body

    print(f"Found {len(messages)} messages to process")

    for msg in messages:
        from_me = msg.get("from_me", False)
        print(f"Message from_me={from_me}, type={msg.get('type')}")

        if not from_me:
            background_tasks.add_task(process_whapi_message, msg)

    return {"status": "ok"}


async def process_whapi_message(msg: dict):
    """Process a single incoming Whapi message"""
    try:
        # Extract sender and message text
        chat_id = msg.get("chat_id", "")  # e.g. "923001234567@s.whatsapp.net"
        sender = msg.get("from", "")
        text_body = ""

        # Handle text messages
        msg_type = msg.get("type", "")
        if msg_type == "text":
            text_obj = msg.get("text", {})
            if isinstance(text_obj, dict):
                text_body = text_obj.get("body", "")
            elif isinstance(text_obj, str):
                text_body = text_obj
        # Some Whapi payloads put text in "body" directly
        elif "body" in msg:
            text_body = msg.get("body", "")
        else:
            phone = chat_id.replace("@s.whatsapp.net", "")
            if phone:
                send_whatsapp_message(phone, "I can only process text messages for now. Please type your question!")
            return

        if not text_body:
            return

        # Extract phone number from chat_id
        phone = chat_id.replace("@s.whatsapp.net", "")
        if not phone:
            phone = sender

        print(f"Processing message from {phone}: {text_body}")

        # 1. Get AI Response
        ai_response = await chat_engine.get_response(text_body)
        print(f"AI Response: {ai_response[:100]}...")

        # 2. Send back via WhatsApp
        result = send_whatsapp_message(phone, ai_response)
        print(f"Send result: {result}")

    except Exception as e:
        print(f"Error processing Whapi webhook message: {e}")
        import traceback
        traceback.print_exc()

