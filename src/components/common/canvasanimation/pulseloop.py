from kivy.graphics import Ellipse
from kivy.animation import Animation
from kivy.properties import NumericProperty, ColorProperty
from .animateitembase import AnimateItemBase

class PulseCircle(AnimateItemBase):
    """脉冲圆形动画项 - 支持动态添加"""
    min_radius = NumericProperty(20)
    max_radius = NumericProperty(180)
    pulse_duration = NumericProperty(2.0)
    circle_color = ColorProperty([0.2, 0.6, 1, 0.7])
    color_opacity = NumericProperty(0.3)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.circle_color=self.theme_cls.primaryColor
        
    def update_theme(self, instance, value):
        """主题更新处理"""
        self.circle_color=self.theme_cls.primaryColor
        self._update_color((*self.circle_color[:3],self.color_opacity))
    
    def create_initial_graphics(self):
        """创建初始圆形"""
        for i in range(4):
            self.add_circle(i+1)
        
    def add_circle(self,num=1):
        """添加新圆形"""
        # 初始半径
        radius = (self.min_radius + self.max_radius) / 2
        
        # 创建图形代理
        #随机颜色
        # color=[random.random() for i in range(3)]
        proxy = self.create_color_shape_pair(
            rgba=(*self.circle_color[:3],self.color_opacity),
            shape_type=Ellipse,
            pos=(self.center_x-radius, self.center_y-radius),
            size=(radius*2, radius*2)
        )
        # 创建动画
        start_anim = Animation(
            size=(self.min_radius*2, self.min_radius*2),
            pos=(self.center_x, self.center_y),
            rgba=(*self.circle_color[:3],self.color_opacity),
            duration=0.3*num
        )
        
        loop_anim = Animation(
            size=(self.max_radius*2, self.max_radius*2),
            pos=(self.center_x-self.max_radius, self.center_y-self.max_radius),
            duration=self.pulse_duration/2,
            t='out_quad'
        ) + Animation(
            size=(self.min_radius*2, self.min_radius*2),
            pos=(self.center_x-self.min_radius, self.center_y-self.min_radius),
            duration=self.pulse_duration/2,
            t='in_quad'
        )
        loop_anim.repeat = True
        
        end_anim = Animation(
            rgba=(*self.circle_color[:3], 0),
            size=(self.min_radius*2, self.min_radius*2),
            pos=(self.center_x-self.min_radius, self.center_y-self.min_radius),
            duration=0.5
        )
        
        # 添加图形项
        self.add_graphic(
            graphic=proxy,
            start_anim=start_anim,
            loop_anim=loop_anim,
            end_anim=end_anim
        )
    
    
    def add_dynamic_data(self, data=None):
        """动态添加新圆形"""
        self.add_circle(2)