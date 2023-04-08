import json
import datetime
from loguru import logger
from utils.mysql_util import add_chat_log, add_api_log


def make_response(code, errType, errMsg, msg):
    res_dict = {"code": 1, "errType": None, "errMsg": None, "msg": None,
                'code': code, 'errType': errType, 'errMsg': errMsg, 'msg': msg}
    res_json = json.dumps(res_dict)
    return res_json, 200, {"Content-Type": "application/json"}


def make_response2(code, ip, user_id, chat_id, query, msg, errType, errMsg, select_api_key):
    res_dict = {'code': code,
                'ip': ip,
                'userId': user_id,
                'chatId': chat_id,
                'query': query,
                'msg': msg,
                'errType': errType,
                'errMsg': errMsg
                }
    if code == 1:
        logger.error(errType + ":" + errMsg)
    else:
        logger.info("success")
    add_chat_log(ip, user_id, chat_id, query, msg, code, errType, errMsg, select_api_key, datetime.datetime.now())
    res_json = json.dumps(res_dict)
    return res_json, 200, {"Content-Type": "application/json"}


def make_response3(code, ip, request_dict, response_text, err_type, err_msg, Authorization_key, select_api_key):
    request_str = None
    response_json = None
    if request_dict:
        request_str = json.dumps(request_dict, ensure_ascii=False)
    add_api_log(ip, request_str, response_text, code, err_type, err_msg, Authorization_key, select_api_key, datetime.datetime.now())
    if response_text:
        response_json = json.loads(response_text)
    res_dict = {
        'msg': response_json,
        'err_type': err_type,
        'err_msg': err_msg
    }
    res_json = json.dumps(res_dict)
    headers = {"Content-Type": "application/json; charset=utf-8"}
    if code == 1:
        logger.error(err_type + ":" + err_msg)
        return res_json, 400, {"Content-Type": "application/json;charset=utf-8"}
    else:
        logger.info("success")
        return res_json, 200, {"Content-Type": "application/json;charset=utf-8"}
