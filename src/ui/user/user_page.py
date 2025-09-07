from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
import tkinter as tk
from tkinter import filedialog
from kivy.properties import NumericProperty, ListProperty, BooleanProperty, StringProperty
from kivy.metrics import dp
from kivy.uix.widget import Widget

Builder.load_string('''
<UserItem>:
    orientation:'vertical'
    size_hint:1,None
    height:dp(70)
    padding:dp(10)
    md_bg_color:app.theme_cls.onPrimaryColor
    MDBoxLayout:
        orientation:'horizontal'
        size_hint:1,None
        height:dp(69)
        MDLabel:
            text:root.title
            font_style:'STSONG'
            pos_hint:{"center_y":.2}
        MDTextField:
            id:input_field
            hint_text:root.hint_text
            font_name:'STSONG'
            text:root.text
            font_size: "26sp"
            readonly:root.only_read
            on_text:root.rollback()
            #disabled:root.only_read
    MDDivider:
        height:dp(1)
<UserAdvter>:
    size_hint:None,None
    size:dp(160),dp(160)
    radius: "80dp", "80dp", "80dp", "80dp"
    pos_hint: {"center_x":.5, "center_y":.5}
    md_bg_color:app.theme_cls.primaryColor
    FitImage:
        id:advter_image
        source: "src/resource/image/advter_image.jpg"
        size_hint:None,None
        size:dp(160),dp(160)
        radius: "80dp", "80dp", "80dp", "80dp"
        pos_hint: {"center_x":.5, "center_y":.5}       
<UserPage>:
    orientation: 'vertical'
    padding: 10
    spacing: 10
    size_hint:1,1
    md_bg_color:app.theme_cls.backgroundColor
    MDBoxLayout:
        orientation:'vertical'
        MDRelativeLayout:
            size_hint:1,None
            height:dp(300)
            FitImage:
                source: "src/resource/image/back_image.jpg"
                size_hint:1,1
                pos_hint: {"center_x": .5, "center_y": .5}
                radius: "36dp", "36dp", 0, 0
            UserAdvter:
        MDScrollView:
            do_scroll_x:False
            do_scroll_y:True
                        
            MDBoxLayout:
                orientation:'vertical'
                id:user_data_layout
                adaptive_height: True
        MDBoxLayout:
            orientation:'horizontal'
            size_hint:1,None
            height:dp(60)
            padding:dp(10)
            spacing:dp(10)
            Widget:
            MDButton:
                pos_hint:{"center_x":0.5, "center_y":0.5}
                radius: 0,0,0,0
                on_release:root.create_user()
                MDButtonText:
                    text:"注册新用户"
                    font_style:"STSONG"
                    font_size: "26sp"
            MDButton:
                pos_hint:{"center_x":0.5, "center_y":0.5}
                radius: 0,0,0,0
                on_release:root.switch_user()
                MDButtonText:
                    text:"切换账号"
                    font_style:"STSONG"
                    font_size: "26sp"
            Widget:

''')
from global_instance import user_data
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
class UserAdvter(MDCard):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.open_file_manager()
            
    def open_file_manager(self):
        if advter_file_path := self.select_file():
            print("选中文件路径:", advter_file_path)
            #如果是图片文件，就显示在头像上
            if advter_file_path.endswith((".jpg", ".png", ".jpeg")):
                self.ids.advter_image.source=advter_file_path
        else:
            print("未选择文件")
    def select_file(self):
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        file_path = filedialog.askopenfilename(
            title="选择文件",
            filetypes=[("所有文件", "*.*"), ("文本文件", "*.txt")]  # 可选文件类型过滤
        )
        root.destroy()
        return file_path if file_path else None
    
class UserItem(MDBoxLayout):
    title=StringProperty('')
    hint_text=StringProperty('')
    text=StringProperty('')
    only_read=BooleanProperty(False)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def rollback(self):
        self.text=self.ids.input_field.text
        
def convert_seconds(seconds):
    if type(seconds)!=int:
        return seconds
    hours = seconds // 3600
    remaining = seconds % 3600
    minutes = remaining // 60
    return f"{hours}小时{minutes}分"
