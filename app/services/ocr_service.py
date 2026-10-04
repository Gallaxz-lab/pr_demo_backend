"""
Phase 3 — invoice OCR, via Claude's vision API.

This is now a real implementation, not a stub: it sends the invoice image
to Claude with an extraction prompt and parses structured fields back out.
It needs ANTHROPIC_API_KEY set (same key the AI Q&A service uses) — without
one, it falls back to the old "not connected" placeholder so the app still
runs with zero external credentials.

Accuracy depends on image quality like any OCR; this hasn't been tested
against real supplier invoices from this environment (no network access
here), so treat early extractions as a starting draft to verify, not as
ground truth — which is exactly why the workflow keeps a human review step
before anything posts to the books.
"""
import os
import re
import json
import httpx

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

_EXTRACTION_PROMPT = (
    "Extract these fields from this invoice image and respond with ONLY a "
    'JSON object, no other text: {"vendor": string, "invoice_number": string, '
    '"date": string, "amount": number}. "amount" is the final total including '
    "any tax, as a plain number with no currency symbol or thousands "
    "separators. If a field isn't visible, use an empty string (0 for amount)."
)


def extract_invoice_fields(image_base64: str, media_type: str = "image/jpeg") -> dict:
    if not ANTHROPIC_API_KEY:
        return {
            "vendor": "",
            "amount": 0.0,
            "raw_text": "OCR not connected — set ANTHROPIC_API_KEY to enable real extraction.",
        }

    resp = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-6",
            "max_tokens": 500,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_base64}},
                    {"type": "text", "text": _EXTRACTION_PROMPT},
                ],
            }],
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
    cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()

    try:
        fields = json.loads(cleaned)
    except json.JSONDecodeError:
        return {"vendor": "", "amount": 0.0, "raw_text": f"Could not parse model output: {text[:300]}"}

    return {
        "vendor": fields.get("vendor", ""),
        "amount": float(fields.get("amount") or 0),
        "raw_text": json.dumps(fields, ensure_ascii=False),
    }
