from fastapi import FastAPI
from app.auth import auth_router
from app.content import content_router
from app.profile import profile_router
from app.moderation import moderation_router
from app.sync import sync_router
from app.ipfs import ipfs_router
from app.user import user_router
from app.post import post_router
from app.vote import vote_router
from app.comment import comment_router
from app.moderation_log import moderation_log_router
from app.database import init_db
from app.docker_utils import start_cassandra_container
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# Add CORS middleware to the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Start the Cassandra container
start_cassandra_container()

# Initialize the Cassandra database
init_db()

app.include_router(auth_router, prefix="/auth")
app.include_router(content_router, prefix="/content")
app.include_router(profile_router, prefix="/profile")
app.include_router(moderation_router, prefix="/moderate")
app.include_router(sync_router, prefix="/node")
app.include_router(user_router, prefix="/users")
app.include_router(post_router, prefix="/posts")
app.include_router(vote_router, prefix="/votes")
app.include_router(comment_router, prefix="/comments")
app.include_router(moderation_log_router, prefix="/moderation_logs")
app.include_router(ipfs_router, prefix="/ipfs")

@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}

# Ensure Cassandra is stopped when the application exits
# import atexit
# atexit.register(stop_cassandra_container)