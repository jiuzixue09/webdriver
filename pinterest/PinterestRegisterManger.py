

import yaml

from pinterest import LoggingUtil
from pinterest.PinterestAccountRedis import PinterestAccountRedis
from pinterest.PinterestRegister import PinterestRegister

with open('config.yaml') as f:
    config = yaml.safe_load(f.read())
logging = LoggingUtil.get_logging()


class PinterestRegisterManger:

    def __init__(self, env):
        if env == 'dev':
            c = config['dev']['webdriver']
        elif env == 'prod':
            c = config['prod']['webdriver']
        else:
            raise Exception('IllegalArgumentException: env can\'t be' + env)
        logging.info('env=%s, config=%s', env, c)
        self.redis = PinterestAccountRedis(env)

        self.p = PinterestRegister(c['hide_browser'], c['path'])

    def register(self, user_name):
        self.p.delete_all_cookies()
        cookie = self.redis.r_get(user_name)
        if not cookie:
            logging.info('can\'t find user: %s' % user_name)
            raise Exception('can\'t find user:{}'.format(user_name))
        for i in range(3):
            try:
                n_cookie = self.p.get_cookie(cookie)
                if n_cookie:
                    return n_cookie
            except Exception as e:
                logging.error('error', e)

    def close(self):
        self.p.close()
