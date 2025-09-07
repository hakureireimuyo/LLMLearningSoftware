import sys
from pathlib import Path

# 自动添加项目根目录和 src 目录
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / "src"))

from src.app import TestApp
from src.components.common.blureffect import BlurEffect

from kivy.app import App
from kivy.uix.slider import Slider
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

class TestApp(App):
    def build(self):
        self.com = effect = BlurEffect()
        
        # 创建主布局
        main_layout = BoxLayout(orientation='vertical')
        
        # 添加滑块控制
        control_layout = BoxLayout(size_hint_y=0.1)
        self.slider = Slider(min=0, max=1, value=0, size_hint_x=0.8)
        self.slider.bind(value=self.on_slider_change)
        
        # 添加启用/禁用按钮
        toggle_button = Button(text="禁用模糊",font_name="STSONG", size_hint_x=0.2)
        toggle_button.bind(on_press=self.toggle_blur)
        
        control_layout.add_widget(self.slider)
        control_layout.add_widget(toggle_button)
        
        # 添加内容区域
        content_layout = BoxLayout(orientation='vertical')
        
        # 添加到内容区域（会被模糊）
        effect.add_widget_to_content(Button(text="Background Button 1", size_hint=(None, None), size=(200, 100), pos=(100, 100)))
        effect.add_widget_to_content(Button(text="Background Button 2", size_hint=(None, None), size=(200, 100), pos=(350, 200)))
        
        # 添加前景组件（不会被模糊）
        effect.add_widget_to_foreground(Button(text="Foreground Button", size_hint=(None, None), size=(200, 50), pos=(150, 200)))
        
        # 将模糊效果组件添加到内容布局
        content_layout.add_widget(effect)
        
        # 将控制布局和内容布局添加到主布局
        main_layout.add_widget(control_layout)
        main_layout.add_widget(content_layout)
        
        return main_layout
    
    def on_slider_change(self, instance, value):
        """滑块值变化时的回调函数"""
        self.com.set_progress(value)
    
    def toggle_blur(self, instance):
        """切换模糊效果的启用状态"""
        if self.com.enabled:
            self.com.disable_blur()
            instance.text = "启用模糊"
        else:
            self.com.enable_blur()
            instance.text = "禁用模糊"

if __name__ == '__main__':
    TestApp().run()