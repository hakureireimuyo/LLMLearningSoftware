from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import RenderContext, Color, Rectangle
from kivy.core.image import Image
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.graphics.context_instructions import BindTexture
import os

# 简单着色器：将颜色变为灰度
shader_code = '''
$HEADER$

void main(void) {
    vec4 color = frag_color * texture2D(texture0, tex_coord0);
    float gray = dot(color.rgb, vec3(0.299, 0.587, 0.114));
    gl_FragColor = vec4(gray, gray, gray, color.a);
}
'''

class ShaderWidget(Widget):
    rect = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 使用RenderContext替换默认画布 - 启用必要特性
        self.canvas = RenderContext(
            use_parent_projection=True,
            use_parent_modelview=True
        )
        # 设置自定义着色器
        self.canvas.shader.fs = shader_code
        
        # 创建默认纹理
        texture = Image("input_texture.png").texture
        
        with self.canvas:
            Color(0.5, 0.8, 1, 1)  # 浅蓝色
            self.rect = Rectangle(size=self.size,pos=(0,0),texture=texture)
        
        # 绑定尺寸变化事件
        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        # 更新矩形位置和尺寸以填充整个小部件
        self.rect.pos = self.pos
        self.rect.size = self.size

class TestApp(App):
    def build(self):
        return ShaderWidget()

if __name__ == '__main__':
    TestApp().run()