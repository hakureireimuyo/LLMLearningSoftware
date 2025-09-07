"""
主要用于实现弹窗通知
会弹出一个包含消息的浮动窗口
显示几秒后自动消失
"""
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivy.animation import Animation
from kivymd.uix.behaviors import MotionDialogBehavior
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard

class Notification(MDCard,MotionDialogBehavior):
    title = StringProperty()
    content = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)  # 设置为固定大小
        self.size=(240,50)
        self.orientation = "vertical"
        self.radius = [30, 30, 30, 30]
        r,g,b,a =self.theme_cls.inverseOnSurfaceColor
        self.md_bg_color = (r,g,b,0.4)
        self.scale_value_x = 0
        self.scale_value_y = 0
        self.pos = kwargs.get("pos",(Window.width/2-120,Window.height/2-50))
        self.event = Clock.schedule_once(lambda dt:self.delete(),3)
        # self.add_widget(MDLabel(text=self.title,
        #                         font_style="STSONG",
        #                         role="medium",
        #                         pos_hint={"center_x":0.5,"center_y":0.7},
        #                         halign="center",))

        self.add_widget(MDLabel(text=self.content,
                                font_style="STSONG",
                                role="small",
                                pos_hint={"center_x":0.5,"center_y":0.9},
                                halign="center",))
        self.show()

    def show(self,*ages):
        Animation(scale_value_x=1,scale_value_y=1,duration=0.2).start(self)
        Window.add_widget(self)

    def delete(self,*ages):
        Animation(scale_value_x=0,scale_value_y=0,duration=0.2).start(self)
        Clock.schedule_once(self.remove,0.2)

    def remove(self,*args):
        Window.remove_widget(self)

from kivymd.app import MDApp
class test(MDApp):
    def build(self):
        return Notification(title="Test Title", content="Test Content")

if __name__ == "__main__":
    test().run()