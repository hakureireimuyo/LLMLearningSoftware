from kivy.graphics import Rectangle
from kivy.animation import Animation
import random
from .animateitembase import AnimateItemBase
from kivy.properties import NumericProperty, ColorProperty
from line_profiler import LineProfiler
profiler = LineProfiler()

class RisingMatrix(AnimateItemBase):
    """矩阵上升浮动动画项"""
    bar_width = NumericProperty(4)  # 矩阵宽度
    bar_spacing = NumericProperty(1)  # 矩阵间距
    min_height = NumericProperty(20)  # 矩阵最小高度
    max_height = NumericProperty(100)  # 矩阵最大高度
    rise_duration = NumericProperty(1.5)  # 上升动画持续时间
    float_duration = NumericProperty(2.0)  # 浮动动画持续时间
    fade_duration = NumericProperty(0.5)  # 淡出动画持续时间
    float_range = NumericProperty(20)  # 浮动范围
    base_color = ColorProperty([0.2, 0.6, 1, 0.7])  # 基础颜色
    color_variation = NumericProperty(0.1)  # 颜色变化范围
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bar_count = 0  # 矩阵数量
        self.base_color = self.theme_cls.primaryColor
    
    def update_theme(self, instance, value):
        """主题更新处理"""
        self.base_color = self.theme_cls.primaryColor
        self._update_colors()
    
    def create_initial_graphics(self):
        """创建初始矩阵"""
        # 计算可容纳的矩阵数量
        self.bar_count = self._calculate_bar_count()
        
        # 创建矩阵
        for i in range(self.bar_count):
            self.add_bar(i)
    
    def _calculate_bar_count(self):
        """计算可容纳的矩阵数量"""
        if self.width <= 0:
            return 0
        return max(1, int((self.width - self.bar_spacing) / (self.bar_width + self.bar_spacing)))
    
    def add_bar(self, index):
        """添加一个新的矩阵"""
        # 计算位置
        x = self.x + index * (self.bar_width + self.bar_spacing)
        y = self.y  # 起始位置在底部
        
        # 随机高度
        target_height = random.uniform(self.min_height, self.max_height)
        
        # 随机颜色
        r = max(0, min(1, self.base_color[0] + random.uniform(-self.color_variation, self.color_variation)))
        g = max(0, min(1, self.base_color[1] + random.uniform(-self.color_variation, self.color_variation)))
        b = max(0, min(1, self.base_color[2] + random.uniform(-self.color_variation, self.color_variation)))
        a = random.uniform(0.5, 0.8)  # 随机透明度
        
        # 创建图形代理
        proxy = self.create_color_shape_pair(
            rgba=(r, g, b, 0),  # 初始完全透明
            shape_type=Rectangle,
            pos=(x, y),
            size=(self.bar_width, 0)  # 初始高度为0
        )
        # 开启动画 - 上升并淡入
        start_anim = Animation(
            size=(self.bar_width, target_height),
            pos=(x, self.y + target_height),
            rgba=(r, g, b, a),
            duration=self.rise_duration,
            t='out_quad'
        )
        
        # 循环动画 - 上下浮动
        float_height = random.uniform(target_height - self.float_range, target_height + self.float_range)
        loop_anim = Animation(
            size=(self.bar_width, float_height),
            pos=(x, self.y + float_height),
            duration=self.float_duration * 0.5,
            t='in_out_sine'
        ) + Animation(
            size=(self.bar_width, target_height),
            pos=(x, self.y + target_height),
            duration=self.float_duration * 0.5,
            t='in_out_sine'
        )
        loop_anim.repeat = True
        
        # 结束动画 - 下降并淡出
        end_anim = Animation(
            size=(self.bar_width, 0),
            pos=(x, self.y),
            rgba=(r, g, b, 0),
            duration=self.fade_duration,
            t='in_quad'
        )
        
        # 添加图形项
        self.add_graphic(
            graphic=proxy,
            start_anim=start_anim,
            loop_anim=loop_anim,
            end_anim=end_anim,
            auto_remove=False
        )
    
    def _update_colors(self):
        """更新所有矩阵颜色"""
        for i, item in enumerate(self._graphic_items):
            if hasattr(item.graphic, 'rgba'):
                # 保留原始颜色的RGB，但使用基础颜色的变化
                r = max(0, min(1, self.base_color[0] + random.uniform(-self.color_variation, self.color_variation)))
                g = max(0, min(1, self.base_color[1] + random.uniform(-self.color_variation, self.color_variation)))
                b = max(0, min(1, self.base_color[2] + random.uniform(-self.color_variation, self.color_variation)))
                a = item.graphic.rgba[3]  # 保持当前透明度
                item.graphic.rgba = (r, g, b, a)
    
    def add_dynamic_data(self, data=None):
        """动态添加新矩阵"""
        # 如果有空闲位置，添加到空闲位置
        if len(self._graphic_items) < self.bar_count:
            self.add_bar(len(self._graphic_items))
    
    def _on_layout_change(self, instance, value):
        """布局变化时更新所有矩阵"""
        super()._on_layout_change(instance, value)

