from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Rotate, PushMatrix, PopMatrix

class TransformedWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            # 原始矩形（红色）
            Color(1, 0, 0)
            Rectangle(pos=(100, 100), size=(100, 100))
            
            # 应用变换
            PushMatrix()
            Rotate(angle=45, origin=(150, 150))
            
            # 变换后的矩形（蓝色）
            Color(0, 0, 1)
            Rectangle(pos=(100, 100), size=(100, 100))
            
            PopMatrix()

class TestApp(App):
    def build(self):
        return TransformedWidget()

if __name__ == '__main__':
    TestApp().run()