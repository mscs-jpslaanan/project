from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context

from todo.models import ToDo
from django.contrib.auth.models import User

from todo.forms import ToDoForm, AddUserForm
from django.contrib.auth.forms import UserCreationForm
from django.core.context_processors import csrf

from django.utils.timezone import utc

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
                            'full_name':fullname
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
    
    return render_to_response('add_todo.html', args)                  

def home_page(request):
    if 'id' not in request.session:
        return HttpResponseRedirect('/accounts/unauthorized')
        
    import time
    current_date = time.strftime('%Y-%m-%d')
    
    #REVISE CODE HERE
    ToDo.objects.filter(date_todo__lt=current_date).filter(archive='0').update(date_todo=current_date)
    
    current_todo_list = ToDo.objects.filter(date_todo=current_date)
    
    fullname = request.session['first_name'] + ' ' + request.session['last_name']
    
    return render(request, 'home.html', 
                            {'curr_date': current_date,
                            'todoList': current_todo_list,
                            'full_name':fullname
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
