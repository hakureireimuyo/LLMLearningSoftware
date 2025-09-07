import sys
from pathlib import Path

# 自动添加项目根目录和 src 目录
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / "src"))

from src.components.common.ime import IMEManager,IMEPreviewUI
from src.app import TestApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton,MDButtonText
from kivy.clock import Clock

# class TestIMEApp(TestApp):
#     def build(self):
#         self.com=MDBoxLayout(size_hint=(1, 1))
#         self.com.add_widget(MDLabel(text="测试输入法UI", pos=(100, 200), font_style="STSONG",size_hint=(None, None), size=(200, 50)))
#         self.button=MDButton(pos=(200, 300), size_hint=(None, None), size=(200, 50))
#         self.button.add_widget(MDButtonText(text="显示输入法候选词",))
#         self.button.bind(on_release=lambda x: self.show_ime(100, 300))
#         self.com.add_widget(self.button)
#         self.index=0
#         button=MDButton(
#             pos=(200, 300),
#             size_hint=(None, None),
#             size=(200, 50), 
#         )
#         button.bind(on_release=lambda x:self.add())
#         self.com.add_widget(button)
#         button2=MDButton(
#             pos=(400, 300),
#             size_hint=(None, None),
#             size=(200, 50)
#         )
#         button2.bind(on_release=lambda x:self.sub())
#         self.com.add_widget(button2)
#         self.ime_ui = IMEPreviewUI()
#         return super().build()
    
#     def show_ime(self, x, y):
#         """显示输入法候选词UI"""
#         Window.add_widget(self.ime_ui) 
#         self.ime_ui.update_position(x, y)
#         self.ime_ui.update_candidates(["候选asasa词", "候选词", "候选词","99999"])
#         self.ime_ui.opacity = 1
#         Clock.schedule_once(lambda x: self.ime_ui.update_selected_index(2), 2)
#         Clock.schedule_once(lambda x: self.ime_ui.update_selected_index(0), 4)
    
#     def add(self):
#         self.index+=1
#         self.ime_ui.update_selected_index(self.index)

#     def sub(self):
#         self.index-=1
#         self.ime_ui.update_selected_index(self.index)   

from src.components.common.ime import ImeTextInput

class TestIme(TestApp):
    def build(self):
        self.com=MDBoxLayout(size_hint=(1, 1))
        self.input=ImeTextInput(
            callback=lambda x:print(x),
            multiline=True
        )
        self.com.add_widget(self.input)
        self.input2=ImeTextInput(
            multiline=True
        )
        self.com.add_widget(self.input2)
        return super().build()
    
if __name__ == "__main__":
    TestIme().fps_monitor_start()
    TestIme().run()