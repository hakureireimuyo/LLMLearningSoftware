
from kivy.graphics import RenderContext, Color, Rectangle, Fbo
from kivy.graphics.texture import Texture
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
        # 模糊参数
        self.blur_radius = 0.5
        self.iterations = 1
        self.downscale_factor = 1.5
        
        # 纹理管理
        self.input_texture = None  # 输入纹理
        self.output_texture = None  # 输出纹理
        # FBO缓存池
        self.fbo_pool = []
        
        # 处理状态
        self.processing_time = 0  # 处理时间（毫秒）
        self.texture_size = (0, 0)                 # 当前处理纹理尺寸

    def set_input_texture(self, texture):
        """设置输入纹理并重置裁剪区域"""
        self.input_texture = texture
        self.texture_size = texture.size

    def set_blur_parameters(self, blur_radius, iterations, downscale_factor):
        """更新模糊参数"""
        self.blur_radius = blur_radius
        self.iterations = iterations
        self.downscale_factor = downscale_factor

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
        fbo = self.get_fbo(target_size)
        fbo.shader.fs = resize_shader
        
        with fbo:
            Color(1, 1, 1, 1)
            Rectangle(texture=texture, size=target_size)
        
        fbo.draw()
        result = fbo.texture
        self.release_fbo(fbo)
        return result

    def apply_blur_pass(self, texture, size, horizontal):
        """应用单个模糊通道"""
        fbo = self.get_fbo(size)
        
        # 设置着色器和参数
        fbo.shader.fs = horizontal_blur_shader if horizontal else vertical_blur_shader
        with fbo:
            fbo['textureSize'] = (float(size[0]), float(size[1]))
            fbo['blurRadius'] = self.blur_radius
            Color(1, 1, 1, 1)
            Rectangle(texture=texture, size=size)
        
        fbo.draw()
        result = fbo.texture
        self.release_fbo(fbo)
        return result

    def process(self):
        """执行模糊处理流程"""
        if not self.input_texture:
            return
            
        start_time = time.time()
        
        # 确定要处理的纹理（裁剪或完整）
        source_texture = self.input_texture
        original_size = source_texture.size

        # 计算降采样尺寸
        downscaled_size = (
            max(1, int(original_size[0] * self.downscale_factor)),
            max(1, int(original_size[1] * self.downscale_factor))
        )
        
        # 第一步：降采样
        downscaled_texture = self.resize_texture(source_texture, downscaled_size)
        
        # 处理纹理（在降采样尺寸上）
        current_texture = downscaled_texture
        blur_size = downscaled_size
        
        for i in range(self.iterations):
            # 水平模糊
            horizontal_texture = self.apply_blur_pass(current_texture, blur_size, True)
            
            # 垂直模糊
            vertical_texture = self.apply_blur_pass(horizontal_texture, blur_size, False)
            
            current_texture = vertical_texture
        
        # 上采样回原始尺寸
        final_texture = self.resize_texture(current_texture, original_size)
        
        # 更新输出纹理
        self.output_texture = final_texture
        
        # 记录处理时间
        self.processing_time = (time.time() - start_time) * 1000
        print(f"Blur processed in {self.processing_time:.2f} ms (Size: {original_size} -> {downscaled_size})")
        
        return self.output_texture
