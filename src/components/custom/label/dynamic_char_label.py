from kivy.clock import Clock
from collections import deque
from kivymd.uix.label import MDLabel

class DynamicCharLabel(MDLabel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = self.theme_cls.backgroundColor
        self.font_style = "STSONG"
        # 使用队列作为缓冲区
        self.buffer = deque()
        # 存储当前显示文本的副本
        self.current_text = self.text
        # 每帧添加/删除的字符数（恒定速率）
        self.chars_per_frame = 1  # 恒定速度，每帧处理1个字符
        # 添加字符的定时器事件
        self.add_event = None
        # 删除字符的定时器事件
        self.delete_event = None
        # 帧率
        self.frame_rate = 30  # 默认30帧/秒
    
    def add_text(self, text: str):
        """向缓冲区添加文本"""
        # 如果正在删除，清空缓冲区并停止删除
        if self.delete_event:
            self._stop_delete()
            self.buffer.clear()
        
        # 将文本分解为字符添加到队列
        for char in text:
            self.buffer.append(char)
        
        # 如果没有正在添加，开始添加过程
        if not self.add_event:
            self.start_adding()
    
    def start_adding(self):
        """开始添加缓冲区中的文本"""
        # 设置状态
        self.is_adding = True
        
        # 创建定时器，每帧执行一次添加操作
        self.add_event = Clock.schedule_interval(self._add_next_char, 1/self.frame_rate)
    
    def _add_next_char(self, dt):
        """添加缓冲区中的下一个字符（每帧调用）"""
        # 如果没有要添加的字符，结束添加过程
        if not self.buffer:
            self._finish_adding()
            return
        
        # 每次添加固定数量的字符
        for _ in range(min(self.chars_per_frame, len(self.buffer))):
            # 从队列前端取出字符
            char = self.buffer.popleft()
            # 更新当前文本和显示
            self.current_text += char
            self.text = self.current_text
        
        # 如果缓冲区为空，结束添加过程
        if not self.buffer:
            self._finish_adding()
    
    def _finish_adding(self):
        """完成添加过程"""
        # 重置状态
        self.is_adding = False
        # 取消定时器
        if self.add_event:
            self.add_event.cancel()
            self.add_event = None
    
    def delete_all(self):
        """开始删除所有文本"""
        # 如果正在添加，停止添加并清空缓冲区
        if self.add_event:
            self._finish_adding()
            self.buffer.clear()
        
        # 如果没有文本或已经在删除，直接返回
        if not self.current_text or self.delete_event:
            return
        
        # 创建定时器，每帧执行一次删除操作
        self.delete_event = Clock.schedule_interval(self._delete_chars, 1/self.frame_rate)
    
    def _delete_chars(self, dt):
        """删除字符（每帧调用）"""
        # 每次删除固定数量的字符
        chars_to_delete = min(self.chars_per_frame, len(self.current_text))
        
        # 如果没有需要删除的字符，结束删除过程
        if chars_to_delete <= 0:
            self._finish_deleting()
            return
        
        # 删除字符并更新显示
        self.current_text = self.current_text[:-chars_to_delete]
        self.text = self.current_text
        
        # 如果所有文本都已删除，结束删除过程
        if not self.current_text:
            self._finish_deleting()
    
    def _finish_deleting(self):
        """完成删除过程"""
        if self.delete_event:
            self.delete_event.cancel()
            self.delete_event = None
    
    def set_frame_rate(self, frame_rate: int):
        """设置帧率（字符处理速度）"""
        self.frame_rate = frame_rate
        # 更新添加定时器
        if self.add_event:
            self.add_event.cancel()
            self.start_adding()
        # 更新删除定时器
        if self.delete_event:
            self.delete_event.cancel()
            self.delete_event = Clock.schedule_interval(self._delete_chars, 1/self.frame_rate)
    
    def set_chars_per_frame(self, count: int):
        """设置每帧处理的字符数（影响速度）"""
        if count > 0:
            self.chars_per_frame = count
    
    def clear(self):
        """立即清除所有文本"""
        # 停止所有动画
        self._finish_adding()
        self._finish_deleting()
        # 清空缓冲区和当前文本
        self.buffer.clear()
        self.current_text = ""
        self.text = ""