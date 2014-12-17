from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context

from todo.models import ToDo
from django.contrib.auth.models import User

from todo.forms import ToDoForm, AddUserForm
from django.contrib.auth.forms import UserCreationForm
from django.core.context_processors import csrf

from django.utils.timezone import utc

import datetime

def delete_user(request, userID):
    if 'id' not in request.session:
        return HttpResponseRedirect('/accounts/unauthorized')
    
    if request.session['is_superuser'] != 1:
        return HttpResponseRedirect('/todo/unauthorized')
    
    User.objects.filter(id=userID).delete()
    return redirect('/todo/view_users')

def view_users(request):
    if 'id' not in request.session:
        return HttpResponseRedirect('/accounts/unauthorized')

    if request.session['is_superuser'] != 1:
        return HttpResponseRedirect('/todo/unauthorized')
        
    import time
    current_date = time.strftime('%Y-%m-%d')
    fullname = request.session['first_name'] + ' ' + request.session['last_name']
    
    user_list = User.objects.filter(is_active=1)
    
    return render(request, 'userlist.html', 
                            {'curr_date': current_date,
                            'userList': user_list,
                            'full_name':fullname,
                            'is_administrator':request.session['is_superuser']
                           }
                  )

def add_user(request):
    if 'id' not in request.session:
        return HttpResponseRedirect('/accounts/unauthorized')
    
    if request.session['is_superuser'] != 1:
        return HttpResponseRedirect('/todo/unauthorized')
    
    import time
    current_date = time.strftime('%Y-%m-%d')
    fullname = request.session['first_name'] + ' ' + request.session['last_name']
    
    if request.method == "POST":
        form = AddUserForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.is_superuser = 0
            instance.is_staff = 1
            instance.is_active = 1
            instance.save()
            return HttpResponseRedirect('/todo/view_users')
            
    args = {}
    args.update( csrf(request) )
    args['form'] = AddUserForm()      
    args['curr_date'] = current_date
    args['full_name'] = fullname
    args['is_administrator'] = request.session['is_superuser']
    
    return render_to_response('adduser.html', args)

def addtodo(request):
    if 'id' not in request.session:
        return HttpResponseRedirect('/accounts/unauthorized')
    
    if request.POST:
        form = ToDoForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.added_by = request.session['id']
            instance.archive = 0
            instance.save()
            return HttpResponseRedirect('/todo/home')
    else:
        form = ToDoForm()
    
    args = {}
    args.update( csrf(request) )
    args['form'] = form
    
    fullname = request.session['first_name'] + ' ' + request.session['last_name']
    import time
    current_date = time.strftime('%Y-%m-%d')
    
    args['curr_date'] = current_date
    args['full_name'] = fullname
    args['is_administrator'] = request.session['is_superuser']
    
    return render_to_response('add_todo.html', args)                  
def backoperations(request):
    if 'id' not in request.session:
        return HttpResponseRedirect('/accounts/unauthorized')
    
    import time
    current_date = time.strftime('%Y-%m-%d')
    
    #pending todo items will be transferred today
    ToDo.objects.filter(date_todo__lt=current_date).filter(archive='0').update(date_todo=current_date)
    
    #purge done and cancelled to do items < 7 days
    import datetime
    today = datetime.date.today()
    seven_days = datetime.timedelta(days=7)
    seven_days_ago = today - seven_days
    ToDo.objects.filter(date_todo__lt=seven_days_ago).delete()
    
    return HttpResponseRedirect('/todo/home')

def view_monthly(request, today = datetime.date.today()):
    if 'id' not in request.session:
        return HttpResponseRedirect('/accounts/unauthorized')
    
    first_day_current = datetime.datetime(today.year, today.month, 1)
    
    if(today.month == 12):
        first_day_next_month = datetime.datetime(today.year+1, 1, 1)
    else:
        first_day_next_month = datetime.datetime(today.year, today.month+1, 1)
        
    one_day = datetime.timedelta(days=1)
    last_day_current = first_day_next_month - one_day
    
    
    #last_day_previous = first_day_current - datetime.   timedelta(days=1)
    #first_day_previous = datetime.datetime(last_day_previous.year, last_day_previous.month, 1)

        
    monthly_todo_list = ToDo.objects.filter(date_todo__lte=last_day_current).filter(date_todo__gte=first_day_current).filter(added_by=request.session['id'])
    
    fullname = request.session['first_name'] + ' ' + request.session['last_name']
    
    return render(request, 'view_monthly.html', 
                            {'curr_date': today,
                            'end_month_day':last_day_current,
                            'start_month_day':first_day_current,
                            'todoList': monthly_todo_list,
                            'full_name':fullname,
                            'is_administrator':request.session['is_superuser']
                           }
                  )    
    
    
def view_weekly(request, date_today = datetime.date.today()):
    if 'id' not in request.session:
        return HttpResponseRedirect('/accounts/unauthorized')
    
    
    dow_today = date_today.weekday()
    if dow_today == 6:
        days_ago_saturday = 1
    else:
        days_ago_saturday = dow_today + 2
    
    delta_saturday = datetime.timedelta(days=days_ago_saturday)
    saturday = date_today - delta_saturday
    delta_prevsunday = datetime.timedelta(days=6)
    prev_sunday = saturday - delta_prevsunday
    
    eight_days = datetime.timedelta(days=8)
    
    week_end = saturday + eight_days
    week_start = prev_sunday + eight_days
    
    
    week_end = week_end.strftime('%Y-%m-%d')
    week_start = week_start.strftime('%Y-%m-%d')
    
        
    weekly_todo_list = ToDo.objects.filter(date_todo__lte=week_end).filter(date_todo__gte=week_start).filter(added_by=request.session['id'])
    
    fullname = request.session['first_name'] + ' ' + request.session['last_name']
    
    return render(request, 'view_weekly.html', 
                            {'curr_date': date_today,
                            'end_week_day':week_end,
                            'start_week_day':week_start,
                            'todoList': weekly_todo_list,
                            'full_name':fullname,
                            'is_administrator':request.session['is_superuser']
                           }
                  )    
    
def home_page(request):
    if 'id' not in request.session:
        return HttpResponseRedirect('/accounts/unauthorized')
        
    import time
    current_date = time.strftime('%Y-%m-%d')
    
    current_todo_list = ToDo.objects.filter(date_todo=current_date).filter(added_by=request.session['id'])
    
    fullname = request.session['first_name'] + ' ' + request.session['last_name']
    
    return render(request, 'home.html', 
                            {'curr_date': current_date,
                            'todoList': current_todo_list,
                            'full_name':fullname,
                            'is_administrator':request.session['is_superuser']
                           }
                  )

def tick_done(request, todoID):
    if 'id' not in request.session:
        return HttpResponseRedirect('/accounts/unauthorized')
        
    ToDo.objects.filter(id=todoID).update(archive=1)
    return redirect('home')

def tick_cancel(request, todoID):
    if 'id' not in request.session:
        return HttpResponseRedirect('/accounts/unauthorized')
        
    ToDo.objects.filter(id=todoID).update(archive=2)
    return redirect('home')

def unauthorized(request):
    import time
    current_date = time.strftime('%Y-%m-%d')
    fullname = request.session['first_name'] + ' ' + request.session['last_name']

    return render_to_response('unauthorized_access2.html', {'curr_date':current_date, 'full_name':fullname})
