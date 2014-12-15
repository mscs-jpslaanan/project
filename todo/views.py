from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import Context

from todo.models import ToDo

def home_page(request):
    import time
    current_date = time.strftime('%Y-%m-%d')
        
    ToDo.objects.filter(date_todo__lt=current_date).filter(archive='0').update(date_todo=current_date)
    
    current_todo_list = ToDo.objects.filter(date_todo=current_date)
    
    return render(request, 'home.html', 
                            {'curr_date': current_date,
                            'todoList': current_todo_list
                            }
                  )

def tick_done(request, todoID=1):
    ToDo.objects.filter(id=todoID).update(archive=1)
    return redirect('home')

def tick_cancel(request, todoID=1):
    ToDo.objects.filter(id=todoID).update(archive=2)
    return redirect('home')