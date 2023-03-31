from mysql.connector import pooling
from common import key_manager

# 家中开发
home_config = {
    "host": "202.144.195.96",
    "port": 13306,
    "user": "aiuser",
    "password": "BIGBOSS@aiproject",
    "database": "aidb"
}
# 院内开发生产
dev_config = {
    "host": "172.16.135.9",
    "port": 13306,
    "user": "aiuser",
    "password": "Gpdi@510630",
    "database": "aidb"
}

# 生产
pro_config = {
    "host": "127.0.0.1",
    "port": 13306,
    "user": "aiuser",
    "password": "Gpdi@510630",
    "database": "aidb"
}

# 创建 MySQL 连接池
try:
    connection_pool = pooling.MySQLConnectionPool(pool_name="my_pool",
                                                  pool_size=25,
                                                  **pro_config)
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


def add_chat_log(ip, user_id, chat_id, query, answer, status, err_type, err_msg, select_api_key, create_time):
    connection_add = connection_pool.get_connection()
    cursor_add = connection_add.cursor()
    insert_query = "INSERT INTO t_chat_log (ip, user_id,chat_id,query,answer,status,err_type, err_msg, select_api_key, create_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    values = (ip, user_id, chat_id, query, answer, status, err_type, err_msg, select_api_key, create_time)
    cursor_add.execute(insert_query, values)
    connection_add.commit()
    cursor_add.close()
    connection_add.close()
