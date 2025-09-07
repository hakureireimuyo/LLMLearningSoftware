from kivy.properties import  NumericProperty, ColorProperty
from kivy.graphics import Color, Rectangle
from time import time
from .animateitembase import AnimateItemBase
from core.signalprocessing import ExponentialSmoothing

class BarAnimateItem(AnimateItemBase):
    """柱状图动画项 - 使用图形指令列表优化"""
    # 定义属性（自动绑定事件系统）
    frequency = NumericProperty(30) # 每秒更新频率
    time_window = NumericProperty(0.0638) # 时间窗口
    spacing = NumericProperty(1)    # 柱体间距
    animation_duration = NumericProperty(0.5)    # 动画持续时间
    fade_duration = NumericProperty(0.1)        # 消失动画持续时间
    bar_color = ColorProperty([0.2, 0.6, 1, 0.5])    # 柱体颜色
    bar_width = NumericProperty(10)  # 柱体数量

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bars = []  # 存储柱体数据
        self.bar_instructions = []  # 存储图形指令
        self._pending_value = None
        self._last_generate_time = time()
        self.bar_color = self.theme_cls.primaryColor
        self.md_bg_color = self.theme_cls.backgroundColor
        self.animation_speed = (self.bar_width + self.spacing) * self.frequency
        self.bar_interval = 1 / self.frequency
        self._smoother = ExponentialSmoothing(alpha=0.2)  # 指数平滑器


    def update_theme(self, instance, value):
        """更新主题颜色"""
        self.bar_color = self.theme_cls.primaryColor
        self.md_bg_color = self.theme_cls.backgroundColor
        self._update_bar_colors()

    def _update_bar_colors(self):
        """更新所有柱体颜色"""
        for bar, instr in zip(self.bars, self.bar_instructions):
            instr['color'].rgba = (*self.bar_color[:3], bar['color'][3])  # 保持原有透明度

    def add_item(self, value):
        """添加新值（柱体高度）"""
        max_height = self.height / 2
        value=self._smoother.smooth(value)  # 应用指数平滑
        self._pending_value = min(value, max_height) if value else None

    def clear(self):
        """清除所有柱体和图形指令"""
        super().clear()
        self.bars = []
        self.bar_instructions = []

    def start(self):
        """启动动画"""
        if not self.bar_instructions:
            self._create_bar_instructions()
        super().start()

    def _create_bar_instructions(self):
        """创建并缓存图形指令"""
        with self.canvas:
            for bar in self.bars:
                # 创建颜色指令
                color_instr = Color(*bar['color'])
                # 创建矩形指令
                rect_instr = Rectangle(
                    pos=(bar['x'], self.center_y - bar['height']/2),
                    size=(self.bar_width, bar['height'])
                )
                self.bar_instructions.append({
                    'color': color_instr,
                    'rect': rect_instr
                })

    def update(self, dt):
        """更新柱体状态"""
        if self.is_paused:
            return
        current_time = time()

        # 1. 生成新柱体
        detal_time = current_time - self._last_generate_time
        if detal_time >= self.bar_interval:
            if self._pending_value is None or not isinstance(self._pending_value, (int, float)):
                self._pending_value = 1
            detal_x=max(detal_time*self.animation_speed-self.bar_width,self.bar_width)
            new_bar = {
                'x': self.right-detal_x,
                'start_time': current_time,
                'target_height': self._pending_value,
                'height': 0,
                'color': (*self.bar_color[:3], 1.0),  # 初始透明度1.0
                'state': 'growing',
                'fade_start_time': 0
            }
            self.bars.append(new_bar)
            
            # 为新柱体创建图形指令
            with self.canvas:
                color_instr = Color(*new_bar['color'])
                rect_instr = Rectangle(
                    pos=(new_bar['x'], self.center_y - new_bar['height']/2),
                    size=(self.bar_width, new_bar['height'])
                )
                self.bar_instructions.append({
                    'color': color_instr,
                    'rect': rect_instr
                })
            self._last_generate_time = current_time

        # 2. 更新现有柱体状态
        bars_to_remove = []
        for idx, bar in enumerate(self.bars):
            bar['x'] -= self.animation_speed * dt
            instr = self.bar_instructions[idx]
            
            # 移出左边界检测
            if bar['x'] < self.x + self.bar_width*3 and bar['state'] != 'fading':
                bar['state'] = 'fading'
                bar['fade_start_time'] = current_time
            
            # 状态处理
            if bar['state'] == 'growing':
                elapsed = current_time - bar['start_time']
                progress = min(elapsed / self.animation_duration, 1.0)
                bar['height'] = bar['target_height'] * progress
            elif bar['state'] == 'fading':
                elapsed = current_time - bar['fade_start_time']
                progress = min(elapsed / self.fade_duration, 1.0)
                bar['height'] = bar['target_height'] * (1 - progress)
                # 更新透明度 wocao,颜色指令适合图像绑定的
                alpha = 1.0 - progress
                bar['color'] = (*bar['color'][:3], alpha)
                instr['color'].rgba = bar['color']
                
                if progress >= 1.0:
                    bars_to_remove.append((idx, bar))
            
            # 更新矩形位置和大小
            instr['rect'].pos = (bar['x'], self.center_y- bar['height']/2)
            instr['rect'].size = (self.bar_width, bar['height'])
        
        # 3. 移除已消失柱体（从后往前移除）
        for idx_bar in sorted([idx for idx, _ in bars_to_remove], reverse=True):
            bar = self.bars.pop(idx_bar)
            instr = self.bar_instructions.pop(idx_bar)
            
            # 从画布中移除图形指令
            self.canvas.remove(instr['color'])
            self.canvas.remove(instr['rect'])