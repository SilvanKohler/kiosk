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
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import NoTransition, Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput


import _client.badge as badge
import _shared.data as data
import directories

data.init('client')

Config.read(os.path.join(directories.__client__, 'config.ini'))
style = Builder.load_file(os.path.join(directories.__client__, 'style.kv'))
sm = ScreenManager(transition=NoTransition())
keys = [
    '1,2,3,4,5,6,7,8,9,0',
    'q,w,e,r,t,z,u,i,o,p',
    'a,s,d,f,d,g,h,j,k,l',
    'y,x,c,v,b,n,m',
    '.,@,-,del,SPEICHERN'
]
focused = None
times = {}
badge_ = None
user = None
itemlayout = None


def login(b):
    global user
    user = data.login_user(b)
    sm.current = 'Kiosk'
    refresh()


def logout():
    global user, badge_
    user = None
    badge_ = None
    sm.current = 'Login'


def refresh(content='all'):
    if content == 'balance':
        KS.ids['balance'].text = str(user.balance) + ' CHF'
    elif content == 'userinformation':
        KS.ids['balance'].text = str(user.balance) + ' CHF'
        KS.ids['name'].text = user.firstname + '\n' + user.lastname
        KS.ids['avatar'].source = user.avatar
    elif content == 'drinks':
        itemlayout.refresh()
    elif content == 'all':
        refresh('balance')
        refresh('userinformation')
        refresh('drinks')


def on_badge(b):
    global badge_
    logout()
    print(b, badge_)
    if b != badge_:
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
        global times, user
        # logger.debug('Application: '+time.time() - times.get(instance.text, time.time() - 100))
        if time.time() - times.get(instance.text, time.time() - 100) > .05:
            times.update({instance.text: time.time()})
            # logger.debug('Application: '+instance.text)
            if focused is not None:
                if instance.text not in ('DEL', 'SPEICHERN'):
                    focused.text += instance.text
                elif instance.text == 'DEL':
                    if focused.cursor_col > 0:
                        focused.text = focused.text[:focused.cursor_col -
                                                    1] + focused.text[focused.cursor_col:]
                elif instance.text == 'SPEICHERN':
                    firstname = self.parent.parent.ids.firstname
                    lastname = self.parent.parent.ids.lastname
                    email = self.parent.parent.ids.email
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
                    # Clear fields
                    firstname.text = ''
                    lastname.text = ''
                    email.text = ''
                    sm.current = 'Login'


class LoginScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class KioskScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
        self.did = 0
        self.name = ""
        self.stock = 0
        self.price = 0
        self.id = uuid.uuid1().hex

    def on_press(self):
        disable_items()
        Clock.schedule_once(enable_items, 3)
        user.buy(self.did)
        refresh('balance')



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
        for drink in data.get_drinks().items():
            b = Item()
            b.did = drink[0]
            b.name = drink[1]['name']
            b.stock = drink[1]['stock']
            b.price = drink[1]['price']
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
badgesensor = Thread(target=badge.run, args=[on_badge, ])
badgesensor.start()

app = KioskApp()
app.run()
# except Exception as e:
#     logger.exception('Application: '+e)
