from sqlite3 import Connection
from typing import Union
from .base import BaseTableOperator
from .registry import OperatorRegistry

@OperatorRegistry.register('stats')
class StatsOperator(BaseTableOperator):
    def __init__(self, conn:Connection):
        super().__init__(conn, 'stats')

    def get_table_definition(self) -> str:
        table = '''CREATE TABLE IF NOT EXISTS word_stats (
                    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                    "word_id" INTEGER NOT NULL UNIQUE,
                    "word" TEXT NOT NULL,
                    "translate_count" INTEGER DEFAULT 0,
                    "use_count" INTEGER DEFAULT 0,
                    "listen_count" INTEGER DEFAULT 0,
                    "see_count" INTEGER DEFAULT 0,
                    "correct_count" INTEGER DEFAULT 0,
                    "wrong_count" INTEGER DEFAULT 0
                )'''
        return table
    
    def increment_stat(self, word_id: int, stat_field: str, increment: int = 1) -> int:
        """
        原子操作增加统计计数（支持新增的correct_count/wrong_count）
        """
        valid_fields = {
            'translate_count', 'use_count', 'listen_count', 
            'see_count', 'correct_count', 'wrong_count'
        }
        if stat_field not in valid_fields:
            raise ValueError(f"无效统计字段: {stat_field}")

        update_data = {stat_field: increment}
        return self.update(
            where_clause="word_id=?",
            where_params=(word_id,),
            update_data=update_data,
            incremental=True
        )

    def get_word_stats(self, word_id: int) -> dict:
        """
        获取单词完整统计数据
        返回格式：{
            'translate_count': int,
            'use_count': int,
            'listen_count': int,
            'see_count': int,
            'correct_count': int,
            'wrong_count': int
        }
        """
        result = self.select(
            columns="translate_count,use_count,listen_count,see_count,correct_count,wrong_count",
            where_clause="word_id=?",
            where_params=(word_id,)
        )
        return result[0] if result else self._default_stats()

    def upsert_word(self, word_id: int, word: str) -> int:
        """
        插入或更新单词记录（原子操作）
        返回操作后的rowid
        """
        data = {
            'word_id': word_id,
            'word': word
        }
        try:
            return self.insert(data)
        except sqlite3.IntegrityError:
            # 已存在则更新word字段
            self.update(
                where_clause="word_id=?",
                where_params=(word_id,),
                update_data={'word': word}
            )
            return word_id
        # ================= 批量操作方法 =================
    
    def bulk_increment_stats(self, increments: List[Tuple[int, str, int]]) -> int:
        """
        批量增加统计计数（高性能版本）
        参数格式：[(word_id, stat_field, increment), ...]
        返回成功更新的记录数
        """
        # 按字段分组处理
        field_groups = defaultdict(list)
        for word_id, field, inc in increments:
            if field in {'correct_count', 'wrong_count'}:
                field_groups[field].append((word_id, inc))

        total = 0
        for field, data in field_groups.items():
            sql = f"""
                UPDATE {self.table_name} 
                SET {field} = {field} + ?
                WHERE word_id = ?
            """
            params = [(inc, wid) for wid, inc in data]
            total += self._execute_many(sql, params)
        return total
    # ================= 辅助方法 =================
    
    def _default_stats(self) -> dict:
        """返回默认统计字典"""
        return {
            'translate_count': 0,
            'use_count': 0,
            'listen_count': 0,
            'see_count': 0,
            'correct_count': 0,
            'wrong_count': 0
        }

    def _execute_many(self, sql: str, params_list: list) -> int:
        """执行批量SQL"""
        try:
            cursor = self.conn.cursor()
            cursor.executemany(sql, params_list)
            return cursor.rowcount
        except sqlite3.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"批量操作失败: {str(e)}")
        