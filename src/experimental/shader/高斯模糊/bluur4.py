from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import RenderContext, Color, Rectangle
from kivy.core.image import Image
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.slider import Slider
from kivy.uix.label import Label
import os
import io
from PIL import Image as PILImage, ImageDraw

fshader="""
$HEADER$

// 高斯模糊参数
const float gauss_kernel[9] = float[](
    0.0162162162, 0.0540540541, 0.1216216216,
    0.1945945946, 0.2270270270,
    0.1945945946, 0.1216216216, 0.0540540541, 0.0162162162
);

const float gauss_offset[9] = float[](
    -4.0, -3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0
);

// 平均模糊参数（3x3）
const float avg_kernel[9] = float[](
    1.0/9.0, 1.0/9.0, 1.0/9.0,
    1.0/9.0, 1.0/9.0, 1.0/9.0,
    1.0/9.0, 1.0/9.0, 1.0/9.0
);

const vec2 avg_offset[9] = vec2[](
    vec2(-1.0, -1.0), vec2(0.0, -1.0), vec2(1.0, -1.0),
    vec2(-1.0, 0.0),  vec2(0.0, 0.0),  vec2(1.0, 0.0),
    vec2(-1.0, 1.0),  vec2(0.0, 1.0),  vec2(1.0, 1.0)
);

// 控制参数
uniform float blurRadius;      // 主模糊半径 (0.0 - 5.0)
uniform float avgBlurFactor;   // 平均模糊强度 (0.0 - 1.0)
uniform int avgPasses;         // 平均模糊次数 (1-4)
uniform vec2 textureSize;      // 纹理尺寸

// 高斯模糊函数
vec4 gaussianBlur(vec2 coord) {
    vec2 texelSize = 1.0 / textureSize;
    vec4 result = vec4(0.0);
    
    // 水平模糊
    for (int i = 0; i < 9; i++) {
        vec2 offsetCoord = vec2(gauss_offset[i] * texelSize.x * blurRadius, 0.0);
        result += texture2D(texture0, coord + offsetCoord) * gauss_kernel[i];
    }
    
    vec4 result2 = vec4(0.0);
    // 垂直模糊
    for (int i = 0; i < 9; i++) {
        vec2 offsetCoord = vec2(0.0, gauss_offset[i] * texelSize.y * blurRadius);
        result2 += texture2D(texture0, coord + offsetCoord) * gauss_kernel[i];
    }
    
    return (result + result2) * 0.5;
}

// 平均模糊函数
vec4 averageBlur(vec2 coord) {
    vec2 texelSize = 1.0 / textureSize;
    vec4 result = vec4(0.0);
    
    for (int i = 0; i < 9; i++) {
        vec2 offset = avg_offset[i] * texelSize * avgBlurFactor;
        result += texture2D(texture0, coord + offset) * avg_kernel[i];
    }
    
    return result;
}

void main(void) {
    // 初始高斯模糊
    vec4 color = gaussianBlur(tex_coord0);
    
    // 应用多次平均模糊
    for (int pass = 0; pass < avgPasses; pass++) {
        color = mix(color, averageBlur(tex_coord0), 0.4);
    }
    
    gl_FragColor = color;
}
"""

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

// 控制参数
uniform float blurRadius;      // 主模糊半径 (0.0 - 5.0)
uniform float avgBlurFactor;   // 平均模糊强度 (0.0 - 1.0)
uniform int avgPasses;         // 平均模糊次数 (1-4)
uniform vec2 textureSize;      // 纹理尺寸

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

class AdvancedBlurWidget(Widget):
    rect = ObjectProperty(None)
    blur_radius = NumericProperty(2.0)
    avg_blur_factor = NumericProperty(0.5)
    avg_passes = NumericProperty(2)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 混合模糊着色器代码
        self.shader_code = fshader
        
        # 创建渲染上下文
        self.canvas = RenderContext(
            use_parent_projection=True,
            use_parent_modelview=True
        )
        
        # 设置着色器
        self.canvas.shader.fs = self.shader_code
        
        # 创建测试图像
        self.texture = Image("input_texture.png").texture   # self.create_test_image()
        self.size=(self.texture.size[0]*2,self.texture.size[1]*2  )  

        with self.canvas:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(texture=self.texture, size=self.texture.size, pos=self.pos)
            self.rect2 = Rectangle(texture=self.texture, size=self.texture.size, pos=(self.pos[0]+self.texture.size[0], self.pos[1]))
        # 绑定事件
        self.bind(
            pos=self.update_rect, 
            size=self.update_rect,
            blur_radius=self.update_uniforms,
            avg_blur_factor=self.update_uniforms,
            avg_passes=self.update_uniforms
        )
        
        # 初始化统一变量
        self.update_uniforms()
        
        # 调试输出
        if not self.canvas.shader.success:
            print("Shader编译错误:", self.canvas.shader.log)
    
    def update_rect(self, *args):
        """更新矩形位置和尺寸"""
        self.rect.pos = self.pos
        self.rect.size = self.texture.size
        self.rect2.pos = (self.pos[0]+self.texture.size[0], self.pos[1])
        self.update_uniforms()
    
    def update_uniforms(self, *args):
        """更新着色器统一变量"""
        if self.rect and self.rect.texture:
            self.canvas['textureSize'] = self.rect.size
        # if self.rect2 and self.rect2.texture:
        #     self.canvas['textureSize2'] = self.rect2.size

        self.canvas['blurRadius'] = self.blur_radius
        self.canvas['avgBlurFactor'] = self.avg_blur_factor
        self.canvas['avgPasses'] = self.avg_passes

class AdvancedBlurApp(App):
    def build(self):
        # 创建主布局
        layout = BoxLayout(orientation='vertical')
        
        # 创建模糊窗口
        blur_widget = AdvancedBlurWidget()
        layout.add_widget(blur_widget)
        
        # 创建控制面板
        controls = BoxLayout(orientation='vertical', size_hint=(1, 0.3))
        
        # 高斯模糊半径控制
        gauss_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.5))
        gauss_layout.add_widget(Label(text="Gaussian Blur :", size_hint=(0.3, 1)))
        slider = Slider(min=0.0, max=100.0, value=2.0)
        slider.bind(value=lambda i, v: setattr(blur_widget, 'blur_radius', v))
        gauss_layout.add_widget(slider)
        
        # 平均模糊强度控制
        avg_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.5))
        avg_layout.add_widget(Label(text="Average blur strength:", size_hint=(0.3, 1)))
        avg_slider = Slider(min=0.0, max=50, value=0.5)
        avg_slider.bind(value=lambda i, v: setattr(blur_widget, 'avg_blur_factor', v))
        avg_layout.add_widget(avg_slider)
        
        # 平均模糊次数控制
        passes_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.5))
        passes_layout.add_widget(Label(text="Average blur passes:", size_hint=(0.3, 1)))
        passes_slider = Slider(min=1, max=5, value=2, step=1)
        passes_slider.bind(value=lambda i, v: setattr(blur_widget, 'avg_passes', int(v)))
        passes_layout.add_widget(passes_slider)
        
        # 添加到控制面板
        controls.add_widget(gauss_layout)
        controls.add_widget(avg_layout)
        controls.add_widget(passes_layout)
        
        # 添加到主布局
        layout.add_widget(controls)
        
        return layout

if __name__ == '__main__':
    AdvancedBlurApp().run()