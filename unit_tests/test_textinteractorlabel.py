import sys
from pathlib import Path

# 自动添加项目根目录和 src 目录
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / "src"))

from src.components.common.textinteractorlabel import (TestTextInteractorLabel,
                                                       TestTestInteractorLabel2,
                                                       StreamLabel)
from src.app import TestApp
from src.app.common_app import CommonApp
from kivymd.uix.label import MDLabel
from kivy.uix.widget import Widget
from kivy.lang import Builder


KV="""
#:import Widget kivy.uix.widget.Widget
#:import dp kivy.metrics.dp
MDBoxLayout:
    orientation: "vertical"
    spacing: dp(10)
    padding: dp(10)
    size_hint: 1, 1
    md_bg_color: 0.5,0.5,0.5,1
    pos_hint: {"center_x": 0.5, "center_y": 0.5}
    # L:
    #     id: label1
    StreamLabel:
        id: label1
        text: ""
        #md_bg_color: self.theme_cls.backgroundColor
        adaptive_width_from_parent: True
        adaptive_width_ratio: 0.8
    # StreamLabel:
    #     id: label2
    #     text: "This is another test label"
    #     adaptive_width_from_parent: False
    
    MDButton:
        on_release: root.ids.label1.stream_text("你好")

    # MDButton:
    #     on_release: root.ids.label2.stream_text("aa")
"""
"""TestTextInteractorLabel:
        id: label2
        text: "This is another test label"
    TestTextInteractorLabel:
        id: label3
        width: dp(200)
        text: "This is a test label你好啊啊1啊quqheoquehqoheuh183y9183y98y31111111111111111111111111194y92479
"""
class L(MDLabel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text="你好"
        self._last_text = ""            # 上次更新文本
        self._last_max_width = 0           # 上次更新文本最大宽度
        self._last_line_width = 0           # 上次更新文本最大行宽度
        self._last_text_length = 0              # 上次更新文本长度
        self.font_style="STSONG"
    def _calculate_max_text_width(self,*args):
        """增量计算文本最大宽度（假设文本只会增长）"""
        if not hasattr(self, '_label') or self._label is None:
            print(f"当前_label尚未创建{args}")
            return 0
        
        # 如果文本未变化，使用缓存值
        if self.text == self._last_text:
            print("未更新,使用缓存")
            return self._last_max_width + self.padding[0] + self.padding[2]
        
        # 获取文本变化部分
        new_text = self.text
        old_text = self._last_text
        
        # 如果文本被重置（长度变短），重新计算
        if len(new_text) < len(old_text):
            self._last_text = ""
            self._last_max_width = 0
            self._last_line_width = 0
            old_text = ""
        
        # 增量计算新增部分的宽度
        start_index = len(old_text)
        max_width = self._last_max_width
        current_line_width = self._last_line_width
        
        # 处理新增文本
        for char in new_text[start_index:]:
            if char == "\n":
                # 换行时更新最大宽度
                max_width = max(max_width, current_line_width)
                current_line_width = 0
            else:
                # 累加字符宽度
                char_size = self._label.get_extents(char)
                current_line_width += char_size[0]
        # 更新缓存值
        self._last_text = new_text
        self._last_max_width = max(max_width, current_line_width)
        self._last_line_width = current_line_width
        self._last_text_length = len(new_text)
        print(f"更新,计算新的值{self._last_max_width , self.padding[0] ,self.padding[2]}")
        return self._last_max_width + self.padding[0] + self.padding[2]


class Test(TestApp):
    def build(self):
        self.com = Builder.load_string(KV)

        return super().build()
    

if __name__ == '__main__':
    Test().fps_monitor_start()
    Test().run()

# ========================测试MDLabel=====================
# from kivymd.app import MDApp
# from kivymd.uix.boxlayout import MDBoxLayout
# from kivymd.uix.button import MDButton
# from kivymd.uix.card import MDCard
# KV2="""
# #:import Widget kivy.uix.widget.Widget
# #:import dp kivy.metrics.dp
# MDBoxLayout:
#     orientation: "vertical"
#     spacing: dp(10)
#     padding: dp(10)
#     size_hint: 1, 1
#     md_bg_color: 0.5,0.5,0.5,1
#     pos_hint: {"center_x": 0.5, "center_y": 0.5}
#     MDLabel:
#         id: label1
#         text: "11111"
#         md_bg_color: self.theme_cls.primaryColor
#     MDLabel:
#         id: label2
#         text: "22222"
#         md_bg_color: self.theme_cls.secondaryColor
#     MDLabel:
#         id: label3
#         text: "33333"
#         md_bg_color: self.theme_cls.tertiaryColor
#     MDButton:
#         on_release: root.add_widget(Widget(size_hint=(None, None), size=(dp(100), dp(100))))
#     MDButton:
#         on_release: if self!=root.children[0]:root.remove_widget(root.children[0])

# """
# class textapp(MDApp,CommonApp):
#     def build(self):
#         self.box=MDBoxLayout(orientation="vertical",size_hint=(1,1))
#         self.box.md_bg_color=self.theme_cls.backgroundColor
#         self.MDIconButton=MDButton(
#             pos_hint={"center_x":0.5,"center_y":0.5},
#             on_release=lambda x:self.open_menu(self.MDIconButton),
#             size_hint=(None,None),
#             size=(30,30),
#             radius=[0,0,0,0]
#         )
#         self.box.add_widget(self.MDIconButton)
#         self.com=Builder.load_string(KV2)
#         self.box.add_widget(self.com)
        
#         return self.box
# textapp().run()