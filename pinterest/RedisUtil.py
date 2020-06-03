import redis

from pinterest import LoggingUtil

log = LoggingUtil.get_logging('redis_module')


class RedisUtil:

    def __init__(self, host, port, password=None):
        self.__pool = redis.ConnectionPool(host=host, port=port, password=password)

    # 保存数据
    # expire：过期时间，单位秒
    def r_set(self, key, value, expire=None):
        log.info('add key: %s', key)
        redi = redis.Redis(connection_pool=self.__pool)
        redi.set(key, value, ex=expire)

    def r_keys(self, pattern):
        redi = redis.Redis(connection_pool=self.__pool)
        keys = redi.keys(pattern)
        keys = [key.decode("UTF-8") for key in keys]
        return keys

    # 获取数据
    def r_get(self, key):
        redi = redis.Redis(connection_pool=self.__pool)
        value = redi.get(key)
        if value is None:
            return None
        value = value.decode("UTF-8")
        return value

    def r_smembers(self, name):
        redi = redis.Redis(connection_pool=self.__pool)
        value = redi.smembers(name)
        if value is None:
            return None
        value = [v.decode("UTF-8") for v in value]
        return value

    def r_sadd(self, name, item):
        redi = redis.Redis(connection_pool=self.__pool)
        redi.sadd(name, item)

    def r_srandmember(self, name, number=1):
        redi = redis.Redis(connection_pool=self.__pool)
        srandmember = redi.srandmember(name, number)
        member = [v.decode("UTF-8") for v in srandmember]
        return member

    # 删除数据
    def r_del(self, key):
        log.info('delete key %s', key)
        redi = redis.Redis(connection_pool=self.__pool)
        redi.delete(key)
