from kivy.uix.label import Label
from kivy.properties import BooleanProperty, StringProperty
from kivy.utils import escape_markup
from kivy.clock import Clock

class MarkdownToKivyMarkupMixin:
    """
    基于状态机的 Markdown 到 Kivy Markup 转换器混合类
    使用逐个字符解析的方式，避免多次正则匹配
    """
    
    use_markdown = BooleanProperty(True)
    """是否启用 Markdown 转换，默认为 True"""
    
    original_text = StringProperty("")
    """存储原始的 Markdown 文本"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(use_markdown=self._update_text)
        self.bind(original_text=self._update_text)
        self.markup = True
        self._update_text(None,None)
    
    def _update_text(self, instance, value):
        """更新文本内容"""
        print(f"更新文本: {self.original_text}")
        if self.use_markdown:
            self.text = self.convert_markdown(self.original_text)
        else:
            self.text = self.original_text
    
    def convert_markdown(self, text):
        """将 Markdown 语法转换为 Kivy Markup"""
        if not text:
            return ""
        
        # 创建状态机解析器
        parser = MarkdownParser(text)
        return parser.parse()
    
    def on_ref_press(self, ref):
        """处理链接点击事件"""
        print(f"链接被点击: {ref}")

class MarkdownParser:
    """Markdown 解析器（基于状态机）"""
    
    def __init__(self, text):
        self.text = text
        self.position = 0
        self.result = []
        self.stack = []
        self.link_text = None
        self.link_url = None
        self.last_char = None
        self.states = {
            'normal': self.process_normal,
            'bold': self.process_bold,
            'italic': self.process_italic,
            'strikethrough': self.process_strikethrough,
            'underline': self.process_underline,
            'code': self.process_code,
            'link_text': self.process_link_text,
            'link_url': self.process_link_url,
            'heading': self.process_heading,
            'list_item': self.process_list_item,
            'blockquote': self.process_blockquote,
        }
        self.current_state = 'normal'
    
    def parse(self):
        """解析 Markdown 文本"""
        while self.position < len(self.text):
            char = self.text[self.position]
            self.states[self.current_state](char)
            self.last_char = char
            self.position += 1
        
        # 关闭所有未关闭的标签
        while self.stack:
            self.close_tag(self.stack.pop())
        
        return ''.join(self.result)
    
    def process_normal(self, char):
        """处理普通文本状态"""
        if char == '*':
            if self.peek(1) == '*':
                self.open_tag('bold', '[b]', '**')
            else:
                self.open_tag('italic', '[i]', '*')
        elif char == '_':
            if self.peek(1) == '_':
                self.open_tag('bold', '[b]', '__')
            else:
                self.open_tag('italic', '[i]', '_')
        elif char == '~' and self.peek(1) == '~':
            self.open_tag('strikethrough', '[s]', '~~')
        elif char == '[':
            self.open_link_text()
        elif char == '`':
            self.open_tag('code', '[font=monospace]', '`')
        elif char == '<' and self.peek(1) == 'u' and self.peek(2) == '>':
            self.open_tag('underline', '[u]', '<u>')
        elif char == '#' and (self.position == 0 or self.last_char == '\n'):
            self.open_heading()
        elif char == '-' and (self.position == 0 or self.last_char == '\n'):
            self.open_list_item()
        elif char == '>' and (self.position == 0 or self.last_char == '\n'):
            self.open_blockquote()
        elif char == '\\':  # 转义字符
            self.handle_escape()
        else:
            self.add_char(char)
    
    def process_bold(self, char):
        """处理粗体状态"""
        if self.stack and self.stack[-1] == 'bold' and self.match_end_tag('**') or self.match_end_tag('__'):
            self.close_tag('bold')
        else:
            self.add_char(char)
    
    def process_italic(self, char):
        """处理斜体状态"""
        if self.stack and self.stack[-1] == 'italic' and (char == '*' or char == '_'):
            self.close_tag('italic')
        else:
            self.add_char(char)
    
    def process_strikethrough(self, char):
        """处理删除线状态"""
        if self.stack and self.stack[-1] == 'strikethrough' and char == '~' and self.peek(1) == '~':
            self.close_tag('strikethrough')
            self.position += 1  # 跳过第二个~
        else:
            self.add_char(char)
    
    def process_underline(self, char):
        """处理下划线状态"""
        if self.stack and self.stack[-1] == 'underline' and char == '<' and self.peek(1) == '/' and self.peek(2) == 'u' and self.peek(3) == '>':
            self.close_tag('underline')
            self.position += 3  # 跳过</u>
        else:
            self.add_char(char)
    
    def process_code(self, char):
        """处理代码状态"""
        if self.stack and self.stack[-1] == 'code' and char == '`':
            self.close_tag('code')
        else:
            self.add_char(char)
    
    def process_link_text(self, char):
        """处理链接文本状态"""
        if char == ']' and self.peek(1) == '(':
            # 链接文本结束，开始链接URL
            self.position += 1  # 跳过 '('
            self.current_state = 'link_url'
            self.link_url = []
        else:
            if self.link_text is None:
                self.link_text = []
            self.link_text.append(char)
    
    def process_link_url(self, char):
        """处理链接URL状态"""
        if char == ')':
            # 链接结束
            self.close_link()
        else:
            if self.link_url is None:
                self.link_url = []
            self.link_url.append(char)
    
    def process_heading(self, char):
        """处理标题状态"""
        if char == ' ':
            # 标题级别结束，开始标题文本
            self.current_state = 'normal'
            heading_level = self.stack.pop()
            size = 32 - (heading_level * 4)
            self.result.append(f'[size={size}]')
            self.stack.append('heading')
        else:
            # 统计标题级别
            if self.stack and self.stack[-1] == 'heading':
                self.stack[-1] += 1
            else:
                self.stack.append(1)
    
    def process_list_item(self, char):
        """处理列表项状态"""
        if char == ' ':
            # 列表项开始
            self.result.append('• ')
            self.current_state = 'normal'
            self.stack.pop()  # 移除列表标记
        else:
            # 跳过列表标记字符
            pass
    
    def process_blockquote(self, char):
        """处理引用状态"""
        if char == ' ':
            # 引用开始
            self.result.append('[i]')
            self.current_state = 'normal'
            self.stack.append('blockquote')
        else:
            # 跳过引用标记字符
            pass
    
    def open_tag(self, tag, markup, pattern=None):
        """打开一个标签"""
        self.stack.append(tag)
        self.result.append(markup)
        self.current_state = tag
        if pattern:
            self.position += len(pattern) - 1  # 跳过标记字符
    
    def close_tag(self, tag):
        """关闭一个标签"""
        if tag in self.stack:
            # 找到最近匹配的标签
            while self.stack:
                top = self.stack.pop()
                if top == tag:
                    break
                # 关闭中间未关闭的标签
                self.result.append(self.get_close_tag(top))
            
            # 添加关闭标签
            self.result.append(self.get_close_tag(tag))
            self.current_state = 'normal'
    
    def open_link_text(self):
        """开始链接文本"""
        self.stack.append('link')
        self.current_state = 'link_text'
        self.link_text = []
    
    def close_link(self):
        """关闭链接"""
        if self.link_text and self.link_url:
            link_text = ''.join(self.link_text)
            link_url = ''.join(self.link_url)
            self.result.append(f'[ref="{link_url}"]{link_text}[/ref]')
        
        # 重置链接状态
        self.link_text = None
        self.link_url = None
        self.current_state = 'normal'
        
        # 从栈中移除链接标记
        if 'link' in self.stack:
            self.stack.remove('link')
    
    def open_heading(self):
        """开始标题"""
        self.stack.append('heading')
        self.current_state = 'heading'
    
    def open_list_item(self):
        """开始列表项"""
        self.stack.append('list')
        self.current_state = 'list_item'
    
    def open_blockquote(self):
        """开始引用"""
        self.stack.append('blockquote')
        self.current_state = 'blockquote'
    
    def get_close_tag(self, tag):
        """获取标签的关闭标记"""
        tags = {
            'bold': '[/b]',
            'italic': '[/i]',
            'strikethrough': '[/s]',
            'underline': '[/u]',
            'code': '[/font]',
            'heading': '[/size]',
            'blockquote': '[/i]',
        }
        return tags.get(tag, '')
    
    def add_char(self, char):
        """添加字符到结果，处理转义"""
        # 处理特殊字符转义
        if char == '&':
            self.result.append('&amp;')
        elif char == '[':
            self.result.append('&bl;')
        elif char == ']':
            self.result.append('&br;')
        else:
            self.result.append(char)
    
    def handle_escape(self):
        """处理转义字符"""
        if self.position + 1 < len(self.text):
            next_char = self.text[self.position + 1]
            if next_char in ['*', '_', '~', '[', ']', '\\', '#', '-', '>', '`']:
                self.result.append(next_char)
                self.position += 1  # 跳过下一个字符
            else:
                self.result.append('\\')
        else:
            self.result.append('\\')
    
    def peek(self, offset=1):
        """查看指定偏移处的字符"""
        pos = self.position + offset
        if pos < len(self.text):
            return self.text[pos]
        return None
    
    def match_end_tag(self, tag):
        """检查是否匹配结束标签"""
        if self.text.startswith(tag, self.position):
            return True
        return False
    