"""
将于数据操作对象结合,不断接收来自不用的Message的数据,将数据存储进入数据库,或者是取出特定的数据
这个类是数据操作对象与上下文管理器的桥接,上下文管理器不必直接和dao打交道
只需要向这个类索要和存储数据就足够了
通过单例模式可以让任何上下文管理器仅使用同一个数据操作对象,
"""
import threading
from typing import Dict, Any, List, Callable, Optional

class DataStorageManager:
    """统一的数据存储管理器"""
    
    _instance = None  # 单例实例
    _lock = threading.Lock()  # 线程安全锁
    
    def __new__(cls):
        """单例模式实现"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """初始化管理器状态"""
        self.storage_handlers: Dict[str, Callable] = {}

    def get_context_data(self,session:str,max_tokes:int):
        """
        通过session获取到该会话的原始信息和压缩信息数据的最后一次对话的id
        首先查找回话的system信息,
        然后按照一定比例加载一定的压缩信息,
        然后拼接一定数量的原始信息
        """
        raw = {"session":session,"service_type":"raw","start_id":1}
        com = {"session":session,"service_type":"compressed","start_id":1}
        pompmt=[]
        message = []
        return raw,com,pompmt,message
    
    def register_handler(self, data_type: str, handler: Callable[[Dict], None]):
        """注册特定类型数据的处理函数"""
        with self._lock:
            self.storage_handlers[data_type] = handler
    
    def store_data(self,session:str,data: Dict):
        """存储数据的主方法

        Args:
            session (str): 消息对象的会话id
            data (Dict): 包含全部信息的消息数据字典

        Returns:
            _type_: _description_
        """        
        print(f"桥接实例:{session}:{data}")
    
    def get_context_handler(self, session_id: str) -> Optional[Callable]:
        """获取特定会话的上下文处理函数（示例）"""
        # 在实际实现中，这里会返回处理该会话上下文的函数
        return lambda context: self.store_data({
            "type": "context",
            "session_id": session_id,
            "context": context
        })
    def get_all_provider_configs(self):
        """获取所有提供者的配置信息"""
        pass

    def save_session_tree(self,**kwargs):
        """存储会话树"""
        pass

    def get_session_tree(self,id):
        """根据根id获取整个会话树,如果是某个跟节点的子节点,加载完成后会自动切换到当前节点"""
        pass

    def get_session_news_id(self):
        """获取最新的session的id"""
        pass

    def save_message(self,**kwrage):
        """存储对话信息到数据库中"""
        print(kwrage)
        pass

    def load_message(self,session):
        """通过session根节点从数据库中获取所有信息"""
        pass