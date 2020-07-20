import requests
import yaml

from pinterest import LoggingUtil
from pinterest.PinterestAccountRedis import PinterestAccountRedis

max_age = 7 * 24 * 60 * 60
logging = LoggingUtil.get_logging()


with open('config.yaml') as f:
    config = yaml.safe_load(f.read())


class CookieManager:

    def __init__(self, env):
        self.url = config[env]['account']['update']['api']
        self.p = PinterestAccountRedis(env)

    def add_cookie(self, user_name, cookie, user_type=None):
        # noinspection PyBroadException
        try:
            url = self.url + '/' + user_name
            params = {'cookie': cookie, 'user_status': 1, 'cookie_status': 1}
            if user_type:
                params['user_type'] = user_type

            resp = requests.post(url, json=params)
            logging.info('user_name=%s, rs=%s', user_name, resp.content.decode("utf-8"))
        except Exception:
            logging.exception('add cookie error: ')

    def disable_cookie(self, user_name, cookie):
        # noinspection PyBroadException
        try:
            # self.p.remove_cookie(user_name)

            url = self.url + '/' + user_name
            params = {'cookie': cookie, 'user_status': 0, 'cookie_status': 0}
            resp = requests.post(url, json=params)
            logging.info('user_name=%s, rs=%s', user_name, resp.content.decode("utf-8"))
        except Exception:
            logging.exception('add cookie error: ')
