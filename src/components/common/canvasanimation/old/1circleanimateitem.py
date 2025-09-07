from kivy.properties import NumericProperty, ColorProperty
from kivy.graphics import Color, Ellipse
from kivy.animation import Animation
from .animateitembase import AnimateItemBase
import math
import random

class CircleProxy:
    """圆形代理类 - 用于动画属性绑定"""
    def __init__(self, center):
        self.center = center
        self._radius = 0
        self.ellipse = None
        self.uid=None
    
    @property
    def radius(self):
        return self._radius
    
    @radius.setter
    def radius(self, value):
        self._radius = value
        self.update_ellipse()
    
    def update_ellipse(self):
        """更新椭圆图形的位置和大小"""
        if self.ellipse:
            self.ellipse.pos = (self.center[0] - self._radius, 
                               self.center[1] - self._radius)
            self.ellipse.size = (self._radius * 2, self._radius * 2)

class CircleAnimateItem(AnimateItemBase):
    """圆形波动画项 - 使用GraphicGroup管理动画"""
    # 定义属性
    circle_count = NumericProperty(4)
    min_radius = NumericProperty(10)
    max_radius = NumericProperty(60)
    pulse_speed = NumericProperty(1.0)
    circle_color = ColorProperty([0.2, 0.6, 1, 0.5])
    pulse_duration = NumericProperty(2.0)  # 脉动动画周期
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.circle_phases = []  # 存储每个圆形的相位
        self.circle_alphas = []   # 存储每个圆形的透明度
        self.circle_proxies = []  # 存储圆形代理对象
        self._init_circles()
    
    def _init_circles(self):
        """初始化圆环参数"""
        self.circle_phases = [i / self.circle_count for i in range(self.circle_count)]
        self.circle_alphas = [0.8 - (i * 0.8 / self.circle_count) for i in range(self.circle_count)]
    
    def create_graphics(self):
        """创建图形指令和动画对象"""
        # 清除旧图形
        self.graphic_group.remove_all()
        self.circle_proxies = []
        
        # 创建图形指令和动画
        with self.canvas:
            for i in range(self.circle_count):
                # 创建颜色指令
                color = Color(*self.circle_color[:3], self.circle_alphas[i])
                
                # 创建圆形代理对象
                proxy = CircleProxy(self.center)
                
                # 创建圆形指令
                ellipse = Ellipse()
                proxy.ellipse = ellipse
                proxy.uid=ellipse.uid
                
                # 计算当前半径
                progress = (math.sin(self.circle_phases[i] * 2 * math.pi) + 1) / 2
                radius = self.min_radius + (self.max_radius - self.min_radius) * progress
                proxy.radius = radius
                
                # 创建开启动画（淡入）
                start_anim = Animation(
                    rgba=(*self.circle_color[:3],self.circle_alphas[i]),
                    duration=0.5
                )
                
                # 创建循环动画（脉动效果）
                loop_anim = Animation(
                    radius=self.max_radius,
                    duration=(self.pulse_duration/2*(i+1)),
                    t='out_sine'
                ) + Animation(
                    radius=self.min_radius,
                    duration=(self.pulse_duration/2*(i+1)),
                    t='in_sine'
                )
                loop_anim.repeat = True
                
                # 创建结束动画（淡出）
                end_anim = Animation(
                    rgba=(0,0,0,0),
                    duration=0.3
                )
                
                # 添加到图形组
                self.graphic_group.add_item(
                    graphic=color,
                    start_anim=start_anim,
                    loop_anim=None,  # 颜色不参与脉动
                    end_anim=end_anim
                )
                
                self.graphic_group.add_item(
                    graphic=proxy,
                    start_anim=None,
                    loop_anim=loop_anim,
                    end_anim=None
                )
                
                self.circle_proxies.append(proxy)
    
    def update_layout(self):
        """更新布局"""
        # 更新所有圆形代理的中心点
        for proxy in self.circle_proxies:
            proxy.center = self.center
    
    def clear_canvas(self):
        """清除画布内容"""
        super().clear_canvas()
        self.circle_proxies = []
    
    def add_item(self, item):
        """添加新圆形（可选功能）"""
        # 添加一个新圆形
        self.circle_count += 1
        self._init_circles()
        
        # 如果动画正在运行，重新创建图形
        if self.is_animating:
            self.create_graphics()
            self.graphic_group.start_animations('loop_anim')

