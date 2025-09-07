import asyncio
import threading
import re
from kivy.clock import Clock, mainthread
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDButton,MDButtonText
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty, DictProperty,OptionProperty
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle,Line
from kivymd.uix.textfield import MDTextField
from kivymd.uix.scrollview import MDScrollView
#from .streaming_parser import StreamingJSONParser
from kivymd.uix.tooltip import MDTooltip
from kivymd.uix.button import MDIconButton

Builder.load_string("""
<YourTooltipClass>
    MDTooltipPlain:
        text:root.text_tool
        font_style: "STSONG" 
        font_role:"large"
        
<TooltipMDIconButton>
    MDIconButton:
        icon: root.icon
                    
<DynamicHeightLabel>:
    #md_bg_color: self.theme_cls.secondaryContainerColor
    # text_size: self.width, None
    # height: self.texture_size[1]
    #size: self.texture_size
    size_hint: 1,None
    height: self.texture_size[1]
    text_size: self.width, None
    markup: True
    radius:[10,10,10,10]
    halign:'left'
    valign:'top'
    font_style:"STSONG"
    role:"medium"
    allow_copy:True
                    
<ParseComponent>:
                    
<EssaySuggestions>:
    orientation: "horizontal"
    #adaptive_height: True
    TextInput:
        id:content
        # size_hint: 1,None
        # height: self.texture_size[1]
        # text_size: self.width, None
        # markup: True
        # radius:[10,10,10,10]
        # halign:'left'
        # valign:'top'
        # font_name:"STSONG"
        #role:"medium"
        #allow_copy:True
        hint_text: "只读模式"
        font_name: "STSONG"
        font_size: "26sp"
        background_normal: ""
        border: 6,6,6,6
        readonly:True
<CorrectionSuggestions>:
    MDScrollView:
        do_scroll_x: False
        MDBoxLayout:
            id: suggestions_box
            orientation: "vertical"
            adaptive_height: True
            padding: 10, 10, 10, 10
            spacing: 10
<WritingGuidance>:
    id: chat_message_loader
    size_hint:1,1
    orientation: "vertical"
    md_bg_color: app.theme_cls.backgroundColor
    MDNavigationBar:
        set_bars_color: True
        size_hint_y: None
        height: "56dp"
        padding: "12dp","12dp","12dp","12dp"
        elevation: 4
        MDLabel:
            text: "Writing Guidance"
            font_style: "STSONG"
            size_hint_x: None
            width: "400dp"
            pos_hint: {"center_x":.5, "center_y":.5}
        MDLabel:
            text: ""
            font_style: "STSONG"
        MDNavigationItem:
            size_hint_x: None
            width: "64dp"
            on_release: screen_manager.current = "screen_1"
            MDNavigationItemIcon:
                icon: "text-box-multiple"
            
        MDNavigationItem:
            size_hint_x: None
            width: "64dp"
            on_release: screen_manager.current = "screen_2"
            MDNavigationItemIcon:
                icon: "text-box-plus"
            
        MDNavigationItem:
            size_hint_x: None
            width: "64dp"
            on_release: screen_manager.current = "screen_3"
            MDNavigationItemIcon:
                icon: "tooltip-text"
            
        MDNavigationItem:
            size_hint_x: None
            width: "64dp"
            on_release: screen_manager.current = "screen_4"
            MDNavigationItemIcon:
                icon: "cogs"
    MDBoxLayout:
        orientation: "horizontal"
        MDBoxLayout:    
            orientation: "vertical"
            padding: 10, 10, 10, 30
            spacing: 10
            MDLabel:
                text: "标题"
                font_style: "STSONG"
                role:"medium"
                size_hint_y: None
                height: self.texture_size[1]
            MDTextField:
                id: title
                MDTextFieldMaxLengthText:
                    max_text_length: 70
            MDLabel:
                text: "正文"
                font_style: "STSONG"
                role:"small"
                size_hint_y: None
                height: self.texture_size[1]
            MyInputComponent:
                id: content
                hint_text: "此处输入正文内容"
                font_name: "STSONG"
                font_size: "26sp"
                background_normal: ""
                border: 6,6,6,6
                
        MDDivider:
            orientation: "vertical"
        MDBoxLayout:
            orientation: "vertical"
            padding: 10, 10, 10, 10
            spacing: 10
            MDScreenManager:
                id: screen_manager
                MDScreen:
                    name: "screen_1"
                    id: screen_1
                    MDBoxLayout:
                        orientation: "vertical"
                        MDLabel:
                            text:"作文批改"
                            size_hint:1,None
                            height:"60dp"
                            font_style:"STSONG"
                            role:"large"
                            halign:"center"
                            valign:"middle"
                            pos_hint:{"center_x":.5,"center_y":0.5}
                        CorrectionSuggestions:
                            id: correction_suggestions
                            button_state_callback:root.set_button_state
                MDScreen:
                    name: "screen_2"
                    id: screen_2
                    MDBoxLayout:
                        orientation: "vertical"
                        MDBoxLayout:
                            orientation: "horizontal"
                            size_hint:1,None
                            height:"60dp"
                            MDButton:
                                size_hint_x:None
                                style: "elevated"
                                width: "10dp"
                                radius:[0,0,0,0]
                                pos_hint: {"center_x": .5, "center_y": .5}
                                MDButtonIcon:
                                    icon: "arrow-left-bold"
                            MDLabel:
                                text:"作文建议"
                                size_hint:1,None
                                height:"60dp"
                                font_style:"STSONG"
                                role:"large"
                                halign:"center"
                                valign:"middle"
                                pos_hint:{"center_x":.5,"center_y":0.5}
                        EssaySuggestions:
                            id: essay_suggestions
                            button_state_callback:root.set_button_state
                MDScreen:
                    name: "screen_3"
                    id: screen_3
                MDScreen:
                    name: "screen_4"
                    id: screen_4

            MDButton:
                id:button
                style: "elevated"
                theme_height: "Custom"
                theme_width: "Custom"
                size_hint:1,None
                height:"40dp"
                radius:0,0,0,0
                pos_hint: {"center_x": .5, "center_y": .5}
                on_release: root.grading_essays(root.ids.title.text,root.ids.content.text)
                MDButtonIcon:
                    id:button_icon
                    icon: "plus"

                MDButtonText:
                    id:button_text
                    text: "Start parsing"
""")

