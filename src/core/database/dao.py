from contextlib import contextmanager
from .registry import OperatorRegistry
from .base import BaseTableOperator
from sqlite3 import Connection
from typing import Type, TypeVar, Union, Generic

# 定义泛型类型变量
T = TypeVar('T', bound='BaseTableOperator')
# ------ 模块数据访问对象 ------ 
class DAO(Generic[T]):
    def __init__(
        self, 
        conn: Connection, 
        allowed_tables: Union[str, list[str]]
    ):
        self._conn = conn
        self._allowed_tables = [allowed_tables] if isinstance(allowed_tables, str) else allowed_tables

    def __getattr__(self, table_name: str) -> T:
        if table_name not in self._allowed_tables:
            raise AttributeError(f"模块无权访问表 {table_name}")
            
        operator_cls = OperatorRegistry.get(table_name)
        if operator_cls is None:
            raise NameError("未注册的操作对象")
            
        return operator_cls(self._conn)  

    @contextmanager
    def transaction(self):
        """事务管理"""
        try:
            yield
            self._conn.commit()
        except:
            self._conn.rollback()
            raise