import kivy
kivy.require('2.0.0')
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.text import Label as CoreLabel, DEFAULT_FONT
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle, Color, InstructionGroup
from kivy.clock import Clock
from kivy.properties import (
    StringProperty, NumericProperty, BooleanProperty, ListProperty, 
    DictProperty, OptionProperty, ColorProperty, ObjectProperty
)
import re

class StreamLabel(Widget):
    """
    高性能流式文本渲染组件，使用独立小纹理渲染
    """
    # 字体相关属性
    font_size = NumericProperty('15sp')
    font_name = StringProperty(DEFAULT_FONT)
    color = ColorProperty([1, 1, 1, 1])
    halign = OptionProperty('left', options=['left', 'center', 'right', 'justify'])
    valign = OptionProperty('top', options=['top', 'middle', 'bottom'])
    padding = ListProperty([0, 0, 0, 0])
    markup = BooleanProperty(False)
    line_height = NumericProperty(1.0)
    mipmap = BooleanProperty(False)
    outline_width = NumericProperty(0)
    outline_color = ColorProperty([0, 0, 0, 1])
    bold = BooleanProperty(False)
    italic = BooleanProperty(False)
    underline = BooleanProperty(False)
    strikethrough = BooleanProperty(False)
    
    # 布局和尺寸属性
    char_spacing = NumericProperty(0)  # 字符间距
    line_spacing = NumericProperty(4)  # 行间距
    max_width = NumericProperty(800)  # 最大内容宽度
    clip_width = NumericProperty(300)  # 裁切窗口宽度
    clip_height = NumericProperty(400)  # 裁切窗口高度
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 文本存储结构
        self.text_chunks = []  # 存储文本块(单词或字符)
        self.char_groups = []  # 存储渲染指令组
        
        # 布局状态
        self.current_x = 0  # 当前行x位置
        self.current_y = 0  # 当前y位置
        self.max_line_height = 0  # 当前行最大高度
        self.content_height = 0  # 内容总高度
        
        # 绑定属性变化
        self.bind(
            font_size=self._mark_dirty,
            font_name=self._mark_dirty,
            color=self._mark_dirty,
            halign=self._mark_dirty,
            padding=self._mark_dirty,
            markup=self._mark_dirty,
            line_height=self._mark_dirty,
            max_width=self._mark_dirty,
            clip_width=self._mark_dirty,
            clip_height=self._mark_dirty,
            outline_width=self._mark_dirty,
            outline_color=self._mark_dirty,
            bold=self._mark_dirty,
            italic=self._mark_dirty,
            underline=self._mark_dirty,
            strikethrough=self._mark_dirty,
            char_spacing=self._mark_dirty,
            line_spacing=self._mark_dirty
        )
        
        # 初始渲染
        self._mark_dirty()
        Clock.schedule_interval(self._update_drawing, 1/60)  # 60FPS更新

    def _mark_dirty(self, *args):
        """标记需要重绘"""
        self.canvas.clear()
        with self.canvas:
            # 绘制背景
            Color(0.1, 0.1, 0.1, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        
        self._dirty = True

    def stream_text(self, text):
        """流式添加文本"""
        if not text:
            return
            
        # 分割为单词和空格
        words = re.split(r'(\s+)', text)
        for word in words:
            if word:
                self._render_and_add_word(word)
        
        # 标记需要重绘
        self._mark_dirty()

    def reset(self):
        """重置组件状态"""
        self.canvas.clear()
        with self.canvas:
            Color(0.1, 0.1, 0.1, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            
        self.text_chunks = []
        self.char_groups = []
        self.current_x = 0
        self.current_y = 0
        self.max_line_height = 0
        self.content_height = 0
        self._dirty = False

    def _estimate_word_size(self, text):
        """估算单词尺寸"""
        try:
            # 创建临时标签估算尺寸
            label = CoreLabel(
                text=text,
                font_size=self.font_size,
                font_name=self.font_name,
                bold=self.bold,
                italic=self.italic
            )
            label.refresh()
            return label.texture.size if label.texture else (0, 0)
        except:
            return (0, 0)

    def _render_word(self, text):
        """渲染单词纹理并返回尺寸和纹理"""
        try:
            label = CoreLabel(
                text=text,
                font_size=self.font_size,
                font_name=self.font_name,
                color=self.color,
                halign='left',  # 左对齐单个单词
                padding=self.padding,
                markup=self.markup,
                line_height=self.line_height,
                outline_width=self.outline_width,
                outline_color=self.outline_color,
                bold=self.bold,
                italic=self.italic,
                underline=self.underline,
                strikethrough=self.strikethrough
            )
            label.refresh()
            
            if label.texture:
                # 创建纹理 - 不再翻转纹理
                texture = label.texture
                return {
                    'texture': texture,
                    'size': texture.size
                }
        except Exception as e:
            print(f"Rendering error: {e}")
            
        return None

    def _render_and_add_word(self, word):
        """渲染单词并添加到显示流"""
        # 特殊处理换行
        if word == '\n':
            self._new_line()
            return
            
        # 渲染单词
        word_data = self._render_word(word)
        if not word_data:
            return
            
        # 获取单词尺寸
        w, h = word_data['size']
        
        # 检查是否超出当前行宽度
        if self.current_x + w > self.max_width:
            self._new_line()
            
        # 添加单词到当前行
        x = self.current_x
        y = self.height - self.current_y - h  # 修正y坐标计算
        
        # 创建指令组
        group = InstructionGroup()
        group.add(Color(1, 1, 1, 1))
        group.add(Rectangle(
            texture=word_data['texture'],
            pos=(self.x + x, self.y + y),
            size=word_data['size']
        ))
        
        # 存储信息
        self.text_chunks.append({
            'text': word,
            'x': x,
            'y': y,
            'width': w,
            'height': h,
            'group': group
        })
        self.char_groups.append(group)
        
        # 更新行状态
        self.current_x += w + self.char_spacing
        if h > self.max_line_height:
            self.max_line_height = h
            
    def _new_line(self):
        """开始新行"""
        self.current_x = 0
        self.current_y += self.max_line_height + self.line_spacing
        self.max_line_height = 0
        self.content_height = self.current_y

    def _update_drawing(self, dt):
        """更新绘制（60FPS）"""
        if not self._dirty:
            return
            
        # 更新背景位置
        self.bg_rect.pos = self.pos
        self.bg_rect.size = (self.clip_width, self.clip_height)
        
        # 添加所有文本块到画布
        for group in self.char_groups:
            self.canvas.add(group)
        
        # 标记更新完成
        self._dirty = False

# 测试应用 - 使用英文文本
class StreamLabelTestApp(App):
    def build(self):
        # 创建主布局
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # 创建控制面板
        control_panel = BoxLayout(size_hint=(1, None), height=50)
        
        # 添加控制按钮
        self.start_btn = Button(text="Start", on_press=self.start_stream)
        self.stop_btn = Button(text="Stop", on_press=self.stop_stream, disabled=True)
        self.reset_btn = Button(text="Reset", on_press=self.reset_label)
        
        control_panel.add_widget(self.start_btn)
        control_panel.add_widget(self.stop_btn)
        control_panel.add_widget(self.reset_btn)
        
        # 创建输入框 - 使用英文提示
        self.input_box = TextInput(
            hint_text="Enter text to stream", 
            size_hint=(1, None), 
            height=100,
            multiline=True
        )
        
        # 创建StreamLabel实例
        self.stream_label = StreamLabel(
            font_size=24,
            color=(0.9, 0.9, 0.9, 1),
            halign='left',
            valign='top',
            size_hint=(1, 1),
            padding=(10, 10),
            max_width=800,
            clip_width=400,
            clip_height=500,
            char_spacing=0,  # 修复字符间距问题
            line_spacing=4
        )
        
        # 创建性能显示 - 使用英文
        self.stats_label = Label(
            text="Ready",
            size_hint=(1, None),
            height=30,
            color=(0.7, 0.7, 0.7, 1)
        )
        
        # 添加所有部件
        layout.add_widget(control_panel)
        layout.add_widget(self.input_box)
        layout.add_widget(self.stream_label)
        layout.add_widget(self.stats_label)
        
        # 初始化流式输入状态
        self.is_streaming = False
        self.stream_index = 0
        self.chars_added = 0
        
        return layout
    
    def start_stream(self, instance):
        """开始流式输入"""
        if not self.input_box.text:
            self.stats_label.text = "Error: Input is empty"
            return
        
        self.is_streaming = True
        self.stream_index = 0
        self.chars_added = 0
        self.start_btn.disabled = True
        self.stop_btn.disabled = False
        self.stats_label.text = "Streaming..."
        
        # 设置流式更新定时器
        Clock.schedule_interval(self.add_next_char, 0.001)  # 1000字符/秒
    
    def stop_stream(self, instance):
        """停止流式输入"""
        self.is_streaming = False
        self.start_btn.disabled = False
        self.stop_btn.disabled = True
        Clock.unschedule(self.add_next_char)
        self.stats_label.text = f"Stopped. Added {self.chars_added} characters"
    
    def reset_label(self, instance):
        """重置标签"""
        self.stream_label.reset()
        self.stats_label.text = "Label reset"
        self.chars_added = 0
    
    def add_next_char(self, dt):
        """添加下一个字符"""
        if not self.is_streaming:
            return
        
        text = self.input_box.text
        if self.stream_index >= len(text):
            # 已添加完所有字符
            self.stop_stream(None)
            return
        
        # 获取下一个字符
        char = text[self.stream_index]
        self.stream_index += 1
        
        # 添加到流式标签
        self.stream_label.stream_text(char)
        self.chars_added += 1
        
        # 更新状态（每秒更新一次）
        if self.stream_index % 100 == 0:
            self.stats_label.text = f"Added {self.stream_index}/{len(text)} characters"

if __name__ == '__main__':
    StreamLabelTestApp().run()