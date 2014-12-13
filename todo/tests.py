from django.http import HttpRequest
from django.template.loader import render_to_string
from django.test import TestCase


from todo.views import home_page
from todo.views import add_todo_page

from todo.models import todo

class HomePageTest(TestCase):

    def test_home_page_display_current_date(self):
        request = HttpRequest()
        response = home_page(request)
        import time
        current_date = time.strftime('%Y-%m-%d')
        self.assertIn(current_date, response.content.decode())
    
    def test_home_page_if_it_gets_list_of_todo(self):
        request = HttpRequest()
        response = home_page(request)
        self.assertEqual(Todo.objects.count(), 1)