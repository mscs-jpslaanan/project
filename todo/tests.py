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

ADMIN_ID = 1
ADMIN_PASSWORD = "patster"
ADMIN_IS_SUPERUSER = 1
ADMIN_USERNAME = "patster"
ADMIN_FIRST_NAME = "patrick"
ADMIN_LAST_NAME = "la-anan"
ADMIN_EMAIL = "john_patrick_laanan@yahoo.com"
ADMIN_IS_STAFF = 1
ADMIN_IS_ACTIVE = 1

OTHER_ID = 500
OTHER_PASSWORD = "otheruser"
OTHER_IS_SUPERUSER = 0
OTHER_USERNAME = "otheruser"
OTHER_FIRST_NAME = "other"
OTHER_LAST_NAME = "user"
OTHER_EMAIL = "otheruser@otheruser.com"
OTHER_IS_STAFF = 1
OTHER_IS_ACTIVE = 1

import datetime
TODAY = datetime.date.today()

class HistoryOperationsTest(TestCase):
    def test_purge_data_after_7_days(self):
        seven_days = datetime.timedelta(days=7)
        eight_days = datetime.timedelta(days=8)
        three_days = datetime.timedelta(days=3)
        
        eight_days_ago = TODAY - eight_days
        seven_days_ago = TODAY - seven_days
        three_days_ago = TODAY - three_days
        three_days_from_today = TODAY + three_days
        
        item1 = 'Code unit test 1'
        item2 = 'Code unit test 2'
        item3 = 'Code unit test 3'
        item4 = 'Code unit test 4'
        item5 = 'Code unit test 5'
        
        ToDo.objects.create(id='1', item=item1, added_by=ADMIN_ID, date_todo=eight_days_ago, archive='1')
        ToDo.objects.create(id='2', item=item2, added_by=ADMIN_ID, date_todo=seven_days_ago, archive='2')
        ToDo.objects.create(id='3', item=item3, added_by=ADMIN_ID, date_todo=three_days_ago, archive='1')
        ToDo.objects.create(id='4', item=item4, added_by=ADMIN_ID, date_todo=TODAY, archive='2')
        ToDo.objects.create(id='5', item=item5, added_by=ADMIN_ID, date_todo=three_days_from_today, archive='1')

        saved_todos = ToDo.objects.all()
        self.assertEqual(saved_todos.count(), 5)
        todo1 = ToDo.objects.get(id=1)
        todo2 = ToDo.objects.get(id=2)
        todo3 = ToDo.objects.get(id=3)
        todo4 = ToDo.objects.get(id=4)
        todo5 = ToDo.objects.get(id=5)
        self.assertEqual(todo1.item, item1)
        self.assertEqual(todo2.item, item2)
        self.assertEqual(todo3.item, item3)
        self.assertEqual(todo4.item, item4)
        self.assertEqual(todo5.item, item5)
        
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = OTHER_ID
        request.session['is_superuser'] = OTHER_IS_SUPERUSER
        request.session['first_name'] = ADMIN_FIRST_NAME
        request.session['last_name'] = ADMIN_LAST_NAME
        
        response = home_page(request)
        
        self.assertEqual(ToDo.objects.all().count(), 4)
        self.assertEqual(ToDo.objects.get(id=1).item, '')
        self.assertEqual(ToDo.objects.get(id=2).item, item2)
        self.assertEqual(ToDo.objects.get(id=3).item, item3)
        self.assertEqual(ToDo.objects.get(id=4).item, item4)
        self.assertEqual(ToDo.objects.get(id=5).item, item5)
        

