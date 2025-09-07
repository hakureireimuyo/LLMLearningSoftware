import json
from enum import Enum

class ParserState(Enum):
    WAIT_KEY = 0
    IN_STRING = 1
    CAPTURING = 2

class StreamingJSONParser:
    def __init__(self):
        self.buffer = []
        self.brace_stack = []  # 记录{的索引位置
        self.quote_positions = []  # 记录"的索引位置
        self.current_key = None
        self.state = ParserState.WAIT_KEY
        self.escape = False
        self.target_braces = 3  # 目标层级深度
        self.process_parse_data = lambda x: None
        self.process_suggestion_data = lambda x: None

    def set_callbacks(self, callback1, callback2):
        self.process_parse_data = callback1
        self.process_suggestion_data = callback2

    def process_char(self, char):
        # 更新缓冲区
        self.buffer.append(char)
        index = len(self.buffer) - 1

        # 状态机核心逻辑
        if self.state == ParserState.WAIT_KEY:
            self._handle_wait_key(char, index)
        elif self.state == ParserState.IN_STRING:
            self._handle_in_string(char, index)
            return None
        elif self.state == ParserState.CAPTURING:
            #print("捕获数据中")
            self._handle_capturing(char, index)

    def _handle_wait_key(self, char, index):
        if char == '{':
            self.brace_stack.append(index)
            if len(self.brace_stack) == 1:  # 根层级的{
                self.quote_positions = []
        elif char == '}':
            if self.brace_stack:
                start = self.brace_stack.pop()
                # 当捕获到目标层级的闭合
                if len(self.brace_stack) == self.target_braces:
                    self._process_slice(start+1, index)
        elif char == '"':
            self.state = ParserState.IN_STRING
            self.quote_positions.append(index)

    def _handle_in_string(self, char, index):
        if char == '"':
            # 提取完整键名
            start = self.quote_positions[-1]
            key = ''.join(self.buffer[start+1:index])
            #print(start,index,key)
            if key in ('parse', 'suggestion') and len(self.brace_stack)==1:
                #print(f"关键字{key}判定成功")
                self.current_key = key
                self.state = ParserState.CAPTURING
                self.target_start = None
                return True
            self.quote_positions.append(index)
            self.state = ParserState.WAIT_KEY
        return False
    
    def _handle_capturing(self, char, index):
        if char == '{':
            self.brace_stack.append(index)
            if len(self.brace_stack) == self.target_braces:
                self.target_start = index
        elif char == '}':
            #print(f"当前层级{len(self.brace_stack)}")
            if self.brace_stack and len(self.brace_stack) >= self.target_braces:
                start_index = self.brace_stack.pop()
                #print(start_index)
                if len(self.brace_stack) == self.target_braces-1:#pop出数据，所以判定的时候需要-1
                    # 提取目标数据段
                    json_str = ''.join(self.buffer[self.target_start:index+1])
                    #print(json_str)
                    try:
                        data = json.loads(json_str)
                        self._dispatch_data(data)
                    except json.JSONDecodeError:
                        pass
            else:
                self.brace_stack.pop()
            #当前层级的数据全部取出后，继续等待下一层
            if len(self.brace_stack) == 1:
                self.state = ParserState.WAIT_KEY
            #print(f"当前层级{len(self.brace_stack)}")

    def _process_slice(self, start, end):
        """处理第三层数据切片"""
        json_str = ''.join(self.buffer[start:end])
        try:
            data = json.loads('{'+json_str+'}')  # 补全为合法JSON
            self._dispatch_data(data)
        except json.JSONDecodeError as e:
            print(f"解析失败: {str(e)}")

    def _dispatch_data(self, data):
        """分发处理数据"""
        if self.current_key == 'parse':
            self.handle_parse(data)
        elif self.current_key == 'suggestion':
            self.handle_suggestion(data)
        # 清空状态
        self.target_start = None

    def handle_parse(self, data):
        # print("\n捕获到语法分析数据:")
        # print(data)
        self.process_parse_data(data)
        
    def handle_suggestion(self,data):
        # print("\n捕获到优化建议:")
        # print(data)
        self.process_suggestion_data(data)
     