from kivy.graphics import RenderContext, Rectangle
from kivy.uix.widget import Widget

# GLSL 着色器代码
gradient_shader = '''
$HEADER$  // Kivy 会自动填充默认头文件

uniform vec2 u_size;
uniform vec4 u_start_color;
uniform vec4 u_end_color;

void main(void) {
    // 计算当前片元位置 (0.0 到 1.0)
    vec2 position = gl_FragCoord.xy / u_size;
    
    // 创建水平渐变
    vec4 color = mix(u_start_color, u_end_color, position.x);
    
    // 应用透明度
    gl_FragColor = color * v_color;
}
'''

class ShaderGradientWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 创建渲染上下文
        self.canvas = RenderContext()
        self.canvas.shader.fs = gradient_shader
        
        # 设置初始颜色
        self.canvas['u_start_color'] = (1, 0, 0, 1)  # 红色
        self.canvas['u_end_color'] = (0, 0, 1, 1)    # 蓝色
        
        with self.canvas:
            self.rect = Rectangle(pos=self.pos, size=self.size)
        
        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.canvas['u_size'] = self.size

radial_shader = '''
$HEADER$

uniform vec2 u_center;
uniform vec4 u_inner_color;
uniform vec4 u_outer_color;
uniform float u_radius;

void main(void) {
    // 计算当前点到中心的距离
    float dist = distance(gl_FragCoord.xy, u_center);
    
    // 计算渐变比例 (0.0 在中心, 1.0 在边缘)
    float t = clamp(dist / u_radius, 0.0, 1.0);
    
    // 创建径向渐变
    vec4 color = mix(u_inner_color, u_outer_color, t);
    
    gl_FragColor = color * v_color;
}
'''

class RadialGradientWidget(ShaderGradientWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.canvas.shader.fs = radial_shader
    
    def update_rect(self, *args):
        super().update_rect(*args)
        # 更新着色器参数
        center = (self.center_x, self.center_y)
        self.canvas['u_center'] = center
        self.canvas['u_radius'] = min(self.width, self.height) / 2
        self.canvas['u_inner_color'] = (1, 1, 0, 1)  # 黄色
        self.canvas['u_outer_color'] = (0, 0.5, 0, 1)  # 绿色

from kivy.app import App
class TestApp(App):
    def build(self):
        return RadialGradientWidget()
    
TestApp().run()
