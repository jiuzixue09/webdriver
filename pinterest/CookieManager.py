from flask import Response

from pinterest import LoggingUtil
from pinterest.PinterestAccountMysql import PinterestAccountMysql
from pinterest.PinterestAccountRedis import PinterestAccountRedis

max_age = 7 * 24 * 60 * 60

logging = LoggingUtil.get_logging()


def get_cookie(request):
    list_cookies = [k + '=' + v for k, v in request.cookies.items()]
    str_cookie = ';'.join(list_cookies)
    return str_cookie


def cookie_exist(request):
    request_cookies = request.cookies
    return True if len(request_cookies) > 0 and request_cookies.get('_pinterest_sess') else False


def get_cookie_resp(cookie, content):
    res = Response(content, content_type='application/json')
    for c in cookie.split(';'):
        kv = c.split('=', 1)
        k, v = kv[0], kv[1]
        res.set_cookie(k, v, max_age)
    return res


class CookieManager:

    def __init__(self, env):
        self.p = PinterestAccountRedis(env)
        self.m = PinterestAccountMysql(env)

    def pick_up_cookie(self, cookie_type=None, name=None):
        if name:
            return name, self.p.r_get(name)
        return self.p.get_random_cookie()

    def add_cookie(self, user_name, cookie):
        try:
            self.p.add_cookie(user_name, cookie)
            self.m.update_cookie(user_name, cookie, 1, 1)
        except Exception as e:
            logging.error('add cookie error: ', e)
