
from typing import Union, Any, Dict
from .base import BaseTableOperator
from .registry import OperatorRegistry

@OperatorRegistry.register('settings')
class SettingsOperator(BaseTableOperator):
    def __init__(self, conn):
        super().__init__(conn, 'settings')

    def get_table_definition(self) -> str:
        table='''
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    setting_key TEXT NOT NULL,
                    setting_value TEXT,
                    UNIQUE(user_id, setting_key),
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                )'''
        return table
    
    def get_setting(self, user_id: int, setting_key: str, 
                   default: Any = None) -> Union[int, float, str, bool, list, dict]:
        """
        获取用户配置项（带类型转换）
        返回转换后的值或默认值
        
        参数:
            user_id: 用户ID
            setting_key: 配置键名
            default: 如果配置不存在时返回的默认值
        """
        setting = self.get_setting_raw(user_id, setting_key)
        if not setting:
            return default
            
        return self._convert_value_from_storage(
            setting['setting_value'], 
            setting['value_type']
        )

    def get_setting_raw(self, user_id: int, setting_key: str) -> dict:
        """
        获取原始配置记录（不进行类型转换）
        返回完整记录或None
        """
        result = self.select(
            where_clause="user_id=? AND setting_key=?",
            where_params=(user_id, setting_key)
        )
        return result[0] if result else None

    def get_all_settings(self, user_id: int) -> Dict[str, Any]:
        """获取指定用户的所有设置项"""
        records = self.select(
            where_clause="user_id=?",
            where_params=(user_id,))
        return {r['setting_key']: r['setting_value'] for r in records}

    def update_multiple_settings(self, user_id: int, settings: Dict[str, Any]) -> int:
        """批量更新设置项"""
        affected = 0
        with self._conn:
            for key, value in settings.items():
                affected += self.set_setting(user_id, key, value)
        return affected

    def set_setting(self, user_id: int, setting_key: str, setting_value: Any) -> int:
        """简化后的设置方法（已移除类型相关代码）"""
        existing = self.get_setting_raw(user_id, setting_key)
        
        if existing:
            return self.update(
                where_clause="user_id=? AND setting_key=?",
                where_params=(user_id, setting_key),
                update_data={'setting_value': setting_value}
            )
        else:
            return self.insert({
                'user_id': user_id,
                'setting_key': setting_key,
                'setting_value': setting_value
            })
