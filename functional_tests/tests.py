from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys



class NewVisitorTest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)
    
    def tearDown(self):
        self.browser.quit()
    
    def test_display_current_date(self):

        # Edith has heard about a cool new online to-do app. She goes
        # to check out its homepage
        self.browser.get(self.live_server_url)

       
        self.fail('Finish the test!')
