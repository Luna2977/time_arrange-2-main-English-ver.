from django.http import HttpRequest,JsonResponse,HttpResponse
from django.shortcuts import render, redirect
from time_arrangement.sqltools import DB_TOOLS
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .sqltools import DB_TOOLS
import uuid

import time
import random
import datetime
import calendar
import json
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
# weekday_number = now.weekday()

 
def get_current_time():
    current_time = datetime.datetime.now()
    current_date=str(current_time)[:10]
    current_min=str(current_time)[11:16]

    today = datetime.date.today()
 
    # 获取今天是星期几（0是星期一，1是星期二，...，6是星期日）
    weekday_number = today.weekday()
 
    # 使用calendar模块将数字转换为英文
    weekday = calendar.day_name[weekday_number]

    return current_time,current_date,current_min,weekday

def add_all(a):
    res=0
    for row in a:
        res+=int(row[0])
    return res

def generate_user_id():
    """generate random user id by register time"""
    timestamp = int(time.time() * 1000)
    random_number = random.randint(1000, 9999)
    return f"{timestamp}{random_number}"


def login_page(request:HttpRequest):
    return render(request, 'login_and_register.html')

def switch_timestamp(time):
    dt = datetime.datetime.strptime(time, "%H:%M")
 
    # 为了得到一个完整的时间戳，我们需要一个完整的日期，这里我们使用今天作为日期
    today1 = datetime.datetime.now().date()  # 获取今天的日期
    full_datetime = datetime.datetime.combine(today1, dt.time())  # 结合日期和时间
    
    # 将datetime对象转换为时间戳
    timestamp = int(full_datetime.timestamp())
    return timestamp

def is_worktime(userid,today):
    periods=DB_TOOLS().get_daily_starttime_endtime_by_userid(userid,today)

    working_periods = []
    for start_str, end_str in periods:
        start = switch_timestamp(start_str)
        end = switch_timestamp(end_str)
        working_periods.append((start, end))

    # 获取当前时间
    now_time = datetime.datetime.now()

    # 获取当前时间的时间戳
    now = int(now_time.timestamp())
    endtime=0

    for start, end in working_periods:
        if start <= now <= end:
            return True,end
    return False,endtime



def count_down_page(request:HttpRequest):
    userid = request.session.get('user_id')
    today=get_current_time()[1]
    duration=DB_TOOLS().get_alarm_duration_by_userid(userid)
    worktime=DB_TOOLS().get_daily_worktime_by_userid(userid,today)
    #endtime=DB_TOOLS().get_daily_endtime_by_userid(userid,today)

    isWorktime=is_worktime(userid,today)[0]
    if isWorktime:
        endtimestamp=is_worktime(userid,today)[1]
    else:
        endtimestamp=0

    # print(isWorktime)
    # endtimestamp = switch_timestamp(endtime)
    # print("时间戳:", endtimestamp)

    print("今天是啊啊啊啊啊啊"+today)
    task = DB_TOOLS().get_today_task_by_userid(userid,today)
    tasks = []
    for row in task:
        task = {
            'taskid': row[0],  # 第一个字段是 taskid
            'taskname': row[1],  # 第二个字段是 task_name
        }
        tasks.append(task)
    if tasks!=None:
        return render(request,"count_down.html", {'isWorktime':isWorktime,'duration':duration,'worktime':worktime,'endtime':endtimestamp,'task': tasks})
    else:
        return render(request,"count_down.html", {'isWorktime':isWorktime,'duration':duration,'worktime':worktime,'endtime':endtimestamp,'task': None})
    # return render(request, 'count_down.html',{'duration':duration,'worktime':worktime})

def taskdetail_page(request:HttpRequest):
    return render(request, 'taskDetail.html')

