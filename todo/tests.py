from django.http import HttpRequest
from django.template.loader import render_to_string
from django.test import TestCase


from todo.views import home_page, tick_done, tick_cancel, addtodo, adduser
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

other_id = "2"
other_password = "otheruser"
other_is_superuser = "0"
other_username = "otheruser"
other_first_name = "other"
other_last_name = "user"
other_email = "otheruser@otheruser.com"
other_is_staff = "1"
other_is_active = "1"


class ViewUsersPageTest(TestCase):
    def test_is_list_of_users_displayed(TestCase):
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = admin_id
        request.session['is_superuser'] = admin_is_superuser
        request.session['first_name'] = admin_first_name
        request.session['last_name'] = admin_last_name
        response = viewusers(request)
        self.assertIn("List of users", response.content.decode())
        
class AddUserTest(TestCase):
    #import datetime
    #User.objects.create(id=other_id, password=other_password, last_login=datetime.datetime.now(), is_superuser=other_is_superuser, first_name=other_first_name, last_name=other_last_name, email=other_email, is_staff=other_is_staff, is_active=other_is_active, date_joined=datetime.datetime.now())
    
    def test_is_user_added(self):
        request = HttpRequest()
        request.method = "POST"
        import datetime
        today = datetime.date.today()
        
        request.POST["id"]=other_id
        request.POST["password"]=other_password
        request.POST["last_login"]=datetime.datetime.now()
        request.POST["is_superuser"]=other_is_superuser
        request.POST["first_name"]=other_first_name
        request.POST["last_name"]=other_last_name
        request.POST["email"]=other_email
        request.POST["is_staff"]=other_is_staff
        request.POST["is_active"]=other_is_active
        request.POST["date_joined"]=datetime.datetime.now()
        
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = admin_id
        request.session['is_superuser'] = admin_is_superuser
        request.session['first_name'] = admin_first_name
        request.session['last_name'] = admin_last_name
        response = adduser(request)
    
        user = User.objects.get(id=other_id)
        self.assertEqual(user.id, other_id)
    


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
        
    def test_home_page_displays_prompt_on_empty_todolist(self):
        request = HttpRequest()
        
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = admin_id
        request.session['first_name'] = admin_first_name
        request.session['last_name'] = admin_last_name
        
        response = home_page(request)
        
        self.assertIn('To do list is empty', response.content.decode())
        
    
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
        saved_todos = ToDo.objects.all()
        self.assertEqual(saved_todos.count(), 0)
        request = HttpRequest()
        request.method = "POST"
        import datetime
        today = datetime.date.today()
        request.POST["item"] = "Code unit test"
        request.POST["date_todo"] = today
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = admin_id
        request.session['first_name'] = admin_first_name
        request.session['last_name'] = admin_last_name
        response = addtodo(request)
        saved_todos = ToDo.objects.all()
        self.assertEqual(saved_todos.count(), 1)
        

class SecurityTest(TestCase):
    def test_successful_login(self):
        request = HttpRequest()
        request.method = "POST"
        request.POST["username"] = admin_username
        request.POST["password"] = admin_password
        response = auth_view(request)
        #self.assertEqual(response.status_code, 302)
        #self.assertEqual(response['location'], '/todo/home')
    
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