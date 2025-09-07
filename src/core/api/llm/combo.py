from .zhipu import ZhipuAIProvider
from .group import ProviderGroup
from .provider import LLMProviderBase
from .model import Message
from typing import Optional,Any,Dict,List,Callable

class LLMCombo:
    """
    组合使用提供者、消息和参数的"枪"类
    支持动态切换组件
    """
    
    def __init__(self):

        self._current_provider: Optional[LLMProviderBase] = None
        self._current_message: Optional[Message] = None
        self._current_callback:List[Callable] = []
        self._error_callback:List[Callable] = []
    
    def load_provider(self, provider):
        """加载指定的提供者"""
        self._current_provider = provider
    
    def set_message(self, message: Message):
        """设置消息上下文"""
        self._current_message = message
        if self._current_provider:
            self._current_provider.set_message(message)
    
    def update_parameters(self, **kwargs):
        """更新当前提供者的参数配置"""
        if not self._current_provider:
            raise RuntimeError("参数未初始化")
        self._current_provider.update_parameters(**kwargs)
    
    def add_stream_callback(self,callback:callable):
        self._current_callback.append(callback)
        if self._current_provider is not None:
            self._current_provider.add_stream_callback(callback)

    def add_stream_finish_callback(self,callback:callable):
        if self._current_provider is not None:
            self._current_provider.add_stream_finish_callback(callback)

    def add_error_callback(self,callback:callable):
        if self._current_provider is not None:
            self._current_provider.add_error_callback(callback)

    def get_params(self) -> Dict[str, Any]:
        """获取当前参数配置"""
        return self._current_provider.get_parameters()
    
    def chat(self) -> Any:
        """执行聊天请求"""
        self._validate_components()
        return self._current_provider.chat()
    
    def stream(self):
        """执行流式聊天"""
        self._validate_components()
        return self._current_provider.stream()


    def stop_stream(self):
        """停止流式输出"""
        if self._current_provider:
            self._current_provider.stop_stream()

    def join(self):
        if self._current_provider:
            self._current_provider.join()

    def add_message(self,role:str,context:str):
        """添加消息"""
        if self._current_message:
            self._current_message.add_message(role=role,content=context)

    def add_messages(self,role,messages:list[str]):
        """添加消息列表"""
        for message in messages:
            self._current_message.add_message(role=role,content=message)

    def switch_provider(self, new_provider: LLMProviderBase, keep_message: bool = True,keep_callback:bool=True):
        """
        切换到新的提供者
        
        Args:
            keep_message: 是否保留当前消息上下文
        """
        # 保存当前消息
        current_message = self._current_message
        
        # 加载新提供者
        self.load_provider(new_provider)
        
        # 恢复消息
        if keep_message and current_message:
            self.set_message(current_message)

        # 恢复回调函数列表
        if keep_callback:
            self._current_provider.add_stream_callback(self._current_callback)

    
    def _validate_components(self):
        """验证所有组件已就绪"""
        if not self._current_provider:
            raise RuntimeError("提供者未加载")
        if not self._current_message:
            raise RuntimeError("消息上下文未设置")
    
    @property
    def message(self) -> Message:
        """当前消息实例"""
        return self._current_message
    
