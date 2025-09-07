from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.lang import Builder
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import BooleanProperty,NumericProperty,StringProperty

class SlideDrawer(MDBoxLayout):
    """
    具有滑动效果的抽屉
    """
    # 记录组件的状态，是否打开，初始化赋值会影响到组件的初始状态
    open=BooleanProperty(False)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.floater = MDFloatLayout()
        self.floater.size=self.size
        self.boxlayout=MDBoxLayout(orientation='vertical')
        self.floater.add_widget(self.boxlayout)
        #Clock.schedule_once(lambda dt:self.auto_bind())
        self.floater.bind(size=self.update_size,pos=self.update_pos)
        self.is_frist=True
        #self.bind(theme_cls=self.update_colors)
        self.theme_cls.bind(primary_palette=self.update_theme)
        self.theme_cls.bind(theme_style=self.update_theme)
        self.theme_cls.bind(dynamic_scheme_name=self.update_theme)
        self.update_theme()
    
    def update_theme(self, *args):
        # 在这里更新组件的所有颜色相关属性
        self.boxlayout.md_bg_color=self.theme_cls.primaryContainerColor
        
    def update_size(self, *args):
        self.boxlayout.size=self.floater.size

    def update_pos(self, *args):
        self.boxlayout.pos=self.floater.pos

    def add_widget(self, widget, index=0):
        self.boxlayout.add_widget(widget, index)

    def clear_widgets(self, widgets=None):
        self.boxlayout.clear_widgets(widgets)

    def _open(self):
        # 首先将子组件加载到抽屉中
        # 然后设置该组件的大小
        # 然后将浮动窗口从某个方向升起
        if self.is_frist:
            self.is_frist=False
            self.size_hint=(1,1)
            self.floater.pos_hint={'center_x':0.5,'center_y':0.5}
            super(SlideDrawer, self).add_widget(self.floater)
        else:
            Clock.schedule_once(lambda dt:self.up())

    def close(self):
        # 首先将浮动窗口从某个方向降下
        # 然后将子组件从抽屉中移除
        # 然后设置该组件的大小
        if self.is_frist:
            self.is_frist=False
            self.size_hint=(0,0)
            self.floater.pos_hint={'center_x':0.5,'center_y':2}
            super(SlideDrawer, self).add_widget(self.floater)
        else:
            Clock.schedule_once(lambda dt:self.down())

    def up(self):
        self.floater.pos_hint={'center_x':0.5,'center_y':2}
        an=Animation(pos_hint={'center_x':0.5,'center_y':0.5},duration=0.5,t='out_quad')
        Animation(size_hint=(1,1),duration=0.5).start(self)        
        Clock.schedule_once(lambda dt:an.start(self.floater),0.5)
        Clock.schedule_once(lambda dt:super(SlideDrawer, self).add_widget(self.floater),0.5)

    def down(self):
        an=Animation(size_hint=(0,0),duration=0.5)
        self.floater.pos_hint={'center_x':0.5,'center_y':0.5}
        Animation(pos_hint={'center_x':0.5,'center_y':2},duration=0.5,t='in_cubic').start(self.floater)
        Clock.schedule_once(lambda dt:an.start(self),0.5)
        Clock.schedule_once(lambda dt:super(SlideDrawer, self).remove_widget(self.floater),0.5)

    def on_open(self,instance,value):
        if self.open:
            self._open()
        else:
            self.close()

    def print(self):
        print('====drawer====')
        print(self.size)
        print(self.pos)
        print('====floater====')
        print(self.floater.size)
        print(self.pos)
        print('====boxlayout====')
        print(self.boxlayout.size)
        print(self.pos)

class TestSlideDrawer(SlideDrawer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def change(self):
        self.print()
        return super().change()