import abc
from typing import List, Tuple

class BaseIMEPlatform(abc.ABC):
    """输入法平台抽象基类"""
    @abc.abstractmethod
    def start_listening(self):
        """开始监听输入法事件"""
        
    @abc.abstractmethod
    def stop_listening(self):
        """停止监听输入法事件"""
        
    @abc.abstractmethod
    def get_preview_data(self) -> Tuple[List[str], int]:
        """
        获取当前预览词数据
        :return: (候选词列表, 当前选中索引)
        """
        
    @abc.abstractmethod
    def handle_key_event(self, key: str) -> bool:
        """
        处理键盘事件
        :param key: 按键名称
        :return: 是否已处理该事件
        """