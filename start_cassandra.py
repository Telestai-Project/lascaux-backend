from app.docker_utils import start_cassandra_container, stop_cassandra_container

def start_cassandra():
    print("Starting Cassandra container...")
    start_cassandra_container()
    print("Cassandra container started.")

if __name__ == "__main__":
    start_cassandra()