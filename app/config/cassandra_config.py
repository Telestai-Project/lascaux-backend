from cassandra.cluster import Cluster

def get_cluster():
    return Cluster(['127.0.0.1'], port=9052)

def create_keyspace(session, keyspace="lascaux"):
    session.execute(f"""
        CREATE KEYSPACE IF NOT EXISTS {keyspace}
        WITH replication = {{ 'class': 'SimpleStrategy', 'replication_factor': 1 }}
    """)