import docker
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = docker.from_env()

# Define unique container and network names for the dev instance
CONTAINER_NAME = "cassandra_dev"
NETWORK_NAME = "cassandra_dev_network"
IMAGE_NAME = "cassandra:latest"  # Use a valid tag like "latest"
PORT_MAPPING = {"9042/tcp": 9052}  # Use unique port mappings

def start_cassandra_container():
    """Starts a Cassandra Docker container with a custom network."""
    try:
        create_network_if_not_exists(NETWORK_NAME)

        if is_container_running(CONTAINER_NAME):
            logger.info(f"{CONTAINER_NAME} container is already running.")
            return

        logger.info(f"Ensuring the Docker image '{IMAGE_NAME}' is available...")
        client.images.pull(IMAGE_NAME.split(":")[0], IMAGE_NAME.split(":")[1])

        logger.info(f"Starting {CONTAINER_NAME} container...")
        client.containers.run(
            IMAGE_NAME,
            name=CONTAINER_NAME,
            hostname=CONTAINER_NAME,
            network=NETWORK_NAME,
            ports=PORT_MAPPING,
            detach=True,
            remove=True,
        )

        logger.info(f"Waiting for {CONTAINER_NAME} to initialize...")
        time.sleep(15)

    except docker.errors.APIError as e:
        logger.error(f"Failed to start {CONTAINER_NAME} container: {e}")
        raise

def stop_cassandra_container():
    """Stops and removes the Cassandra Docker container and network."""
    try:
        if is_container_running(CONTAINER_NAME):
            logger.info(f"Stopping {CONTAINER_NAME} container...")
            container = client.containers.get(CONTAINER_NAME)
            container.stop()

        remove_network_if_exists(NETWORK_NAME)

    except docker.errors.APIError as e:
        logger.error(f"Error stopping {CONTAINER_NAME} container: {e}")
        raise

def create_network_if_not_exists(network_name):
    """Creates a Docker network if it does not exist."""
    try:
        if network_name not in [net.name for net in client.networks.list()]:
            logger.info(f"Creating Docker network '{network_name}'...")
            client.networks.create(network_name, driver="bridge")
    except docker.errors.APIError as e:
        logger.error(f"Failed to create network '{network_name}': {e}")
        raise

def remove_network_if_exists(network_name):
    """Removes a Docker network if it exists."""
    try:
        network = client.networks.list(names=[network_name])
        if network:
            logger.info(f"Removing Docker network '{network_name}'...")
            network[0].remove()
    except docker.errors.APIError as e:
        logger.warning(f"Failed to remove network '{network_name}': {e}")

def is_container_running(container_name):
    """Checks if a Docker container is running."""
    try:
        container = client.containers.get(container_name)
        return container.status == "running"
    except docker.errors.NotFound:
        return False
