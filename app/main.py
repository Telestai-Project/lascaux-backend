from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.v1.endpoints import auth
from app.api.v1.endpoints import user
from app.api.v1.endpoints import posts
from app.api.v1.endpoints import news
from app.api.v1.endpoints import votes
from app.core.database import init_db
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.auth_middleware import AuthMiddleware

app = FastAPI(
    title="Social Platform API",
    description="API for social platform with Cassandra database",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

app.add_middleware(AuthMiddleware)

init_db()

# Mount the img directory to serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routes
app.include_router(auth.auth_router, prefix="/api/v1", tags=["Authentication"])
app.include_router(user.user_router, prefix="/api/v1", tags=["Users"])
app.include_router(posts.post_router, prefix="/api/v1", tags=["Posts And Replies"])
app.include_router(news.news_router, prefix="/api/v1", tags=["News"])
app.include_router(votes.vote_router, prefix="/api/v1", tags=["Votes"])

@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}
