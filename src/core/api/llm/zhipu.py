from typing import Dict, Any, Optional, AsyncGenerator, List, Callable
from zhipuai import ZhipuAI
from zhipuai.core._errors import ZhipuAIError,APIAuthenticationError,APIStatusError,APIResponseValidationError
import warnings
import threading
import inspect
from .provider import LLMProviderBase
from .model import Message, ZhipuChatParams

class ZhipuAIProvider(LLMProviderBase):
    def __init__(self):
        '''智谱ai提供类'''        
        super().__init__()
        self._provider_name = "ZhiPu"
        self._api_key = ""
        self._client = None
        self._params = ZhipuChatParams()
        self._context_manager = None
        self._stream_callback:List[Callable] = []
        self._stream_finish_callback:List[Callable]=[]
        self._error_callback:List[Callable]=[]
        self._stream_thread = None
        self._stop_stream = threading.Event()
        
    def initialize(self,api_key: str="",identity:str=""):
        """
        初始化客户端和上下文管理器
        
        :param api_key: ZhiPu API密钥
        :raises ValueError: 如果参数不合法
        """
        # 参数验证
        errors = []
        if not api_key or len(api_key.strip()) < 16:
            errors.append("API密钥无效或太短")
        # 如果发现错误则抛出异常
        if errors:
            raise ValueError("\n".join(errors))
        
        # 初始化API客户端
        self._api_key = api_key
        self._client = ZhipuAI(api_key=api_key)
    
    def set_message(self,message:Message):
        # 初始化上下文管理器
        if type(message) is not Message:
            return TypeError("参数类型必须是Message")
        self._context_manager = message

    def set_params(self,params:ZhipuChatParams):
        if type(ZhipuChatParams) is not ZhipuChatParams:
            return TypeError("参数类型必须是ZhipuChatParams")
        self._params = params

    def get_params(self):
        """返回内部的参数实例"""
        return self._params
    
    def add_system_prompt(self, prompt: str):
        """设置系统提示词"""
        if self._context_manager is None:
                return ValueError("未设置上下文")
        if self._context_manager:
            self._context_manager.add_system_pompmt(prompt)
            
    def set_stream_callback(self,callback):
        self._stream_callback.append(callback)

    def add_stream_callback(self, callback: Callable[[str], None]):
        """设置流式响应回调函数"""
        self._stream_callback.append(callback)

    def add_stream_finish_callback(self, callback: Callable[[str], None]):
        """设置一次流式完成应该执行的回调函数"""
        self._stream_finish_callback.append(callback)

    def add_error_callback(self, callback):
        self._error_callback.append(callback)
    
    def add_message(self, role: str, content: str):
        """添加用户/助手消息"""
        if self._context_manager is None:
                return ValueError("未设置上下文")
        if self._context_manager:
            self._context_manager.add_message(role, content)
    
    def get_message(self):
        if self._context_manager is None:
                return ValueError("未设置上下文")
        return self._context_manager
    
    def update_parameters(self, **kwargs) -> None:
        """更新模型参数"""
        if self._params is None:
                return ValueError("未设置参数")
        valid_params = [
            'model', 'temperature', 'top_p', 'max_tokens', 
            'stream', 'do_sample', 'tools', 'tool_choice'
        ]
        
        for key, value in kwargs.items():
            if key in valid_params:
                setattr(self._params, key, value)
            else:
                warnings.warn(f"忽略无效参数: {key}")
    
    def get_parameters(self) -> dict:
        """返回当前模型参数配置"""
        if self._params is None:
            return ValueError("parpams参数为空")
        return self._params.payload()
    
    def chat(self) -> Any:
        """非流式聊天补全接口"""
        if not self._client:
            raise RuntimeError("Provider not initialized. Call initialize() first.")
        
        try:
            # 使用传入的消息或上下文管理器中的消息
            if self._context_manager is None:
                return ValueError("未设置上下文")
            if self._params is None:
                return ValueError("未设置参数")
            final_messages = self._context_manager.get_context()
            
            # 设置API参数
            self._params.set_message(final_messages)
            self._params.stream = False
            # 获取参数
            params = self._params.payload()
            # 检查SDK是否支持response_format参数,暂时为了在交互环境中使用
            # 可能是因为版本原因,交互式环境不支持格式参数,此处将参数移除
            # 正常调用支持不会影响,但后续也会删除
            create_params = inspect.signature(self._client.chat.completions.create).parameters
            if "response_format" not in create_params:
                params.pop("response_format", None)
        
            # 调用API
            response = self._client.chat.completions.create(**params)
            
            # 处理响应
            if response.choices and response.choices[0].message.content: # type: ignore
                content = response.choices[0].message.content # type: ignore
                total_tokens = response.usage["total_tokens"]
                self._context_manager.process_token_excess(total_tokens)
                # 添加到上下文
                if self._context_manager:
                    self._context_manager.add_message("assistant", content)
                
                return content
            return None
            
        except ZhipuAIError as e:
            self._handle_api_error(e)
            for callback in self._error_callback:
                callback()
            return None
    
    def _stream_worker(self):
        """流式工作线程函数"""
        if not self._client:
            raise RuntimeError("Provider not initialized. Call initialize() first.")
        try:
            # 获取当前上下文
            if self._context_manager is None:
                return ValueError("未设置上下文")
            if self._params is None:
                return ValueError("未设置参数")
            messages = self._context_manager.get_context()
            self._params.set_message(messages)
            self._params.stream = True
            
            # 调用流式API
            response = self._client.chat.completions.create(**self._params.payload())
            
            # 处理流式响应
            full_content = ""
            for chunk in response:
                if self._stop_stream.is_set():
                    break
                last_chunk = chunk
                if chunk.choices and chunk.choices[0].delta.content: # type: ignore
                    content_piece = chunk.choices[0].delta.content # type: ignore
                    full_content += content_piece
                    
                    # 通过回调传递数据
                    # if self._stream_callback:
                    #     self._stream_callback(content_piece)

                    # 每次流式信息的回调
                    for call in self._stream_callback:
                        call(content_piece)
            
            # 将完整响应添加到上下文
            if full_content and self._context_manager:
                self._context_manager.add_message("assistant", full_content)

            # 设置总tokens
            try:
                # 尝试直接提取usage.total_tokens
                total_tokens = last_chunk.usage.total_tokens
            except AttributeError:
                # 尝试从字典结构提取（某些API可能返回字典）
                if hasattr(last_chunk, 'to_dict'):
                    chunk_dict = last_chunk.to_dict()
                    if 'usage' in chunk_dict and 'total_tokens' in chunk_dict['usage']:
                        total_tokens = chunk_dict['usage']['total_tokens']
            
            if total_tokens is not None:
                self._context_manager.process_token_excess(total_tokens)

            # 完成一次流式的回调
            for callback in self._stream_finish_callback:
                callback("assistant",full_content)

        except ZhipuAIError as e:
            self._handle_api_error(e)
            for callback in self._error_callback:
                callback()
        finally:
            self._stop_stream.clear()
    
    def stream(self):
        """流式聊天补全接口（在新线程中执行）"""
        if not self._client:
            raise RuntimeError("Provider not initialized. Call initialize() first.")
        
        if self._stream_thread and self._stream_thread.is_alive():
            raise RuntimeError("Stream operation already in progress")
        
        self._stop_stream.clear()
        self._stream_thread = threading.Thread(target=self._stream_worker)
        self._stream_thread.daemon = True
        self._stream_thread.start()
        return True
    
    def join(self,timeout:int=300):
        import time
        p=0
        while True:
            p+=1
            if not self._stream_thread.is_alive() or p>timeout:
                break
            else:
                time.sleep(1)

    def stop_stream(self):
        """停止流式响应"""
        if self._stream_thread and self._stream_thread.is_alive():
            self._stop_stream.set()
            self._stream_thread.join(timeout=2.0)
    
    def _handle_api_error(self, error: ZhipuAIError):
        """处理API错误"""
        error_type = type(error).__name__
        error_msg = f"ZhipuAI API Error ({error_type}): {str(error)}"
        
        if isinstance(error, APIAuthenticationError):
            error_msg += "\n请检查API密钥是否正确"
        elif isinstance(error, APIStatusError):
            error_msg += f"\nHTTP状态码: {error.status_code}"
        elif isinstance(error, APIResponseValidationError):
            error_msg += "\nAPI响应格式验证失败"
        
        warnings.warn(error_msg)
    
    def embeddings(self, text: str) -> List[float]:
        """文本嵌入向量生成（暂未实现）"""
        warnings.warn("Embeddings not implemented for ZhipuAIProvider")
        return []
    
    def token_count(self, text: str) -> int:
        """计算文本的token数量（估算）"""
        # 简单估算：英文1token≈4字符，中文1token≈2字符
        ch_count = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        en_count = len(text) - ch_count
        return int(en_count / 4 + ch_count / 2)
    
    def is_available(self) -> bool:
        """连通性测试"""
        if not self._client:
            return False
        
        try:
            if self._params is None:
                return ValueError("未设置参数")
            # 发送一个简单的测试请求
            test_params = ZhipuChatParams()
            test_params.set_message([{"role": "user", "content": "ping"}])
            test_params.max_tokens = 1
            
            self._client.chat.completions.create(**test_params.payload())
            return True
        except:
            return False
    
    def save_context_to_db(self):
        """保存当前对话上下文到数据库（示意）"""
        if self._context_manager is None:
                return ValueError("未设置上下文")
        # 实际实现中会连接数据库并保存上下文
        if self._context_manager:
            context = self._context_manager.get_full_context()
            print(f"保存上下文到数据库: {context}")
            # 实际数据库操作代码...
    
    def load_context_from_db(self, session_id: str):
        """从数据库加载对话上下文（示意）"""
        if self._context_manager is None:
                return ValueError("未设置上下文")
        # 实际实现中会从数据库加载上下文
        print(f"从数据库加载上下文: {session_id}")
        # 实际数据库操作代码...
        # 初始化上下文管理器
        self._context_manager = Message(session_id=session_id)