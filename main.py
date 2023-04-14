from config.config import config
from loguru import logger
from openai_service import clear_session, openai_service_v7, openai_edit_v7, openai_api_chat
from flask import Flask
from flask_session import Session
import atexit

app = Flask(__name__)
# app.debug = True
# app.config['SESSION_TYPE'] = 'redis'  # session类型为redis
# app.config['SESSION_PERMANENT'] = True  # 如果设置为True，则关闭浏览器session就失效。
# app.config['SESSION_USE_SIGNER'] = 'BIGBOSS@510630'  # 是否对发送到浏览器上session的cookie值进行加密
# app.config['SESSION_KEY_PREFIX'] = 'bigboss'  # 保存到session中的值的前缀
# app.config['SESSION_REDIS'] = REDIS  # 用于连接redis的配置
# app.config['MYSQL_POOL'] = connection_pool
# app.config.from_object(config["Pro"])
# Session(app)


@app.route("/ai/openai/clear_flask_session", methods=("GET", "POST"))
def clear():
    return clear_session.clear()


@app.route("/ai/openai/clear_Redis_session", methods=("GET", "POST"))
def clear_redis():
    return clear_session.clear_redis()


@app.route("/ai/openai/v7/gpt35turbo", methods=("GET", "POST"))
def gpt35turbov7():
    return openai_service_v7.gpt35turbo()


@app.route("/ai/openai/v7/edit", methods=("GET", "POST"))
def v7edit():
    return openai_edit_v7.edit()


@app.route("/api/openai/chat", methods=("GET", "POST"))
def openai_chat():
    return openai_api_chat.chat()


@app.before_first_request
def setup():
    atexit.register(close_database_connection)
    logger.info("程序初始化完毕")


def close_database_connection():
    logger.info("程序已退出")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
    logger.info("系统已关闭") #为什么会跑两次


# @app.route('exit')
# def hello_world():
#     sys.exit("程序退出")