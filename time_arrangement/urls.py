from django.urls import path
from time_arrangement import views

urlpatterns = [
    path('', views.login_page, name='login_page'),
    # path('base/', views.base, name='base'),
    path('login_check/', views.login_check, name='login_check'),
    path('register/', views.register, name='register'),
    path('count_down/', views.count_down_page, name='count_down_page'),
    path('task_details/', views.get_task_details, name='task_details'),
    path('statistics/', views.statistics_page, name='statistics'),
    path('settings/', views.setting_page, name='settings'),
    path('test/', views.test, name='test'),
    path('set_alarm/', views.set_alarm, name='set_alarm'),
    path('set_schedule/', views.set_schedule, name='set_schedule'),
    path('set_account/', views.set_account, name='set_account'),

    path('add_tasks/', views.add_tasks, name='add_tasks'),
    path('upadate_task_status/', views.upadate_task_status, name='upadate_task_status'),
    path('get_timestamp/', views.get_timestamp, name='get_timestamp'),
]

