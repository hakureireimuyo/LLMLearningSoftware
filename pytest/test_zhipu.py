import sys
import os

# 添加项目根目录到模块查找路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from src.core.api.llm import ZhipuAIProvider
from src.core.api.llm.model import Message,ZhipuChatParams

def test():
    provider = ZhipuAIProvider()

    params = ZhipuChatParams(model='glm-4.5-flash',max_tokens=1024*16,stream=True)
    message = Message(session="ceshi",raw_id_start=1,compressed_id_start=1)

    provider.initialize(api_key="7358c739697e4278c61eca16c7261856.8V5qJXS60Sdo1tGw")
    provider.set_message(message=message)
    provider.set_params(params=params)
    provider.set_stream_callback(lambda content:print(content,end="",flush=True))
        
    while True:
        _in = input("")
        if _in == "" or _in == "exit":
            break
        message.add_message(role="user",content=_in)
        result = provider.stream()
        #print(result)
        provider.join()
        print(provider.get_message())

if __name__ == "__main__":
    test()