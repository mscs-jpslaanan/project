from django.http import HttpRequest
from django.template.loader import render_to_string
from django.test import TestCase


from todo.views import home_page

from todo.models import ToDo

class HomePageTest(TestCase):

    def test_home_page_display_current_date(self):
        request = HttpRequest()
        response = home_page(request)
        import time
        current_date = time.strftime('%Y-%m-%d')
        self.assertIn(current_date, response.content.decode())

    def test_home_page_displays_todolist(self):
        ToDo.objects.create(item='Code unit test', added_by='1', date_todo='2014-12-13', archive='0')
        ToDo.objects.create(item='Fix code', added_by='1', date_todo='2014-12-13', archive='0')
        
        request = HttpRequest()
        response = home_page(request)
        
        self.assertIn('Code unit test', response.content.decode())
        self.assertIn('Fix code', response.content.decode())
    
    def test_home_page_transfer_pending_todos_to_current_day(self):
        import datetime
        today = datetime.date.today()
        one_day = datetime.timedelta(days=1)
        yesterday = today - one_day
        tomorrow = today + one_day
        
        #Done
        ToDo.objects.create(item='Code unit test 1', added_by='1', date_todo=yesterday, archive='1')
        #Cancelled
        ToDo.objects.create(item='Code unit test 2', added_by='1', date_todo=yesterday, archive='2')
        #Pending
        ToDo.objects.create(item='Fix code', added_by='1', date_todo=yesterday, archive='0')
        
        #Current
        ToDo.objects.create(item='Rerun the unit test', added_by='1', date_todo=today, archive='0')
        
        #Future
        ToDo.objects.create(item='Refactor', added_by='1', date_todo=tomorrow, archive='0')

        request = HttpRequest()
        response = home_page(request)
        
        self.assertNotIn('Code unit test 1', response.content.decode())
        self.assertNotIn('Code unit test 2', response.content.decode())
        self.assertIn('Fix code', response.content.decode())
        self.assertIn('Rerun the unit test', response.content.decode())
        self.assertNotIn('Refactor', response.content.decode())
    
        

class TodoModelTest(TestCase):

    def test_saving_and_retrieving_todoList(self):
        ToDo.objects.create(item='Code unit test', added_by='1', date_todo='2014-12-13', archive='0')
        ToDo.objects.create(item='Fix code', added_by='1', date_todo='2014-12-13', archive='0')
        saved_todos = ToDo.objects.all()
        self.assertEqual(saved_todos.count(), 2)
        first_saved_todo = saved_todos[0]
        second_saved_todo = saved_todos[1]
        self.assertEqual(first_saved_todo.item, 'Code unit test')
        self.assertEqual(second_saved_todo.item, 'Fix code')