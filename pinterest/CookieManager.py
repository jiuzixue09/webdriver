from pinterest import LoggingUtil
from pinterest.PinterestAccountMysql import PinterestAccountMysql
from pinterest.PinterestAccountRedis import PinterestAccountRedis

max_age = 7 * 24 * 60 * 60
logging = LoggingUtil.get_logging()


class CookieManager:

    def __init__(self, env):
        self.p = PinterestAccountRedis(env)
        self.m = PinterestAccountMysql(env)

    def pick_up_cookie(self, user_type=None, name=None):
        if name:
            return name, self.p.r_get(name)
        return self.p.get_random_cookie(user_type)

    def add_cookie(self, user_name, cookie, user_type=None):
        try:
            self.p.add_cookie(user_name, cookie, user_type)
            self.m.update_cookie(user_name, cookie, 1, 1, user_type)
        except Exception as e:
            logging.exception('add cookie error: ')

    def disable_cookie(self, user_name, cookie):
        try:
            self.p.remove_cookie(user_name)
            self.m.update_cookie(user_name, cookie, 0, 0)
        except Exception as e:
            logging.exception('add cookie error: ')
