from kivy.clock import Clock
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.graphics import RenderContext, Fbo, Color, Rectangle, ClearBuffers, ClearColor
from kivy.graphics.texture import Texture
from kivy.logger import Logger
import numpy as np
import os
import time
import json

# 设置详细的日志级别
os.environ['KIVY_LOG_LEVEL'] = 'debug'

# 简化但功能明确的着色器
simple_debug_shader = '''
$HEADER$
uniform vec2 resolution;
uniform float time;
uniform float blurRadius;

void main() {
    // 简单调试着色器：显示渐变和当前时间
    vec2 uv = tex_coord0;
    float timeFactor = sin(time) * 0.5 + 0.5;
    vec3 color = vec3(
        uv.x, 
        uv.y * timeFactor, 
        blurRadius / 15.0
    );
    gl_FragColor = vec4(color, 1.0);
}
'''

# 完整的高斯模糊着色器
gaussian_blur_shader = '''
$HEADER$
uniform vec2 resolution;
uniform float time;
uniform float blurRadius;

void main() {
    vec2 uv = tex_coord0;
    vec2 direction = vec2(1.0, 0.0); // 水平模糊
    vec4 color = vec4(0.0);
    
    // 高斯核权重 (5个采样点)
    float weights[5] = float[](
        0.06136, 0.24477, 0.38774, 0.24477, 0.06136
    );
    
    // 根据模糊半径调整采样范围
    float radius = clamp(blurRadius, 0.5, 15.0);
    vec2 texelSize = 1.0 / resolution * radius;
    
    for (int i = -2; i <= 2; i++) {
        vec2 offset = direction * float(i) * texelSize;
        vec4 sample = texture2D(texture0, uv + offset);
        color += sample * weights[i+2];
    }
    
    // 添加时间效果用于调试
    float timeFactor = sin(time) * 0.1;
    color.r += timeFactor;
    
    gl_FragColor = vec4(color.rgb, 1.0);
}
'''

class DebugInfo:
    """调试信息收集器"""
    def __init__(self):
        self.data = {}
        self.log_file = "debug_log.json"
        
    def add(self, key, value):
        """添加调试信息"""
        self.data[key] = value
        Logger.info(f"Debug: {key} = {value}")
        
    def save(self):
        """保存调试信息到文件"""
        with open(self.log_file, 'w') as f:
            json.dump(self.data, f, indent=4)
        Logger.info(f"Debug info saved to {self.log_file}")
        
    def capture_texture(self, texture, name):
        """保存纹理到文件"""
        if texture:
            try:
                filename = f"{name}.png"
                texture.save(filename)
                self.add(f"texture_{name}", filename)
                Logger.info(f"Saved texture {name} to {filename}")
                return True
            except Exception as e:
                Logger.error(f"Failed to save texture: {str(e)}")
        return False

# 全局调试对象
debug = DebugInfo()

