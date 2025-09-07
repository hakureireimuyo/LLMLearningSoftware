"""
记录作文和对应的批改情况
"""
from .base import BaseTableOperator
from .registry import OperatorRegistry
from typing import Union

@OperatorRegistry.register('conposition')
class Conposition(BaseTableOperator):
    def __init__(self, conn):
        super().__init__(conn, 'conposition')
        
    def get_table_definition(self):
        table="""
        """
        return table

    # ================= 基础CRUD方法 =================
    
    def add_guide(
        self,
        user_id: int,
        title: str,
        content: str
    ) -> int:
        """
        添加新的写作指南
        返回插入的rowid
        """
        data = {
            'user_id': user_id,
            'title': title,
            'content': content
        }
        return self.insert(data)

    def get_guide_by_id(self, guide_id: int) -> Optional[Dict]:
        """
        通过ID获取单个写作指南
        返回字典或None
        """
        result = self.select(
            where_clause="id=?",
            where_params=(guide_id,)
        )
        return result[0] if result else None

    def update_guide(
        self,
        guide_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None
    ) -> int:
        """
        更新写作指南
        返回受影响的行数
        """
        update_data = {
            'title': title,
            'content': content
        }
        # 移除值为None的键
        update_data = {k: v for k, v in update_data.items() if v is not None}
        return self.update(
            where_clause="id=?",
            where_params=(guide_id,),
            update_data=update_data
        )

    def delete_guide(self, guide_id: int) -> int:
        """
        删除写作指南
        返回受影响的行数
        """
        return self.delete(
            where_clause="id=?",
            where_params=(guide_id,)
        )

    # ================= 特定查询方法 =================
    
    def get_guides_by_user(
        self,
        user_id: int,
        order_by_date: bool = True,
        descending: bool = True
    ) -> List[Dict]:
        """
        获取用户的所有写作指南
        参数:
            user_id: 用户ID
            order_by_date: 是否按日期排序
            descending: 是否降序排列(最新的在前)
        返回列表
        """
        order_clause = ""
        if order_by_date:
            order_clause = "ORDER BY create_date"
            if descending:
                order_clause += " DESC"
            else:
                order_clause += " ASC"
                
        return self.select(
            where_clause="user_id=?",
            where_params=(user_id,),
            order_by=order_clause.strip() if order_clause else None
        )

    def get_recent_guides(
        self,
        user_id: int,
        limit: int = 5
    ) -> List[Dict]:
        """
        获取用户最近修改的写作指南
        参数:
            user_id: 用户ID
            limit: 返回数量限制
        返回列表
        """
        sql = f"""
        SELECT * FROM {self._table_name} 
        WHERE user_id=? 
        ORDER BY last_modified DESC 
        LIMIT ?
        """
        cursor = self._execute(sql, (user_id, limit))
        return [dict(row) for row in cursor.fetchall()]

    # ================= 完整数据操作方法 =================
    
    def get_full_guide_data(self, guide_id: int) -> Optional[Dict]:
        """
        通过ID获取写作指南的全部数据
        返回包含所有字段的字典或None
        """
        return self.get_guide_by_id(guide_id)