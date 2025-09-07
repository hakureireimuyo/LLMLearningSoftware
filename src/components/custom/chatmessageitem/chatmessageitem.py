from components.common.textinteractorlabel import TextInteractorLabel,StreamLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, ObjectProperty,NumericProperty,ListProperty
from components.custom.avatarbadge import AvatarBadge
from src.core.evn import internal_resource_path
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.graphics import Color, Ellipse


class ChatMessageItem(MDBoxLayout):
    identifier = StringProperty()  # 用于唯一标识消息项的属性    
    message = StringProperty('')  # 消息内容的属性
    identity = StringProperty()  # 消息发送者的身份属性，例如 'user' 或 'ai'
    avatar_path = StringProperty()  # 头像路径属性

    def __init__(self, **kwargs):
        
        super().__init__(**kwargs)
        self._avatar=AvatarBadge(source=internal_resource_path(self.avatar_path),
                                 sizeVariant="large")

        self.orientation="horizontal"
        self.spacing=5
        self.adaptive_height=True
        self.size_hint_x=1
        if self.identity=="ai":
            self.add_widget(self._avatar)
            self._message=StreamLabel(radius = [0, 20, 20, 20])
            self.add_widget(self._message)
            self.add_widget(Widget(size_hint_x=1))
            r,g,b,a = self.theme_cls.surfaceColor
            self._message.set_background_color((r,g,b))
            self.pos_hint={"left":1}
        else:
            self.add_widget(Widget(size_hint_x=1))
            self._message=StreamLabel(radius = [20, 0, 20, 20])
            self.add_widget(self._message)
            self.add_widget(self._avatar)
            r,g,b,a = self.theme_cls.primaryContainerColor
            self._message.set_background_color((r,g,b))
            self.pos_hint={"right":1}

        self._safe_add_stream_str(self.message)

    def on_identity(self,instance,value):
        #print("identity",value)
        self.pos_hint={"left":1} if value=="ai" else {"right":1}
        # 交换顺序
        if self.identity=="user":
            return
        else:
            if len(self.children)!=3:
                return
            self.children[0],self.children[1],self.children[2]=self.children[2],self.children[1],self.children[0]
        
    def update_theme(self, instance, value):
        if self.identity=="ai":
            r,g,b,a = self.theme_cls.surfaceColor
            self._message.set_background_color((r,g,b))
        else:
            r,g,b,a = self.theme_cls.inversePrimaryColor
            self._message.set_background_color((r,g,b))
        pass

    def add_stream_str(self,_str):
        # 移动到主线程中进行
        Clock.schedule_once(lambda dt, s=_str: self._safe_add_stream_str(s))
    
    def _safe_add_stream_str(self, _str):
        """在主线程安全更新message属性"""
        self._message.stream_text(_str)