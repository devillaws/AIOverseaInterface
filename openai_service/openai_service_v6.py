import json
import time
from json import JSONDecodeError

import flask
import openai
import redis
import requests
from flask import Flask, redirect, render_template, request, url_for, logging, session
from loguru import logger
from common import key_manager
from common.my_exception import balanceException, getApiKeyException
from utils.redis_util import REDIS
from common import response_manager
from flask import current_app


def gpt35turbo():
    try:
        response_redis = REDIS.client_list()
    except redis.exceptions.RedisError as e:
        logger.error("redis_error:连接不上redis")
        return response_manager.make_response(1, "redis", "获取redis连接失败", None)
    try:
        authorization_key = request.headers.get("Authorization-Key")
        user_id = request.headers.get("user-id")
        chat_id = request.headers.get("chat-id")
        logger.info("authorization_key:" + authorization_key)
        print("user_id", user_id)
        requset_json = flask.request.json
        if requset_json is None or authorization_key is None or authorization_key != "BIGBOSS@510630":
            logger.error("请求头key不正确，或入参json不存在，请检查请求")
            return response_manager.make_response(1, "request", "请求头key不正确，或入参json不存在，请检查请求", None)
        if requset_json is None or user_id is None or chat_id is None or len(user_id) == 0 or len(chat_id) == 0:
            logger.error("会话id或用户id为空")
            return response_manager.make_response(1, "session", "会话id或用户id为空", None)
        model = requset_json.get('model', "gpt-3.5-turbo")  # 必要，模型名字
        session_id = user_id + "&" + chat_id
        is_clear_session = requset_json.get('is_clear_session', 0)  # "is_clear_session":1,
        session_id_test = session_id

        # api_key调度代码段——start
        try:
            openai_api_key = key_manager.catch_key_times()
            print("选用的key:", openai_api_key)
        except getApiKeyException as e:
            return response_manager.make_response(1, "getApiKey", "多线程获取api失败，原因：" + str(e), None)
        except balanceException as e:
            return response_manager.make_response(1, "balance",
                                                  "已从key池中选出最少调用的key，但该key依旧在20秒内超过5次调用，请缓缓",
                                                  None)

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

        #session_prompt_arr = session.get(session_id, [])
        redis_session = REDIS.get(session_id)
        session_prompt_arr = []
        if redis_session is not None:
            session_prompt_arr = json.loads(redis_session)
        messages_request = build_session_query(messages, system, session_id, session_prompt_arr)
        answer = ""
        try:
            headers = {}
            headers["Content-Type"] = "application/json; charset=UTF-8"
            headers["Authorization"] = "Bearer " + openai_api_key
            data = {}
            data["model"] = "gpt-3.5-turbo"
            data["temperature"] = temperature
            data["messages"] = messages_request
            data["stream"] = True
            data["max_tokens"] = max_tokens
            data["presence_penalty"] = presence_penalty
            data["frequency_penalty"] = frequency_penalty
            url = 'https://api.openai.com/v1/chat/completions'
            # proxies = {  # 针对urllib3最新版bug的手动设置代理
            #     'http': 'http://127.0.0.1:3129',
            #     'https': 'http://127.0.0.1:3129'
            # }
            proxies = {  # 针对urllib3最新版bug的手动设置代理,且针对院内走ssh隧道
                'http': 'socks5h://127.0.0.1:3129',
                'https': 'socks5h://127.0.0.1:3129'
            }
            # 注意如果上下文太长，会报None is not of type 'string' - 'messages.1.content'"
            response = requests.post(url, data=json.dumps(data), headers=headers, proxies=proxies, stream=True)
            #response = requests.post(url, data=json.dumps(data), headers=headers, stream=True)
            # sse返回
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        line = line[6:].strip()
                        response_data = json.loads(line)
                        if "choices" in response_data:
                            delta = response_data["choices"][0]["delta"]
                            if "content" in delta:
                                content = delta["content"]
                                answer += content
                                print(content)
                                yield "data:{}\n\n".format(content)
                            finish_reason = response_data["choices"][0]["finish_reason"]
                            if finish_reason is not None and finish_reason == "stop":
                                # save_session_answer(messages, answer, session_id, session_prompt_arr)
                                yield "data:[DONE]\n\n"
                                break
                                # response.close()
                                # logger.info("success")
            response.close()
            save_session_answer(messages, answer, session_id, session_prompt_arr)
            # REDIS.flushdb()
            logger.info("success")
            return
            # sse
        except JSONDecodeError as e:
            logger.error("request.post:" + str(e))
            return response_manager.make_response(1, "request.post", str(e), None)
        except Exception as e:
            logger.error("request.post:" + str(e))
            e.traceback.print_exc()
            return response_manager.make_response(1, "request.post", str(e), None)
    except Exception as e:
        logger.error("system_error:" + str(e))
        e.traceback.print_exc()
        return response_manager.make_response(1, "system", str(e), None)


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
    session[session_id] = session_prompt  # 保存进session
    numbers_str = json.dumps(session_prompt)
    REDIS.set(session_id, numbers_str)
