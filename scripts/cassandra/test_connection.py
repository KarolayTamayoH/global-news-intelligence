
from cassandra.cluster import Cluster

# Puerto de Cassandra expuesto en nuestra Mac
cluster = Cluster(["127.0.0.1"], port=9043)

try:
    session = cluster.connect("global_news_analytics")

    rows = session.execute(
        "SELECT table_name FROM system_schema.tables "
        "WHERE keyspace_name = 'global_news_analytics'"
    )

    print("Conexion exitosa con Cassandra")

    for row in rows:
        print("-", row.table_name)

finally:
    cluster.shutdown()