def statistics_page(request:HttpRequest):
    userid = request.session.get('user_id')
    today=get_current_time()[1]
    now = timezone.now()

    # 计算一周前的时间
    one_week_ago = str(now - datetime.timedelta(days=6))
    print("一周前是啊啊啊啊啊啊"+str(one_week_ago))

    d_totalworktime=DB_TOOLS().get_daily_worktime_by_userid(userid,today)
    d_exactworktime=DB_TOOLS().get_daily_totalworktime_by_userid(userid,today)

    # d_total=add_all(d_totalworktime)
    d_exact=add_all(d_exactworktime)
    # print(d_totalworktime,d_exactworktime)
    daily_res=(int(d_exact)/(60*int(d_totalworktime)))*100

    w_totalworktime=DB_TOOLS().get_weekly_worktime_by_userid(userid,today,one_week_ago)
    w_exactworktime=DB_TOOLS().get_weekly_totalworktime_by_userid(userid,today,one_week_ago)

    w_total=add_all(w_totalworktime)
    w_exact=add_all(w_exactworktime)

    print(w_exact,w_total)

    weekly_res=(w_exact/60*w_total)*100

    # 查询过去一周的数据
    task = DB_TOOLS().get_completed_task_by_userid(userid,today,one_week_ago[:10])
    # print(task)
    tasks = []
    for row in task:
        task = {
            'taskid': row[0],  # 第一个字段是 taskid
            'taskname': row[1],  # 第二个字段是 task_name
        }
        tasks.append(task)
    if tasks!=None:
        return render(request,"Statistics.html", {'task': tasks,'daily_res':daily_res,'weekly_res':weekly_res})
    else:
        return render(request,"Statistics.html", {'task': None,'daily_res':daily_res,'weekly_res':weekly_res})

def get_schedules(userid,today):
    periods=DB_TOOLS().get_daily_starttime_endtime_by_userid(userid,today)

    working_periods = []
    for row in periods:
        task = {
            'start_time': row[0],  # 第一个字段是 taskid
            'end_time': row[1],  # 第二个字段是 task_name
        }
        working_periods.append(task)
    return working_periods

def setting_page(request:HttpRequest):
    userid = request.session.get('user_id')
    today=get_current_time()[1]
    working_periods=get_schedules(userid,today)
    return render(request, 'settings.html',{'periods':working_periods})

def base(request:HttpRequest):    
    return render(request, 'base.html')

def test(request:HttpRequest):
    # if request.method == 'POST':
    #     # 获取表单数据
    #     user_name = request.POST.get('user_name')
    #     user_age = request.POST.get('user_age')
        
    #     # 处理数据（这里只是简单返回数据示例）
    #     return HttpResponse(f"收到的数据: 用户名 - {user_name}, 年龄 - {user_age}")
    
    # 如果是 GET 请求，渲染表单页面
    return render(request, '1.html')

# def get_date(request:HttpRequest):
#     return render(request, 'base.html')

def check_time(a,b):
    a1=a[:2]
    a2=a[3:]
    b1=b[:2]
    b2=b[3:]
    if a1>b1:
        return False
    elif a1==b1 and a2>b2:
        return False
    else:
        return True
    
def time_duration(starttime,endtime):
    a1=starttime[:2]
    a2=starttime[3:]
    b1=endtime[:2]
    b2=endtime[3:]
    duration=60*(int(b1)-int(a1))+int(b2)-int(a2)
    return duration

# @csrf_exempt
from django.contrib.auth.hashers import check_password


from django.shortcuts import redirect  # 确保有引入

def login_check(request: HttpRequest):
    if request.method == 'POST':
        loginUsername = request.POST.get('loginUsername')
        loginPassword = request.POST.get('loginPassword')

        db_tool = DB_TOOLS()
        userid_list = db_tool.get_userid_by_username(loginUsername)

        if not userid_list:
            return render(request, "login_and_register.html", {'login_error_message': 'User does not exist!'})

        userid = userid_list[0]
        hashed_psw = db_tool.get_psw_by_userid(userid)

        if not hashed_psw:
            return render(request, "login_and_register.html", {'login_error_message': 'User password not found!'})

        if loginPassword == hashed_psw:  # 你现在存的是明文，所以直接比对
            request.session['user_id'] = userid
            return redirect('count_down_page')  # ✅ 成功后重定向到主页或其他页面
        else:
            return render(request, "login_and_register.html", {'login_error_message': 'Wrong username or password!'})


