from .animateitembase import AnimateItemBase
from kivy.graphics import Rectangle, Color
from kivy.animation import Animation
from kivy.properties import NumericProperty, ListProperty
import random
from kivy.clock import Clock

class WaveLoop(AnimateItemBase):
    """矩阵波浪运动循环（基于动画阶段管理）"""
    rect_count = NumericProperty(15)
    min_height = NumericProperty(30)
    max_height = NumericProperty(150)
    wave_speed = NumericProperty(1.0)
    colors = ListProperty([[0.2, 0.5, 0.8, 0.2], [0.3, 0.7, 0.9, 0.3]])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas)
    
    def create_initial_graphics(self):
        """创建初始矩阵图形"""
        self.add_dynamic_data()
        self.update_canvas()
    
    def update_canvas(self, *args):
        """
        更新所有矩形的位置和大小
        如果不清理资源,则会影响图形对象的属性,因为位置是通过i计算的
        没用考虑宽度和动画情况,所以会导致图形对象的属性错误
        """
        if not self._graphic_items:
            return
            
        width = self.width / self.rect_count
        for i, graphic in enumerate(self._graphic_items):
            # 只更新矩形的位置和宽度，高度由动画控制
            graphic.graphic.pos = (self.x + i * width, self.y)
            graphic.graphic.size = (width, graphic.graphic.size[1])
    
    def add_dynamic_data(self, dt=None):
        """添加新的波浪矩阵项"""
        # 计算每个矩形的宽度
        width = self.width / self.rect_count
        
        # 为每个矩形创建动画
        for i in range(self.rect_count):
            # 随机基础高度和波动速度
            base_height = random.uniform(self.min_height, self.max_height)
            speed = random.choice([0.5, 0.8, 1.2, 1.5]) * self.wave_speed
            
            # 计算动画周期 (2π / speed)
            cycle_duration = 2 * 3.14159 / speed
            
            # 选择颜色
            color = self.colors[i % len(self.colors)]
            
            # 创建矩阵图形
            proxy = self.create_color_shape_pair(
                rgba=color,
                shape_type=Rectangle,
                pos=(self.x + i * width, self.y),
                size=(width, 0)  # 初始高度
            )
            start_anim = Animation(
                h=base_height * 0.5,  # 从0到一半高度
                duration=cycle_duration/2,  # 持续时间
                t='in_out_sine'  # 缓动效果
            )
            # 定义波动动画 (循环动画)
            # 动画周期分为两部分：上升和下降
            loop_anim = Animation(
                h=base_height,  # 到峰值高度
                duration=cycle_duration / 2,
                t='in_out_sine'
            )+Animation(
                h=base_height * 0.5,  # 到谷值高度
                duration=cycle_duration / 2,
                t='in_out_sine'
            )
            
            #loop_anim.repeat = True
            
            end_anim = Animation(
                h=0,  # 到0高度
                duration=cycle_duration,  # 持续时间
                t='in_out_sine'  # 缓动效果
            )
            # 添加到基类管理（无开始/结束动画）
            self.add_graphic(
                graphic=proxy,
                start_anim=start_anim,
                loop_anim=loop_anim,
                end_anim=end_anim,
                auto_remove=True,  # 自动移除
            )
