import json
import datetime
import redis
from loguru import logger
from common import key_manager
from common.my_exception import balanceException, getApiKeyException
from common.response_manager import make_response3
import requests
from utils import mysql_util
from utils.mysql_util import add_api_log
from flask import request, Response
from utils.redis_util import REDIS
from config import setting

def chat():
    requset_json = None
    response_text = None
    ip = None
    openai_api_key = None
    authorization_key = None
    try:
        ip = request.remote_addr
        authorization_key = request.headers.get("Authorization-Key")
        check_key = mysql_util.check_key(authorization_key)
        if authorization_key is None or not check_key:
            err_type = "hearder_error"
            err_msg = "请求头的Authorization-Key不正确，请检查"
            return make_response3(1, ip, requset_json, response_text, err_type, err_msg, authorization_key, openai_api_key)
        requset_json = request.json
        if requset_json is None:
            err_type = "system_error"
            err_msg = "无法加载json或json为空，请检查request.body中的json是否正确"
            return make_response3(1, ip, requset_json, response_text, err_type, err_msg, authorization_key, openai_api_key)
        try:
            response_redis = REDIS.client_list()
        except redis.exceptions.RedisError as e:
            err_type = "redis_error"
            err_msg = "连接不上redis"
            return make_response3(1, ip, requset_json, response_text, err_type, err_msg, authorization_key, openai_api_key)
        model = requset_json.get('model', None)  # model = "gpt-3.5-turbo"
        messages = requset_json.get('messages', None)  # 必填，消息内容
        temperature = requset_json.get('temperature', 1)  # 可选，默认为1，0~2，数值越高创造性越强
        top_p = requset_json.get('top_p', None)  # 可选，默认为1，0~1，效果类似temperature，不建议都用
        n = requset_json.get('n', 1)  # 可选，默认为1，chatgpt对一个提问生成多少个回答
        stream = requset_json.get('stream', None)  # 可选，默认为False，设置为True和网页效果类似，需监听事件来解析
        stop = requset_json.get('stop', None)  # 可选，chatgpt遇到stop里的字符串时停止生成内容
        max_tokens = requset_json.get('max_tokens',None)  # 可选，默认无穷大，如果设置了，需要满足max_tokens+message_token<=4096,这是生成文本的最大长度
        presence_penalty = requset_json.get('presence_penalty', 0)  # 可选，默认为0，-2~2，越大越不允许跑题
        frequency_penalty = requset_json.get('frequency_penalty', 0)  # 可选，默认为0，-2~2，越大越不允许复读机
        logit_bias = requset_json.get('logit_bias', None)  # 可选，默认无，影响特定词汇的生成概率？
        user = requset_json.get('user', None)  # 可选，默认无，用户名
        try:
            openai_api_key = key_manager.catch_key_times()
            logger.info("选用的key:" + openai_api_key)
        except getApiKeyException as e:
            err_type = "getApiKey_error"
            err_msg = "多线程获取api失败，原因：" + str(e)
            return make_response3(1, ip, requset_json, response_text, err_type, err_msg, authorization_key, openai_api_key)
        except balanceException as e:
            err_type = "balance_error"
            err_msg = "已从key池中选出最少调用的key，但该key依旧在20秒内超过5次调用，请缓缓"
            return make_response3(1, ip, requset_json, response_text, err_type, err_msg, authorization_key, openai_api_key)
        try:
            headers = {}
            headers["Content-Type"] = "application/json; charset=UTF-8"
            headers["Authorization"] = "Bearer " + openai_api_key
            data = {}
            data["model"] = model
            data["messages"] = messages
            if temperature is not None:
                data["temperature"] = temperature
            if top_p is not None:
                data["top_p"] = top_p
            if n is not None:
                data["n"] = n
            if stream is not None:
                data["stream"] = stream
            if stop is not None:
                data["stop"] = stop
            if max_tokens is not None:
                data["max_tokens"] = max_tokens
            if presence_penalty is not None:
                data["presence_penalty"] = presence_penalty
            if frequency_penalty is not None:
                data["frequency_penalty"] = frequency_penalty
            if logit_bias is not None:
                data["logit_bias"] = logit_bias
            if user is not None:
                data["user"] = user
            url = 'https://api.openai.com/v1/chat/completions'
            proxies = {  # 针对urllib3最新版bug的手动设置代理
                'http': setting.proxies,
                'https': setting.proxies
            }
            try:
                if stream:
                    response = requests.post(url, data=json.dumps(data), headers=headers, proxies=proxies, stream=True, timeout=30)
                else:
                    response = requests.post(url, data=json.dumps(data), headers=headers, proxies=proxies, timeout=30)
                response.raise_for_status()
            except requests.exceptions.Timeout as e:
                err_type = "timeout_error"
                err_msg = "访问openai连接已超时30s,请稍后再尝试提交"
                return make_response3(1, ip, requset_json, response_text, err_type, err_msg, authorization_key, openai_api_key)
            except requests.RequestException as e:
                if e.response is not None and e.response.text is not None:
                    err_json = json.loads(e.response.text)
                    err_json = err_json['error']
                    openai_err_msg = err_json.get('message', "")
                    openai_err_type = err_json.get('type', "")
                    err_type = "openai_error"
                    err_msg = openai_err_type + "," + openai_err_msg
                    return make_response3(1, ip, requset_json, response_text, err_type, err_msg, authorization_key, openai_api_key)
                else:
                    err_type = "response_error"
                    err_msg = str(e)
                    return make_response3(1, ip, requset_json, response_text, err_type, err_msg, authorization_key, openai_api_key)
            if response.status_code == 200:
                if stream:
                    def event_stream():
                        sumline = ""
                        for line in response.iter_lines():
                            if line:
                                line = line.decode('utf-8')
                                line = line[6:].strip()
                                yield "data:{}\n\n".format(line)
                                sumline += line+","
                        add_api_log(ip, json.dumps(requset_json), sumline, 0, None, None, authorization_key, openai_api_key, datetime.datetime.now())
                        response.close()
                        logger.info("success")
                    return Response(event_stream(), mimetype="text/event-stream")
                else:
                    response_text = response.text
                    return make_response3(0, ip, requset_json, response_text, None, None, authorization_key, openai_api_key)
            else:
                if response.text is not None:
                    err_json = json.loads(response.text)
                    err_json = err_json['error']
                    openai_err_msg = err_json.get('message', "")
                    openai_err_type = err_json.get('type', "")
                    err_type = "openai_error"
                    err_msg = openai_err_type+","+openai_err_msg
                    return make_response3(1, ip, requset_json, response_text, err_type, err_msg, authorization_key, openai_api_key)
                else:
                    err_type = "openai_error"
                    err_msg = "response.text为空"
                    return make_response3(1, ip, requset_json, response_text, err_type, err_msg, authorization_key, openai_api_key)
        except Exception as e:
            err_type = "request_error"
            err_msg = str(e)
            return make_response3(1, ip, requset_json, response_text, err_type, err_msg, authorization_key, openai_api_key)
    except Exception as e: # e.traceback.print_exc()
        err_type = "system_error"
        err_msg = str(e)
        return make_response3(1, ip, requset_json, response_text, err_type, err_msg, authorization_key, openai_api_key)