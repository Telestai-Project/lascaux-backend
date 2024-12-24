# app/start_application.py
import logging
import subprocess
import sys
import time
from utils.docker_utils import start_cassandra_container, stop_cassandra_container

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_fastapi_server():
    """Starts the FastAPI server with Uvicorn."""
    try:
        logger.info("Starting FastAPI server...")
        subprocess.run(["uvicorn", "app.main:app", "--reload"], check=True)
    except subprocess.CalledProcessError as e:
        logger.error("Failed to start FastAPI server: %s", e)
        sys.exit(1)

def start_application():
    """Starts the Cassandra container and FastAPI server."""
    try:
        start_cassandra_container()

        logger.info("Ensuring Cassandra is fully initialized...")
        time.sleep(15)

        start_fastapi_server()
    except Exception as e:
        logger.error("Application failed to start: %s", e)
        stop_cassandra_container()
        sys.exit(1)

if __name__ == "__main__":
    try:
        start_application()
    except KeyboardInterrupt:
        logger.info("Application interrupted. Stopping services...")
        stop_cassandra_container()
        logger.info("Cleanup complete. Exiting.")
        sys.exit(0)
