from kivy.graphics import Rectangle, Color
from kivy.graphics.texture import Texture

from kivy.uix.widget import Widget
import numpy as np

class TextureGradientWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.texture = self.create_gradient_texture()
        self.bind(pos=self.update_rect, size=self.update_rect)
        self.update_rect()
    
    def create_gradient_texture(self):
        # 创建渐变纹理 (256x1 像素)
        texture = Texture.create(size=(256, 1), colorfmt='rgba')
        
        # 生成渐变数据
        buffer = bytearray()
        for x in range(256):
            # 从红色到蓝色的渐变
            r = int(255 * (1 - x/255))
            g = 0
            b = int(255 * (x/255))
            a = 255
            buffer.extend([r, g, b, a])
        
        # 设置纹理数据
        texture.blit_buffer(buffer, colorfmt='rgba', bufferfmt='ubyte')
        return texture
    
    def update_rect(self, *args):
        self.canvas.clear()
        with self.canvas:
            Rectangle(
                pos=self.pos,
                size=self.size,
                texture=self.texture
            )

from kivy.app import App
class TestApp(App):
    def build(self):
        return TextureGradientWidget(size=(300, 200), pos=(0, 0))
    
TestApp().run()
