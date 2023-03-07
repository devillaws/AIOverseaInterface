import json
import flask
import openai
import redis
from flask import Flask, redirect, render_template, request, url_for, logging, session
from utils.log import logger
from flask_session import Session
from utils.redis_util import REDIS


def gpt35turbo():
    res_dict = {
        "code": 1,
        "errType": None,
        "errMsg": None,
        "msg": None
    }
    try:
        response = REDIS.client_list()
    except redis.exceptions.RedisError as e:
        logger.error("redis_error:连接不上redis")
        res_dict['errType'] = "redis"
        res_dict['errMsg'] = "获取redis连接失败"
        res_json = json.dumps(res_dict)
        return res_json, 200, {"Content-Type": "application/json"}

    try:
        authorization_key = flask.request.headers.get("Authorization-Key")
        user_id = flask.request.headers.get("user_id")
        chat_id = flask.request.headers.get("session_id")
        requset_json = flask.request.json
        if requset_json is None or authorization_key is None or authorization_key != "BIGBOSS@510630":
            logger.info("请求头key不正确，或入参json不存在，请检查请求")
            res_dict['errType'] = "request"
            res_dict['errMsg'] = "请求头key不正确，或入参json不存在，请检查请求"
            res_json = json.dumps(res_dict)
            return res_json, 200, {"Content-Type": "application/json"}
        if requset_json is None or user_id is None or chat_id is None:
            logger.info("会话id或用户id为空")
            res_dict['errType'] = "session"
            res_dict['errMsg'] = "会话id或用户id为空"
            res_json = json.dumps(res_dict)
            return res_json, 200, {"Content-Type": "application/json"}
        model = requset_json.get('model', "gpt-3.5-turbo")  # 必要，模型名字
        open_api_key = requset_json.get('open_api_key', None)
        system = requset_json.get('system', None)
        session_id = user_id + "&" + chat_id

        is_clear_session = requset_json.get('is_clear_session', 0)  # "is_clear_session":1,
        if is_clear_session == 1:
            del session[session_id]
            logger.info("success")
            res_dict["code"] = 0
            res_dict['msg'] = "已清空session_id："+session_id
            res_json = json.dumps(res_dict)
            return res_json, 200, {"Content-Type": "application/json"}

        messages = requset_json.get('messages', None)  # 必填，消息内容
        temperature = requset_json.get('temperature', 1)  # 可选，默认为1，0~2，数值越高创造性越强
        top_p = requset_json.get('top_p', 1)  # 可选，默认为1，0~1，效果类似temperature，不建议都用
        n = requset_json.get('n', 1)  # 可选，默认为1，chatgpt对一个提问生成多少个回答
        stream = requset_json.get('stream', False)  # 可选，默认为False，设置为True和网页效果类似，需监听事件来解析
        stop = requset_json.get('stop', None)  # 可选，chatgpt遇到stop里的字符串时停止生成内容
        max_tokens = requset_json.get('max_tokens', 2048)  # 可选，默认无穷大，如果设置了，需要满足max_tokens+message_token<=4096
        presence_penalty = requset_json.get('presence_penalty', 0)  # 可选，默认为0，-2~2，越大越不允许跑题
        frequency_penalty = requset_json.get('frequency_penalty', 0)  # 可选，默认为0，-2~2，越大越不允许复读机
        logit_bias = requset_json.get('logit_bias', None)  # 可选，默认无，影响特定词汇的生成概率？
        user = requset_json.get('user', None)  # 可选，默认无，用户名
        tran_ascii = requset_json.get('tran_ascii', 0)

        session_prompt_arr = session.get(session_id, [])
        messages_request = build_session_query(messages, session_id, system, session_prompt_arr)
        try:
            openai.api_key = open_api_key
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages_request,
                temperature=temperature,
                stream=stream,
                max_tokens=max_tokens,
                presence_penalty=presence_penalty,
                frequency_penalty=frequency_penalty
            )
        except Exception as e:
            logger.error("openai_error:" + str(e))
            res_dict["code"] = 1
            res_dict["errType"] = "openai"
            res_dict['errMsg'] = str(e)
            res_json = json.dumps(res_dict)
            return res_json, 200, {"Content-Type": "application/json"}

        # text = response['choices'][0]['message']['content']
        # [choice.message.content for choice in response.choices]
        answer = response['choices'][0]['message']['content']
        save_session_answer(session_prompt_arr, messages, answer, session_id)
        logger.info("success")
        res_dict["code"] = 0
        res_dict['msg'] = answer
        res_json = json.dumps(res_dict)
        return res_json, 200, {"Content-Type": "application/json"}

    except Exception as e:
        logger.error("system_error:" + str(e))
        res_dict["code"] = 1
        res_dict["errType"] = "system"
        res_dict['errMsg'] = str(e)
        res_json = json.dumps(res_dict)
        return res_json, 200, {"Content-Type": "application/json"}


def build_session_query(query, session_id, system, session_prompt):
    query_dict = {"role": "user", "content": query}
    system_dict = {"role": "system", "content": system}
    session_prompt = session.get(session_id, [])
    session_prompt.append(query_dict)
    session_prompt.append(system_dict)
    return session_prompt


def save_session_answer(session_prompt_arr, query, answer, session_id):
    answer_dict = {"role": "assistant", "content": answer}
    query_dict = {"role": "user", "content": query}
    session_prompt_arr.append(answer_dict)
    session_prompt_arr.append(query_dict)
    session[session_id] = session_prompt_arr

