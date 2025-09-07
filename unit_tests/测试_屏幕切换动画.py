from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.transition import MDSharedAxisTransition
from kivymd.uix.button import MDButtonText
from kivy.properties import NumericProperty

KV = '''
<TestScreen>:
    
    MDBoxLayout:
        orientation: "vertical"
        padding: "20dp"
        spacing: "20dp"
        
        MDLabel:
            text: "Screen {}".format(root.screen_id)
            theme_text_color: "Custom"
            text_color: "white"
            halign: "center"

        MDButton:
            on_release: app.switch_screen()
            size_hint: None, None
            size: "200dp", "50dp"
            pos_hint: {"center_x": 0.5}
            MDButtonText:
                text: "Next Screen"
        
'''
Builder.load_string(KV)

class TestScreen(MDScreen):
    screen_id = NumericProperty()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.screen_id % 2 == 0:
            self.md_bg_color = self.theme_cls.primaryColor
        else:
            self.md_bg_color = self.theme_cls.secondaryColor

import sys
from pathlib import Path
# 自动添加项目根目录和 src 目录
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / "src"))

from src.app import TestApp
from src.components.common.transition import *

class SharedAxisDemo(TestApp):
    def build(self):
        # 设置窗口大小
        Window.size = (400, 700)
        # 设置主题
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"
        
        # 创建界面
        self.root = MDScreenManager()
        self.root.add_widget(TestScreen(name="screen1", screen_id=1))
        self.root.add_widget(TestScreen(name="screen2", screen_id=2))
        self.transition_direction = "standard"
        return self.root
    
    def switch_screen(self):
        # 获取当前屏幕管理器
        sm = self.root

        # 创建并配置过渡效果
        transition = MDFadeTransition()
        self.root.transition = transition
        # 切换到下一个屏幕
        if sm.current == "screen1":
            sm.current = "screen2"
        else:
            sm.current = "screen1"

if __name__ == "__main__":
    SharedAxisDemo().run()