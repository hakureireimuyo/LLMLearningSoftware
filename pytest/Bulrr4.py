from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.properties import NumericProperty, ObjectProperty
from kivy.core.image import Image
from kivy.clock import Clock
from kivy.graphics import Fbo, Color, Rectangle
import time
import sys
import os

# 添加项目根目录到模块查找路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.experimental.shader.高斯模糊.bulrr_provesser import TextureBlurProcessor


class FboBlurWidget(Widget):
    current_blur_radius = NumericProperty(0.5)
    current_iterations = NumericProperty(1)
    current_downscale_factor = NumericProperty(0.5)
    
    original_texture = ObjectProperty(None)
    result_texture = ObjectProperty(None)
    processing_time = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.processor = TextureBlurProcessor()
        
        # 加载原始纹理
        try:
            original_image = Image("resource/internal/image/1080p.jpg")
            self.original_texture = original_image.texture
            
            # 定义裁剪区域
            crop_x, crop_y = 200, 200  # 从原图的(200,200)位置开始裁剪
            crop_width, crop_height = 400, 400  # 裁剪400x400的区域
            
            # 创建FBO用于裁剪
            fbo = Fbo(size=(crop_width, crop_height))
            
            with fbo:
                # 清除FBO
                Color(0, 0, 0, 0)
                Rectangle(size=fbo.size)
                
                # 绘制裁剪区域
                Color(1, 1, 1)
                # 计算纹理坐标以进行裁剪
                tex_x = crop_x / self.original_texture.width
                tex_y = crop_y / self.original_texture.height
                tex_width = crop_width / self.original_texture.width
                tex_height = crop_height / self.original_texture.height
                
                # 创建自定义纹理坐标的矩形
                Rectangle(
                    texture=self.original_texture,
                    size=fbo.size,
                    tex_coords=(
                        tex_x, tex_y,  # 左下
                        tex_x + tex_width, tex_y,  # 右下
                        tex_x + tex_width, tex_y + tex_height,  # 右上
                        tex_x, tex_y + tex_height  # 左上
                    )
                )
            
            # 更新FBO
            fbo.draw()
            
            # 获取裁剪后的纹理
            cropped_texture = fbo.texture
            
            # 设置处理器输入纹理
            self.processor.set_input_texture(cropped_texture)
            
            # 创建屏幕绘制矩形
            with self.canvas:
                Color(1, 1, 1, 1)
                self.result_rect = Rectangle(
                    texture=cropped_texture, 
                    pos=self.pos, 
                    size=(crop_width, crop_height)
                )
                
        except Exception as e:
            print(f"Error loading or cropping texture: {e}")
            # 创建备用纹理
            with self.canvas:
                Color(1, 0, 0, 1)
                self.result_rect = Rectangle(pos=self.pos, size=(400, 400))
        
        self.size_hint = (None, None)
        self.size = (400, 400)
        
        # 绑定参数变化
        self.bind(
            current_blur_radius=self.update_processor_params,
            current_iterations=self.update_processor_params,
            current_downscale_factor=self.update_processor_params
        )
        
        # 初始模糊处理
        Clock.schedule_once(lambda dt: self.apply_blur(), 0.1)
    
    def update_processor_params(self, *args):
        self.processor.set_blur_parameters(
            self.current_blur_radius,
            self.current_iterations,
            self.current_downscale_factor
        )
    
    def apply_blur(self):
        if not hasattr(self.processor, 'input_texture') or not self.processor.input_texture:
            return
            
        start_time = time.time()
        processed_texture = self.processor.process()
        
        if self.result_rect and processed_texture:
            self.result_rect.texture = processed_texture

        self.processing_time = (time.time() - start_time) * 1000
        print(f"Blur processed in {self.processing_time:.2f} ms")

class FboBlurApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        
        blur_widget = FboBlurWidget()
        layout.add_widget(blur_widget)
        
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
        
        controls.add_widget(radius_layout)
        controls.add_widget(iter_layout)
        controls.add_widget(downscale_layout)
        controls.add_widget(apply_btn)
        controls.add_widget(perf_layout)
        
        layout.add_widget(controls)
        
        return layout

if __name__ == '__main__':
    FboBlurApp().run()