class AdministratorAccessTest(TestCase):
    def test_otheruser_not_access_user_management_modules(self):
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = OTHER_ID
        request.session['is_superuser'] = OTHER_IS_SUPERUSER
        request.session['first_name'] = OTHER_FIRST_NAME
        request.session['last_name'] = OTHER_LAST_NAME
        #view users
        response = view_users(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/todo/unauthorized')
        #add user
        response = add_user(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/todo/unauthorized')
        #delete user
        User.objects.create(id=OTHER_ID, password=OTHER_PASSWORD, is_superuser=OTHER_IS_SUPERUSER, first_name=OTHER_FIRST_NAME, last_name=OTHER_LAST_NAME, email=OTHER_EMAIL, is_staff=OTHER_IS_STAFF, is_active=OTHER_IS_ACTIVE)
        response = delete_user(request, OTHER_ID)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/todo/unauthorized')
    
    def test_administrator_access_to_user_management_modules(self):
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = ADMIN_ID
        request.session['is_superuser'] = ADMIN_IS_SUPERUSER
        request.session['first_name'] = ADMIN_FIRST_NAME
        request.session['last_name'] = ADMIN_LAST_NAME
        #view users
        response = view_users(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn("List of users", response.content.decode())
        #add user
        response = add_user(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Add User", response.content.decode())
        #delete user
        User.objects.create(id=OTHER_ID, password=OTHER_PASSWORD, is_superuser=OTHER_IS_SUPERUSER, first_name=OTHER_FIRST_NAME, last_name=OTHER_LAST_NAME, email=OTHER_EMAIL, is_staff=OTHER_IS_STAFF, is_active=OTHER_IS_ACTIVE)
        response = delete_user(request, OTHER_ID)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/todo/view_users')
        
    def test_view_user_link_not_visible_to_other_user(self):
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = OTHER_ID
        request.session['is_superuser'] = OTHER_IS_SUPERUSER
        request.session['first_name'] = OTHER_FIRST_NAME
        request.session['last_name'] = OTHER_LAST_NAME
        response = home_page(request)
        self.assertNotIn("View Users", response.content.decode())
        
    def test_view_user_link_visible_to_administrator(self):
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = ADMIN_ID
        request.session['is_superuser'] = ADMIN_IS_SUPERUSER
        request.session['first_name'] = ADMIN_FIRST_NAME
        request.session['last_name'] = ADMIN_LAST_NAME
        response = home_page(request)
        self.assertIn("View Users", response.content.decode())
        
class ViewUsersPageTest(TestCase):
    
    def test_is_list_of_users_displayed(self):
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = ADMIN_ID
        request.session['is_superuser'] = ADMIN_IS_SUPERUSER
        request.session['first_name'] = ADMIN_FIRST_NAME
        request.session['last_name'] = ADMIN_LAST_NAME
        response = view_users(request)
        self.assertIn("List of users", response.content.decode())

    def test_is_user_info_displayed(self):
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = ADMIN_ID
        request.session['is_superuser'] = ADMIN_IS_SUPERUSER
        request.session['first_name'] = ADMIN_FIRST_NAME
        request.session['last_name'] = ADMIN_LAST_NAME
        User.objects.create(id=OTHER_ID, password=OTHER_PASSWORD, is_superuser=OTHER_IS_SUPERUSER, first_name=OTHER_FIRST_NAME, last_name=OTHER_LAST_NAME, email=OTHER_EMAIL, is_staff=OTHER_IS_STAFF, is_active=OTHER_IS_ACTIVE)
        response = view_users(request)
        self.assertEqual(User.objects.all().count(), 1)
        self.assertIn(OTHER_USERNAME, response.content.decode())
        
    def test_other_user_has_delete(self):
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = ADMIN_ID
        request.session['is_superuser'] = ADMIN_IS_SUPERUSER
        request.session['first_name'] = ADMIN_FIRST_NAME
        request.session['last_name'] = ADMIN_LAST_NAME
        User.objects.create(id=OTHER_ID, password=OTHER_PASSWORD, is_superuser=OTHER_IS_SUPERUSER, first_name=OTHER_FIRST_NAME, last_name=OTHER_LAST_NAME, email=OTHER_EMAIL, is_staff=OTHER_IS_STAFF, is_active=OTHER_IS_ACTIVE)
        response = view_users(request)
        self.assertEqual(User.objects.all().count(), 1)
        self.assertIn("Delete", response.content.decode())
    
    def test_admistrator_has_no_delete(self):
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = ADMIN_ID
        request.session['is_superuser'] = ADMIN_IS_SUPERUSER
        request.session['first_name'] = ADMIN_FIRST_NAME
        request.session['last_name'] = ADMIN_LAST_NAME
        import datetime
        User.objects.create(id=ADMIN_ID, password=ADMIN_PASSWORD, is_superuser=ADMIN_IS_SUPERUSER, first_name=ADMIN_FIRST_NAME, last_name=ADMIN_LAST_NAME, email=ADMIN_EMAIL, is_staff=ADMIN_IS_STAFF, is_active=ADMIN_IS_ACTIVE)
        response = view_users(request)
        self.assertEqual(User.objects.all().count(), 1)
        self.assertNotIn("Delete", response.content.decode())
        
    def test_if_user_is_deleted(self):
        User.objects.create(id=OTHER_ID, password=OTHER_PASSWORD, is_superuser=OTHER_IS_SUPERUSER, first_name=OTHER_FIRST_NAME, last_name=OTHER_LAST_NAME, email=OTHER_EMAIL, is_staff=OTHER_IS_STAFF, is_active=OTHER_IS_ACTIVE)
        self.assertEqual(User.objects.all().count(), 1)
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = ADMIN_ID
        request.session['is_superuser'] = ADMIN_IS_SUPERUSER
        request.session['first_name'] = ADMIN_FIRST_NAME
        request.session['last_name'] = ADMIN_LAST_NAME
        response = delete_user(request, OTHER_ID)
        
        
    
    
class AddUserPageTest(TestCase):
    #import datetime
    #User.objects.create(id=OTHER_ID, password=OTHER_PASSWORD, last_login=datetime.datetime.now(), is_superuser=OTHER_IS_SUPERUSER, first_name=OTHER_FIRST_NAME, last_name=OTHER_LAST_NAME, email=OTHER_EMAIL, is_staff=OTHER_IS_STAFF, is_active=OTHER_IS_ACTIVE, date_joined=datetime.datetime.now())
    def test_if_adduser_form_required_fields_present(self):
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = ADMIN_ID
        request.session['is_superuser'] = ADMIN_IS_SUPERUSER
        request.session['first_name'] = ADMIN_FIRST_NAME
        request.session['last_name'] = ADMIN_LAST_NAME
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
        request.POST["username"]=OTHER_USERNAME
        request.POST["password1"]=OTHER_PASSWORD
        request.POST["password2"]=OTHER_PASSWORD
        request.POST["last_login"]=timezone.now()
        request.POST["is_superuser"]=OTHER_IS_SUPERUSER
        request.POST["first_name"]=OTHER_FIRST_NAME
        request.POST["last_name"]=OTHER_LAST_NAME
        request.POST["email"]=OTHER_EMAIL
        request.POST["is_staff"]=OTHER_IS_STAFF
        request.POST["is_active"]=OTHER_IS_ACTIVE
        request.POST["date_joined"]=timezone.now()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = ADMIN_ID
        request.session['is_superuser'] = ADMIN_IS_SUPERUSER
        request.session['first_name'] = ADMIN_FIRST_NAME
        request.session['last_name'] = ADMIN_LAST_NAME
        response = add_user(request)
        self.assertEqual(User.objects.all().count(), 1)
    
class HomePageTest(TestCase):

    def test_home_page_displays_only_todos_added(self):
        ToDo.objects.create(item='Code unit test', added_by=ADMIN_ID, date_todo=TODAY, archive='0')
        ToDo.objects.create(item='Fix code', added_by=OTHER_ID, date_todo=TODAY, archive='0')
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = ADMIN_ID
        request.session['is_superuser'] = ADMIN_IS_SUPERUSER
        request.session['first_name'] = ADMIN_FIRST_NAME
        request.session['last_name'] = ADMIN_LAST_NAME
        response = home_page(request)
        self.assertIn('Code unit test', response.content.decode())
        self.assertNotIn('Fix code', response.content.decode())
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = OTHER_ID
        request.session['is_superuser'] = OTHER_IS_SUPERUSER
        request.session['first_name'] = OTHER_FIRST_NAME
        request.session['last_name'] = OTHER_LAST_NAME
        response = home_page(request)
        self.assertNotIn('Code unit test', response.content.decode())
        self.assertIn('Fix code', response.content.decode())

    def test_home_page_display_current_date(self):
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = ADMIN_ID
        request.session['is_superuser'] = ADMIN_IS_SUPERUSER
        request.session['first_name'] = ADMIN_FIRST_NAME
        request.session['last_name'] = ADMIN_LAST_NAME
        response = home_page(request)
        import time
        current_date = time.strftime('%Y-%m-%d')
        self.assertIn(current_date, response.content.decode())

    def test_home_page_displays_todolist(self):
        ToDo.objects.create(item='Code unit test', added_by='1', date_todo=TODAY, archive='0')
        ToDo.objects.create(item='Fix code', added_by='1', date_todo=TODAY, archive='0')
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = ADMIN_ID
        request.session['is_superuser'] = ADMIN_IS_SUPERUSER
        request.session['first_name'] = ADMIN_FIRST_NAME
        request.session['last_name'] = ADMIN_LAST_NAME
        response = home_page(request)
        self.assertIn('Code unit test', response.content.decode())
        self.assertIn('Fix code', response.content.decode())
        
    def test_home_page_displays_prompt_on_empty_todolist(self):
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = ADMIN_ID
        request.session['is_superuser'] = ADMIN_IS_SUPERUSER
        request.session['first_name'] = ADMIN_FIRST_NAME
        request.session['last_name'] = ADMIN_LAST_NAME
        response = home_page(request)
        self.assertIn('To do list is empty', response.content.decode())
        
    
    def test_home_page_transfer_pending_todos_to_current_day(self):
        one_day = datetime.timedelta(days=1)
        yesterday = TODAY - one_day
        tomorrow = TODAY + one_day
        
        #Done
        ToDo.objects.create(item='Code unit test 1', added_by='1', date_todo=yesterday, archive='1')
        #Cancelled
        ToDo.objects.create(item='Code unit test 2', added_by='1', date_todo=yesterday, archive='2')
        #Pending
        ToDo.objects.create(item='Fix code', added_by='1', date_todo=yesterday, archive='0')
        
        #Current
        ToDo.objects.create(item='Rerun the unit test', added_by='1', date_todo=TODAY, archive='0')
        
        #Future
        ToDo.objects.create(item='Refactor', added_by='1', date_todo=tomorrow, archive='0')
        
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = ADMIN_ID
        request.session['is_superuser'] = ADMIN_IS_SUPERUSER
        request.session['first_name'] = ADMIN_FIRST_NAME
        request.session['last_name'] = ADMIN_LAST_NAME
        response = home_page(request)
        self.assertNotIn('Code unit test 1', response.content.decode())
        self.assertNotIn('Code unit test 2', response.content.decode())
        self.assertIn('Fix code', response.content.decode())
        self.assertIn('Rerun the unit test', response.content.decode())
        self.assertNotIn('Refactor', response.content.decode())
        self.assertEqual(ToDo.objects.filter(date_todo=TODAY).count(), 2);
    
    def test_home_page_check_for_cancel_and_done_labels(self):
        ToDo.objects.create(item='Code unit test 1', added_by='1', date_todo=TODAY, archive='2')
        ToDo.objects.create(item='Code unit test 2', added_by='1', date_todo=TODAY, archive='1')
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = ADMIN_ID
        request.session['is_superuser'] = ADMIN_IS_SUPERUSER
        request.session['first_name'] = ADMIN_FIRST_NAME
        request.session['last_name'] = ADMIN_LAST_NAME
        response = home_page(request)
        self.assertIn('Cancelled', response.content.decode())
        self.assertIn('Done', response.content.decode())
    
        
class TodoOperationsTest(TestCase):
    def test_tick_as_done(self):
        ToDo.objects.create(id='5', item='Code unit test', added_by='1', date_todo=TODAY, archive='0')
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = '1';
        response = tick_done(request, 5)
        self.assertEqual(ToDo.objects.get(id=5).archive, 1)

    def test_tick_as_cancelled(self):
        ToDo.objects.create(id='5', item='Code unit test', added_by='1', date_todo=TODAY, archive='0')
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
        request.session['id'] = ADMIN_ID
        request.session['is_superuser'] = ADMIN_IS_SUPERUSER
        request.session['first_name'] = ADMIN_FIRST_NAME
        request.session['last_name'] = ADMIN_LAST_NAME
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
        request.POST["item"] = "Code unit test"
        request.POST["date_todo"] = TODAY
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['id'] = ADMIN_ID
        request.session['is_superuser'] = ADMIN_IS_SUPERUSER
        request.session['first_name'] = ADMIN_FIRST_NAME
        request.session['last_name'] = ADMIN_LAST_NAME
        response = addtodo(request)
        saved_todos = ToDo.objects.all()
        self.assertEqual(saved_todos.count(), 1)
        

class SecurityTest(TestCase):
    def test_successful_login(self):
        request = HttpRequest()
        request.method = "POST"
        request.POST["username"] = ADMIN_USERNAME
        request.POST["password"] = ADMIN_PASSWORD
        response = auth_view(request)
        #self.assertEqual(response.status_code, 302)
        #self.assertEqual(response['location'], '/todo/home')
    
    def test_logout_if_session_variables_are_unset(self):
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.session['username'] = ADMIN_USERNAME
        request.session['id'] = ADMIN_ID
        request.session['is_superuser'] = ADMIN_IS_SUPERUSER
        request.session['first_name'] = ADMIN_FIRST_NAME
        request.session['last_name'] = ADMIN_LAST_NAME
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
        
        request.session['username'] = ADMIN_USERNAME
        request.session['id'] = ADMIN_ID
        request.session['is_superuser'] = ADMIN_IS_SUPERUSER
        request.session['first_name'] = ADMIN_FIRST_NAME
        request.session['last_name'] = ADMIN_LAST_NAME
        
        response = logout(request)
        self.assertIn("Logged out!", response.content.decode())
        
class TodoModelTest(TestCase):

    def test_saving_and_retrieving_todoList(self):
        ToDo.objects.create(item='Code unit test', added_by='1', date_todo=TODAY, archive='0')
        ToDo.objects.create(item='Fix code', added_by='1', date_todo=TODAY, archive='0')
        saved_todos = ToDo.objects.all()
        self.assertEqual(saved_todos.count(), 2)
        first_saved_todo = saved_todos[0]
        second_saved_todo = saved_todos[1]
        self.assertEqual(first_saved_todo.item, 'Code unit test')
        self.assertEqual(second_saved_todo.item, 'Fix code')