from dataclasses import dataclass, field
from typing import List, Dict, Any, Literal, Optional, Union

@dataclass
class ZhipuChatParams:
    """
    智谱AI对话API请求参数类
    文档参考: https://open.bigmodel.cn/dev/api#chat
    """
    
    # 必需参数
    model: Literal[
        "glm-4.5", "glm-4.5-air", "glm-4.5-x", "glm-4.5-airx", "glm-4.5-flash",
        "glm-4-plus", "glm-4-air-250414", "glm-4-airx", "glm-4-flashx",
        "glm-4-flashx-250414", "glm-z1-air", "glm-z1-airx", "glm-z1-flash", "glm-z1-flashx"
    ] = "glm-4.5-flash"
    """调用的对话模型代码"""
    
    messages: List[Dict[str, Any]] = field(default_factory=list)
    """对话消息列表，包含完整上下文信息"""
    
    # 可选参数
    request_id: Optional[str] = None
    """请求唯一标识符，建议使用UUID"""
    
    do_sample: bool = True
    """是否启用采样策略生成文本"""
    
    stream: bool = False
    """是否启用流式输出模式"""
    
    temperature: float = 0.6
    """采样温度，控制输出的随机性"""
    
    top_p: float = 0.95
    """核采样参数，控制输出的多样性"""
    
    max_tokens: int = 1024*16
    """模型输出的最大token数量"""
    
    tools: Optional[List[Dict[str, Any]]] = None
    """模型可以调用的工具列表"""
    
    tool_choice: Literal["auto"] = "auto"
    """控制模型如何选择工具"""
    
    user_id: Optional[str] = None
    """终端用户的唯一标识符"""
    
    stop: Optional[List[str]] = None
    """停止词列表"""
    
    _thinking_enabled: bool = False  # 内部存储布尔值

    _response_format_type: Literal["text","json"] = "text"  # 内部存储字符串值
    # 自动处理默认值的逻辑
    def __post_init__(self):
        # 根据模型系列设置默认参数
        if any(model_prefix in self.model for model_prefix in ["glm-z1", "glm-4"]):
            self.temperature = 0.75 if self.temperature == 0.6 else self.temperature
            self.top_p = 0.9 if self.top_p == 0.95 else self.top_p
        
        # 验证参数范围
        self._validate_parameters()
    
    def _validate_parameters(self):
        """验证参数是否符合API要求"""
        if self.temperature < 0 or self.temperature > 1:
            raise ValueError("temperature必须在0.0到1.0之间")
        
        if self.top_p < 0 or self.top_p > 1:
            raise ValueError("top_p必须在0.0到1.0之间")
        
        if self.max_tokens < 1 or self.max_tokens > 98304:
            raise ValueError("max_tokens必须在1到98304之间")
        
        if self.user_id and (len(self.user_id) < 6 or len(self.user_id) > 128):
            raise ValueError("user_id长度必须在6到128个字符之间")
        
        if self.stop and len(self.stop) > 1:
            raise ValueError("stop列表最多只能包含一个元素")
        
    def set_message(self,message:List[Dict[str, Any]]) -> None:
        self.messages = message

    @property
    def thinking(self) -> dict:
        """返回API需要的思维链配置结构"""
        return {"type": "enabled"} if self._thinking_enabled else {"type": "disabled"}
    
    @property
    def response_format(self) -> dict:
        """返回API需要的响应格式结构"""
        return {"type": "text"} if self._response_format_type == "text" else {"type": "json_object"}

    # 提供设置器方法用于外部赋值
    def set_thinking(self, enabled: bool):
        self._thinking_enabled = enabled
    
    def set_response_format(self, fmt: Literal["text","json"]):
        self._response_format_type = fmt

    def payload(self) -> Dict[str, Any]:
        """转换为API请求格式"""
        return {
            "model": self.model,
            "messages": self.messages,
            "request_id": self.request_id,
            "do_sample": self.do_sample,
            "stream": self.stream,
            #"thinking": self.thinking,  # 使用属性获取结构化数据 sdk不支持思考参数,使用会报错
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens,
            "tools": self.tools,
            "tool_choice": self.tool_choice,
            "user_id": self.user_id,
            "stop": self.stop,
            "response_format": self.response_format  # 使用属性获取结构化数据
        }
    def __str__(self) -> str:
        """返回对象的字符串表示，展示关键配置参数"""
        # 构建消息摘要
        msg_summary = f"包含{len(self.messages)}条消息"
        if self.messages:
            last_msg = self.messages[-1]
            if len(last_msg['content']) > 20:
                last_msg_content = last_msg['content'][:17] + "..."
            else:
                last_msg_content = last_msg['content']
            msg_summary += f" (最后: {last_msg['role']}:'{last_msg_content}')"
        
        # 构建工具摘要
        tool_summary = f"包含{len(self.tools)}个工具" if self.tools else "无工具"
        
        # 构建停止词摘要
        stop_summary = f"停止词: {self.stop[0]}" if self.stop and len(self.stop) > 0 else "无停止词"
        
        # 构建温度/采样策略摘要
        strategy = f"温度 {self.temperature:.2f} | 核采样 {self.top_p:.2f}"
        if not self.do_sample:
            strategy += " | 确定性输出"
        
        return (
            f"ZhipuChatParams(model={self.model})\n"
            f"├── 消息: {msg_summary}\n"
            f"├── 输出: {'流式' if self.stream else '一次性'} | 最大tokens: {self.max_tokens}\n"
            f"├── 策略: {strategy}\n"
            f"├── 工具: {tool_summary} | 选择方式: {self.tool_choice}\n"
            f"├── 格式: {self._response_format_type.upper()} | 思维链: {'启用' if self._thinking_enabled else '禁用'}\n"
            f"└── {stop_summary}"
        )