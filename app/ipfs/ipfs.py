import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from fastapi import APIRouter

ipfs_router = APIRouter()

@ipfs_router.get("/heartbeat")
async def heartbeat():
    return {"status": "ipfs service is alive"}