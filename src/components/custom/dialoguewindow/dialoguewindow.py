from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.graphics import Rectangle, Color
from kivy.properties import StringProperty, NumericProperty,ObjectProperty
from kivy.core.image import Image
from kivy.clock import Clock
from kivy.metrics import dp
from components.common.canvasanimation import RisingMatrixAnimated
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.core.video import Video as CoreVideo
from kivy.uix.video import Video
import os

class DialogueWindow(MDFloatLayout):
    background_image = StringProperty()
    background_video = StringProperty()
    background_opacity = NumericProperty(0.7, max=1, min=0)
    titlebar_opacity = NumericProperty(0.6, max=1, min=0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, 1)
        # 视频播放器实例（非组件）
        self._video = None
        self._video_texture = None
        self._video_is_loaded = False
        # 背景元素
        self.bg_color_instruction = None
        self.bg_rect_instruction = None
        self.bg_image = None
        # rma=RisingMatrixAnimated()
        # rma.start()
        # super().add_widget(rma)
        r ,g,b,a= self.theme_cls.surfaceContainerLowColor
        title_bar_bg_color = (r,g,b,self.titlebar_opacity)

        self.title_bar=MDBoxLayout(
            orientation='horizontal',
            size_hint=(1,None),
            height=dp(60),
            pos_hint={'top':1},
            md_bg_color=title_bar_bg_color
            )

        self.title_bar.add_widget(MDLabel(
            text="聊天记录",
            font_style="STSONG",
            font_size="20sp",
            size_hint=(1,1),
            valign='middle',
            halign='center',))

        super().add_widget(self.title_bar)
        self._scollview = DialogueWindowScrollView()
        super().add_widget(self._scollview)

        # 绑定属性变化
        self.bind(
            background=self._update_background,
            background_video=self._update_video_source,
            background_opacity=self.update_background_opacity,
            size=self._resize_background,
            pos=self._reposition_background
        )

        # 初始背景更新,手动更新视频源
        self._update_video_source(None,self.background_video)
        Clock.schedule_once(lambda dt: self._update_background())

    def _update_video_source(self, instance, value):
        """更新视频源"""
        # 清理现有视频
        if self._video:
            self._video.stop()
            self._video.unload()
            self._video = None
            self._video_texture = None
        
        # 创建新视频播放器
        if value and os.path.exists(value):
            try:
                self._video = CoreVideo(
                    filename=value,
                    eos='loop',  # 循环播放
                    volume=0  # 静音
                )
                # 绑定视频事件
                self._video.bind(
                    on_load=self._on_video_load,
                    on_eos=self._on_video_eos,
                    on_frame=self._on_video_frame
                )
                self._video.play()
                self._video_is_loaded = True

            except Exception as e:
                print(f"Video initialization error: {e}")
        
        self._update_background()

    def _on_video_load(self, *args):
        """视频加载完成回调"""
        if self._video:
            self._update_background()
        else:
            print(f"Failed to load video: {self._video.filename}")
            self._video_texture = None
            self._update_background()

    def _on_video_eos(self, instance):
        """视频播放结束回调（循环播放已处理）"""
        pass

    def _on_video_frame(self, instance):
        """新视频帧回调"""
        self._video_texture = instance.texture
        # 仅在有有效纹理时更新
        if self._video_texture:
            self._update_background_texture()

    def _update_background(self, *args):
        """更新背景（图片或视频）"""
        # 确保canvas存在
        if not self.canvas:
            return
            
        # 清理现有背景
        self._clear_background()
        
        # 添加基础背景色
        with self.canvas.before:
            r, g, b, a = self.theme_cls.surfaceContainerHighestColor
            self.bg_color_instruction = Color(r, g, b, a)
            self.bg_rect_instruction = Rectangle(
                pos=self.pos,
                size=self.size
            )
        
        # 优先使用视频背景
        if self._video_texture:
            self._create_video_background()
        # 尝试使用图片背景
        elif self.background_image:
            try:
                texture = Image(self.background_image).texture
                self._create_image_background(texture)
            except Exception as e:
                print(f"Background image error: {e}")

    def _update_background_texture(self):
        """仅更新背景纹理（用于视频帧更新）"""
        if self.bg_image and self._video_texture:
            self.bg_image.texture = self._video_texture
            self._resize_background_texture()

    def _create_video_background(self):
        """创建视频背景"""
        if not self._video_texture:
            return
            
        with self.canvas.before:
            Color(1, 1, 1, self.background_opacity)
            self.bg_image = Rectangle(
                texture=self._video_texture,
                size=self.size,
                pos=self.pos
            )
        self._resize_background_texture()

    def _create_image_background(self, texture):
        """创建图片背景"""
        with self.canvas.before:
            Color(1, 1, 1, self.background_opacity)
            self.bg_image = Rectangle(
                texture=texture,
                size=self.size,
                pos=self.pos
            )
        self._resize_background_texture()

    def _resize_background_texture(self):
        """调整背景纹理大小（保持宽高比）"""
        if not self.bg_image or not self.bg_image.texture:
            return
            
        tex = self.bg_image.texture
        if not hasattr(tex, 'size'):  # 视频纹理可能没有size属性
            return
            
        tex_w, tex_h = tex.size
        if not tex_w or not tex_h:
            return
            
        # 计算缩放比例和位置
        scale = max(self.width / tex_w, self.height / tex_h)
        scaled_w = tex_w * scale
        scaled_h = tex_h * scale
        pos_x = (self.width - scaled_w) / 2
        pos_y = (self.height - scaled_h) / 2
        
        self.bg_image.size = (scaled_w, scaled_h)
        self.bg_image.pos = (self.x + pos_x, self.y + pos_y)

    def _clear_background(self):
        """清理背景元素"""
        if self.bg_image:
            self.canvas.before.remove(self.bg_image)
            self.bg_image = None
        if self.bg_color_instruction:
            self.canvas.before.remove(self.bg_color_instruction)
            self.bg_color_instruction = None
        if self.bg_rect_instruction:
            self.canvas.before.remove(self.bg_rect_instruction)
            self.bg_rect_instruction = None

    def update_background_opacity(self, *args):
        """更新背景透明度"""
        if self.bg_image:
            # 更新canvas中对应的Color指令
            for instr in self.canvas.before.get_group('color'):
                if hasattr(instr, 'rgba'):
                    instr.a = self.background_opacity

    def update_theme(self, *args):
        """更新主题颜色"""
        if self.bg_color_instruction:
            r, g, b, a = self.theme_cls.surfaceContainerHighestColor
            self.bg_color_instruction.rgba = (r, g, b, a)

    def _resize_background(self, *args):
        """调整背景大小"""
        if self.bg_rect_instruction:
            self.bg_rect_instruction.size = self.size
        if self.bg_image:
            self._resize_background_texture()

    def _reposition_background(self, *args):
        """重新定位背景"""
        if self.bg_rect_instruction:
            self.bg_rect_instruction.pos = self.pos
        if self.bg_image:
            self._resize_background_texture()

    def on_stop(self):
        """停止视频播放（在不需要时调用）"""
        if self._video:
            self._video.stop()
            self._video.unload()

    def add_widget(self, message):
        """添加消息到滚动视图"""
        class_name = type(message).__name__
        if class_name in ['ChatMessageItem', 'MDButton', 'Timestamp']:
            self.scroll_view.add_message(message)
        else:
            super().add_widget(message)
        
    def add_widget(self, message):
        class_name = type(message).__name__
        module_name = type(message).__module__
        full_path = f"{module_name}.{class_name}"
        
        # 自定义组件的完整类路径
        if full_path == "src.components.custom.chatmessageitem.chatmessageitem.ChatMessageItem":
            self._scollview.add_message(message)
            print("是ChatMessageItem")
        elif class_name == "MDButton":
            self._scollview.add_message(message)
            print("是MDButton")
        elif class_name == "Timestamp":
            self._scollview.add_message(message)
            print("是Timestamp")
        else:
            super().add_widget(message)
            print("是other")

