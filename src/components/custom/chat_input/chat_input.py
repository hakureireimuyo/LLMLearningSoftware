from src.components.common.ime import ImeTextInput
from kivymd.uix.textfield import MDTextFieldTrailingIcon,MDTextFieldLeadingIcon
from kivy.properties import OptionProperty
from src.components.common.informationitem import Notification

class ChatInput(ImeTextInput):
    """
    在实现了中文输入法下面实现了更多关于聊天输入的功能
    包括:
    图标按钮
    输出按钮
    语音输入

    """
    status = OptionProperty("normal", options=["normal", "sending", "waiting"])
    def __init__(self, **kwargs):
        super(ChatInput, self).__init__(**kwargs)
        # 其他初始化代码
        self.add_widget(MDTextFieldTrailingIcon(icon="send-circle-outline"))

    def on_status(self, instance, value):
        if value == "normal":
            self._trailing_icon.icon = "send-circle-outline"
        elif value == "sending":
            self._trailing_icon.icon = "send-variant-clock-outline"
        elif value == "waiting":
            self._trailing_icon.icon = "pause-circle-outline"

    def key_down_enter(self):
        if self.status == "sending":
            Notification(title="", content="正在输出中,请先中断输出")
            self.status = "waiting"
            return False
        
        if self.status!="normal":
            return
        
        if super().key_down_enter():
            self.status = "sending"
            return True
        return False

    def waiting_over(self,*args):
        self.status = "normal"