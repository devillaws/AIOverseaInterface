import flask
import gevent
# from gevent import monkey
# from gevent import pywsgi
# monkey.patch_all()  # 打上猴子补丁，非常耗时
from loguru import logger
from werkzeug.debug import DebuggedApplication
from openai_service import openai_service_v2, openai_service_v1, openai_service_v4, openai_service_v5, \
    openai_service_v6, clear_session, openai_service_v3
from flask import Flask, request, render_template, Response, stream_with_context, session
from flask_session import Session, RedisSessionInterface
from config import config
from utils.mysql_util import connection_pool
from flask_sse import sse
from flask_cors import CORS

app = Flask(__name__)
# app.debug = True
# app.secret_key = "BIGBOSS@510630"
# app.config['SESSION_TYPE'] = 'redis'  # session类型为redis
# app.config['SESSION_PERMANENT'] = True  # 如果设置为True，则关闭浏览器session就失效。
# app.config['SESSION_USE_SIGNER'] = 'BIGBOSS@510630'  # 是否对发送到浏览器上session的cookie值进行加密
# app.config['SESSION_KEY_PREFIX'] = 'bigboss'  # 保存到session中的值的前缀
# app.config['SESSION_REDIS'] = REDIS  # 用于连接redis的配置
app.config.from_object(config["Dev"])
app.config["REDIS_URL"] = "redis://127.0.0.1"
app.register_blueprint(sse, url_prefix="/sse/data")
session_interface = RedisSessionInterface(app.config['SESSION_REDIS'], app.config['SESSION_KEY_PREFIX'])
app.session_interface = session_interface
cors = CORS(app)
app.config['MYSQL_POOL'] = connection_pool
#Session(app)


@app.route('/')
def index():
    return """
        <!DOCTYPE html>
        <html>
            <body>
            <h1>response:</h1>
            <div id="result"></div>
            <script>
            var source = new EventSource("/sse/data");
            source.onmessage = function(event) {
                document.getElementById("result").innerHTML += event.data + "<br>";
            };
            </script>
            </body>
        </html>
        """


@app.route("/ai/openai/v1/gpt35turbo", methods=("GET", "POST"))
def gpt35turbo():
    return openai_service_v1.gpt35turbo()


@app.route("/ai/openai/v2/gpt35turbo", methods=("GET", "POST"))
def gpt35turbov2():
    return openai_service_v2.gpt35turbo()


@app.route("/ai/openai/v3/gpt35turbo", methods=("GET", "POST"))
def gpt35turbov3():
    return openai_service_v3.gpt35turbo()


@app.route("/ai/openai/v4/gpt35turbo", methods=("GET", "POST"))
def gpt35turbov4():
    return openai_service_v4.gpt35turbo()


@app.route("/ai/openai/v5/gpt35turbo", methods=("GET", "POST"))
def gpt35turbov5():
    return openai_service_v5.gpt35turbo()


@app.route("/ai/openai/v6/gpt35turbo", methods=("GET", "POST"))
def gpt35turbov6():
    # openai_service_v6.gpt35turbo()
    response = Response(stream_with_context(openai_service_v6.gpt35turbo()), mimetype='text/event-stream')
    return response


@app.route("/ai/openai/clear_flask_session", methods=("GET", "POST"))
def clear():
    return clear_session.clear()


@app.route("/ai/openai/clear_Redis_session", methods=("GET", "POST"))
def clear_redis():
    return clear_session.clear_redis()

# @app.teardown_appcontext
# def close_db_pool(exception):
#     # Retrieve the connection pool from Flask's application context
#     if connection_pool is not None:
#         # Release all connections in the pool
#         connection_pool.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
    logger.info("系统已关闭")
    # dapp = DebuggedApplication(app, evalex=True)
    # gevent.config.threadpool_size = 50
    # server = pywsgi.WSGIServer(('127.0.0.1', 5000), app)
    # server.serve_forever()
