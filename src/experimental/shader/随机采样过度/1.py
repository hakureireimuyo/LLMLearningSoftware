from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import RenderContext, Color, Mesh,Fbo,Rectangle
from kivy.graphics.texture import Texture
from kivy.properties import NumericProperty, ObjectProperty, ListProperty
from kivy.core.image import Image
from kivy.clock import Clock
import random
import numpy as np
from scipy.spatial import Delaunay
import time

# 顶点着色器 - 处理位置和颜色插值
vertex_shader = '''
$HEADER$
attribute vec2 v_pos;
attribute vec4 v_color;
varying vec4 vertex_color;

void main(void) {
    gl_Position = projection_mat * modelview_mat * vec4(v_pos, 0.0, 1.0);
    vertex_color = v_color;
}
'''

# 片段着色器 - 应用插值函数
fragment_shader = '''
$HEADER$
varying vec4 vertex_color;

void main(void) {
    gl_FragColor = vertex_color;
}
'''

class TextureGeneratorWidget(Widget):
    input_texture = ObjectProperty(None)      # 输入纹理
    output_texture = ObjectProperty(None)     # 输出纹理
    sample_count = NumericProperty(50)        # 采样点数量
    output_size = ListProperty([512, 512])   # 输出纹理大小
    interpolation_type = NumericProperty(0)  # 插值类型：0=线性, 1=指数, 2=平滑步进
    interpolation_param = NumericProperty(1.0) # 插值参数
    processing_time = NumericProperty(0)      # 处理时间（毫秒）
    
    # 采样点：[(x, y, r, g, b, a), ...]
    sample_points = ListProperty([])
    triangles = ListProperty([])  # 三角剖分结果：[v1_idx, v2_idx, v3_idx, ...]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (512, 512)
        
        # 创建渲染上下文
        self.canvas = RenderContext()
        self.canvas.shader.vs = vertex_shader
        self.canvas.shader.fs = fragment_shader
        
        # 初始纹理
        self.input_texture = Image("input_texture.png").texture
        self.output_texture = Texture.create(size=self.output_size)
        
        # 初始生成
        Clock.schedule_once(lambda dt: self.generate_texture(), 0.1)
    
    def generate_samples(self):
        """生成随机采样点"""
        points = []
        for _ in range(self.sample_count):
            # 随机位置 (0-1)
            x = random.random()
            y = random.random()
            
            # 从输入纹理获取颜色
            color = self.get_texture_color(self.input_texture, x, y)
            
            # 添加点 (x, y, r, g, b, a)
            points.extend([x, y, color[0], color[1], color[2], color[3]])
        
        return points
    
    def get_texture_color(self, texture, u, v):
        """获取纹理在(u,v)位置的颜色"""
        width, height = texture.size
        x = int(u * (width - 1))
        y = int(v * (height - 1))
        
        # 获取纹理区域并读取像素
        region = texture.get_region(x, y, 1, 1)
        return region.pixels[:4]  # 返回RGBA
    
    def triangulate_points(self, points):
        """对点集进行三角剖分"""
        # 提取位置坐标
        positions = np.array([(points[i], points[i+1]) for i in range(0, len(points), 6)])
        
        # 使用Delaunay三角剖分
        tri = Delaunay(positions)
        
        # 返回三角形索引
        return tri.simplices.flatten().tolist()
    
    def create_mesh_vertices(self):
        """创建网格顶点数据"""
        vertices = []
        indices = []
        
        # 添加采样点
        for i in range(0, len(self.sample_points), 6):
            x, y, r, g, b, a = self.sample_points[i:i+6]
            vertices.extend([x, y, 0, 0, r, g, b, a])
        
        # 添加三角形索引
        indices = self.triangles
        
        return vertices, indices
    
    def apply_interpolation(self, vertices):
        """应用插值函数 - 在这个实现中，我们通过顶点颜色插值"""
        # 在这个简化版本中，我们依赖GPU的自动插值
        # 更高级的插值可以在片段着色器中实现
        return vertices
    
    def generate_texture(self):
        """生成纹理"""
        start_time = time.time()
        
        # 1. 生成采样点
        self.sample_points = self.generate_samples()
        
        # 2. 三角剖分
        self.triangles = self.triangulate_points(self.sample_points)
        
        # 3. 创建网格顶点
        vertices, indices = self.create_mesh_vertices()
        
        # 4. 应用插值函数
        vertices = self.apply_interpolation(vertices)
        
        # 5. 创建FBO用于渲染
        fbo = Fbo(size=self.output_size)
        with fbo:
            # 清除背景
            Color(0, 0, 0, 1)
            Rectangle(pos=(0, 0), size=self.output_size)
            
            # 绘制三角形网格
            Color(1, 1, 1, 1)
            Mesh(
                vertices=vertices,
                indices=indices,
                mode='triangles',
                fmt=[
                    ('v_pos', 2, 'float'),
                    ('v_tex', 2, 'float'),  # 未使用
                    ('v_color', 4, 'float')
                ]
            )
        
        # 渲染到FBO
        fbo.draw()
        
        # 获取结果纹理
        self.output_texture = fbo.texture
        
        # 计算处理时间
        self.processing_time = (time.time() - start_time) * 1000
        print(f"Texture generated in {self.processing_time:.2f} ms")
        
        # 更新显示
        self.update_display()
    
    def update_display(self):
        """更新显示"""
        # 清除当前绘制
        self.canvas.clear()
        
        # 绘制结果纹理
        with self.canvas:
            Color(1, 1, 1, 1)
            Rectangle(texture=self.output_texture, pos=self.pos, size=self.size)
    
    def on_size(self, instance, value):
        """当尺寸变化时更新显示"""
        self.size = self.output_size
        self.update_display()
    
    def on_pos(self, instance, value):
        """当位置变化时更新显示"""
        self.update_display()

