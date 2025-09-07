import ast
import json
from typing import Any

class LiteralParser:
    """
    将字符串转换为Python基本数据结构的解析器
    
    支持转换类型：
    - int, float, bool
    - str
    - list, tuple, set
    - dict
    
    示例：
    >>> parser = StringToPythonParser()
    >>> parser.parse("123")
    123
    >>> parser.parse("[1, 2, 3]")
    [1, 2, 3]
    >>> parser.parse('{"name": "John", "age": 30}')
    {'name': 'John', 'age': 30}
    """
    
    def parse(self, input_str: str) -> Any:
        """
        解析输入字符串为Python对象
        
        :param input_str: 要解析的字符串
        :return: 解析后的Python对象
        """
        # 尝试直接解析为基本类型
        result = self._try_parse_basic_types(input_str)
        if result is not None:
            return result
        
        # 尝试解析为JSON格式
        try:
            return json.loads(input_str)
        except json.JSONDecodeError:
            pass
        
        # 尝试使用ast安全解析
        try:
            return ast.literal_eval(input_str)
        except (ValueError, SyntaxError):
            pass
        
        # 如果所有方法都失败，返回原始字符串
        return input_str
    
    def _try_parse_basic_types(self, input_str: str) -> Any:
        """尝试解析基本类型（int, float, bool, None）"""
        stripped = input_str.strip()
        
        # 处理空值
        if stripped.lower() in ("null", "none"):
            return None
        
        # 处理布尔值
        if stripped.lower() == "true":
            return True
        if stripped.lower() == "false":
            return False
        
        # 处理整数
        try:
            return int(stripped)
        except ValueError:
            pass
        
        # 处理浮点数
        try:
            return float(stripped)
        except ValueError:
            pass
        
        return None
