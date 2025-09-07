from src.core.parser import LiteralParser
import pytest

@pytest.fixture
def parser():
    return LiteralParser()

# 测试基本类型解析
def test_int_parsing(parser):
    assert parser.parse("123") == 123
    assert parser.parse("-456") == -456
    assert parser.parse("0") == 0

def test_float_parsing(parser):
    assert parser.parse("3.14") == 3.14
    assert parser.parse("-2.718") == -2.718
    assert parser.parse("0.0") == 0.0

def test_bool_parsing(parser):
    assert parser.parse("true") is True
    assert parser.parse("false") is False
    assert parser.parse("True") is True  # 测试大小写不敏感
    assert parser.parse("False") is False

def test_none_parsing(parser):
    assert parser.parse("null") is None
    assert parser.parse("None") is None  # Python 风格的 None

# 测试字符串解析
def test_string_parsing(parser):
    assert parser.parse("hello") == "hello"
    assert parser.parse("123abc") == "123abc"  # 看起来像数字但不是纯数字
    assert parser.parse('"quoted string"') == "quoted string"

# 测试列表解析
def test_list_parsing(parser):
    assert parser.parse("[1, 2, 3]") == [1, 2, 3]
    assert parser.parse('["a", "b", "c"]') == ["a", "b", "c"]
    assert parser.parse("[true, false, null]") == [True, False, None]
    assert parser.parse("[]") == []  # 空列表

# 测试字典解析
def test_dict_parsing(parser):
    assert parser.parse('{"name": "John", "age": 30}') == {"name": "John", "age": 30}
    assert parser.parse('{"is_active": true, "balance": 100.50}') == {"is_active": True, "balance": 100.50}
    assert parser.parse('{}') == {}  # 空字典

# 测试嵌套结构解析
def test_nested_structure(parser):
    input_str = '{"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}], "count": 2}'
    expected = {
        "users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}],
        "count": 2
    }
    assert parser.parse(input_str) == expected

# 测试无效输入处理
def test_invalid_input(parser):
    # 无效的 JSON 字符串
    assert parser.parse("invalid{json") == "invalid{json"
    
    # Python 语法中无效的结构
    assert parser.parse("{'key': 'value'}") == "{'key': 'value'}"  # JSON 要求双引号
    
    # 无法解析的输入
    assert parser.parse("this is a string with spaces") == "this is a string with spaces"
    
    # 空字符串和空白字符串
    assert parser.parse("") == ""
    assert parser.parse("   ") == "   "

# 测试自定义格式
def test_custom_formats(parser):
    # Python 元组表示法
    assert parser.parse("(1, 2, 3)") == (1, 2, 3)
    
    # Python 集合表示法
    assert parser.parse("{1, 2, 3}") == {1, 2, 3}
    
    # Python 中的 None 表示法
    assert parser.parse("None") is None
    
    # JSON 中的 null 表示法
    assert parser.parse("null") is None

# 测试空格处理
def test_whitespace_handling(parser):
    assert parser.parse("  123  ") == 123
    assert parser.parse("  true  ") is True
    assert parser.parse('  {"key":"value"}  ') == {"key": "value"}