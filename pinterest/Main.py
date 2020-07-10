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


if __name__ == "__main__":
    args = sys.argv[1:]
    env = args[0]
    app.run(host='0.0.0.0')
