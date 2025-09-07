
from kivy.graphics import RenderContext, Color, Rectangle, Fbo, ClearBuffers, ClearColor
from kivy.graphics.texture import Texture
from kivy.graphics.context_instructions import BindTexture
from kivy.core.image import Image
import time
import numpy as np


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

class TextureBlurProcessor:
    def __init__(self):
        # FBO缓存池
        self.fbo_pool = []
        
        # 默认参数
        self.default_blur_radius = 0.5
        self.default_iterations = 1
        self.default_downscale_factor = 0.5

    def get_fbo(self, size):
        """从缓存池获取或创建FBO"""
        for fbo in self.fbo_pool:
            if fbo.size == size:
                self.fbo_pool.remove(fbo)
                return fbo
        return Fbo(size=size)

    def release_fbo(self, fbo):
        """将FBO释放回缓存池"""
        fbo.clear()
        self.fbo_pool.append(fbo)

    def resize_texture(self, texture, target_size):
        """缩放纹理到目标尺寸"""
        fbo = self.get_fbo(target_size)
        fbo.shader.fs = resize_shader
        
        with fbo:
            Color(1, 1, 1, 1)
            Rectangle(texture=texture, size=target_size)
        
        fbo.draw()
        result = fbo.texture
        self.release_fbo(fbo)
        return result

    def apply_blur_pass(self, texture, size, horizontal, blur_radius):
        """应用单个模糊通道"""
        fbo = self.get_fbo(size)
        
        # 设置着色器和参数
        fbo.shader.fs = horizontal_blur_shader if horizontal else vertical_blur_shader
        with fbo:
            fbo['textureSize'] = (float(size[0]), float(size[1]))
            fbo['blurRadius'] = blur_radius
            Color(1, 1, 1, 1)
            Rectangle(texture=texture, size=size)
        
        fbo.draw()
        result = fbo.texture
        self.release_fbo(fbo)
        return result

    def process(self, texture, blur_radius=None, iterations=None, downscale_factor=None):
        """
        执行模糊处理流程
        
        Args:
            texture: 输入纹理
            blur_radius: 模糊半径，如果为None则使用默认值
            iterations: 迭代次数，如果为None则使用默认值
            downscale_factor: 降采样因子，如果为None则使用默认值
            
        Returns:
            处理后的纹理
        """
        if not texture:
            return None
            
        start_time = time.time()
        
        # 使用提供的参数或默认值
        blur_radius = blur_radius if blur_radius is not None else self.default_blur_radius
        iterations = iterations if iterations is not None else self.default_iterations
        downscale_factor = downscale_factor if downscale_factor is not None else self.default_downscale_factor
        
        original_size = texture.size

        # 计算降采样尺寸
        downscaled_size = (
            max(1, int(original_size[0] * downscale_factor)),
            max(1, int(original_size[1] * downscale_factor))
        )
        
        # 第一步：降采样
        if downscale_factor != 1.0:
            downscaled_texture = self.resize_texture(texture, downscaled_size)
        else:
            downscaled_texture = texture
            
        # 处理纹理（在降采样尺寸上）
        current_texture = downscaled_texture
        blur_size = downscaled_size
        
        for i in range(iterations):
            # 水平模糊
            horizontal_texture = self.apply_blur_pass(current_texture, blur_size, True, blur_radius)
            
            # 垂直模糊
            vertical_texture = self.apply_blur_pass(horizontal_texture, blur_size, False, blur_radius)
            
            current_texture = vertical_texture
        
        # 上采样回原始尺寸
        final_texture = self.resize_texture(current_texture, original_size)
        
        # 记录处理时间
        processing_time = (time.time() - start_time) * 1000
        print(f"Blur processed in {processing_time:.2f} ms (Size: {original_size} -> {downscaled_size})")
        
        return final_texture

