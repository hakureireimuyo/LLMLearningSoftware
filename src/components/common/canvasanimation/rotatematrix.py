from .animateitembase import AnimateItemBase
from kivy.properties import NumericProperty, ColorProperty, ListProperty
from kivy.graphics import Rectangle, Color
import random
from kivy.animation import Animation


class RotateMatrixAnimated(AnimateItemBase):
    """半透明矩阵旋转动画项"""
    bar_width_min = NumericProperty(10)  # 矩阵最小宽度
    bar_width_max = NumericProperty(40)  # 矩阵最大宽度

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def create_initial_graphics(self):
        """初始创建一组矩阵"""
        # 创建矩形图形
        proxy = self.create_color_shape_pair(
            rgba=self.theme_cls.primaryColor,
            shape_type=Rectangle,
            pos=(100, 100), 
            size=(100, 100),
            angle=0  # 初始角度为0
        )

        loop_anim = Animation(angle=180, duration=2)+Animation(angle=360, duration=2)  # 回到初始角度
        loop_anim.repeat = True  # 无限循环

        # 添加到基类管理（无开始/结束动画）
        self.add_graphic(
            graphic=proxy,
            loop_anim=loop_anim,
            auto_remove=False  # 自动移除
        )