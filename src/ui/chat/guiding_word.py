"""
2025年4月7日 17点19分
该组件是当产生引导词的时候添加进入聊天框的组件
该组件会承载一些文本内容
点击该组件会将文本内容加载进输入栏并且在输入后删除掉自己
一次性可以产生多个引导词
"""
from kivy.lang import Builder
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty,NumericProperty
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton
from kivy.metrics import dp

Builder.load_string(
    """
<GuidingWord>:
    md_bg_color: app.theme_cls.primaryContainerColor
    font_style: "STSONG"
    #font_name: "Label"
    role:"medium"
    size_hint: None,None
    height: self.texture_size[1]
    text_size: self.width, None
    halign: "left"
    valign: "center"
    radius: 10,10,10,10
    padding: 10,0,10,0
    elevation: 4
    shadow_offset: 0, -8
    shadow_softness: 6

<GuidingWordRight>:
    orientation:"horizontal"
    adaptive_size: True
    MDWidget:
        size_hint:1,1
        #width: 100
        #theme_width:"Custom"
        md_bg_color: "blue"
        #text:"1111111111"
    GuidingWord:
        id:guiding_word

<GudiingWordManager>:
    orientation:"vertical"
    size_hint: 1,None
    height: self.minimum_height
    spacing: 10
    padding: 10,10,10,10
    # MDButton:
    #     text:"添加引导词"
    #     on_release: root.add_word("这是一个测试文本，用于测试文本的宽度是否超过了最大值。")
"""
)
from kivy.metrics import sp,dp
from kivymd.uix.behaviors import HoverBehavior
from kivymd.uix.behaviors import CommonElevationBehavior
class GuidingWord(CommonElevationBehavior,MDLabel,HoverBehavior):
    """
    由于增加了对于文本决定宽度的实时判定，因此不能在创建的时候给text初始值
    否则会引发没用_label错误
    """
    max_width=NumericProperty(900)
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
    
    def on_text(self,instance,value):
        """
        文本改变的时候计算宽度是否超过了最大值
        必须在组件初始化完成后才能设置文本，否则会触发不可用的_label错误
        """
        def calculate_width(self):
            width = 0
            max_width=0
            for char in self.text:
                if char=="\n":
                    max_width=max(width,max_width)
                    width=0
                char_size = self._label.get_extents(char)
                width += char_size[0]
                max_width=max(width,max_width)
            return max_width*1.2

        new_width = calculate_width(self)
        if new_width > self.max_width:
            self.width = self.max_width  # Set the width of the label
        else:
            if new_width<dp(100):
                new_width=dp(100)
            self.width = new_width  # Set the width of the label
        
        self.texture_update()  # Update the texture

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            #点击了该组件，将文本加载进输入栏并且删除自己
            self.parent.word_input_to_textfield(self,self.text)
            self.parent.delete_all_word()

    def on_enter(self, *args):
        #print("鼠标进入")
        self.md_bg_color = self.theme_cls.secondaryContainerColor

    def on_leave(self, *args):
        #print("鼠标离开")
        self.md_bg_color = self.theme_cls.primaryContainerColor
        
class GuidingWordRight(MDBoxLayout):
    """
    添加一个空组件占据空间，实现右对齐
    """
    text=StringProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.guiding_word.text=self.text
import re

def contains_letter(s):
    return bool(re.search(r'[a-zA-Z]', s))

class GudiingWordManager(MDBoxLayout):
    callback=lambda *arges:print(arges)
    max_number=NumericProperty(3)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation="vertical"
        #self.add_word("这是一个测试文本，用于测试文本的宽度是否超过了最大值。\n测试文本的宽度是否超过了最大值。\n 1234")

    def add_word(self,words:str):
        """
        添加一个引导词组件
        """
        self.delete_all_word()
        for word in words.split('\n'):
            if contains_letter(word):
                w=GuidingWord()
                w.text=word
                self.add_widget(w)
                self.max_number-=1
                if self.max_number<=0:
                    break
        self.max_number=3
    
    def delete_all_word(self):
        self.clear_widgets()

    def word_input_to_textfield(self,instance,value):
        #print(value)
        self.callback(instance,value)

class Example(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"  # 设置为深色主题
        self.theme_cls.primary_palette = "Blue"  # 设置主色调为蓝色
        self.theme_cls.primary_hue = "500"  # 设置主色调的亮度
        t=GudiingWordManager()
        t.add_word("这是一个测试文本，用于测试文本的宽度是否超过了最大值。\n测试文本的宽度是否超过了最大值。\n 1234")
        return t

if __name__ == "__main__":
    Example().run()