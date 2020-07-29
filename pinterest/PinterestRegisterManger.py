import json
from queue import Queue

import requests
import yaml

from pinterest import LoggingUtil
from pinterest.PinterestRegister import PinterestRegister

with open('config.yaml') as f:
    config = yaml.safe_load(f.read())
logging = LoggingUtil.get_logging()

browsers = Queue()
browser_size, max_browser_size = 0, 2


def open_browser(env):
    global browser_size
    if browser_size < max_browser_size:
        # noinspection PyBroadException
        try:
            b = PinterestRegisterManger(env)
            browsers.put(b)
            browser_size += 1
            return b
        except Exception:
            logging.exception('open browser error')


def register(user_name, env):
    # noinspection PyBroadException
    try:
        p = browsers.get(timeout=5)
    except Exception:
        p = open_browser(env)
        if p is None:
            return p
    # noinspection PyBroadException
    try:
        str_cookies = p.process(user_name)
        if str_cookies:
            browsers.put(p)
            return str_cookies
    except Exception:
        logging.exception('register error')
        close_browser(p, env)


def close_browser(p, env):
    # noinspection PyBroadException
    try:
        p.close()
    except Exception:
        logging.exception('close browser error')
    finally:
        open_browser(env)


class PinterestRegisterManger:

    def __init__(self, env):
        # noinspection PyBroadException
        try:
            c = config[env]['webdriver']
        except Exception:
            raise Exception('IllegalArgumentException: env can\'t be' + env)

        self.cookie_url = config[env]['redis']['api']['cookie']
        logging.info('env=%s, config=%s', env, c)

        self.p = PinterestRegister(c['hide_browser'], c['path'])
        self.env = env

    def process(self, user_name):
        # self.p.delete_all_cookies()
        request_url = self.cookie_url + "?name=" + user_name
        logging.info('request_url=%s', request_url)
        content = requests.get(request_url).content.decode('utf-8')

        if not content:
            logging.info('can\'t find user: %s' % user_name)
            raise Exception('can\'t find user:{}'.format(user_name))

        j = json.loads(content)
        if not j or 'cookies' not in j:
            logging.info('can\'t find user: %s' % user_name)
            raise Exception('can\'t find user:{}'.format(user_name))
        cookie = j['cookies']
        for i in range(3):
            # noinspection PyBroadException
            try:
                n_cookie = self.p.get_cookie(cookie)
                if n_cookie:
                    return n_cookie
            except Exception:
                logging.exception('error')

    def close(self):
        self.p.close()
