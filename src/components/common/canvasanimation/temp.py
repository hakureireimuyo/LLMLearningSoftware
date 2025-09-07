from kivy.animation import Animation
from kivy.properties import NumericProperty, ColorProperty, ListProperty, BooleanProperty
from kivy.graphics import Color, Ellipse, Rectangle, Line, Scale, Rotate, PushMatrix, PopMatrix
from kivy.clock import Clock
from math import sin, cos, pi
import random
from .old.animateitembase import AnimateItemBase

class PulseIntro(AnimateItemBase):
    """透明圆叠加缩放启动动画"""
    circle_count = NumericProperty(5)
    max_scale = NumericProperty(1.5)
    duration = NumericProperty(1.0)
    circle_color = ColorProperty([1, 1, 1, 0.3])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.circles = []
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        
    def start(self):
        self.clear()
        center_x, center_y = self.center
        max_radius = min(self.width, self.height) * 0.4
        
        with self.canvas:
            for i in range(self.circle_count):
                scale = 0.1
                radius = max_radius * (1 - i * 0.1)
                Color(*self.circle_color)
                circle = Ellipse(pos=(center_x - radius, center_y - radius), 
                                size=(radius*2, radius*2))
                self.circles.append({
                    'obj': circle,
                    'radius': radius,
                    'scale': scale
                })
                
                anim = Animation(scale=self.max_scale, duration=self.duration, 
                                transition='out_quad')
                anim.start(circle)
        self.is_playing = True

    def update_canvas(self, *args):
        center_x, center_y = self.center
        for circle in self.circles:
            radius = circle['radius'] * circle['scale']
            circle['obj'].pos = (center_x - radius, center_y - radius)
            circle['obj'].size = (radius*2, radius*2)

    def clear(self):
        self.canvas.clear()
        self.circles = []
        self.is_playing = False


class RisingMatrixIntro(AnimateItemBase):
    """矩阵渐显上升动画"""
    rect_count = NumericProperty(12)
    spacing = NumericProperty(10)
    duration = NumericProperty(1.5)
    rect_color = ColorProperty([0.2, 0.6, 1, 0.7])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rects = []
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        
    def start(self):
        self.clear()
        width = (self.width - (self.rect_count - 1) * self.spacing) / self.rect_count
        
        with self.canvas:
            for i in range(self.rect_count):
                x = self.x + i * (width + self.spacing)
                height = random.uniform(30, self.height * 0.6)
                rect = Rectangle(pos=(x, self.y), size=(width, 0))
                Color(*self.rect_color)
                self.rects.append({
                    'obj': rect,
                    'target_height': height,
                    'target_y': self.y + random.uniform(20, 100)
                })
                
                anim = Animation(height=height, y=self.rects[-1]['target_y'], 
                                opacity=1, duration=self.duration,
                                transition='out_quad')
                anim.start(rect)
        self.is_playing = True

    def update_canvas(self, *args):
        width = (self.width - (self.rect_count - 1) * self.spacing) / self.rect_count
        for i, rect in enumerate(self.rects):
            rect['obj'].pos = (self.x + i * (width + self.spacing), rect['obj'].y)
            rect['obj'].size = (width, rect['obj'].size[1])

    def clear(self):
        self.canvas.clear()
        self.rects = []
        self.is_playing = False


class FlyInZoomIntro(AnimateItemBase):
    """图形飞入缩放动画"""
    shape = ListProperty(['ellipse', 'rectangle'])
    duration = NumericProperty(0.8)
    color = ColorProperty([0.9, 0.4, 0.2, 1])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.shapes = []
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        
    def start(self):
        self.clear()
        center_x, center_y = self.center
        
        with self.canvas:
            for shape_type in self.shape:
                # 随机起始位置（屏幕外）
                start_x = random.choice([-100, self.width + 100])
                start_y = random.uniform(self.y + 50, self.y + self.height - 50)
                
                # 初始尺寸很小
                size = 10
                if shape_type == 'ellipse':
                    obj = Ellipse(pos=(start_x, start_y), size=(size, size))
                else:
                    obj = Rectangle(pos=(start_x, start_y), size=(size, size))
                
                Color(*self.color)
                self.shapes.append(obj)
                
                # 目标位置和尺寸
                target_size = random.uniform(50, 120)
                target_x = center_x - target_size/2 + random.uniform(-100, 100)
                target_y = center_y - target_size/2 + random.uniform(-50, 50)
                
                anim = Animation(
                    x=target_x, y=target_y, 
                    width=target_size, height=target_size,
                    duration=self.duration, transition='out_back'
                )
                anim.start(obj)
        self.is_playing = True

    def clear(self):
        self.canvas.clear()
        self.shapes = []
        self.is_playing = False


