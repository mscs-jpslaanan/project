from django.shortcuts import render
from django.http import HttpResponse
from django.template import Context

from todo.models import ToDo

def home_page(request):
    import time
    current_date = time.strftime('%Y-%m-%d')
    current_todo_list = ToDo.objects.filter(date_todo=current_date)
    
    return render(request, 'home.html', 
                            {'curr_date': current_date,
                            'todoList': current_todo_list
                            }
                  )