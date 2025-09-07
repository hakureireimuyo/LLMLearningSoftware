import sys
from pathlib import Path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / "src"))
from src.app import TestApp

from src.components.custom.dialoguewindow import ChatMessages,ChatMessageScrollView
from src.components.custom.chatmessageitem import ChatMessageItem
from src.components.custom.avatarbadge import AvatarBadge
from src.components.custom.timestamp import Timestamp
from kivy.lang import Builder

KV="""
MDBoxLayout:
    ChatMessages:
        id:chatmessages
        background:'resource/image/back_image.jpg'
        ChatMessageItem:
            message:"你好啊"
            identity:"user"
        ChatMessageItem:
            message:"helleqweqweo world"
            identity:"ai"
        ChatMessageItem:
            message:"你eqweqe好啊"
            identity:"user"
        ChatMessageItem:
            message:"heleqweqewlo world"
            identity:"ai"
        ChatMessageItem:
            message:"你qeweq好啊"
            identity:"user"
        Timestamp:
            time:"2024-08-08 12:00:00"
        ChatMessageItem:
            message:"你好eqweqwe啊"
            identity:"user"
        ChatMessageItem:
            message:"helh91ryy4913123lo world"
            identity:"ai"
        ChatMessageItem:
            message:"你好eqweqwe啊"
            identity:"user"
        ChatMessageItem:
            message:"helh91ryy4913123lo world"
            identity:"ai"
        ChatMessageItem:
            message:"你好eqweqeqwe啊"
            identity:"user"
        ChatMessageItem:
            message:"hello world"
            identity:"ai"
            
"""
from src.core.evn import internal_resource_path
from kivymd.uix.button import MDButton
class Test(TestApp):
    def build(self):
        self.com=ChatMessages(background=internal_resource_path("image/back_image.jpg"),background_opacity=0.5)
        self.com.add_widget(ChatMessageItem(message="你好啊",identity="user"))
        self.com.add_widget(ChatMessageItem(message="helleqweqweo world",identity="ai"))
        # button=MDButton(on_press=lambda x:self.com.add_widget(ChatMessageItem(message="你好啊",identity="user")))
        # self.com.add_widget(button)
        # def change_background():
        #     self.com.background='resource/image/R-C.jpg'
        #     print("背景改变")
        # def change_opacity():
        #     self.com.background_opacity+=0.1
        #     if self.com.background_opacity>1:
        #         self.com.background_opacity=0
        # _button=MDButton(on_press=lambda x:change_background())
        # self.com.add_widget(_button)
        # _button2=MDButton(on_press=lambda x:change_opacity())
        # self.com.add_widget(_button2)
        self.com.add_widget(ChatMessageItem(message="你eqweqe好啊",identity="user"))
        self.com.add_widget(ChatMessageItem(message="heleqweqewlo world",identity="ai"))
        self.com.add_widget(ChatMessageItem(message="你qewewq好啊",identity="user"))
        self.com.add_widget(Timestamp(time="2024-08-08 12:00:00"))
        self.com.add_widget(ChatMessageItem(message="你好eqweqwe啊",identity="user"))
        self.com.add_widget(ChatMessageItem(message="helh91ryy4913123lo world",identity="ai"))
        self.com.add_widget(ChatMessageItem(message="你好eqweqwe啊",identity="user"))
        self.com.add_widget(ChatMessageItem(message="helh91ryy4913123lo world",identity="ai"))
        self.com.add_widget(ChatMessageItem(message="你好eqweqeqwe啊",identity="user"))
        self.com.add_widget(ChatMessageItem(message="hello world",identity="ai"))
        self.com.add_widget(ChatMessageItem(message="你好qeq47293479274982749872389478923749729347924927947972083748927408273408723084708237480273084732074032740987234807eqeqeqweqweqweqweweweqweqweqwewee啊",identity="user"))
        self.com.add_widget(ChatMessageItem(message="helh91ryy4913123lo world",identity="ai"))
        self.com.add_widget(ChatMessageItem(message="你好eqweqwe啊",identity="user"))
        self.com.add_widget(ChatMessageItem(message="helh91ryy4913123lo world",identity="ai"))
        self.com.add_widget(ChatMessageItem(message="你好eqweqeqwe啊",identity="user"))
        self.com.add_widget(ChatMessageItem(message="hello world",identity="ai"))
        self.com.add_widget(ChatMessageItem(message="你好eqweqwe啊",identity="user"))
        self.com.add_widget(ChatMessageItem(message="helh91ryy4913123lo world",identity="ai"))
        #self.com=Builder.load_string(KV)
        return super().build()

if __name__=="__main__":
    Test().fps_monitor_start()
    Test().run()