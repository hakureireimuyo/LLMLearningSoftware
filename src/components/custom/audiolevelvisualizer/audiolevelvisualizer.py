from kivymd.uix.floatlayout import MDFloatLayout
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivymd.uix.behaviors import ScaleBehavior
from components.common.canvasanimation import DynamicAnimateLabel

class AudioVisualizerContainer(MDFloatLayout,ScaleBehavior):
    # 这个组件用于包容动画显示组件,显示更多其它信息,完成一些开始和结束的动画效果,使用策略模式可以替换不同的动画显示组件
    text=StringProperty("")
    def __init__(self, **kwargs):
        super(AudioVisualizerContainer,self).__init__(**kwargs)
        self.size_hint=(None,None)
        self.size=(dp(400),dp(300))
        self._animation=DynamicAnimateLabel()
        self.add_widget(self._animation)
        self.md_bg_color = self.theme_cls.secondaryContainerColor
        self.line_color = self.theme_cls.primaryColor
        self.line_width=2
        self.close()

    def update_theme(self, instance, value):
        self.md_bg_color = self.theme_cls.secondaryContainerColor
        self.line_color = self.theme_cls.primaryColor
    
    def open(self):
        self.disabled=False
        Animation(scale_value_x=1, scale_value_y=1, d=0.2, t="out_quad").start(self)
        
    def close(self):
        self.disabled=True
        Animation(scale_value_x=0, scale_value_y=0, d=0.2, t="out_quad").start(self)
        self._animation.stop()

    def change_visualize_mode(self):
        if self.disabled:return
        if self._animation.animation_mode=="circle":
            self._animation.switch_animation_mode("bars")
            return
        if self._animation.animation_mode=="bars":
            self._animation.switch_animation_mode("circle")
            return


    
        