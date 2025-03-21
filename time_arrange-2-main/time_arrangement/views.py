from django.http import HttpRequest,JsonResponse,HttpResponse
from django.shortcuts import render, redirect
from time_arrangement.sqltools import DB_TOOLS
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import authenticate, login

import time
import random
import datetime
import calendar
import json

# weekday_number = now.weekday()
 
def get_current_time():
    current_time = datetime.datetime.now()
    current_date=str(current_time)[:10]
    current_min=str(current_time)[11:16]

    today = datetime.date.today()
 
    # Get the day of the week today (0 is Monday, 1 is Tuesday, ..., 6 is Sunday)
    weekday_number = today.weekday()
 
    # Use the calendar module to convert numbers to English
    weekday = calendar.day_name[weekday_number]

    return current_time,current_date,current_min,weekday

def add_all(a):
    if a is None:  # How to enter None，Return 0
        return 0

    res = 0
    for row in a:
        if row and row[0] is not None:  # Ensure row[0] is not None
            res += int(row[0])
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
 
    # To get a complete timestamp, we need a complete date, here we use today as the date
    today1 = datetime.datetime.now().date()  # Get today's date
    full_datetime = datetime.datetime.combine(today1, dt.time())  # Combining date and time
    
    # Convert a datetime object to a timestamp
    timestamp = int(full_datetime.timestamp())
    return timestamp

