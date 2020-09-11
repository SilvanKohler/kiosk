from kivy.app import App
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
import time

style = Builder.load_file("style.kv")
sm = ScreenManager()
keys = [
    "q,w,e,r,t,z,u,i,o,p",
    "a,s,d,f,d,g,h,j,k,l",
    "y,x,c,v,b,n,m",
    ".,@,del,SPEICHERN"
]
focused = None
times = {}

class Keyboard(GridLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rows = len(keys)
        self.cols = len(keys[0].split(","))
        for i, y in enumerate(keys):
            for x in range(self.cols):
                self.add_widget(Button(text=y.upper().split(",")[x], font_size=30, on_press=self.on_press) if x < len(
                    y.split(",")) else Label())

    def on_press(self, instance):
        global times
        print(time.time() - times.get(instance.text, time.time() - 100))
        if time.time() - times.get(instance.text, time.time() - 100) > .01:
            times.update({instance.text: time.time()})
            # print(instance.text)
            if focused is not None:
                if instance.text != "DEL" and instance.text != "ENT":
                    focused.text += instance.text
                elif instance.text == "DEL":
                    focused.text = focused.text[:-1]
                elif instance.text == "SPEICHERN":

                    sm.current = "Kiosk"


class KioskScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


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


KS = KioskScreen(name="Kiosk")
RS = RegisterScreen(name="Register")
sm.add_widget(KS)
sm.add_widget(RS)
sm.current = "Kiosk"


class KioskApp(App):
    def build(self):
        return sm


app = KioskApp()
app.run()
