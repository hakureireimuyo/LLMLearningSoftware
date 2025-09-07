from kivy.animation import Animation
from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior

from kivymd.app import MDApp
from kivymd.uix.behaviors import ScaleBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

KV = '''
MDScreen:

    ScaleBox:
        size_hint: .5, .5
        pos_hint: {"center_x": .5, "center_y": .5}
        on_release: app.change_scale(self)
        md_bg_color: "red"
        MDLabel:
            text: "测试"

'''


class ScaleBox(ButtonBehavior, ScaleBehavior, MDBoxLayout):
    pass


class Test(MDApp):
    def build(self):
        return Builder.load_string(KV)

    def change_scale(self, instance_button: ScaleBox) -> None:
        an = Animation(
            scale_value_x=0.5,
            scale_value_y=0.5,
            scale_value_z=0.5,
            d=0.3,
        )+Animation(
            scale_value_x=1,
            scale_value_y=1,
            scale_value_z=1,
            d=0.3,
        )
        an.start(instance_button)   



Test().run()