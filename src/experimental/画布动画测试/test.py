from kivy.animation import Animation
from kivymd.app import MDApp
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock

class TextWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (100, 50)  # 初始大小
        self.pos = (200,100)  # 初始位置
        with self.canvas:
            self.col=Color(1, 0, 0, 1)  # 红色
            self.ret=Rectangle(pos=self.pos, size=self.size)
            self.ret2=Rectangle(pos=(self.x+100,self.y+100), size=self.size)
        self.anim=None
        self.animate()


    def animate(self):
        # 定义动画
        self.anim = Animation(pos=(self.x + 100, self.y), t='out_quad', duration=15)
        self.anim += Animation(pos=(self.x, self.y), t='in_quad', duration=15)
        #self.anim.repeat = True  # 无限循环
        # 启动动画
        self.anim.start(self.ret)
        self.anim.start(self.ret2)
        # 颜色渐变动画
        color_anim = Animation(rgba=(1, 1, 0, 1), t='out_quad', duration=2) + Animation(rgba=(1, 0, 0, 1), t='in_quad', duration=2)
        color_anim.repeat = True  # 无限循环
        color_anim.start(self.col)

    def set_top(self):
        if self.anim is None:return
        Clock.schedule_once(lambda x:self.anim.cancel(self.ret), 2.5)  # 每5秒执行一次动画
        Clock.schedule_once(lambda x:self.anim.start(self.ret), 4)  # 每5秒执行一次动画
        Clock.schedule_once(lambda x:self.clear_canvas(), 5)  # 每5秒执行一次动画

    def clear_canvas(self):
        """清除画布"""
        self.canvas.remove(self.ret)

class TestApp(MDApp):
    def build(self):
        return TextWidget()
if __name__ == '__main__':
    TestApp().run()