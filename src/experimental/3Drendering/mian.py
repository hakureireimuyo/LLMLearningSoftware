from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.resources import resource_find
from kivy.graphics.transformation import Matrix
from kivy.graphics.opengl import glEnable, glDisable, GL_DEPTH_TEST
from kivy.graphics import RenderContext, Callback, PushMatrix, PopMatrix, \
    Color, Translate, Rotate, Mesh, UpdateNormalMatrix
from kivy.properties import NumericProperty, BooleanProperty
from objloader import ObjFile
import math

class Renderer(Widget):
    # 定义旋转属性
    rotation_x = NumericProperty(0)
    rotation_y = NumericProperty(0)
    
    # 定义缩放属性
    zoom = NumericProperty(-3)
    
    # 鼠标拖动状态
    is_dragging = BooleanProperty(False)
    last_mouse_pos = None

    def __init__(self, **kwargs):
        self.canvas = RenderContext(compute_normal_mat=True)
        self.canvas.shader.source = resource_find('simple.glsl')
        self.scene = ObjFile(resource_find("3d_object.obj"))
        super(Renderer, self).__init__(**kwargs)
        
        with self.canvas:
            self.cb = Callback(self.setup_gl_context)
            PushMatrix()
            self.setup_scene()
            PopMatrix()
            self.cb = Callback(self.reset_gl_context)
        
        # 绑定鼠标事件
        Window.bind(mouse_pos=self.on_mouse_pos)
        Window.bind(on_touch_down=self.on_touch_down)
        Window.bind(on_touch_up=self.on_touch_up)
        
        Clock.schedule_interval(self.update_glsl, 1 / 60.)

    def setup_gl_context(self, *args):
        glEnable(GL_DEPTH_TEST)

    def reset_gl_context(self, *args):
        glDisable(GL_DEPTH_TEST)

    def update_glsl(self, delta):
        asp = self.width / float(self.height)
        proj = Matrix().view_clip(-asp, asp, -1, 1, 1, 100, 1)
        self.canvas['projection_mat'] = proj
        
        # 创建模型视图矩阵
        mv_mat = Matrix()
        mv_mat.translate(0, 0, self.zoom)  # 平移
        mv_mat = mv_mat.rotate(self.rotation_y, 0, 1, 0)  # Y轴旋转
        mv_mat = mv_mat.rotate(self.rotation_x, 1, 0, 0)  # X轴旋转
        
        # 获取模型视图矩阵的逆矩阵
        try:
            inv_mv = mv_mat.inverse()
        except:
            # 如果逆矩阵无法计算，使用单位矩阵
            inv_mv = Matrix()
        
        # 正确构建法线矩阵（3x3矩阵作为9元素列表）
        # 注意：Kivy的Matrix使用一维数组存储4x4矩阵，索引如下：
        # [0, 1, 2, 3]
        # [4, 5, 6, 7]
        # [8, 9, 10, 11]
        # [12, 13, 14, 15]
        normal_mat = [
            inv_mv[0], inv_mv[1], inv_mv[2],   # 第一行
            inv_mv[4], inv_mv[5], inv_mv[6],   # 第二行
            inv_mv[8], inv_mv[9], inv_mv[10]   # 第三行
        ]
        
        self.canvas['modelview_mat'] = mv_mat
        self.canvas['normal_mat'] = normal_mat  # 传入3x3法线矩阵
        
        # 传递时间变量给着色器（用于动画效果）
        time = Clock.get_boottime()
        self.canvas['time'] = time
        
        # 不再需要的代码（使用新着色器不需要这些）
        # self.canvas['light_dir'] = (1.0, 0.5, 0.5)
        # self.canvas['diffuse_color'] = (0.8, 0.8, 0.8)
        # self.canvas['ambient_color'] = (0.4, 0.4, 0.4)
        # self.canvas['rotation_x'] = self.rotation_x
        # self.canvas['rotation_y'] = self.rotation_y
        # self.canvas['model_mat'] = rotation_matrix
        
        # 更新旋转器
        self.rot_x.angle = self.rotation_x
        self.rot_y.angle = self.rotation_y

    def setup_scene(self):
        Color(1, 1, 1, 1)
        PushMatrix()
        # 使用zoom属性控制距离
        Translate(0, 0, self.zoom)
        
        # 创建两个旋转器分别控制X和Y轴旋转
        self.rot_y = Rotate(0, 0, 1, 0)
        self.rot_x = Rotate(0, 1, 0, 0)
        
        # 渲染所有对象
        for name, obj in self.scene.objects.items():
            Mesh(
                vertices=obj.vertices,
                indices=obj.indices,
                fmt=obj.vertex_format,
                mode='triangles',
            )
            
        PopMatrix()

    def on_touch_down(self, instance, touch):
        if touch.button == 'left':
            self.is_dragging = True
            self.last_mouse_pos = touch.pos
            return True
        elif touch.button == 'scrollup':
            self.zoom += 0.5  # 拉近
            self.update_camera_position()
            return True
        elif touch.button == 'scrolldown':
            self.zoom -= 0.5  # 拉远
            self.update_camera_position()
            return True
        return super(Renderer, self).on_touch_down(touch)

    def on_touch_up(self, instance, touch):
        if touch.button == 'left':
            self.is_dragging = False
            self.last_mouse_pos = None
            return True

        return super(Renderer, self).on_touch_up(touch)

    def on_mouse_pos(self, *args):
        if not self.is_dragging or self.last_mouse_pos is None:
            return
            
        mouse_pos = args[1]
        dx = mouse_pos[0] - self.last_mouse_pos[0]
        dy = mouse_pos[1] - self.last_mouse_pos[1]
        
        # 更新旋转角度
        self.rotation_x += dy * 0.5
        self.rotation_y -= dx * 0.5
        
        # 限制X轴旋转范围，避免翻转
        self.rotation_x = max(-90, min(90, self.rotation_x))
        
        self.last_mouse_pos = mouse_pos
        
        # 更新旋转器
        self.rot_x.angle = self.rotation_x
        self.rot_y.angle = self.rotation_y

    def update_camera_position(self):
        # 限制缩放范围
        self.zoom = max(-15, min(-1, self.zoom))
        
        # 更新相机位置
        with self.canvas:
            # 移除旧的平移
            self.canvas.children = [c for c in self.canvas.children 
                                   if not (isinstance(c, Translate) and c.z != 0)]
            # 添加新的平移
            PushMatrix()
            Translate(0, 0, self.zoom)
            PopMatrix()


class RendererApp(App):
    def build(self):
        return Renderer()


if __name__ == "__main__":
    RendererApp().run()