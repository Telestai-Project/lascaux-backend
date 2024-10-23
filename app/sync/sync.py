import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from fastapi import APIRouter

sync_router = APIRouter()

@sync_router.get("/heartbeat")
async def heartbeat():
    return {"status": "sync service is alive"}