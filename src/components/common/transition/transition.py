from kivy.animation import Animation
from kivy.graphics import PushMatrix, PopMatrix, Scale
from kivy.properties import NumericProperty, OptionProperty
from kivymd.uix.transition import MDTransitionBase
from kivymd.uix.screenmanager import MDScreenManager

class MDFadeSlideInTransition(MDTransitionBase):
    """
    自定义过渡效果：新屏幕从指定方向滑入并淡入
    
    特性：
    1. 旧屏幕保持不变
    2. 新屏幕从指定方向滑入
    3. 新屏幕初始时透明且缩放
    4. 新屏幕逐渐恢复不透明度和正常大小
    5. 新屏幕完全出现后旧屏幕立即消失
    
    参数：
    direction: 滑入方向 ('left', 'right', 'top', 'bottom')
    initial_scale: 新屏幕初始缩放比例 (0.0-1.0)
    duration: 过渡持续时间 (秒)
    """

    direction = OptionProperty('right', options=['left', 'right', 'top', 'bottom'])
    initial_scale = NumericProperty(0.8)
    duration = NumericProperty(0.3)
    
    # 存储缩放指令的映射
    _scale_map = {}
    
    def start(self, manager: MDScreenManager) -> None:
        """初始化过渡动画"""
        # 调用父类方法进行必要的初始化
        super().start(manager)
        
        # 获取当前屏幕（即将离开）和新屏幕（即将进入）
        screen_out = self.screen_out
        screen_in = self.screen_in
        
        # 确保新屏幕有图形上下文
        if not hasattr(screen_in, 'canvas'):
            return
        
        # 初始化新屏幕的缩放变换
        screen_id = id(screen_in)
        if screen_id not in self._scale_map:
            # 创建缩放变换矩阵
            with screen_in.canvas.before:
                PushMatrix()
                self._scale_map[screen_id] = Scale(
                    origin=(screen_in.center_x, screen_in.center_y)
                )
            with screen_in.canvas.after:
                PopMatrix()
        
        # 获取缩放指令
        scale = self._scale_map[screen_id]
        
        # 设置新屏幕初始状态
        scale.xyz = (self.initial_scale, self.initial_scale, 1)  # 初始缩放
        screen_in.opacity = 0  # 初始完全透明
        
        # 根据方向设置新屏幕初始位置
        if self.direction == 'left':
            screen_in.x = manager.x + manager.width
        elif self.direction == 'right':
            screen_in.x = manager.x - manager.width
        elif self.direction == 'top':
            screen_in.y = manager.y - manager.height
        elif self.direction == 'bottom':
            screen_in.y = manager.y + manager.height
        
        # 创建动画
        anim = Animation(
            opacity=1,  # 淡入
            duration=self.duration,
            t='out_quad'
        )
        
        # 添加位置动画
        if self.direction in ['left', 'right']:
            anim &= Animation(x=manager.x, duration=self.duration, t='out_back')
        else:
            anim &= Animation(y=manager.y, duration=self.duration, t='out_back')
        
        # 添加缩放动画
        anim &= Animation(
            xyz=(1, 1, 1),  # 缩放恢复
            d=self.duration * 0.8,  # 缩放动画稍快于其他动画
            t='out_back'
        )
        
        # 设置动画目标为缩放指令
        anim.cancel_all(scale)
        anim.start(scale)
        
        # 设置动画完成回调
        anim.bind(on_complete=self._on_animation_complete)
        
        # 开始动画
        anim.start(screen_in)
    
    def _on_animation_complete(self, *args):
        """动画完成时调用"""
        # 调用父类方法完成过渡
        super().on_complete()
        
        # 清理缩放变换
        screen_id = id(self.screen_in)
        if screen_id in self._scale_map:
            # 重置缩放
            self._scale_map[screen_id].xyz = (1, 1, 1)
            # 移除图形指令
            del self._scale_map[screen_id]
    
    def on_progress(self, progress):
        """过渡进度更新"""
        # 调用父类方法
        super().on_progress(progress)
        
        # 如果需要更细致的控制，可以在这里添加逻辑
        # 但当前实现通过Animation自动处理进度，所以不需要额外代码


"""
Custom Transitions for KivyMD
=============================

This module defines new screen transition components based on the
existing KivyMD transition infrastructure, offering additional visual
effects for screen changes.

Transitions included:
- MDFadeTransition: Simple fade-in/fade-out between screens.
- MDRotateTransition: Rotates outgoing/incoming screens during transition.
- MDZoomTransition: Zooms out the current screen and zooms in the next screen.
- MDBounceSlideTransition: Slide with a bounce effect.
"""

from kivy.animation import Animation, AnimationTransition
from kivy.graphics import PushMatrix, PopMatrix, Rotate, Scale
from kivy.properties import NumericProperty, OptionProperty
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManagerException

