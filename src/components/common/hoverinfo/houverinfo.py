
"""
以下实现了一些信息的悬浮显示
"""
from kivymd.uix.label import MDLabel
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.metrics import sp,dp
from kivymd.app import MDApp
from kivymd.uix.behaviors import HoverBehavior
from components import common_path
# import os
# from kivy.lang import Builder

# with open(
#     os.path.join(common_path, "hoverinfo", "hoverinfo.kv"), encoding="utf-8"
# ) as kv_file:
#     Builder.load_string(kv_file.read())
# 不需要了，所有属性在类中定义

class HoverInfo(MDLabel,HoverBehavior):
    fade_time = NumericProperty(50)  # 默认显示2秒
    event_dismiss=None
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_max_x=dp(500)
        #self.size_hint_min_x=dp(50)
        self.text_size = (self.size_hint_max_x, None)  # 允许文本自动换行
        self.adaptive_height = True
        self.markup = True
        self.radius = [10, 10, 10, 10]
        self.halign = 'left'
        self.valign = 'top'
        self.font_style = "STSONG"
        self.role = "medium"
        self.markup = True
        self.md_bg_color = self.theme_cls.secondaryContainerColor

    def show(self, pos):
        """显示信息面板并启动自动销毁定时器"""
        # 调整显示位置（防止超出屏幕）
        x = pos[0]   
        y = int(int(pos[1]/20)*20)+40 # 20为行高，避免出现半行的情况
        
        # 位于固定高度
        if y + self.height > Window.height:
            y = Window.height - self.height - 10
        if y < 0:
            y = 10
        self.pos = (x, y)
        Window.add_widget(self)
        self.event_dismiss=Clock.schedule_once(self.dismiss, self.fade_time)
        # 测试，每秒自动增加文本
        def add_text(dt):
            self.text += "111111111111"

        self.test_event=Clock.schedule_interval(add_text, 1)

    def dismiss(self, dt):
        """移除面板"""
        if self.event_dismiss!=None:
            Clock.unschedule(self.event_dismiss)
            self.event_dismiss=None
        Window.remove_widget(self)

    def on_enter(self, *args):
        '''
        The method will be called when the mouse cursor
        is within the borders of the current widget.
        '''
        print("鼠标进入")
        if self.event_dismiss!=None:
            Clock.unschedule(self.event_dismiss)
            self.event_dismiss=None
        self.md_bg_color = self.theme_cls.primaryContainerColor

    def on_leave(self, *args):
        '''
        The method will be called when the mouse cursor goes beyond
        the borders of the current widget.
        '''
        print("鼠标离开")
        if self.event_dismiss==None:
            self.event_dismiss=Clock.schedule_once(self.dismiss, self.fade_time/3)
        self.md_bg_color = self.theme_cls.secondaryContainerColor
    
                
from kivymd.uix.boxlayout import MDBoxLayout
class TextHoverInfo(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        hover_info=HoverInfo(text="测试文本")
        hover_info.show((100,100))

        