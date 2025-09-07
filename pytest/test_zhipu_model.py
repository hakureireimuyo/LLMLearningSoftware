import sys
import os

# 添加项目根目录到模块查找路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time
from src.core.api.llm.model import ZhipuChatParams
from src.core.api.llm.model import Message
import requests
import json

url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
message = Message(
    session_id="test",
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

def async_chat():
    while True:
        _in = input("")
        if _in=="exit":
            break
        message.add_message(role="user",content=_in)
        params.set_message(message=message.get_context())

        payload = params.payload()
        headers = {
            "Authorization": "Bearer 7358c739697e4278c61eca16c7261856.8V5qJXS60Sdo1tGw",
            "Content-Type": "application/json"
        }

        start_time = time.time()
        with requests.post(url, json=payload, headers=headers, stream=True) as response:
            # 立即开始处理流
            full_content = ""
            role = None
            total_tokens = None
            
            # print("响应开始时间:", time.time() - start_time)  # 显示首个字节到达时间
            
            for chunk in response.iter_lines():
                
                # 处理空行和结束标记
                if not chunk or chunk == b'data: [DONE]':
                    continue
                
                # 处理数据块
                if chunk.startswith(b'data: '):
                    json_str = chunk[6:].decode('utf-8')
                    try:
                        data = json.loads(json_str)
                    except:
                        continue
                    
                    # 处理角色信息
                    if not role and "choices" in data:
                        for choice in data["choices"]:
                            if "role" in choice.get("delta", {}):
                                role = choice["delta"]["role"]
                    
                    # 实时输出内容
                    if "choices" in data:
                        for choice in data["choices"]:
                            delta = choice.get("delta", {})
                            if delta.get("content"):
                                content_piece = delta["content"]
                                full_content += content_piece
                                print(content_piece, end='', flush=True)
                    # 处理token统计
                    if "usage" in data and "total_tokens" in data["usage"]:
                        total_tokens = data["usage"]["total_tokens"]
            print("")
            # print("\n响应结束时间:", time.time() - start_time)
        # 最终结果
        # print(f"\nRole: {role}")  # 输出: assistant
        # print(f"Full Content: {full_content}")  # 输出: Templates
        # print(f"Total Tokens: {total_tokens}")  # 输出: 140

def chat():
    
    while True:
        _in = input("")
        if _in=="exit":
            break
        message.add_message(role="user",content=_in)
        
        params.set_message(message=message.get_context())
        params.stream=False
        payload = params.payload()
        headers = {
            "Authorization": "Bearer 7358c739697e4278c61eca16c7261856.8V5qJXS60Sdo1tGw",
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=payload, headers=headers)
        role = response.json()['choices'][0]['message']['role']
        content = response.json()['choices'][0]['message']['content']
        print(content)
        message.add_message(role=role,content=content)

from zhipuai import ZhipuAI

def chat_api():
    client = ZhipuAI(api_key="7358c739697e4278c61eca16c7261856.8V5qJXS60Sdo1tGw")
    message.add_message(role="user",content="ls -l")
    print(message.get_context())
    response = client.chat.completions.create(
        model=params.model,
        messages=message.get_context(),
        temperature=params.temperature,
        stream=params.stream,
        max_tokens=params.max_tokens,
        tools=params.tools,
        top_p=params.top_p
    )
    print(response.choices[0].message.content) # type: ignore

    
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
        if chunk.choices[0].delta.content: # type: ignore
            print(chunk.choices[0].delta.content,end='') # type: ignore

if __name__ =="__main__":
    #async_chat()
    #chat()
    sync_api()