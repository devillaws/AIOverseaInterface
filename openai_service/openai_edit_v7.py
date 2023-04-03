import json
import flask
import redis
from flask import request
from loguru import logger
from utils.redis_util import REDIS
from common import response_manager


def edit():
    try:
        response_redis = REDIS.client_list()
    except redis.exceptions.RedisError as e:
        logger.error("redis_error:连接不上redis")
        return response_manager.make_response(1, "redis", "获取redis连接失败", None)
    try:
        authorization_key = request.headers.get("Authorization-Key")
        user_id = request.headers.get("user-id")
        chat_id = request.headers.get("chat-id")
        requset_json = flask.request.json
        if requset_json is None or authorization_key is None or authorization_key != "BIGBOSS@510630":
            logger.error("请求头key不正确，或入参json不存在，请检查请求")
            return response_manager.make_response(1, "request", "请求头key不正确，或入参json不存在，请检查请求", None)
        if requset_json is None or user_id is None or chat_id is None or len(user_id) == 0 or len(chat_id) == 0:
            logger.error("会话id或用户id为空")
            return response_manager.make_response(1, "session", "会话id或用户id为空", None)
        session_id = user_id + "&" + chat_id
        logger.info("session_id用户调用edit接口:" + session_id)
        messages = requset_json.get('messages', None)  # 必填，消息内容
        try:
            numbers_str = json.dumps(messages)
            REDIS.set(session_id, numbers_str)
            print("已编辑session_id：", session_id)
            logger.info("已编辑session_id：" + session_id)
            return response_manager.make_response(0, None, None, "已编辑session_id：" + session_id)
        except Exception as e:
            print("edit_session_error：", session_id)
            logger.error("edit_session_error:" + str(e))
            return response_manager.make_response(1, "edit_session_error", str(e), None)
    except Exception as e:
        logger.error("system_error:" + str(e))
        return response_manager.make_response(1, "system_error", str(e), None)