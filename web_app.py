from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
import requests
import json

# Replace with your Flask app URL
BASE_URL = 'http://localhost:5000'

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        layout.add_widget(Label(text='Parent Login'))
        
        self.username_input = TextInput(hint_text='Username')
        layout.add_widget(self.username_input)
        
        self.password_input = TextInput(hint_text='Password', password=True)
        layout.add_widget(self.password_input)
        
        login_btn = Button(text='Login')
        login_btn.bind(on_press=self.login)
        layout.add_widget(login_btn)
        
        register_btn = Button(text='Register')
        register_btn.bind(on_press=self.go_to_register)
        layout.add_widget(register_btn)
        
        self.add_widget(layout)
    
    def login(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        response = requests.post(f'{BASE_URL}/api/parent_login', json={'username': username, 'password': password})
        if response.status_code == 200:
            data = response.json()
            self.manager.get_screen('dashboard').parent_id = data['parent_id']
            self.manager.current = 'dashboard'
        else:
            print('Login failed')
    
    def go_to_register(self, instance):
        self.manager.current = 'register'

class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        layout.add_widget(Label(text='Parent Registration'))
        
        self.username_input = TextInput(hint_text='Username')
        layout.add_widget(self.username_input)
        
        self.password_input = TextInput(hint_text='Password', password=True)
        layout.add_widget(self.password_input)
        
        self.mobile_input = TextInput(hint_text='Mobile Number')
        layout.add_widget(self.mobile_input)
        
        # For simplicity, assume student selection is done via ID
        self.student_id_input = TextInput(hint_text='Student ID')
        layout.add_widget(self.student_id_input)
        
        register_btn = Button(text='Register')
        register_btn.bind(on_press=self.register)
        layout.add_widget(register_btn)
        
        back_btn = Button(text='Back to Login')
        back_btn.bind(on_press=self.go_to_login)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def register(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        mobile = self.mobile_input.text
        student_id = self.student_id_input.text
        response = requests.post(f'{BASE_URL}/api/parent_register', json={
            'username': username,
            'password': password,
            'mobile': mobile,
            'student_id': student_id
        })
        if response.status_code == 201:
            self.manager.current = 'login'
        else:
            print('Registration failed')
    
    def go_to_login(self, instance):
        self.manager.current = 'login'

class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.parent_id = None
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.info_label = Label(text='Dashboard')
        layout.add_widget(self.info_label)
        
        update_mobile_btn = Button(text='Update Mobile')
        update_mobile_btn.bind(on_press=self.go_to_update_mobile)
        layout.add_widget(update_mobile_btn)
        
        view_attendance_btn = Button(text='View Attendance')
        view_attendance_btn.bind(on_press=self.view_attendance)
        layout.add_widget(view_attendance_btn)
        
        logout_btn = Button(text='Logout')
        logout_btn.bind(on_press=self.logout)
        layout.add_widget(logout_btn)
        
        self.add_widget(layout)
    
    def on_enter(self):
        if self.parent_id:
            response = requests.get(f'{BASE_URL}/api/parent_dashboard/{self.parent_id}')
            if response.status_code == 200:
                data = response.json()
                self.info_label.text = f"Student: {data['student_name']}\nMobile: {data['mobile']}"
    
    def go_to_update_mobile(self, instance):
        self.manager.current = 'update_mobile'
    
    def view_attendance(self, instance):
        self.manager.get_screen('attendance').parent_id = self.parent_id
        self.manager.current = 'attendance'
    
    def logout(self, instance):
        self.parent_id = None
        self.manager.current = 'login'

class UpdateMobileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        layout.add_widget(Label(text='Update Mobile Number'))
        
        self.mobile_input = TextInput(hint_text='New Mobile Number')
        layout.add_widget(self.mobile_input)
        
        update_btn = Button(text='Update')
        update_btn.bind(on_press=self.update_mobile)
        layout.add_widget(update_btn)
        
        back_btn = Button(text='Back to Dashboard')
        back_btn.bind(on_press=self.go_to_dashboard)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def update_mobile(self, instance):
        mobile = self.mobile_input.text
        parent_id = self.manager.get_screen('dashboard').parent_id
        response = requests.post(f'{BASE_URL}/api/update_mobile/{parent_id}', json={'mobile': mobile})
        if response.status_code == 200:
            self.manager.current = 'dashboard'
        else:
            print('Update failed')
    
    def go_to_dashboard(self, instance):
        self.manager.current = 'dashboard'

class AttendanceScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.parent_id = None
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        layout.add_widget(Label(text='Attendance Records'))
        
        self.scroll_view = ScrollView()
        self.grid = GridLayout(cols=2, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll_view.add_widget(self.grid)
        layout.add_widget(self.scroll_view)
        
        back_btn = Button(text='Back to Dashboard')
        back_btn.bind(on_press=self.go_to_dashboard)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def on_enter(self):
        if self.parent_id:
            response = requests.get(f'{BASE_URL}/api/parent_attendance/{self.parent_id}')
            if response.status_code == 200:
                data = response.json()
                self.grid.clear_widgets()
                for record in data:
                    self.grid.add_widget(Label(text=str(record['date'])))
                    self.grid.add_widget(Label(text=record['status']))
    
    def go_to_dashboard(self, instance):
        self.manager.current = 'dashboard'

class AttendanceApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(UpdateMobileScreen(name='update_mobile'))
        sm.add_widget(AttendanceScreen(name='attendance'))
        return sm

if __name__ == '__main__':
    AttendanceApp().run()
