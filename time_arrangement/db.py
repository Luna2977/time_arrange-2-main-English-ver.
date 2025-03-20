import pymysql
from django.conf import settings

MYSQLDB = {
    'time_arrangement': {
        'host': '127.0.0.1',
        'user': 'root',
        'password': 'zqydemysql',
        'port': 3306,
        'charset': 'utf8mb4',
        'database': 'time_arrangement'  # ✅ 确保指定数据库
    }
}


class BaseDB:
    """用于连接 MySQL，并处理数据库操作"""

    def __init__(self, machine='time_arrangement', database='time_arrangement', cursor="Cursor"):
        db = MYSQLDB.get(machine)
        if not db:
            raise ValueError(f"数据库配置 '{machine}' 未找到")

        self.host = db.get("host")
        self.user = db.get("user")
        self.pwd = db.get("password")
        self.port = db.get("port")

        try:
            self.conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.pwd,
                database=database,  # ✅ 指定默认数据库
                port=self.port,
                charset=db.get("charset", "utf8mb4"),
                autocommit=True,
                cursorclass=pymysql.cursors.DictCursor if cursor == "DictCursor" else pymysql.cursors.Cursor,
            )
            self.cur = self.conn.cursor()
        except pymysql.MySQLError as e:
            print(f"❌ 数据库连接失败: {e}")
            self.conn = None
            self.cur = None

    def check_cursor(self):
        """检查数据库连接是否有效"""
        if not self.conn or not self.cur:
            raise AttributeError("数据库连接未初始化或已关闭，无法执行查询。")

    def query_one(self, sql, params=None):
        """执行查询并返回第一行数据"""
        self.check_cursor()
        self.cur.execute(sql, params)
        return self.cur.fetchone()

    def query_all(self, sql, params=None):
        """执行查询，返回所有数据"""
        self.check_cursor()
        self.cur.execute(sql, params)
        return self.cur.fetchall()

    def update(self, sql, params=None):
        """执行更新 SQL"""
        self.check_cursor()
        self.cur.execute(sql, params)
        self.conn.commit()

    def update_result(self, sql, params=None):
        """执行更新 SQL 并返回受影响的行数"""
        self.check_cursor()
        rows_affected = self.cur.execute(sql, params)
        self.conn.commit()
        return rows_affected

    def query_one_and_one_field(self, sql, params=None):
        """执行查询并返回单个字段值"""
        self.check_cursor()
        if params and not isinstance(params, tuple):
            params = (params,)  # 确保参数是元组
        self.cur.execute(sql, params)
        result = self.cur.fetchone()
        return result[0] if result else None

    def __del__(self):
        """析构函数，关闭数据库连接"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
