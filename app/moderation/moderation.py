import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from fastapi import APIRouter

moderation_router = APIRouter()

@moderation_router.get("/heartbeat")
async def heartbeat():
    return {"status": "moderation service is alive"}