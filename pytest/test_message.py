import sys
import os

# 添加项目根目录到模块查找路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.api.llm.model.message import Message
import time

def sync_compressor(messages):
    time.sleep(3)
    compressed_content = "\n".join([msg['content'] for msg in messages])
    return f"Compressed: {compressed_content[:100]}..."

manager = Message(
    session_id="test",
    compression_callback=sync_compressor
)

# 添加消息
manager.add_message("user", "Hello world")
manager.add_message("user", "Hello world")
manager.add_message("user", "Hello world")
manager.add_message("user", "Hello world")

excess_messages = manager.process_token_excess(5000)
print(excess_messages)
time.sleep(4)

print(manager.get_context())
print(manager.get_full_context())
