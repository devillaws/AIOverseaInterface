import json
import traceback
import hashlib
import redis
from config.config import conf

config = conf()
_conn_pool = redis.ConnectionPool(
    host=config.get("redis_host", False),
    port=config.get("redis_port", False),
    username=config.get("redis_user", False),
    password=config.get("redis_pass", False),
    db=config.get("redis_db", False),
)

REDIS = redis.Redis(connection_pool=_conn_pool)

"""
redis工具类
"""


class RedisUtil(object):
    redis = REDIS
    """
    redis的key定义 属性名与属性值必须一致 属性名为大写
    """
    DAY_FUND_COMMENT = 'day_fund_comment'  # 天天基金基金评论详情数据
    DAY_FAIL_FUND_COMMENT = 'day_fail_fund_comment'  # 天天基金基金失败评论详情数据
    XUEQIU_FAIL_FUND_COMMENT = 'xueqiu_fail_fund_comment'  # 雪球基金失败评论详情数据

    DAY_BASE_PENDING_TASK = 'day_base_pending_task'  # 详情基本任务
    DAY_FAIL_PENDING_TASK = 'day_fail_pending_task'  # 失败任务

    PARSER_INTERVAL = 100  # 队列空等待时长
    ERROR_INTERVAL = 2  # 出错等待时长
    EXPIRE_SECOND = 86400  # 登录cookie过期时间

    @classmethod
    def expire(cls, key: str, ex: int):
        """
        添加过期时间
        :param key:
        :param ex:
        :return:
        """
        cls.redis.expire(key, ex)

    @classmethod
    def set(cls, key: str, value, ex=None):
        cls.redis.set(key, value, ex=ex)

    @classmethod
    def delete(cls, *names):
        cls.redis.delete(*names)

    @classmethod
    def incr(cls, key):
        cls.redis.incr(key, amount=1)

    @classmethod
    def decr(cls, key):
        cls.redis.decr(key, amount=1)

    @classmethod
    def get(cls, key: str):
        return cls.redis.get(key)

    @classmethod
    def sadd(cls, key_name: str, result: str) -> bool:
        '''
        集合去重
        :param key_name:
        :param result:
        :return:
        '''
        v = cls.redis.sadd(key_name, result)
        return True if v else False

    @classmethod
    def spop(cls, key_name: str) -> dict:
        v = cls.redis.spop(key_name)
        if v:
            return json.loads(bytes.decode(v))

    @classmethod
    def smembers(cls, key_name: str) -> set:
        s = {bytes.decode(each) for each in cls.redis.smembers(key_name)}
        return s

    @classmethod
    def sismember(cls, key_name: str, value: str) -> bool:
        return cls.redis.sismember(key_name, value)

    @classmethod
    def lpush(cls, key_name: str, **kwargs) -> bool:
        cls.redis.lpush(key_name, json.dumps(kwargs, ensure_ascii=False))
        return True

    @classmethod
    def lrange(cls, key_name: str) -> list:
        return [json.loads(bytes.decode(each)) for each in cls.redis.lrange(key_name, 0, -1)]

    @classmethod
    def rpop(cls, key_name: str) -> dict:
        try:
            assert cls.not_empty(key_name), 'Redis queue was empty.'
            _val = cls.redis.rpop(key_name).decode('utf-8')
        except Exception as e:
            print(e)
            return {}
        # Decode json object, if fail, put back.
        try:
            _val = json.loads(_val)
            return _val
        except Exception as e:
            print(e)
            cls.redis.lpush(key_name, _val)
            return {}

    @classmethod
    def not_empty(cls, key_name: str):
        length = cls.redis.llen(key_name)
        # print(f'Queue remaining: {length}')
        if length > 0:
            return True
        else:
            return False

    @classmethod
    def join(cls, key: str, *args):
        '''
        拼接redis的key
        :param key:
        :param args:
        :return:
        '''
        return key + ':' + ':'.join([i for i in args if i])

    @classmethod
    def hset(cls, name: str, key: str, value: object):
        cls.redis.hset(name, key, value)

    @classmethod
    def hget(cls, name: str, key: str) -> str:
        v = cls.redis.hget(name, key)
        return bytes.decode(v)

    @classmethod
    def hdel(cls, name: str, *key):
        cls.redis.hdel(name, *key)

    @classmethod
    def hgetall(cls, name: str) -> dict:
        raw_dict = cls.redis.hgetall(name)
        new_dict = {bytes.decode(k): json.loads(bytes.decode(v)) for k, v in raw_dict.items()}
        return new_dict

    @classmethod
    def keys(cls, msg: str):
        v = cls.redis.keys(msg)
        if v:
            return [bytes.decode(each) for each in v]
        return []

    @classmethod
    def countllen(cls, key: str) -> int:
        """
        返回数量
        """
        length = cls.redis.llen(key)
        return length


if __name__ == '__main__':
    # # RedisUtil.isin_success_task('1')
    # RedisUtil.sadd('11', {'a': ''})
    # print(RedisUtil.spop('11'))
    # print(RedisUtil.smembers('11'))
    # 8aacdb17187e6acf2b175d4aa08d7213
    # RedisUtil.incr('222')
    # RedisUtil.decr('111')
    # print(RedisUtil.get('ztc_download_token:acnestudios官方旗舰店'))
    # # RedisUtil.hgetall('ztc_crawl_task_future:skechers童鞋旗舰店:3天转化')
    # RedisUtil.delete('ztc_shop_odd_amount:skechers童鞋旗舰店')
    # print(RedisUtil.hget(RedisUtil.TMALL_SHOPID, 'ecco爱步运动旗舰店'))
    pass
