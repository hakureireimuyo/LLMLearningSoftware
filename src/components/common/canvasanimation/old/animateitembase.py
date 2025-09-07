from kivy.properties import BooleanProperty
from kivymd.uix.behaviors import DeclarativeBehavior, BackgroundColorBehavior
from kivy.uix.widget import Widget
from kivymd.theming import ThemableBehavior
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.clock import Clock

class AnimateItemBase(DeclarativeBehavior, Widget, ThemableBehavior, BackgroundColorBehavior):
    """动画项基类 - 添加完整生命周期管理"""
    is_animating = BooleanProperty(False)  # 动画是否正在运行
    is_paused = BooleanProperty(False)     # 动画是否暂停
    _clock_event = None                    # 存储Clock事件
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.initialize()
    
    def initialize(self):
        """初始化动画状态"""
        self.is_animating = False
        self.is_paused = False

    def start(self):
        """开始或恢复动画"""
        self.print_info("start")
        if not self.is_animating:
            self.is_animating = True
            self.is_paused = False
            if self._clock_event is None:
                self._clock_event = Clock.schedule_interval(self.update, 1/60)
        elif self.is_paused:
            self.resume()
    
    def pause(self):
        """暂停动画"""
        self.print_info("pause")
        if self.is_animating and not self.is_paused:
            self.is_paused = True
            if self._clock_event is not None:
                self._clock_event.cancel()
                self._clock_event = None
    
    def resume(self):
        """恢复暂停的动画"""
        self.print_info("resume")
        if self.is_animating and self.is_paused:
            self.is_paused = False
            if self._clock_event is None:
                self._clock_event = Clock.schedule_interval(self.update, 1/60)
    
    def stop(self):
        """停止动画并重置状态"""
        self.print_info("stop")
        if self.is_animating:
            self.is_animating = False
            self.is_paused = False
            if self._clock_event is not None:
                self._clock_event.cancel()
                self._clock_event = None
        self.clear()

    def print_info(self,text):
        print(f"AnimateItemBase Info:{self}")
        print(text)
        print(f"is_animating: {self.is_animating}, is_paused: {self.is_paused}")
        print(f"pos: {self.pos}, size: {self.size}")

    def update(self, dt):
        """更新动画状态 - 需要子类实现"""
        pass
    
    def draw(self):
        """绘制动画 - 需要子类实现"""
        pass
    
    def clear(self):
        """清除动画状态 - 需要子类实现"""
        self.canvas.clear()
    
    def add_item(self, item):
        """添加动画项 - 需要子类实现"""
        pass

