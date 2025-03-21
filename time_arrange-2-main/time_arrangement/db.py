
# coding=utf-8
import os
import pymysql

MYSQLDB = {
    'time_arrange': {
        'host': 'localhost',
        'user': 'root',
        'password': '123456',
        'port': 3306,
        'charset': 'utf8',
    }
}


class BaseDB:
    """Used to connect to the database and realize automatic close on exit"""

    def __init__(self,machine,cursor="Cursor",charset="utf8",database=''):
        db = MYSQLDB.get(machine)
        self.host = db.get("host")
        self.user = db.get("user")
        self.pwd = db.get("password")
        
        if cursor == "DictCursor":
            try:
                self.conn = pymysql.connect(
                    host=self.host,
                    user=self.user,
                    password=self.pwd,
                    charset=charset,
                    autocommit=True,
                    db=database,
                    cursorclass=pymysql.cursors.DictCursor,
                )
                self.cur = self.conn.cursor()
            except Exception:
                conn = 0
        else:
            try:
                self.conn = pymysql.connect(
                    host=self.host,
                    user=self.user,
                    password=self.pwd,
                    charset=charset,
                    autocommit=True,
                    db=database,
                    cursorclass=pymysql.cursors.Cursor,  # You don't need to write it, the default is Cursor
                )
                # my_logg.debug("Print sql connection")
                # my_logg.debug(conn)
                self.cur = self.conn.cursor()
            except:
                conn = 0

    def __enter__(self,charset="utf8", cursor="Cursor"):
        """Login to database"""
        return self


    def query_one_and_one_field(self,sql,params=(),keyparams={}):
        """Get one and get the first field. Format is required in SQL to pass parameters."""
        res = self.cur.execute(sql.format(*params,**keyparams))
        if res:
            res1 = self.cur.fetchone()
            return res1[0]
        
    def query_one(self,sql,params=(),keyparams={}):
        """Get one and get all fields"""
        # In sql, you need to use format to pass parameters
        res = self.cur.execute(sql.format(*params,**keyparams))
        if res :
            res1 = self.cur.fetchone()
            return res1
        
    def query_all(self,sql,params=(),keyparams={}):
        """Get all"""
        print(sql.format(*params, **keyparams))
        if self.cur.execute(sql.format(*params,**keyparams)):
            return self.cur.fetchall()
        else:
            return []
        
    # def query_one(self,sql,params=(),keyparams={}):
    #     """Get one and get all fields"""
    #     # In sql, you need to use format to pass parameters
    #     self.cur.execute(sql.format(*params,**keyparams))

    def update(self,sql,params=(),keyparams={}):
        """Update SQL statement"""
        print(sql.format(*params, **keyparams))
        self.cur.execute(sql.format(*params, **keyparams))
        self.conn.commit()

    def update_result(self, sql, params=(), keyparams={}):
        """
        Update SQL statements and return updated results
        Args:
            sql:
            params:
            keyparams:

        Returns:

        """
        return self.cur.execute(sql.format(*params, **keyparams))

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