class HorizontalBlurProcessor(FloatLayout):
    fs = StringProperty(None)
    texture = ObjectProperty(None)
    blur_radius = NumericProperty(5.0)
    debug_mode = False
    
    def __init__(self, texture=None, **kwargs):
        super(HorizontalBlurProcessor, self).__init__(**kwargs)
        
        # 初始化调试信息
        debug.add("processor_init", "开始初始化模糊处理器")
        debug.add("processor_size", self.size)
        debug.add("processor_pos", self.pos)
        
        # 创建渲染上下文
        try:
            self.canvas = RenderContext(
                use_parent_projection=True,
                use_parent_modelview=True,
                use_parent_frag_modelview=True
            )
            debug.add("render_context_created", True)
        except Exception as e:
            debug.add("render_context_error", str(e))
            raise
        
        # 创建FBO
        try:
            self.fbo = Fbo(
                size=self.size, 
                with_stencilbuffer=False,
                with_depthbuffer=False
            )
            debug.add("fbo_created", True)
            debug.add("fbo_size", self.size)
            debug.add("fbo_texture_size", self.fbo.texture.size if self.fbo.texture else None)
        except Exception as e:
            debug.add("fbo_creation_error", str(e))
            raise
        
        # 在主画布上绘制FBO的纹理
        with self.canvas:
            try:
                Color(1, 1, 1, 1)
                self.fbo_rect = Rectangle(
                    size=self.size, 
                    pos=self.pos, 
                    texture=self.fbo.texture
                )
                debug.add("fbo_rect_created", True)
            except Exception as e:
                debug.add("fbo_rect_error", str(e))
                raise
        
        # 设置初始纹理
        self.texture = texture
        if texture:
            debug.add("initial_texture_size", texture.size)
        
        # 初始使用简单着色器用于调试
        self.fs = simple_debug_shader
        debug.add("initial_shader", "simple_debug_shader")
        
        # 设置更新时钟
        #Clock.schedule_interval(self.update_glsl, 1/60.)
        #debug.add("update_clock_started", True)
        
        # 绑定属性变化
        self.bind(
            size=self._update_fbo_size,
            pos=self._update_fbo_rect_pos,
            texture=self._update_texture
        )
        debug.add("property_bindings", True)
        
        debug.add("processor_init_complete", True)
    
    def _update_fbo_size(self, instance, value):
        debug.add("size_changed", value)
        # 更新FBO和矩形大小
        if self.fbo:
            self.fbo.size = value
            debug.add("fbo_size_updated", value)
        if self.fbo_rect:
            self.fbo_rect.size = value
            debug.add("fbo_rect_size_updated", value)
        self.update_fbo()
    
    def _update_fbo_rect_pos(self, instance, value):
        debug.add("pos_changed", value)
        if self.fbo_rect:
            self.fbo_rect.pos = value
            debug.add("fbo_rect_pos_updated", value)
    
    def _update_texture(self, instance, value):
        debug.add("texture_changed", value.size if value else None)
        self.update_fbo()
    
    def enable_blur_shader(self):
        """启用真正的模糊着色器"""
        self.fs = gaussian_blur_shader
        debug.add("shader_changed", "gaussian_blur_shader")
    
    def update_glsl(self, *largs):
        """更新着色器uniform变量"""
        # 收集当前状态信息
        debug.add("update_cycle_start", time.time())
        
        # 更新uniform变量
        if self.canvas:
            try:
                self.canvas['time'] = Clock.get_boottime()
                self.canvas['resolution'] = [float(v) for v in self.size]
                self.canvas['blurRadius'] = float(self.blur_radius)
                debug.add("uniforms_set", True)
            except Exception as e:
                debug.add("uniform_set_error", str(e))
        
        # 更新FBO内容
        self.update_fbo()
        
        # 调试：保存状态信息
        if self.debug_mode:
            debug.add("update_cycle_end", time.time())
            debug.save()
        
        # 每10帧切换一次着色器用于调试
        if int(time.time() * 10) % 20 == 0:
            if self.fs == simple_debug_shader:
                self.enable_blur_shader()
            else:
                self.fs = simple_debug_shader
                debug.add("shader_changed", "simple_debug_shader")
    
    def update_fbo(self):
        """更新帧缓冲区内容"""
        debug.add("fbo_update_start", time.time())
        
        if not self.texture:
            debug.add("fbo_update", "Skipped - no texture")
            Logger.warning("FBO update: No texture set")
            return
            
        if not self.fbo:
            debug.add("fbo_update", "Skipped - no FBO")
            Logger.error("FBO update: No FBO created")
            return
        
        # 保存原始纹理用于调试
        if self.debug_mode:
            debug.capture_texture(self.texture, "input_texture")
        
        try:
            # 绑定FBO
            self.fbo.bind()
            
            # 清除FBO
            self.fbo.clear_buffer()
            debug.add("fbo_cleared", True)
            
            # 在FBO中绘制纹理
            with self.fbo:
                # 绘制背景用于调试
                if self.debug_mode:
                    Color(0.2, 0.2, 0.8, 0.5)  # 半透明蓝色背景
                    Rectangle(size=self.size)
                
                # 绘制传入的纹理
                Color(1, 1, 1, 1)
                Rectangle(size=self.size, texture=self.texture)
                debug.add("texture_drawn_in_fbo", True)
            
            # 保存FBO纹理用于调试
            if self.debug_mode:
                debug.capture_texture(self.fbo.texture, "fbo_output")
            
            # 释放FBO
            self.fbo.release()
            
            # 更新显示的纹理
            if self.fbo_rect:
                self.fbo_rect.texture = self.fbo.texture
                debug.add("fbo_texture_set_to_rect", True)
            
            debug.add("fbo_update_success", True)
        except Exception as e:
            debug.add("fbo_update_error", str(e))
            Logger.error(f"FBO update error: {str(e)}")
        
        debug.add("fbo_update_end", time.time())
    
    def on_fs(self, instance, value):
        if not self.canvas:
            return
            
        shader = self.canvas.shader
        old_value = shader.fs
        shader.fs = value
        
        debug.add("shader_change_attempted", value[:100] + "..." if len(value) > 100 else value)
        
        if not shader.success:
            shader.fs = old_value
            error_msg = f"Shader compilation failed: {shader.log}"
            debug.add("shader_compile_error", error_msg)
            Logger.error(error_msg)
            return False
        else:
            debug.add("shader_compile_success", value[:50] + "...")
            Logger.info("Shader compiled successfully")
            return True
    
    def on_blur_radius(self, instance, value):
        debug.add("blur_radius_changed", value)
        Logger.info(f"Blur radius changed to {value}")
        self.update_glsl()

class BlurTestApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.debug_mode = True
    
    def build(self):
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.image import Image
        from kivy.uix.slider import Slider
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        # 初始化调试
        debug.add("app_build_start", time.time())
        Logger.info("Starting application build")
        
        # 主布局
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 创建测试纹理
        texture = self.create_test_texture()
        debug.capture_texture(texture, "original_texture")
        
        # 添加标题
        title = Label(text="高级模糊效果调试", size_hint=(1, 0.1), font_size=24)
        layout.add_widget(title)
        
        # 添加原始图像
        original_label = Label(text="原始图像 (调试视图)", size_hint=(1, 0.05))
        layout.add_widget(original_label)
        original = Image(texture=texture, size_hint=(1, 0.25))
        layout.add_widget(original)
        
        # 添加FBO视图
        fbo_label = Label(text="FBO内容视图", size_hint=(1, 0.05))
        layout.add_widget(fbo_label)
        self.fbo_view = Image(size_hint=(1, 0.25))
        layout.add_widget(self.fbo_view)
        
        # 添加模糊处理器
        blur_label = Label(text="模糊处理器输出", size_hint=(1, 0.05))
        layout.add_widget(blur_label)
        self.blur_processor = HorizontalBlurProcessor(
            texture=texture, 
            size_hint=(1, 0.25)
        )
        self.blur_processor.debug_mode = self.debug_mode
        layout.add_widget(self.blur_processor)
        
        # 添加控制面板
        control_panel = BoxLayout(orientation='horizontal', size_hint=(1, 0.15), spacing=10)
        
        # 模糊控制
        blur_control = BoxLayout(orientation='vertical', size_hint=(0.4, 1))
        blur_control.add_widget(Label(text="模糊强度控制", size_hint=(1, 0.3)))
        
        self.radius_label = Label(text=f"模糊半径: {self.blur_processor.blur_radius:.1f}", 
                                 size_hint=(1, 0.3))
        blur_control.add_widget(self.radius_label)
        
        self.slider = Slider(
            min=0.1, 
            max=6.0, 
            value=self.blur_processor.blur_radius,
            size_hint=(1, 0.4)
        )
        self.slider.bind(value=self.on_slider_change)
        blur_control.add_widget(self.slider)
        
        control_panel.add_widget(blur_control)
        
        # 调试控制
        debug_control = BoxLayout(orientation='vertical', size_hint=(0.6, 1))
        debug_control.add_widget(Label(text="调试工具", size_hint=(1, 0.3)))
        
        # 着色器切换按钮
        shader_btn_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.4))
        debug_btn = Button(text="调试着色器", size_hint=(0.5, 1))
        debug_btn.bind(on_press=self.enable_debug_shader)
        shader_btn_layout.add_widget(debug_btn)
        
        blur_btn = Button(text="模糊着色器", size_hint=(0.5, 1))
        blur_btn.bind(on_press=self.enable_blur_shader)
        shader_btn_layout.add_widget(blur_btn)
        
        debug_control.add_widget(shader_btn_layout)
        
        # 保存调试按钮
        save_btn = Button(text="保存调试信息", size_hint=(1, 0.3))
        save_btn.bind(on_press=self.save_debug_info)
        debug_control.add_widget(save_btn)
        
        control_panel.add_widget(debug_control)
        
        layout.add_widget(control_panel)
        
        # 状态栏
        self.status_bar = Label(text="就绪", size_hint=(1, 0.05), 
                               color=(0.8, 0.8, 0.8, 1))
        layout.add_widget(self.status_bar)
        
        # 设置FBO视图更新时钟
        #Clock.schedule_interval(self.update_fbo_view, 1/10)
        
        #debug.add("app_build_complete", True)
        self.update_status("应用程序初始化完成")
        return layout
    
    def update_status(self, message):
        """更新状态栏"""
        self.status_bar.text = message
        Logger.info(f"Status: {message}")
    
    def on_slider_change(self, instance, value):
        """滑块值变化时更新模糊效果"""
        self.blur_processor.blur_radius = value
        self.radius_label.text = f"模糊半径: {value:.1f}"
        self.update_status(f"模糊半径更新为: {value:.1f}")
        self.update_fbo_view(1/60)
    
    def enable_debug_shader(self, instance):
        """启用调试着色器"""
        self.blur_processor.fs = simple_debug_shader
        self.update_status("启用调试着色器")
    
    def enable_blur_shader(self, instance):
        """启用模糊着色器"""
        if self.blur_processor.on_fs(None, gaussian_blur_shader):
            self.update_status("启用高斯模糊着色器")
    
    def save_debug_info(self, instance):
        """保存调试信息"""
        debug.save()
        self.update_status("调试信息已保存")
    
    def update_fbo_view(self, dt):
        """更新FBO视图"""
        if self.blur_processor and self.blur_processor.fbo:
            self.fbo_view.texture = self.blur_processor.fbo.texture
            debug.add("fbo_view_updated", True)
    
    def create_test_texture(self):
        """创建测试纹理（带颜色的测试图案）"""
        size = (400, 400)
        data = np.zeros((size[1], size[0], 4), dtype=np.uint8)
        block_size = 40
        
        # 创建彩色测试图案
        for y in range(size[1]):
            for x in range(size[0]):
                # 中心圆
                cx, cy = size[0]//2, size[1]//2
                dist = np.sqrt((x-cx)**2 + (y-cy)**2)
                
                if dist < 100:
                    # 彩色渐变
                    r = int(255 * (0.5 + 0.5 * np.sin(x/30.0)))
                    g = int(255 * (0.5 + 0.5 * np.cos(y/30.0)))
                    b = int(255 * (0.5 + 0.5 * np.sin((x+y)/40.0)))
                    data[y, x] = [r, g, b, 255]
                else:
                    # 网格图案
                    if (x // block_size + y // block_size) % 2 == 0:
                        data[y, x] = [255, 200, 200, 255]  # 浅红色
                    else:
                        data[y, x] = [200, 200, 255, 255]  # 浅蓝色
        
        # 创建Kivy纹理
        texture = Texture.create(size=size, colorfmt='rgba')
        texture.blit_buffer(data.flatten(), colorfmt='rgba', bufferfmt='ubyte')
        texture.wrap = 'repeat'
        return texture

if __name__ == '__main__':
    app = BlurTestApp()
    app.run()
    # 应用结束后保存最终调试信息
    debug.add("app_exit_time", time.time())
    debug.save()