class TexturePyramidBlurProcessor:
    def __init__(self):
        # FBO缓存池
        self.fbo_pool = []

        # 默认参数
        self.default_downscale_factor = 0.25
        self.default_iterations = 3
        self.default_blur_radius = 1.5

        # 高斯模糊着色器
        self.gaussian_blur_shader = '''
        $HEADER$
        uniform vec2 direction;
        uniform float blurSize;
        uniform vec2 textureSize;

        const float weights[5] = float[](
            0.227027, 0.1945946, 0.1216216, 0.054054, 0.016216
        );

        void main(void) {
            vec2 texelSize = 1.0 / textureSize;
            vec4 color = texture2D(texture0, tex_coord0) * weights[0];

            for (int i = 1; i < 5; i++) {
                vec2 offset = direction * texelSize * blurSize * float(i);
                color += texture2D(texture0, tex_coord0 + offset) * weights[i];
                color += texture2D(texture0, tex_coord0 - offset) * weights[i];
            }

            gl_FragColor = color;
        }
        '''

        # 正确的混合着色器
        self.blend_shader = '''
        $HEADER$
        uniform sampler2D texture1;
        void main(void) {
            vec4 color0 = texture2D(texture0, tex_coord0);
            vec4 color1 = texture2D(texture1, tex_coord0);
            gl_FragColor = (color0 + color1) * 0.5;
        }
        '''

    def get_fbo(self, size):
        """从缓存池获取或创建FBO"""
        for fbo in self.fbo_pool:
            if fbo.size == size:
                self.fbo_pool.remove(fbo)
                return fbo
        fbo = Fbo(size=size)
        return fbo

    def release_fbo(self, fbo):
        """将FBO释放回缓存池"""
        fbo.clear()
        self.fbo_pool.append(fbo)

    def resize_texture(self, texture, target_size):
        """缩放纹理到目标尺寸"""
        fbo = self.get_fbo(target_size)
        fbo.shader.fs = resize_shader
        
        with fbo:
            Color(1, 1, 1, 1)
            Rectangle(texture=texture, size=target_size)
        
        fbo.draw()
        result = fbo.texture
        self.release_fbo(fbo)
        return result

    def apply_gaussian_blur(self, texture, size, blur_radius):
        """应用高斯模糊"""
        # 水平模糊
        horizontal_fbo = self.get_fbo(size)
        horizontal_fbo.shader.fs = self.gaussian_blur_shader

        # 设置统一变量
        horizontal_fbo['direction'] = (1.0, 0.0)
        horizontal_fbo['blurSize'] = blur_radius
        horizontal_fbo['textureSize'] = (float(size[0]), float(size[1]))

        with horizontal_fbo:
            Color(1, 1, 1, 1)
            Rectangle(texture=texture, size=size)

        horizontal_fbo.draw()
        horizontal_texture = horizontal_fbo.texture
        self.release_fbo(horizontal_fbo)

        # 垂直模糊
        vertical_fbo = self.get_fbo(size)
        vertical_fbo.shader.fs = self.gaussian_blur_shader

        # 设置统一变量
        vertical_fbo['direction'] = (0.0, 1.0)
        vertical_fbo['blurSize'] = blur_radius
        vertical_fbo['textureSize'] = (float(size[0]), float(size[1]))

        with vertical_fbo:
            Color(1, 1, 1, 1)
            Rectangle(texture=horizontal_texture, size=size)

        vertical_fbo.draw()
        result = vertical_fbo.texture
        self.release_fbo(vertical_fbo)

        return result

    def build_gaussian_pyramid(self, texture, levels):
        """构建高斯金字塔"""
        if levels < 1:
            return []
            
        pyramid = []
        current_texture = texture
        current_size = texture.size
        
        # 添加原始纹理作为第0层
        pyramid.append({
            "texture": current_texture,
            "size": current_size
        })
        
        # 构建金字塔
        for level in range(1, levels):
            # 缩小尺寸
            new_size = (
                max(1, int(current_size[0] * 0.5)),
                max(1, int(current_size[1] * 0.5))
            )
            
            # 应用高斯模糊
            blurred = self.apply_gaussian_blur(current_texture, current_size, 1.0)
            
            # 降采样
            downscaled = self.resize_texture(blurred, new_size)
            
            # 添加到金字塔
            pyramid.append({
                "texture": downscaled,
                "size": new_size
            })
            
            current_texture = downscaled
            current_size = new_size
        
        return pyramid

    def reconstruct_from_pyramid(self, pyramid):
        """从高斯金字塔重建纹理"""
        if not pyramid:
            return None
            
        # 从最小尺寸开始
        current_texture = pyramid[-1]["texture"]
        
        # 从底层向上重建
        for level in range(len(pyramid) - 2, -1, -1):
            target_size = pyramid[level]["size"]
            
            # 放大到上一级尺寸
            upscaled = self.resize_texture(current_texture, target_size)
            
            # 与原始金字塔层混合
            blended = self.blend_textures(upscaled, pyramid[level]["texture"])
            
            current_texture = blended
        
        return current_texture

    def blend_textures(self, texture1, texture2):
        """混合两个纹理"""
        if not texture1 or not texture2:
            return texture1 or texture2

        size = texture1.size
        fbo = self.get_fbo(size)
        fbo.shader.fs = self.blend_shader

        with fbo:
            Color(1, 1, 1, 1)
            # 关键：Rectangle传递texture1、texture2
            Rectangle(size=size, texture=texture1, texture1=texture2)
        fbo.draw()
        result = fbo.texture
        self.release_fbo(fbo)
        return result

    def process(self, texture, blur_radius=None, iterations=None, downscale_factor=None):
        """
        执行金字塔模糊处理流程
        
        Args:
            texture: 输入纹理
            blur_radius: 模糊半径系数，如果为None则使用默认值
            iterations: 迭代次数/金字塔层数，如果为None则使用默认值
            downscale_factor: 金字塔降采样因子，如果为None则使用默认值
            
        Returns:
            处理后的纹理
        """
        if not texture or texture.size[0] == 0 or texture.size[1] == 0:
            return texture  # 返回原始纹理
            
        start_time = time.time()
        
        # 使用提供的参数或默认值
        blur_radius = blur_radius if blur_radius is not None else self.default_blur_radius
        iterations = iterations if iterations is not None else self.default_iterations
        downscale_factor = downscale_factor if downscale_factor is not None else self.default_downscale_factor
        
        original_size = texture.size
        
        try:
            # 第一步：应用初始模糊
            initial_blur = self.apply_gaussian_blur(texture, original_size, blur_radius)
            
            # 第二步：构建高斯金字塔
            pyramid_levels = min(iterations + 1, 8)  # 最多8层金字塔
            pyramid = self.build_gaussian_pyramid(initial_blur, pyramid_levels)
            
            # 第三步：从金字塔重建纹理
            if pyramid_levels > 1:
                reconstructed = self.reconstruct_from_pyramid(pyramid)
            else:
                reconstructed = initial_blur
                
            # 第四步：应用最终模糊
            final_blur = self.apply_gaussian_blur(reconstructed, original_size, blur_radius * 0.5)
            
            # 记录处理时间
            processing_time = (time.time() - start_time) * 1000
            print(f"Pyramid blur processed in {processing_time:.2f} ms (Levels: {pyramid_levels})")
            
            return final_blur
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error in pyramid blur processing: {e}")
            return texture  # 出错时返回原始纹理
        

