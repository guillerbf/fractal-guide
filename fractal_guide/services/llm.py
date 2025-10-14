from __future__ import annotations

import base64
import os
from typing import Iterable, Tuple

from openai import OpenAI


SYSTEM_RULES = (
    "You are a local guide. Use only location context + user photo/text. If unsure, ask. "
    "Ask one clarifier when ambiguity is high. Prefer ranges and uncertainty markers. Avoid absolutes."
)


def _image_part(image_bytes: bytes | None):
    if not image_bytes:
        return None
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    return {
        "type": "input_image",
        "image_data": {
            "data": b64,
            "mime_type": "image/jpeg",
        },
    }


def summarize_context(
    *,
    place_text: str,
    user_text: str,
    image_bytes: bytes | None,
) -> Tuple[str, bool, list[str]]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return ("OpenAI API key not configured.", False, [])

    client = OpenAI(api_key=api_key)

    content: list[dict] = [
        {"type": "text", "text": f"Context: {place_text}\nUser: {user_text or 'Describe briefly what to notice here.'}"}
    ]
    img = _image_part(image_bytes)
    if img:
        content.append(img)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_RULES},
            {"role": "user", "content": content},
        ],
        temperature=0.6,
        max_tokens=400,
    )

    text = response.choices[0].message.content or ""

    # Heuristic for clarifier need; real logic can be improved later
    need_clarifier = "clarify" in text.lower() or "which one" in text.lower()
    options: list[str] = []
    if need_clarifier:
        options = ["Option A", "Option B"]

    return (text.strip(), need_clarifier, options)


