from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context

from todo.models import ToDo

from todo.forms import ToDoForm
from django.core.context_processors import csrf

def home_page(request):
    #if 'id' not in request.session:
    #    return HttpResponseRedirect('/accounts/unauthorized')
        
    import time
    current_date = time.strftime('%Y-%m-%d')
        
    ToDo.objects.filter(date_todo__lt=current_date).filter(archive='0').update(date_todo=current_date)
    
    current_todo_list = ToDo.objects.filter(date_todo=current_date)
    
    #fullname = request.session['first_name'] + ' ' + request.session['last_name']
    
    #return render(request, 'home.html', 
    #                        {'curr_date': current_date,
    #                        'todoList': current_todo_list,
    #                        'full_name':fullname
    #                       }
    #              )
    
    return render(request, 'home.html', 
                            {'curr_date': current_date,
                            'todoList': current_todo_list
                            }
                  )

def tick_done(request, todoID=1):
    #if 'id' not in request.session:
    #    return HttpResponseRedirect('/accounts/unauthorized')
        
    ToDo.objects.filter(id=todoID).update(archive=1)
    return redirect('home')

def tick_cancel(request, todoID=1):
    #if 'id' not in request.session:
    #    return HttpResponseRedirect('/accounts/unauthorized')
        
    ToDo.objects.filter(id=todoID).update(archive=2)
    return redirect('home')

def add(request):
    if request.POST:
        form = ToDoForm(request.POST)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect('/todo/home')
    else:
        form = ToDoForm()
    
    args = {}
    args.update( csrf(request) )
    
    args['form'] = form
    
    #fullname = request.session['first_name'] + ' ' + request.session['last_name']
    
    import time
    current_date = time.strftime('%Y-%m-%d')
    
    #return render_to_response('add_todo.html', {'form':form, 
    #                                            'full_name':fullname,
    #                                            'curr_date': current_date
    #                                            }
    #                          )
    
    return render_to_response('add_todo.html', {'form':form, 
                                                'curr_date': current_date
                                                }
                              )