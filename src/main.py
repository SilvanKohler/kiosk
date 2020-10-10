from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from threading import Thread
from badge import run
import time
from data import register_customer, login_customer, customer_exists, blankprofile, get_drinks, get_drink, close
import uuid

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
times2 = {}
badge = None
customer = None


def refresh():
    KS.ids['balance'].text = str(customer.get_balance()) + ' CHF'
    KS.ids['name'].text = customer.get_firstname() + '\n' + customer.get_lastname()
    KS.ids['avatar'].source = customer.get_avatar()


def on_badge(b):
    global badge, badgesensor, customer
    badge = b
    if customer_exists(b):
        customer = login_customer(b)
        sm.current = 'Kiosk'
        refresh()
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
                        p = Popup()
                        p.title = 'Fehler'
                        p.content = b
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

    blank = blankprofile

    def get_balance(self):
        if customer is not None:
            return customer.get_avatar()
        else:
            return 'Error'

    def get_avatar(self):
        if customer is not None:
            return customer.get_avatar()
        else:
            return blankprofile

    def transactions(self):
        t = GridLayout(cols=3, size_hint_y=None)
        t.bind(minimum_height=t.setter('height'))
        hy = .1
        t.add_widget(Label(text='Zeit', size_hint_y=hy))
        t.add_widget(Label(text='Artikel', size_hint_y=hy))
        t.add_widget(Label(text='Preis', size_hint_y=hy))
        for PID, dt, FK_DID, FK_UID in customer.get_transactions()[::-1][:30]:
            t.add_widget(Label(text=dt, size_hint_y=hy))
            t.add_widget(Label(text=get_drink(FK_DID)[0], size_hint_y=hy))
            t.add_widget(Label(text=str(get_drink(FK_DID)[2])+' CHF', size_hint_y=hy))
        s = ScrollView(size_hint=(1, None))
        s.add_widget(t)
        b = BoxLayout()
        b.orientation = 'vertical'
        b.add_widget(s)
        btn = Button(text='Schliessen', size_hint_y=.1)
        b.add_widget(btn)
        p = Popup(title='Transaktionen', content=b)
        btn.bind(on_press=p.dismiss)
        p.open()


class RegisterScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Item(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.DID = 0
        self.name = ""
        self.stock = 0
        self.price = 0
        self.id = uuid.uuid1().hex

    def on_press(self):
        if time.time() - times2.get(self.id, time.time() - 100) > 1:
            times2.update({self.id: time.time()})
            customer.withdraw(self.DID)
            refresh()


class ItemLayout(GridLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sm = sm
        self.items = get_drinks()
        for item in self.items:
            b = Item()
            b.DID = item[0]
            b.name = item[1]
            b.stock = item[2]
            b.price = item[3]
            b.text = f'''{b.name}\n{b.price} CHF'''
            self.add_widget(b)


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


try:
    badgesensor = Thread(target=run, args=[on_badge, ])
    badgesensor.start()
    app = KioskApp()
    app.run()
except Exception as e:
    print(e)
    close()
