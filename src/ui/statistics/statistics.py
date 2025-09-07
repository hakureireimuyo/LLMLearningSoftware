"""
本模块用于显示一个数据的统计结果
主要是呈现一个单词的出现过的频率
初始化会从数据库加载
也会回写进数据库
为了避免过多组件同时加载，当组件第一次启动的时候
只会从数据库中读取一定量的数据传入，随着用户的下滑行为，
再不断地从数据库中进行读取。
"""

from kivymd.uix.recyclegridlayout import RecycleGridLayout
from kivymd.uix.recycleview import MDRecycleView
from kivymd.uix.refreshlayout import MDScrollViewRefreshLayout
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, BooleanProperty, ListProperty, DictProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivymd.app import MDApp

Builder.load_string("""
<StatisticsPage>:
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
        #indicator_duration: 0.2
        
        MDDivider:             
                           
        MDTabsCarousel:
            id: related_content_container
            size_hint_y:1
            #height: dp(300)
            #size_hint:1,.9
            lock_swiping:True
            scroll_timeout:2
            # pos_hint:{"center_x":.5,"center_y":.5}
""")
from kivymd.uix.tab import MDTabsItemText, MDTabsItem,MDTabsItemIcon
from .word_statistics import WordList
from ..user.user_page import UserPage
class StatisticsPage(MDBoxLayout):
    """
    统计页面,包含了用户使用的各种数据信息
    并以图形化的方式进行展示
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_start(self):
        #============用户数据页面============
        self.ids.tabs.add_widget(
            MDTabsItem(
                MDTabsItemText(
                    text="用户设置",
                    font_style="STSONG",
                    role="medium"
                ),
            )
        )
        self.ids.related_content_container.add_widget(
            # MDBoxLayout(size_hint=(1,1),md_bg_color="red")
            UserPage()
        )
        #============单词统计页面============
        self.ids.tabs.add_widget(
            MDTabsItem(
                MDTabsItemText(
                    text="单词表",
                    font_style="STSONG",
                    role="medium"
                ),
            )
        )
        self.ids.related_content_container.add_widget(
            # MDBoxLayout(size_hint=(1,1),md_bg_color="red")
            WordList()
        )
        #============单词统计页面============
        self.ids.tabs.add_widget(
            MDTabsItem(
                MDTabsItemText(
                    text="数据统计表",
                    font_style="STSONG",
                    role="medium"
                ),
            )
        )
        self.ids.related_content_container.add_widget(
            MDBoxLayout(size_hint=(1,1),md_bg_color="black")
            #WordList()
        )
    
class Example(MDApp):
    def build(self):
        return StatisticsPage()
    def on_start(self):
        pass

if __name__ == '__main__':
    Example().run()