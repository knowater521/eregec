import sqlite3
import config
import utils as api

class DBApi:
    def __init__(self, table):
        self.sql = ''
        self.table = table
        self._data = []

    def select(self, *args):
        sql = ' SELECT '
        is_frist = True
        for arg in args:
            if is_frist:
                is_frist = False
            else:
                sql += ', '
            sql += arg
        sql += ' FROM {} '.format(self.table)
        self.sql = sql
        return self

    def where(self, **kwargs):
        sql = ' WHERE '
        is_frist = True
        for k, v in kwargs.items():
            v = '"' + v + '"' if type(v) == type('') else str(v)
            if is_frist:
                is_frist = False
            else:
                sql += ' AND '
            sql += k + '=' + v
        sql += ' '
        self.sql += sql
        return self

    def update(self, **kwargs):
        sql = ' UPDATE {} SET '.format(self.table)
        is_frist = True
        for k, v in kwargs.items():
            v = '"' + v + '"' if type(v) == type('') else str(v)
            if is_frist:
                is_frist = False
            else:
                sql += ', '
            sql += k + '=' + v
        sql += ' '
        self.sql = sql
        return self

    def insert(self, **kwargs):
        sql = ' INSERT INTO {} '.format(self.table)
        k_sql, v_sql = '(', '('
        is_frist = True
        for k, v in kwargs.items():
            v = '"' + v + '"' if type(v) == type('') else str(v)
            if is_frist:
                is_frist = False
            else:
                v_sql += ', '
                k_sql += ', '
            k_sql += k
            v_sql += v
        v_sql += ') '
        k_sql += ') '
        self.sql = sql + k_sql + ' VALUES ' + v_sql
        return self

    def delete(self):
        self.sql = 'DELETE FROM {} '.format(self.table)
        return self

    def execute(self, raise_error=False):
        api.pinfo('sqlite execute: {}'.format(self.sql))
        self._data = []
        try:
            conn = sqlite3.connect(config.sqlite3_database_file)
            ret = conn.execute(self.sql)
        except Exception as e:
            api.pwarning('SQLite3 execute failed: {} [{}]'.format(e, self.sql))
            conn.close()
            if raise_error:
                raise
            return False

        for v in ret:
            self._data.append(v)

        if self._data:
            api.pinfo('ret: {}'.format(self._data))
        conn.commit()
        conn.close()
        return True

    def all(self):
        return self._data

    def first(self):
        if self._data:
            return self._data[0]
        return ()


if __name__ == '__main__':
    db = DBApi('api_userinfo')
    db.insert(
        username='eregec2',
        password='123456',
        sex=0,
        tel='123456789'
    ).execute()

    db.select('username', 'name', 'password').execute()
