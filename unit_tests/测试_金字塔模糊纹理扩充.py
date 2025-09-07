from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
from kivy.core.image import Image as CoreImage
from kivy.clock import Clock
from kivy.graphics import RenderContext, Color, Rectangle, Fbo
import sys
from pathlib import Path

# 自动添加项目根目录和 src 目录
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / "src"))
# 假设这些类已定义或导入
from src.components.common.blureffect import ExpansionOnePassStrongBlur

class PyramidBlurWidget(Widget):
    def __init__(self, **kwargs):
        super(PyramidBlurWidget, self).__init__(**kwargs)
        
        # 初始化模糊处理器
        self.blur_processor = ExpansionOnePassStrongBlur()

        # 默认参数
        self.blur_radius = 1.5
        self.iterations = 3
        self.expansion_factor = 1.2
        
        # 加载测试纹理
        self.original_texture = self.load_test_texture()
        
        # 初始处理
        self.process_texture()
        
        # 绘制原始纹理和处理后的纹理
        self.draw_textures()
    
    def load_test_texture(self):
        # 尝试加载测试图像
        try:
            # 使用Kivy内置图像或自定义路径
            from kivy.core.image import Image as CoreImage
            from kivy.resources import resource_find
            
            # 如果找不到内置图像，创建一个简单的纹理
            from kivy.graphics import Color, Rectangle
            from kivy.core.image import Image
            
            # 创建一个简单的彩色纹理
            size = (256, 256)
            fbo = Fbo(size=size)
            with fbo:
                Color(1, 0.5, 0, 1)
                Rectangle(pos=(0, 0), size=size)
                Color(0, 0.7, 1, 1)
                Rectangle(pos=(64, 64), size=(128, 128))
                Color(0, 1, 0.5, 1)
                Rectangle(pos=(128, 128), size=(64, 64))
            fbo.draw()
            return fbo.texture
        
        except Exception as e:
            print(f"Error loading texture: {e}")
            # 创建回退纹理
            size = (256, 256)
            fbo = Fbo(size=size)
            with fbo:
                Color(1, 0, 0, 1)
                Rectangle(pos=(0, 0), size=size)
            
            fbo.draw()
            return fbo.texture
    
    def process_texture(self):
        # 使用模糊处理器处理纹理
        self.processed_texture ,self.offset= self.blur_processor.process(
            self.original_texture
        )

    def draw_textures(self):
        # 清除之前的绘制
        self.canvas.clear()
        
        # 绘制原始纹理
        with self.canvas:
            Color(1, 1, 1, 1)
            Rectangle(
                texture=self.original_texture,
                pos=(50, 150),
                size=self.original_texture.size
            )
            
            # 绘制处理后的纹理（考虑偏移）
            Rectangle(
                texture=self.processed_texture,
                pos=(350 - self.offset[0], 150 - self.offset[1]),
                size=self.processed_texture.size
            )
            
            # 添加标签
            Color(0, 0, 0, 1)
            self.original_label = Label(
                text="Original Texture",
                pos=(50, 100),
                size=(200, 30)
            )
            
            self.processed_label = Label(
                text="Blurred Texture",
                pos=(350, 100),
                size=(200, 30)
            )
        
        # 将标签添加到画布
        self.add_widget(self.original_label)
        self.add_widget(self.processed_label)

    def update_blur_radius(self, instance, value):
        self.blur_radius = value
        self.update_processing()

    def update_iterations(self, instance, value):
        self.iterations = int(value)
        self.update_processing()
    
    def update_expansion_factor(self,instance, value):
        self.expansion_factor = value
        self.update_processing()
    
    def update_processing(self):
        # 使用Clock延迟处理，避免过于频繁的更新
        Clock.unschedule(self._do_processing)
        Clock.schedule_once(self._do_processing, 0.1)
    
    def _do_processing(self, dt):
        self.process_texture()
        self.draw_textures()


class PyramidBlurApp(App):
    def build(self):
        # 创建主布局
        layout = BoxLayout(orientation='vertical')
        
        # 创建模糊窗口
        blur_widget = PyramidBlurWidget()
        layout.add_widget(blur_widget)
        
        # 创建控制面板
        controls = BoxLayout(orientation='vertical', size_hint=(1, 0.3))
        
        # 模糊半径控制
        blur_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.33))
        blur_layout.add_widget(Label(text="Blur Radius:", size_hint=(0.3, 1)))
        blur_slider = Slider(min=0.1, max=5.0, value=1.5)
        blur_slider.bind(value=blur_widget.update_blur_radius)
        blur_layout.add_widget(blur_slider)
        
        # 迭代次数控制
        iter_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.33))
        iter_layout.add_widget(Label(text="Iterations:", size_hint=(0.3, 1)))
        iter_slider = Slider(min=1, max=8, value=3, step=1)
        iter_slider.bind(value=blur_widget.update_iterations)
        iter_layout.add_widget(iter_slider)
        
        # 扩展因子控制
        exp_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.33))
        exp_layout.add_widget(Label(text="Expansion:", size_hint=(0.3, 1)))
        exp_slider = Slider(min=1.0, max=2.0, value=1.2)
        exp_slider.bind(value=blur_widget.update_expansion_factor)
        exp_layout.add_widget(exp_slider)
        
        # 添加到控制面板
        controls.add_widget(blur_layout)
        controls.add_widget(iter_layout)
        controls.add_widget(exp_layout)
        
        # 添加到主布局
        layout.add_widget(controls)
        
        return layout


if __name__ == '__main__':
    PyramidBlurApp().run()