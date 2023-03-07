import json
import flask
import openai
import redis
import openai_service_v1
from flask import Flask, redirect, render_template, request, url_for, logging, session
from flask_session import Session
from utils import redis_util
import openai_service_v2
from utils.redis_util import REDIS


app = Flask(__name__)
# app.debug = True
app.secret_key = "BIGBOSS@510630"
app.config['SESSION_TYPE'] = 'redis'  # session类型为redis
app.config['SESSION_PERMANENT'] = False  # 如果设置为True，则关闭浏览器session就失效。
app.config['SESSION_USE_SIGNER'] = False  # 是否对发送到浏览器上session的cookie值进行加密
app.config['SESSION_KEY_PREFIX'] = 'session:'  # 保存到session中的值的前缀
app.config['SESSION_REDIS'] = REDIS # 用于连接redis的配置

Session(app)


@app.route("/ai/openai/v1/gpt35turbo", methods=("GET", "POST"))
def gpt35turbo():
    return openai_service_v1.gpt35turbo()


@app.route("/ai/openai/v2/gpt35turbo", methods=("GET", "POST"))
def gpt35turbov2():
    return openai_service_v2.gpt35turbo()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
