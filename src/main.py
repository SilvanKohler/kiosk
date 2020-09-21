from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from threading import Thread
from badge import run
from data import register_customer, login_customer, customer_exists, blankprofile
import time

style = Builder.load_file('style.kv')
sm = ScreenManager(transition=NoTransition())
keys = [
    'q,w,e,r,t,z,u,i,o,p',
    'a,s,d,f,d,g,h,j,k,l',
    'y,x,c,v,b,n,m',
    '.,@,del,SPEICHERN'
]
focused = None
times = {}
badge = None
customer = None

def on_badge(b):
    global badge, badgesensor
    badge = b
    if customer_exists(b):
        login_customer(b)
        sm.current = 'Login'
    else:
        sm.current = 'Register'

class Keyboard(BoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.rows = len(keys)
        # self.cols = len(keys[0].split(','))
        # for i, y in enumerate(keys):
        #     for x in range(self.cols):
        #         self.add_widget(Button(text=y.upper().split(',')[x], font_size=30, on_press=self.on_press) if x < len(
        #             y.split(',')) else Label())
        self.orientation = 'vertical'
        for i, y in enumerate(keys):
            row = BoxLayout()
            row.orientation = 'horizontal'
            for x in y.upper().split(','):
                row.add_widget(Button(text=x, font_size=30, on_press=self.on_press))
            self.add_widget(row)

    def on_press(self, instance):
        global times, customer
        # print(time.time() - times.get(instance.text, time.time() - 100))
        if time.time() - times.get(instance.text, time.time() - 100) > .05:
            times.update({instance.text: time.time()})
            # print(instance.text)
            if focused is not None:
                if instance.text not in ('DEL', 'SPEICHERN'):
                    focused.text += instance.text
                elif instance.text == 'DEL':
                    focused.text = focused.text[:-1]
                elif instance.text == 'SPEICHERN':
                    firstname = self.parent.parent.ids.firstname
                    lastname = self.parent.parent.ids.lastname
                    email = self.parent.parent.ids.email
                    if '' in (firstname.text, lastname.text, email.text):
                        b = BoxLayout()
                        b.orientation = 'vertical'
                        b.add_widget(Label(text='Bitte alle Felder ausfüllen!'))
                        btn = Button(text='Ok')
                        b.add_widget(btn)
                        p = Popup(title='Fehler', content=b)
                        btn.bind(on_press=p.dismiss)
                        p.open()
                        return
                    # Create customer
                    customer = register_customer(firstname.text, lastname.text, email.text, badge)
                    # Clear fields
                    firstname.text = ''
                    lastname.text = ''
                    email.text = ''
                    sm.current = 'Login'


class LoginScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_enter(self, *args):
        global badgesensor
        badgesensor = Thread(target=run, args=[on_badge, ])
        badgesensor.start()
        super().on_enter(self, *args)


class KioskScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    balance = 0
    def get_balance(self):
        if customer is not None:
            return customer.get_avatar()
        else:
            return self.balance
    def get_avatar(self):
        if customer is not None:
            return customer.get_avatar()
        else:
            return blankprofile


class RegisterScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ItemLayout(GridLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sm = sm


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
sm.current = 'Kiosk'


class KioskApp(App):
    def build(self):
        return sm


badgesensor = Thread(target=run, args=[on_badge, ])
badgesensor.start()
app = KioskApp()
app.run()