from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.transition import MDTransitionBase

__all__ = (
    "MDFadeTransition",
    "MDRotateTransition",
    "MDZoomTransition",
    "MDBounceSlideTransition",
)

class MDFadeTransition(MDTransitionBase):
    """
    Simple fade transition between two screens.
    我喜欢这个
    """

    duration = NumericProperty(0.3)

    def start(self, instance_screen_manager: MDScreenManager) -> None:
        if self.is_active:
            raise ScreenManagerException("start() is called twice!")
        self.manager = instance_screen_manager

        self.screen_in.opacity = 0
        self.screen_in.pos = self.manager.pos
        self.add_screen(self.screen_in)
        self.screen_in.transition_progress = 0.0
        self.screen_in.transition_state = "in"
        self.screen_out.transition_progress = 0.0
        self.screen_out.transition_state = "out"

        self.screen_in.dispatch("on_pre_enter")
        self.screen_out.dispatch("on_pre_leave")

        anim = Animation(opacity=1, d=self.duration)
        anim.bind(on_progress=self._on_progress, on_complete=self._on_complete)
        self.is_active = True
        anim.start(self.screen_in)
        self.dispatch("on_progress", 0)

    def on_progress(self, progression: float) -> None:
        # progression is handled by Animation, nothing extra needed
        pass

    def on_complete(self) -> None:
        self.screen_in.opacity = 1
        self.screen_out.opacity = 1
        super().on_complete()


class MDRotateTransition(MDTransitionBase):
    """
    Rotates the outgoing screen while fading in the incoming screen.
    修正了 _rot_angle 的绑定方式，避免 AttributeError
    """
    duration = NumericProperty(0.4)
    angle = NumericProperty(90)
    direction = OptionProperty("left", options=["left", "right"])

    def start(self, instance_screen_manager: MDScreenManager) -> None:
        if self.is_active:
            raise ScreenManagerException("start() is called twice!")
        self.manager = instance_screen_manager

        # Setup canvas for rotation
        self._rot = None
        with self.screen_out.canvas.before:
            PushMatrix()
            self._rot = Rotate(origin=self.screen_out.center, angle=0)
        with self.screen_out.canvas.after:
            PopMatrix()

        self.screen_in.opacity = 0
        self.screen_in.pos = self.manager.pos
        self.add_screen(self.screen_in)
        self.screen_in.transition_progress = 0.0
        self.screen_in.transition_state = "in"
        self.screen_out.transition_progress = 0.0
        self.screen_out.transition_state = "out"

        self.screen_in.dispatch("on_pre_enter")
        self.screen_out.dispatch("on_pre_leave")

        self.is_active = True

        # 直接控制 self._rot.angle
        target_angle = self.angle if self.direction == "left" else -self.angle
        anim_out = Animation(angle=target_angle, opacity=0, d=self.duration)
        anim_in = Animation(opacity=1, d=self.duration)
        anim_out.bind(on_complete=lambda *_: self._finish_rotation())
        anim_in.start(self.screen_in)
        anim_out.start(self._rot)
        Animation(opacity=0, d=self.duration).start(self.screen_out)

    def _finish_rotation(self):
        # 恢复角度
        if self._rot:
            self._rot.angle = 0
        self.on_complete()

    def on_progress(self, progression: float) -> None:
        pass

    def on_complete(self) -> None:
        self.screen_in.opacity = 1
        self.screen_out.opacity = 1
        if self._rot:
            try:
                self.screen_out.canvas.before.remove(self._rot)
            except Exception:
                pass
        super().on_complete()


