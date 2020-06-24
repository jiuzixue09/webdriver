from queue import Queue

import yaml

from pinterest import LoggingUtil
from pinterest.PinterestAccountRedis import PinterestAccountRedis
from pinterest.PinterestRegister import PinterestRegister

with open('config.yaml') as f:
    config = yaml.safe_load(f.read())
logging = LoggingUtil.get_logging()

browsers = Queue()
browser_size, max_browser_size = 0, 5


def open_browser(env):
    global browser_size
    if browser_size < max_browser_size:
        try:
            b = PinterestRegisterManger(env)
            browsers.put(b)
            browser_size += 1
            return b
        except Exception as e:
            logging.exception('open browser error')


def register(user_name, env):
    try:
        p = browsers.get(timeout=5)
    except:
        p = open_browser(env)
        if p is None:
            return p

    try:
        str_cookies = p.process(user_name)
        if str_cookies:
            browsers.put(p)
            return str_cookies
    except Exception as e:
        logging.exception('register error')
        close_browser(p, env)


def close_browser(p, env):
    try:
        p.close()
    except Exception as e:
        logging.exception('close browser error')
    finally:
        open_browser(env)


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
        self.env = env

    def process(self, user_name):
        # self.p.delete_all_cookies()
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
                logging.exception('error')

    def close(self):
        self.p.close()