class CenteredPaddedTexturePyramidBlurProcessor(TexturePyramidBlurProcessor):
    """算法有严重bug"""
    ...

from kivy.graphics import Color, Rectangle
from kivy.graphics.fbo import Fbo

from kivy.graphics import Color, Rectangle
from kivy.graphics.fbo import Fbo

class ExpansionOnePassStrongBlur:
    """
    支持输入纹理扩充（透明padding，内容居中），再一次shader实现强模糊的Kivy处理器。
    用法:
        blur = ExpansionOnePassStrongBlur()
        result_texture, (offset_x, offset_y) = blur.process(texture, expansion_factor=1.5, radius=32, samples=32)
    """

    def __init__(self):
        self.fbo_pool = []

        self.blur_shader = '''
        $HEADER$
        uniform vec2 tex_size;
        uniform float radius;

        #define SAMPLES 32

        void main(void) {
            vec2 uv = tex_coord0;
            vec2 pixel = 1.0 / tex_size;
            vec4 col = vec4(0.0);
            float total = 0.0;

            for (int i = 0; i < SAMPLES; ++i) {
                float angle = 6.2831853 * float(i) / float(SAMPLES);
                float dist = radius * (0.3 + float(i % 4) / 3.0);
                vec2 offset = vec2(cos(angle), sin(angle)) * dist * pixel;
                vec4 s = texture2D(texture0, uv + offset);
                col.rgb += s.rgb * s.a;
                col.a   += s.a;
                total   += s.a;
            }
            // 加中心
            vec4 center = texture2D(texture0, uv);
            col.rgb += center.rgb * center.a;
            col.a   += center.a;
            total   += center.a;

            if (col.a > 0.0)
                gl_FragColor = vec4(col.rgb / col.a, col.a);
            else
                gl_FragColor = vec4(0.0, 0.0, 0.0, 0.0);
        }
        '''

    def get_fbo(self, size):
        for fbo in self.fbo_pool:
            if fbo.size == size:
                self.fbo_pool.remove(fbo)
                fbo.clear()
                if hasattr(fbo, "clear_buffer"):
                    fbo.clear_buffer()
                if hasattr(fbo, "canvas"):
                    fbo.canvas.clear()
                return fbo
        fbo = Fbo(size=size)
        fbo.clear()
        if hasattr(fbo, "clear_buffer"):
            fbo.clear_buffer()
        if hasattr(fbo, "canvas"):
            fbo.canvas.clear()
        return fbo

    def release_fbo(self, fbo):
        fbo.clear()
        if hasattr(fbo, "clear_buffer"):
            fbo.clear_buffer()
        if hasattr(fbo, "canvas"):
            fbo.canvas.clear()
        self.fbo_pool.append(fbo)

    def pad_and_center(self, texture, expansion_factor=1.0):
        orig_w, orig_h = texture.size
        pad_w = int(orig_w * expansion_factor)
        pad_h = int(orig_h * expansion_factor)
        pad_w = max(pad_w, orig_w)
        pad_h = max(pad_h, orig_h)
        offset_x = (pad_w - orig_w) // 2
        offset_y = (pad_h - orig_h) // 2

        fbo = self.get_fbo((pad_w, pad_h))
        with fbo:
            Color(0, 0, 0, 0)
            Rectangle(size=(pad_w, pad_h), pos=(0, 0))
            Color(1, 1, 1, 1)
            Rectangle(texture=texture, size=texture.size, pos=(offset_x, offset_y))
        fbo.draw()
        padded_texture = fbo.texture
        self.release_fbo(fbo)
        return padded_texture, (offset_x, offset_y), (pad_w, pad_h)

    def process(self, texture, expansion_factor=1.2, radius=32, samples=32):
        """
        :param texture: 输入Kivy纹理
        :param expansion_factor: 扩展比例（内容区居中，边缘透明填充）
        :param radius: 模糊半径
        :param samples: 采样点数量
        :return: (模糊后纹理, (内容区左上角offset_x, offset_y))
        """
        if not texture or texture.size[0] == 0 or texture.size[1] == 0:
            return texture, (0, 0)

        padded_texture, (offset_x, offset_y), pad_size = self.pad_and_center(texture, expansion_factor)
        fbo = self.get_fbo(pad_size)
        shader_code = self.blur_shader.replace('#define SAMPLES 32', f'#define SAMPLES {samples}')
        fbo.shader.fs = shader_code
        fbo['tex_size'] = (float(pad_size[0]), float(pad_size[1]))
        fbo['radius'] = float(radius)
        with fbo:
            Color(1, 1, 1, 1)
            Rectangle(texture=padded_texture, size=pad_size)
        fbo.draw()
        result = fbo.texture
        self.release_fbo(fbo)
        return result, (offset_x, offset_y)