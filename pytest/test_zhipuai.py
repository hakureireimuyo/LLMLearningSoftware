"""为了找出智谱的sdk的返回的数据结构以及一些特定信息"""

import sys
import os

# 添加项目根目录到模块查找路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.api.llm import LLMCombo
from src.core.api.llm import ProviderGroup
from src.core.api.llm.model import Message,ZhipuChatParams
from zhipuai import ZhipuAI


message = Message(
    session="test",
    max_context_tokens=1024,
    system_prompt="""
    你是一个linux系统,
    你要对用户输入的终端指令进行模拟,
    模拟并返回该指令的输出,
    仅仅返回指令产生的输出,
    以及模拟终端的交互界面,
    root@hcss-ecs-12ef:~#
    以上是用户的身份,计算机名字,以及初始位置,
    一些指令如果正确执行不会产生任何输出,同样你也要做到这点,
    对于错误的指令,同样要模拟错误返回,
    其余的都不需要返回"""
)
params = ZhipuChatParams(
    model="glm-4.5-flash",
    stream=False
)

def chat_api():
    client = ZhipuAI(api_key="7358c739697e4278c61eca16c7261856.8V5qJXS60Sdo1tGw")
    message.add_message(role="user",content="ls -l")
    #print(message.get_context())
    response = client.chat.completions.create(
        model=params.model,
        messages=message.get_context(),
        temperature=params.temperature,
        stream=params.stream,
        max_tokens=params.max_tokens,
        tools=params.tools,
        top_p=params.top_p
    )
    print(response.to_dict())
    #print(response.choices[0].message.content) # type: ignore

def sync_api():
    client = ZhipuAI(api_key="7358c739697e4278c61eca16c7261856.8V5qJXS60Sdo1tGw")
    message.add_message(role="user",content="ls -l")
    params.stream=True
    response = client.chat.completions.create(
        model=params.model,
        messages=message.get_context(),
        temperature=params.temperature,
        stream=params.stream,
        max_tokens=params.max_tokens,
        tools=params.tools,
        top_p=params.top_p
    )
    for chunk in response:
        #if chunk.choices[0].delta.content: # type: ignore
            # print(chunk.choices[0].delta.content,end='') # type: ignore
        print(chunk.to_dict())
    

if __name__ =="__main__":
    #async_chat()
    chat_api()
    sync_api()
