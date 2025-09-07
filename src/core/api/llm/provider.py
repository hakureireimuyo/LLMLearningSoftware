"""
在此处定义了接口的数据(包括一些公共数据和独立字典结构的属性)
以及api需要实现的函数,这些函数作为接口将提供最基础的调用
抽象类以及子类仅依赖第三方库,不依赖项目中的其他组件
数据将会通过传递的方式获取,实现松耦合
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, AsyncGenerator,List

# ================= 大语言模型基础接口定义 =================
class LLMProviderBase(ABC):
    """大语言模型服务提供者基础接口
    
    定义所有大语言模型服务提供者必须实现的通用接口
    """
    
    def __init__(self):
        """初始化大语言模型提供者"""
        self._endpoint: str = ""        # API请求地址
        self._identity: str = ""        # 身份标识（如组织ID）
        self._api_key: str = ""         # API密钥
        self._provider_name: str = ""   # 服务提供者名称

    def initialize(self,**krage):
        """设置必须的参数,比如身份凭证和api_key"""
        pass

    @abstractmethod
    def chat(self, messages: List[dict]) -> Any:
        """非流式聊天补全接口
        
        一次性获取完整的模型响应
        
        Args:
            messages: 对话消息列表，格式为 [{"role": "user", "content": "你好"}]
            
        Returns:
            完整的模型响应内容
        """
        pass
    
    @abstractmethod
    def stream(self, messages: List[dict]) -> Any:
        """流式聊天补全接口
        
        以流式方式逐步获取模型响应
        
        Args:
            messages: 对话消息列表
            
        Returns:
            生成器或流式响应对象，可逐步获取响应内容
        """
        pass

    @abstractmethod
    def stop_stream(self):
        """终止流输出"""
        pass

    @abstractmethod
    def embeddings(self, text: str) -> List[float]:
        """文本嵌入向量生成
        
        将文本转换为向量表示
        
        Args:
            text: 输入文本
            
        Returns:
            文本的向量表示
        """
        pass
    
    @abstractmethod
    def token_count(self, text: str) -> int:
        """计算文本的token数量
        
        Args:
            text: 输入文本
            
        Returns:
            文本对应的token数量
        """
        pass

    @abstractmethod
    def update_parameters(self, **kwargs) -> None:
        """更新模型参数"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """连通性测试"""
        pass

    @abstractmethod
    def get_parameters(self) -> dict:
        """返回当前配置的参数字典"""
        pass

    @abstractmethod
    def get_params(self):
        """返回params类型实例"""

    @abstractmethod
    def set_message(self,message):
        """设置上下文"""
        pass
    
    @abstractmethod
    def update_parameters(self,**kwarge):
        """更新参数"""
        pass

    @abstractmethod
    def set_params(self,params):
        """设置参数类对象"""
        pass

    @abstractmethod
    def set_stream_callback(self,callback):
        """设置流回调"""
        pass

    @abstractmethod
    def add_stream_callback(self, callback):
        """设置回调函数列表"""
        pass
    
    @abstractmethod
    def add_stream_finish_callback(self, callback):
        """设置流结束回调"""
        pass

    @abstractmethod
    def add_error_callback(self, callback):
        """"""
        pass
    
    @abstractmethod
    def join(self):
        """如果正在接受流式回调,则使用这个方法后等待流式结束才进行下一步"""
        pass
