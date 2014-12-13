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
    
    def test_home_page_displays_added_todo(self):
        ToDo.objects.create(item='Code unit test', added_by='1', date_todo='2014-12-13', archive='0')
        
        request = HttpRequest()
        response = home_page(request)
        
        self.assertIn('Code unit test', response.content.decode())