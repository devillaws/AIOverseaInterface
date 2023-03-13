import threading
import time
from collections import deque
from loguru import logger
from flask import logging
import json
from common import response_manager
from common.my_exception import getApiKeyException, balanceException

lock = threading.Lock()

key_times = {}

key_time_deque = {}


def catch_key_times():
    start_time = time.time()
    lock.acquire()
    global key_times
    global key_time_deque
    # 在修改全局变量之前，获取锁
    try:
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
            key_times[min_key] += 1
            return min_key
        elif len(call_time_list) >= 5:
            for i in range(1, 5):  # i 不能
                new = call_time_list[-i]
                old = call_time_list[-i - 1]
                sum_dec += abs(new - old)
            sum_dec += call_time - call_time_list[-1]
            if sum_dec < 20:
                logger.error("balance_error:已从key池中选出最少调用的key，但该key依旧在20秒内超过5次调用，请缓缓")
                raise balanceException(
                    "balance_error:已从key池中选出最少调用的key，但该key依旧在20秒内超过5次调用，请缓缓")
            else:
                key_times[min_key] += 1
                call_time_list.append(call_time)
                key_time_deque[min_key] = call_time_list
                return min_key
        else:
            call_time_list.append(call_time)
            key_time_deque[min_key] = call_time_list
            key_times[min_key] += 1
            return min_key
    except Exception as e:
        logger.error("getApiKey_error:多线程获取api失败，原因：" + str(e))
        raise getApiKeyException(str(e))
    finally:
        # 释放锁
        lock.release()
        end_time = time.time()
        logger.info("取锁耗时：" + str(abs(end_time-start_time)))
