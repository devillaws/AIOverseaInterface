import base64
import datetime
import json
import time
from json import JSONDecodeError
# import tiktoken
import flask
import gevent
import redis
import requests
from flask import Flask, redirect, render_template, request, url_for, logging, session, Response
from loguru import logger
from common import key_manager
from common.my_exception import balanceException, getApiKeyException
from utils.mysql_util import add_chat_log
from utils.redis_util import REDIS
from common import response_manager


def gpt35turbo():
    user_id = None
    chat_id = None
    messages = None
    answer = None
    ip = None
    openai_api_key = None
    try:
        ip = request.remote_addr
        authorization_key = request.headers.get("Authorization-Key")
        user_id = request.headers.get("user-id", None)
        chat_id = request.headers.get("chat-id", None)
        requset_json = flask.request.json
        if requset_json is None or authorization_key is None or authorization_key != "BIGBOSS@510630":
            err_type = "hearder_error"
            err_msg = "请求头key不正确，或入参json不存在，请检查请求"
            return response_manager.make_response2(1, ip, user_id, chat_id, messages, answer, err_type, err_msg, openai_api_key)
        if requset_json is None or user_id is None or chat_id is None or len(user_id) == 0 or len(chat_id) == 0:
            err_type = "hearder_error"
            err_msg = "会话id或用户id为空"
            return response_manager.make_response2(1, ip, user_id, chat_id, messages, answer, err_type, err_msg, openai_api_key)
        try:
            response_redis = REDIS.client_list()
        except redis.exceptions.RedisError as e:
            err_type = "redis_error"
            err_msg = "连接不上redis"
            return response_manager.make_response2(1, ip, user_id, chat_id, messages, answer, err_type, err_msg, openai_api_key)
        session_id = user_id + "&" + chat_id
        logger.info("session_id:" + session_id+",进入系统")
        messages = requset_json.get('messages', None)  # 必填，消息内容
        temperature = requset_json.get('temperature', 1)  # 可选，默认为1，0~2，数值越高创造性越强
        top_p = requset_json.get('top_p', 1)  # 可选，默认为1，0~1，效果类似temperature，不建议都用
        n = requset_json.get('n', 1)  # 可选，默认为1，chatgpt对一个提问生成多少个回答
        stream = False  # 可选，默认为False，设置为True和网页效果类似，需监听事件来解析
        system = requset_json.get('system', None)
        stop = requset_json.get('stop', None)  # 可选，chatgpt遇到stop里的字符串时停止生成内容
        # max_tokens = requset_json.get('max_tokens',None)  # 可选，默认无穷大，如果设置了，需要满足max_tokens+message_token<=4096,这是生成文本的最大长度
        presence_penalty = requset_json.get('presence_penalty', 0)  # 可选，默认为0，-2~2，越大越不允许跑题
        frequency_penalty = requset_json.get('frequency_penalty', 0)  # 可选，默认为0，-2~2，越大越不允许复读机
        logit_bias = requset_json.get('logit_bias', None)  # 可选，默认无，影响特定词汇的生成概率？
        user = requset_json.get('user', None)  # 可选，默认无，用户名
        tran_ascii = requset_json.get('tran_ascii', 0)
        # api_key调度代码段——start
        try:
            openai_api_key = key_manager.catch_key_times()
            logger.info("选用的key:" + openai_api_key)
        except getApiKeyException as e:
            err_type = "getApiKey_error"
            err_msg = "多线程获取api失败，原因：" + str(e)
            return response_manager.make_response2(1, ip, user_id, chat_id, messages, answer, err_type, err_msg, openai_api_key)
        except balanceException as e:
            err_type = "balance_error"
            err_msg = "已从key池中选出最少调用的key，但该key依旧在20秒内超过5次调用，请缓缓"
            return response_manager.make_response2(1, ip, user_id, chat_id, messages, answer, err_type, err_msg, openai_api_key)
        # api_key调度代码段——end
        redis_session = REDIS.get(session_id)
        session_prompt_arr = []
        if redis_session is not None:
            session_prompt_arr = json.loads(redis_session)
        messages_request = build_session_query(messages, system, session_id, session_prompt_arr)
        model = "gpt-3.5-turbo"  # 官方模型名字gpt-3.5-turbo
        try:
            headers = {}
            headers["Content-Type"] = "application/json; charset=UTF-8"
            headers["Authorization"] = "Bearer " + openai_api_key
            data = {}
            data["model"] = model
            data["temperature"] = temperature
            data["messages"] = messages_request
            data["stream"] = True
            # data["max_tokens"] = max_tokens
            data["presence_penalty"] = presence_penalty
            data["frequency_penalty"] = frequency_penalty
            url = 'https://api.openai.com/v1/chat/completions'
            proxies_dev = {  # 针对urllib3最新版bug的手动设置代理
                'http': 'http://127.0.0.1:2080',
                'https': 'http://127.0.0.1:2080' #注意必须要
            }
            proxies_product = {  # 针对院内走ssh隧道
                'http': 'socks5h://127.0.0.1:3129',
                'https': 'socks5h://127.0.0.1:3129'
            }
            proxies_dev2 = {  # 针对院内走ssh隧道
                'http': 'socks5h://172.16.135.9:3129',
                'https': 'socks5h://172.16.135.9:3129'
            }
            # 注意如果上下文太长，会报None is not of type 'string' - 'messages.1.content'"
            # response = requests.post(url, data=json.dumps(data), headers=headers, stream=True) # 无代理请求
            response = requests.post(url, data=json.dumps(data), headers=headers, proxies=proxies_product, stream=True)
            response.raise_for_status()
            # stream_delay = 0.1
            if response.status_code == 200:
                def event_stream():
                    answer = ""
                    for line in response.iter_lines():
                        # time.sleep(stream_delay)
                        # gevent.sleep(stream_delay)
                        if line:
                            line = line.decode('utf-8')
                            line = line[6:].strip()
                            if line == "[DONE]":
                                yield "data:[DONE]\n\n"
                                break
                            response_data = json.loads(line)
                            if "choices" in response_data:
                                delta = response_data["choices"][0]["delta"]
                                finish_reason = response_data["choices"][0]["finish_reason"]
                                if "content" in delta:
                                    content = delta["content"]
                                    answer += content
                                    json_content = json.dumps(content)
                                    yield "data:{}\n\n".format(json_content)
                                if finish_reason is not None and (finish_reason == "stop" or finish_reason == "length"):
                                    yield "data:[DONE]\n\n"
                                    break
                    response.close()
                    save_session_answer(messages, answer, session_id, session_prompt_arr)
                    add_chat_log(ip, user_id, chat_id, messages, answer, 0, None, None, openai_api_key, datetime.datetime.now())
                    logger.info("success")
                return Response(event_stream(), mimetype="text/event-stream")
            else:
                if response.text is not None:
                    err_json = json.loads(response.text)
                    err_json = err_json['error']
                    openai_err_msg = err_json.get('message', "")
                    openai_err_type = err_json.get('type', "")
                    err_type = "openai_error"
                    err_msg = openai_err_type+","+openai_err_msg
                    return response_manager.make_response2(1, ip, user_id, chat_id, messages, answer, err_type, err_msg, openai_api_key)
                else:
                    err_type = "openai_error"
                    err_msg = "response.text为空"
                    return response_manager.make_response2(1, ip, user_id, chat_id, messages, answer, err_type, err_msg, openai_api_key)
        except requests.exceptions.RequestException as e:
            if e.response is not None and e.response.text is not None:
                err_json = json.loads(e.response.text)
                err_json = err_json['error']
                openai_err_msg = err_json.get('message', "")
                openai_err_type = err_json.get('type', "")
                err_type = "openai_error"
                err_msg = openai_err_type + "," + openai_err_msg
                return response_manager.make_response2(1, ip, user_id, chat_id, messages, answer, err_type, err_msg, openai_api_key)
                #logger.error("openai_error:" + openai_err_type + "," + openai_err_msg + ",session_id:" + session_id + ",key:" + openai_api_key)
            else:
                err_type = "response_error"
                err_msg = str(e)
                return response_manager.make_response2(1, ip, user_id, chat_id, messages, answer, err_type, err_msg, openai_api_key)
        except Exception as e:
            err_type = "request_error"
            err_msg = str(e)
            return response_manager.make_response2(1, ip, user_id, chat_id, messages, answer, err_type, err_msg, openai_api_key)
    except Exception as e: # e.traceback.print_exc()
        err_type = "system_error"
        err_msg = str(e)
        return response_manager.make_response2(1, ip, user_id, chat_id, messages, answer, err_type, err_msg, openai_api_key)


def build_session_query(query, system, session_id, session_prompt_arr):
    query_dict = {"role": "user", "content": query}
    system_dict = {"role": "system", "content": system}
    session_prompt = []
    if session_prompt_arr is not None:
        session_prompt = session_prompt_arr.copy()
    session_prompt.append(query_dict)
    session_prompt.append(system_dict)
    return session_prompt


def save_session_answer(query, answer, session_id, session_prompt_arr):
    query_dict = {"role": "user", "content": query}
    answer_dict = {"role": "assistant", "content": answer}
    session_prompt = []
    if session_prompt_arr is not None:
        session_prompt = session_prompt_arr.copy()
    session_prompt.append(query_dict)
    session_prompt.append(answer_dict)
    length = len(session_prompt)
    if length > 10:
        del session_prompt[:2]
    numbers_str = json.dumps(session_prompt)
    REDIS.set(session_id, numbers_str)