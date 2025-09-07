from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import RenderContext, Color, Rectangle, Fbo
from kivy.graphics.texture import Texture
from kivy.properties import NumericProperty, ObjectProperty
from kivy.core.image import Image
from kivy.clock import Clock
import time

# 水平模糊着色器
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

# 垂直模糊着色器
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

# 双线性纹理缩放着色器
resize_shader = """
$HEADER$

void main(void) {
    vec4 tex_color = texture2D(texture0, tex_coord0);
    gl_FragColor = tex_color;
}
"""

class FboBlurWidget(Widget):
    # 当前参数（滑块值）
    current_blur_radius = NumericProperty(0.5)
    current_iterations = NumericProperty(1)
    current_downscale_factor = NumericProperty(0.5)
    
    # 结果纹理
    original_texture = ObjectProperty(None)  # 原始纹理
    result_texture = ObjectProperty(None)   # 最终模糊后的纹理
    processing_time = NumericProperty(0)   # 处理时间（毫秒）
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 创建FBO缓存池
        self.fbo_pool = []
        
        # 加载原始纹理
        self.original_texture = Image("resource\\internal\\image\\1080p.jpg").texture
        self.size=(200,200)
        # 初始设置结果纹理
        self.result_texture = self.original_texture
        self.texture_size = self.original_texture.size
        self.size_hint = (None, None)
        
        # 创建屏幕绘制矩形
        with self.canvas:
            Color(1, 1, 1, 1)
            self.result_rect = Rectangle(texture=self.result_texture, pos=self.pos, size=self.texture_size)
        
        # 初始模糊处理
        Clock.schedule_once(lambda dt: self.apply_blur(), 0.1)
    
    def update_result_rect(self, *args):
        """更新结果矩形的位置"""
        if self.result_rect:
            self.result_rect.pos = self.pos
            self.result_rect.size = self.texture_size
    def get_fbo(self, size):
        """从缓存池获取或创建FBO"""
        for fbo in self.fbo_pool:
            if fbo.size == size:
                self.fbo_pool.remove(fbo)
                return fbo
        return Fbo(size=size)
    
    def release_fbo(self, fbo):
        """将FBO释放回缓存池"""
        self.fbo_pool.append(fbo)
    
    def resize_texture(self, texture, target_size):
        """缩放纹理到目标尺寸"""
        # 获取FBO
        fbo = self.get_fbo(target_size)
        fbo.shader.fs = resize_shader
        
        # 缩放纹理
        with fbo:
            Color(1, 1, 1, 1)
            Rectangle(texture=texture, size=target_size)
        
        fbo.draw()
        result = fbo.texture
        
        # 释放FBO
        self.release_fbo(fbo)
        return result
    
    def apply_blur_pass(self, texture, size, horizontal):
        """应用单个模糊通道"""
        # 获取FBO
        fbo = self.get_fbo(size)
        
        # 设置着色器和参数
        fbo.shader.fs = horizontal_blur_shader if horizontal else vertical_blur_shader
        with fbo:
            fbo['textureSize'] = (float(size[0]), float(size[1]))
            fbo['blurRadius'] = self.current_blur_radius
            Color(1, 1, 1, 1)
            Rectangle(texture=texture, size=size)
        
        # 渲染结果
        fbo.draw()
        result = fbo.texture
        
        # 释放FBO
        self.release_fbo(fbo)
        return result
    
    def apply_blur(self):
        """执行模糊处理 - 使用降采样优化"""
        if not self.original_texture:
            return
            
        start_time = time.time()
        
        # 计算降采样尺寸
        original_size = self.original_texture.size
        downscaled_size = (
            max(1, int(original_size[0] * self.current_downscale_factor)),
            max(1, int(original_size[1] * self.current_downscale_factor))
        )
        
        # 第一步：降采样原始纹理
        downscaled_texture = self.resize_texture(self.original_texture, downscaled_size)
        
        # 处理纹理（在降采样尺寸上）
        current_texture = downscaled_texture
        blur_size = downscaled_size
        
        # 根据迭代次数进行循环处理
        for i in range(self.current_iterations):
            # 水平模糊
            horizontal_texture = self.apply_blur_pass(current_texture, blur_size, True)
            
            # 垂直模糊
            vertical_texture = self.apply_blur_pass(horizontal_texture, blur_size, False)
            
            current_texture = vertical_texture
        
        # 上采样回原始尺寸
        final_texture = self.resize_texture(current_texture, original_size)
        
        # 更新结果纹理
        self.result_texture = final_texture
        
        # 更新显示矩形
        if self.result_rect:
            self.result_rect.texture = self.result_texture
        
        # 计算并记录处理时间
        self.processing_time = (time.time() - start_time) * 1000
        print(f"Blur processed in {self.processing_time:.2f} ms (Size: {original_size} -> {downscaled_size})")

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
        radius_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2))
        radius_layout.add_widget(Label(text="Blur Radius:", size_hint=(0.3, 1)))
        radius_slider = Slider(min=0.1, max=5.0, value=0.5)
        radius_slider.bind(value=lambda i, v: setattr(blur_widget, 'current_blur_radius', v))
        radius_layout.add_widget(radius_slider)
        
        # 迭代次数控制
        iter_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2))
        iter_layout.add_widget(Label(text="Iterations:", size_hint=(0.3, 1)))
        iter_slider = Slider(min=1, max=5, value=1, step=1)
        iter_slider.bind(value=lambda i, v: setattr(blur_widget, 'current_iterations', int(v)))
        iter_layout.add_widget(iter_slider)
        
        # 降采样比例控制
        downscale_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2))
        downscale_layout.add_widget(Label(text="Downscale:", size_hint=(0.3, 1)))
        downscale_slider = Slider(min=0.1, max=1.0, value=0.5)
        downscale_slider.bind(value=lambda i, v: setattr(blur_widget, 'current_downscale_factor', v))
        downscale_layout.add_widget(downscale_slider)
        
        # 应用按钮
        apply_btn = Button(text="apply effect", size_hint=(1, 0.2), background_color=(0.2, 0.6, 1, 1))
        apply_btn.bind(on_press=lambda instance: blur_widget.apply_blur())
        
        # 性能信息显示
        perf_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2))
        perf_layout.add_widget(Label(text="Processing Time:", size_hint=(0.3, 1)))
        time_label = Label(text=f"{blur_widget.processing_time:.1f} ms")
        blur_widget.bind(processing_time=lambda i, v: setattr(time_label, 'text', f"{v:.1f} ms"))
        perf_layout.add_widget(time_label)
        
        # 添加到控制面板
        controls.add_widget(radius_layout)
        controls.add_widget(iter_layout)
        controls.add_widget(downscale_layout)
        controls.add_widget(apply_btn)
        controls.add_widget(perf_layout)
        
        # 添加到主布局
        layout.add_widget(controls)
        
        return layout

if __name__ == '__main__':
    FboBlurApp().run()