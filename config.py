from utils.redis_util import REDIS
from utils.mysql_util import connection_pool


class Config(object):
    SECRET_KEY = 'BIGBOSS@510630'


class Dev(Config):
    SESSION_TYPE = 'redis'  # session类型为redis
    SESSION_REDIS = REDIS
    SESSION_KEY_PREFIX = 'bigboss:'  # 保存到session中的值的前缀
    SESSION_USE_SIGNER = 'BIGBOSS@510630'  # 是否对发送到浏览器上session的cookie值进行加密
    # PERMANENT_SESSION_LIFETIME = timedelta()
    SESSION_PERMANENT = True  # 如果设置为True，则关闭浏览器session就失效。
    SECRET_KEY = 'bigboss-secret-key'
    MYSQL_POOL = connection_pool
    DEBUG = True


class Pro(Config):
    SESSION_TYPE = 'redis'  # session类型为redis
    SESSION_REDIS = REDIS
    SESSION_KEY_PREFIX = 'bigboss:'  # 保存到session中的值的前缀
    SESSION_USE_SIGNER = 'BIGBOSS@510630'  # 是否对发送到浏览器上session的cookie值进行加密
    # PERMANENT_SESSION_LIFETIME = timedelta()
    SESSION_PERMANENT = True  # 如果设置为True，则关闭浏览器session就失效。
    SECRET_KEY = 'bigboss-secret-key'
    MYSQL_POOL = connection_pool
    DEBUG = False


config = {"Dev": Dev, "Pro": Pro}
