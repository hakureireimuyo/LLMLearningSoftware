'''
聊天栏的单独设置信息，拥有一个界面，主要是一些选项和按钮
在此处设置当前聊天栏的一些默认设置
一些通用的设置：
1 语音播放速度
2 输入检查：
    自动纠错
    提示词
3 陌生词汇自动加入生词本
4 开启用户数据信息收集
5 聊天数据最大保存时间
6 大语言模型选择
7 大语言模型的设置：
    温度
    最大token
    上下文长度
8 TTS选择
9 翻译选择
10 翻译设置：
    翻译源
    翻译目标
11 删除当前所有聊天记录
'''

from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, BooleanProperty, ListProperty, DictProperty, OptionProperty, BoundedNumericProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.animation import Animation
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.slider import MDSlider
from .common_app import CommonApp
from global_instance import api_manager
from global_instance import SSC

Builder.load_string('''
<ChatSetting>:
    orientation: 'vertical'
    #size_hint: 1,None
    # size_hint_x: None
    # width:dp(500)
    adaptive_height:True
    spacing: dp(10)
    pos_hint: {"center_x": .5, "center_y": .5}
    md_bg_color: self.theme_cls.backgroundColor
    MDBoxLayout:
        md_bg_color: self.theme_cls.backgroundColor
        orientation:'horizontal'
        size_hint_y: None
        height:dp(160)
        padding:[dp(20),0,dp(20),0]
        MDLabel:
            text:'语速设置'
            font_style:"STSONG"
            role:"small"
        MDSlider:
            max:20
            min:5
            step:1
            value: root.speech_speed
            suffix:"x"
            track_active_width:dp(6)
            scaling:10.0
            on_value: root.set_speech_speed(self, self.value)
            MDSliderHandle:
            MDSliderValueLabel:
    MDDivider:
        size_hint_x: 1
        pos_hint: {'center_x': .5, 'center_y': .5}
    MDBoxLayout:
        md_bg_color: self.theme_cls.backgroundColor
        orientation:'horizontal'
        size_hint_y: None
        height:dp(60)
        padding:[dp(20),0,dp(20),0]
        MDLabel:
            text:'自动纠错'
            font_style:"STSONG"
            role:"small"
        MDSwitch:
            active: root.auto_correct
            on_active: root.set_auto_correct(self, self.active)
            pos_hint: {'center_x': .5, 'center_y': .5}
    MDDivider:
        size_hint_x: 1
        pos_hint: {'center_x': .5, 'center_y': .5}
    MDBoxLayout:
        md_bg_color: self.theme_cls.backgroundColor
        orientation:'horizontal'
        size_hint_y: None
        height:dp(60)
        padding:[dp(20),0,dp(20),0]
        MDLabel:
            text:'提示词'
            font_style:"STSONG"
            role:"small"
        MDSwitch:
            active: root.show_prompts
            on_active: root.set_show_prompts(self, self.active)
            pos_hint: {'center_x': .5, 'center_y': .5}
    MDDivider:
        size_hint_x: 1
        pos_hint: {'center_x': .5, 'center_y': .5}
    MDBoxLayout:
        md_bg_color: self.theme_cls.backgroundColor
        orientation:'horizontal'
        size_hint_y: None
        height:dp(60)
        padding:[dp(20),0,dp(20),0]
        MDLabel:
            text:'陌生词汇自动加入生词本'
            font_style:"STSONG"
            role:"small"
        MDSwitch:
            active: root.add_to_wordbook
            on_active: root.set_add_to_wordbook(self, self.active)
            pos_hint: {'center_x': .5, 'center_y': .5}
    MDDivider:
        size_hint_x: 1
        pos_hint: {'center_x': .5, 'center_y': .5}
    MDBoxLayout:
        md_bg_color: self.theme_cls.backgroundColor
        orientation:'horizontal'
        size_hint_y: None
        height:dp(60)
        padding:[dp(20),0,dp(20),0]
        MDLabel:
            text:'聊天数据最大保存时间'
            font_style:"STSONG"
            role:"small"
        MySlider:
            MDSliderHandle:
            MDSliderValueLabel:
                size:[dp(50),dp(50)]
    MDDivider:
        size_hint_x: 1
        pos_hint: {'center_x': .5, 'center_y': .5}            
    MDBoxLayout:
        md_bg_color: self.theme_cls.backgroundColor
        orientation:'horizontal'
        size_hint_y: None
        height:dp(60)
        padding:[dp(20),0,dp(20),0]
        MDLabel:
            text:'大语言模型选择'
            font_style:"STSONG"
            role:"small"
        MDDropDownItem:
            pos_hint: {"center_x": .5, "center_y": .5}
            on_release: root.open_LLM_select_menu(self)
            MDDropDownItemText:
                id: llm_select
                text: root.selected_llm
    MDDivider:
        size_hint_x: 1
        pos_hint: {'center_x': .5, 'center_y': .5}
    MDBoxLayout:
        md_bg_color: self.theme_cls.backgroundColor
        orientation:'horizontal'
        size_hint_y: None
        height:dp(60)
        padding:[dp(20),0,dp(20),0]
        MDLabel:
            text:'语音合成服务选择'
            font_style:"STSONG"
            role:"small"
        MDDropDownItem:
            pos_hint: {"center_x": .5, "center_y": .5}
            on_release: root.open_tts_select_menu(self)
            MDDropDownItemText:
                id: tts_select
                text: root.auto_tts_select
    MDDivider:
        size_hint_x: 1
        pos_hint: {'center_x': .5, 'center_y': .5}
    MDBoxLayout:
        md_bg_color: self.theme_cls.backgroundColor
        orientation:'horizontal'
        size_hint_y: None
        height:dp(60)
        padding:[dp(20),0,dp(20),0]
        MDLabel:
            text:'语音识别服务选择'
            font_style:"STSONG"
            role:"small"
        MDDropDownItem:
            pos_hint: {"center_x": .5, "center_y": .5}
            on_release: root.open_stt_select_menu(self)
            MDDropDownItemText:
                id: stt_select
                text: root.auto_stt_select
    MDDivider:
        size_hint_x: 1
        pos_hint: {'center_x': .5, 'center_y': .5}
    MDBoxLayout:
        md_bg_color: self.theme_cls.backgroundColor
        orientation:'vertical'
        size_hint_y: None
        height:dp(100)
        padding:[dp(20),0,dp(20),0]
        MDBoxLayout:
            orientation:'horizontal'
            MDLabel:
                text:'翻译服务选择'
                font_style:"STSONG"
                role:"small"
            MDDropDownItem:
                pos_hint: {"center_x": .5, "center_y": .5}
                on_release: root.open_tran_select_menu(self)
                MDDropDownItemText:
                    id: tran_select
                    text: root.auto_tran_select
        MDBoxLayout:
            orientation:'horizontal'
            MDLabel:
                text:'翻译设置'
                font_style:"STSONG"
                role:"small"
            MDLabel:
                text:'源语言'
                font_style:"STSONG"
                role:"small"
            MDDropDownItem:
                pos_hint: {"center_x": .5, "center_y": .5}
                on_release: root.open_src_lang_select_menu(self)
                MDDropDownItemText:
                    id: src_lang
                    text: root.translation_source
            MDLabel:
                text:'目标语言'
                font_style:"STSONG"
                role:"small"
            MDDropDownItem:
                pos_hint: {"center_x": .5, "center_y": .5}
                on_release: root.open_tar_lang_select_menu(self)
                MDDropDownItemText:
                    id: tar_lang
                    text: root.translation_target
    MDDivider:
        size_hint_x: 1
        pos_hint: {'center_x': .5, 'center_y': .5}
    MDBoxLayout:
        md_bg_color: self.theme_cls.backgroundColor
        orientation:'horizontal'
        size_hint_y: None
        height:dp(60)
        #padding:[dp(20),0,dp(20),0]
        MDButton:
            # size_hint_x:None
            # width:root.width
            theme_width: "Custom"
            height: "56dp"
            size_hint_x: 1
            radius: [0,0,0,0 ]
            MDButtonText:
                text:'删除当前所有聊天记录'
                font_style:"STSONG"
                role:"small"
                theme_text_color: "Custom"
                text_color: 1, 0, 0, 1
                pos_hint: {"center_x":.5, "center_y":.5}
    MDBoxLayout:
        size_hint:[None,1]
''')