class PulseLoop(AnimateItemBase):
    """透明圆脉动缩放循环"""
    circle_count = NumericProperty(3)
    min_scale = NumericProperty(0.5)
    max_scale = NumericProperty(1.8)
    duration = NumericProperty(2.0)
    colors = ListProperty([[1, 0.5, 0.8, 0.4], [0.5, 0.8, 1, 0.4], [0.8, 1, 0.5, 0.4]])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.circles = []
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        
    def start(self):
        self.clear()
        center_x, center_y = self.center
        base_radius = min(self.width, self.height) * 0.2
        
        with self.canvas:
            for i in range(self.circle_count):
                radius = base_radius * (1 + i * 0.3)
                color = self.colors[i % len(self.colors)]
                Color(*color)
                circle = Ellipse(pos=(center_x - radius, center_y - radius), 
                                size=(radius*2, radius*2))
                self.circles.append({
                    'obj': circle,
                    'radius': radius,
                    'scale': self.min_scale
                })
        
        self.animate_loop()
        self.is_playing = True
        
    def animate_loop(self):
        for idx, circle in enumerate(self.circles):
            anim = Animation(scale=self.max_scale, duration=self.duration/2, 
                            transition='out_quad') + \
                   Animation(scale=self.min_scale, duration=self.duration/2, 
                            transition='in_quad')
            anim.repeat = True
            anim.start(circle)
    
    def update_canvas(self, *args):
        center_x, center_y = self.center
        for circle in self.circles:
            radius = circle['radius'] * circle['scale']
            circle['obj'].pos = (center_x - radius, center_y - radius)
            circle['obj'].size = (radius*2, radius*2)
            
    def clear(self):
        self.canvas.clear()
        self.circles = []
        self.is_playing = False


class WaveLoop(AnimateItemBase):
    """矩阵波浪运动循环"""
    rect_count = NumericProperty(15)
    min_height = NumericProperty(30)
    max_height = NumericProperty(150)
    wave_speed = NumericProperty(1.0)
    colors = ListProperty([[0.2, 0.5, 0.8, 0.7], [0.3, 0.7, 0.9, 0.7]])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rects = []
        self.time = 0
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        
    def start(self):
        self.clear()
        width = self.width / self.rect_count
        
        with self.canvas:
            for i in range(self.rect_count):
                height = random.uniform(self.min_height, self.max_height)
                rect = Rectangle(
                    pos=(self.x + i * width, self.y),
                    size=(width, height)
                )
                color = self.colors[i % len(self.colors)]
                Color(*color)
                self.rects.append({
                    'obj': rect,
                    'base_height': height,
                    'speed': random.choice([0.5, 0.8, 1.2, 1.5])
                })
        
        Clock.schedule_interval(self.update_wave, 1/60.)
        self.is_playing = True
        
    def update_wave(self, dt):
        self.time += dt * self.wave_speed
        for rect in self.rects:
            wave_factor = sin(self.time * rect['speed']) * 0.5 + 0.5
            height = rect['base_height'] * (0.7 + 0.3 * wave_factor)
            rect['obj'].size = (rect['obj'].size[0], height)
            rect['obj'].pos = (rect['obj'].pos[0], self.y)
    
    def clear(self):
        Clock.unschedule(self.update_wave)
        self.canvas.clear()
        self.rects = []
        self.time = 0
        self.is_playing = False


class RotateColorLoop(AnimateItemBase):
    """旋转颜色渐变循环"""
    star_points = NumericProperty(5)
    size = NumericProperty(100)
    rotate_speed = NumericProperty(45)  # 度/秒
    color_cycle = NumericProperty(10.0)  # 颜色循环周期（秒）
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.angle = 0
        self.color_time = 0
        self.bind(pos=self.update_canvas)
        
    def start(self):
        self.clear()
        self.angle = 0
        self.color_time = 0
        
        with self.canvas:
            PushMatrix()
            self.rot = Rotate(origin=self.center, angle=self.angle)
            Color(0.2, 0.8, 1, 1)  # 初始冷色调
            self.star = self.create_star()
            PopMatrix()
        
        Clock.schedule_interval(self.update_rotation, 1/60.)
        self.is_playing = True
        
    def create_star(self):
        points = []
        center_x, center_y = self.center
        outer_radius = self.size / 2
        inner_radius = outer_radius * 0.4
        
        for i in range(self.star_points * 2):
            angle = i * pi / self.star_points - pi/2
            radius = inner_radius if i % 2 == 1 else outer_radius
            x = center_x + radius * cos(angle)
            y = center_y + radius * sin(angle)
            points.extend([x, y])
        
        return Line(points=points, close=True, width=2)
    
    def update_rotation(self, dt):
        # 更新旋转
        self.angle += self.rotate_speed * dt
        self.rot.angle = self.angle
        
        # 更新颜色渐变
        self.color_time += dt
        color_progress = (self.color_time % self.color_cycle) / self.color_cycle
        
        # 冷色调(蓝)到暖色调(橙)的渐变
        r = 0.2 + 0.8 * color_progress
        g = 0.8 - 0.4 * color_progress
        b = 1.0 - 0.8 * color_progress
        self.star.rgba = (r, g, b, 1)
    
    def clear(self):
        Clock.unschedule(self.update_rotation)
        self.canvas.clear()
        self.is_playing = False


