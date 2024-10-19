from app.docker_utils import stop_cassandra_container

def stop_cassandra():
    print("Stopping Cassandra Container...")
    try:
        stop_cassandra_container()
        print("Cassandra Container stopped successfully.")
    except Exception as e:
        print(f"Failed to stop Cassandra container: {str(e)}")

if __name__ == "__main__":
    stop_cassandra()
