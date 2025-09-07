import time
from kivy.graphics import Color, Rectangle

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
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.app import MDApp
from pathlib import Path
import copy
import time
from kivy.graphics import Color, Rectangle
from kivy.core.image import Image as CoreImage

class CenteredPaddedPyramidBlur:
    """
    支持输入纹理中心居中透明扩展、金字塔模糊、自动高斯半径/层数/缩放因子控制的“一站式”模糊处理器
    只暴露一个接口: process(texture, blur_radius=None, iterations=None, downscale_factor=None, pad_scale=1.0, save_debug=False)
    返回 (处理后纹理, (内容区offset_x, offset_y))
    """

    def __init__(self):
        self.fbo_pool = []
        # 默认参数
        self.default_downscale_factor = 0.5
        self.default_iterations = 2
        self.default_blur_radius = 1.0

        # 高斯核更快衰减，避免边缘脏色
        self.gaussian_blur_shader = '''
        $HEADER$
        uniform vec2 direction;
        uniform float blurSize;
        uniform vec2 textureSize;

        const float weights[5] = float[](
            0.5, 0.25, 0.15, 0.07, 0.03
        );

        void main(void) {
            vec2 texelSize = 1.0 / textureSize;
            vec4 sum = vec4(0.0);
            float totalAlpha = 0.0;
            for (int i = 0; i < 5; i++) {
                vec2 offset = direction * texelSize * blurSize * float(i);
                vec4 s1 = texture2D(texture0, tex_coord0 + offset);
                vec4 s2 = texture2D(texture0, tex_coord0 - offset);
                sum.rgb += s1.rgb * s1.a * weights[i];
                sum.rgb += s2.rgb * s2.a * weights[i];
                sum.a   += s1.a * weights[i];
                sum.a   += s2.a * weights[i];
                totalAlpha += s1.a * weights[i];
                totalAlpha += s2.a * weights[i];
            }
            if (sum.a > 0.0)
                gl_FragColor = vec4(sum.rgb / sum.a, sum.a);
            else
                gl_FragColor = vec4(0.0,0.0,0.0,0.0);
        }
        '''

        self.blend_shader = '''
        $HEADER$
        uniform sampler2D texture1;
        void main(void) {
            vec4 color0 = texture2D(texture0, tex_coord0);
            vec4 color1 = texture2D(texture1, tex_coord0);
            // 预乘混合, 防止透明边缘污染
            float a = color0.a + color1.a - color0.a * color1.a;
            vec3 rgb = (color0.rgb * color0.a * (1.0 - color1.a) + color1.rgb * color1.a) / max(a, 1e-5);
            gl_FragColor = vec4(rgb, a);
        }
        '''

    def get_fbo(self, size):
        for fbo in self.fbo_pool:
            if fbo.size == size:
                self.fbo_pool.remove(fbo)
                fbo.clear()
                fbo.clear_buffer()
                return fbo
        from kivy.graphics.fbo import Fbo
        fbo = Fbo(size=size)
        fbo.clear()
        return fbo

    def release_fbo(self, fbo):
        fbo.clear()
        fbo.clear_buffer()
        self.fbo_pool.append(fbo)

    def _resize(self, texture, target_size):
        fbo = self.get_fbo(target_size)
        fbo.shader.fs = None
        with fbo:
            Color(1, 1, 1, 0)
            Rectangle(texture=texture, size=target_size)
        fbo.draw()
        result = fbo.texture
        self.release_fbo(fbo)
        return result

    def _gaussian_blur(self, texture, size, blur_radius):
        # 水平
        horizontal_fbo = self.get_fbo(size)
        horizontal_fbo.shader.fs = self.gaussian_blur_shader
        horizontal_fbo['direction'] = (1.0, 0.0)
        horizontal_fbo['blurSize'] = blur_radius
        horizontal_fbo['textureSize'] = (float(size[0]), float(size[1]))
        with horizontal_fbo:
            Color(1, 1, 1, 0)
            Rectangle(texture=texture, size=size)
        horizontal_fbo.draw()
        horizontal_texture = horizontal_fbo.texture
        self.release_fbo(horizontal_fbo)
        # 垂直
        vertical_fbo = self.get_fbo(size)
        vertical_fbo.shader.fs = self.gaussian_blur_shader
        vertical_fbo['direction'] = (0.0, 1.0)
        vertical_fbo['blurSize'] = blur_radius
        vertical_fbo['textureSize'] = (float(size[0]), float(size[1]))
        with vertical_fbo:
            Color(1, 1, 1, 0)
            Rectangle(texture=horizontal_texture, size=size)
        vertical_fbo.draw()
        result = vertical_fbo.texture
        self.release_fbo(vertical_fbo)
        return result

    def _build_gaussian_pyramid(self, texture, levels, downscale_factor):
        pyramid = []
        current_texture = texture
        current_size = texture.size
        pyramid.append({"texture": current_texture, "size": current_size})
        for level in range(1, levels):
            new_size = (
                max(1, int(current_size[0] * downscale_factor)),
                max(1, int(current_size[1] * downscale_factor))
            )
            blurred = self._gaussian_blur(current_texture, current_size, 1.0)
            downscaled = self._resize(blurred, new_size)
            pyramid.append({"texture": downscaled, "size": new_size})
            current_texture = downscaled
            current_size = new_size
        return pyramid

    def _reconstruct_pyramid(self, pyramid):
        if not pyramid:
            return None
        current_texture = pyramid[-1]["texture"]
        for level in range(len(pyramid) - 2, -1, -1):
            target_size = pyramid[level]["size"]
            upscaled = self._resize(current_texture, target_size)
            blended = self._blend(upscaled, pyramid[level]["texture"])
            current_texture = blended
        return current_texture

    def _blend(self, texture1, texture2):
        size = texture1.size
        fbo = self.get_fbo(size)
        fbo.shader.fs = self.blend_shader
        with fbo:
            Color(1, 1, 1, 0)
            Rectangle(size=size, texture=texture1, texture1=texture2)
        fbo.draw()
        result = fbo.texture
        self.release_fbo(fbo)
        return result

    def _pad_and_center(self, texture, scale):
        orig_w, orig_h = texture.size
        target_w = int(orig_w * scale)
        target_h = int(orig_h * scale)
        pad_w = max(target_w, orig_w)
        pad_h = max(target_h, orig_h)
        fbo = self.get_fbo((pad_w, pad_h))
        offset_x = (pad_w - orig_w) // 2
        offset_y = (pad_h - orig_h) // 2
        with fbo:
            Color(1, 1, 1, 0)
            Rectangle(size=(pad_w, pad_h))
            Color(1, 1, 1, 1)
            Rectangle(texture=texture, size=texture.size, pos=(offset_x, offset_y))
        fbo.draw()
        padded_texture = fbo.texture
        self.release_fbo(fbo)
        return padded_texture, (offset_x, offset_y)

    def process(self, texture, blur_radius=None, iterations=None, downscale_factor=None, pad_scale=1.0, save_debug=True):
        """
        对输入纹理进行中心透明扩展与金字塔模糊
        :param texture:      输入Kivy纹理
        :param blur_radius:  高斯模糊半径(float)
        :param iterations:   金字塔层数(int)
        :param downscale_factor: 每层缩放因子(float)
        :param pad_scale:    扩展比例(float, 1.0为不扩展)
        :param save_debug:   是否保存中间结果到temp目录以调试
        :return: (处理后纹理, (内容区左上角offset_x, offset_y))
        """
        if not texture or texture.size[0] == 0 or texture.size[1] == 0:
            return texture, (0, 0)

        # 参数处理
        blur_radius = blur_radius if blur_radius is not None else self.default_blur_radius
        iterations = iterations if iterations is not None else self.default_iterations
        downscale_factor = downscale_factor if downscale_factor is not None else self.default_downscale_factor

        # 1. 透明扩展
        padded_texture, offset = self._pad_and_center(texture, pad_scale)
        padded_size = padded_texture.size

        # 2. 初始模糊
        initial_blur = self._gaussian_blur(padded_texture, padded_size, blur_radius)

        # 3. 构建金字塔
        pyramid_levels = min(iterations + 1, 8)
        pyramid = self._build_gaussian_pyramid(initial_blur, pyramid_levels, downscale_factor)

        # 4. 重建
        if pyramid_levels > 1:
            reconstructed = self._reconstruct_pyramid(pyramid)
        else:
            reconstructed = initial_blur

        # 5. 最终模糊
        final_blur = self._gaussian_blur(reconstructed, padded_size, blur_radius * 0.5)

        # 可选：保存调试图像
        print(save_debug)
        if save_debug:
            import os
            os.makedirs("temp", exist_ok=True)
            CoreImage(texture).save("temp/input.png")
            CoreImage(padded_texture).save("temp/padded.png")
            CoreImage(initial_blur).save("temp/initial_blur.png")
            for i, item in enumerate(pyramid):
                CoreImage(item["texture"]).save(f"temp/pyramid_{i}.png")
            CoreImage(reconstructed).save("temp/reconstructed.png")
            CoreImage(final_blur).save("temp/final_blur.png")

        return final_blur, offset
    
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

class PyramidBlurWidget(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.adaptive_size = True
        # 创建新的调试步骤容器
        
        # 初始化模糊处理器
        self.blur_processor = CenteredPaddedPyramidBlur()

        # 默认参数
        self.blur_radius = 1.5
        self.iterations = 1
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
        self.processed_texture, self.offset= self.blur_processor.process(
            self.original_texture,
            blur_radius=self.blur_radius,
            iterations=self.iterations,
            pad_scale=self.expansion_factor
        )
        print(self.original_texture.size)
        print(self.processed_texture.size,self.offset)
        print(self.blur_radius,self.iterations,self.expansion_factor)
        
        # 绘制调试步骤

    def draw_textures(self):
        # 清除之前的绘制
        self.canvas.clear()
        
        # 绘制原始纹理
        with self.canvas:
            Color(1, 1, 1 , 1)
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

        # 清空调试步骤以防止重复绘制
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


class PyramidBlurApp(MDApp):
    def build(self):
        # 创建主布局
        layout = MDBoxLayout(orientation='vertical')

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