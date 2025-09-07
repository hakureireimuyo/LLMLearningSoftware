"""
实验性,组件可以获取子组建的渲染结果,然后裁切
对于部分区域进行高斯模糊,实现半透明模糊效果的纹理

"""

from kivy.core.image import Image
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import RenderContext, Color, Rectangle, Fbo, ClearBuffers, ClearColor
from kivy.properties import ListProperty, NumericProperty,BooleanProperty
from kivy.clock import Clock
from .bulr import TextureBlurProcessor,TexturePyramidBlurProcessor
from kivy.properties import NumericProperty
from kivy.graphics.texture import Texture

class ExportBoxLayout(BoxLayout):
    """
    一个可以导出自身及子组件纹理信息的BoxLayout容器
    支持深度控制，可以递归导出子组件的纹理信息
    不会重复导出已有export_tree方法的子组件的纹理
    """
    
    # 定义最大递归深度属性
    max_export_depth = NumericProperty(1)
    
    def export_tree(self, depth=None):
        """
        导出容器及其子组件的纹理和布局信息
        
        Args:
            depth (int): 导出的递归深度，如果为None则使用max_export_depth
            
        Returns:
            dict: 包含纹理、位置、大小和子组件信息的字典
        """
        if depth is None:
            depth = self.max_export_depth
            
        # 构建基础信息
        export_data = {
            "id": str(self.ids),
            "pos": self.pos,
            "size": self.size,
            "type": self.__class__.__name__,
            "children": []
        }
        
        # 只有当前容器没有支持export_tree的子组件时，才导出自己的纹理
        has_exportable_children = False
        
        # 如果深度大于0，递归处理子组件
        if depth > 0:
            for child in self.children:
                # 检查子组件是否有export_tree方法
                if hasattr(child, 'export_tree') and callable(getattr(child, 'export_tree')):
                    child_data = child.export_tree(depth - 1)
                    export_data["children"].append(child_data)
                else:
                    # 如果没有export_tree方法，尝试使用export_as_texture
                    try:
                        child_texture = child.export_as_texture()
                        child_data = {
                            "id": str(child.ids),
                            "texture": child_texture,
                            "pos": child.pos,
                            "size": child.size,
                            "type": child.__class__.__name__,
                            "children": []  # 无法进一步递归
                        }
                        export_data["children"].append(child_data)
                    except AttributeError:
                        # 如果连export_as_texture方法都没有，跳过此子组件
                        continue
        
        return export_data

class BlurLayout(FloatLayout):
    """专门用于渲染模糊纹理的布局"""
    
    # 添加进度控制属性
    progress = NumericProperty(0.0)
    # 纯色背景颜色
    background_color = ListProperty([1, 1, 1, 0.7])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.texture_data = None
        self.bind(pos=self._redraw, size=self._redraw)
        # 绑定进度变化时重绘
        self.bind(progress=self._redraw)
    
    def set_texture_data(self, texture_data):
        """设置纹理数据并重新绘制"""
        self.texture_data = texture_data
        self._redraw()
    
    def _redraw(self, *args):
        """根据纹理数据重新绘制"""
        # 清除之前的绘制
        self.canvas.after.clear()
        
        # 绘制纯色背景
        with self.canvas.after:
            # 背景透明度随进度变化 (0到background_color[3])
            bg_alpha = self.background_color[3] * self.progress
            Color(self.background_color[0], self.background_color[1], 
                  self.background_color[2], bg_alpha)
            Rectangle(pos=self.pos, size=self.size)
        
        # 如果有纹理数据，绘制纹理
        if self.texture_data is not None:
            # 纹理透明度随进度变化 (0到1)
            self._draw_texture_data(self.texture_data, self.pos, self.size)
    
    def _draw_texture_data(self, texture_data, parent_pos, parent_size):
        """
        递归绘制纹理数据
        
        Args:
            texture_data (dict): 包含纹理和位置信息的字典
            parent_pos (tuple): 父组件的绝对位置
            parent_size (tuple): 父组件的尺寸
        """
        # 计算当前组件的绝对位置
        abs_pos = (
            parent_pos[0] + texture_data["pos"][0],
            parent_pos[1] + texture_data["pos"][1]
        )
        
        # 如果当前组件有纹理，绘制它
        if "texture" in texture_data and texture_data["texture"] is not None:
            with self.canvas.after:
                # 纹理透明度随进度变化
                Color(1, 1, 1, self.progress)
                Rectangle(
                    texture=texture_data["texture"],
                    pos=abs_pos,
                    size=texture_data["size"],
                    tex_coords=(0, 1, 1, 1, 1, 0, 0, 0)
                )
            
        # 递归绘制子组件
        for child in texture_data.get("children", []):
            self._draw_texture_data(child, abs_pos, texture_data["size"])


