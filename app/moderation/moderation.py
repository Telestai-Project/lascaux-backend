from fastapi import APIRouter

moderation_router = APIRouter()

@moderation_router.get("/heartbeat")
async def heartbeat():
    return {"status": "moderation service is alive"}