"""
这个模块用于呈现api的使用情况，以及管理使用该模块所需要的一些
属于个人数据的信息，比如密钥，身份码等等。该界面提供了对于基础
模块的连通性检查
2025年3月21日 18点03分
"""
from kivy.lang import Builder
from kivy.properties import StringProperty, ListProperty, ObjectProperty, OptionProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivymd.app import MDApp
from kivy.clock import Clock
from kivymd.uix.expansionpanel import MDExpansionPanel
from kivy.metrics import dp
from .connectivity_test import GroupLabel

Builder.load_string('''
<ApiManager>:
    orientation: 'vertical'
    md_bg_color: app.theme_cls.backgroundColor
    MDTopAppBar:
        type: "small"
        size_hint_x: 1
        pos_hint: {"center_x": .5, "center_y": .5}

        MDTopAppBarLeadingButtonContainer:
            MDActionTopAppBarButton:
                icon: "arrow-left-bold"
                on_release: root.go_back()

        MDTopAppBarTitle:
            text: "API连通性测试"
            font_style: "STSONG"
            pos_hint: {"center_x": .5}

        MDTopAppBarTrailingButtonContainer:
            MDActionTopAppBarButton:
                icon: "restart"
                on_release: root.is_available()
            
    MDScrollView:
        do_scroll_x: False
        do_scroll_y: True
        always_overscroll: True
        scroll_type: ['bars', 'content']
        pos_hint: {"center_x": .5, "center_y": .5}
        MDBoxLayout:
            orientation: "vertical"
            size_hint_y: None
            height: self.minimum_height
            id: container
                    
''')

class APIManager(MDBoxLayout):
    callback=ObjectProperty()

    def  __init__(self,api_manager,callback:None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loading_api_manger(api_manager)
        self.callback=callback
    
    def loading_api_manger(self,api_manager):
        group_name=api_manager.get_groups_names()
        print(group_name)
        for name in group_name:
            name_t=""
            if name=="zhipu":
                name_t="智谱"
            elif name=="openai":
                name_t="OpenAI"
            elif name=="baidu_translate":
                name_t="百度翻译"
            elif name=="baidu_mind_cloud":
                name_t="百度智能云"
            elif name=="azure":
                name_t="Azure"
            elif name=="ali":
                name_t="阿里"
            elif name=="tencent":
                name_t="腾讯"
            elif name=="volcengine":
                name_t="火山"
            elif name=="google":
                name_t="Google"
            elif name=="youdao":
                name_t="有道"
            elif name=="sogou":
                name_t="搜狗"
            elif name=="xunfei":
                name_t="讯飞"
            elif name=="360":
                name_t="360"
            elif name=="microsoft":
                name_t="微软"
            else:name_t=name
            group=api_manager.get_group(name)
            temp=GroupLabel(group_name=name_t)
            temp.loading_group(group)
            self.ids.container.add_widget(temp)

    def is_available(self):
        for ch in self.ids.container.children:
            ch.is_available()

    def go_back(self):
        if self.callback==None:return
        self.callback()