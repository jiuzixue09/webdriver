import json
import sys

from flask import Flask, request

from pinterest import CookieManager as Manager, LoggingUtil
from pinterest.CookieManager import CookieManager
from pinterest.PinterestLogin import PinterestLogin
from pinterest.PinterestRecommend import PinterestImageSearch
from pinterest.PinterestSearchImprovement import PinterestSearchImprovement

app = Flask(__name__)
logging = LoggingUtil.get_logging()

env = 'dev'


@app.route('/pinterest/recommend')
def recommend():
    set_cookie, cookie = get_cookie(request)

    keyword = request.args.get("keyword")
    keywords = PinterestImageSearch(cookie).get_recommend(keyword)

    rs = {'status': 200}
    if keywords:
        rs['keywords'] = keywords
    else:
        rs['status'] = 500

    return Manager.get_cookie_resp(cookie, json.dumps(rs)) if set_cookie else rs


def get_cookie(req):
    set_cookie = False
    if not Manager.cookie_exist(req):
        cookie = CookieManager(env).pick_up_cookie()
        set_cookie = True
    else:
        cookie = Manager.get_cookie(req)
    return set_cookie, cookie


@app.route('/pinterest/improvement')
def improvement():
    set_cookie, cookie = get_cookie(request)

    keyword = request.args.get("keyword")
    keywords = PinterestSearchImprovement(cookie).get_recommend(keyword)
    rs = {'status': 200}
    if keywords:
        rs['keywords'] = keywords
    else:
        rs['status'] = 500

    return Manager.get_cookie_resp(cookie, json.dumps(rs)) if set_cookie else rs


@app.route('/pinterest/login')
def login():
    user_name = request.args.get("user_name")
    user_password = request.args.get("user_password")
    str_cookies = PinterestLogin().get_cookie(user_name, user_password)
    rs = {'status': 200}
    if str_cookies:
        rs['cookies'] = str_cookies
        CookieManager(env).add_cookie(user_name, str_cookies)
    else:
        rs['status'] = 500

    return rs


@app.route('/pinterest/cookie')
def pick_up_cookie():
    cookie_type = request.args.get("type")
    rs = {'status': 500}

    for i in range(2):
        cookie = CookieManager(env).pick_up_cookie(cookie_type)
        if cookie:
            rs['status'] = 200
            rs['cookies'] = cookie
            break

    return rs


if __name__ == "__main__":
    args = sys.argv[1:]
    env = args[0]
    app.run(host='0.0.0.0')
