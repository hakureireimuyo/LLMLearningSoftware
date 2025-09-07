from typing import Union,Dict, Type, TypeVar, Generic, Any,Callable
from .base import BaseTableOperator

# 定义操作类基类型
T = TypeVar('T', bound=BaseTableOperator)

class OperatorRegistry:
    """表操作类的单例注册中心
    
    通过单例模式确保全局只有一个注册表实例，管理所有表操作类的映射关系。
    使用类装饰器注册自定义表操作类，提供统一的访问接口。
    
    Attributes:
        _instance (OperatorRegistry): 单例实例
        _registry (dict): 表名到操作类的映射字典
    """
    
    _instance = None
    _registry: Dict[str, Type[Any]] = {}  # 显式声明类型
    
    def __new__(cls):
        """单例模式实现：确保全局只有一个注册表实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._registry = {}  # 初始化注册表
        return cls._instance
    
    @classmethod
    def register(cls, table_name: str) -> Callable[..., type[BaseTableOperator]]:
        """装饰器方法：注册表操作类到注册中心
        
        Args:
            table_name (str): 目标表名称（如'users'）
            
        Returns:
            function: 类装饰器
            
        Example:
            @OperatorRegistry.register('users')
            class UserOperator(BaseTableOperator):
                ...
        """
        def decorator(operator_cls: Type[T]) -> Type[T]:
            cls._registry[table_name] = operator_cls
            return operator_cls
        return decorator
        
    @classmethod
    def get(cls, table_name) -> Union[Any,None]:
        """获取表对应的操作类
        
        Args:
            table_name (str): 目标表名称
            
        Returns:
            type: 注册的表操作类，未注册时返回None
            
        Raises:
            KeyError: 表名未注册时抛出（可选）
        """
        return cls._registry.get(table_name, None)

    @classmethod
    def clear(cls):
        """清空注册表（主要用于测试环境）"""
        cls._registry = {}

    @classmethod
    def list_registered_tables(cls):
        """返回所有已注册表名"""
        return list(cls._registry.keys())