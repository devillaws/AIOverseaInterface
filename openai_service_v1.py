import json
import flask
import openai
import requests
from flask import Flask, redirect, render_template, request, url_for, logging


def gpt35turbo():
    res_dict = {
        "code": 1,
        "errType": None,
        "errMsg": None,
        "msg": None
    }

    try:
        authorization_key = flask.request.headers.get("Authorization-Key")
        if flask.request.json is None or authorization_key is None or authorization_key != "BIGBOSS@510630":
            res_dict['errType'] = "request"
            res_dict['errMsg'] = "请求头key不正确，或入参json不存在，请检查请求"
            res_json = json.dumps(res_dict)
            return res_json, 200, {"Content-Type": "application/json"}
        model = flask.request.json.get('model', "gpt-3.5-turbo")  # 必要，模型名字
        open_api_key = flask.request.json.get('open_api_key', None)
        messages = flask.request.json.get('messages', None)  # 必填，消息内容
        temperature = flask.request.json.get('temperature', 1)  # 可选，默认为1，0~2，数值越高创造性越强
        top_p = flask.request.json.get('top_p', 1)  # 可选，默认为1，0~1，效果类似temperature，不建议都用
        n = flask.request.json.get('n', 1)  # 可选，默认为1，chatgpt对一个提问生成多少个回答
        stream = flask.request.json.get('stream', False)  # 可选，默认为False，设置为True和网页效果类似，需监听事件来解析
        stop = flask.request.json.get('stop', None)  # 可选，chatgpt遇到stop里的字符串时停止生成内容
        max_tokens = flask.request.json.get('max_tokens', 2048)  # 可选，默认无穷大，如果设置了，需要满足max_tokens+message_token<=4096
        presence_penalty = flask.request.json.get('presence_penalty', 0)  # 可选，默认为0，-2~2，越大越不允许跑题
        frequency_penalty = flask.request.json.get('frequency_penalty', 0)  # 可选，默认为0，-2~2，越大越不允许复读机
        logit_bias = flask.request.json.get('logit_bias', None)  # 可选，默认无，影响特定词汇的生成概率？
        user = flask.request.json.get('user', None)  # 可选，默认无，用户名
        tran_ascii = flask.request.json.get('tran_ascii', 0)

        try:
            openai.api_key = open_api_key
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature,
                stream=stream,
                max_tokens=max_tokens,
                presence_penalty=presence_penalty,
                frequency_penalty=frequency_penalty
            )
            # headers = {"Content-Type": "application/json; charset=UTF-8",
            #            "Authorization": "Bearer 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"}
            # data = {
            #     "model": "gpt-3.5-turbo",
            #     "temperature": 0.9,
            #     "messages": [
            #         {"role": "system", "content": "你是一个小助手"},
            #         {"role": "user", "content": "我是孙悟空"},
            #         {"role": "assistant", "content": "你好,悟空"},
            #         {"role": "user", "content": "今天师傅有没有被抓走？"}
            #     ]
            # }
            # url = 'https://api.openai.com/v1/chat/completions'
            # proxies = {  # 针对urllib3最新版bug的手动设置代理
            #     'http': 'http://127.0.0.1:2080',
            #     'https': 'http://127.0.0.1:2080'
            # }
            # response = requests.post(url, data=data, headers=headers, proxies=proxies)
            # print(response)
        except Exception as e:
            print(str(e))
            res_dict["code"] = 1
            res_dict["errType"] = "openai"
            res_dict['errMsg'] = str(e)
            res_json = json.dumps(res_dict)
            return res_json, 200, {"Content-Type": "application/json"}

        # text = response['choices'][0]['message']['content']
        # [choice.message.content for choice in response.choices]
        res_dict["code"] = 0
        res_dict['msg'] = response
        res_json = json.dumps(res_dict)
        return res_json, 200, {"Content-Type": "application/json"}

    except Exception as e:
        print(str(e))
        res_dict["code"] = 1
        res_dict["errType"] = "system"
        res_dict['errMsg'] = str(e)
        res_json = json.dumps(res_dict)
        return res_json, 200, {"Content-Type": "application/json"}
