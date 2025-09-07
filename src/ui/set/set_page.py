"""
该模块的功能是通过注册的方式让其他模块的设置相关调用暴露在此处让用户进行设置操作
2025年3月25日 18点59分
"""

from kivy.lang import Builder
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.app import MDApp
from kivymd.uix.tab import MDTabsItemText, MDTabsItem,MDTabsItemIcon
from kivymd.uix.label import MDLabel
from .dynamic_color_set import ThemeSettingsPage

Builder.load_string('''
<SetPage>:
    md_bg_color: app.theme_cls.backgroundColor
    size_hint:1,1
    orientation: "vertical"
    pos_hint: {"center_x": .5, "center_y": .5}
  
    MDTabsPrimary:
        id: tabs
        #pos_hint: {"center_x": .5, "center_y": .3}
        size_hint_x: 1
        size_hint_y: 1
        allow_stretch: True
        #label_only: True
        #indicator_duration:True
                    
        MDDivider:             
                           
        MDTabsCarousel:
            id: related_content_container
            size_hint_y: 1
            #scroll_timeout:20 #通过缩短滚动超时时间(默认55ms)判定来变相禁用该层组件的滚动，让事件下发进子层组件,但是更改此值会影响其他事件的传递
            # # height: dp(600)
            # size_hint:1,None
            # height: "1000dp"
    
            
''')
from ..api_management_page.api_manager import APIManager
from ..api_management_page.identiteit_bestuur import IdentityBestuur
from global_instance import api_manager

class SetPage(MDBoxLayout):
    """设置页面"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #self.on_start()

    def on_start(self):
        #============API测试页面============
        self.ids.tabs.add_widget(
            MDTabsItem(
                MDTabsItemText(
                    text="API管理",
                    font_style="STSONG",
                    role="medium"
                ),
            )
        )
        self.ids.related_content_container.add_widget(
           APIManager(api_manager,None)
        )
        #============API数据设置也============
        self.ids.tabs.add_widget(
            MDTabsItem(
                MDTabsItemText(
                    text="API数据设置",
                    font_style="STSONG",
                    role="medium"
                ),
            )
        )
        self.ids.related_content_container.add_widget(
           IdentityBestuur()
        )    
        #============主题设置==============
        self.ids.tabs.add_widget(
            MDTabsItem(
                MDTabsItemText(
                    text="主题设置",
                    font_style="STSONG",
                    role="medium"
                ),
            )
        )
        self.ids.related_content_container.add_widget(
           ThemeSettingsPage()
        )    
        self.ids.tabs.switch_tab(text="API管理")

class Example(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Olive"
        return SetPage()
    
if  __name__ == "__main__":
    Example().run()