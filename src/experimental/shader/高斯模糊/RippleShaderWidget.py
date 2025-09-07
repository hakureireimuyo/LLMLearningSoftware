from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import RenderContext, Rectangle, Color
from kivy.clock import Clock
from kivy.properties import NumericProperty, ListProperty
from kivy.graphics.context_instructions import Scale, Translate, PushMatrix, PopMatrix

class RippleShaderWidget(Widget):
    time = NumericProperty(0)
    resolution = ListProperty([800.0, 600.0])  # 默认分辨率
    
    def __init__(self, **kwargs):
        super(RippleShaderWidget, self).__init__(**kwargs)
        
        # 创建渲染上下文
        self.canvas = RenderContext()
        
        # 波纹着色器 - 修复变量声明问题
        shader_code = '''
        $HEADER$
        uniform float time;
        uniform vec2 resolution;
        
        void main(void) {
            // 使用Kivy提供的标准纹理坐标变量
            vec2 uv = tex_coord0.st;
            
            // 计算中心距离（使用标准化坐标）
            vec2 center = vec2(0.5, 0.5);
            float dist = distance(uv, center);
            
            // 创建波纹效果
            float wave = sin(dist * 20.0 - time * 5.0) * 0.5 + 0.5;
            
            // 生成颜色
            vec3 color = vec3(wave * 0.5, wave * 0.7, wave);
            gl_FragColor = vec4(color, 1.0);
        }
        '''
        
        # 设置着色器代码
        self.canvas.shader.fs = shader_code
        
        # 初始绘制矩形
        with self.canvas:
            PushMatrix()
            self.scale = Scale(1, -1, 1)  # 翻转Y轴
            self.translate = Translate(-self.width/2, -self.height/2)
            self.rect = Rectangle(pos=self.pos, size=self.size)
            PopMatrix()
        
        # 绑定属性和定时器
        Clock.schedule_interval(self.update_time, 1/60.)
        self.bind(
            pos=self.update_rect,
            size=self.update_rect
        )
        
        # 初始化分辨率
        self.resolution = [self.width, self.height]
        self.canvas['resolution'] = self.resolution
    
    def update_time(self, dt):
        """更新时间并设置着色器参数"""
        self.time += dt
        self.canvas['time'] = self.time  # 设置time uniform变量
    
    def update_rect(self, *args):
        """更新矩形位置和大小"""
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.resolution = [self.width, self.height]
        self.canvas['resolution'] = self.resolution
        self.translate.xy = (-self.width/2, -self.height/2)

class RippleApp(App):
    def build(self):
        return RippleShaderWidget()

if __name__ == '__main__':
    RippleApp().run()