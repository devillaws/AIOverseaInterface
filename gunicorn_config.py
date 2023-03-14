nd = '127.0.0.1:8000'  # 绑定的 IP 和端口
workers = 1  # Gunicorn 进程数
threads = 5
work_connections = 100
worker_class = 'gevent'  # 工作进程类型
pidfile = '/var/run/gunicorn.pid'
accesslog = "log/gunicorn_access.log"
errorlog = "log/gunicorn_error.log"

loglevel = "info"
