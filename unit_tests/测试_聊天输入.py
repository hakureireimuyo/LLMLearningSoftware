import sys
from pathlib import Path

# 自动添加项目根目录和 src 目录
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / "src"))

from src.components.custom.chat_input import ChatInput

from src.core.api.llm import LLMCombo,ProviderGroup
from src.core.api.llm.model import Message

g = ProviderGroup()
data = [
    {
        "type":"zhipu",
        "voucher":{
            "api_key":"7358c739697e4278c61eca16c7261856.8V5qJXS60Sdo1tGw",
            "identity":""
        },
        "params":{
            "model":"glm-4.5-flash",
            "temperature":0.4,
            "top_p":0.2,
            "max_tokens":1024*8,
        }
    }
]
g.load_from_data(data)
zhipu = g.create_provider("zhipu")

c = LLMCombo()
c.load_provider(zhipu)
c.set_message(Message("ceshi"))
from src.components.custom.dialoguewindow import ChatMessages,ChatMessageScrollView
from src.components.custom.chatmessageitem import ChatMessageItem
from src.components.common.ime import ImeTextInput
from src.app import TestApp
from src.core.evn import internal_resource_path
from kivymd.uix.boxlayout import MDBoxLayout

current_stream_ai_message=None
class Test(TestApp):
    def build(self):
        self.com=MDBoxLayout(orientation='vertical',md_bg_color=self.theme_cls.backgroundColor)
        chat_message = ChatMessages(background_image=internal_resource_path("image/background.jpg"),
                                    background_opacity=0.8,
                                    background_video="D:/ProjectFloder/obs/2024-06-13 16-57-11.mp4")
        self.com.add_widget(chat_message)
        
        c.add_stream_callback(lambda x:add_ai_item_str(x))

        def add_item(x):
            item = ChatMessageItem(message=x,identity='user',avatar_path="image/user.jpg")
            chat_message.add_widget(item)
            c.add_message(role="user",context=x)
            c.stream()
            item = ChatMessageItem(message='',identity='ai',avatar_path="image/ai.png")

            chat_message.add_widget(item)
            global current_stream_ai_message
            current_stream_ai_message=item
            print(item.message,len(item.message))
            print(item._message.text)

        def add_ai_item_str(x):
            global current_stream_ai_message
            current_stream_ai_message.add_stream_str(x)
        chat_input = ChatInput(callback=add_item,multiline=True)
        self.com.add_widget(chat_input)

        c.add_stream_finish_callback(chat_input.waiting_over)
        c.add_error_callback(chat_input.waiting_over)
        return self.com
    
if __name__ == "__main__":
    Test().fps_monitor_start()
    Test().run()