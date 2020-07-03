import yaml

from pinterest import LoggingUtil
from pinterest.PymysqlUtil import PymysqlUtil

with open('config.yaml') as f:
    config = yaml.safe_load(f.read())
logging = LoggingUtil.get_logging()


class PinterestAccountMysql:

    def __init__(self, env):
        if env == 'dev':
            c = config['dev']['mysql']
        elif env == 'prod':
            c = config['prod']['mysql']
        else:
            raise Exception('IllegalArgumentException: env can\'t be' + env)
        logging.info('env=%s, config=%s', env, c['host'])
        self.mysql = PymysqlUtil(c['host'], c['port'], c['username'], c['password'], c['dbname'], c['charsets'])

    def update_cookie(self, user_name, cookie, user_status, cookie_status, user_type=None):
        if user_type:
            sql = 'update account_cookie set cookies=\'{}\',cookie_status={}, user_status={},user_type={}, ' \
                  'update_at=now() where user_name=\'{}\''.format(cookie, cookie_status, user_status, user_type,
                                                                  user_name)
        else:
            sql = 'update account_cookie set cookies=\'{}\',cookie_status={}, user_status={},update_at=now() where ' \
                       'user_name=\'{}\''.format(cookie, cookie_status, user_status, user_name)
        return self.mysql.edit(sql)
