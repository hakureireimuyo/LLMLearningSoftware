"""
对ai上下文进行存储管理的类
"""
from .base import BaseTableOperator
from .registry import OperatorRegistry
from datetime import datetime
from typing import Union,Optional,List

@OperatorRegistry.register('context')
class Context(BaseTableOperator):
    def __init__(self, conn):
        super().__init__(conn, 'context')

    def get_table_definition(self) -> str:
        table = '''
                CREATE TABLE IF NOT EXISTS context (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    scenario_id INTEGER,
                    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    content TEXT NOT NULL,
                    translation_cache TEXT,
                    role TEXT CHECK(role IN ('user', 'ai')),
                    audio_id INTEGER,
                    evaluation_id INTEGER,
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    FOREIGN KEY(scenario_id) REFERENCES scenarios(id),
                    FOREIGN KEY(audio_id) REFERENCES audio_cache(id),
                    FOREIGN KEY(evaluation_id) REFERENCES speech_evaluations(id)
                )'''
        return table
    
    def add_chat_record(
        self,
        user_id: int,
        content: str,
        role: str,
        scenario_id: Optional[int] = None,
        translation_cache: Optional[str] = None,
        audio_id: Optional[int] = None,
        evaluation_id: Optional[int] = None
    ) -> int:
        """
        添加新的聊天记录
        返回插入的rowid
        """
        data = {
            'user_id': user_id,
            'scenario_id': scenario_id,
            'content': content,
            'translation_cache': translation_cache,
            'role': role,
            'audio_id': audio_id,
            'evaluation_id': evaluation_id
        }
        # 移除值为None的键
        data = {k: v for k, v in data.items() if v is not None}
        return self.insert(data)

    def get_record_by_id(self, record_id: int) -> Optional[dict]:
        """
        通过ID获取单条聊天记录
        返回字典或None
        """
        result = self.select(
            where_clause="id=?",
            where_params=(record_id,)
        )
        return result[0] if result else None

    def update_record_by_id(
        self,
        record_id: int,
        content: Optional[str] = None,
        translation_cache: Optional[str] = None,
        audio_id: Optional[int] = None,
        evaluation_id: Optional[int] = None
    ) -> int:
        """
        通过ID更新聊天记录
        返回受影响的行数
        """
        update_data = {
            'content': content,
            'translation_cache': translation_cache,
            'audio_id': audio_id,
            'evaluation_id': evaluation_id
        }
        # 移除值为None的键
        update_data = {k: v for k, v in update_data.items() if v is not None}
        return self.update(
            where_clause="id=?",
            where_params=(record_id,),
            update_data=update_data
        )

    def delete_record_by_id(self, record_id: int) -> int:
        """
        通过ID删除聊天记录
        返回受影响的行数
        """
        return self.delete(
            where_clause="id=?",
            where_params=(record_id,)
        )

    # ================= 特定查询方法 =================
    
    def get_records_by_user(
        self,
        user_id: int,
        scenario_id: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[dict]:
        """
        获取用户的所有聊天记录（可指定场景）
        返回列表
        """
        where_clause = "user_id=?"
        where_params = (user_id,)
        
        if scenario_id is not None:
            where_clause += " AND scenario_id=?"
            where_params += (scenario_id,)
            
        sql = f"SELECT * FROM {self._table_name} WHERE {where_clause} ORDER BY create_time DESC"
        
        if limit is not None:
            sql += f" LIMIT {limit}"
            if offset is not None:
                sql += f" OFFSET {offset}"
                
        cursor = self._execute(sql, where_params)
        return [dict(row) for row in cursor.fetchall()]

    def get_records_by_time_range(
        self,
        user_id: int,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        scenario_id: Optional[int] = None,
        role: Optional[str] = None
    ) -> List[dict]:
        """
        获取指定时间范围内的聊天记录
        返回列表
        """
        # 转换日期格式
        if isinstance(start_date, datetime):
            start_date = start_date.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(end_date, datetime):
            end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')
            
        where_clause = "user_id=? AND create_time BETWEEN ? AND ?"
        where_params = (user_id, start_date, end_date)
        
        if scenario_id is not None:
            where_clause += " AND scenario_id=?"
            where_params += (scenario_id,)
            
        if role is not None:
            where_clause += " AND role=?"
            where_params += (role,)
            
        return self.select(
            where_clause=where_clause,
            where_params=where_params,
            order_by="create_time ASC"  # 按时间升序排列
        )

    def delete_records_by_user(
        self,
        user_id: int,
        scenario_id: Optional[int] = None
    ) -> int:
        """
        删除用户的所有聊天记录（可指定场景）
        返回受影响的行数
        """
        where_clause = "user_id=?"
        where_params = (user_id,)
        
        if scenario_id is not None:
            where_clause += " AND scenario_id=?"
            where_params += (scenario_id,)
            
        return self.delete(
            where_clause=where_clause,
            where_params=where_params
        )

    # ================= 特定字段操作方法 =================
    
    def update_audio_id(self, record_id: int, audio_id: Optional[int]) -> int:
        """
        更新聊天记录的audio_id
        返回受影响的行数
        """
        return self.update(
            where_clause="id=?",
            where_params=(record_id,),
            update_data={'audio_id': audio_id}
        )

    def update_evaluation_id(self, record_id: int, evaluation_id: Optional[int]) -> int:
        """
        更新聊天记录的evaluation_id
        返回受影响的行数
        """
        return self.update(
            where_clause="id=?",
            where_params=(record_id,),
            update_data={'evaluation_id': evaluation_id}
        )

    def get_translation_cache(self, record_id: int) -> Optional[str]:
        """
        获取聊天记录的翻译缓存
        返回字符串或None
        """
        record = self.get_record_by_id(record_id)
        return record.get('translation_cache') if record else None

    def update_translation_cache(self, record_id: int, translation_cache: Optional[str]) -> int:
        """
        更新聊天记录的翻译缓存
        返回受影响的行数
        """
        return self.update(
            where_clause="id=?",
            where_params=(record_id,),
            update_data={'translation_cache': translation_cache}
        )