"""
Phase 2 — LINE Messaging API helpers.

STUB: real signature verification and message sending need a live LINE
Official Account's LINE_CHANNEL_SECRET and LINE_CHANNEL_ACCESS_TOKEN (from
the LINE Developers Console), plus a public HTTPS URL for the webhook —
none of which exist in this environment. Without credentials set, this
runs in "dev mode": signatures pass automatically and replies are printed
instead of sent, so the webhook logic itself is fully testable now.
"""
import base64
import hashlib
import hmac
import os
from typing import Optional
import httpx

LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")


def verify_signature(body: bytes, signature: Optional[str]) -> bool:
    if not LINE_CHANNEL_SECRET:
        return True  # dev mode — no real channel secret configured yet
    if not signature:
        return False
    mac = hmac.new(LINE_CHANNEL_SECRET.encode(), body, hashlib.sha256).digest()
    expected = base64.b64encode(mac).decode()
    return hmac.compare_digest(expected, signature)


def reply_message(reply_token: str, text: str) -> None:
    if not LINE_CHANNEL_ACCESS_TOKEN:
        print(f"[LINE dev mode] would reply: {text}")
        return
    httpx.post(
        "https://api.line.me/v2/bot/message/reply",
        headers={"Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}", "Content-Type": "application/json"},
        json={"replyToken": reply_token, "messages": [{"type": "text", "text": text}]},
        timeout=10,
    )
