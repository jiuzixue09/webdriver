import base64
import sys

from flask import Flask, request
from flask_cors import CORS

from pinterest import LoggingUtil
from pinterest.CookieManager import CookieManager
from pinterest.PinterestLogin import PinterestLogin

app = Flask(__name__)
CORS(app)
logging = LoggingUtil.get_logging()

env = 'dev'


@app.route('/pinterest/login')
def login():
    user_type = request.args.get("type")
    user_name = request.args.get("user_name")
    user_password = request.args.get("user_password")
    status_code, str_cookies = PinterestLogin().get_cookie(user_name, user_password)
    rs = {'status': status_code}
    if status_code == 200:
        rs['cookies'] = str_cookies
        CookieManager(env).add_cookie(user_name, str_cookies, user_type)

    return rs


@app.route('/pinterest/cookie')
def pick_up_cookie():
    user_type = request.args.get("type")
    name = request.args.get("name")
    rs = {'status': 500}

    for i in range(2):
        key, cookie = CookieManager(env).pick_up_cookie(user_type, name)
        if cookie:
            rs['status'] = 200
            rs['cookies'] = cookie
            rs['name'] = key
            break

    return rs


@app.route('/pinterest/user')
def pick_up_user():
    user_type = request.args.get("type")
    rs = {'status': 500}

    for i in range(2):
        key, cookie = CookieManager(env).pick_up_cookie(user_type)
        if cookie:
            rs['status'] = 200
            name = base64.b64encode(key.encode('utf-8'))
            rs['name'] = str(name, encoding="utf-8")

            break

    return rs


if __name__ == "__main__":
    args = sys.argv[1:]
    env = args[0]
    app.run(host='0.0.0.0')