def get_task_details(request:HttpRequest):
    userid = request.session.get('user_id')
    print(userid)
    task = DB_TOOLS().get_task_by_userid(userid)
    # print(tasks[0])
    if task!=None:
        tasks = []
        for row in task:
            task = {
                'taskid': row[1],  # 第一个字段是 taskid
                'taskname': row[2],  # 第二个字段是 task_name
                'taskdetail': row[3], 
                'taskddl': row[4], 
                'status':row[5],
            }
            tasks.append(task)
        return render(request,"taskDetail.html", {'task': tasks})
    else:
        return render(request,"taskDetail.html", {'task': None})
    
# def get_today_task_details(request:HttpRequest):


def set_alarm(request:HttpRequest):
    #这个是设置休息时间的
    today=get_current_time()[1]
    if request.method == 'POST':
        print('我要设闹钟')
        userid = request.session.get('user_id')
        duration = request.POST.get('alarmInterval')
        check=DB_TOOLS().get_alarm_duration_by_userid(userid)
        if check is not None:
            DB_TOOLS().update_alarm_by_userid(duration,userid)
        # print(duration)
        else:
            DB_TOOLS().set_alarm_by_userid(duration,userid)
        working_periods=get_schedules(userid,today)
        return render(request,"settings.html",{'redirect_url': None,'periods':working_periods})
    
def check_not_used(userid,today,starttime,endtime):
    periods=DB_TOOLS().get_daily_starttime_endtime_by_userid(userid,today)

    working_periods = []
    for start_str, end_str in periods:
        start = switch_timestamp(start_str)
        end = switch_timestamp(end_str)
        working_periods.append((start, end))

    new_s=switch_timestamp(starttime)
    new_e=switch_timestamp(endtime)


    for start, end in working_periods:
        if new_s<end:
            if new_e>start:
                return False
        elif new_e>start:
            if new_s<end:
                return False
    return True
    

    
def set_schedule(request:HttpRequest):
    #这个是设置工作起始时间的
    if request.method == 'POST':
        print('我要设闹钟')
        userid = request.session.get('user_id')
        starttime = request.POST.get('onDutyTime')
        endtime = request.POST.get('offDutyTime')
        today=get_current_time()[1]
        time_check=check_time(starttime,endtime)
        print(today)
        if time_check:
            # check=DB_TOOLS().get_daily_worktime_by_userid(userid,today)
            check=check_not_used(userid,today,starttime,endtime)
            print(starttime,endtime)
            duration=time_duration(starttime,endtime)
            # DB_TOOLS().set_schedule_by_userid(starttime,endtime,userid,duration,today)
            print(check)
            if check:
                DB_TOOLS().set_schedule_by_userid(starttime,endtime,userid,duration,today)
                working_periods=get_schedules(userid,today)
                return render(request,"settings.html",{'redirect_url': None,'periods':working_periods})
            # # print(duration)
            else:
                return render(request,"settings.html",{'redirect_url': None,'msg':"Overlapping hours are not allowed.!"})
            #     
        else:
            return render(request,"settings.html",{'redirect_url': None,'msg':"Start time should not be later than end time!"})
        return render(request,"settings.html")
    
def set_account(request:HttpRequest):
    #这个是更新账户信息的
    if request.method == 'POST':
        print('我要设用户信息！！！')
        userid = request.session.get('user_id')
        userName = request.POST.get('userName')
        userPassword = request.POST.get('userPassword')

        check=DB_TOOLS().get_userid_by_username(userName)
        print(check)
        if len(check)!=0:
            red='None' 
            msg='User name repeated!'
            today=get_current_time()[1]
            working_periods=get_schedules(userid,today)
            return render(request,"settings.html", {'redirect_url':red,'msg':msg,'periods':working_periods})
        else:
            DB_TOOLS().update_account_by_userid(userName,userPassword,userid)
            return render(request,"settings.html", {'redirect_url': '/login_check/','msg':None})
        # return redirect('/login_check/')
        # return HttpResponse("Account settings updated successfully.")

def add_tasks(request:HttpRequest):
    userid = request.session.get('user_id')
    taskName = request.POST.get('taskName')
    taskDetail = request.POST.get('taskDetail')
    taskDeadline = request.POST.get('taskDeadline')
    taskid=generate_user_id()
    DB_TOOLS().insert_new_task_by_userid(userid,taskid,str(taskName),str(taskDetail),taskDeadline)
    # return render(request,"taskDetail.html")
    return redirect('/task_details/')


