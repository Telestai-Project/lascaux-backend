from fastapi import APIRouter

profile_router = APIRouter()

@profile_router.get("/heartbeat")
async def heartbeat():
    return {"status": "profile service is alive"}