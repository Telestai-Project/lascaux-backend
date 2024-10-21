from fastapi import APIRouter

content_router = APIRouter()

@content_router.get("/heartbeat")
async def heartbeat():
    return {"status": "content service is alive"}
