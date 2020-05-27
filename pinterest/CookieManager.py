from flask import Response

from pinterest.PinterestAccountMysql import PinterestAccountMysql
from pinterest.PinterestAccountRedis import PinterestAccountRedis


def get_cookie(request):
    list_cookies = [k + '=' + v for k, v in request.cookies.items()]
    str_cookie = ';'.join(list_cookies)
    return str_cookie


def cookie_exist(request):
    request_cookies = request.cookies
    return True if len(request_cookies) > 0 and request_cookies['_pinterest_sess'] else False


def get_cookie_resp(cookie, content):
    res = Response(content, content_type='application/json')
    for c in cookie.split(';'):
        kv = c.split('=', 1)
        k, v = kv[0], kv[1]
        res.set_cookie(k, v)
    return res


class CookieManager:

    def __init__(self, env):
        self.p = PinterestAccountRedis(env)
        self.m = PinterestAccountMysql(env)

    def pick_up_cookie(self, cookie_type=None):
        return self.p.get_random_cookie()

    def add_cookie(self, user_name, cookie):
        self.p.add_cookie(user_name, cookie)
        self.m.update_cookie(user_name, cookie, 1, 1)
