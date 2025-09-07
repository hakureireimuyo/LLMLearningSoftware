import sys
import os

# 添加项目根目录到模块查找路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.api.llm import LLMCombo
from src.core.api.llm import ProviderGroup
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
c.add_callback(lambda x:print(x,end=''))

m = Message("text")
m.add_system_pompmt("你是一个诗人,我给你一些题材或限定范围,你来写五言律诗,题目自拟,中心主题围绕提供的材料,每次只写一首,要巧妙的将主题融入进诗句中,不要反悔诗句外的其他内容")

c.set_message(m)

c.add_message("user","历史类")
#print(c.chat())
c.stream()
c.join()

m = Message("text")
m.add_system_pompmt("你是一个小说爱好者,推荐一些小说,只要书名和简介即可")

c.set_message(m)
    
c.add_message("user","历史类")
c.stream()
#print(c.chat())
c.join()
