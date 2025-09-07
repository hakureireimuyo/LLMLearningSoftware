
from datetime import datetime
from typing import List, Optional, Dict, Union
import sqlite3
from .registry import OperatorRegistry
from .base import BaseTableOperator

@OperatorRegistry.register('plan')
class StudyPlanOperator(BaseTableOperator):
    def __init__(self, conn):
        super().__init__(conn, 'plan')

    def get_table_definition(self) -> str:
        table='''
                CREATE TABLE IF NOT EXISTS plan (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word_count INTEGER NOT NULL,
                    wordlist_name TEXT NOT NULL,
                    created_time TEXT DEFAULT (datetime('now', 'localtime')),
                    current_index INTEGER DEFAULT 0,
                    completed_time TEXT,
                    user_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 10,
                    is_current INTEGER NOT NULL DEFAULT 0 CHECK(is_current IN (0, 1)), 
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    UNIQUE (wordlist_name, user_id)
                );'''
        return table
    
    def create_study_plan(
        self,
        word_count: int,
        wordlist_name: str,
        is_current: int = 0,
        user_id: int = 0
    ) -> int:
        """
        创建新的学习计划
        参数:
            user_id: 用户ID
            word_count: 单词数量
            wordlist_name: 单词列表名称
            is_current: 是否设为当前计划(0/1)
        返回插入的rowid
        """
        # 如果设置为当前计划,先取消其他当前计划
        try:
            if is_current == 1:
                self._clear_current_plan(user_id)
                
            data = {
                'user_id': user_id,
                'word_count': word_count,
                'wordlist_name': wordlist_name,
                'is_current': is_current
            }
            return self.insert(data)
        except sqlite3.IntegrityError as e:
            # 处理唯一约束冲突
            if "UNIQUE constraint failed" in str(e):
                # 获取已存在的计划ID
                existing = self.select(
                    where_clause="wordlist_name=? AND user_id=?",
                    where_params=(wordlist_name, user_id),
                    columns="id"
                )[0]
                
                # 更新现有记录
                self.update(
                    where_clause="id=?",
                    where_params=(existing['id'],),
                    update_data={'is_current': 1}
                )
                return existing['id']
            else:
                # 其他错误
                raise e

    def get_plan_by_id(self, plan_id: int) -> Optional[Dict]:
        """
        通过ID获取学习计划
        返回字典或None
        """
        result = self.select(
            where_clause="id=?",
            where_params=(plan_id,)
        )
        return result[0] if result else None

    def update_plan(
        self,
        plan_id: int,
        word_count: Optional[int] = None,
        wordlist_name: Optional[str] = None,
        current_index: Optional[int] = None,
        completed_time: Optional[Union[str, datetime]] = None,
        is_current: Optional[int] = None
    ) -> int:
        """
        更新学习计划
        参数:
            plan_id: 计划ID
            word_count: 单词数量
            wordlist_name: 单词列表名称
            current_index: 当前学习索引
            completed_time: 完成时间
            is_current: 是否设为当前计划(0/1)
        返回受影响的行数
        """
        # 处理完成时间格式
        if isinstance(completed_time, datetime):
            completed_time = completed_time.strftime('%Y-%m-%d %H:%M:%S')
            
        update_data = {
            'word_count': word_count,
            'wordlist_name': wordlist_name,
            'current_index': current_index,
            'completed_time': completed_time,
            'is_current': is_current
        }
        # 移除值为None的键
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        # 如果设置为当前计划,先取消其他当前计划
        if 'is_current' in update_data and update_data['is_current'] == 1:
            plan = self.get_plan_by_id(plan_id)
            if plan:
                self._clear_current_plan(plan['user_id'])
                
        return self.update(
            where_clause="id=?",
            where_params=(plan_id,),
            update_data=update_data
        )

    def delete_plan(self, plan_id: int) -> int:
        """
        删除学习计划
        返回受影响的行数
        """
        return self.delete(
            where_clause="id=?",
            where_params=(plan_id,)
        )

    # ================= 特定功能方法 =================
    
    def get_current_plan(self, user_id: int = 0) -> Optional[Dict]:
        """
        获取用户的当前学习计划
        返回字典或None
        """
        result = self.select(
            where_clause="user_id=? AND is_current=1",
            where_params=(user_id,)
        )
        return result[0] if result else None

    def set_current_plan(self, plan_id: int, user_id: int = 0) -> int:
        """
        设置指定计划为当前学习计划
        返回受影响的行数
        """
        # 先取消其他当前计划
        self._clear_current_plan(user_id)
        
        # 设置新的当前计划
        return self.update(
            where_clause="id=? AND user_id=?",
            where_params=(plan_id, user_id),
            update_data={'is_current': 1}
        )

    def get_user_plans(
        self,
        user_id: int = 0,
        include_completed: bool = False,
        order_by_created: bool = True,
        descending: bool = True
    ) -> List[Dict]:
        """
        获取用户的所有学习计划
        参数:
            user_id: 用户ID
            include_completed: 是否包含已完成计划
            order_by_created: 是否按创建时间排序
            descending: 是否降序排列(最新的在前)
        返回列表
        """
        where_clause = "user_id=?"
        where_params = (user_id,)
        
        if not include_completed:
            where_clause += " AND completed_time IS NULL"
            
        order_by_clause = None
        if order_by_created:
            order_by_clause = "created_time"
            order_by_clause += " DESC" if descending else " ASC"

        return self.select(
            where_clause=where_clause,
            where_params=where_params,
            order_by=order_by_clause  # 传入排序条件
        )
    def update_quantity(self, plan_id: int, quantity: int) -> int:
        """
        更新学习计划的单词数量
        参数:
            plan_id: 计划ID
            quantity: 新的单词数量
        返回受影响的行数
        """
        return self.update(
            where_clause="id=?",
            where_params=(plan_id,),
            update_data={'quantity': quantity}
        )
    def update_progress(
        self,
        plan_id: int,
        current_index: int,
        mark_completed: bool = False
    ) -> int:
        """
        更新学习进度
        参数:
            plan_id: 计划ID
            current_index: 新的当前索引
            mark_completed: 是否标记为已完成
        返回受影响的行数
        """
        update_data = {
            'current_index': current_index
        }
        
        if mark_completed:
            update_data['completed_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
        return self.update(
            where_clause="id=?",
            where_params=(plan_id,),
            update_data=update_data
        )

    # ================= 私有方法 =================
    
    def _clear_current_plan(self, user_id: int = 0) -> int:
        """
        清除用户的所有当前计划标记
        返回受影响的行数
        """
        return self.update(
            where_clause="user_id=? AND is_current=1",
            where_params=(user_id,),
            update_data={'is_current': 0}
        )