from kivymd.uix.dialog import MDDialog
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogIcon,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogButtonContainer,
    MDDialogContentContainer,
)
from kivymd.uix.divider import MDDivider
from kivymd.uix.button import MDButton,MDButtonText
class UserPage(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #print(self.user_data.data)
        self.load_data()

    def load_data(self):
        for key,value in user_data.data.items():
            #print(key,value)
            if key=="id":continue
            if key=="advter_image":continue
            if key=="username":
                temp_com=UserItem(title='用户名',hint_text='请输入用户名',text=value,only_read=False)
                self.ids.user_data_layout.add_widget(temp_com)
                continue
            if key=="registration_time":
                temp_com=UserItem(title='注册时间',hint_text='',text=value,only_read=True)
                self.ids.user_data_layout.add_widget(temp_com)
                continue
            if key=="total_usage_time":

                temp_com=UserItem(title='总使用时间',hint_text='',text=convert_seconds(value),only_read=True)
                self.ids.user_data_layout.add_widget(temp_com)
                continue
            if key=="total_listening":
                _str=str(value)+"个"
                temp_com=UserItem(title='总听力单词',hint_text='',text=_str,only_read=True)
                self.ids.user_data_layout.add_widget(temp_com)
                continue
            if key=="total_translation":
                _str=str(value)+"个"
                temp_com=UserItem(title='总翻译单词',hint_text='',text=_str,only_read=True)
                self.ids.user_data_layout.add_widget(temp_com)
                continue
            if key=="total_reading":
                _str=str(value)+"个"
                temp_com=UserItem(title='总阅读单词',hint_text='',text=_str,only_read=True)
                self.ids.user_data_layout.add_widget(temp_com)
                continue
            if key=="total_writing":
                _str=str(value)+"个"
                temp_com=UserItem(title='总书写单词',hint_text='',text=_str,only_read=True)
                self.ids.user_data_layout.add_widget(temp_com)
                continue
            if key=="total_api_calls":
                _str=str(value)+"次"
                temp_com=UserItem(title='总api调用次数',hint_text='',text=_str,only_read=True)
                self.ids.user_data_layout.add_widget(temp_com)
                continue
            if key=="total_output_tokens":
                _str=str(value)+"tokens"
                temp_com=UserItem(title='总输出token数',hint_text='',text=_str,only_read=True)                
                self.ids.user_data_layout.add_widget(temp_com)
                continue
    def create_user(self):
        MDDialog(
            # ----------------------------Icon-----------------------------
            # MDDialogIcon(
            #     icon="refresh",
            # ),
            # # -----------------------Headline text-------------------------
            # MDDialogHeadlineText(
            #     text="Reset settings?",
            # ),
            # # -----------------------Supporting text-----------------------
            # MDDialogSupportingText(
            #     text="This will reset your app preferences back to their "
            #     "default settings. The following accounts will also "
            #     "be signed out:",
            # ),
            # -----------------------Custom content------------------------
            MDDialogContentContainer(
                MDDivider(),
                MDBoxLayout(
                    MDBoxLayout(
                        MDLabel(
                            text="账号名字",
                            font_style="STSONG",
                            font_size="26sp",
                        ),
                        MDTextField(
                            hint_text="请输入用户名",
                            font_name="STSONG",
                            font_size="26sp",
                            
                        ),
                        orientation="horizontal",
                        padding="12dp",
                        spacing="12dp",
                    ),
                    MDDivider(),
                    MDBoxLayout(
                        MDLabel(
                            text="账号密码",
                            font_style="STSONG",
                            font_size="26sp",
                        ),
                        MDTextField(
                            hint_text="请输入密码",
                            font_name="STSONG",
                            font_size="26sp",
                        ),
                        orientation="horizontal",
                        padding="12dp",
                        spacing="12dp",
                    ),
                    orientation="vertical",
                    size_hint_y=None,
                    height="200dp",
                    size_hint_x=None,
                    width="400dp",
                ),
                
            ),
            # ---------------------Button container------------------------
            MDDialogButtonContainer(
                Widget(),
                MDButton(
                    MDButtonText(
                        text="Cancel",
                    ),
                    style="text",
                ),
                MDButton(
                    MDButtonText(
                        text="Accept",
                    ),
                    style="text",
                ),
                spacing="8dp",
            ),
            # -------------------------------------------------------------
        ).open()
    def switch_user(self):
        MDDialog(
            # ----------------------------Icon-----------------------------
            # MDDialogIcon(  
            #     icon="refresh",
            # ),
            # # -----------------------Headline text-------------------------
            # MDDialogHeadlineText(
            #     text="Reset settings?",
            # ),
            # # -----------------------Supporting text-----------------------
            # MDDialogSupportingText(
            #     text="This will reset your app preferences back to their "
            #     "default settings. The following accounts will also "
            #     "be signed out:",
            # ),
            # -----------------------Custom content------------------------
            MDDialogContentContainer(
                MDDivider(),
                MDBoxLayout(
                    MDBoxLayout(
                        MDCard(
                            MDLabel(
                            text="root",
                            font_style="STSONG",
                            font_size="26sp",
                        )
                        )
                        , 
                        MDCard(
                            MDLabel(
                            text="user1",
                            font_style="STSONG",
                            font_size="26sp", 
                        )
                        ),
                        MDCard(
                            MDLabel (
                            text="user2",
                            font_style="STSONG",
                            font_size="26sp", 
                        )
                        ),
                        orientation="vertical",
                    ),
                    size_hint_y=None,
                    height="200dp",
                    size_hint_x=None,
                    width="400dp",
                )  
            )
        ).open()


from kivymd.app import MDApp
class ExampleApp(MDApp):
    def build(self):
        return UserPage()
if __name__ == '__main__':
    ExampleApp().run()