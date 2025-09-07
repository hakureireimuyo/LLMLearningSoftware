
import json
from typing import List, Optional, Dict, Union
from datetime import datetime
from .registry import OperatorRegistry
from .base import BaseTableOperator

@OperatorRegistry.register('daily')
class DailyStudyOperator(BaseTableOperator):
    def __init__(self, conn):
        super().__init__(conn, 'daily')

    def get_table_definition(self) -> str:
        table='''
                CREATE TABLE IF NOT EXISTS daily_study (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    study_date DATE UNIQUE DEFAULT CURRENT_DATE,
                    question_count INTEGER DEFAULT 0,
                    correct_count INTEGER DEFAULT 0,
                    wrong_count INTEGER DEFAULT 0,
                    word_list TEXT,
                    usage_time INTEGER DEFAULT 0,
                    study_plan_id INTEGER,  -- 新增字段
                    review_count INTEGER DEFAULT 0,  -- 新增字段
                    new_word_count INTEGER DEFAULT 0,  -- 新增字段
                    FOREIGN KEY (study_plan_id) REFERENCES study_plan(id)  -- 添加外键
                )'''
        return table
    
    def create_daily_record(
        self,
        study_plan_id: Optional[int] = None,
        question_count: int = 0,
        correct_count: int = 0,
        wrong_count: int = 0,
        word_list: Optional[List[int]] = None,  # 修改为word_list
        usage_time: int = 0,
        review_count: int = 0,
        new_word_count: int = 0,
    ) -> int:
        """
        创建新的每日学习记录
        参数:
            study_plan_id: 关联的学习计划ID
            question_count: 问题总数
            correct_count: 正确数
            wrong_count: 错误数
            word_list: 错误的单词ID列表  # 参数说明更新
            usage_time: 使用时间(秒)
        返回插入的rowid
        """
        data = {
            'study_plan_id': study_plan_id,
            'question_count': question_count,
            'correct_count': correct_count,
            'wrong_count': wrong_count,
            'word_list': self._list_to_str(word_list),  # 字段修改为word_list
            'usage_time': usage_time,
            'review_count': review_count,
            'new_word_count': new_word_count,
        }
        data = {k: v for k, v in data.items() if v is not None}
        return self.insert(data)

    def get_record_by_id(self, record_id: int) -> Optional[Dict]:
        """
        通过ID获取每日学习记录
        返回字典(包含转换后的word_list)或None
        """
        result = self.select(where_clause="id=?", where_params=(record_id,))
        return self._process_record(result[0]) if result else None

    def update_record(
        self,
        record_id: int,
        question_count: Optional[int] = None,
        correct_count: Optional[int] = None,
        wrong_count: Optional[int] = None,
        word_list: Optional[List[int]] = None,  # 修改为word_list
        usage_time: Optional[int] = None,
        study_plan_id: Optional[int] = None,
        review_count: Optional[int] = None,
        new_word_count: Optional[int] = None
    ) -> int:
        """
        更新每日学习记录
        返回受影响的行数
        """
        update_data = {
            'question_count': question_count,
            'correct_count': correct_count,
            'wrong_count': wrong_count,
            'word_list': self._list_to_str(word_list),  # 字段修改为word_list
            'usage_time': usage_time,
            'study_plan_id': study_plan_id,
            'review_count': review_count,
            'new_word_count': new_word_count,
        }
        update_data = {k: v for k, v in update_data.items() if v is not None}
        return self.update(where_clause="id=?", where_params=(record_id,), update_data=update_data)

    # ================= 特定查询方法 =================
    
    def get_record_by_date(
        self,
        study_date: Union[str, datetime],
        study_plan_id: int  # 新增必填参数
    ) -> Optional[Dict]:
        """通过日期和学习计划ID获取每日学习记录"""
        if isinstance(study_date, datetime):
            study_date = study_date.strftime('%Y-%m-%d')
            
        result = self.select(
            where_clause="study_date=? AND study_plan_id=?",  # 修改查询条件
            where_params=(study_date, study_plan_id)
        )
        return self._process_record(result[0]) if result else None

    # ================= 统计方法 =================
    
    def get_today_stats(
        self,
        study_plan_id: int  # 新增必填参数
    ) -> Dict:
        """获取今日学习计划的统计数据"""
        if study_plan_id is None:  # 检查study_plan_id是否为None
            return None
        today = datetime.now().strftime('%Y-%m-%d')
        record = self.get_record_by_date(today, study_plan_id)
        
        # 返回包含study_plan_id的默认数据结构
        return record or {
            'study_plan_id': study_plan_id,  # 保持ID一致性
            'question_count': 0,
            'correct_count': 0,
            'wrong_count': 0,
            'usage_time': 0,
            'word_list': [],
            'review_count': 0,
            'new_word_count': 0,
        }

    def increment_today_stats(
        self,
        study_plan_id: int,  # 改为必填参数
        question_count: int = 0,
        correct_count: int = 0,
        wrong_count: int = 0,
        wrong_word_id: Optional[list] = None,
        usage_time: int = 0,
        review_count: int = 0,
        new_word_count: int = 0
    ) -> Dict:
        """
        增量更新今天的学习统计数据
        参数:
            study_plan_id: 必填的学习计划ID
            question_count: 新增问题总数
            correct_count: 新增正确数
            wrong_count: 新增错误数
            wrong_word_id: 可选错误单词ID
            usage_time: 新增使用时间(秒)
        返回更新后的记录
        """
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 获取当前记录（带study_plan_id条件）
        today_record = self.get_record_by_date(today, study_plan_id)
        
        # 初始化基础数据
        update_data = {
            'study_plan_id': study_plan_id,  # 强制使用当前传入的ID
            'question_count': question_count,
            'correct_count': correct_count,
            'wrong_count': wrong_count,
            'usage_time': usage_time,
            'review_count': review_count,
            'new_word_count': new_word_count,
        }
        word_list = []

        # 合并已有数据
        if today_record:
            word_list = today_record['word_list']
            update_data = {
                'study_plan_id': study_plan_id,
                'question_count': today_record['question_count'] + question_count,
                'correct_count': today_record['correct_count'] + correct_count,
                'wrong_count': today_record['wrong_count'] + wrong_count,
                'usage_time': today_record['usage_time'] + usage_time,
                'review_count': today_record['review_count'] + review_count,
                'new_word_count': today_record['new_word_count'] + new_word_count,
            }

        # 处理错误单词
        if wrong_word_id is not None:
            word_list.extend(wrong_word_id)
            update_data['word_list'] = word_list

        # 执行操作
        if today_record:
            self.update_record(today_record['id'], **update_data)
        else:
            # 确保新建时包含必要字段
            self.create_daily_record(
                study_plan_id=study_plan_id,
                question_count=update_data.get('question_count', 0),
                correct_count=update_data.get('correct_count', 0),
                wrong_count=update_data.get('wrong_count', 0),
                word_list=word_list,
                usage_time=update_data.get('usage_time', 0),
                review_count=update_data.get('review_count', 0),
                new_word_count=update_data.get('new_word_count', 0)
            )

        return self.get_record_by_date(today, study_plan_id)

    # ================= 辅助方法 =================
    
    def _list_to_str(self, id_list: Optional[List[int]]) -> Optional[str]:
        """将ID列表转换为字符串格式"""
        return json.dumps(id_list) if id_list else None

    def _str_to_list(self, id_str: Optional[str]) -> List[int]:
        """将字符串格式的ID列表转换为Python列表"""
        try:
            return json.loads(id_str) if id_str else []
        except json.JSONDecodeError:
            return []

    def _process_record(self, record: Dict) -> Dict:
        """处理记录字段转换"""
        return {
            **record,
            'word_list': self._str_to_list(record.get('word_list'))  # 只处理word_list
        }
    
