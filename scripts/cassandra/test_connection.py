
from cassandra.cluster import Cluster
from src.config import CASSANDRA_HOST, CASSANDRA_PORT, CASSANDRA_KEYSPACE

# Puerto de Cassandra expuesto en nuestra Mac
cluster = Cluster([CASSANDRA_HOST], port=CASSANDRA_PORT)

try:
    session = cluster.connect(CASSANDRA_KEYSPACE)

    rows = session.execute(
        "SELECT table_name FROM system_schema.tables "
        "WHERE keyspace_name = %s", (CASSANDRA_KEYSPACE,)
    )

    print("Conexion exitosa con Cassandra")

    for row in rows:
        print("-", row.table_name)

finally:
    cluster.shutdown()
