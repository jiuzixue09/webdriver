import json
import sys
from queue import Queue

from flask import Flask, request

from pinterest import CookieManager as Manager, LoggingUtil
from pinterest.CookieManager import CookieManager
from pinterest.PinterestLogin import PinterestLogin
from pinterest.PinterestRecommend import PinterestImageSearch
from pinterest.PinterestRegisterManger import PinterestRegisterManger
from pinterest.PinterestSearchImprovement import PinterestSearchImprovement

app = Flask(__name__)
logging = LoggingUtil.get_logging()

env = 'dev'
browsers = Queue()
browser_size, max_browser_size = 0, 5


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


def open_browser():
    if ++browser_size < max_browser_size:
        b = PinterestRegisterManger(env)
        browsers.put(b)
        return b


def close_browser(p: PinterestRegisterManger):
    try:
        p.close()
    except Exception as e:
        logging.error('close browser error', e)
    finally:
        open_browser()


def browser():
    PinterestRegisterManger(env)


@app.route('/pinterest/register')
def register():
    rs = {'status': 200}
    try:
        p = browsers.get(timeout=5)
    except:
        p = open_browser()
        if p is None:
            rs['status'] = 300
            rs['message'] = 'too many connection'
            return

    try:
        user_name = request.args.get("user_name")
        p.register(user_name)
        browsers.put(p)
    except Exception as e:
        logging.error('register error', e)
        close_browser(p)


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
    open_browser()
    app.run(host='0.0.0.0')
