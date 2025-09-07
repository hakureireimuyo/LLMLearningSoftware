"""通过canvas实现画布填色渐变"""

from kivy.graphics import Rectangle, Color
from kivy.graphics.vertex_instructions import Mesh
from kivy.uix.widget import Widget

class GradientWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_gradient, size=self.update_gradient)
        self.update_gradient()
    
    def update_gradient(self, *args):
        self.canvas.clear()
        
        with self.canvas:
            # 创建网格来实现渐变效果
            # 顶点格式: (x, y, u, v, r, g, b, a)
            vertices = [
                # 左下 - 开始颜色
                self.x, self.y, 0, 0, 1, 0, 0, 1,  # 红色
                # 右下 - 开始颜色
                self.right, self.y, 1, 0, 1, 0, 0, 1,  # 红色
                # 右上 - 结束颜色
                self.right, self.top, 1, 1, 0, 0, 1, 1,  # 蓝色
                # 左上 - 结束颜色
                self.x, self.top, 0, 1, 0, 0, 1, 1,  # 蓝色
            ]
            
            # 索引定义两个三角形
            indices = [0, 1, 2, 2, 3, 0]
            
            # 创建网格
            Mesh(
                vertices=vertices,
                indices=indices,
                mode='triangles',
            )
from kivy.app import App
class TestApp(App):
    def build(self):
        return GradientWidget()
TestApp().run()
