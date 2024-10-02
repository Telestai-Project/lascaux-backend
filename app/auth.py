from fastapi import APIRouter, Depends

auth_router = APIRouter()

@auth_router.get("/heartbeat")
async def heartbeat():
    return {"status": "auth service is alive"}

@auth_router.post("/login")
async def login():
    # Logic to handle wallet signature verification
    return {"message": "Logged in"}

@auth_router.post("/register")
async def register():
    # Logic to handle registration
    return {"message": "Registered"}