class MDZoomTransition(MDTransitionBase):
    """
    Zooms out the current screen and zooms in the next screen.
    修正了 _scale_in/_scale_out 的动画绑定方式，避免 AttributeError
    换不回来了
    """
    duration = NumericProperty(0.35)
    zoom = NumericProperty(0.7)

    def start(self, instance_screen_manager: MDScreenManager) -> None:
        if self.is_active:
            raise ScreenManagerException("start() is called twice!")
        self.manager = instance_screen_manager

        self._scale_out = None
        self._scale_in = None
        # Setup canvas for scaling
        with self.screen_out.canvas.before:
            PushMatrix()
            self._scale_out = Scale(origin=self.screen_out.center, x=1, y=1, z=1)
        with self.screen_out.canvas.after:
            PopMatrix()
        with self.screen_in.canvas.before:
            PushMatrix()
            self._scale_in = Scale(origin=self.screen_in.center, x=self.zoom, y=self.zoom, z=1)
        with self.screen_in.canvas.after:
            PopMatrix()

        self.screen_in.opacity = 0
        self.screen_in.pos = self.manager.pos
        self.add_screen(self.screen_in)
        self.screen_in.transition_progress = 0.0
        self.screen_in.transition_state = "in"
        self.screen_out.transition_progress = 0.0
        self.screen_out.transition_state = "out"

        self.screen_in.dispatch("on_pre_enter")
        self.screen_out.dispatch("on_pre_leave")

        self.is_active = True

        # 用lambda绑定Scale属性
        anim_out = Animation(x=self.zoom, y=self.zoom, d=self.duration)
        anim_in = Animation(x=1, y=1, d=self.duration)
        fade_out = Animation(opacity=0, d=self.duration)
        fade_in = Animation(opacity=1, d=self.duration)
        anim_out.bind(on_progress=lambda a, w, p: self._set_scale(self._scale_out, a, w, p))
        anim_in.bind(on_progress=lambda a, w, p: self._set_scale(self._scale_in, a, w, p))
        fade_out.bind(on_complete=lambda *_: self._finish_zoom())
        anim_out.start(self._scale_out)
        anim_in.start(self._scale_in)
        fade_in.start(self.screen_in)
        fade_out.start(self.screen_out)

    def _set_scale(self, scale_obj, anim, widget, progression):
        if scale_obj is None:
            return
        # 动画作用的是Scale对象本身
        scale_obj.x = widget.x
        scale_obj.y = widget.y

    def _finish_zoom(self):
        # 恢复缩放
        if self._scale_out:
            self._scale_out.x = 1
            self._scale_out.y = 1
        if self._scale_in:
            self._scale_in.x = 1
            self._scale_in.y = 1
        self.on_complete()

    def on_progress(self, progression: float) -> None:
        pass

    def on_complete(self) -> None:
        self.screen_in.opacity = 1
        self.screen_out.opacity = 1
        super().on_complete()


class MDBounceSlideTransition(MDTransitionBase):
    """
    Slide transition with a bounce effect.
    修正：支持来回切换（direction），并自动重置位置
    并没有
    """
    direction = OptionProperty("left", options=["left", "right", "up", "down"])
    duration = NumericProperty(0.4)
    bounce_distance = NumericProperty(dp(80))

    def start(self, instance_screen_manager: MDScreenManager) -> None:
        if self.is_active:
            raise ScreenManagerException("start() is called twice!")
        self.manager = instance_screen_manager

        # 记录原始位置，方便切回来
        self._original_in_pos = self.screen_in.pos
        self._original_out_pos = self.screen_out.pos

        # Initial positions
        if self.direction == "left":
            self.screen_in.x = self.manager.width
            self.screen_in.y = self.manager.y
            dest_out_x = -self.manager.width
            dest_in_x = self.manager.x
            anim_out = Animation(x=dest_out_x, t="in_quad", d=self.duration)
            anim_in = Animation(x=dest_in_x, t="out_bounce", d=self.duration)
        elif self.direction == "right":
            self.screen_in.x = -self.manager.width
            self.screen_in.y = self.manager.y
            dest_out_x = self.manager.width
            dest_in_x = self.manager.x
            anim_out = Animation(x=dest_out_x, t="in_quad", d=self.duration)
            anim_in = Animation(x=dest_in_x, t="out_bounce", d=self.duration)
        elif self.direction == "up":
            self.screen_in.y = -self.manager.height
            self.screen_in.x = self.manager.x
            dest_out_y = self.manager.height
            dest_in_y = self.manager.y
            anim_out = Animation(y=dest_out_y, t="in_quad", d=self.duration)
            anim_in = Animation(y=dest_in_y, t="out_bounce", d=self.duration)
        else:  # down
            self.screen_in.y = self.manager.height
            self.screen_in.x = self.manager.x
            dest_out_y = -self.manager.height
            dest_in_y = self.manager.y
            anim_out = Animation(y=dest_out_y, t="in_quad", d=self.duration)
            anim_in = Animation(y=dest_in_y, t="out_bounce", d=self.duration)

        self.add_screen(self.screen_in)
        self.screen_in.transition_progress = 0.0
        self.screen_in.transition_state = "in"
        self.screen_out.transition_progress = 0.0
        self.screen_out.transition_state = "out"

        self.screen_in.dispatch("on_pre_enter")
        self.screen_out.dispatch("on_pre_leave")

        self.is_active = True

        anim_in.bind(on_complete=lambda *a: self._finish_slide())
        anim_in.start(self.screen_in)
        anim_out.start(self.screen_out)

    def _finish_slide(self):
        # 重置位置，支持反向切换
        self.screen_in.pos = self.manager.pos
        self.screen_out.pos = self.manager.pos
        self.on_complete()

    def on_progress(self, progression: float) -> None:
        pass

    def on_complete(self) -> None:
        self.screen_in.opacity = 1
        self.screen_out.opacity = 1
        super().on_complete()