import requests
import yaml

from pinterest import LoggingUtil

logging = LoggingUtil.get_logging()


with open('config.yaml') as f:
    config = yaml.safe_load(f.read())


class CookieManager:

    def __init__(self, env):
        try:
            self.account_url = config[env]['db']['api']['account']
            self.cookie_url = config[env]['redis']['api']['cookie']
        except Exception:
            logging.exception('config error: ')

    def add_cookie(self, user_name, cookie, user_type):
        # noinspection PyBroadException
        try:
            url = self.account_url + '/' + user_name
            params = {'cookie': cookie, 'user_status': 1, 'cookie_status': 1, 'user_name': user_name,
                      "user_type": user_type}

            requests.post(self.cookie_url, json=params)  # put the cookie to redis
            resp = requests.post(url, json=params)  # put the account info to database
            logging.info('user_name=%s, rs=%s', user_name, resp.content.decode("utf-8"))
        except Exception:
            logging.exception('add cookie error: ')

    def disable_cookie(self, user_name, cookie):
        # noinspection PyBroadException
        try:
            url = self.account_url + '/' + user_name
            params = {'cookie': cookie, 'user_status': 0, 'cookie_status': 0}
            resp = requests.post(url, json=params)
            logging.info('user_name=%s, rs=%s', user_name, resp.content.decode("utf-8"))
        except Exception:
            logging.exception('add cookie error: ')
