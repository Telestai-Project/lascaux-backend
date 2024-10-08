import os
import socket
import subprocess
import requests
import sqlite3
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
from app.database import DATABASE_PATH

app = FastAPI()

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

@app.get("/nodeinfo")
async def nodeinfo():
    # Check if the node is up-to-date
    try:
        local_commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode('utf-8')
        remote_commit = subprocess.check_output(["git", "ls-remote", "origin", "HEAD"]).split()[0].decode('utf-8')
        up_to_date = local_commit == remote_commit
    except Exception as e:
        up_to_date = False

    # Ping to the internet
    try:
        ping_response = subprocess.run(["ping", "-c", "1", "8.8.8.8"], capture_output=True)
        ping_status = ping_response.returncode == 0
    except Exception as e:
        ping_status = False

    # Private IP address
    private_ip = socket.gethostbyname(socket.gethostname())

    # Public IP address
    try:
        public_ip = requests.get('https://api.ipify.org').text
    except Exception as e:
        public_ip = "Unavailable"

    # Number of content in SQLite DB
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM content_table")
        content_count = cursor.fetchone()[0]
        conn.close()
    except Exception as e:
        content_count = "Unavailable"


    # Dirty or clean status
    try:
        git_status = subprocess.check_output(["git", "status", "--porcelain"]).strip()
        dirty_status = bool(git_status)
    except Exception as e:
        dirty_status = "Unknown"

    # Current git commit
    try:
        current_commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode('utf-8')
    except Exception as e:
        current_commit = "Unavailable"

    return {
        "up_to_date": up_to_date,
        "ping_status": ping_status,
        "private_ip": private_ip,
        "public_ip": public_ip,
        "content_count": content_count,
        "dirty_status": dirty_status,
        "current_commit": current_commit
    }

@app.get("/heartbeat")
async def heartbeat():
    return {"status": "Lascaux API is UP"}