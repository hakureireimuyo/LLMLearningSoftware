from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.button import Button
from kivy.metrics import dp, sp
from kivy.clock import Clock
import random
import time
import sys
from pathlib import Path

# 自动添加项目根目录和 src 目录
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / "src"))
from src.app import TestApp

class StreamWidthLabel(MDLabel):
    """自定义标签，实现增量宽度计算"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._last_text = ""
        self._last_max_width = 0
        self._last_line_width = 0
        
    def incremental_calc_width(self, new_text):
        """增量计算文本最大宽度"""
        if not hasattr(self, '_label') or self._label is None:
            return 0
        # 如果文本被重置（长度变短），重新计算
        old_text = self._last_text
        
        if len(new_text) < len(old_text):
            self._last_text = ""
            self._last_max_width = 0
            self._last_line_width = 0
            old_text = ""
        
        # 增量计算新增部分的宽度
        start_index = len(old_text)
        max_width = self._last_max_width
        current_line_width = self._last_line_width
        
        # 处理新增文本
        for char in new_text[start_index:]:
            if char == "\n":
                # 换行时更新最大宽度
                max_width = max(max_width, current_line_width)
                current_line_width = 0
            else:
                # 获取字符宽度
                char_width = self._label.get_extents(char)[0]
                current_line_width += char_width
        
        # 更新缓存值
        self._last_text = new_text
        self._last_max_width = max(max_width, current_line_width)
        self._last_line_width = current_line_width

        return self._last_max_width
    
    def full_calc_width(self, text):
        """完整重新计算文本宽度（作为基准）"""
        if not hasattr(self, '_label') or self._label is None:
            return 0
        width = 0
        max_width = 0
        
        for char in text:
            if char == "\n":
                max_width = max(max_width, width)
                width = 0
            else:
                char_width = self._label.get_extents(char)[0]
                width += char_width
        
        # 最后一行也需要比较
        max_width = max(max_width, width)
        return max_width


class StreamWidthCalculatorTest(TestApp):
    def build(self):
        self.layout = MDBoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        
        # 创建自定义标签实例（用于测量）
        self.test_label = StreamWidthLabel(
            font_name="STSONG",
            font_size=sp(16),
            halign="left",
            valign="top"
        )
        
        # 控制面板
        self.control_panel = MDBoxLayout(size_hint=(1, None), height=dp(50), spacing=dp(10))
        self.start_btn = Button(text="开始流式测试",font_name="STSONG", on_release=self.start_stream_test)
        self.pause_btn = Button(text="暂停测试",font_name="STSONG", on_release=self.toggle_pause, disabled=True)
        self.control_panel.add_widget(self.start_btn)
        self.control_panel.add_widget(self.pause_btn)
        
        # 状态面板
        self.status_label = MDLabel(
            text="就绪，点击'开始流式测试'按钮开始",
            halign="center",
            font_style="STSONG",
            adaptive_size=True,
            size_hint_y=None,
            height=dp(50),
            md_bg_color=(1,1,1,0.5)

        )
        
        # 结果统计标签
        self.results_label = MDLabel(
            text="",
            halign="center",
            font_style="STSONG",
            adaptive_size=True,
            size_hint_y=None,
            height=dp(60),
            md_bg_color=(1,1,1,0.5)
        )
        
        self.layout.add_widget(self.control_panel)
        self.layout.add_widget(self.status_label)
        self.layout.add_widget(self.results_label)
        
        # 测试状态
        self.testing = False
        self.paused = False
        self.current_text = ""
        self.char_count = 0
        self.incremental_errors = 0
        self.incremental_error_rate = 0.0
        self.total_chars = 0
        self.start_time = 0
        self.last_update_time = 0
        
        return self.layout
    
    def start_stream_test(self, *args):
        self.testing = True
        self.paused = False
        self.start_btn.disabled = True
        self.pause_btn.disabled = False
        self.pause_btn.text = "暂停测试"
        self.status_label.text = "流式测试进行中..."
        self.current_text = ""
        self.char_count = 0
        self.incremental_errors = 0
        self.total_chars = 0
        self.start_time = time.time()
        self.last_update_time = self.start_time
        
        # 重置标签状态
        self.test_label._last_text = ""
        self.test_label._last_max_width = 0
        self.test_label._last_line_width = 0
        
        # 开始流式测试
        Clock.schedule_interval(self.stream_next_char, 0.01)
    
    def toggle_pause(self, *args):
        self.paused = not self.paused
        self.pause_btn.text = "继续测试" if self.paused else "暂停测试"
        self.status_label.text = "测试已暂停" if self.paused else "流式测试进行中..."
    
    def stream_next_char(self, dt):
        if not self.testing or self.paused:
            return
        
        # 随机决定添加中文、英文还是换行符
        char_type = random.random()
        if char_type < 0.85:  # 85%概率添加中文字符
            char = chr(random.randint(0x4E00, 0x9FA5))
        elif char_type < 0.95:  # 10%概率添加英文字符
            char = chr(random.randint(97, 122))
        else:  # 5%概率添加换行符
            char = '\n'
        
        # 添加到当前文本
        self.current_text += char
        self.char_count += 1
        self.total_chars += 1
        
        # 使用自定义标签计算宽度
        incremental_width = self.test_label.incremental_calc_width(self.current_text)
        full_width = self.test_label.full_calc_width(self.current_text)
        
        # 检查差异
        diff = abs(incremental_width - full_width)
        if diff > 1:  # 允许1像素的误差（可能是浮点计算误差）
            self.incremental_errors += 1
        
        # 更新错误率
        self.incremental_error_rate = self.incremental_errors / self.total_chars * 100
        
        # 每50个字符在控制台输出一次结果
        if self.char_count >= 50:
            self.print_console_result(self.total_chars, incremental_width, full_width, diff)
            self.char_count = 0
        
        # 每0.5秒更新UI状态
        current_time = time.time()
        if current_time - self.last_update_time >= 0.5:
            elapsed_time = current_time - self.start_time
            chars_per_sec = self.total_chars / elapsed_time if elapsed_time > 0 else 0
            
            self.status_label.text = (
                f"流式测试进行中... 已处理字符: {self.total_chars}\n"
                f"速度: {chars_per_sec:.1f} 字符/秒"
            )
            
            self.results_label.text = (
                f"增量算法错误: {self.incremental_errors} ({self.incremental_error_rate:.2f}%)\n"
                f"当前平均误差: {diff:.4f} 像素"
            )
            
            self.last_update_time = current_time
        
        # 达到2000个字符后结束测试
        if self.total_chars >= 2000:
            self.stop_test()
    
    def print_console_result(self, char_count, incremental_width, full_width, diff):
        """在控制台输出结果"""
        print(f"\n--- 测试点 ({char_count} 字符) ---")
        print(f"增量计算结果: {incremental_width:.2f} 像素")
        print(f"全量计算结果: {full_width:.2f} 像素")
        print(f"差异: {diff:.4f} 像素")
        if diff > 1:
            print("⚠️ 检测到显著差异！")
    
    def stop_test(self):
        self.testing = False
        Clock.unschedule(self.stream_next_char)
        self.start_btn.disabled = False
        self.pause_btn.disabled = True
        self.status_label.text = f"测试完成！共处理 {self.total_chars} 个字符"
        
        elapsed_time = time.time() - self.start_time
        chars_per_sec = self.total_chars / elapsed_time if elapsed_time > 0 else 0
        
        self.results_label.text = (
            f"测试结果:\n"
            f"总字符数: {self.total_chars}\n"
            f"增量算法错误次数: {self.incremental_errors}\n"
            f"错误率: {self.incremental_error_rate:.2f}%\n"
            f"处理速度: {chars_per_sec:.1f} 字符/秒"
        )
        
        # 在控制台输出最终摘要
        print("\n" + "="*50)
        print("测试摘要:")
        print(f"总字符数: {self.total_chars}")
        print(f"增量计算错误次数: {self.incremental_errors}")
        print(f"错误率: {self.incremental_error_rate:.4f}%")
        print(f"平均处理速度: {chars_per_sec:.1f} 字符/秒")
        print("="*50)

if __name__ == "__main__":
    StreamWidthCalculatorTest().run()