import sqlite3
from typing import Optional
import os
from .dao import DAO
from .registry import OperatorRegistry
# ================= 数据库管理器 =================
class DB:
    def __init__(self, database_path: str):
        """
        初始化数据库管理器
        
        Args:
            database_path: SQLite 数据库文件路径
        """
        # 确保单例模式只初始化一次
        if hasattr(self, '_database_path'):
            return
            
        self._database_path = database_path
        self._conn: Optional[sqlite3.Connection] = None
        
        # 检查并创建数据库文件
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """确保数据库文件存在，不存在则创建空数据库"""
        # 检查数据库文件是否存在
        if not os.path.exists(self._database_path):
            # 创建目录路径（如果需要）
            db_dir = os.path.dirname(self._database_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            
            print(f"创建新的数据库文件: {self._database_path}")
            
            # 创建空数据库文件
            with open(self._database_path, 'w') as f:
                pass  # 只需创建空文件
            
            # 建立连接以确保数据库有效
            self._create_connection()
            
    
    def _create_connection(self):
        """创建数据库连接并设置 row_factory"""
        self._conn = sqlite3.connect(self._database_path)
        self._conn.row_factory = sqlite3.Row
        # 启用外键支持
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.close()
        self._conn = None

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self._database_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def get_all_dao(self) -> DAO:
        return DAO(self.conn, OperatorRegistry.list_registered_tables())
    
    def get_dao(self,table_name) -> DAO:
        return DAO(self.conn, table_name)
    
    def close(self):
        if self._conn:
            self._conn.close()



    