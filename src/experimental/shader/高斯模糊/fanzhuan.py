from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.graphics import RenderContext, Rectangle
from kivy.core.image import Texture
from kivy.properties import ObjectProperty
from kivy.graphics.context_instructions import BindTexture, Scale, Translate, PushMatrix, PopMatrix
import numpy as np

class TextureShaderProcessor(Widget):
    """纹理处理器：应用反色效果的着色器"""
    source_texture = ObjectProperty(None)
    
    def __init__(self, texture, **kwargs):
        super().__init__(**kwargs)
        self.source_texture = texture
        self.size = texture.size
        
        # 创建渲染上下文
        self.canvas = RenderContext(
            use_parent_modelview=True, 
            use_parent_projection=True
        )
        
        # 设置反色着色器代码
        shader_code = '''
        $HEADER$
        void main(void) {
            // 使用Kivy提供的标准纹理坐标变量
            vec4 color = texture2D(texture0, tex_coord0);
            // 简单反色效果 (RGB取反)
            gl_FragColor = vec4(1.0 - color.rgb, color.a);
        }
        '''
        self.canvas.shader.fs = shader_code
        
        # 初始绘制
        with self.canvas:
            PushMatrix()
            
            # 绑定纹理并绘制
            BindTexture(texture=self.source_texture, index=0)
            self.rect = Rectangle(pos=(0, 0), size=self.size,texture=self.source_texture)

            PopMatrix()
        
        # 绑定更新事件
        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        """更新矩形位置和大小"""
        self.rect.pos = self.pos
        self.rect.size = self.size
        # 更新坐标系修正
        #self.translate_inst.xy = (-self.width/4, -self.height/2)

class TextureShader(BoxLayout):
    """主布局：包含原始纹理和处理后的纹理"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.padding = 10
        self.spacing = 10
        
        # 创建测试纹理
        texture = self.create_test_texture()
        
        # 添加原始图像
        self.original_image = Image(texture=texture)
        self.add_widget(self.original_image)
        
        # 添加处理后的图像
        self.processed_widget = TextureShaderProcessor(texture=texture)
        self.add_widget(self.processed_widget)
    
    def create_test_texture(self):
        """创建测试纹理（棋盘格图案）"""
        size = (400, 400)
        data = np.zeros((size[1], size[0], 4), dtype=np.uint8)
        block_size = 20
        
        # 填充棋盘格图案
        for y in range(size[1]):
            for x in range(size[0]):
                if (x // block_size + y // block_size) % 2 == 0:
                    data[y, x] = [255, 255, 255, 255]  # 白色
                else:
                    data[y, x] = [200, 150, 150, 255]  # 粉色
        
        # 创建Kivy纹理
        texture = Texture.create(size=size, colorfmt='rgba')
        texture.blit_buffer(data.flatten(), colorfmt='rgba', bufferfmt='ubyte')
        texture.wrap = 'clamp_to_edge'  # 设置纹理边缘处理[4](@ref)
        return texture

class TextureShaderApp(App):
    """主应用类"""
    def build(self):
        return TextureShader()

if __name__ == '__main__':
    TextureShaderApp().run()