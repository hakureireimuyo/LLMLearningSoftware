"""
该模块是一个简单的头像类，继承于MDIconButton,在聊天框中会和每条message组件一起绑定
并且渲染，头像类主要区分用户和ai的回答，点击ai的头像会进入角色卡设置界面，点击用户的
头像会进入到用户个人数据设置界面
"""
from kivymd.uix.button import MDIconButton
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty,ObjectProperty
KV = """
<HeadImage>:
    size_hint: None, None
    size: dp(40), dp(40)
    pos_hint: {"center_y":.5, "center_y":.9}
    #md_bg_color: "blue"
    MDIconButton:
        id: head_image
        size_hint: None, None
        size: dp(40), dp(40)
        icon: root.icon
        on_release: root.on_press()
"""
Builder.load_string(KV)

class HeadImage(MDBoxLayout):
    icon=StringProperty("account")
    identity=StringProperty("User")
    callback = ObjectProperty(None)
    def __init__(self, **kwargs):
        super(HeadImage,self).__init__(**kwargs)
        # self.identity = kwargs.get("identity", "User")
        # self.icon = kwargs.get("icon", "account")
        # self.callback = kwargs.get("callback", None)

    def set_callback(self, func):
        self.callback = func

    def on_press(self):
        if self.callback:
            self.callback()
        # No need to call super().on_press() as MDBoxLayout has no on_press method
        return

class ExampleApp(MDApp):
    def build(self):    
        kwargs = {"identity": "User", "icon": "account", "callback": None}
        return HeadImage(**kwargs)

if __name__ == "__main__":
    ExampleApp().run()