def is_worktime(userid,today):
    periods=DB_TOOLS().get_daily_starttime_endtime_by_userid(userid,today)

    working_periods = []
    for start_str, end_str in periods:
        start = switch_timestamp(start_str)
        end = switch_timestamp(end_str)
        working_periods.append((start, end))

    # Get the current time
    now_time = datetime.datetime.now()

    # Get the current time stamp
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
    endtime=DB_TOOLS().get_daily_endtime_by_userid(userid,today)

    isWorktime=is_worktime(userid,today)[0]
    if isWorktime:
        endtimestamp=is_worktime(userid,today)[1]
    else:
        endtimestamp=0

    # print(isWorktime)
    # endtimestamp = switch_timestamp(endtime)
    # print("Timestamp:", endtimestamp)

    print("Today is ahhhhh"+today)
    task = DB_TOOLS().get_today_task_by_userid(userid,today)
    tasks = []
    for row in task:
        task = {
            'taskid': row[0],  # The first field is taskid
            'taskname': row[1],  # The second field is task_name
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

    # Calculate the time one week ago
    one_week_ago = str(now - datetime.timedelta(days=6))
    print("A week ago "+str(one_week_ago))

    d_totalworktime=DB_TOOLS().get_daily_worktime_by_userid(userid,today)
    d_exactworktime=DB_TOOLS().get_daily_totalworktime_by_userid(userid,today)

    # d_total=add_all(d_totalworktime)
    # Calculation d_totalworktime sum d_exactworktime sum
    d_totalworktime = add_all(d_totalworktime)
    d_exactworktime = add_all(d_exactworktime)

    # No guarantee amount None，Exemption from avoidance 0
    d_totalworktime = int(d_totalworktime) if d_totalworktime not in [None, 0] else 1  # Avoid ZeroDivisionError
    d_exactworktime = int(d_exactworktime) if d_exactworktime is not None else 0  # Avoiding TypeError

    # 计算 daily_res
    daily_res = (d_exactworktime / (60 * d_totalworktime)) * 100


    w_totalworktime=DB_TOOLS().get_weekly_worktime_by_userid(userid,today,one_week_ago)
    w_exactworktime=DB_TOOLS().get_weekly_totalworktime_by_userid(userid,today,one_week_ago)

    w_total=add_all(w_totalworktime)
    w_exact=add_all(w_exactworktime)

    print(w_exact,w_total)

    weekly_res=(w_exact/60*w_total)*100

    # Query data for the past week
    task = DB_TOOLS().get_completed_task_by_userid(userid,today,one_week_ago[:10])
    # print(task)
    tasks = []
    for row in task:
        task = {
            'taskid': row[0],  # The first field is taskid
            'taskname': row[1],  # The second field is task_name
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
            'start_time': row[0],  # The first field is taskid
            'end_time': row[1],  # The second field is task_name
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
    #     # Get form data
    #     user_name = request.POST.get('user_name')
    #     user_age = request.POST.get('user_age')
        
    #     # Processing data (here is just a simple example of returning data)
    #     return HttpResponse(f"Data obtained: User name - {user_name}, age - {user_age}")
    
    # If it is a GET request, render the form page
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
def login_check(request:HttpRequest):
    """
    check if the user is exist and if the username and password matches
    """
    if request.method == 'POST':
        loginUsername = request.POST.get('loginUsername')
        loginPassword = request.POST.get('loginPassword')
        # print(loginUsername+'111')
        userid_list = DB_TOOLS().get_userid_by_username(loginUsername)
        # print(userid)
        # print(userid) 
        # print(imgroupid)
        if len(userid_list)!=0:
            userid=userid_list[0][0]
            psw = DB_TOOLS().get_psw_by_userid(userid)
            if psw==loginPassword:
                # user = authenticate(request, username=loginUsername, password=loginPassword)
                # login(request, user)
            # After successful login, the user ID is stored in the session
                request.session['user_id'] = userid
                date=get_current_time()[1]
                weekday=get_current_time()[3]
                print('111',date,weekday)
                # print('true')
                return render(request,"base.html", {'date':date,'weekday':weekday})
            else:
                return render(request,"login_and_register.html", {'login_error_message': 'Wrong name or password! Please check.'})
        else:
            return render(request,"login_and_register.html", {'login_error_message': 'User does not exist! Please check or register.'})
    return render(request,"login_and_register.html", {'login_error_message': None})

def get_task_details(request:HttpRequest):
    userid = request.session.get('user_id')
    print(userid)
    task = DB_TOOLS().get_task_by_userid(userid)
    # print(tasks[0])
    if task!=None:
        tasks = []
        for row in task:
            task = {
                'taskid': row[1],  # The first field is taskid
                'taskname': row[2],  # The second field is task_name
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
    #This is to set the rest time
    today=get_current_time()[1]
    if request.method == 'POST':
        print('I want to set an alarm')
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
    #This is to set the work start time
    if request.method == 'POST':
        print('I want to set an alarm')
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
    #This is to update the account information
    if request.method == 'POST':
        print('I want to set user information!!!')
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

def register(request:HttpRequest):
    if request.method == 'POST':
        registerUsername = request.POST.get('registerUsername')
        registerPassword = request.POST.get('registerPassword')
        confirmPassword = request.POST.get('confirmPassword')
        print(registerUsername)
        userid = DB_TOOLS().get_userid_by_username(registerUsername)
        print(userid) 
        # print(imgroupid)
        if len(userid)!=0:
            #check if userid repeated
            return render(request,"login_and_register.html", {'register_error_message': 'Repeated username! Please change!'})
        elif registerPassword!=confirmPassword:
            #check if password matches
            return render(request,"login_and_register.html", {'register_error_message': 'Password does not match!'})
        elif len(userid)==0 and registerPassword==confirmPassword:
            #register
            userid=generate_user_id()
            DB_TOOLS().insert_new_user(userid,registerUsername,confirmPassword)
            return render(request,"login_and_register.html", {'login_error_message': 'Register success! Please log in!'})
        
def upadate_task_status(request:HttpRequest):
    if request.method == 'POST':
        try:
            # Parsing the data in the request body
            data = json.loads(request.body)
            task_id = data.get('task_id')  # Get the task ID

            userid = request.session.get('user_id')
            print('Took it from the front end!!！'+task_id)
            # Find tasks and update status
            DB_TOOLS().completed_task_by_userid(userid,task_id)
            # task.completed = True  # Assume that there is a completed field in the task model
            # task.save()

            # Returns a successful response
            return JsonResponse({'message': 'Task marked as completed'}, status=200)
        except Exception as e:
            return JsonResponse({'message': f'Error: {str(e)}'}, status=500)

def get_timestamp(request:HttpRequest):
    if request.method == 'POST':
        userid = request.session.get('user_id')
        today=get_current_time()[1]
        try:
            # Get the content of the request
            data = json.loads(request.body)
            timestamp = data.get('timestamp')
            status = data.get('status')

            if timestamp:
                # Convert a timestamp to a datetime object
                timestamp_datetime = datetime.datetime.fromtimestamp(timestamp / 1000)

                # Parse a timestamp into a certain format (for example, return year, month, day, hour, minute, and second)
                formatted_time = timestamp_datetime.strftime('%Y-%m-%d %H:%M:%S')
                if status=='timedif':
                    DB_TOOLS().insert_daily_totalworktime_by_userid(userid,int(timestamp),today)
                print('Countdown timestamp！！！'+ status +'   '+ str(timestamp))

                # Returns the parsed time information
                return JsonResponse({'message': 'Timestamp received and parsed', 'parsed_time': formatted_time})

            return JsonResponse({'error': 'Timestamp not provided'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)
    


# def calculate_weekly_work(request:HttpRequest):