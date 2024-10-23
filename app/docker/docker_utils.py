import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import subprocess
import time

def start_cassandra_container():
    """
    Starts a Cassandra container.

    Raises:
        subprocess.CalledProcessError: If Docker command fails.
    """
    try:
        # Pull Cassandra image
        subprocess.run(["docker", "pull", "cassandra:latest"], check=True)

        # Create Docker network
        create_network()

        # Start Cassandra container
        start_container()

        # Wait for Cassandra initialization
        print("Waiting for Cassandra to start...")
        time.sleep(15)

    except subprocess.CalledProcessError as e:
        print(f"Error starting Cassandra container: {e}")
        raise

def stop_cassandra_container():
    """
    Stops a Cassandra container.

    Raises:
        Exception: If Docker command fails.
    """
    try:
        # Check if Cassandra container exists
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=cassandra", "--format", "{{.Names}}"],
            capture_output=True, text=True, check=False
        )
        if "cassandra" in result.stdout:
            stop_container()
        else:
            print("Cassandra container is not running.")

        # Check if Cassandra network exists
        result = subprocess.run(
            ["docker", "network", "ls", "--filter", "name=cassandra", "--format", "{{.Name}}"],
            capture_output=True, text=True, check=False
        )
        if "cassandra" in result.stdout:
            remove_network(force=True)
        else:
            print("Cassandra network does not exist.")

    except Exception as e:
        print(f"Error stopping Cassandra container: {str(e)}")
        raise

def create_network():
    """
    Creates a Docker network for Cassandra.
    """
    result = subprocess.run(
        ["docker", "network", "ls", "--filter", "name=cassandra", "--format", "{{.Name}}"],
        capture_output=True, text=True, check=False
    )
    if "cassandra" not in result.stdout:
        subprocess.run(["docker", "network", "create", "cassandra"], check=True)

def start_container():
    """
    Starts a Cassandra container instance.
    """
    result = subprocess.run(
        ["docker", "ps", "--filter", "name=cassandra", "--format", "{{.Names}}"],
        capture_output=True, text=True, check=False
    )
    if "cassandra" in result.stdout:
        print("Cassandra container is already running.")
        return
    subprocess.run([
        "docker", "run", "--rm", "-d", "--name", "cassandra",
        "--hostname", "cassandra", "--network", "cassandra",
        "-p", "9042:9042", "cassandra:latest"
    ], check=True)


def stop_container():
    """
    Stops and removes a Cassandra container instance.
    """
    def run_docker_command(command):
        return subprocess.run(
            command,
            shell=True,
            check=False,
            capture_output=True,
            text=True
        )
        
    # Function to check if container exists
    def container_exists(container_name):
        result = run_docker_command(f"docker ps -a --filter name={container_name} --format {{.Names}}")
        return container_name in result.stdout

    # Initial check
    if not container_exists("cassandra"):
        print("Cassandra container does not exist or has been removed.")
        return

    print("Attempting to stop Cassandra container...")
    
    # Try to stop the container
    stop_result = run_docker_command("docker stop cassandra")
    if stop_result.returncode == 0:
        print("Cassandra container stopped successfully.")
    elif "already in progress" in stop_result.stderr.lower():
        print("Cassandra container is already being stopped or has been stopped.")
    else:
        print(f"Failed to stop Cassandra container: {stop_result.stderr.strip()}")

    # Wait for the container to actually stop (give it some time)
    max_attempts = 5
    attempt = 0
    while container_exists("cassandra") and attempt < max_attempts:
        print("Waiting for Cassandra container to stop...", end='\r')
        time.sleep(2)  
        attempt += 1

    if not container_exists("cassandra"):
        print("\nCassandra container has stopped.")
    else:
        print("\nTimeout waiting for Cassandra container to stop.")

    # Attempt to remove the container
    print("Attempting to remove Cassandra container...")
    remove_result = run_docker_command("docker rm cassandra")
    if remove_result.returncode == 0:
        print("Cassandra container removed successfully.")
    elif "No such container" in remove_result.stderr:
        print("Cassandra container has already been removed.")
    else:
        print(f"Failed to remove Cassandra container: {remove_result.stderr.strip()}")

def remove_network(force=False):
    """
    Removes a Cassandra Docker network. If 'force' is True, 
    disconnects active containers before attempting to remove.
    """
    max_attempts = 3

    if force:
        # Disconnect any active containers from the network
        subprocess.run(["docker", "network", "disconnect", "-f", "cassandra"], check=False)

    for attempt in range(max_attempts):
        result = subprocess.run(["docker", "network", "rm", "cassandra"], check=False, capture_output=True, text=True)
        if result.returncode == 0:
            print("Cassandra network removed successfully.")
            break
        elif "active endpoints" in result.stderr:
            print(f"Attempt {attempt+1}/{max_attempts}: Waiting for network disconnection...")
            time.sleep(5)
        else:
            print(f"Warning: Failed to remove Cassandra network (attempt {attempt+1}/{max_attempts}):", result.stderr.strip())

