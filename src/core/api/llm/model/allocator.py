from typing import Dict,Union

class MessageIDAllocator:
    """
    消息ID分配器，支持为不同类型的消息分配唯一ID

    每个会话每种服务类型只能创建一个实例,否则会造成数据冲突
    """
    
    def __init__(
        self, 
        session: str, 
        service_type: str, 
        start_id: int = 1
    ):
        """
        初始化消息ID分配器
        
        Args:
            session: 会话唯一标识符
            service_type: 服务类型（如 'raw', 'compressed'）
            start_id: 起始ID（默认为1）
        """
        self.session:str = session
        self.service_type:str = service_type
        self.current_id:int = start_id
    
    def get_next_id(self) -> int:
        """获取下一个唯一ID"""
        new_id = self.current_id
        self.current_id += 1
        return new_id
    
    def __call__(self) -> int:
        """使分配器可调用，直接返回新ID"""
        return self.get_next_id()
    
    def reset(self, new_start: int = 1):
        """重置分配器"""
        self.current_id = new_start
    
    def get_current_state(self) -> Dict[str, Union[str, int]]:
        """获取当前状态（用于持久化）"""
        return {
            "session": self.session,
            "service_type": self.service_type,
            "current_id": self.current_id
        }

    def load_data(self,
                session: str, 
                service_type: str, 
                start_id: int = 1):
        """
        重新分配数据
        
        Args:
            session: 会话唯一标识符
            service_type: 服务类型（如 'raw', 'compressed'）
            start_id: 起始ID（默认为1）
        """
        self.session:str = session
        self.service_type:str = service_type
        self.current_id:int = start_id