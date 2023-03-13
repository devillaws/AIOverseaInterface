from mysql.connector import pooling
from common import key_manager

# 开发
config = {
    "host": "202.144.195.96",
    "port": 13306,
    "user": "aiuser",
    "password": "BIGBOSS@aiproject",
    "database": "aidb"
}
# 生产
pro_config = {
    "host": "202.144.195.96",
    "port": 13306,
    "user": "aiuser",
    "password": "BIGBOSS@aiproject",
    "database": "aidb"
}

# 创建 MySQL 连接池
try:
    connection_pool = pooling.MySQLConnectionPool(pool_name="my_pool",
                                                  pool_size=25,
                                                  **config)
    connection = connection_pool.get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT api_key FROM openai_keys where status = 0")
    result = cursor.fetchall()
    column_values = []
    for row in result:
        column_values.append(row[0])  # 获取第一列的数据
    # 把key装进字典里
    for i in range(len(column_values)):
        key_manager.key_times[column_values[i]] = 0
    # 将连接放回连接池
    if connection.is_connected():
        cursor.close()
        connection.close()
except Exception as e:
    raise e