class DialogueWindowScrollView(MDScrollView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.do_scroll_x = False
        self.do_scroll_y = True
        self.always_overscroll = False
        self.scroll_type = ['content']
        self._chat_messages = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            size_hint_x=1,
            spacing=20,
            padding=[30, 0, 30, 0],
            #size_hint_min_x=300,
        )
        self.scroll_timeout = 20
        self.scroll_distance = 5
        self.add_widget(self._chat_messages)
        self.block=Widget(size_hint_y=None, height=100)
        self._chat_messages.add_widget(self.block)
    
    def add_message(self, message):
        self._chat_messages.remove_widget(self.block)
        self._chat_messages.add_widget(message)
        self._chat_messages.add_widget(self.block)
        Clock.schedule_once(self._scroll_to_bottom, 0.1)
    
    def _scroll_to_bottom(self, dt):
        """滚动到底部"""
        if self._chat_messages.height > self.height:
            self.scroll_y = 0

    def on_scroll_start(self, touch):
        return super().on_scroll_start(touch)
    
    def on_scroll_move(self, touch):
        return super().on_scroll_move(touch)
    
    def on_scroll_stop(self, touch):
        return super().on_scroll_stop(touch)
    
    def on_touch_down(self, touch):
        return super().on_touch_down(touch)
    
    def on_touch_move(self, touch):
        return super().on_touch_move(touch)
    
    def on_touch_up(self, touch):
        return super().on_touch_up(touch)

