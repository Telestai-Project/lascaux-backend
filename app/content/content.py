import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from fastapi import APIRouter

content_router = APIRouter()

@content_router.get("/heartbeat")
async def heartbeat():
    return {"status": "content service is alive"}