# def register(request: HttpRequest):
#     if request.method == 'POST':
#         registerUsername = request.POST.get('registerUsername')
#         registerPassword = request.POST.get('registerPassword')
#         confirmPassword = request.POST.get('confirmPassword')
#
#         print("📌 注册用户名:", registerUsername)
#
#         db_tool = DB_TOOLS("time_arrangement")
#         userid = db_tool.get_userid_by_username(registerUsername)
#
#         if userid:
#             # 用户名已存在
#             return render(request, "login_and_register.html", {'register_error_message': 'Repeated username! Please change!'})
#
#         if registerPassword != confirmPassword:
#             # 密码不匹配
#             return render(request, "login_and_register.html", {'register_error_message': 'Password does not match!'})
#
#         # 生成唯一 ID 并存储用户
#         new_user_id = str(uuid.uuid4())
#         hashed_password = make_password(confirmPassword)  # 使用 Django 内置方法加密密码
#
#         db_tool.insert_new_user(new_user_id, registerUsername, hashed_password)
#
#         return render(request, "login_and_register.html", {'login_error_message': 'Register success! Please log in!'})
#
#     return render(request, "login_and_register.html")
def register(request: HttpRequest):
    """
    用户注册
    """
    if request.method == 'POST':
        registerUsername = request.POST.get('registerUsername')
        registerPassword = request.POST.get('registerPassword')
        confirmPassword = request.POST.get('confirmPassword')

        print("📌 注册用户名:", registerUsername)

        db_tool = DB_TOOLS("time_arrangement")
        userid = db_tool.get_userid_by_username(registerUsername)

        if userid:
            return render(request, "login_and_register.html", {'register_error_message': 'Repeated username! Please change!'})

        if registerPassword != confirmPassword:
            return render(request, "login_and_register.html", {'register_error_message': 'Password does not match!'})

        # 直接存明文密码 ❌不安全❌
        new_user_id = str(uuid.uuid4())
        raw_password = confirmPassword  # 直接存明文密码

        print(f"🚨 存入数据库的明文密码: {raw_password}")

        db_tool.insert_new_user(new_user_id, registerUsername, raw_password)

        return render(request, "login_and_register.html", {'login_error_message': 'Register success! Please log in!'})

    return render(request, "login_and_register.html")

def upadate_task_status(request:HttpRequest):
    if request.method == 'POST':
        try:
            # 解析请求体中的数据
            data = json.loads(request.body)
            task_id = data.get('task_id')  # 获取任务 ID

            userid = request.session.get('user_id')
            print('从前端拿来的！！！'+task_id)
            # 查找任务并更新状态
            DB_TOOLS().completed_task_by_userid(userid,task_id)
            # task.completed = True  # 假设任务模型中有 completed 字段
            # task.save()

            # 返回成功响应
            return JsonResponse({'message': 'Task marked as completed'}, status=200)
        except Exception as e:
            return JsonResponse({'message': f'Error: {str(e)}'}, status=500)

def get_timestamp(request:HttpRequest):
    if request.method == 'POST':
        userid = request.session.get('user_id')
        today=get_current_time()[1]
        try:
            # 获取请求的内容
            data = json.loads(request.body)
            timestamp = data.get('timestamp')
            status = data.get('status')

            if timestamp:
                # 将时间戳转换为 datetime 对象
                timestamp_datetime = datetime.datetime.fromtimestamp(timestamp / 1000)

                # 将时间戳解析为某种格式（例如，返回年月日时分秒）
                formatted_time = timestamp_datetime.strftime('%Y-%m-%d %H:%M:%S')
                if status=='timedif':
                    DB_TOOLS().insert_daily_totalworktime_by_userid(userid,int(timestamp),today)
                print('倒计时的时间戳！！！'+ status +'   '+ str(timestamp))

                # 返回解析后的时间信息
                return JsonResponse({'message': 'Timestamp received and parsed', 'parsed_time': formatted_time})

            return JsonResponse({'error': 'Timestamp not provided'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)
    


# def calculate_weekly_work(request:HttpRequest):
