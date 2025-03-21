from time_arrangement.db import BaseDB

class DB_TOOLS:
    """Connect 218 database"""

    def __init__(self, database="time_arrangement", cursor='Cursor'):
        """You can also use cursor='DictCursor'"""
        self.db = BaseDB(database, cursor=cursor)

    def query_sql(self, sql):
        """Execute SQL"""
        msg = self.db.query_all(sql)
        return msg

    def update_sql(self, sql):
        """Execute SQL"""
        try:
            self.db.update(sql)
        except Exception as e:
            return e

    def get_userid_by_username(self, username):
            """Get userid by username"""
            sql = "select user_id from time_arrangement.users where user_name = '{}' "
            print(sql)
            params = (username,)  # A single parameter must have a comma, otherwise it is not a tuple
            return self.db.query_all(sql, params)
    
    def get_psw_by_userid(self, userid):
            """Get mima by userid"""
            sql = "select pswd from time_arrangement.users where user_id = '{}' "
            params = (userid,)  # A single parameter must have a comma, otherwise it is not a tuple
            return self.db.query_one_and_one_field(sql, params)
    
    def get_task_by_userid(self, userid):
            """Get task by userid"""
            sql = "select * from time_arrangement.tasks where user_id = '{}'"
            params = (userid,)  # A single parameter must have a comma, otherwise it is not a tuple
            return self.db.query_all(sql, params)
    
    def get_today_task_by_userid(self, userid, today):
            """Get task by userid"""
            sql = "select task_id as taskid,task_name as taskname from time_arrangement.tasks where user_id = '{}' and task_date='{}'"
            params = (userid,today)  # A single parameter must have a comma, otherwise it is not a tuple
            return self.db.query_all(sql, params)
    
    def get_completed_task_by_userid(self, userid, date1,date2):
            """Get task by userid"""
            sql = "select task_id as taskid,task_name as taskname from time_arrangement.tasks where user_id = '{}' and status='1' and task_date BETWEEN '{}' AND '{}'"
            params = (userid,date2,date1)  # A single parameter must have a comma, otherwise it is not a tuple
            return self.db.query_all(sql, params)
    
    def completed_task_by_userid(self, userid, taskid):
            """Get task by userid"""
            sql = "update time_arrangement.tasks set status='1' where user_id = '{}' and task_id='{}'"
            params = (userid,taskid)  # A single parameter must have a comma, otherwise it is not a tuple
            return self.db.query_all(sql, params)
    
    def update_alarm_by_userid(self, duration, userid):
            """Get task by userid"""
            # sql = "INSERT INTO time_arrangement.alarm (user_id, duration) VALUES (?, ?)"
            sql="UPDATE time_arrangement.alarm SET duration = '{}' WHERE user_id = '{}'"
            params = (duration,userid) 
            return self.db.update(sql, params)
    
    def set_alarm_by_userid(self, duration, userid):
            """if not exist, insert alarm duration"""
            sql = "INSERT INTO time_arrangement.alarm (user_id, duration) VALUES ({}, {})"
            # sql="UPDATE time_arrangement.alarm SET duration = '{}' WHERE user_id = '{}'"
            params = (userid,duration)  
            return self.db.update(sql, params)
    
    def get_alarm_duration_by_userid(self, userid):
            """Get task by userid"""
            sql = "select duration from time_arrangement.alarm where user_id = '{}'"
            params = (userid,)  
            return self.db.query_one_and_one_field(sql, params)
    
    def get_daily_worktime_by_userid(self, userid, today):
            """Get the total working time of the day by userid"""
            sql = "select work_duration from time_arrangement.schedule where user_id = '{}' and date='{}' "
            params = (userid,today)  
            return self.db.query_one_and_one_field(sql, params)
    
    def get_daily_starttime_endtime_by_userid(self, userid, today):
            """Get the total working time of the day by userid"""
            sql = "select start_time, end_time from time_arrangement.schedule where user_id = '{}' and date='{}' ORDER BY start_time ASC;"
            params = (userid,today)  
            return self.db.query_all(sql, params)
    
    def get_daily_endtime_by_userid(self, userid, today):
            """Get the total working time of the day by userid"""
            sql = "select end_time from time_arrangement.schedule where user_id = '{}' and date='{}' "
            params = (userid,today)  
            return self.db.query_all(sql, params)
    
    def update_account_by_userid(self, username, userpassword,userid):
            """update user account by userid """
            sql="UPDATE time_arrangement.users SET user_name = '{}',pswd = '{}' WHERE user_id = '{}'"
            params = (username,userpassword,userid) 
            return self.db.update(sql, params)
    
    def insert_new_user(self, userid,username,userpassword):
            """if not exist, insert alarm duration"""
            sql = "INSERT INTO time_arrangement.users (user_id, user_name, pswd) VALUES ({}, {}, {})"
            params = (userid,username,userpassword)  
            return self.db.update(sql, params)
    
    def insert_new_task_by_userid(self, userid,taskid,taskname,taskcontent,taskddl):
            """if not exist, insert alarm duration"""
            sql = "INSERT INTO time_arrangement.tasks (user_id, task_id, task_name, task_content, task_date,status) VALUES ({}, {}, '{}', '{}', '{}',0)"
            params = (userid,taskid,taskname,taskcontent,taskddl)  
            return self.db.update(sql, params)
    
    # def add_task(self, taskName,taskDetail,taskDeadline):
    #         """Get userid by username"""
    #         sql = "INSERT INTO time_arrangement.tasks (username, email, age) VALUES ('张三', 'zhangsan@example.com', 25);"
    #         params = (userid,)  # A single parameter must have a comma, otherwise it is not a tuple
    #         return self.db.query_one_and_one_field(sql, params)

    def update_schedule_by_userid(self, starttime, endtime, userid, duration,date):
            """Get task by userid"""
            # sql = "INSERT INTO time_arrangement.alarm (user_id, duration) VALUES (?, ?)"
            sql="UPDATE time_arrangement.Schedule SET start_time='{}', end_time='{}', work_duration = '{}' WHERE user_id = '{}' and date='{}'"
            params = (starttime, endtime, duration, userid, date) 
            return self.db.update(sql, params)
    
    def set_schedule_by_userid(self, starttime, endtime, userid, duration,date):
            """if not exist, insert alarm duration"""
            sql = "INSERT INTO time_arrangement.Schedule (user_id, start_time, end_time, date, work_duration) VALUES ({}, '{}','{}','{}','{}')"
            # sql="UPDATE time_arrangement.alarm SET duration = '{}' WHERE user_id = '{}'"
            params = (userid, starttime, endtime, date, duration)  
            return self.db.update(sql, params)
    
    def get_daily_totalworktime_by_userid(self, userid, date):
            """if not exist, insert alarm duration"""
            sql = "select durations from time_arrangement.totalWorktime where user_id = '{}' and date='{}' "
            params = (userid, date)  
            return self.db.query_all(sql, params)
    
    def insert_daily_totalworktime_by_userid(self, userid, durations, date):
            """if not exist, insert alarm duration"""
            sql = "INSERT INTO time_arrangement.totalWorktime (user_id, durations, date) VALUES ({}, '{}','{}')"
            params = (userid, durations, date)  
            return self.db.update(sql, params)
    
    def update_daily_totalworktime_by_userid(self, userid, date):
            """if not exist, insert alarm duration"""
            sql = "select durations from time_arrangement.totalWorktime where user_id = '{}' and date='{}' "
            params = (userid, date)  
            return self.db.query_one_and_one_field(sql, params)
    
    def get_weekly_totalworktime_by_userid(self, userid, date1,date2):
        """if not exist, insert alarm duration"""
        sql = "select durations from time_arrangement.totalWorktime where user_id = '{}' and date BETWEEN '{}' AND '{}' "
        params = (userid, date2,date1)  
        return self.db.query_all(sql, params)
    
    def get_weekly_worktime_by_userid(self, userid, date1,date2):
        """Get the total working time of the day by userid"""
        sql = "select work_duration from time_arrangement.schedule where user_id = '{}' and date BETWEEN '{}' AND '{}' "
        params = (userid,date2,date1)  
        return self.db.query_all(sql, params)