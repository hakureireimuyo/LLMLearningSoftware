import sqlite3
from dataclasses import dataclass,fields
from typing import List, Optional, Dict
from datetime import datetime

@dataclass(frozen=True)
class Word:
    """单词数据类"""
    id: int
    word: str
    pronunciation: Optional[str]
    translation: Optional[str]

    def __str__(self):
        return f"{self.word} {self.pronunciation or ''} - {self.translation or ''}"

    @classmethod
    def from_row(cls, row: sqlite3.Row):
        """从数据库行创建Word实例"""
        return cls(
            id=row['id'],
            word=row['word'],
            pronunciation=row['pronunciation'],
            translation=row['translation']
        )
    def get(self, key, default=None):
        """类似字典的get方法，根据字段名获取值"""
        # 获取所有数据类字段的名称
        field_names = {field.name for field in fields(self)}
        if key in field_names:
            return getattr(self, key)
        return default
@dataclass
class WordListStat:
    """单词表统计信息类"""
    table_name: str
    word_count: int
    last_updated: datetime

    def to_dict(self):
        return {
            "table_name": self.table_name,
            "word_count": self.word_count,
            "last_updated": self.last_updated.isoformat()
        }

class WordDatabase:
    """SQLite单词数据库管理类"""
    
    def __init__(self, db_path: str):
        """
        初始化数据库连接
        :param db_path: 数据库文件路径
        """
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # 使查询结果支持字典访问
        self.cursor = self.conn.cursor()
        self.tables = ['zk','gk','cet4','cet4lx','cet6lx', 'cet6', 'toefl', 'gre']
        self._valid_fields = ['id', 'word', 'pronunciation', 'translation']

    def _init_tables(self):
        """初始化数据库表结构"""
        for table in self.tables:
            self.cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT NOT NULL UNIQUE,
                    pronunciation TEXT,
                    translation TEXT
                )
            """)
        # 创建统计表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS wordlist_stats (
                table_name TEXT PRIMARY KEY,
                word_count INTEGER DEFAULT 0,
                last_updated DATETIME
            )
        """)
        self.conn.commit()

    def get_available_tables(self) -> List[str]:
        """获取所有单词表名称"""
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [row['name'] for row in self.cursor.fetchall()]
    
    def update_word_counts(self):
        """更新所有单词表的统计信息"""
        for table in self.tables:
            count=self.get_table_size(table)
            update_time = datetime.now()
            
            self.cursor.execute("""
                INSERT OR REPLACE INTO wordlist_stats 
                (table_name, word_count, last_updated)
                VALUES (?, ?, ?)
            """, (table, count, update_time))
        self.conn.commit()

    def get_word_count(self, table: str) -> int:
        """获取指定表的单词数量"""
        self._validate_table(table)
        self.cursor.execute(f"""
            SELECT COUNT(*) FROM {table}
        """)
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def get_all_stats(self) -> Dict[str, WordListStat]:
        """获取所有统计信息"""
        self.cursor.execute("SELECT * FROM wordlist_stats")
        return {
            row["table_name"]: WordListStat(
                table_name=row["table_name"],
                word_count=row["word_count"],
                last_updated=datetime.fromisoformat(row["last_updated"])
            )
            for row in self.cursor.fetchall()
        }
    
    def batch_query(
        self,
        table_name: str,
        start_id: int = 1,
        count: int = 10
    ) -> List[Word]:
        """批量顺序查询完整单词数据"""
        self._validate_table(table_name)
        query = f"""
            SELECT * FROM {table_name}
            WHERE id >= ?
            ORDER BY id
            LIMIT ?
        """
        self.cursor.execute(query, (start_id, count))
        return [Word.from_row(row) for row in self.cursor.fetchall()]

    def random_query(
        self,
        table_name: str,
        count: int = 10
    ) -> List[Word]:
        """随机查询完整单词数据"""
        self._validate_table(table_name)
        query = f"""
            SELECT * FROM {table_name}
            ORDER BY RANDOM()
            LIMIT ?
        """
        self.cursor.execute(query, (count,))
        return [Word.from_row(row) for row in self.cursor.fetchall()]

    def _validate_table(self, table_name: str):
        """验证表名有效性"""
        if table_name not in self.tables:
            raise ValueError(f"无效表名：{table_name}")

    def get_table_size(self, table_name: str) -> int:
        """获取表记录总数"""
        self._validate_table(table_name)
        self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        return self.cursor.fetchone()[0]

    def close(self):
        """关闭数据库连接"""
        self.conn.close()

    def _validate_table(self, table_name: str):
        """验证表是否存在"""
        self.cursor.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        if not self.cursor.fetchone():
            raise ValueError(f"表 {table_name} 不存在")
        

if __name__ == "__main__":
    db = WordDatabase('src\\core\\kivymd_component\\word_recitation\\database\\words.db')
    db._init_tables()  # 初始化表结构
    # print(db.get_available_tables())  # 输出所有表名
    # #测试随机读取
    # print(db.random_query('cet4lx', 10))  # 随机获取10条单词
    # #测试顺序读取
    # print(db.batch_query('cet4lx', 1, 10))  # 顺序获取10条单词
    # #测试表大小
    # print(db.get_table_size('cet4lx'))  # 获取cet4lx表大小
    #测试更新
    db.update_word_counts()  # 更新所有表的统计信息
    #测试单词数量
    #print(db.get_word_count('cet4lx'))  # 获取cet4lx表单词数量
    #测试统计信息
    print(db.get_all_stats())  # 获取所有统计信息
    db.close()  # 关闭数据库连接
