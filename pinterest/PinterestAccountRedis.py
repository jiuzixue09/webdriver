import yaml

from pinterest import LoggingUtil
from pinterest.RedisUtil import RedisUtil

with open('config.yaml') as f:
    config = yaml.safe_load(f.read())
logging = LoggingUtil.get_logging('redis_module')

redis_cookie_pre_key = 'pinterest:cookie:'  # 存储登录后的cookie
redis_account_key = 'pinterest:accounts'  # 存储用户名


def g_key(key):
    if not key.startswith(redis_cookie_pre_key):
        key = redis_cookie_pre_key + key
    return key


class PinterestAccountRedis:
    two_weeks = 60 * 60 * 24 * 30

    def __init__(self, env):
        c = config[env]['redis']
        if not c:
            raise Exception('IllegalArgumentException: env can\'t be' + env)

        logging.info('env=%s, config=%s', env, c['host'])
        self.redis = RedisUtil(c['host'], c['port'], c['password'])

    def add_cookie(self, user_name, cookie, user_type):
        logging.info('add cookie for user: %s', user_name)

        self.redis.r_set(g_key(user_name), cookie, self.two_weeks)
        self.redis.r_sadd(redis_account_key, user_name)
        self.redis.r_sadd(redis_account_key + ':' + str(user_type), user_name)

    def remove_cookie(self, user_name):
        self.redis.r_srem(redis_account_key, user_name)
        [self.redis.r_srem(key, user_name) for key in self.redis.r_keys(redis_account_key + ':*')]

    def r_get(self, key: str):
        return self.redis.r_get(g_key(key))

