# import json
# import sqlite3
# from typing import Any, Dict
# from .database_management.config_mamger import CM
# class SystemSettingsCache:
#     """
#     系统设置缓存类（单例模式）
#     功能：
#     1. 自动加载当前用户的设置
#     2. 跟踪修改并在析构时自动保存
#     3. 提供属性式访问设置项
#     4. 支持手动重新加载数据
#     5. 支持创建新设置项
#     """
#     _instance = None
#     _initialized = False

#     def __new__(cls, *args, **kwargs):
#         # 单例核心逻辑：仅当实例不存在时创建新实例
#         if not cls._instance:
#             # 创建实例时传递参数给__init__
#             cls._instance = super().__new__(cls)
#             # 仅在首次创建时初始化
#             cls._instance.__init__(*args, **kwargs)
#         return cls._instance

#     def __init__(self, db_manager):
#         # 通过标志位确保只初始化一次
#         if self.__class__._initialized:
#             return

#         self._current_user_id = None
#         self._settings: Dict[str, Any] = {}
#         self._modified: Dict[str, Any] = {}
#         self._dao = db_manager.get_module_dao('system_settings')
#         self.reload()
#         self.__class__._initialized = True  # 使用类属性确保跨实例同步

#     def reload(self):
#         """重新加载当前用户的设置"""
#         new_user_id = CM.CURRENT_USER_ID
        
#         # 仅在用户改变或首次加载时执行
#         if new_user_id != self._current_user_id:
#             self._current_user_id = new_user_id
#             self._settings.clear()
#             self._modified.clear()

#             # 从数据库加载所有设置项
#             with self._dao.transaction():
#                 operator = self._dao.system_settings
#                 records = operator.select(
#                     where_clause="user_id=?",
#                     where_params=(self._current_user_id,)
#                 )
                
#                 for record in records:
#                     key = record['setting_key']
#                     value = record['setting_value']
#                     self._settings[key] = value

#     def __getattr__(self, name: str) -> Any:
#         """通过属性访问设置值"""
#         if name in self._settings:
#             return self._settings[name]
#         raise AttributeError(f"系统设置 '{name}' 不存在")
    
#     def get(self, name: str, default: Any = None) -> Any:
#         """安全获取设置值（推荐方式），允许指定默认值"""
#         return self._settings.get(name, default)
    
#     def __setattr__(self, name: str, value: Any):
#         """通过属性设置值时跟踪修改"""
#         if name.startswith('_'):
#             super().__setattr__(name, value)
#         else:
#             # 只在值实际发生变化时记录修改
#             current = self._settings.get(name, None)
#             if current != value:
#                 self._settings[name] = value
#                 self._modified[name] = value

#     def set(self, name: str, value: Any):
#         """安全设置设置值（推荐方式）"""
#         self.__setattr__(name, value)

#     def create_setting(self, key: str, value: Any):
#         """
#         显式创建新设置项
#         """
#         with self._dao.transaction():
#             self._dao.system_settings.set_setting(
#                 user_id=self._current_user_id,
#                 setting_key=key,
#                 setting_value=value
#             )
#         # 更新本地缓存
#         self._settings[key] = value
#         # 如果存在于修改记录中则移除
#         self._modified.pop(key, None)

#     def __del__(self):
#         """析构时自动保存修改"""
#         try:
#             if self._modified:
#                 with self._dao.transaction():
#                     operator = self._dao.system_settings
#                     for key, value in self._modified.items():
#                         operator.set_setting(
#                             user_id=self._current_user_id,
#                             setting_key=key,
#                             setting_value=value
#                         )
#         except (sqlite3.ProgrammingError, AttributeError):
#             # 处理数据库连接已关闭的情况
#             pass

#     @property
#     def is_dirty(self) -> bool:
#         """检查是否有未保存的修改"""
#         return bool(self._modified)

#     def manual_save(self):
#         """手动立即保存修改"""
#         self.__del__()  # 调用析构保存逻辑
#         self._modified.clear()
import json
import sqlite3
from typing import Any, Dict, Callable, List
from collections import defaultdict
from .database_management.config_mamger import CM

class SystemSettingsCache:
    """
    系统设置缓存类（单例模式）
    功能：
    1. 自动加载当前用户的设置
    2. 跟踪修改并在析构时自动保存
    3. 提供属性式访问设置项
    4. 支持手动重新加载数据
    5. 支持创建新设置项
    6. 观察者模式支持属性变更回调
    """
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.__init__(*args, **kwargs)
        return cls._instance

    def __init__(self, db_manager):
        if self.__class__._initialized:
            return

        self._current_user_id = None
        self._settings: Dict[str, Any] = {}
        self._modified: Dict[str, Any] = {}
        self._dao = db_manager.get_module_dao('system_settings')
        self._observers: Dict[str, List[Callable[[str, Any, Any], None]]] = defaultdict(list)
        self.reload()
        self.__class__._initialized = True

    def reload(self):
        """重新加载当前用户的设置"""
        new_user_id = CM.CURRENT_USER_ID
        if new_user_id != self._current_user_id:
            self._current_user_id = new_user_id
            self._settings.clear()
            self._modified.clear()

            with self._dao.transaction():
                operator = self._dao.system_settings
                records = operator.select(
                    where_clause="user_id=?",
                    where_params=(self._current_user_id,)
                )
                
                for record in records:
                    key = record['setting_key']
                    value = record['setting_value']
                    self._settings[key] = value

    def __getattr__(self, name: str) -> Any:
        if name in self._settings:
            return self._settings[name]
        raise AttributeError(f"系统设置 '{name}' 不存在")
    
    def get(self, name: str, default: Any = None) -> Any:
        return self._settings.get(name, default)
    
    def __setattr__(self, name: str, value: Any):
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            current = self._settings.get(name, None)
            if current != value:
                old_value = current
                self._settings[name] = value
                self._modified[name] = value
                self._trigger_callbacks(name, old_value, value)

    def set(self, name: str, value: Any):
        self.__setattr__(name, value)

    def _trigger_callbacks(self, key: str, old_value: Any, new_value: Any):
        """触发指定键的所有回调函数"""
        for callback in self._observers.get(key, []):
            try:
                callback(key, old_value, new_value)
            except Exception as e:
                # 异常处理，可根据需要记录日志
                pass

    def register_callback(self, key: str, callback: Callable[[str, Any, Any], None]):
        """注册属性变更回调函数"""
        if callback not in self._observers[key]:
            self._observers[key].append(callback)

    def unregister_callback(self, key: str, callback: Callable[[str, Any, Any], None]):
        """注销属性变更回调函数"""
        if callback in self._observers[key]:
            self._observers[key].remove(callback)

    def create_setting(self, key: str, value: Any):
        """显式创建新设置项并触发回调"""
        with self._dao.transaction():
            self._dao.system_settings.set_setting(
                user_id=self._current_user_id,
                setting_key=key,
                setting_value=value
            )
        old_value = self._settings.get(key, None)
        self._settings[key] = value
        self._modified.pop(key, None)
        self._trigger_callbacks(key, old_value, value)

    def __del__(self):
        try:
            if self._modified:
                with self._dao.transaction():
                    operator = self._dao.system_settings
                    for key, value in self._modified.items():
                        operator.set_setting(
                            user_id=self._current_user_id,
                            setting_key=key,
                            setting_value=value
                        )
        except (sqlite3.ProgrammingError, AttributeError):
            pass

    @property
    def is_dirty(self) -> bool:
        return bool(self._modified)

    def manual_save(self):
        self.__del__()
        self._modified.clear()