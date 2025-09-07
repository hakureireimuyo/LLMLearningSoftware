
import asynckivy
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.navigationrail import MDNavigationRailItem
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy import __version__ as kv__version__
from kivy.lang import Builder
from kivy.metrics import dp
from kivymd import __version__
from kivymd.uix.list import (
    MDListItem,
    MDListItemHeadlineText,
    MDListItemSupportingText,
    MDListItemLeadingIcon,
)
from materialyoucolor import __version__ as mc__version__
from kivy.properties import NumericProperty, ListProperty, BooleanProperty
from kivy.clock import Clock
from copy import deepcopy
from .chat_component.role_option import UserCard
#from 导航栏抽屉 import ChatMessageScoll
from .chat_component.chat_message_scoll import ChatMessageScoll
# from .chat_component.del.user_card_recycle_view import UserCardRecycleView
from .chat_component.chat_input import ChatInput
from .writing_instruction import WritingGuidance
from .set.set_page import SetPage
from .api_management_page.api_manager import APIManager
from .statistics.statistics import StatisticsPage
import cProfile
from .word_recitation.word_plan_page import FinalInterface

KV = '''
<MainWindows>:
    name: "MainWindows"
    MDBoxLayout:
        md_bg_color: self.theme_cls.backgroundColor  # 设置屏幕的背景颜色
        orientation: 'vertical'
        # MDBoxLayout:
        #     orientation: 'horizontal'
        #     size_hint_y: None  # 锁定高度
        #     height: '20dp'  # 设置固定高度
            #md_bg_color: "white"
            # BoxLayout:
            #     #size_hint_x: None  # 锁定宽度
            #     #width: '1200dp'  # 设置固定宽度
            #     # size_hint_y: None  # 锁定宽度
            #     # height: '20dp'  # 设置固定宽度 
            #     orientation: 'horizontal'

            #     #adding: 0,0,0,0
            #     #spacing: "20dp"
            #     MDButton:
            #         style: "tonal"
            #         theme_width: "Custom"
            #         height: "20dp"
            #         width: "30dp"
            #         radius: [0, 0, 0, 0]
            #         #theme_bg_color: "Custom"
                    
            #         MDButtonIcon:
            #             #x: text.x - (self.width + dp(2))
            #             icon: "plus"
            #             pos_hint: {"center_x": .5, "center_y": .5}
            
            #     MDButton:
            #         style: "text"
            #         theme_width: "Custom"
            #         height: "20dp"
            #         width: "60dp"
            #         radius: [0, 0, 0, 0]
            #         on_press: root.open_file(self)
            #         MDButtonText:
            #             id: text
            #             text: "文件(F)"
            #             font_style:"STSONG"
            #             role:"small"
            #             pos_hint: {"center_x": .5, "center_y": .5}

            #     MDButton:
            #         style: "text"
            #         theme_width: "Custom"
            #         height: "20dp"
            #         width: "60dp"
            #         radius: [0, 0, 0, 0]
            #         on_press: root.open_edit(self)
            #         MDButtonText:
            #             id: text
            #             text: "Edit(E)"
            #             pos_hint: {"center_x": .5, "center_y": .5}
                        
            #     MDButton:
            #         style: "text"
            #         theme_width: "Custom"
            #         height: "20dp"
            #         width: "60dp"
            #         radius: [0, 0, 0, 0]
            #         on_press: root.open_select(self)
            #         MDButtonText:
            #             id: text
            #             text: "Select(S)"
            #             pos_hint: {"center_x": .5, "center_y": .5}
                        
            #     MDButton:
            #         style: "text"
            #         theme_width: "Custom"
            #         height: "20dp"
            #         width: "60dp"
            #         radius: [0, 0, 0, 0]
            #         on_press: root.open_view(self)
            #         MDButtonText:
            #             id: text
            #             text: "View(V)"
            #             pos_hint: {"center_x": .5, "center_y": .5}

            #     MDButton:
            #         style: "text"
            #         theme_width: "Custom"
            #         height: "20dp"
            #         width: "60dp"
            #         radius: [0, 0, 0, 0]
            #         on_press:root.open_help(self)
            #         MDButtonText:
            #             id: text
            #             text: "Help(H)"
            #             pos_hint: {"center_x": .5, "center_y": .5}
                        
            #     Label:
            #         text: "111"
            #         theme_width: "Custom"
            #         width: "400dp"
            #         #size_hint: .5,None
            #     Label:
            #         text: "22"
            #         theme_width: "Custom"
            #         width: "400dp"
        MDBoxLayout:
            orientation: 'horizontal'
            MDBoxLayout:
                size_hint: None, 1
                width: "40dp"
                md_bg_color: app.theme_cls.secondaryContainerColor
                orientation: 'vertical'
                MDButton:
                    theme_width: "Custom"
                    height: "40dp"
                    width: "40dp"
                    radius: [0, 0, 0, 0]
                    #theme_bg_color: "Custom"
                    on_press: root.change_screen_to_chat()
                    MDButtonIcon:
                        icon: "folder-outline"
                        pos_hint: {"center_x": .5, "center_y": .5}
                MDButton:
                    on_press: app.root.ids.screen_manager.current="Library"
                    theme_width: "Custom"
                    height: "40dp"
                    width: "40dp"
                    radius: [0, 0, 0, 0]
                    #theme_bg_color: "Custom"
                    MDButtonIcon:
                        icon: "bookmark"
                        pos_hint: {"center_x": .5, "center_y": .5}
                MDButton:
                    on_press: app.root.ids.screen_manager.current="Bookmark"
                    theme_width: "Custom"
                    height: "40dp"
                    width: "40dp"
                    radius: [0, 0, 0, 0]
                    #theme_bg_color: "Custom"
                    MDButtonIcon:
                        icon: "library"
                        pos_hint: {"center_x": .5, "center_y": .5}
                MDLabel:
                    text: ""
                    theme_height: "Custom"
                    height: "40dp"
                MDButton:
                    on_press: app.root.ids.screen_manager.current="account"
                    theme_width: "Custom"
                    height: "40dp"
                    width: "40dp"
                    radius: [0, 0, 0, 0]
                    #theme_bg_color: "Custom" 
                    MDButtonIcon:
                        icon: "account-circle"
                        pos_hint: {"center_x": .5, "center_y": .5}
                MDButton:
                    on_press: app.root.ids.screen_manager.current="set"
                    theme_width: "Custom"
                    height: "40dp"
                    width: "40dp"
                    radius: [0, 0, 0, 0]
                    MDButtonIcon:
                        icon: "cog"
                        pos_hint: {"center_x": .5, "center_y": .5}
            MDScreenManager:
                id: screen_manager
                MDScreen:
                    name: "Files"
                    md_bg_color: app.theme_cls.surfaceBrightColor
                    MDBoxLayout:
                        orientation: 'horizontal'
                        MDFloatLayout:
                            size_hint_x: None
                            width: "250dp"
                            id: user_card_float_layout
                            md_bg_color: app.theme_cls.surfaceBrightColor
                            MDScrollView:
                                id: user_card_scroll_view
                                do_scroll_x: False
                                do_scroll_y: True
                                always_overscroll: True
                                bar_width: dp(3)
                                
                                MDBoxLayout:
                                    id: user_card_box
                                    padding: "10dp",0,"10dp",0
                                    orientation: "vertical"
                                    size_hint_y: None
                                    height: self.minimum_height
                                    spacing: dp(7)
                                    size_hint_x: None
                                    width: "250dp"
                                    UserCard:
                                        name:"Scene dialogue"
                                        image_path:"src/resource/image/character_avatar/ai_1.png"
                                        text:"Role-play chat"
                                        screen_name:"ChatMessageScoll_1"
                                        callback: root.change_chat_screen
                                    UserCard:
                                        name:"Topic training"
                                        image_path:"src/resource/image/character_avatar/ai_2.png"
                                        text:"Exercises"
                                        screen_name:"ChatMessageScoll_2"
                                        callback: root.change_chat_screen

                                    UserCard:
                                        name:"Writing guidance"
                                        image_path:"src/resource/image/character_avatar/ai_3.png"
                                        text:"Writing guidance"
                                        screen_name:"ChatMessageScoll_3"
                                        callback: root.change_chat_screen     
                        MDScreenManager:
                            id: chat_screen_manager
                            #只有动态添加才会生成动态id
                            MDScreen:
                                id: ChatMessageScoll_1
                                name: "ChatMessageScoll_1"
                                # ChatMessageScoll:
                                #     name:"1"
                            MDScreen:
                                id: ChatMessageScoll_2
                                name: "ChatMessageScoll_2"
                                #ChatMessageScoll:
                                size_hint:1,1
                            MDScreen:
                                id: ChatMessageScoll_3
                                name: "ChatMessageScoll_3"
                                #ChatMessageScoll:
                MDScreen:
                    name: "Bookmark"
                    #md_bg_color: app.theme_cls.primaryColor
                    MDLabel:
                        text: "Bookmark"
                        halign: "center"
                        #text_color: "white"
                    MDBoxLayout:
                        spacing: "24dp"
                        pos_hint: {"center_x": .5, "center_y": .7}
                        adaptive_size: True
                        orientation: 'horizontal'
            
                        MDButton:
                            on_release: screen_manager.current = "Files"
                            text: "Open standard sheet"

                        MDButton:
                            on_release: screen_manager.current = "Library"
                            text: "Open modal sheet"

                MDScreen:
                    name: "Library"
                    #md_bg_color: app.theme_cls.primaryColor
                    MDLabel:
                        text: "Library"
                        halign: "center"
                        #text_color: "white"
                    MDBoxLayout:
                        spacing: "24dp"
                        pos_hint: {"center_x": .5, "center_y": .7}
                        adaptive_size: True
                        orientation: 'horizontal'
                        MDButton:
                            on_release: screen_manager.current = "Bookmark"
                            text: "Open standard sheet"

                        MDButton:
                            on_release: screen_manager.current = "Files"
                            text: "Open modal sheet"
                MDScreen:
                    name: "set"
                    md_bg_color: app.theme_cls.primaryColor
                    SetPage:
                        id:setpage
                MDScreen:
                    name: "account"
                    md_bg_color: app.theme_cls.primaryColor
                    StatisticsPage:
                        id:statisticspage
        MDBoxLayout:
            orientation: 'horizontal'
            md_bg_color: "white"
            size_hint_y: None  # 锁定高度
            height: '20dp'  # 设置固定高度
            MDLabel:
                text: "状态栏，用于实时显示一些数据和程序状态"
                font_style: "STSONG"
                role:"small"
            MDLabel:
                text: "22"
                font_style: "STSONG"
                role:"small"

'''
Builder.load_string(KV)
from global_instance import api_manager,zhipu_group
from kivymd.uix.menu import MDDropdownMenu

