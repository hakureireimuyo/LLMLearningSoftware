"""
实验性,组件可以获取子组建的渲染结果,然后裁切
对于部分区域进行高斯模糊,实现半透明模糊效果的纹理

"""

from kivy.uix.image import Image
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import RenderContext, Color, Rectangle, Fbo, ClearBuffers, ClearColor
from kivy.graphics.texture import Texture
from kivy.properties import ListProperty, NumericProperty
from kivy.clock import Clock
from .bulrr_provesser import TextureBlurProcessor

class BlurEffect(FloatLayout):
    # 定义模糊区域列表，每个区域为(x, y, width, height)
    blur_regions = ListProperty([])
    # 模糊处理迭代次数
    blur_iterations = NumericProperty(1)
    # 模糊半径
    blur_radius = NumericProperty(0.5)
    # 降采样因子
    downscale_factor = NumericProperty(1.5)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._fbo = None
        self._texture = None
        self.blur_processor = TextureBlurProcessor()
        self.content_layout = BoxLayout(size_hint=(None, None), size=(400, 400), pos=(100, 100))
        self.blur_layout = FloatLayout(size_hint=(None, None), size=(400, 400), pos=(100, 100))
        self.add_widget(self.blur_layout)
        self.add_widget(self.content_layout)
        
        # 绑定尺寸变化事件
        self.bind(size=self._update_fbo, pos=self._update_fbo)
        self.content_layout.bind(size=self._update_fbo, pos=self._update_fbo)
        
        # 初始渲染
        Clock.schedule_once(self._update_fbo)

    def _update_fbo(self, *args):
        """创建或更新FBO以捕获子组件渲染"""
        if self.content_layout.width == 0 or self.content_layout.height == 0:
            return
            
        # 创建FBO
        if self._fbo is None or self._fbo.size != self.content_layout.size:
            self._fbo = Fbo(size=self.content_layout.size)
        
        # 渲染子组件到FBO
        with self._fbo:
            ClearBuffers()
            ClearColor(0, 0, 0, 0)
        self._fbo.draw()
        
        # 获取完整纹理
        self._texture = self._fbo.texture
        self._texture.flip_vertical()  # Kivy FBO纹理是倒置的
        
        # 触发模糊处理
        self._process_blur_regions()

    def _process_blur_regions(self):
        """处理所有模糊区域"""
        if not self._texture or not self.blur_regions:
            return
            
        # 设置模糊参数
        self.blur_processor.set_blur_parameters(
            blur_radius=self.blur_radius,
            iterations=self.blur_iterations,
            downscale_factor=self.downscale_factor
        )
        
        # 清除之前的模糊绘制
        self.blur_layout.canvas.before.clear()
        
        # 为每个模糊区域创建处理后的纹理
        for region in self.blur_regions:
            x, y, width, height = region
            # 裁剪纹理区域
            crop_x = max(0, min(x, self._texture.width - 1))
            crop_y = max(0, min(y, self._texture.height - 1))
            crop_width = min(width, self._texture.width - crop_x)
            crop_height = min(height, self._texture.height - crop_y)
            
            if crop_width <= 0 or crop_height <= 0:
                continue
            
            # 创建临时FBO进行裁剪
            crop_fbo = Fbo(size=(crop_width, crop_height))
            with crop_fbo:
                Color(1, 1, 1)
                # 计算纹理坐标（注意垂直翻转）
                tex_x = crop_x / self._texture.width
                tex_y = crop_y / self._texture.height
                tex_width = crop_width / self._texture.width
                tex_height = crop_height / self._texture.height
                
                Rectangle(
                    texture=self._texture,
                    size=crop_fbo.size,
                    tex_coords=(
                        tex_x, 1 - tex_y - tex_height,  # 左下
                        tex_x + tex_width, 1 - tex_y - tex_height,  # 右下
                        tex_x + tex_width, 1 - tex_y,  # 右上
                        tex_x, 1 - tex_y  # 左上
                    )
                )
            crop_fbo.draw()
            cropped_texture = crop_fbo.texture
            
            # 设置输入纹理并处理模糊
            self.blur_processor.set_input_texture(cropped_texture)
            blurred_texture = self.blur_processor.process()
            
            # 在blur_layout的背景中绘制模糊后的纹理
            with self.blur_layout.canvas.before:
                Color(1, 1, 1, 1)
                Rectangle(
                    texture=blurred_texture,
                    pos=(crop_x + self.blur_layout.x, crop_y + self.blur_layout.y),
                    size=(crop_width, crop_height)
                )

    def add_widget_to_content(self, widget):
        """添加子组件到内容区域"""
        self.content_layout.add_widget(widget)

    def add_widget_to_foreground(self, widget):
        """添加子组件到前景（不会被模糊）"""
        self.blur_layout.add_widget(widget)

    def add_blur_region(self, x, y, width, height):
        """添加模糊区域"""
        self.blur_regions.append((x, y, width, height))
        self._process_blur_regions()

    def clear_blur_regions(self):
        """清除所有模糊区域"""
        self.blur_regions = []
        self.blur_layout.canvas.before.clear()


class TestApp(App):
    def build(self):
        effect = BlurEffect()
        
        # 添加背景内容
        from kivy.uix.button import Button
        from kivy.uix.label import Label
        
        # 添加到内容区域（会被模糊）
        effect.add_widget_to_content(Button(text="Background Button", size_hint=(None, None), size=(200, 100), pos=(100, 100)))
        effect.add_widget_to_content(Label(text="Background Label", color=(1, 0, 0, 1), pos=(50, 50)))
        
        # 添加模糊区域（整个内容区域）
        effect.add_blur_region(0, 0, 400, 400)
        
        # 添加前景组件（不会被模糊）
        effect.add_widget_to_foreground(Button(text="Foreground Button", size_hint=(None, None), size=(200, 50), pos=(150, 200)))
        
        return effect

if __name__ == '__main__':
    TestApp().run()