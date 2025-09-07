from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.core.image import Image
from kivy.graphics import Fbo
from kivy.clock import Clock

class TextureSplitTest(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 加载原始纹理
        self.original_texture = Image("resource/internal/image/1080p.jpg").texture
        
        # 设置分割参数
        self.rows = 3
        self.cols = 3
        self.spacing = 10  # 间隔像素
        
        # 延迟初始化以确保尺寸正确
        Clock.schedule_once(self.init_split_textures)
    
    def init_split_textures(self, dt):
        # 计算每个小块的大小
        crop_width = self.original_texture.width // self.cols
        crop_height = self.original_texture.height // self.rows
        
        # 清除现有图形
        self.canvas.clear()
        
        with self.canvas:
            # 遍历所有分割块
            for row in range(self.rows):
                for col in range(self.cols):
                    # 计算裁剪区域
                    crop_x = col * crop_width
                    crop_y = row * crop_height
                    
                    # 创建FBO进行裁剪
                    fbo = Fbo(size=(crop_width, crop_height))
                    
                    with fbo:
                        Color(1, 1, 1)
                        # 计算纹理坐标
                        tex_x = crop_x / self.original_texture.width
                        tex_y = crop_y / self.original_texture.height
                        tex_width = crop_width / self.original_texture.width
                        tex_height = crop_height / self.original_texture.height
                        
                        Rectangle(
                            texture=self.original_texture,
                            size=fbo.size,
                            tex_coords=(
                                tex_x, 1 - tex_y - tex_height,  # 左下
                                tex_x + tex_width, 1 - tex_y - tex_height,  # 右下
                                tex_x + tex_width, 1 - tex_y,  # 右上
                                tex_x, 1 - tex_y  # 左上
                            )
                        )
                                            
                    # 绘制裁剪后的纹理块
                    fbo.draw()
                    pos_x = col * (crop_width + self.spacing)
                    pos_y = row * (crop_height + self.spacing)
                    
                    with self.canvas:
                        Color(1, 1, 1)
                        Rectangle(
                            texture=fbo.texture,
                            pos=(pos_x, pos_y),
                            size=(crop_width, crop_height)
                        )

class TextureSplitApp(App):
    def build(self):
        return TextureSplitTest()

if __name__ == '__main__':
    TextureSplitApp().run()