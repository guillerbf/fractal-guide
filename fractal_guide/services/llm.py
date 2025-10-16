from __future__ import annotations

import base64
import os
from typing import Iterable, Tuple, Sequence

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
        "type": "image_url",
        "image_url": {
            "url": f"data:image/jpeg;base64,{b64}",
        },
    }


def summarize_context(
    *,
    place_text: str,
    user_text: str,
    image_bytes: bytes | None,
    history: Sequence[tuple[str, str]] | None = None,
) -> Tuple[str, bool, list[str]]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return ("OpenAI API key not configured.", False, [])

    client = OpenAI(api_key=api_key)

    # Build prior textual messages for conversation continuity
    messages: list[dict] = [{"role": "system", "content": SYSTEM_RULES}]
    if history:
        for role, content_text in history[-8:]:
            messages.append({"role": role, "content": content_text})

    content: list[dict] = [
        {"type": "text", "text": f"Context: {place_text}\nUser: {user_text or 'Describe briefly what to notice here.'}"}
    ]
    img = _image_part(image_bytes)
    if img:
        content.append(img)

    messages.append({"role": "user", "content": content})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.6
    )

    text = response.choices[0].message.content or ""

    # Conversation mode, no disambiguation UI
    return (text.strip(), False, [])


