import os
from typing import Iterator

from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse
from fastapi_clerk_auth import (
    ClerkConfig,
    ClerkHTTPBearer,
    HTTPAuthorizationCredentials,
)
from openai import OpenAI

app = FastAPI()

clerk_config = ClerkConfig(jwks_url=os.getenv("CLERK_JWKS_URL"))
clerk_guard = ClerkHTTPBearer(clerk_config)


@app.get("/")
def idea(creds: HTTPAuthorizationCredentials = Depends(clerk_guard)):
    # Clerk user id (available if you want to log/limit later)
    _user_id = creds.decoded.get("sub")

    client = OpenAI()  # uses OPENAI_API_KEY from env

    prompt = [
        {
            "role": "user",
            "content": (
                "Reply with a new business idea for AI Agents, formatted with "
                "headings, sub-headings and bullet points"
            ),
        }
    ]

    stream = client.chat.completions.create(
        model="gpt-5-nano",
        messages=prompt,
        stream=True,
    )

    def event_stream() -> Iterator[str]:
        # Optional: initial message so UI changes from "Connecting…" quickly
        yield "data: \n\n"

        for chunk in stream:
            delta = getattr(chunk.choices[0], "delta", None)
            text = getattr(delta, "content", None) if delta else None
            if not text:
                continue

            # Send exactly what we got. Client accumulates it.
            yield f"data: {text}\n\n"

    headers = {
        "Cache-Control": "no-cache, no-transform",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers=headers,
    )
