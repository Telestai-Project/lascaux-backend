import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from fastapi import APIRouter

profile_router = APIRouter()

@profile_router.get("/heartbeat")
async def heartbeat():
    return {"status": "profile service is alive"}