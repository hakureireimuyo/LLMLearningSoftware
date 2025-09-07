import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any
import threading

# 全局单例会话ID分配器
class GlobalSessionIDAllocator:
    """全局单例会话ID分配器 (线程安全)"""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._allocator_lock = threading.Lock()
                cls._instance.current_id = 1  # 默认起始ID
            return cls._instance

    def get_next_id(self) -> int:
        """获取下一个唯一ID (线程安全)"""
        with self._allocator_lock:
            new_id = self.current_id
            self.current_id += 1
            return new_id
    
    def set_start(self, new_start: int):
        """设置分配器的起始点 (线程安全)"""
        with self._allocator_lock:
            if new_start > self.current_id:
                self.current_id = new_start
            # 如果新起始值小于当前ID，保持当前值不变，避免ID冲突

class SessionNode:
    """会话节点类 - 表示树中的一个节点"""
    
    def __init__(self, 
                 session_id: int,  # 改为整数类型且必填
                 parent_id: Optional[int] = None,  # 改为可选整数类型
                 title: str = "新对话", 
                 create_time: datetime = datetime.now()):
        """
        初始化会话节点
        
        Args:
            session_id: 会话唯一ID (整数)
            parent_id: 父会话ID (整数或None)
            title: 会话标题
            create_time: 创建时间
        """
        self.session_id = session_id
        self.parent_id = parent_id
        self.title = title
        self.create_time = create_time
        self.children: List[SessionNode] = []
    
    def add_child(self, child: 'SessionNode'):
        """添加子节点"""
        child.parent_id = self.session_id
        self.children.append(child)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        return {
            "session_id": self.session_id,
            "parent_id": self.parent_id,
            "title": self.title,
            "create_time": self.create_time.isoformat(),
            "children": [child.to_dict() for child in self.children]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionNode':
        """从字典创建对象"""
        # 确保ID被正确转换为整数
        session_id = data['session_id']
        parent_id = data['parent_id']
        
        node = cls(
            session_id=session_id,
            parent_id=parent_id,
            title=data['title'],
            create_time=datetime.fromisoformat(data['create_time'])
        )
        
        # 递归创建子节点
        for child_data in data['children']:
            node.add_child(cls.from_dict(child_data))
            
        return node
    
    def __repr__(self) -> str:
        """简化表示"""
        return f"SessionNode({self.title}, id={self.session_id})"


class SessionTree:
    """会话树管理器 - 负责树结构的操作和状态管理"""
    
    def __init__(self,allocator:GlobalSessionIDAllocator):
        """可以接收根节点"""
        # 创建ID分配器并设置初始值
        self.id_allocator = allocator

        root_id = self.id_allocator.get_next_id()
        self.root = SessionNode(session_id=root_id, title="root")
            
        self.current_node: SessionNode = self.root
        self._node_map: Dict[int, SessionNode] = {}  # 键改为整数
        self._index_tree(self.root)
    
    def _index_tree(self, node: SessionNode):
        """递归索引树结构"""
        self._node_map[node.session_id] = node
        for child in node.children:
            self._index_tree(child)
    
    def _find_max_id(self, node: SessionNode) -> int:
        """递归查找树中最大ID"""
        max_id = node.session_id
        for child in node.children:
            child_max = self._find_max_id(child)
            if child_max > max_id:
                max_id = child_max
        return max_id
    
    def set_allocator_start(self, new_start: int):
        """设置ID分配器的起始点"""
        self.id_allocator.set_start(new_start)
    
    def create_child_branch(self, title: str = "新分支") -> SessionNode:
        """在当前节点下创建子分支"""
        # 使用分配器获取新ID
        new_id = self.id_allocator.get_next_id()
        child = SessionNode(session_id=new_id, title=title)
        self.current_node.add_child(child)
        self._index_tree(child)
        return child
    
    def switch_to_node(self, session_id: int) -> bool:  # 参数类型改为整数
        """切换到指定节点"""
        if session_id in self._node_map:
            self.current_node = self._node_map[session_id]
            return True
        return False
    
    def back_to_parent(self) -> bool:
        """返回到父节点"""
        if (self.current_node.parent_id is not None and 
            self.current_node.parent_id in self._node_map):
            self.current_node = self._node_map[self.current_node.parent_id]
            return True
        return False
    
    def back_to_root(self) -> bool:
        """返回到根节点"""
        self.current_node = self.root
        return True
    
    def get_node_path(self) -> List[SessionNode]:
        """获取从根节点到当前节点的路径"""
        path = []
        node = self.current_node
        
        while node:
            path.insert(0, node)
            if node.parent_id is not None and node.parent_id in self._node_map:
                node = self._node_map[node.parent_id]
            else:
                node = None
        
        return path
    
    def get_current_branch(self) -> List[SessionNode]:
        """获取当前分支的所有节点（当前节点的子节点）"""
        return self.current_node.children
    
    def _tree_to_string(self, node: SessionNode, prefix: str = "", is_last: bool = True) -> str:
        """递归生成树状结构字符串"""
        is_current = node.session_id == self.current_node.session_id
        current_marker = " [当前]" if is_current else ""
        
        # 当前节点表示
        result = prefix
        if is_last:
            result += "└── "
            new_prefix = prefix + "    "
        else:
            result += "├── "
            new_prefix = prefix + "│   "
        
        result += f"{node.title}{current_marker} [{node.session_id}]\n"
        
        # 子节点处理
        child_count = len(node.children)
        for i, child in enumerate(node.children):
            is_child_last = (i == child_count - 1)
            result += self._tree_to_string(child, new_prefix, is_child_last)
        
        return result

    def to_tree_string(self) -> str:
        """将树结构转换为可视化字符串"""
        # 根节点特殊处理
        is_current = self.root.session_id == self.current_node.session_id
        current_marker = " [当前]" if is_current else ""
        result = f"{self.root.title}{current_marker} [{self.root.session_id}]\n"
        
        # 递归处理子节点
        child_count = len(self.root.children)
        for i, child in enumerate(self.root.children):
            is_last = (i == child_count - 1)
            result += self._tree_to_string(child, "", is_last)
        
        return result.rstrip()  # 移除最后的换行符
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        return self.root.to_dict()
    
    def load_from_dict(self, data: Dict[str, Any]):
        """从字典加载树结构"""
        self.root = SessionNode.from_dict(data)
        self.current_node = self.root
        self._node_map = {}
        self._index_tree(self.root)
        # 更新分配器到最大ID+1
    
    def get_node(self, session_id: int) -> Optional[SessionNode]:  # 参数类型改为整数
        """获取指定节点"""
        return self._node_map.get(session_id)