from decouple import config

# mysql配置
# mysql_host=172.16.135.9
mysql_host = config("mysql_host")
mysql_port = config("mysql_port", default=13306, cast=int)
mysql_user = config("mysql_user")
mysql_password = config("mysql_password")
mysql_db = config("mysql_db")
mysql_minsize = config("mysql_minsize", default=25, cast=int)
mysql_maxsize = config("mysql_maxsize", default=50, cast=int)
# redis配置
redis_host = config("redis_host")
redis_port = config("redis_port", default=23333, cast=int)
redis_password = config("redis_password")
redis_max_connections = config("redis_max_connections", default=500, cast=int)
# 代理配置
proxies = config("proxies")
