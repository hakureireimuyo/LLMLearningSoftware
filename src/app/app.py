from kivy.core.text import LabelBase
from kivy.metrics import sp
from kivymd.app import MDApp
from src.core.config import FontConfigManager
import os
from kivy.core.window import Window
from src.core.evn import external_resource_path

class App(MDApp):
    """增强的MDApp类，支持自动字体加载"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_config = FontConfigManager()
        self.fonts_loaded = False
        self.theme_cls.on_colors=lambda:self.update_theme_root_and_window()
    
    def update_theme_root_and_window(self):
        #print("更新主题")
        #self.update_theme(self.root,None)
        self.update_theme(Window,None)

    def update_theme(self,instance,value):
        """
        更新主题
        当前函数的作用是递归调用自己(并非子项的update_theme方法)
        遍历传入的实例的所有子项，如果子项有update_theme方法，则调用该方法
        默认传入app.root让遍历开始
        因此虽然组件(Widget)的update_theme方法会被调用，但是组件并不会递归
        """
        if instance is None:
            return
        if hasattr(instance, "children"):
            for child in instance.children:
                if hasattr(child, "update_theme"):
                    child.update_theme(None,None)
                self.update_theme(child, None)
            

    def _register_font(self, font_name: str, font_path: str) -> None:
        """注册单个字体"""
        try:
            # 检查是否已注册
            if font_name not in self.theme_cls.font_styles:
                # 从配置获取或使用默认样式
                style = self.font_config.get_font_style(font_name)
                
                # 注册到Kivy
                LabelBase.register(
                    name=font_name,
                    fn_regular=font_path
                )
                
                # 创建字体样式配置
                self.theme_cls.font_styles[font_name] = {
                    "large": {
                        "line-height": style["large"]["line_height"],
                        "font-name": font_name,
                        "font-size": sp(style["large"]["size"])
                    },
                    "medium": {
                        "line-height": style["medium"]["line_height"],
                        "font-name": font_name,
                        "font-size": sp(style["medium"]["size"])
                    },
                    "small": {
                        "line-height": style["small"]["line_height"],
                        "font-name": font_name,
                        "font-size": sp(style["small"]["size"])
                    }
                }
                
                # 如果是新字体则保存配置
                if font_name not in self.font_config.config["font_styles"]:
                    self.font_config.update_font_style(font_name, style)
        except Exception as e:
            print(f"字体 {font_name} 注册失败: {str(e)}")
    
    def auto_load_fonts(self) -> None:
        """自动加载字体"""    
        # 遍历字体文件
        for root, _, files in os.walk(external_resource_path('font')):
            for file in files:
                if file.lower().endswith(('.ttf', '.otf')):
                    font_path = os.path.join(root, file)
                    font_name = os.path.splitext(file)[0]
                    self._register_font(font_name, font_path)
    
        self.fonts_loaded = True
    
    def _run_prepare(self):
        # 自动加载字体
        self.auto_load_fonts()
        super()._run_prepare()