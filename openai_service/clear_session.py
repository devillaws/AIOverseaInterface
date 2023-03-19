import json
import time

import flask
from flask import request, session
from loguru import logger
from common import response_manager
from utils.redis_util import REDIS


def clear():
    try:
        authorization_key = request.headers.get("Authorization-Key")
        user_id = request.headers.get("user-id")
        chat_id = request.headers.get("chat-id")
        logger.info("authorization_key:" + authorization_key)
        if  authorization_key is None or authorization_key != "BIGBOSS@510630":
            logger.error("请求头key不正确，请检查请求")
            return response_manager.make_response(1, "request", "请求头key不正确，请检查请求", None)
        session_id = user_id + "&" + chat_id
        try:
            del session[session_id]
            print("已清空session_id：", user_id)
            logger.info("已清空session_id：" + session_id)
            return response_manager.make_response(0, None, None, "已清空session_id：" + session_id)
        except KeyError as e:
            print("clear_session_error:查询不到sessionid", session_id)
            logger.error("clear_session_error:查询不到" + str(e))
            return response_manager.make_response(1, "clear_session_error", "查询不到" + str(e), None)
    except Exception as e:
        logger.error("system_error:" + str(e))
        e.traceback.print_exc()
        return response_manager.make_response(1, "system", str(e), None)


def clear_redis():
    try:
        authorization_key = request.headers.get("Authorization-Key")
        user_id = request.headers.get("user-id")
        chat_id = request.headers.get("chat-id")
        logger.info("authorization_key:" + authorization_key)
        if authorization_key is None or authorization_key != "BIGBOSS@510630":
            logger.error("请求头key不正确，请检查请求")
            return response_manager.make_response(1, "request", "请求头key不正确，请检查请求", None)
        if user_id is None or chat_id is None or len(user_id) == 0 or len(chat_id) == 0:
            logger.error("会话id或用户id为空")
            return response_manager.make_response(1, "session", "会话id或用户id为空", None)
        session_id = user_id + "&" + chat_id
        try:
            REDIS.delete(session_id)
            print("已清空session_id：", user_id)
            logger.info("已清空session_id：" + session_id)
            return response_manager.make_response(0, None, None, "已清空session_id：" + session_id)
        except KeyError as e:
            print("clear_session_error:查询不到sessionid", session_id)
            logger.error("clear_session_error:查询不到" + str(e))
            return response_manager.make_response(1, "clear_session_error", "查询不到" + str(e), None)
    except Exception as e:
        logger.error("system_error:" + str(e))
        e.traceback.print_exc()
        return response_manager.make_response(1, "system", str(e), None)