class MainWindows(Screen):
    menu: MDDropdownMenu = None
    def __init__(self, **kwargs):
        super(MainWindows, self).__init__(**kwargs)
        self.temp_user_card_box_pos=self.ids.user_card_box.pos
        self.init_set()

    def change_chat_screen(self,text):
        self.ids.chat_screen_manager.current=text
        print(f"切换聊天屏幕到{text}")

    def init_set(self):
        self.ids.setpage.on_start()
        self.ids.statisticspage.on_start()
        return
    
    def open_account(self):
        return
    
    def open_help(self, menu_button):
        menu_items = []
        for item, method in {
            "Welcome": lambda: print("欢迎"),
            "documentation": lambda: print("后续功能开发中"),
            "about": lambda: print("后续功能开发中"),
        }.items():
            menu_items.append(
                {
                    "text": item,
                    "on_release": method,
                }
            )
        self.menu = MDDropdownMenu(
            caller=menu_button,
            items=menu_items,
        )
        self.menu.open()
        return
    def open_file(self,menu_button):
        menu_items = []
        for item, method in {
            "open file": lambda: print("打开文件并加载进阅读器"),
            "Open a recent file": lambda:print("显示近期文件列表，点击后加载"),
            "Save": lambda: print("手动保存历史记录"),
            "Quit": lambda: print("关闭程序"),
        }.items():
            menu_items.append(
                {
                    "text": item,
                    "on_release": method,
                }
            )
        self.menu = MDDropdownMenu(
            caller=menu_button,
            items=menu_items,
        )
        self.menu.open()
        return

    def open_edit(self,menu_button):
        menu_items = []
        for item, method in {
            "quash": lambda: print("撤销"),
            "recover": lambda: print("恢复"),
            "copy": lambda: print("复制"),
            "shear": lambda: print("剪切"),
            "Find": lambda: print("查找"),
        }.items():
            menu_items.append(
                {
                    "text": item,
                    "on_release": method,
                }
            )
        self.menu = MDDropdownMenu(
            caller=menu_button,
            items=menu_items,
        )
        self.menu.open()
        return
    
    def open_select(self,menu_button):
        menu_items = []
        for item, method in {
            "None": lambda: print("暂无功能"),
        }.items():
            menu_items.append(
                {
                    "text": item,
                    "on_release": method,
                }
            )
        self.menu = MDDropdownMenu(
            caller=menu_button,
            items=menu_items,
        )
        self.menu.open()
        return
    
    def open_view(self,menu_button):
        menu_items = []
        for item, method in {
            "Command Panel": lambda: print("命令面板"),
        }.items():
            menu_items.append(
                {
                    "text": item,
                    "on_release": method,
                }
            )
        self.menu = MDDropdownMenu(
            caller=menu_button,
            items=menu_items,
        )
        self.menu.open()
        return
    def change_screen_to_chat(self):
        if self.ids.screen_manager.current != "Files":
            self.ids.screen_manager.current="Files"
        else:
            print("动画触发")
            return
        
