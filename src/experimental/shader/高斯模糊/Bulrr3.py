from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import RenderContext, Color, Rectangle
from kivy.core.image import Image
from kivy.properties import ObjectProperty, NumericProperty
from kivy.clock import Clock
import os
import io

# 二维高斯模糊着色器
gaussian_blur_shader = '''
$HEADER$

const float kernel[9] = float[](
    0.0162162162, 0.0540540541, 0.1216216216,
    0.1945945946, 0.2270270270,
    0.1945945946, 0.1216216216, 0.0540540541, 0.0162162162
);

const float offset[9] = float[](
    -4.0, -3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0
);

uniform float blurRadius;
uniform vec2 textureSize;

void main(void) {
    vec2 texelSize = 1.0 / textureSize;
    
    vec4 result = vec4(0.0);
    for (int i = 0; i < 9; i++) {
        vec2 offsetCoord = vec2(offset[i] * texelSize.x * blurRadius, 0.0);
        result += texture2D(texture0, tex_coord0 + offsetCoord) * kernel[i];
    }
    
    vec4 result2 = vec4(0.0);
    for (int i = 0; i < 9; i++) {
        vec2 offsetCoord = vec2(0.0, offset[i] * texelSize.y * blurRadius);
        result2 += texture2D(texture0, tex_coord0 + offsetCoord) * kernel[i];
    }
    
    gl_FragColor = (result + result2) * 0.5;
}
'''

class GaussianBlurWidget(Widget):
    rect = ObjectProperty(None)
    blur_radius = NumericProperty(0.5)  # 默认模糊半径
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 创建渲染上下文
        self.canvas = RenderContext(
            use_parent_projection=True,
            use_parent_modelview=True
        )
        
        # 设置着色器
        self.canvas.shader.fs = gaussian_blur_shader
        
        # 创建测试图像纹理
        self.texture = Image("input_texture.png").texture      #self.create_test_image()
        
        with self.canvas:
            Color(1, 1, 1, 1)  # 白色（不影响纹理颜色）
            self.rect = Rectangle(texture=self.texture, size=self.size, pos=self.pos)
        
        # 绑定尺寸变化事件
        self.bind(
            pos=self.update_rect, 
            size=self.update_rect,
            blur_radius=self.update_uniforms
        )
        
        # 初始化统一变量
        self.update_uniforms()
        
        # 添加调试输出
        if not self.canvas.shader.success:
            print("Shader编译错误:", self.canvas.shader.log)
    
    def update_rect(self, *args):
        """更新矩形位置和尺寸"""
        self.rect.pos = self.pos
        self.rect.size = self.size
        # 更新纹理尺寸统一变量
        self.canvas['textureSize'] = self.rect.size
    
    def update_uniforms(self, *args):
        """更新着色器统一变量"""
        self.canvas['blurRadius'] = self.blur_radius
        if self.rect:
            self.canvas['textureSize'] = self.rect.size

class GaussianBlurApp(App):
    def build(self):
        widget = GaussianBlurWidget()
        
        # 添加控件来调整模糊半径
        from kivy.uix.slider import Slider
        from kivy.uix.boxlayout import BoxLayout
        
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(widget)
        
        slider = Slider(min=0.0, max=15.0, value=0.5)
        slider.bind(value=lambda instance, value: setattr(widget, 'blur_radius', value))
        layout.add_widget(slider)
        
        return layout

if __name__ == '__main__':
    GaussianBlurApp().run()