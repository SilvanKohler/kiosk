from kivy.app import App
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.vkeyboard import VKeyboard
from kivy.uix.textinput import TextInput
import os

style = Builder.load_file("style.kv")
sm = ScreenManager()


class Keyboard(VKeyboard):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



class KioskScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class RegisterScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def onfocus(self, instance, value):
        if value:
            instance.parent.parent.children[0].target = instance #todo: FUNKTIONIERT NICHT
        else:
            pass


class ItemLayout(GridLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sm = sm


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
