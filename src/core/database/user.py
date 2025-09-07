
from sqlite3 import Connection
from typing import Union
from .base import BaseTableOperator
from .registry import OperatorRegistry

@OperatorRegistry.register('user')
class UserOperator(BaseTableOperator):
    def __init__(self, conn: Connection):
        super().__init__(conn, 'user')

    def get_table_definition(self):
        table='''
                CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                avatar_path TEXT,
                username TEXT UNIQUE NOT NULL,
                registration_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_usage_time INTEGER DEFAULT 0,
                total_listening INTEGER DEFAULT 0,
                total_translation INTEGER DEFAULT 0,
                total_reading INTEGER DEFAULT 0,
                total_writing INTEGER DEFAULT 0,
                total_api_calls INTEGER DEFAULT 0,
                total_output_tokens INTEGER DEFAULT 0
            )'''
        return table
    
    def get_by_username(self, username: str) -> Union[dict, None]:
        """根据用户名获取用户信息"""
        result = self.select(where_clause="username=?", where_params=(username,))
        return result[0] if result else None

    # ================= 统计累加方法 =================
    def _atomic_increment(self, field: str, value: int, user_id: int = 0) -> bool:
        """原子操作累加字段值"""
        if value <= 0:
            raise ValueError("增量值必须大于0")
        if user_id is None:
            raise ValueError("必须提供有效的用户ID")
        
        sql = f"""
            UPDATE {self._table_name} 
            SET {field} = {field} + ? 
            WHERE id = ?
        """
        cursor = self._execute(sql, (value, user_id))
        return cursor.rowcount > 0

    def add_usage_time(self, seconds: int, user_id: int = 0) -> bool:
        """累计使用时长（秒）"""
        return self._atomic_increment('total_usage_time', seconds, user_id)

    def add_api_calls(self, count: int, user_id: int = 0) -> bool:
        """累计API调用次数"""
        return self._atomic_increment('total_api_calls', count, user_id)

    def add_listening(self, count: int, user_id: int = 0) -> bool:
        """累计听力练习次数"""
        return self._atomic_increment('total_listening', count, user_id)

    def add_translation(self, count: int, user_id: int = 0) -> bool:
        """累计翻译练习次数"""
        return self._atomic_increment('total_translation', count, user_id)

    def add_writing(self, count: int, user_id: int = 0) -> bool:
        """累计写作练习次数"""
        return self._atomic_increment('total_writing', count, user_id)

    def add_reading(self, count: int, user_id: int = 0) -> bool:
        """累计阅读练习次数"""
        return self._atomic_increment('total_reading', count, user_id)

    def add_output_tokens(self, tokens: int, user_id: int = 0) -> bool:
        """累计输出token数量"""
        return self._atomic_increment('total_output_tokens', tokens, user_id)

    # ================= 头像管理 =================
    def update_avatar(self, avatar_path: str, user_id: int = 0) -> bool:
        """
        更新头像路径（仅校验路径格式）
        :param avatar_path: 符合格式要求的路径字符串（无需真实存在）
        :return: 是否更新成功
        """
        if user_id is None:
            raise ValueError("必须提供有效的用户ID")

        updated = self.update(
            where_clause="id=?", 
            where_params=(user_id,),
            update_data={"avatar_path": avatar_path}
        )
        return updated > 0

    # ================= 综合统计 =================
    def get_statistics(self, user_id: int = 0) -> dict:
        """获取用户完整统计信息"""
        if user_id is None:
            raise ValueError("必须提供有效的用户ID")
            
        user = self.select(
            columns="total_usage_time, total_listening, total_translation, "
                    "total_reading, total_writing, total_api_calls, total_output_tokens",
            where_clause="id=?",
            where_params=(user_id,)
        )
        return user[0] if user else {}
    def current_user_all_data(self,user_id=0):
        """获取当前用户的所有数据"""
        return self.select(where_clause="id=?",where_params=(user_id,))[0] if user_id else {}
