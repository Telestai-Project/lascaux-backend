from fastapi import APIRouter

ipfs_router = APIRouter()

@ipfs_router.get("/heartbeat")
async def heartbeat():
    return {"status": "ipfs service is alive"}