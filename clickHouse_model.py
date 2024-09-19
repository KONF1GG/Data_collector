from sqlalchemy import create_engine

# Replace with your ClickHouse credentials
clickhouse_url = 'clickhouse+http://default:Kehrvjfh123@192.168.110.52:8123/default'
engine = create_engine(clickhouse_url)

# Test connection
with engine.connect() as connection:
    result = connection.execute("SELECT version()")
    for row in result:
        print(row)
