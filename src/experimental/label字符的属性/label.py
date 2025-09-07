from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.core.text import Label as CoreLabel
from kivy.core.text.text_layout import LayoutWord
import random
from kivy.metrics import dp

class LineDebugLabel(Label):
    """只绘制行级布局信息的标签"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._debug_draw = True
        self.bind(text=self.on_text_debug)
        
    def on_text_debug(self, instance, value):
        """当文本改变时更新调试绘制"""
        if self._debug_draw:
            self.update_debug_drawing()
    
    def update_debug_drawing(self, *args):
        """更新行级调试绘制"""
        # 清除之前的绘制
        self.canvas.after.clear()
        
        # 确保文本布局已完成
        self.texture_update()
        
        # 检查是否有可用的布局信息
        if not hasattr(self, '_label') or not hasattr(self._label, '_cached_lines'):
            return
        
        # 获取文本在标签中的位置
        texture_x = self.center_x - self.texture_size[0] / 2
        texture_y = self.center_y - self.texture_size[1] / 2
        
        # 计算累计行高
        total_height = 0
        
        with self.canvas.after:
            # 遍历所有行
            for line in self._label._cached_lines:
                # 计算行在标签中的实际位置
                line_x = texture_x + line.x
                line_y = texture_y + self.texture_size[1] - total_height - line.h
                
                # 随机生成半透明颜色
                r = random.random()
                g = random.random()
                b = random.random()
                
                # 绘制行边界框（随机半透明颜色）
                Color(r, g, b, 0.5)  # 半透明
                Rectangle(pos=(line_x, line_y), size=(line.w, line.h))
                
                # 更新累计行高
                total_height += line.h
                
                # # 添加行间距（如果有）
                # if line != self._label._cached_lines[-1]:  # 不是最后一行
                #     line_spacing = self._label.get_extents('\n')[1]  # 行高
                #     total_height += line_spacing

class WordDebugLabel(Label):
    """只绘制单词级布局信息的标签"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._debug_draw = True
        self.bind(text=self.on_text_debug)
        
    def on_text_debug(self, instance, value):
        """当文本改变时更新调试绘制"""
        if self._debug_draw:
            self.update_debug_drawing()
    
    def update_debug_drawing(self, *args):
        """更新单词级调试绘制"""
        # 清除之前的绘制
        self.canvas.after.clear()
        
        # 确保文本布局已完成
        self.texture_update()
        
        # 检查是否有可用的布局信息
        if not hasattr(self, '_label') or not hasattr(self._label, '_cached_lines'):
            return
        
        # 获取文本在标签中的位置
        texture_x = self.center_x - self.texture_size[0] / 2
        texture_y = self.center_y - self.texture_size[1] / 2
        
        # 计算累计行高
        total_height = 0
        
        with self.canvas.after:
            # 遍历所有行
            for line in self._label._cached_lines:
                # 计算行在标签中的实际位置
                line_x = texture_x + line.x
                line_y = texture_y + self.texture_size[1] - total_height - line.h
                print(len(self._label._cached_lines))
                print(len(line.words))
                # 遍历行中的每个单词
                word_x = line_x
                for word in line.words:
                    
                    print(word.text)

                    # 计算单词在标签中的实际位置
                    word_y = line_y
                    
                    # 随机生成半透明颜色
                    r = random.random()
                    g = random.random()
                    b = random.random()
                    
                    # 绘制单词边界框（随机半透明颜色）
                    Color(r, g, b, 0.5)  # 半透明
                    Rectangle(pos=(word_x, word_y), size=(word.lw, word.lh))
                    
                    # 移动到下一个单词位置
                    word_x += word.lw
                
                # 更新累计行高
                total_height += line.h

class CharDebugLabel(Label):
    """只绘制字符级布局信息的标签"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._debug_draw = True
        self.bind(text=self.on_text_debug)
        
    def on_text_debug(self, instance, value):
        """当文本改变时更新调试绘制"""
        if self._debug_draw:
            self.update_debug_drawing()
    
    def update_debug_drawing(self, *args):
        """更新字符级调试绘制"""
        # 清除之前的绘制
        self.canvas.after.clear()
        
        # 确保文本布局已完成
        self.texture_update()
        
        # 检查是否有可用的布局信息
        if not hasattr(self, '_label') or not hasattr(self._label, '_cached_lines'):
            return
        
        # 获取文本在标签中的位置
        texture_x = self.center_x - self.texture_size[0] / 2
        texture_y = self.center_y - self.texture_size[1] / 2
        
        # 计算累计行高
        total_height = 0
        
        with self.canvas.after:
            # 遍历所有行
            for line in self._label._cached_lines:
                # 计算行在标签中的实际位置
                line_x = texture_x + line.x
                line_y = texture_y + self.texture_size[1] - total_height - line.h
                
                # 遍历行中的每个单词
                char_x = line_x
                for word in line.words:
                    # 遍历单词中的每个字符
                    for char in word.text:
                        # 获取字符尺寸
                        char_size = self._label.get_extents(char)
                        
                        # 计算字符在标签中的实际位置
                        char_y = line_y
                        
                        # 随机生成半透明颜色
                        r = random.random()
                        g = random.random()
                        b = random.random()
                        
                        # 绘制字符边界框（随机半透明颜色）
                        Color(r, g, b, 0.5)  # 半透明
                        Rectangle(
                            pos=(char_x, char_y), 
                            size=(char_size[0], char_size[1])
                        )
                        
                        # 移动到下一个字符位置
                        char_x += char_size[0]
                
                # 更新累计行高
                total_height += line.h
                
from kivy.uix.button import Button

class TestApp(App):
    def build(self):
        # 创建一个测试布局
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # 创建测试文本
        test_text = "Hello World\nThis is a test\nWith multiple lines,123._api break"
        
        # 创建行级调试标签
        line_label = LineDebugLabel(
            text="line\n" + test_text,
            font_size=24,
            halign='left',
            valign='middle',
            size_hint=(1, 0.3),
            height=dp(200)
        )
        
        # 创建单词级调试标签
        word_label = WordDebugLabel(
            text="word:\n" + test_text,
            font_size=24,
            halign='left',
            valign='middle',
            size_hint=(1, 0.3),
            height=dp(200),
        )
        
        # 创建字符级调试标签
        char_label = CharDebugLabel(
            text="char:\n" + test_text,
            font_size=24,
            halign='left',
            valign='middle',
            size_hint=(1, 0.3),
            height=dp(200)
        )
        
        # 添加到布局
        layout.add_widget(line_label)
        layout.add_widget(word_label)
        layout.add_widget(char_label)
        button = Button(size_hint=(1, 0.1))

        button.bind(on_release=lambda x: line_label.update_debug_drawing())
        button.bind(on_release=lambda x: word_label.update_debug_drawing())
        button.bind(on_release=lambda x: char_label.update_debug_drawing())
        layout.add_widget(button)

        return layout

if __name__ == '__main__':
    TestApp().run()