from kivy.properties import  StringProperty,BooleanProperty
from kivymd.uix.boxlayout import MDBoxLayout
from .old.baranimateitem import BarAnimateItem
from.old.circleanimateitem import CircleAnimateItem

class DynamicAnimateLabel(MDBoxLayout):
    """动态标签 - 通过依赖注入管理动画项,最大用途是可以切换动画"""
    animation_mode = StringProperty("bars")
    is_animating = BooleanProperty(False)
    is_paused = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        self.current_item = None
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (250, 250)
        self.md_bg_color = self.theme_cls.secondaryContainerColor
        self.line_color = self.theme_cls.primaryColor
        self.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        self.line_width=2
        # 通过依赖注入初始化动画项
        self.bar_item = BarAnimateItem()
        self.circle_item = CircleAnimateItem()
        
        # 初始设置
        self.switch_animation_mode(self.animation_mode)
    
    def update_theme(self, instance, value):
        """主题更新处理"""
    
    def switch_animation_mode(self, mode):
        """切换动画模式（依赖注入）"""
        if mode not in ["bars", "circle"]:
            return
        
        if self.current_item is not None and self.current_item.is_animating:
            self.current_item.stop()
            
        # 移除当前动画项
        if self.current_item and self.current_item in self.children:
            self.remove_widget(self.current_item)
        
        # 设置新动画项
        self.animation_mode = mode
        if mode == "bars":
            self.current_item = self.bar_item
        else:
            self.current_item = self.circle_item
        
        # 添加新动画项并设置尺寸位置
        self.add_widget(self.current_item)
    
    def add_value(self, value):
        """添加新值到当前动画项"""
        if self.animation_mode == "bars":
            self.bar_item.add_item(value)
    
    def start(self):
        """启动动画"""
        self.current_item.start()
    
    def stop(self):
        """停止动画"""
        self.current_item.stop()
    
    def pause(self):
        """暂停动画"""
        self.current_item.pause()

    def resume(self):
        """恢复暂停的动画"""
        self.current_item.resume()