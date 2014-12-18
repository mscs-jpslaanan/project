from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from django.contrib.auth.models import User
from todo.models import ToDo

import time
current_date = time.strftime('%Y-%m-%d')
current_year = time.strftime('%Y')
current_day = time.strftime('%d')
current_month = time.strftime('%m')

import datetime
one_day = datetime.timedelta(days=1)
yesterday = datetime.date.today() - one_day
yesterday_date = yesterday.strftime('%Y-%m-%d')
yesterday_year = yesterday.strftime('%Y')
yesterday_day = yesterday.strftime('%d')
yesterday_month = yesterday.strftime('%m')

tomorrow = datetime.date.today() + one_day
tomorrow_date = tomorrow.strftime('%Y-%m-%d')
tomorrow_year = tomorrow.strftime('%Y')
tomorrow_day = tomorrow.strftime('%d')
tomorrow_month = tomorrow.strftime('%m')


admin_username = 'admin'
admin_password = 'admin'
admin_first_name='first'
admin_last_name='last'
admin_password='admin'
admin_email='admin@example.com'



class AdministratorTest(LiveServerTestCase):
    def setUp(self):
        User.objects.create_superuser(
            username=admin_username,
            first_name=admin_first_name,
            last_name=admin_last_name,
            password=admin_password,
            email=admin_email
        )
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)
    
    def tearDown(self):
        self.browser.quit()
   
    def test_features(self):
        
        
        # ==============================
        # LOGIN PAGE
        # ==============================
        self.browser.get(self.live_server_url)
        self.assertEqual('Login', self.browser.title)
        usernameBox = self.browser.find_element_by_id('username')
        self.assertEqual(
                usernameBox.get_attribute('type'),
                'text'
        )
        passwordBox = self.browser.find_element_by_id('password')
        self.assertEqual(
                passwordBox.get_attribute('type'),
                'password'
        )
        submitButton = self.browser.find_element_by_id('submit')
        self.assertEqual(
                submitButton.get_attribute('type'),
                'submit'
        )
        usernameBox.send_keys(admin_username)
        passwordBox.send_keys(admin_password)
        submitButton.click()
        
        # ==============================
        # HOME PAGE
        # ==============================
        #title check
        self.assertEqual('Home', self.browser.title)
        self.check_current_date_and_fullname_display()
        fullname = admin_first_name + " " + admin_last_name
        self.assertIn(fullname, self.browser.find_element_by_tag_name('body').text )
        #empty todo list check
        self.assertIn("To do list is empty", self.browser.find_element_by_tag_name('body').text )
        
        # ==============================
        # ADD TODO PAGE
        # ==============================
        self.go_to_page_and_check_title("Add to do item", "Add to do item")
        self.check_form_web_element_type("item", "text")
        self.check_form_web_element_type("date_todo_month", "select-one")
        self.check_form_web_element_type("date_todo_day", "select-one")
        self.check_form_web_element_type("date_todo_year", "select-one")
        
        #add todos for today
        self.add_todo("Item 1", current_month, current_day, current_year)
        self.check_item_in_list("Item 1")
        
        #Check ticks for each pending item
        self.check_item_in_list("Done Cancel Transfer date")
        
        self.go_to_page_and_check_title("Add to do item", "Add to do item")
        self.add_todo("Item 2", current_month, current_day, current_year)
        self.check_item_in_list("Item 2")
        
        self.go_to_page_and_check_title("Add to do item", "Add to do item")
        self.add_todo("Item 3", current_month, current_day, current_year)
        self.check_item_in_list("Item 3")
        
        self.go_to_page_and_check_title("Add to do item", "Add to do item")
        self.add_todo("Item 4", current_month, current_day, current_year)
        self.check_item_in_list("Item 4")
        
        today = datetime.date.today()
        first_day_current = datetime.datetime(today.year, today.month, 1)
        if(today.month == 12):
            first_day_next_month = datetime.datetime(today.year+1, 1, 1)
        else:
            first_day_next_month = datetime.datetime(today.year, today.month+1, 1)
        one_day = datetime.timedelta(days=1)
        last_day_current = first_day_next_month - one_day
    
        self.go_to_page_and_check_title("Add to do item", "Add to do item")
        self.add_todo("Item 5", last_day_current.strftime('%m'), last_day_current.strftime('%d'), last_day_current.strftime('%Y'))
        self.check_item_not_in_list("Item 5")
        
        # ==============================
        # TICK AS DONE
        # ==============================
        self.browser.find_element_by_xpath("(//a[contains(text(),'Done')])[1]").click()
        self.check_item_in_list("Item 3")
        self.check_item_in_list("Done")
        
        # ==============================
        # TICK AS CANCELLED
        # ==============================
        self.browser.find_element_by_xpath("(//a[contains(text(),'Cancel')])[2]").click()
        self.check_item_in_list("Cancelled")
        
        # ==============================
        # VIEW USER PAGE
        # ==============================
        self.go_to_page_and_check_title("View Users", "User List")
        
        # ==============================
        # ADD USER PAGE
        # ==============================
        self.go_to_page_and_check_title("Add User", "Add User")
        #check fields
        self.check_form_web_element_type("username", "text")
        self.check_form_web_element_type("password1", "password")
        self.check_form_web_element_type("password2", "password")
        self.check_form_web_element_type("first_name", "text")
        self.check_form_web_element_type("last_name", "text")
        self.check_form_web_element_type("email", "email")
        #add user
        self.add_user(other_username, other_password, other_first_name, other_last_name, other_email)
        self.check_item_in_list(other_username)
        
        # ==============================
        # DELETE USER
        # ==============================
        self.browser.find_element_by_link_text("Delete").click()
        self.check_item_not_in_list(other_username)
        
        # ==============================
        # ADD RECURRING TO DO
        # ==============================
        self.go_to_page_and_check_title("Add recurring todo item", "Add recurring todo item")
        #check fields
        self.check_form_web_element_type("item", "text")
        self.check_form_web_element_type("start_date_month", "select-one")
        self.check_form_web_element_type("start_date_day", "select-one")
        self.check_form_web_element_type("start_date_year", "select-one")
        self.check_form_web_element_type("end_date_month", "select-one")
        self.check_form_web_element_type("end_date_day", "select-one")
        self.check_form_web_element_type("end_date_year", "select-one")
        #add recurring todo
        self.add_recurring_todo("Item Recurring", current_month, current_day, current_year, tomorrow_month, tomorrow_day, tomorrow_year)
        self.assertEqual(ToDo.objects.filter(item='Item Recurring').count() , 2)
        
        # ==============================
        # VIEW WEEKLY
        # ==============================
        self.go_to_page_and_check_title("View weekly", "Weekly ToDo")
        row_count = len(self.browser.find_elements_by_xpath("//table[@id='datatable']/tbody/tr"))
        self.assertEqual(row_count-1,6)
        
        # ==============================
        # VIEW MONTHLY
        # ==============================
        self.go_to_page_and_check_title("View monthly", "Monthly ToDo")
        row_count = len(self.browser.find_elements_by_xpath("//table[@id='datatable']/tbody/tr"))
        self.assertEqual(row_count-1,7)
        
        
        # ==============================
        # TRANSFER TODO TO ANOTHER DATE
        # ==============================
        self.go_to_page_and_check_title("View daily", "Home")
        #change to yesterday (item 2)
        self.browser.find_element_by_xpath("(//a[contains(text(),'Transfer date')])[1]").click()
        
        self.check_form_web_element_type("new_date_month", "select-one")
        self.check_form_web_element_type("new_date_day", "select-one")
        self.check_form_web_element_type("new_date_year", "select-one")
        self.assertEqual("Transfer todo item date", self.browser.title)
        self.check_current_date_and_fullname_display()
        
        yesterdayTodoID = self.browser.find_element_by_name("item_id").get_attribute('value')
        self.transfer_todo_to_other_date(yesterday_month, yesterday_day, yesterday_year)
        self.assertEqual(ToDo.objects.get(id=yesterdayTodoID).date_todo.strftime('%Y-%m-%d'), yesterday_date)
        
        #change to 8 days ago and update to done (item 4)
        self.browser.find_element_by_xpath("(//a[contains(text(),'Transfer date')])[1]").click()
        eight_days = datetime.timedelta(days=8)
        today = datetime.date.today()
        eight_days_ago = today - eight_days
        eight_days_ago_year = eight_days_ago.strftime('%Y')
        eight_days_ago_month = eight_days_ago.strftime('%m')
        eight_days_ago_day = eight_days_ago.strftime('%d')
        eightDaysAgoTodoID = self.browser.find_element_by_name("item_id").get_attribute('value')
        self.transfer_todo_to_other_date(eight_days_ago_month, eight_days_ago_day, eight_days_ago_year)
        self.assertEqual(ToDo.objects.get(id=eightDaysAgoTodoID).date_todo.strftime('%Y-%m-%d'), eight_days_ago.strftime('%Y-%m-%d'))
        ToDo.objects.filter(id=eightDaysAgoTodoID).update(archive=1)
        
        
        # ==============================
        # LOG OUT PAGE
        # ==============================
        self.browser.find_element_by_link_text('Logout').click()
        self.assertIn( "Logged out!", self.browser.find_element_by_tag_name('body').text)
        
        # ==============================
        # LOG IN
        # ==============================
        self.browser.find_element_by_link_text("here").click()
        self.assertEqual("Login", self.browser.title)
        usernameBox = self.browser.find_element_by_id('username')
        passwordBox = self.browser.find_element_by_id('password')
        submitButton = self.browser.find_element_by_id('submit')
        usernameBox.send_keys(admin_username)
        passwordBox.send_keys(admin_password)
        submitButton.click()
    
        # ==============================
        # CHECK IF PENDING ITEMS ARE TRANSFERRED TO TODAY
        # ==============================
        self.assertEqual(ToDo.objects.get(id=yesterdayTodoID).date_todo.strftime('%Y-%m-%d'), datetime.date.today().strftime('%Y-%m-%d'))
        
        # ==============================
        # CHECK IF DONE / CANCELLED DATA < 7 DAYS FROM TODAY IS PURGED
        # ==============================
        self.assertEqual(ToDo.objects.filter(id=eightDaysAgoTodoID).all().count(), 0)
    
    def transfer_todo_to_other_date(self, new_monthTodo, new_dayTodo, new_yearTodo):
        monthBox = self.browser.find_element_by_name('new_date_month')
        self.select_option_in_dropdown(monthBox, new_monthTodo)
        dayBox = self.browser.find_element_by_name('new_date_day')
        self.select_option_in_dropdown(dayBox, new_dayTodo)
        yearBox = self.browser.find_element_by_name('new_date_year')
        self.select_option_in_dropdown(yearBox, new_yearTodo)
        self.browser.find_element_by_name('submit').click()
        
    def add_recurring_todo(self, item, cur_monthTodo, cur_dayTodo, cur_yearTodo, tom_monthTodo, tom_dayTodo, tom_yearTodo):
        self.browser.find_element_by_name('item').send_keys(item)
        
        monthBox = self.browser.find_element_by_name('start_date_month')
        self.select_option_in_dropdown(monthBox, cur_monthTodo)
        dayBox = self.browser.find_element_by_name('start_date_day')
        self.select_option_in_dropdown(dayBox, cur_dayTodo)
        yearBox = self.browser.find_element_by_name('start_date_year')
        self.select_option_in_dropdown(yearBox, cur_yearTodo)
        
        monthBox = self.browser.find_element_by_name('end_date_month')
        self.select_option_in_dropdown(monthBox, tom_monthTodo)
        dayBox = self.browser.find_element_by_name('end_date_day')
        self.select_option_in_dropdown(dayBox, tom_dayTodo)
        yearBox = self.browser.find_element_by_name('end_date_year')
        self.select_option_in_dropdown(yearBox, tom_yearTodo)
        
        self.browser.find_element_by_name('submit').click()
    
    
    def add_user(self, username, password, first_name, last_name, email):
        self.browser.find_element_by_name('username').send_keys(username)
        self.browser.find_element_by_name('password1').send_keys(password)
        self.browser.find_element_by_name('password2').send_keys(password)
        self.browser.find_element_by_name('first_name').send_keys(first_name)
        self.browser.find_element_by_name('last_name').send_keys(last_name)
        self.browser.find_element_by_name('email').send_keys(email)
        self.browser.find_element_by_name('submit').click()
    
    def add_todo(self, todoItem, monthTodo, dayTodo, yearTodo):
        self.browser.find_element_by_name('item').send_keys(todoItem)
        monthBox = self.browser.find_element_by_name('date_todo_month')
        self.select_option_in_dropdown(monthBox, monthTodo)
        dayBox = self.browser.find_element_by_name('date_todo_day')
        self.select_option_in_dropdown(dayBox, dayTodo)
        yearBox = self.browser.find_element_by_name('date_todo_year')
        self.select_option_in_dropdown(yearBox, yearTodo)
        submitButton = self.browser.find_element_by_name('submit')
        submitButton.click()
    
    def check_form_web_element_type(self, web_element_name, web_element_type):
        web_element = self.browser.find_element_by_name(web_element_name)
        self.assertEqual(
                web_element.get_attribute('type'),
                web_element_type
        )
    
    def go_to_page_and_check_title(self, pageLink, title):
        self.browser.find_element_by_link_text(pageLink).click()
        self.assertEqual(title, self.browser.title)
        self.check_current_date_and_fullname_display()
    
    def check_current_date_and_fullname_display(self):
        #current date display
        self.assertIn(current_date, self.browser.
        find_element_by_tag_name('body').text )
        #full name display
        fullname = admin_first_name + " " + admin_last_name
        self.assertIn(fullname, self.browser.find_element_by_tag_name('body').text )
    
    def check_item_in_list(self, row_text):
        table = self.browser.find_element_by_tag_name('table')
        self.assertIn(row_text, table.text)
        #rows = table.find_elements_by_tag_name('tr')
        #self.assertIn(row_text, [row.text for row in rows])
    
    def check_item_not_in_list(self, row_text):
        table = self.browser.find_element_by_tag_name('table')
        self.assertNotIn(row_text, table.text)
        
    def select_option_in_dropdown(self, dropdown_web_element, value):
        dropdownSelector = Select(dropdown_web_element)
        dropdownSelector.select_by_value(value)

        
