"""Local token endpoint for the LiveKit browser client."""

import os
import secrets

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from livekit import api
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="TalkBot LiveKit API")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])


@app.post("/livekit/token")
async def livekit_token() -> dict[str, str]:
    key, secret, url = os.getenv("LIVEKIT_API_KEY"), os.getenv("LIVEKIT_API_SECRET"), os.getenv("LIVEKIT_URL")
    if not key or not secret or not url:
        raise HTTPException(500, "LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET are required")
    room_name = f"talkbot-{secrets.token_urlsafe(8)}"
    token = (api.AccessToken(key, secret).with_identity(f"user-{secrets.token_urlsafe(6)}").with_grants(api.VideoGrants(room_join=True, room=room_name)).with_room_config(api.RoomConfiguration(agents=[api.RoomAgentDispatch(agent_name="talkbot-livekit")])).to_jwt())
    return {"token": token, "url": url, "room": room_name}

