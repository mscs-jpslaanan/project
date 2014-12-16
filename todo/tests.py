from django.http import HttpRequest
from django.template.loader import render_to_string
from django.test import TestCase


from todo.views import home_page, tick_done, tick_cancel, addtodo
from project.views import login, auth_view, logout

from todo.models import ToDo

from django.test.client import Client

from django.conf import settings
from django.utils.importlib import import_module

admin_username = "patster"
admin_password = "patster"
admin_id = "1"
admin_is_superuser = "1"
admin_first_name = "patrick"
admin_last_name = "la-anan"


class HomePageTest(TestCase):

    def test_home_page_display_current_date(self):
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = admin_id
        request.session['first_name'] = admin_first_name
        request.session['last_name'] = admin_last_name
  
        response = home_page(request)
        
        import time
        current_date = time.strftime('%Y-%m-%d')
        
        self.assertIn(current_date, response.content.decode())

    def test_home_page_displays_todolist(self):
        ToDo.objects.create(item='Code unit test', added_by='1', date_todo='2014-12-13', archive='0')
        ToDo.objects.create(item='Fix code', added_by='1', date_todo='2014-12-13', archive='0')
        
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = admin_id
        request.session['first_name'] = admin_first_name
        request.session['last_name'] = admin_last_name
        
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
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = admin_id
        request.session['first_name'] = admin_first_name
        request.session['last_name'] = admin_last_name
        response = home_page(request)
        self.assertNotIn('Code unit test 1', response.content.decode())
        self.assertNotIn('Code unit test 2', response.content.decode())
        self.assertIn('Fix code', response.content.decode())
        self.assertIn('Rerun the unit test', response.content.decode())
        self.assertNotIn('Refactor', response.content.decode())
        
        self.assertEqual(ToDo.objects.filter(date_todo=today).count(), 2);
    
    def test_home_page_check_for_cancel_and_done_labels(self):
        import datetime
        today = datetime.date.today()
        ToDo.objects.create(item='Code unit test 1', added_by='1', date_todo=today, archive='2')
        ToDo.objects.create(item='Code unit test 2', added_by='1', date_todo=today, archive='1')
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = admin_id
        request.session['first_name'] = admin_first_name
        request.session['last_name'] = admin_last_name
        response = home_page(request)
        self.assertIn('Cancelled', response.content.decode())
        self.assertIn('Done', response.content.decode())
    
        
class TodoOperationsTest(TestCase):
    def test_tick_as_done(self):
        import datetime
        today = datetime.date.today()
        ToDo.objects.create(id='5', item='Code unit test', added_by='1', date_todo=today, archive='0')
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = '1';
        response = tick_done(request, 5)
        self.assertEqual(ToDo.objects.get(id=5).archive, 1)

    def test_tick_as_cancelled(self):
        import datetime
        today = datetime.date.today()
        ToDo.objects.create(id='5', item='Code unit test', added_by='1', date_todo=today, archive='0')
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = '1';
        response = tick_cancel(request, 5)
        self.assertEqual(ToDo.objects.get(id=5).archive, 2)

class AddToDoFormTest(TestCase):
    def test_is_todo_form_required_fields_present(self):
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = admin_id
        request.session['first_name'] = admin_first_name
        request.session['last_name'] = admin_last_name
        response = tick_done(request, 5)
        response = addtodo(request)
        self.assertIn("Item:", response.content.decode())
        self.assertIn("Date todo:", response.content.decode())
        self.assertIn("type=\"text\"", response.content.decode())
        self.assertIn("<input type='submit' name='submit' value='Add to do item' />", response.content.decode())
    
    def test_todo_is_added_in_the_list(self):
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = admin_id
        request.session['first_name'] = admin_first_name
        request.session['last_name'] = admin_last_name
        response = tick_done(request, 5)
        response = addtodo(request)
        self.assertIn("Item:", response.content.decode())
        self.assertIn("Date todo:", response.content.decode())
        self.assertIn("type=\"text\"", response.content.decode())
        self.assertIn("<input type='submit' name='submit' value='Add to do item' />", response.content.decode())

class SecurityTest(TestCase):
    def test_if_login_works(self):
        c = Client()
        response = c.post('/login/', {'username':admin_username, 'password':admin_password})
        
    
    def test_logout_if_session_variables_are_unset(self):
        request = HttpRequest()
        
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        
        request.session['username'] = admin_username
        request.session['id'] = admin_id
        request.session['is_superuser'] = admin_is_superuser
        request.session['first_name'] = admin_first_name
        request.session['last_name'] = admin_last_name
        
        response = logout(request)
        
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        
        response = home_page(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/accounts/unauthorized')
        
        response = addtodo(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/accounts/unauthorized')
        
        response = tick_done(request, 5)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/accounts/unauthorized')
        
        response = tick_cancel(request, 5)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/accounts/unauthorized')
        
class LoginLogoutPageTest(TestCase):
    def test_login_page_required_fields_are_present(self):
        request = HttpRequest()
        response = login(request)
        self.assertIn("User name:", response.content.decode())
        self.assertIn("Password:", response.content.decode())
        self.assertIn("type=\"text\"", response.content.decode())
        self.assertIn("type=\"password\"", response.content.decode())
        
        
    def test_logout_page_if_prompt_is_present(self):
        request = HttpRequest()
        
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        
        request.session['username'] = admin_username
        request.session['id'] = admin_id
        request.session['is_superuser'] = admin_is_superuser
        request.session['first_name'] = admin_first_name
        request.session['last_name'] = admin_last_name
        
        response = logout(request)
        self.assertIn("Logged out!", response.content.decode())
        
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