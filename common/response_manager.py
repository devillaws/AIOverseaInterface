import json
from loguru import logger


def make_response(code, errType, errMsg, msg):
    res_dict = {"code": 1, "errType": None, "errMsg": None, "msg": None,
                'code': code, 'errType': errType, 'errMsg': errMsg, 'msg': msg}
    res_json = json.dumps(res_dict)
    return res_json, 200, {"Content-Type": "application/json"}
