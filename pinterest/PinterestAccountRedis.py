from random import Random

import yaml

from pinterest import LoggingUtil
from pinterest.RedisUtil import RedisUtil

with open('config.yaml') as f:
    config = yaml.safe_load(f.read())
logging = LoggingUtil.get_logging('webdriver_module')

pre_key = 'pinterest:cookie:'


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
        self.redis.r_set(self.g_key(user_name), cookie, 60 * 60 * 24 * 7)

    def get_keys(self):
        keys = self.redis.r_keys(pre_key + '*')
        return keys

    def r_get(self, key: str):
        if not key.startswith(pre_key):
            key = pre_key + key
        return self.redis.r_get(key)

    @staticmethod
    def g_key(key):
        return pre_key + key

    def get_random_cookie(self):
        keys = self.get_keys()
        if keys:
            try:
                key = keys[Random().randint(0, len(keys) - 1)]
                key = key.replace(pre_key, '')
                return key, self.r_get(key)
            except Exception as e:
                logging.info('error', e)
                return None
        else:
            return None

