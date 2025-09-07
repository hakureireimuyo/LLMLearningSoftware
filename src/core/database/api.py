"""
存储了api操作所需要的数据
如何做到兼容?除了尽可能覆盖通用的属性,剩下的通过文本与结构解析
毕业设计才需要多个用户,作为单个软件其实完全不需要
因此使用记录调用次数可以直接在这里记录,不需要区分多个用户
"""
from .base import BaseTableOperator
from .registry import OperatorRegistry
from typing import Union
# ================= API身份密钥管理 =================
@OperatorRegistry.register('api')
class API(BaseTableOperator):
    def get_table_definition(self):
        table = '''
                CREATE TABLE IF NOT EXISTS api (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service_provider TEXT DEFAULT '',
                    user_id INTEGER DEFAULT 1,
                    app_id TEXT DEFAULT '',
                    api_key TEXT DEFAULT '',
                    secret_key TEXT DEFAULT '',
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                )'''
        return table

    # ================= 基础查询方法 =================
    def get_by_user_service(self, user_id: int, service: str) -> Union[dict,None]:
        """根据用户ID和服务商获取凭证"""
        result = self.select(
            where_clause="user_id=? AND service_provider=?",
            where_params=(user_id, service))
        return result[0] if result else None

    def get_all_user_credentials(self, user_id: int=0) -> list:
        """获取用户所有API凭证"""
        return self.select(
            where_clause="user_id=?", 
            where_params=(user_id,)
        )

    # ================= 字段更新方法 =================
    def update_service_provider(self, credential_id: int, new_service: str) -> bool:
        """更新服务商名称"""
        if not new_service.strip():
            raise ValueError("服务商名称不能为空")
        return self._update_field(credential_id, 'service_provider', new_service)

    def update_user(self, credential_id: int, new_user_id: int) -> bool:
        """更新关联用户"""
        return self._update_field(credential_id, 'user_id', new_user_id)

    def update_app_id(self, credential_id: int, new_app_id: str) -> bool:
        """更新应用ID"""
        return self._update_field(credential_id, 'app_id', new_app_id)

    def update_api_key(self, credential_id: int, new_api_key: str) -> bool:
        """更新API密钥"""
        if not new_api_key:
            raise ValueError("API密钥不能为空")
        return self._update_field(credential_id, 'api_key', new_api_key)

    def update_secret_key(self, credential_id: int, new_secret: str) -> bool:
        """更新密钥"""
        if not new_secret:
            raise ValueError("密钥不能为空")
        return self._update_field(credential_id, 'secret_key', new_secret)

    # ================= 组合更新方法 =================
    def update_keys(self, credential_id: int, api_key: str, secret_key: str) -> bool:
        """同时更新API密钥和密钥"""
        if not api_key or not secret_key:
            raise ValueError("密钥字段不能为空")
        
        return self.update(
            where_clause="id=?",
            where_params=(credential_id,),
            update_data={
                'api_key': api_key,
                'secret_key': secret_key
            }
        ) > 0

    def update_service_info(self, credential_id: int, 
                          service: str, 
                          provider_id: str) -> bool:
        """更新服务商信息"""
        return self.update(
            where_clause="id=?",
            where_params=(credential_id,),
            update_data={
                'service_provider': service,
                'provider_id': provider_id
            }
        ) > 0

    # ================= 辅助方法 =================
    def _update_field(self, credential_id: int, field: str, value: any) -> bool:
        """通用字段更新方法"""
        return self.update(
            where_clause="id=?",
            where_params=(credential_id,),
            update_data={field: value}
        ) > 0

    # ================= 高级操作 =================
    def rotate_keys(self, credential_id: int, 
                   new_api_key: str, 
                   new_secret: str) -> bool:
        """密钥轮换（保留历史记录）"""
        old_data = self.select(where_clause="id=?", where_params=(credential_id,))
        if not old_data:
            return False

        # 在事务中执行旧记录归档和新记录插入
        with self._conn:
            # 1. 归档旧记录
            self.insert({
                'service_provider': old_data[0]['service_provider'],
                'provider_id': old_data[0]['provider_id'],
                'user_id': old_data[0]['user_id'],
                'app_id': old_data[0]['app_id'],
                'api_key': old_data[0]['api_key'],
                'secret_key': old_data[0]['secret_key']
            })

            # 2. 更新当前记录
            return self.update_keys(credential_id, new_api_key, new_secret)
    # ================= 字段获取方法 =================
    def get_service_provider(self, credential_id: int) -> Union[str, None]:
        """获取服务商名称"""
        return self._get_single_field(credential_id, 'service_provider')

    def get_provider_id(self, credential_id: int) -> Union[str, None]:
        """获取服务商ID"""
        return self._get_single_field(credential_id, 'provider_id')

    def get_user_id(self, credential_id: int) -> Union[int, None]:
        """获取关联用户ID"""
        return self._get_single_field(credential_id, 'user_id')

    def get_app_id(self, credential_id: int) -> Union[str, None]:
        """获取应用ID"""
        return self._get_single_field(credential_id, 'app_id')

    def get_api_key(self, credential_id: int) -> Union[str, None]:
        """获取API密钥"""
        return self._get_single_field(credential_id, 'api_key')

    def get_secret_key(self, credential_id: int) -> Union[str, None]:
        """获取密钥"""
        return self._get_single_field(credential_id, 'secret_key')

    # ================= 组合获取方法 =================
    def get_sensitive_data(self, credential_id: int) -> dict:
        """获取敏感信息（密钥相关）"""
        return self._get_fields(
            credential_id, 
            ['api_key', 'secret_key', 'provider_id']
        )

    def get_service_info(self, credential_id: int) -> dict:
        """获取服务商信息"""
        return self._get_fields(
            credential_id, 
            ['service_provider', 'provider_id', 'app_id']
        )

    # ================= 辅助方法 =================
    def _get_single_field(self, credential_id: int, field: str) -> any:
        """通用单字段查询方法"""
        result = self.select(
            columns=field,
            where_clause="id=?",
            where_params=(credential_id,))
        return result[0].get(field) if result else None

    def _get_fields(self, credential_id: int, fields: list) -> dict:
        """多字段查询方法"""
        columns = ', '.join(fields)
        result = self.select(
            columns=columns,
            where_clause="id=?",
            where_params=(credential_id,))
            
        return result[0] if result else {}
    