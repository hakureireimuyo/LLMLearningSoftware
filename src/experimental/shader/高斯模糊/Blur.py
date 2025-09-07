from kivy.clock import Clock
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.properties import StringProperty, ObjectProperty
from kivy.graphics import RenderContext, Fbo, Color, Rectangle
import itertools

# 高斯模糊着色器 (水平+垂直)
header = '''
$HEADER$
uniform vec2 resolution;
uniform float time;
'''

gaussian_blur_shader = header + '''
void main() {
    vec2 uv = tex_coord0;
    vec2 texelSize = 1.0 / resolution;
    vec4 result = vec4(0.0);
    
    // 高斯核权重 (5x5)
    float weights[25] = float[](
        0.003765, 0.015019, 0.023792, 0.015019, 0.003765,
        0.015019, 0.059912, 0.094907, 0.059912, 0.015019,
        0.023792, 0.094907, 0.150342, 0.094907, 0.023792,
        0.015019, 0.059912, 0.094907, 0.059912, 0.015019,
        0.003765, 0.015019, 0.023792, 0.015019, 0.003765
    );
    
    int index = 0;
    for (int y = -2; y <= 2; y++) {
        for (int x = -2; x <= 2; x++) {
            vec2 offset = vec2(float(x), float(y)) * texelSize;
            vec4 sample = texture2D(texture0, uv + offset);
            result += sample * weights[index];
            index++;
        }
    }
    
    gl_FragColor = vec4(result.rgb, 1.0);
}
'''

class GaussianBlurWidget(FloatLayout):
    fs = StringProperty(None)
    texture = ObjectProperty(None)
    
    def __init__(self, blur_intensity=1.0, **kwargs):
        self._blur_intensity = blur_intensity
        self.canvas = RenderContext(
            use_parent_projection=True,
            use_parent_modelview=True,
            use_parent_frag_modelview=True
        )
        
        with self.canvas:
            self.fbo = Fbo(size=self.size)
            self.fbo_color = Color(1, 1, 1, 1)
            self.fbo_rect = Rectangle()
        
        with self.fbo:
            Color(1, 1, 1, 1)
            Rectangle(size=self.size)
        
        super(GaussianBlurWidget, self).__init__(**kwargs)
        Clock.schedule_interval(self.update_glsl, 0)
        self.fs = gaussian_blur_shader
    
    def update_glsl(self, *largs):
        self.canvas['time'] = Clock.get_boottime()
        self.canvas['resolution'] = [float(v) * self._blur_intensity for v in self.size]
        
    def on_fs(self, instance, value):
        shader = self.canvas.shader
        old_value = shader.fs
        shader.fs = value
        if not shader.success:
            shader.fs = old_value
            raise Exception('Shader compilation failed')
    
    def add_widget(self, *args, **kwargs):
        canvas = self.canvas
        self.canvas = self.fbo
        super(GaussianBlurWidget, self).add_widget(*args, **kwargs)
        self.canvas = canvas
    
    def remove_widget(self, *args, **kwargs):
        canvas = self.canvas
        self.canvas = self.fbo
        super(GaussianBlurWidget, self).remove_widget(*args, **kwargs)
        self.canvas = canvas
    
    def on_size(self, instance, value):
        self.fbo.size = value
        self.texture = self.fbo.texture
        self.fbo_rect.size = value
    
    def on_pos(self, instance, value):
        self.fbo_rect.pos = value
    
    def on_texture(self, instance, value):
        self.fbo_rect.texture = value
    
    @property
    def blur_intensity(self):
        return self._blur_intensity
    
    @blur_intensity.setter
    def blur_intensity(self, value):
        self._blur_intensity = max(0.1, min(value, 5.0))  # 限制在0.1-5.0范围

class BlurDemoApp(App):
    def build(self):
        root = FloatLayout()
        
        # 创建高斯模糊组件
        blur_widget = GaussianBlurWidget(blur_intensity=1.5)
        
        # 添加内容到模糊组件
        from kivy.uix.button import Button
        from kivy.uix.label import Label
        
        # 模糊背景
        with blur_widget.fbo:
            Color(0.2, 0.6, 1.0, 1)
            Rectangle(size=(400, 400), pos=(100, 100))
            Color(1, 0.5, 0.3, 1)
            Rectangle(size=(300, 300), pos=(200, 200))
        
        # 添加控件
        btn = Button(
            text='Blurred Button!', 
            size_hint=(None, None),
            size=(200, 60),
            pos=(300, 300)
        )
        blur_widget.add_widget(btn)
        
        label = Label(
            text='Gaussian Blur Effect',
            font_size=24,
            size_hint=(None, None),
            size=(300, 50),
            pos=(250, 400)
        )
        blur_widget.add_widget(label)
        
        root.add_widget(blur_widget)
        
        # 添加控制按钮
        ctrl = FloatLayout(size_hint=(None, None), size=(200, 100), pos=(10, 10))
        increase = Button(text='+ Intensity', size_hint=(1, 0.5), pos_hint={'x':0, 'y':0.5})
        decrease = Button(text='- Intensity', size_hint=(1, 0.5), pos_hint={'x':0, 'y':0})
        
        def adjust_intensity(delta):
            blur_widget.blur_intensity += delta
            print(f"Blur intensity: {blur_widget.blur_intensity:.1f}")
        
        increase.bind(on_release=lambda x: adjust_intensity(0.3))
        decrease.bind(on_release=lambda x: adjust_intensity(-0.3))
        
        ctrl.add_widget(increase)
        ctrl.add_widget(decrease)
        root.add_widget(ctrl)
        
        return root

if __name__ == '__main__':
    BlurDemoApp().run()