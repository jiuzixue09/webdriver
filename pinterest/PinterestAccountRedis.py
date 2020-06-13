import yaml

from pinterest import LoggingUtil
from pinterest.RedisUtil import RedisUtil

with open('config.yaml') as f:
    config = yaml.safe_load(f.read())
logging = LoggingUtil.get_logging('webdriver_module')

redis_pre_key = 'pinterest:cookie:'
redis_account_key = 'pinterest:accounts'


class PinterestAccountRedis:

    def __init__(self, env):
        if env == 'dev':
            c = config['dev']['redis']
        elif env == 'prod':
            c = config['prod']['redis']
        else:
            raise Exception('IllegalArgumentException: env can\'t be' + env)
        logging.info('env=%s, config=%s', env, c['host'])
        self.redis = RedisUtil(c['host'], c['port'], c['password'])

    def add_cookie(self, user_name, cookie):
        logging.info('add cookie for user: %s', user_name)
        self.redis.r_set(self.g_key(user_name), cookie, 60 * 60 * 24 * 7 * 2)
        self.redis.r_sadd(redis_account_key, user_name)

    def remove_cookie(self, user_name):
        self.redis.r_srem(redis_account_key, user_name)

    def get_keys(self):
        keys = self.redis.r_keys(redis_pre_key + '*')
        return keys

    def r_get(self, key: str):
        if not key.startswith(redis_pre_key):
            key = redis_pre_key + key
        return self.redis.r_get(key)

    @staticmethod
    def g_key(key):
        return redis_pre_key + key

    def get_random_cookie(self):
        try:
            for i in range(5):
                key = self.redis.r_srandmember(redis_account_key)[0]
                data = self.r_get(self.g_key(key))
                if data:
                    return key, data
        except Exception as e:
            logging.exception('error')
            return None
