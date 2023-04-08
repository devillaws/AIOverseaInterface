from config import setting
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
    # 自己库初始连接
    connection_pool = pooling.MySQLConnectionPool(
        pool_size=25,
        pool_name="my_pool",
        host=setting.mysql_host,
        port=setting.mysql_port,
        user=setting.mysql_user,
        password=setting.mysql_password,
        db=setting.mysql_db)
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
    # arena库初始连接
    arena_connection_pool = pooling.MySQLConnectionPool(
        pool_size=25,
        pool_name="my_pool",
        host=setting.arena_mysql_host,
        port=setting.arena_mysql_port,
        user=setting.arena_mysql_user,
        password=setting.arena_mysql_password,
        db=setting.arena_mysql_db)
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



def add_api_log(ip, request_json, response_text, status, err_type, err_msg, authorization_key, select_api_key, create_time):
    connection = connection_pool.get_connection()
    cursor = connection.cursor()
    insert_query = "INSERT INTO t_api_log (ip,request_json,response_text,status,err_type, err_msg, authorization_key, select_api_key, create_time) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    values = (ip, request_json, response_text, status, err_type, err_msg, authorization_key, select_api_key, create_time)
    cursor.execute(insert_query, values)
    connection.commit()
    #if connection.is_connected():
    cursor.close()
    connection.close()


def check_key(authorization_key):
    connection = arena_connection_pool.get_connection()
    query = "SELECT * FROM t_auth_keys WHERE key_id = %s and status = %s"
    values = (authorization_key, 0)
    cursor = connection.cursor()
    cursor.execute(query, values)
    result = cursor.fetchall()
    rowcount = cursor.rowcount
    cursor.close()
    connection.close()
    if rowcount >= 1:
        return True
    else:
        return False

