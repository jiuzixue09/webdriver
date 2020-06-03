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


def login(user_name, user_password):
    str_cookies = pl.get_cookie(user_name, user_password)
    if str_cookies:
        CookieManager(env).add_cookie(user_name, str_cookies)


def register(user_name):
    str_cookies = PinterestRegisterManger.register(user_name, env)
    if str_cookies:
        CookieManager(env).add_cookie(user_name, str_cookies)


def callback(ch, method, properties, body):
    print(str(datetime.datetime.now()), body)
    req = json.loads(body.decode('utf-8'))
    user_name = req['user_name']
    user_password = req['user_password']
    login(user_name, user_password)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    sleep(2)


class PinterestAccountMq:

    def __init__(self, env):
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
        try:
            channel = self.connection.channel()
            channel.queue_bind(exchange=EXCHANGE, queue=Q_NAME, routing_key=R_KEY)

            channel.basic_qos(prefetch_count=2)
            channel.basic_consume(on_message_callback=callback, queue=Q_NAME)

            print("start consuming.")
            channel.start_consuming()
        except Exception as e:
            print(str(e))
            print('connect failed')


if __name__ == '__main__':
    args = sys.argv[1:]
    env = args[0]
    PinterestAccountMq(env).main()

