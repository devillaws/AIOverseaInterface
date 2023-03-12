import json
import flask
import openai
import redis
from collections import deque
from flask import Flask, redirect, render_template, request, url_for, logging, session

from common import key_manager
from common.key_manager import key_times, key_time_deque
from utils.log import logger
from flask_session import Session
from utils.redis_util import REDIS
from common import key_manager
import time


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
        chat_id = flask.request.headers.get("chat_id")
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
        session_id = user_id + "&" + chat_id

        is_clear_session = requset_json.get('is_clear_session', 0)  # "is_clear_session":1,
        if is_clear_session == 1:
            del session[session_id]
            logger.info("success")
            res_dict["code"] = 0
            res_dict['msg'] = "已清空session_id：" + session_id
            res_json = json.dumps(res_dict)
            return res_json, 200, {"Content-Type": "application/json"}
        # api_key调度代码段——start
        openai_api_key = None
        # 获取最小调用次数的key，用来平均key的调用
        print("目前key字典情况：", key_times)
        min_key = min(key_times, key=key_times.get)
        print("选用的key:", min_key)
        # 计算即将调用的key的每分钟使用频率,限制20秒5次
        call_time = time.time()
        call_time_list = key_time_deque.get(min_key)
        sum_dec = 0
        if call_time_list is None:
            call_time_list = deque(maxlen=10)
            call_time_list.append(call_time)
            key_time_deque[min_key] = call_time_list
        elif len(call_time_list) > 5:
            for i in range(1, 5):
                sum_dec += abs(call_time_list[-i], call_time_list[-i - 1])
            sum_dec += call_time - call_time_list[-1]
            if sum_dec < 20:
                logger.error("balance_error:已从key池中选出最少调用的key，但该key依旧在20秒内超过5次调用，请缓缓")
                res_dict["code"] = 1
                res_dict["errType"] = "balance"
                res_dict['errMsg'] = "已从key池中选出最少调用的key，但该key依旧在20秒内超过5次调用，请缓缓"
                res_json = json.dumps(res_dict)
                return res_json, 200, {"Content-Type": "application/json"}
            else:
                key_times[min_key] += 1
                call_time_list.append(call_time)
                key_time_deque[min_key] = call_time_list
                openai_api_key = min_key
        else:
            call_time_list.append(call_time)
            key_time_deque[min_key] = call_time_list

        # api_key调度代码段——end
        messages = requset_json.get('messages', None)  # 必填，消息内容
        temperature = requset_json.get('temperature', 1)  # 可选，默认为1，0~2，数值越高创造性越强
        top_p = requset_json.get('top_p', 1)  # 可选，默认为1，0~1，效果类似temperature，不建议都用
        n = requset_json.get('n', 1)  # 可选，默认为1，chatgpt对一个提问生成多少个回答
        stream = False  # 可选，默认为False，设置为True和网页效果类似，需监听事件来解析
        system = requset_json.get('system', None)
        stop = requset_json.get('stop', None)  # 可选，chatgpt遇到stop里的字符串时停止生成内容
        max_tokens = requset_json.get('max_tokens', 2048)  # 可选，默认无穷大，如果设置了，需要满足max_tokens+message_token<=4096
        presence_penalty = requset_json.get('presence_penalty', 0)  # 可选，默认为0，-2~2，越大越不允许跑题
        frequency_penalty = requset_json.get('frequency_penalty', 0)  # 可选，默认为0，-2~2，越大越不允许复读机
        logit_bias = requset_json.get('logit_bias', None)  # 可选，默认无，影响特定词汇的生成概率？
        user = requset_json.get('user', None)  # 可选，默认无，用户名
        tran_ascii = requset_json.get('tran_ascii', 0)

        session_prompt_arr = session.get(session_id, [])
        messages_request = build_session_query(messages, system, session_id, session_prompt_arr)
        answer = None

        try:
            openai.api_key = openai_api_key
            # response = openai.ChatCompletion.create(
            #     model=model,
            #     messages=messages_request,
            #     temperature=temperature,
            #     stream=stream,
            #     max_tokens=max_tokens,
            #     presence_penalty=presence_penalty,
            #     frequency_penalty=frequency_penalty
            # )
            response ="测试中"

        except Exception as e:
            logger.error("openai_error:" + str(e))
            res_dict["code"] = 1
            res_dict["errType"] = "openai"
            res_dict['errMsg'] = str(e)
            res_json = json.dumps(res_dict)
            return res_json, 200, {"Content-Type": "application/json"}

        save_session_answer(messages, answer, session_id, session_prompt_arr)
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


def build_session_query(query, system, session_id, session_prompt_arr):
    query_dict = {"role": "user", "content": query}
    system_dict = {"role": "system", "content": system}
    session_prompt = session_prompt_arr.copy()
    session_prompt.append(query_dict)
    session_prompt.append(system_dict)
    return session_prompt


def save_session_answer(query, answer, session_id, session_prompt_arr):
    query_dict = {"role": "user", "content": query}
    answer_dict = {"role": "assistant", "content": answer}
    session_prompt = session_prompt_arr.copy()
    session_prompt.append(query_dict)
    session_prompt.append(answer_dict)
    session[session_id] = session_prompt
