from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.core.image import Image

class TexturedWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 加载纹理
        texture = Image("input_texture.png").texture
        self.size = texture.size
        with self.canvas:
            # 设置基础颜色（与纹理颜色混合）
            Color(1, 1, 1)  # 白色（不影响纹理颜色）
            # 添加纹理到矩形
            Rectangle(pos=(100, 100), size=self.size, source="input_texture.png")

class TestApp(App):
    def build(self):
        return TexturedWidget()

if __name__ == '__main__':
    TestApp().run()