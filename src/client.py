import time
import uuid
from threading import Thread
import os
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import NoTransition, Screen, ScreenManager
from kivy.uix.textinput import TextInput


import _client.badge as badge
import _shared.data as data
import directories

def print(*text):
    if len(text) == 0: text = ['']
    Logger.debug(f'{__file__}: {" ".join(str(text))}')
data.init('client')

Config.read(os.path.join(directories.__client__, 'config.ini'))
style = Builder.load_file(os.path.join(directories.__client__, 'style.kv'))
sm = ScreenManager(transition=NoTransition())
keys = [
    'q,w,e,r,t,z,u,i,o,p',
    'a,s,d,f,d,g,h,j,k,l',
    'y,x,c,v,b,n,m',
    '.,-,@,del,SPEICHERN'
]
focused = None
times = {}
badge_ = None
user = None
itemlayout = None
registration_fields = None
timeout = None

def renew_timeout():
    global timeout
    if timeout is not None:
        Clock.unschedule(timeout)
    timeout = Clock.schedule_once(logout, 10)

def login(b):
    global user
    user = data.login_user(b)
    refresh()
    sm.current = 'Kiosk'


def logout():
    global user, badge_
    user = None
    badge_ = None
    if registration_fields is not None:
        for field in registration_fields:
            field.text = ''
        Clock.schedule_once(registration_fields[0].refocus, 0.1)
    sm.current = 'Login'

def refresh(content='all'):
    if content == 'balance':
        KS.ids['balance'].text = str(user.balance) + ' CHF'
    elif content == 'userinformation':
        KS.ids['balance'].text = str(user.balance) + ' CHF'
        KS.ids['name'].text = user.firstname + '\n' + user.lastname
        KS.ids['avatar'].source = user.avatar
    elif content == 'products':
        itemlayout.refresh()
    elif content == 'all':
        refresh('balance')
        refresh('userinformation')
        refresh('products')


def on_badge(b):
    global badge_
    logout()
    print(b, badge_)
    if b != badge_:
        renew_timeout()
        badge_ = b
        if data.user_exists(b):
            login(b)
        else:
            sm.current = 'Register'


class Keyboard(BoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.orientation = 'vertical'
        for y in keys:
            row = BoxLayout()
            row.orientation = 'horizontal'
            for x in y.upper().split(','):
                row.add_widget(
                    Button(text=x, font_size=30, on_press=self.on_press))
            self.add_widget(row)

    def on_press(self, instance):
        renew_timeout()
        global times, user, registration_fields
        if focused is not None:
            Clock.schedule_once(focused.refocus, 0.1)
            
        # logger.debug('Application: '+time.time() - times.get(instance.text, time.time() - 100))
        if time.time() - times.get(instance.text, time.time() - 100) > .05:
            times.update({instance.text: time.time()})
            # logger.debug('Application: '+instance.text)
            if focused is not None:
                if instance.text not in ('DEL', 'SPEICHERN'):
                    focused.insert_text(instance.text)
                elif instance.text == 'DEL':
                    focused.do_backspace()
                elif instance.text == 'SPEICHERN':
                    firstname = self.parent.parent.ids.firstname
                    lastname = self.parent.parent.ids.lastname
                    email = self.parent.parent.ids.email
                    registration_fields = (firstname, lastname, email)
                    if '' in (firstname.text, lastname.text, email.text):
                        b = BoxLayout()
                        b.orientation = 'vertical'
                        b.add_widget(
                            Label(text='Bitte alle Felder ausfüllen!'))
                        btn = Button(text='Ok')
                        b.add_widget(btn)
                        p = Popup()
                        p.title = 'Fehler'
                        p.content = b
                        btn.bind(on_press=p.dismiss)
                        p.open()
                        return
                    # Create user
                    user = data.register_user(
                        firstname.text, lastname.text, email.text, badge_)
                    logout()
                    


class LoginScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class KioskScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def logout(self):
        logout()
    blank = data.default_avatar

    def get_balance(self):
        if user is not None:
            return user.balance
        else:
            return 'Error'

    def get_avatar(self):
        if user is not None:
            return user.avatar
        else:
            return data.default_avatar


class RegisterScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

items = []
def enable_items(*args, **kwargs):
    for item in items:
        item.disabled = False

def disable_items():
    for item in items:
        item.disabled = True

class Item(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prid = 0
        self.name = ""
        self.stock = 0
        self.price = 0
        self.id = uuid.uuid1().hex

    def on_press(self):
        renew_timeout()
        disable_items()
        user.buy(self.prid)
        refresh('balance')
        Clock.schedule_once(enable_items, 2)



class ItemLayout(GridLayout):
    def __init__(self, *args, **kwargs):
        global itemlayout
        super().__init__(*args, **kwargs)
        self.sm = sm
        self.refresh()
        itemlayout = self

    def refresh(self):
        global items
        self.clear_widgets()
        items.clear()
        for product in data.get_products().items():
            b = Item()
            b.prid = product[0]
            b.name = product[1]['name']
            b.stock = product[1]['stock']
            b.price = product[1]['price']
            b.text = f'''{b.name}\n{b.price} CHF'''
            self.add_widget(b)
            items.append(b)


class DetailInput(TextInput):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _on_focus(self, instance, value):
        global focused
        if value:
            focused = instance
        super()._on_focus(instance, value)
    def refocus(self, *args):
        self.focus = True

LS = LoginScreen(name='Login')
KS = KioskScreen(name='Kiosk')
RS = RegisterScreen(name='Register')
sm.add_widget(LS)
sm.add_widget(KS)
sm.add_widget(RS)
sm.current = 'Login'


class KioskApp(App):
    def build(self):
        return sm


# try:
badge.Logger = Logger
badgesensor = Thread(target=badge.run, args=[on_badge, ])
badgesensor.start()

app = KioskApp()
app.run()
# except Exception as e:
#     logger.exception('Application: '+e)
