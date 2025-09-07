from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.graphics import RenderContext, Color, Rectangle, Fbo
from kivy.graphics.texture import Texture
from kivy.properties import NumericProperty, ObjectProperty
from kivy.core.image import Image
from kivy.clock import Clock

# 水平模糊着色器 (修正版)
horizontal_blur_shader = '''
$HEADER$

uniform vec2 textureSize;
uniform float blurRadius;

const float kernel[9] = float[](
    0.0162162162, 0.0540540541, 0.1216216216,
    0.1945945946, 0.2270270270,
    0.1945945946, 0.1216216216, 0.0540540541, 0.0162162162
);

void main(void) {
    vec2 texelSize = 1.0 / textureSize;
    vec4 result = vec4(0.0);
    
    for (int i = 0; i < 9; i++) {
        float offsetX = (float(i) - 4.0) * texelSize.x * blurRadius;
        vec2 coord = vec2(tex_coord0.x + offsetX, tex_coord0.y);
        result += texture2D(texture0, coord) * kernel[i];
    }
    
    gl_FragColor = result;
}
'''

# 垂直模糊着色器 (修正版)
vertical_blur_shader = """
$HEADER$

uniform vec2 textureSize;
uniform float blurRadius;

const float kernel[9] = float[](
    0.0162162162, 0.0540540541, 0.1216216216,
    0.1945945946, 0.2270270270,
    0.1945945946, 0.1216216216, 0.0540540541, 0.0162162162
);

void main(void) {
    vec2 texelSize = 1.0 / textureSize;
    vec4 result = vec4(0.0);
    
    for (int i = 0; i < 9; i++) {
        float offsetY = (float(i) - 4.0) * texelSize.y * blurRadius;
        vec2 coord = vec2(tex_coord0.x, tex_coord0.y + offsetY);
        result += texture2D(texture0, coord) * kernel[i];
    }
    
    gl_FragColor = result;
}
"""

class FboBlurWidget(Widget):
    iterations = NumericProperty(1)  # 模糊迭代次数
    blur_radius = NumericProperty(0.5)  # 模糊半径
    original_texture = ObjectProperty(None)  # 原始纹理
    result_texture = ObjectProperty(None)   # 最终模糊后的纹理
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 加载原始纹理
        self.original_texture = Image("input_texture.png").texture
        
        # 初始设置结果纹理
        self.result_texture = self.original_texture
        self.size = self.original_texture.size
        self.size_hint = (None, None)
        
        # 创建屏幕绘制矩形
        with self.canvas:
            Color(1, 1, 1, 1)
            self.result_rect = Rectangle(texture=self.result_texture, pos=self.pos, size=self.size)
        
        # 绑定属性变化事件
        self.bind(
            pos=self.update_result_rect,
            iterations=self.update_blur,
            blur_radius=self.update_blur
        )
        
        # 初始模糊处理
        Clock.schedule_once(lambda dt: self.update_blur(), 0.1)
    
    def update_result_rect(self, *args):
        """更新结果矩形的位置"""
        if self.result_rect:
            self.result_rect.pos = self.pos
    
    def update_blur(self, *args):
        """执行模糊处理 - 每次从原始纹理开始"""
        if not self.original_texture:
            return
            
        # 始终从原始纹理开始处理
        current_texture = self.original_texture
        size = self.original_texture.size
        
        # 根据迭代次数进行循环处理
        for i in range(self.iterations):
            # 水平模糊
            horizontal_fbo = Fbo(size=size)
            horizontal_fbo.shader.fs = horizontal_blur_shader
            
            # 设置水平模糊参数
            with horizontal_fbo:
                horizontal_fbo['textureSize'] = (float(size[0]), float(size[1]))
                horizontal_fbo['blurRadius'] = self.blur_radius
                Color(1, 1, 1, 1)
                Rectangle(texture=current_texture, size=size)
            
            # 渲染水平模糊结果
            horizontal_fbo.draw()
            horizontal_texture = horizontal_fbo.texture
            
            # 垂直模糊
            vertical_fbo = Fbo(size=size)
            vertical_fbo.shader.fs = vertical_blur_shader
            
            # 设置垂直模糊参数
            with vertical_fbo:
                vertical_fbo['textureSize'] = (float(size[0]), float(size[1]))
                vertical_fbo['blurRadius'] = self.blur_radius
                Color(1, 1, 1, 1)
                Rectangle(texture=horizontal_texture, size=size)
            
            # 渲染垂直模糊结果
            vertical_fbo.draw()
            current_texture = vertical_fbo.texture
        
        # 更新结果纹理
        self.result_texture = current_texture
        
        # 更新显示矩形
        if self.result_rect:
            self.result_rect.texture = self.result_texture

class FboBlurApp(App):
    def build(self):
        # 创建主布局
        layout = BoxLayout(orientation='vertical')
        
        # 创建模糊窗口
        blur_widget = FboBlurWidget()
        layout.add_widget(blur_widget)
        
        # 创建控制面板
        controls = BoxLayout(orientation='vertical', size_hint=(1, 0.3))
        
        # 模糊半径控制
        radius_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.5))
        radius_layout.add_widget(Label(text="Blur Radius:", size_hint=(0.3, 1)))
        radius_slider = Slider(min=0.0, max=5.0, value=0.5)
        radius_slider.bind(value=lambda i, v: setattr(blur_widget, 'blur_radius', v))
        radius_layout.add_widget(radius_slider)
        
        # 迭代次数控制
        iter_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.5))
        iter_layout.add_widget(Label(text="Iterations:", size_hint=(0.3, 1)))
        iter_slider = Slider(min=1, max=5, value=1, step=1)
        iter_slider.bind(value=lambda i, v: setattr(blur_widget, 'iterations', int(v)))
        iter_layout.add_widget(iter_slider)
        
        # 添加到控制面板
        controls.add_widget(radius_layout)
        controls.add_widget(iter_layout)
        
        # 添加到主布局
        layout.add_widget(controls)
        
        return layout

if __name__ == '__main__':
    FboBlurApp().run()