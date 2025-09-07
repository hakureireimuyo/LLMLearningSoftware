from kivy.clock import Clock
from kivy.graphics import Rectangle, Color
from kivy.properties import NumericProperty, ColorProperty, ListProperty
from .animateitembase import AnimateItemBase
import random
from kivy.animation import Animation


class RisingMatrixAnimated(AnimateItemBase):
    """半透明矩阵上升动画项"""
    bar_width_min = NumericProperty(10)  # 矩阵最小宽度
    bar_width_max = NumericProperty(40)  # 矩阵最大宽度
    height_min = NumericProperty(30)     # 矩阵最小高度
    height_max = NumericProperty(150)    # 矩阵最大高度
    rise_duration_min = NumericProperty(3.0)  # 最小上升时间
    rise_duration_max = NumericProperty(8.0)  # 最大上升时间
    fade_duration = NumericProperty(1.5)      # 淡出时间
    spawn_interval = NumericProperty(0.5)     # 新矩阵生成间隔
    base_color = ColorProperty([0.2, 0.6, 1, 0.7])  # 基础颜色
    color_variation = NumericProperty(0.15)   # 颜色变化范围
    sway_amount = NumericProperty(20)         # 左右摇摆幅度

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_color = self.theme_cls.primaryColor
        self._spawn_clock = None  # 用于存储时钟事件

    def start(self):
        """开始动画和生成新矩阵的时钟"""
        super().start()
        if not self._spawn_clock:
            # 启动周期生成矩阵的时钟
            self._spawn_clock = Clock.schedule_interval(
                self.add_dynamic_data, self.spawn_interval
            )

    def end(self):
        """结束动画并停止生成新矩阵"""
        super().end()
        if self._spawn_clock:
            self._spawn_clock.cancel()
            self._spawn_clock = None

    def create_initial_graphics(self):
        """初始创建一组矩阵"""
        # 根据宽度确定初始矩阵数量
        count = max(1, int(self.width / 50))
        for _ in range(count):
            self._create_matrix()

    def add_dynamic_data(self, dt=None):
        """动态添加新矩阵（由时钟或外部调用）"""
        self._create_matrix()

    def _create_matrix(self):
        """创建一个矩阵并设置其动画"""
        # 随机宽度和高度
        width = random.uniform(self.bar_width_min, self.bar_width_max)
        height = random.uniform(self.height_min, self.height_max)
        
        # 随机位置（X坐标）
        x = random.uniform(0, max(1, self.width - width))
        
        # 起始Y位置（屏幕底部下方）
        start_y = -height
        
        # 随机颜色（基于基础色的变化）
        r = max(0, min(1, self.base_color[0] + random.uniform(-self.color_variation, self.color_variation)))
        g = max(0, min(1, self.base_color[1] + random.uniform(-self.color_variation, self.color_variation)))
        b = max(0, min(1, self.base_color[2] + random.uniform(-self.color_variation, self.color_variation)))
        a = random.uniform(0.3, 0.7)  # 随机半透明度
        
        # 创建矩阵图形
        proxy = self.create_color_shape_pair(
            rgba=(r, g, b, a),
            shape_type=Rectangle,
            pos=(x, start_y),
            size=(width, height)
        )
        
        # 上升距离（直到完全超出屏幕顶部）
        end_y = self.height + height
        
        # 上升时间（随机）
        duration = random.uniform(self.rise_duration_min, self.rise_duration_max)
        
        # 计算摇摆动画效果
        sway_time = duration * 0.2  # 摇摆动画时间占比
        sway_start = random.uniform(-self.sway_amount, self.sway_amount)
        sway_end = random.uniform(-self.sway_amount, self.sway_amount)
        
        # 上升动画（主动画）
        rise_anim = Animation(
            y=end_y,
            duration=duration,
            t='linear'
        )
        
        # 摇摆动画（循环动画）
        sway_anim = Animation(
            x=max(0, min(self.width - width, x + sway_start)),
            duration=sway_time,
            t='in_out_sine'
        ) + Animation(
            x=max(0, min(self.width - width, x + sway_end)),
            duration=sway_time,
            t='in_out_sine'
        )
        sway_anim.repeat = False
        
        # 淡出动画（结束动画）
        fade_anim = Animation(
            rgba=(r, g, b, 0),
            x=max(0, min(self.width - width, x + sway_start)),
            duration=self.fade_duration,
            t='in_cubic'
        )
        
        # 添加到基类管理（自动移除）
        self.add_graphic(
            graphic=proxy,
            start_anim=rise_anim,
            loop_anim=sway_anim,
            end_anim=fade_anim,
            auto_remove=True
        )