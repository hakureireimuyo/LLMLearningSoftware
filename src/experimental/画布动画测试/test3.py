from kivy.clock import Clock
from kivy.graphics import Rotate, Rectangle
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Rotate, PushMatrix, PopMatrix


class DynamicRotateWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rotation_angle = 0
        with self.canvas:
            PushMatrix()  # 保存当前矩阵
            self.rotate_inst = Rotate(angle=self.rotation_angle, origin=(150, 150))
            Rectangle(pos=(100, 100), size=(100, 100))
            PopMatrix()  # 恢复矩阵
            Rotate(angle=45, origin=(250, 250))
            Rectangle(pos=(200, 200), size=(100, 100))
            Rotate(angle=90, origin=(350, 350))
            Rectangle(pos=(300, 300), size=(100, 100))
        # 每帧更新角度
        Clock.schedule_interval(self.update_angle, 1/60)

    def update_angle(self, dt):
        self.rotation_angle = (self.rotation_angle + 1) % 360
        self.rotate_inst.angle = self.rotation_angle

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout

class RotateApp(App):
    def build(self):
        layout = FloatLayout()
        widget = DynamicRotateWidget()
        layout.add_widget(widget)
        return layout
        
if __name__ == '__main__':
    RotateApp().run()