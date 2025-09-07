"""
对ai的提示词进行存储的数据操作类
"""
from .base import BaseTableOperator
from .registry import OperatorRegistry

@OperatorRegistry.register('prompt')
class Prompt(BaseTableOperator):
    def __init__(self, conn,table_name):
        super().__init__(conn, 'prompt')
    def get_table_definition(self) -> str:
        table = '''
                CREATE TABLE IF NOT EXISTS prompt (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    the_direction_of_the_plot TEXT,
                    greeting_text TEXT,
                    restraint TEXT,
                    scene TEXT,
                    end_condition TEXT
                )'''
        return table
    
    def add_scenario(self, name: str, description: str = None, 
                    the_direction_of_the_plot: str = None,
                    greeting_text: str = None, restraint: str = None,
                    scene: str = None, end_condition: str = None) -> int:
        """
        添加新场景
        返回插入的rowid
        """
        data = {
            'name': name,
            'description': description,
            'the_direction_of_the_plot': the_direction_of_the_plot,
            'greeting_text': greeting_text,
            'restraint': restraint,
            'scene': scene,
            'end_condition': end_condition
        }
        # 移除值为None的键
        data = {k: v for k, v in data.items() if v is not None}
        return self.insert(data)

    def update_scenario(self, scenario_id: int, name: str = None, 
                       description: str = None, 
                       the_direction_of_the_plot: str = None,
                       greeting_text: str = None, restraint: str = None,
                       scene: str = None, end_condition: str = None) -> int:
        """
        更新场景信息
        返回受影响的行数
        """
        update_data = {
            'name': name,
            'description': description,
            'the_direction_of_the_plot': the_direction_of_the_plot,
            'greeting_text': greeting_text,
            'restraint': restraint,
            'scene': scene,
            'end_condition': end_condition
        }
        # 移除值为None的键
        update_data = {k: v for k, v in update_data.items() if v is not None}
        return self.update(
            where_clause="id=?",
            where_params=(scenario_id,),
            update_data=update_data
        )

    def get_scenario(self, scenario_id: int) -> dict:
        """
        获取单个场景的完整信息
        返回字典或None
        """
        result = self.select(
            where_clause="id=?",
            where_params=(scenario_id,)
        )
        return result[0] if result else None

    def get_scenario_by_name(self, name: str) -> dict:
        """
        根据名称获取场景的完整信息
        返回字典或None
        """
        result = self.select(
            where_clause="name=?",
            where_params=(name,)
        )
        return result[0] if result else None

    def list_scenarios(self) -> list:
        """
        获取所有场景的列表
        返回列表
        """
        return self.select()

    def delete_scenario(self, scenario_id: int) -> int:
        """
        删除场景
        返回受影响的行数
        """
        return self.delete(
            where_clause="id=?",
            where_params=(scenario_id,)
        )

    # ================= 单个属性操作方法 =================
    
    def get_attribute(self, scenario_id: int, attribute_name: str) -> Any:
        """
        获取场景的单个属性值
        返回属性值或None
        """
        result = self.select(
            columns=attribute_name,
            where_clause="id=?",
            where_params=(scenario_id,)
        )
        return result[0][attribute_name] if result else None

    def update_attribute(self, scenario_id: int, attribute_name: str, 
                        attribute_value: Any) -> int:
        """
        更新场景的单个属性值
        返回受影响的行数
        """
        return self.update(
            where_clause="id=?",
            where_params=(scenario_id,),
            update_data={attribute_name: attribute_value}
        )

    # ================= 特定属性便捷方法 =================
    
    def get_greeting_text(self, scenario_id: int) -> str:
        """获取场景的问候文本"""
        return self.get_attribute(scenario_id, 'greeting_text')

    def update_greeting_text(self, scenario_id: int, greeting_text: str) -> int:
        """更新场景的问候文本"""
        return self.update_attribute(scenario_id, 'greeting_text', greeting_text)

    def get_scene_description(self, scenario_id: int) -> str:
        """获取场景描述"""
        return self.get_attribute(scenario_id, 'scene')

    def update_scene_description(self, scenario_id: int, scene: str) -> int:
        """更新场景描述"""
        return self.update_attribute(scenario_id, 'scene', scene)

    def get_end_condition(self, scenario_id: int) -> str:
        """获取场景结束条件"""
        return self.get_attribute(scenario_id, 'end_condition')

    def update_end_condition(self, scenario_id: int, end_condition: str) -> int:
        """更新场景结束条件"""
        return self.update_attribute(scenario_id, 'end_condition', end_condition)
