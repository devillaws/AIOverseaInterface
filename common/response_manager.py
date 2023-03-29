import json
import datetime

from loguru import logger

from utils.mysql_util import add_chat_log


def make_response(code, errType, errMsg, msg):
    res_dict = {"code": 1, "errType": None, "errMsg": None, "msg": None,
                'code': code, 'errType': errType, 'errMsg': errMsg, 'msg': msg}
    res_json = json.dumps(res_dict)
    return res_json, 200, {"Content-Type": "application/json"}


def make_response2(code, ip, user_id, chat_id, query, msg, errType, errMsg):
    res_dict = {'code': code,
                'ip': ip,
                'userId': user_id,
                'chatId': chat_id,
                'query': query,
                'msg': msg,
                'errType': errType,
                'errMsg': errMsg,
                'createTime': datetime.datetime.now()}
    if code == 1:
        logger.error(errType + ":" + errMsg)
    else:
        logger.info("success")
    add_chat_log(ip, user_id, chat_id, query, msg, code, errType, errMsg, datetime.datetime.now())
    res_json = json.dumps(res_dict)
    return res_json, 200, {"Content-Type": "application/json"}
