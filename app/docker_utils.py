import subprocess
import time
from cassandra.cluster import Cluster

def start_cassandra_container():
    try:
        # Pull the Cassandra image if it doesn't exist
        subprocess.run(["docker", "pull", "cassandra:latest"], check=True)

        # Check if the Docker network exists, and create it if it doesn't
        result = subprocess.run(["docker", "network", "ls", "--filter", "name=cassandra", "--format", "{{.Name}}"], capture_output=True, text=True)
        if "cassandra" not in result.stdout:
            subprocess.run(["docker", "network", "create", "cassandra"], check=True)

        # Check if the Cassandra container is already running
        result = subprocess.run(["docker", "ps", "--filter", "name=cassandra", "--format", "{{.Names}}"], capture_output=True, text=True)
        if "cassandra" in result.stdout:
            print("Cassandra container is already running.")
            return

        # Run the Cassandra container
        subprocess.run([
            "docker", "run", "--rm", "-d",
            "--name", "cassandra",
            "--hostname", "cassandra",
            "--network", "cassandra",
            "-p", "9042:9042",
            "cassandra:latest"
        ], check=True)

        # Wait for Cassandra to initialize
        print("Waiting for Cassandra to start...")
        time.sleep(10)  # Adjust the sleep time as needed

    except subprocess.CalledProcessError as e:
        print(f"Error starting Cassandra container: {e}")

def stop_cassandra_container():
    try:
        # Stop and remove the Cassandra container
        subprocess.run(["docker", "stop", "cassandra"], check=True)

        # Remove the Docker network
        subprocess.run(["docker", "network", "rm", "cassandra"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error stopping Cassandra container: {e}")