from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, ColorProperty,NumericProperty
from kivy.core.window import Window
from kivy.base import EventLoop
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.divider import MDDivider
from threading import Thread
FL_IS_LINEBREAK = 0x01
FL_IS_WORDBREAK = 0x02
FL_IS_NEWLINE = FL_IS_LINEBREAK | FL_IS_WORDBREAK

class YourTooltipClass(MDTooltip):
    '''Implements your tooltip base class.'''

class TooltipMDIconButton(YourTooltipClass, MDIconButton):
    '''Implements a button with tooltip behavior.'''
    icon = StringProperty()
    text_tool=StringProperty()
    callback=ObjectProperty(None)
    inputHeight=NumericProperty(0)
    def __init__(self,callback=None, **kwargs):
        super().__init__(**kwargs)
        self.callback=callback
        if self.inputHeight!=0:
            self.ids.input_field.height=self.inputHeight

    def on_press(self, *args):
        #print("鼠标点击")
        if self.callback:
            self.callback()
        return True
    
class DynamicHeightLabel(MDLabel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class EssaySuggestions(MDBoxLayout):
    button_state_callback=ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.valign = 'top'
        self.halign = 'left'
        self.role='medium'
        self.font_name = 'STSONG'
        self.api_moudel = None#ChatAndAPIInterface()

    def set_api_moudel(self,moudel):
        self.api_moudel.set_provider(moudel)
        self.api_moudel.set_system_prompt(
        """将会输入英语作文标题和正文，你的任务是对该作文进行批改，将句子进行优化，丰富语法词汇，给出更多的建议。
        如果没有输入正文，就根据题目写一个。如果没有题目，则提供一些作文的标题供用户参考
        只返回文本内容。不要输出标题，只返回正文内容。没一个自然段都要用中文解释为什么要这样修改，比之前的优点是什么。"""
        )
    def essay_suggestions(self,title,content):
        self.text=''
        if self.button_state_callback:
            self.button_state_callback('await')
        def fun(self,title,content):
            response=self.api_moudel.chat_sync("题目<"+title+">\n正文:"+content,stream=True)
            temp_buffer=''
            for result in response:
                delta_content = getattr(result.choices[0].delta, 'content', '') or ''
                # 合并到缓冲区
                temp_buffer += delta_content
                 # 当缓冲区达到阈值或收到完整句子时更新
                if len(temp_buffer) >= 20 or '.' in delta_content:
                    # 使用闭包捕获当前缓冲区内容
                    def update_closure(content):
                        def wrapper(dt):
                            self._update_ai_text(content)
                        return wrapper
                    Clock.schedule_once(update_closure(temp_buffer), 0.01)
                    temp_buffer = ""  # 重置缓冲区
            if self.button_state_callback:
                self.button_state_callback('available')
        Thread(target=fun,args=(self,title,content)).start()
    
    @mainthread
    def _update_ai_text(self, text):
        """线程安全的UI更新方法"""
        self.ids.content.text+=text
    
class ParseComponent(MDBoxLayout):
    #border_width = NumericProperty(2)
    data=DictProperty({})
    def __init__(self, data,**kwargs):
        super().__init__(**kwargs)
        self.default_color = [0.2, 0.2, 0.2, 1]
        self.hover_color = [0.5, 0.5, 0.5, 1]
        self.data=data
        self.orientation="vertical"
        self.padding=10,10,10,10
        self.spacing=10
        self.adaptive_height=True

        with self.canvas.before:
            self.border_color = Color(*self.default_color)
            self.border = Line(width=1)
        
        self.bind(
            pos=self._update_border,
            size=self._update_border
        )
        self._update_border()

    def _update_border(self, *args):
        offset = 1
        self.border.rectangle = (
            self.x - offset,
            self.y - offset,
            self.width + 2*offset,
            self.height + 2*offset
        )

    def on_enter(self):
        self.border_color.rgba = self.hover_color

    def on_leave(self):
        self.border_color.rgba = self.default_color

    def create_widget(self):
        for key,value in self.data.items():
            #print(type(value))
            text=value.replace("[error]","[color=FF0000]")
            text=text.replace("[/error]","[/color]")
            self.add_widget(DynamicHeightLabel(text=text))
            self.add_widget(MDDivider())
    
class MyInputComponent(TextInput):
    min_height=NumericProperty(0)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def insert_text(self, substring, from_undo=False):    
        #print(substring)        
        if self.text:
            if substring[-1] == "\n":
                super().insert_text(substring+" "*self.tab_width, from_undo=from_undo)
            else:
                super().insert_text(substring, from_undo=from_undo)
        else:
            super().insert_text(' '*self.tab_width+substring, from_undo=from_undo)

#from core.tools.interface.chat_and_api_interface import ChatAndAPIInterface
class CorrectionSuggestions(MDScreen):
    original_text=StringProperty("")
    result=[]
    parser = None #StreamingJSONParser()
    button_state_callback=ObjectProperty(None)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_moudel = None#ChatAndAPIInterface()
        self.parser.set_callbacks(self.generate_error_resolution_component,self.generate_suggestion_component)
        self.is_first_1=True
        self.is_first_2=True
        
    def set_api_moudel(self,moudel):
        self.api_moudel.set_provider(moudel)
        self.api_moudel.change_input_model('json')
        self.api_moudel.set_system_prompt("""
将会输入以句子为单位的列表数据的英语作文，你的任务是对该作文进行批改，主要检查语法，单词等错误，并且给出错误解析。只返回相关的错误，输出格式为
### 输出格式
请严格按照如下格式仅输出JSON，不要输出Python代码或其他信息，JSON字段使用顿号【、】区隔：
                                          {
    "parse":{
        "0": {
            "errorpoints":"有错误的句子，并且使用[error]错误的文本内容[/error]来标记",
            "errorparsing":"错误解析，错误原因"
            },
    },
    "suggestion":{
            "0": {"cause":"修改建议","revise":"修改后的文本"},
    }
}
{
    "parse":{
        "0": {
            "errorpoints":"Simple things like planting trees, recycling wastes, and use public transportation can [error]makes[/error] different.",
            "errorparsing":"动词时态错误，建议将[makes]修改为[make];"
            },
        "1": {
            "errorpoints":"Government should [error]took[/error] strict measures to protect forest.",
            "errorparsing":"动词时态错误，建议将[took]修改为[should take];"
            },
        "2": {
            "errorpoints":"Because of my shy personality, I hesitated [error]for[/error] [error]many[/error] times.",
            "errorparsing":"介词冗余，建议删除[for]; [many]词汇频繁使用，建议替换新单词;"
            }
    },
    "suggestion":{
            "0": {"cause":"使句子更加简洁和有力","revise":"We must act immediately."},
            "1": {"cause":"使句子更加准确和流畅","revise":"Natural resources are being depleted at an alarming rate."},
    }
}
为了标记原文中错误的位置，一定要使用[error]文本[/error]在errorpoints中进行标记
错误点使用[error]错误的文本内容[/error]来标记，必须要有两个[]才行。错误点使用[error]错误的文本内容[/error]来标记
一句话可能包含多个错误，将所有错误点标记在一起，每个错误解析使用;进行分割。
建议是对一些句子的修改，提供关于短句/单词/句式的建议，而不修改原本的含义，数据包含为什么这么修改的原因和修改后的完整句子，与错误解析不同，建议不包含错误，只是试图对句子进行润色和优化。
可以使用更高级的词汇或者固定搭配来润色句子。
使用中文进行解析。
只返回解析，必须使用json格式返回，不要包含其他信息。 
错误点使用[error]错误的文本内容[/error]来标记
""")
    #对输入的原始文本进行数据处理，将其分割成以句子为单位的列表
    def process_text(self, text):
        # 使用正则表达式分割句子（支持中英文标点）
        sentences = re.split(r'(?<=[.!?。！？])\s+', text)
        processed = []
        for sentence in sentences:
            # 1. 去除首尾空格
            clean_sentence = sentence.strip()
            # 2. 移除特殊符号 []{},
            clean_sentence = re.sub(r'[\[\]{}，]', '', clean_sentence)
            # 3. 统一使用单引号（处理双引号情况）
            clean_sentence = clean_sentence.replace('"', "'")
        return processed
    
    #通过api接口进行数据处理，获取错误点和解析
    def get_correction(self,title,content):
        if content=="" or content==None:
            self.ids.suggestions_box.add_widget(MDLabel(
                text="请输入作文内容",
                font_style="STSONG",
                role="medium", 
                size_hint=(1,None),
                height=100,
                halign="left",
                valign="center",
            ))
            return
        self.ids.suggestions_box.clear_widgets()
        #print("原始文本")
        #print(text) 
        #sentences=self.process_text(text)
        #print(sentences)
        #result=response.choices[0].message.content
        self.is_first_1=True
        self.is_first_2=True
        if self.button_state_callback:
            self.button_state_callback('await')
        def fun(self,text):
            #print(text)
            response=self.api_moudel.chat_sync(text,stream=True)
            temp_buffer=''
            for result in response:
                    delta_content = getattr(result.choices[0].delta, 'content', '') or ''
                    for char in delta_content:
                        self.parser.process_char(char)
                    temp_buffer += delta_content
            print(temp_buffer,end='?')
            if self.button_state_callback:
                self.button_state_callback('available')
            assistant_msg = {"role": "assistant", "content": temp_buffer}
            self.api_moudel._provider.historical_dialogue.append(assistant_msg)
            self.api_moudel._provider._update_usage(assistant_msg["content"])
        Thread(target=fun,args=(self,"<"+title+">"+content)).start()

    def generate_error_resolution_component(self,data:dict):
        @mainthread
        def fun():
            if self.is_first_2:
                self.ids.suggestions_box.add_widget(MDLabel(
                text="错误解析",
                font_style="STSONG",
                role="medium", 
                size_hint=(1,None),
                height=100,
                halign="left",
                valign="center",
                ))
                self.is_first_2=False
            t=ParseComponent(data)
            t.create_widget()
            self.ids.suggestions_box.add_widget(t)
            return True
        Clock.schedule_once(lambda dt: fun(),0.01)

    def generate_suggestion_component(self,data:dict):
        @mainthread
        def fun():
            if self.is_first_1:
                self.ids.suggestions_box.add_widget(MDLabel(
                text="优化建议",
                font_style="STSONG",
                role="medium", 
                size_hint=(1,None),
                height=100,
                halign="left",
                valign="center",
                ))
                self.is_first_1=False
            t=ParseComponent(data)
            t.create_widget()
            self.ids.suggestions_box.add_widget(t)
            return True
        Clock.schedule_once(lambda dt:fun(),0.01)
    

class WritingGuidance(MDBoxLayout):
    state=OptionProperty(
        'available', 
        options=[
            'available',
            'await',
        ]
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_api_moudel(self,moudel,moudel2):
        self.ids.correction_suggestions.set_api_moudel(moudel)
        self.ids.essay_suggestions.set_api_moudel(moudel2)

    def grading_essays(self,title:str='',content:str=''):
        #共同用的按钮，通过屏幕状态判断调用的方法
        #print(title,content)
        if self.ids.screen_manager.current=="screen_1":
            self.ids.correction_suggestions.original_text=content
            self.ids.correction_suggestions.get_correction(title,content)
        if self.ids.screen_manager.current=="screen_2":
            self.ids.essay_suggestions.essay_suggestions(title,content)
        if self.ids.screen_manager.current=="screen_3":
            pass
        if self.ids.screen_manager.current=="screen_4":
            pass

    def set_button_state(self,state):
        if state not in ['available','await']:
            raise ValueError("state must be 'available' or 'await'")
        self.state=state

    def on_state(self, instance, value):
        if value == 'await':
            self.ids.button.disabled=True
            self.ids.button_text.text="Loading..."
            self.ids.button_icon.icon="loading"
            self.ids.button_icon.opacity=1
        if value == 'available':
            self.ids.button.disabled=False  
            self.ids.button_text.text="Start parsing"
            self.ids.button_icon.icon="plus"
            self.ids.button_icon.opacity=1

# from global_instance import zhipu_group
class ExampleApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        # self.theme_cls.theme_style = "Dark"
        #self.theme_cls.primary_hue = "A700"
        t=WritingGuidance()
        #t.set_api_moudel(zhipu_group.create_instance("glm-4-flash"),zhipu_group.create_instance("glm-4-flash"))
        return t
if __name__ == "__main__":
    ExampleApp().run()