class TextureGeneratorApp(App):
    def build(self):
        # 创建主布局
        layout = BoxLayout(orientation='vertical')
        
        # 创建纹理生成窗口
        generator_widget = TextureGeneratorWidget()
        layout.add_widget(generator_widget)
        
        # 创建控制面板
        controls = BoxLayout(orientation='vertical', size_hint=(1, 0.4))
        
        # 采样点数量控制
        sample_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2))
        sample_layout.add_widget(Label(text="Sampling number:", size_hint=(0.3, 1)))
        sample_slider = Slider(min=10, max=500, value=50, step=1)
        sample_slider.bind(value=lambda i, v: setattr(generator_widget, 'sample_count', int(v)))
        sample_layout.add_widget(sample_slider)
        
        # 输出尺寸控制
        size_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2))
        size_layout.add_widget(Label(text="Output size:", size_hint=(0.3, 1)))
        
        # 宽度
        width_layout = BoxLayout(orientation='horizontal', size_hint=(0.35, 1))
        width_layout.add_widget(Label(text="Width:", size_hint=(0.3, 1)))
        width_slider = Slider(min=32, max=2048, value=512, step=1)
        width_slider.bind(value=lambda i, v: setattr(generator_widget.output_size, 0, int(v)))
        width_layout.add_widget(width_slider)
        
        # 高度
        height_layout = BoxLayout(orientation='horizontal', size_hint=(0.35, 1))
        height_layout.add_widget(Label(text="Height:", size_hint=(0.3, 1)))
        height_slider = Slider(min=32, max=2048, value=512, step=1)
        height_slider.bind(value=lambda i, v: setattr(generator_widget.output_size, 1, int(v)))
        height_layout.add_widget(height_slider)
        
        size_layout.add_widget(width_layout)
        size_layout.add_widget(height_layout)
        
        # 插值类型控制
        interp_type_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2))
        interp_type_layout.add_widget(Label(text="Interpolation type:", size_hint=(0.3, 1)))
        type_slider = Slider(min=0, max=2, value=0, step=1)
        type_slider.bind(value=lambda i, v: setattr(generator_widget, 'interpolation_type', int(v)))
        interp_type_layout.add_widget(type_slider)
        
        # 插值参数控制
        interp_param_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2))
        interp_param_layout.add_widget(Label(text="Interpolation parameter:", size_hint=(0.3, 1)))
        param_slider = Slider(min=0.1, max=5.0, value=1.0)
        param_slider.bind(value=lambda i, v: setattr(generator_widget, 'interpolation_param', v))
        interp_param_layout.add_widget(param_slider)
        
        # 应用按钮
        apply_btn = Button(text="Generate Texture", size_hint=(1, 0.2), background_color=(0.2, 0.6, 1, 1))
        apply_btn.bind(on_press=lambda instance: generator_widget.generate_texture())
        
        # 性能信息显示
        perf_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2))
        perf_layout.add_widget(Label(text="Processing time:", size_hint=(0.3, 1)))
        time_label = Label(text=f"{generator_widget.processing_time:.1f} ms")
        generator_widget.bind(processing_time=lambda i, v: setattr(time_label, 'text', f"{v:.1f} ms"))
        perf_layout.add_widget(time_label)
        
        # 添加到控制面板
        controls.add_widget(sample_layout)
        controls.add_widget(size_layout)
        controls.add_widget(interp_type_layout)
        controls.add_widget(interp_param_layout)
        controls.add_widget(apply_btn)
        controls.add_widget(perf_layout)
        
        # 添加到主布局
        layout.add_widget(controls)
        
        return layout

if __name__ == '__main__':
    TextureGeneratorApp().run()