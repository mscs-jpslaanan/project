from django.http import HttpRequest
from django.template.loader import render_to_string
from django.test import TestCase


from todo.views import home_page, tick_done, tick_cancel, addtodo, add_user, view_users, delete_user
from project.views import login, auth_view, logout

from todo.models import ToDo
from django.contrib.auth.models import User

from django.test.client import Client

from django.conf import settings
from django.utils.importlib import import_module

from django.utils import timezone

admin_id = 1
admin_password = "patster"
admin_is_superuser = 1
admin_username = "patster"
admin_first_name = "patrick"
admin_last_name = "la-anan"
admin_email = "john_patrick_laanan@yahoo.com"
admin_is_staff = 1
admin_is_active = 1

other_id = 500
other_password = "otheruser"
other_is_superuser = 0
other_username = "otheruser"
other_first_name = "other"
other_last_name = "user"
other_email = "otheruser@otheruser.com"
other_is_staff = 1
other_is_active = 1

import datetime
today = datetime.date.today()


class AdministratorAccessTest(TestCase):
    def test_otheruser_not_access_user_management_modules(self):
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = other_id
        request.session['is_superuser'] = other_is_superuser
        request.session['first_name'] = admin_first_name
        request.session['last_name'] = admin_last_name
        #view users
        response = view_users(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/todo/unauthorized')
        #add user
        response = add_user(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/todo/unauthorized')
        #delete user
        User.objects.create(id=other_id, password=other_password, is_superuser=other_is_superuser, first_name=other_first_name, last_name=other_last_name, email=other_email, is_staff=other_is_staff, is_active=other_is_active)
        response = delete_user(request, other_id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/todo/unauthorized')
    
    def test_administrator_access_to_user_management_modules(self):
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = admin_id
        request.session['is_superuser'] = admin_is_superuser
        request.session['first_name'] = admin_first_name
        request.session['last_name'] = admin_last_name
        #view users
        response = view_users(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn("List of users", response.content.decode())
        #add user
        response = add_user(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Add User", response.content.decode())
        #delete user
        User.objects.create(id=other_id, password=other_password, is_superuser=other_is_superuser, first_name=other_first_name, last_name=other_last_name, email=other_email, is_staff=other_is_staff, is_active=other_is_active)
        response = delete_user(request, other_id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/todo/view_users')
        
    def test_view_user_link_not_visible_to_other_user(self):
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = admin_id
        request.session['is_superuser'] = other_is_superuser
        request.session['first_name'] = other_first_name
        request.session['last_name'] = other_last_name
        response = home_page(request)
        self.assertNotIn("View Users", response.content.decode())
        
    def test_view_user_link_visible_to_administrator(self):
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = admin_id
        request.session['is_superuser'] = admin_is_superuser
        request.session['first_name'] = admin_first_name
        request.session['last_name'] = admin_last_name
        response = home_page(request)
        self.assertIn("View Users", response.content.decode())
        
class ViewUsersPageTest(TestCase):
    
    def test_is_list_of_users_displayed(self):
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = admin_id
        request.session['is_superuser'] = admin_is_superuser
        request.session['first_name'] = admin_first_name
        request.session['last_name'] = admin_last_name
        response = view_users(request)
        self.assertIn("List of users", response.content.decode())

    def test_is_user_info_displayed(self):
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = admin_id
        request.session['is_superuser'] = admin_is_superuser
        request.session['first_name'] = admin_first_name
        request.session['last_name'] = admin_last_name
        User.objects.create(id=other_id, password=other_password, is_superuser=other_is_superuser, first_name=other_first_name, last_name=other_last_name, email=other_email, is_staff=other_is_staff, is_active=other_is_active)
        response = view_users(request)
        self.assertEqual(User.objects.all().count(), 1)
        self.assertIn(other_username, response.content.decode())
        
    def test_other_user_has_delete(self):
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = admin_id
        request.session['is_superuser'] = admin_is_superuser
        request.session['first_name'] = admin_first_name
        request.session['last_name'] = admin_last_name
        User.objects.create(id=other_id, password=other_password, is_superuser=other_is_superuser, first_name=other_first_name, last_name=other_last_name, email=other_email, is_staff=other_is_staff, is_active=other_is_active)
        response = view_users(request)
        self.assertEqual(User.objects.all().count(), 1)
        self.assertIn("Delete", response.content.decode())
    
    def test_admistrator_has_no_delete(self):
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = admin_id
        request.session['is_superuser'] = admin_is_superuser
        request.session['first_name'] = admin_first_name
        request.session['last_name'] = admin_last_name
        import datetime
        User.objects.create(id=admin_id, password=admin_password, is_superuser=admin_is_superuser, first_name=admin_first_name, last_name=admin_last_name, email=admin_email, is_staff=admin_is_staff, is_active=admin_is_active)
        response = view_users(request)
        self.assertEqual(User.objects.all().count(), 1)
        self.assertNotIn("Delete", response.content.decode())
        
    def test_if_user_is_deleted(self):
        User.objects.create(id=other_id, password=other_password, is_superuser=other_is_superuser, first_name=other_first_name, last_name=other_last_name, email=other_email, is_staff=other_is_staff, is_active=other_is_active)
        self.assertEqual(User.objects.all().count(), 1)
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = admin_id
        request.session['is_superuser'] = admin_is_superuser
        request.session['first_name'] = admin_first_name
        request.session['last_name'] = admin_last_name
        response = delete_user(request, other_id)
        
        
    
    
class AddUserPageTest(TestCase):
    #import datetime
    #User.objects.create(id=other_id, password=other_password, last_login=datetime.datetime.now(), is_superuser=other_is_superuser, first_name=other_first_name, last_name=other_last_name, email=other_email, is_staff=other_is_staff, is_active=other_is_active, date_joined=datetime.datetime.now())
    def test_if_adduser_form_required_fields_present(self):
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = admin_id
        request.session['is_superuser'] = admin_is_superuser
        request.session['first_name'] = admin_first_name
        request.session['last_name'] = admin_last_name
        response = add_user(request)
        self.assertIn("Username:", response.content.decode())
        self.assertIn("Password:", response.content.decode())
        self.assertIn("Email:", response.content.decode())
        self.assertIn("First name:", response.content.decode())
        self.assertIn("Last name:", response.content.decode())
        self.assertIn("<input type='submit' name='submit' value='Add User' />", response.content.decode())
        
    def test_if_user_added(self):
        request = HttpRequest()
        request.method = "POST"
        request.POST["username"]=other_username
        request.POST["password1"]=other_password
        request.POST["password2"]=other_password
        request.POST["last_login"]=timezone.now()
        request.POST["is_superuser"]=other_is_superuser
        request.POST["first_name"]=other_first_name
        request.POST["last_name"]=other_last_name
        request.POST["email"]=other_email
        request.POST["is_staff"]=other_is_staff
        request.POST["is_active"]=other_is_active
        request.POST["date_joined"]=timezone.now()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = admin_id
        request.session['is_superuser'] = admin_is_superuser
        request.session['first_name'] = admin_first_name
        request.session['last_name'] = admin_last_name
        response = add_user(request)
        self.assertEqual(User.objects.all().count(), 1)
    
class HomePageTest(TestCase):

    def test_home_page_displays_only_todos_added(self):
        ToDo.objects.create(item='Code unit test', added_by=admin_id, date_todo=today, archive='0')
        ToDo.objects.create(item='Fix code', added_by=other_id, date_todo=today, archive='0')
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = admin_id
        request.session['is_superuser'] = admin_is_superuser
        request.session['first_name'] = admin_first_name
        request.session['last_name'] = admin_last_name
        response = home_page(request)
        self.assertIn('Code unit test', response.content.decode())
        self.assertNotIn('Fix code', response.content.decode())
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = other_id
        request.session['is_superuser'] = other_is_superuser
        request.session['first_name'] = other_first_name
        request.session['last_name'] = other_last_name
        response = home_page(request)
        self.assertNotIn('Code unit test', response.content.decode())
        self.assertIn('Fix code', response.content.decode())

    def test_home_page_display_current_date(self):
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = admin_id
        request.session['is_superuser'] = admin_is_superuser
        request.session['first_name'] = admin_first_name
        request.session['last_name'] = admin_last_name
        response = home_page(request)
        import time
        current_date = time.strftime('%Y-%m-%d')
        self.assertIn(current_date, response.content.decode())

    def test_home_page_displays_todolist(self):
        ToDo.objects.create(item='Code unit test', added_by='1', date_todo=today, archive='0')
        ToDo.objects.create(item='Fix code', added_by='1', date_todo=today, archive='0')
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = admin_id
        request.session['is_superuser'] = admin_is_superuser
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
        request.session['is_superuser'] = admin_is_superuser
        request.session['first_name'] = admin_first_name
        request.session['last_name'] = admin_last_name
        response = home_page(request)
        self.assertIn('To do list is empty', response.content.decode())
        
    
    def test_home_page_transfer_pending_todos_to_current_day(self):
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
        request.session['is_superuser'] = admin_is_superuser
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
        ToDo.objects.create(item='Code unit test 1', added_by='1', date_todo=today, archive='2')
        ToDo.objects.create(item='Code unit test 2', added_by='1', date_todo=today, archive='1')
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = admin_id
        request.session['is_superuser'] = admin_is_superuser
        request.session['first_name'] = admin_first_name
        request.session['last_name'] = admin_last_name
        response = home_page(request)
        self.assertIn('Cancelled', response.content.decode())
        self.assertIn('Done', response.content.decode())
    
        
class TodoOperationsTest(TestCase):
    def test_tick_as_done(self):
        ToDo.objects.create(id='5', item='Code unit test', added_by='1', date_todo=today, archive='0')
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = '1';
        response = tick_done(request, 5)
        self.assertEqual(ToDo.objects.get(id=5).archive, 1)

    def test_tick_as_cancelled(self):
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
        request.session['is_superuser'] = admin_is_superuser
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
        request.session['is_superuser'] = admin_is_superuser
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
        
        random_id = 1000
        
        response = tick_done(request, random_id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/accounts/unauthorized')
        
        response = tick_cancel(request, random_id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/accounts/unauthorized')
        
        response = view_users(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/accounts/unauthorized')
        
        response = add_user(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/accounts/unauthorized')
        
        response = delete_user(request, random_id)
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
        ToDo.objects.create(item='Code unit test', added_by='1', date_todo=today, archive='0')
        ToDo.objects.create(item='Fix code', added_by='1', date_todo=today, archive='0')
        saved_todos = ToDo.objects.all()
        self.assertEqual(saved_todos.count(), 2)
        first_saved_todo = saved_todos[0]
        second_saved_todo = saved_todos[1]
        self.assertEqual(first_saved_todo.item, 'Code unit test')
        self.assertEqual(second_saved_todo.item, 'Fix code')