class MySlider(MDSlider):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.max=3
        self.min=1
        self.step=1
        self.value=SSC.get('chat_data_storage_time',1)
        self.track_active_width=dp(6)
        self.scaling=1.0

    def on_value_pos(self, *args) -> None:
        """
        Fired when the `value_pos` value changes.
        Sets a new value for the value label texture.
        """
        self._update_points()
        if self._value_label and self._value_container:
            # FIXME: I do not know how else I can update the texture.
            self._value_label.text = ""
            self.suffix="30day" if self.value==1 else "90days" if self.value==2 else "forever"
            self._value_label.text = f"{self.suffix}" 
            self._value_label.texture_update()
            label_value_rect = self._value_container.canvas.get_group(
                "md-slider-label-value-rect"
            )[0]
            label_value_rect.texture = None
            label_value_rect.texture = self._value_label.texture
            label_value_rect.size = self._value_label.texture_size
        SSC.set('chat_data_storage_time',self.value)
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            super().on_touch_down(touch)
            return True
        return False
    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            super().on_touch_move(touch)
            return True
        return False

class ChatSetting(MDBoxLayout):
    # 语音相关属性
    speech_speed = NumericProperty(10)
    selected_tts = StringProperty("默认TTS")
    
    # 输入检查
    auto_correct = BooleanProperty(False)
    show_prompts = BooleanProperty(True)
    # 语言模型
    selected_llm = StringProperty("")
    # 翻译设置
    translation_source = StringProperty("chinese")
    translation_target = StringProperty("english")
    language_options = ListProperty(["中文", "英语", "日语", "韩语"])
    #加入生词本
    add_to_wordbook = BooleanProperty(False)
    #可见性
    opacity=NumericProperty(1)
    #默认选择STT
    auto_stt_select = StringProperty("")
    #默认选择TTS
    auto_tts_select = StringProperty("")
    #翻译服务选择
    auto_tran_select = StringProperty("")
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            self.speech_speed = int(SSC.get('speech_speed',10))
        except ValueError:
            self.speech_speed = 10
        self.selected_llm = SSC.get('chat_large_language_model',"")
        self.translation_source = SSC.get('source_language',"chinese")
        self.translation_target = SSC.get('target_language',"english")
        self.auto_stt_select = SSC.get('chat_stt',"")
        self.auto_tts_select = SSC.get('chat_tts',"")

        self.add_to_wordbook = "True"==SSC.get('add_to_wordbook',False)
        self.auto_correct = "True"==SSC.get('auto_correct',False)
        self.show_prompts = "True"==SSC.get('show_prompts',True)


    def open_LLM_select_menu(self,instance):
        print(instance)
        menu_items = [
            {
                "text": f"{group_name}+{model_name}",
                "on_release": lambda g=group_name, m=model_name: self.LLM_select_menu_callback(g, m)
            }
            for group_name in api_manager.get_groups_names()
            for model_name in api_manager.get_group(group_name).list_models_from_type("llm")
        ]
        MDDropdownMenu(caller=instance, items=menu_items).open()

    def open_tts_select_menu(self,instance):
        print(instance)
        menu_items = [
            {
                "text": f"{group_name}+{model_name}",
                "on_release": lambda g=group_name, m=model_name: self.tts_select_menu_callback(g, m)
            } 
            for group_name in api_manager.get_groups_names()
            for model_name in api_manager.get_group(group_name).list_models_from_type("tts")
        ]
        MDDropdownMenu(caller=instance, items=menu_items).open()
        
    def open_tran_select_menu(self,instance):
        print(instance)
        menu_items = [
            {
                "text": f"{group_name}+{model_name}",
                "on_release": lambda g=group_name, m=model_name: self.tran_select_menu_callback(g, m)
            } 
            for group_name in api_manager.get_groups_names()
            for model_name in api_manager.get_group(group_name).list_models_from_type("translate")
        ]
        MDDropdownMenu(caller=instance, items=menu_items).open()

    def open_src_lang_select_menu(self,instance):
        print(instance)
        menu_items = [
            {   
                "text": "chinese",
                "on_release": lambda: self.src_lang_select_menu_callback( "chinese")
            },
            {
                "text": "english",
                "on_release": lambda: self.src_lang_select_menu_callback( "english") 
            },
            {
                "text": "janpanes",
                "on_release": lambda: self.src_lang_select_menu_callback( "japanese")  
            }
        ]
        MDDropdownMenu(caller=instance, items=menu_items).open()

    def open_tar_lang_select_menu(self,instance):
        print(instance)
        menu_items = [
            {
                "text": "chinese",
                "on_release": lambda: self.tar_lang_select_menu_callback( "chinese")
            }, 
        ]
        MDDropdownMenu(caller=instance, items=menu_items).open()

    def open_stt_select_menu(self,instance):
        print(instance)
        menu_items = [
            {
                "text": f"{group_name}+{model_name}",
                "on_release": lambda g=group_name, m=model_name: self.stt_select_menu_callback(g, m)
            } 
            for group_name in api_manager.get_groups_names()
            for model_name in api_manager.get_group(group_name).list_models_from_type("stt")
        ]   
        MDDropdownMenu(caller=instance, items=menu_items).open()

    def toggle(self):
        if self.opacity == 0:
            anim = Animation(opacity=1, duration=0.5)
        else:
            anim = Animation(opacity=0, duration=0.5)
        anim.start(self)

    def LLM_select_menu_callback(self,group,model):
        #由于这个值是绑定到kv文件中的，所以需要在这里更新
        print(f"Selected: {group}+{model}")
        self.selected_llm = model
        SSC.set('chat_large_language_model',model)
        SSC.manual_save()

    def tts_select_menu_callback(self,group,model):
        #由于这个值是绑定到kv文件中的，所以需要在这里更新
        print(f"Selected: {group}+{model}")
        self.auto_tts_select = model
        SSC.set('chat_tts',model)
        SSC.manual_save()

    def stt_select_menu_callback(self,group,model):
        #由于这个值是绑定到kv文件中的，所以需要在这里更新
        print(f"Selected: {group}+{model}")
        self.auto_stt_select = model
        SSC.set('chat_stt',model)
        SSC.manual_save()

    def tran_select_menu_callback(self,group,model):
        #由于这个值是绑定到kv文件中的，所以需要在这里更新
        print(f"Selected: {group}+{model}")
        self.auto_tran_select = model
        SSC.set('chat_translate',model)
        SSC.manual_save()

    def src_lang_select_menu_callback(self,value):
        #由于这个值是绑定到kv文件中的，所以需要在这里更新
        self.translation_source = value
        SSC.set('source_language',value)
        SSC.manual_save()

    def tar_lang_select_menu_callback(self,value):
        #由于这个值是绑定到kv文件中的，所以需要在这里更新
        print(f"Selected: value")
        self.translation_target = value
        SSC.set('target_language',value)
        SSC.manual_save()

    def set_speech_speed(self, instance, value):
        print(f"Speech speed changed to {value},type{type(value)}")
        SSC.set('speech_speed',value)
        SSC.manual_save()

    def set_auto_correct(self, instance, value):
        print(f"Auto correct changed to {value}")
        _value="True" if value else "False"
        SSC.set('auto_correct',_value)
        SSC.manual_save()

    def set_show_prompts(self, instance, value):
        print(f"Show prompts changed to {value}")
        _value="True" if value else "False"
        SSC.set('show_prompts',_value)
        SSC.manual_save()
        
    def set_add_to_wordbook(self, instance, value):
        print(f"Add to wordbook changed to {value}")
        _value="True" if value else "False"
        SSC.set('add_to_wordbook',_value)
        SSC.manual_save()
    # def on_touch_down(self,touch):
    #     if self.opacity==0:
    #         #print("与设置界面无关")
    #         return False
    #     if self.collide_point(*touch.pos):
    #         print("将事件继续传递给子部件")
    #         return super().on_touch_down(touch)
    #     else:
    #         if self.opacity==1:
    #             self.toggle()
    #             print("设置以外的界面触发，关闭设置界面")
    #             return True
    #     print("未触发")
    #     return False
    
    # def on_touch_up(self,touch):
    #     if self.opacity==0:
    #         #print("与设置界面无关")
    #         return False
    #     if self.collide_point(*touch.pos):
    #         print("将事件继续传递给子部件")
    #         return super().on_touch_up(touch)
        
    # def on_touch_move(self,touch):
    #     if self.opacity==0:
    #         #print("与设置界面无关")
    #         return False
    #     if self.collide_point(*touch.pos):
    #         print("将事件继续传递给子部件")
    #         return super().on_touch_move(touch)

class ExampleApp(MDApp,CommonApp):
    def build(self):
        self.theme_cls.theme_style = "Light"  # 设置主题样式为浅色
        self.theme_cls.primary_palette = "Blue"  # 设置主色为蓝色
        return ChatSetting()

if __name__ == '__main__':
    ExampleApp().run()
