import datetime
import json
import sys
from time import sleep

import pika
import yaml

from pinterest import LoggingUtil
from pinterest import PinterestRegisterManger
from pinterest.CookieManager import CookieManager
from pinterest.PinterestLogin import PinterestLogin

logging = LoggingUtil.get_logging('rabbit_module')

with open('config.yaml') as f:
    config = yaml.safe_load(f.read())


EXCHANGE = "direct.python.pinterest.account.exchange"
Q_NAME = "direct.python.pinterest.account.queue"
R_KEY = "direct.python.pinterest.account.key"

env = 'dev'
pl = PinterestLogin()


def login(user_name, user_password, user_type):
    status_code, str_cookies = pl.get_cookie(user_name, user_password)
    manager = CookieManager(env)
    if status_code == 200:
        manager.add_cookie(user_name, str_cookies, user_type)
    elif status_code == 401:
        manager.disable_cookie(user_name, str_cookies)
    elif status_code == 429:  # 控制频率
        logging.info('登录被拒，休眠20分钟')
        sleep(20 * 60)


def register(user_name):
    str_cookies = PinterestRegisterManger.register(user_name, env)
    if str_cookies:
        CookieManager(env).add_cookie(user_name, str_cookies, 1)


def callback(ch, method, _, body):
    logging.info(str(datetime.datetime.now()), body)
    data = json.loads(body.decode('utf-8'))
    user_name = data['userName']
    user_password = data['userPassword']
    user_type = data['userType']

    if user_type != 0 or data['cookieStatus'] == -1:
        login(user_name, user_password, user_type)
    else:
        register(user_name)
    ch.basic_ack(delivery_tag=method.delivery_tag)


class PinterestAccountMq:

    def __init__(self):
        if env == 'dev':
            c = config['dev']['rabbit']
        elif env == 'prod':
            c = config['prod']['rabbit']
        else:
            raise Exception('IllegalArgumentException: env can\'t be' + env)
        logging.info('env=%s, config=%s', env, c['host'])

        user_pwd = pika.PlainCredentials(
            c["username"],
            c["password"]
        )

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=c["host"],
                port=int(c["port"]),
                virtual_host=c["virtual-host"],
                credentials=user_pwd,
                heartbeat=0
            )
        )

    def main(self):
        # noinspection PyBroadException
        try:
            channel = self.connection.channel()
            channel.queue_bind(exchange=EXCHANGE, queue=Q_NAME, routing_key=R_KEY)

            channel.basic_qos(prefetch_count=2)
            channel.basic_consume(on_message_callback=callback, queue=Q_NAME)

            print("start consuming.")
            channel.start_consuming()
        except Exception:
            logging.exception('connect failed')


if __name__ == '__main__':
    args = sys.argv[1:]
    env = args[0]
    PinterestAccountMq().main()
