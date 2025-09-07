from typing import Any,Dict
from .session import SessionNode,SessionTree
from ..bridge import DataStorageManager
from ..api.llm import LLMCombo
from ..api.llm.model import Message
from ..api.llm import ProviderGroup
from .session import GlobalSessionIDAllocator
class ConversationManager:
    """
    对话管理器 - 负责高层业务逻辑和组件集成
    主要负责将对话树和实际的对话信息进行关联,
    实现数据的双向存储
    管理Message中信息的传递方向
    """
    
    def __init__(self):
        # 与数据库的桥梁
        self.storage = DataStorageManager()

        # 初始化包含了所有提供者的信息和实例
        provider_data = self.storage.get_all_provider_configs()
        self.group = ProviderGroup()
        self.group.load_from_data(providers_data=provider_data)

        # 初始化并设置combo的实际使用者
        self.llm_combo = LLMCombo()
        provider = self.group.create_provider('zhipu')
        self.llm_combo.load_provider(provider)
        
        # 给流式调用添加存入数据库方法回调
        self.llm_combo.add_callback(self.storage.save_message)

        # 创建session的分配器
        self.allocator = GlobalSessionIDAllocator()

        # 读取最新的sessionid
        _id = self.storage.get_session_news_id()

        # 设置分配器的起点
        self.allocator.set_start(_id)

        # 对话树的实例化在分配器之前
        self.tree = SessionTree(self.allocator)

        # 每个节点关联的消息上下文 {session_id: Message}
        self.message_contexts: Dict[SessionNode, Message] = {}
    
    def initialize_new_tree(self, title: str = "主对话") -> SessionNode:
        """初始化全新的对话树"""
        self.tree = SessionTree(root=SessionNode(title=title))
        self._create_message_for_node(self.tree.root)
        self.storage.save_session_tree(self.tree.to_dict())
        return self.tree.root
    
    def load_tree(self, tree_id: str) -> bool:
        """从数据库加载对话树"""
        tree_data = self.storage.get_session_tree(tree_id)
        if not tree_data:
            return False
        
        self.tree.load_from_dict(tree_data)
        
        # 确保所有节点都有消息上下文
        for session_id in self.tree._node_map:
            if session_id not in self.message_contexts:
                self._create_message_for_node(self.tree._node_map[session_id])
        
        # 设置当前节点的上下文
        self._set_current_context()
        return True
    
    def create_child_branch(self, title: str = "新分支") -> SessionNode:
        """创建新的子分支"""
        child = self.tree.create_child_branch(title)
        self._create_message_for_node(child)
        self.storage.save_session_tree(self.tree.to_dict())
        return child
    
    def switch_to_branch(self, session_id: str) -> bool:
        """切换到指定分支"""
        if self.tree.switch_to_node(session_id):
            self._set_current_context()
            return True
        return False
    
    def back_to_parent(self) -> bool:
        """返回到父节点"""
        if self.tree.back_to_parent():
            self._set_current_context()
            return True
        return False
    
    def back_to_root(self) -> bool:
        """返回到根节点"""
        if self.tree.back_to_root():
            self._set_current_context()
            return True
        return False
    
    def chat(self,content: str):
        """发送消息并记录到当前会话"""
        role: str = "user", 
        # 获取当前节点的消息上下文
        current_context = self.message_contexts[self.tree.current_node.session_id]
        
        # 添加到消息历史
        current_context.add_message(role, content)
        
        # 存储到数据库
        self.storage.save_message(role,content)
        # 调用LLM
        response = self.llm_combo.chat()
        
        # 添加AI响应
        current_context.add_message("assistant", response)
        # 存储到数据库
        self.storage.save_message("assistant",response)

        return response
    
    def stream(self,content:str):
        """流式调用,通过回调自动存入数据库

        Args:
            content (str): 输入内容

        Returns:
            _type_: 是否成功运行
        """        

        role: str = "user", 
        # 获取当前节点的消息上下文
        current_context = self.message_contexts[self.tree.current_node.session_id]
        
        # 添加到消息历史
        current_context.add_message(role, content)
        
        # 存储到数据库
        self.storage.save_message(role,content)
        # 调用LLM
        response = self.llm_combo.stream()

        return response
    
    def get_tree_structure(self) -> str:
        """获取树结构的可视化表示"""
        return self.tree.to_tree_string()
    
    def _create_message_for_node(self, node: SessionNode):
        """为节点创建消息上下文"""
        # 这里使用之前设计的Message类
        self.message_contexts[node.session_id] = Message(
            session=node.session_id
        )
    
    def _set_current_context(self):
        """设置当前节点的上下文到LLMCombo"""
        session_id = self.tree.current_node.session_id
        if session_id in self.message_contexts:
            self.llm_combo.set_message(self.message_contexts[session_id])
    
    def save_current_state(self):
        """保存当前状态到数据库"""
        # 保存树结构
        self.storage.save_session_tree(self.tree.to_dict())
        
        # 保存所有消息上下文
        for session_id, message in self.message_contexts.items():
            self.storage.save_message_context(session_id, message)