class BounceLoop(AnimateItemBase):
    """弹性跳动效果循环"""
    size = NumericProperty(80)
    bounce_duration = NumericProperty(0.6)
    color = ColorProperty([1, 0.3, 0.4, 1])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.circle = None
        self.bind(pos=self.update_canvas)
        
    def start(self):
        self.clear()
        center_x, center_y = self.center
        
        with self.canvas:
            Color(*self.color)
            self.circle = Ellipse(
                pos=(center_x - self.size/2, center_y - self.size/2),
                size=(self.size, self.size)
        
        self.animate_bounce()
        self.is_playing = True
        
    def animate_bounce(self):
        anim = Animation(size_x=self.size*0.5, size_y=self.size*0.5, 
                        duration=self.bounce_duration/2, t='out_quad') + \
               Animation(size_x=self.size, size_y=self.size, 
                        duration=self.bounce_duration/2, t='out_bounce')
        anim.repeat = True
        anim.start(self.circle)
    
    def clear(self):
        if self.circle:
            Animation.cancel_all(self.circle)
        self.canvas.clear()
        self.circle = None
        self.is_playing = False


class ShrinkFadeOutExit(AnimateItemBase):
    """全局收缩淡出结束动画"""
    duration = NumericProperty(0.8)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.original_size = self.size[:]
        self.original_pos = self.pos[:]
        self.original_alpha = 1.0
    
    def start(self):
        self.clear()
        # 保存原始状态
        self.original_size = self.size[:]
        self.original_pos = self.pos[:]
        self.original_alpha = 1.0
        
        # 创建收缩动画
        target_size = (10, 10)
        target_pos = (
            self.center_x - target_size[0]/2,
            self.center_y - target_size[1]/2
        )
        
        anim = Animation(
            size=target_size, pos=target_pos, opacity=0,
            duration=self.duration, transition='in_cubic'
        )
        anim.bind(on_complete=self.on_animation_complete)
        anim.start(self)
        self.is_playing = True
    
    def on_animation_complete(self, anim, widget):
        self.is_playing = False
        self.clear()
    
    def reset(self):
        """重置到初始状态"""
        self.size = self.original_size
        self.pos = self.original_pos
        self.opacity = self.original_alpha


class MatrixDissipateExit(AnimateItemBase):
    """矩阵分层消散结束动画"""
    exit_duration = NumericProperty(0.7)
    stagger_delay = NumericProperty(0.1)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rects = []
        
    def start(self):
        self.clear()
        if not self.rects:
            self.create_matrix()
        
        for i, rect in enumerate(self.rects):
            delay = i * self.stagger_delay
            target_x = random.choice([-rect['obj'].size[0], self.width + rect['obj'].size[0])
            
            anim = Animation(
                x=target_x, opacity=0, 
                duration=self.exit_duration, t='in_cubic'
            )
            anim.start(rect['obj'])
        
        self.is_playing = True
    
    def create_matrix(self):
        cols = 5
        rows = 3
        rect_width = self.width / cols
        rect_height = self.height / rows
        
        with self.canvas:
            for row in range(rows):
                for col in range(cols):
                    x = self.x + col * rect_width
                    y = self.y + row * rect_height
                    rect = Rectangle(pos=(x, y), size=(rect_width-5, rect_height-5))
                    Color(0.4, 0.7, 1, 0.8)
                    self.rects.append({
                        'obj': rect,
                        'original_pos': (x, y),
                        'original_opacity': 0.8
                    })
    
    def reset(self):
        """重置到初始状态"""
        for rect in self.rects:
            rect['obj'].pos = rect['original_pos']
            rect['obj'].opacity = rect['original_opacity']
    
    def clear(self):
        self.canvas.clear()
        self.rects = []
        self.is_playing = False


class SpinFadeExit(AnimateItemBase):
    """图形旋转隐退结束动画"""
    duration = NumericProperty(0.9)
    spin_speed = NumericProperty(720)  # 旋转角度
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rotation = 0
        self.original_size = self.size[:]
        
    def start(self):
        self.clear()
        self.rotation = 0
        
        with self.canvas:
            PushMatrix()
            self.rot = Rotate(origin=self.center, angle=self.rotation)
            Color(1, 0.8, 0.2, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
            PopMatrix()
        
        # 组合动画：旋转+缩小+淡出
        anim_spin = Animation(rotation=self.spin_speed, duration=self.duration)
        anim_scale = Animation(size=(10, 10), duration=self.duration, t='in_back')
        anim_fade = Animation(opacity=0, duration=self.duration)
        
        anim = anim_spin & anim_scale & anim_fade
        anim.bind(on_complete=self.on_animation_complete)
        anim.start(self)
        self.is_playing = True
    
    def on_rotation(self, instance, value):
        self.rot.angle = value
    
    def on_animation_complete(self, anim, widget):
        self.is_playing = False
        self.clear()
    
    def reset(self):
        """重置到初始状态"""
        self.size = self.original_size
        self.opacity = 1
        self.rotation = 0


class ScaleMoveCombo(AnimateItemBase):
    """缩放移动并行复合动画"""
    duration = NumericProperty(1.2)
    travel_distance = NumericProperty(300)
    start_scale = NumericProperty(1.5)
    end_scale = NumericProperty(0.8)
    color = ColorProperty([0.3, 0.8, 0.5, 1])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.direction = random.choice(['left', 'right', 'up', 'down'])
        self.ellipse = None
        self.bind(pos=self.update_canvas)
        
    def start(self):
        self.clear()
        center_x, center_y = self.center
        
        # 初始位置和大小
        start_x = center_x - (self.size[0] * self.start_scale)/2
        start_y = center_y - (self.size[1] * self.start_scale)/2
        
        with self.canvas:
            Color(*self.color)
            self.ellipse = Ellipse(
                pos=(start_x, start_y),
                size=(self.size[0] * self.start_scale, 
                      self.size[1] * self.start_scale)
            )
        
        # 计算目标位置
        if self.direction == 'left':
            target_x = start_x - self.travel_distance
            target_y = start_y
        elif self.direction == 'right':
            target_x = start_x + self.travel_distance
            target_y = start_y
        elif self.direction == 'up':
            target_x = start_x
            target_y = start_y + self.travel_distance
        else:  # down
            target_x = start_x
            target_y = start_y - self.travel_distance
        
        # 并行动画：移动+缩放
        anim_move = Animation(x=target_x, y=target_y, duration=self.duration)
        anim_scale = Animation(
            width=self.size[0] * self.end_scale,
            height=self.size[1] * self.end_scale,
            duration=self.duration,
            transition='in_out_quad'
        )
        
        combo_anim = anim_move & anim_scale
        combo_anim.start(self.ellipse)
        self.is_playing = True
    
    def clear(self):
        self.canvas.clear()
        self.ellipse = None
        self.is_playing = False


class FadeInRotateSequence(AnimateItemBase):
    """淡入旋转序列复合动画"""
    circle_count = NumericProperty(5)
    fade_duration = NumericProperty(0.3)
    rotate_duration = NumericProperty(0.6)
    spacing = NumericProperty(40)
    colors = ListProperty([[0.9, 0.2, 0.3], [0.2, 0.7, 0.9], [0.8, 0.6, 0.2]])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.circles = []
        self.bind(pos=self.update_canvas)
        
    def start(self):
        self.clear()
        center_x, center_y = self.center
        circle_size = 50
        
        with self.canvas:
            for i in range(self.circle_count):
                x = center_x - circle_size/2 + (i - self.circle_count//2) * self.spacing
                y = center_y - circle_size/2
                circle = Ellipse(pos=(x, y), size=(circle_size, circle_size))
                Color(*self.colors[i % len(self.colors)], 0)  # 初始透明
                self.circles.append(circle)
        
        # 创建序列动画
        self.animate_sequence(0)
        self.is_playing = True
    
    def animate_sequence(self, index):
        if index >= len(self.circles):
            return
            
        circle = self.circles[index]
        
        # 淡入动画
        fade_in = Animation(opacity=1, duration=self.fade_duration)
        
        # 旋转动画
        rotate = Animation(angle=360, duration=self.rotate_duration, t='out_back')
        rotate.repeat = False
        
        # 序列：淡入完成后开始旋转
        seq = fade_in + rotate
        seq.bind(on_complete=lambda *args: self.animate_sequence(index+1))
        seq.start(circle)
    
    def clear(self):
        self.canvas.clear()
        self.circles = []
        self.is_playing = False