class MainProgram(MDApp):

    def build(self):
        Window.size = (1400, 1100)  # 设置窗口大小
        Window.left, Window.top = (100, 100)
        Window.minimum_width,Window.minimum_height = (1000, 800)  # 设置窗口最小大小
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.dynamic_color_quality=1
        self.theme_cls.theme_style_switch_animation = True
        self.theme_cls.theme_style_switch_animation_duration = 0.3
        return MainWindows()
    
    def add_ChatMessageScoll(self):
        """
        添加聊天框 生成动态id
        """
        #instance1.set_system_prompt("你是一个英语老师，主要的回答使用英语来交流，并且使用汉语来解析你的回答中使用的语法，词组，陌生的词汇，常见的知识不需要解释")
        self.CMS_1=ChatMessageScoll(name="场景对话")
        #self.CMS_1.set_api_moudel(instance1)
        self.CMS_1.insttance=self.CMS_1
        #self.CMS_1.add_ai_message()

        # instance2 = api_manager.create_instance("zhipu", "glm-4-flash")
        # instance2.set_system_prompt("你是一个英语老师，你要给学生出英语题目，可以出多种类型的题目，但是每次只出一道题目。出完后等待用户进行回答，回答完后告诉用户正确还是错误，并给出解析。解析完后继续出题")
        # self.CMS_2=ChatMessageScoll(name="题目训练",color="yellow",init_text="你好，我主要的职责是提供英语题目，每次提供一道练习题，你可以试着给出答案，我会详细的给出解析")
        # self.CMS_2.set_api_moudel(instance2)
        # self.CMS_2.add_ai_message()
        # self.CMS_2.insttance=self.CMS_2

        # instance3 = api_manager.create_instance("zhipu", "glm-4-flash")
        # instance3.set_system_prompt("你是一个英语老师，学生向你请教英语作文如何写，接下来的对话都要围绕如何写好作文来展开，学生会将作文的主题和写的作文发给你，你需要做出批改，给出建议")
        # self.CMS_3=WritingGuidance(name="写作指导")
        # self.CMS_3.set_api_moudel(instance3)
        # self.CMS_3.add_ai_message()
        # self.CMS_3.insttance=self.CMS_3

        #print(zhipu_group.list_models())
        # print(provider1.get_history())
        # print(provider2.get_history())
        # print(provider3.get_history())
        #print("————————主程序中查看聊天记录框的ids————————————")
        self.root.ids.ChatMessageScoll_1.add_widget(self.CMS_1)
        # self.root.ids.ChatMessageScoll_2.add_widget(self.CMS_2)
        # self.root.ids.ChatMessageScoll_3.add_widget(self.CMS_3)
        p=FinalInterface()
        self.root.ids.ChatMessageScoll_2.add_widget(p)

        t=WritingGuidance()
        t.set_api_moudel(zhipu_group.create_instance("glm-4-flash"),zhipu_group.create_instance("glm-4-flash"))
        self.root.ids.ChatMessageScoll_3.add_widget(t)


    
    def on_start(self):
        print("on_start")
        self.prev_size = Window.size
        self.prev_pos = (Window.left, Window.top)
        self.is_fullscreen = False
        # roleoption=RoleOption
        # self.root.ids.main_scroll.add_widget(roleoption())
        # print("————————主程序中查看聊天记录框的ids————————————")
        # print(self.root.ids.ChatMessageScoll_3.ids)
        self.add_ChatMessageScoll()
        '''性能分析，发布版记得移除这些'''
        # self.profile = cProfile.Profile()
        # self.profile.enable()

    def on_stop(self):
        # self.profile.disable()
        # self.profile.dump_stats('myapp.profile')
        return

    def open_settings(self, *largs):
        '''重载移除配置面板'''
        pass
    
    def minimize_window(self):
        Window.minimize()

    def toggle_fullscreen(self):
        if self.is_fullscreen:
            Window.maximize()
        else:
            Window.restore()
        self.is_fullscreen=not self.is_fullscreen        
                
    def close_app(self):
        self.stop()

    def on_drop_file(self, filename, x, y, *args):
        super().on_drop_file(filename, x, y, *args)
        print(f"Drop file: {filename}")

    def on_drop_text(self,text, x, y, *args):
        '''我不清楚这个要如何触发'''
        print(f"Drop text: {text}")
        
if __name__ == "__main__":
    MainProgram().run()