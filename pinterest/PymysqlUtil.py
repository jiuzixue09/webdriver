import pymysql

from pinterest import LoggingUtil

log = LoggingUtil.get_logging('mysql_module')


class PymysqlUtil:

    # 初始化方法
    def __init__(self, host, port, user, passwd, dbName, charsets):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.dbName = dbName
        self.charsets = charsets

    # 链接数据库
    def getCon(self):
        log.info('connect to db')
        self.db = pymysql.Connect(
            host=self.host,
            port=self.port,
            user=self.user,
            passwd=self.passwd,
            db=self.dbName,
            charset=self.charsets
        )
        log.info('get cursor')
        self.cursor = self.db.cursor()

    # 关闭链接
    def close(self):
        log.info('close db')
        self.cursor.close()
        self.db.close()

    # 查询单行记录
    def get_first(self, sql):
        try:
            return self.get_one(sql)
        finally:
            self.close()

    # 查询单行记录
    def get_one(self, sql):
        res = None
        # noinspection PyBroadException
        try:
            self.getCon()
            self.cursor.execute(sql)
            res = self.cursor.fetchone()
        except Exception:
            log.exception('sql error, sql= %s', sql)
        return res

    # 查询列表数据
    def get_all(self, sql):
        res = None
        # noinspection PyBroadException
        try:
            self.getCon()
            self.cursor.execute(sql)
            res = self.cursor.fetchall()
        except Exception:
            log.exception('sql error, sql= %s', sql)
        finally:
            self.close()
        return res

    # 插入数据
    def __insert(self, sql):
        count = 0
        # noinspection PyBroadException
        try:
            log.info('sql:%s', sql)
            self.getCon()
            count = self.cursor.execute(sql)
            self.db.commit()
        except Exception:
            log.exception('sql error, sql= %s', sql)
            self.db.rollback()
        finally:
            self.close()
        return count

    # 修改数据
    def edit(self, sql):
        return self.__insert(sql)

    # 删除数据
    def delete(self, sql):
        return self.__insert(sql)

    # 添加数据
    def add(self, sql):
        return self.__insert(sql)