from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ListProperty, NumericProperty
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.graphics import Fbo, Color, Rectangle

class BlurEffect(FloatLayout):
    # 模糊处理迭代次数
    blur_iterations = NumericProperty(2)
    # 模糊半径
    blur_radius = NumericProperty(15)
    # 降采样因子
    downscale_factor = NumericProperty(0.7)
    # 进度控制 (0.0到1.0)
    progress = NumericProperty(0.0)
    # 背景颜色
    background_color = ListProperty([1, 1, 1, 0.7])
    # 是否启用模糊效果
    enabled = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, 1)
        self._texture_data = None
        self.blur = TexturePyramidBlurProcessor()

        # 背景容器 - 使用支持export_tree的容器
        self.content_layout = ExportBoxLayout(size_hint=(1, 1))

        # 模糊效果容器 - 使用新的BlurLayout
        self.blur_layout = BlurLayout(size_hint=(1, 1))
        
        # 绑定属性变化
        self.bind(
            progress=self._update_progress,
            background_color=self._update_background_color,
            enabled=self._update_enabled
        )

        self.add_widget(self.content_layout)
        self.add_widget(self.blur_layout)
        
        # 初始渲染
        Clock.schedule_interval(self._update_blur, 0.5)

    def _update_progress(self, instance, value):
        """更新模糊效果的进度"""
        self.blur_layout.progress = value

    def _update_background_color(self, instance, value):
        """更新背景颜色"""
        self.blur_layout.background_color = value

    def _update_enabled(self, instance, value):
        """启用或禁用模糊效果"""
        if value:
            self.blur_layout.opacity = 1
            self._update_blur()
        else:
            self.blur_layout.opacity = 0
            self.blur_layout.texture_data = None

    def _update_blur(self, *args):
        """更新模糊效果"""
        if not self.enabled:
            return
            
        if self.content_layout.width == 0 or self.content_layout.height == 0:
            return
            
        # 获取所有子组件的纹理数据
        texture_data = self.content_layout.export_tree()
        
        # 处理所有纹理数据，应用模糊效果
        processed_data = self._process_texture_data(texture_data)
        
        # 将处理后的数据传递给blur_layout进行渲染
        self.blur_layout.set_texture_data(processed_data)

    def _process_texture_data(self, texture_data):
        """
        递归处理纹理数据，应用模糊效果
        
        Args:
            texture_data (dict): 包含纹理和子组件信息的字典
            
        Returns:
            dict: 处理后的纹理数据
        """
        
        # 复制原始数据
        processed_data = texture_data.copy()
        
        # 如果当前节点有纹理，进行模糊处理
        if "texture" in processed_data and processed_data["texture"] is not None:
            # 获取正确方向的纹理
            corrected_texture = processed_data["texture"]
            
            # 使用当前设置的模糊参数
            blurred_texture = self.blur.process(
                texture=corrected_texture,
                blur_radius=self.blur_radius,
                iterations=self.blur_iterations,
                downscale_factor=self.downscale_factor
            )
            processed_data["texture"] = blurred_texture

        # 递归处理子组件
        processed_data["children"] = []
        for child in texture_data.get("children", []):
            processed_child = self._process_texture_data(child)
            processed_data["children"].append(processed_child)
        
        return processed_data

    def add_widget_to_content(self, widget):
        """添加子组件到内容区域"""
        self.content_layout.add_widget(widget)

    def add_widget_to_foreground(self, widget):
        """添加子组件到前景（不会被模糊）"""
        self.blur_layout.add_widget(widget)
        
    def set_progress(self, value):
        """设置进度值 (0.0到1.0)"""
        self.progress = max(0.0, min(1.0, value))
        
    def enable_blur(self):
        """启用模糊效果"""
        self.enabled = True
        
    def disable_blur(self):
        """禁用模糊效果"""
        self.enabled = False
        
    def toggle_blur(self):
        """切换模糊效果的启用状态"""
        self.enabled = not self.enabled