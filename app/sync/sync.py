from fastapi import APIRouter

sync_router = APIRouter()

@sync_router.get("/heartbeat")
async def heartbeat():
    return {"status": "sync service is alive"}