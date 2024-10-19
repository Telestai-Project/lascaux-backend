from app.docker_utils import start_cassandra_container

def start_cassandra():
    print("Starting Cassandra container...")
    try:
        start_cassandra_container()
        print("Cassandra container started successfully.")
    except Exception as e:
        print(f"Failed to start Cassandra container: {str(e)}")

if __name__ == "__main__":
    start_cassandra()
