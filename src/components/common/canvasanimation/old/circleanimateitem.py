from kivy.properties import  NumericProperty, ColorProperty
from kivy.graphics import Color, Ellipse
from .animateitembase import AnimateItemBase
import math

class CircleAnimateItem(AnimateItemBase):
    """圆形波动画项"""
    # 定义属性
    circle_count = NumericProperty(4)
    min_radius = NumericProperty(10)
    max_radius = NumericProperty(60)
    pulse_speed = NumericProperty(1.0)
    circle_color = ColorProperty([0.2, 0.6, 1, 0.5])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_circles()
        self.circle_color=self.theme_cls.primaryColor
        self.md_bg_color=self.theme_cls.backgroundColor
        self.circle_instructions = []
        self.max_radius = min(self.width, self.height) / 2
        #self._create_circle_instructions()

    def on_size(self, instance, value):
        self.max_radius = min(self.width, self.height) / 2

    def clear(self):
        super().clear()
        self.circle_instructions = []

    def start(self):
        if len(self.circle_instructions)==0:
            self._create_circle_instructions()
        super().start()
        
    def _init_circles(self):
        """初始化圆环参数"""
        self.circle_phases = [i / self.circle_count for i in range(self.circle_count)]
        self.circle_alphas = [0.8 - (i * 0.8 / self.circle_count) for i in range(self.circle_count)]
    
    def _create_circle_instructions(self):
        """创建并缓存图形指令"""
        diameter = min(self.width, self.height)
    
        with self.canvas:
            for i in range(self.circle_count):
                # 创建颜色指令
                Color(*self.circle_color[:3], self.circle_alphas[i])
                # 创建圆形指令
                progress = (math.sin(self.circle_phases[i] * 2 * math.pi) + 1) / 2
                radius = self.min_radius + (self.max_radius - self.min_radius) * progress
                radius = min(radius, diameter/2)  # 不超过自身尺寸
                ellipse_instr = Ellipse(pos=self.center,size=(radius,radius))
                # 存储指令引用
                self.circle_instructions.append(ellipse_instr)
    
    def update(self, dt):
        """更新圆环相位和图形属性"""
        if self.is_paused:
            return
        for i in range(self.circle_count):
            self.circle_phases[i] += dt * self.pulse_speed
            if self.circle_phases[i] > 1:
                self.circle_phases[i] -= 1
        
        # 直接更新图形属性，避免清除和重绘整个画布
        self._update_circle_properties()
    
    def _update_circle_properties(self):
        """更新圆形指令的属性"""
        diameter = min(self.width, self.height)
        if len(self.circle_instructions)==0:
            print("_update_circle_properties: circle_instructions is empty")
            return
        for i in range(self.circle_count):
            instr= self.circle_instructions[i]
            # 计算当前圆环的半径和位置
            progress = (math.sin(self.circle_phases[i] * 2 * math.pi) + 1) / 2
            radius = self.min_radius + (self.max_radius - self.min_radius) * progress
            radius = min(radius, diameter/2)
            
            # 更新圆形指令的位置和尺寸
            instr.pos = (self.center[0]-radius, self.center[1]-radius)
            instr.size = (radius * 2, radius * 2)
    
    def draw(self):
        """更新图形属性（现在只是更新现有指令）"""
        # self._update_circle_properties()
        pass
    
    def update_theme(self, instance, value):
        """主题更新处理"""
        self.circle_color = self.theme_cls.primaryColor
        # 更新所有圆环的颜色
        self.clear()
        self._create_circle_instructions()
