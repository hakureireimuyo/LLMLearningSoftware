import sys
from pathlib import Path

# 自动添加项目根目录和 src 目录
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / "src"))

from src.components.common.slidedrawer import TestSlideDrawer,SlideDrawer
from src.app import TestApp

KV='''
MDBoxLayout:
    md_bg_color: app.theme_cls.backgroundColor
    MDLabel:
        text:"填充物"
        font_style: "STSONG"
        valign:"middle"
        halign:"center"
    SlideDrawer:
        id:drawer
        size_hint_max_x:dp(500)
        open:True
        MDLabel:
            text:str(root)
            font_style: "STSONG"
            role:"medium"
        MDLabel:
            text:str(root.ids.drawer)
            font_style: "STSONG"
            role:"medium"
        MDLabel:
            text:str(root.ids.drawer.floater)
            font_style: "STSONG"
            role:"medium"
        MDLabel:
            text:str(self.parent)
            font_style: "STSONG"
            role:"medium"
    MDButton:
        on_press:root.ids.drawer.open=not root.ids.drawer.open
    MDLabel:
        text:"填充物"
        font_style: "STSONG"
        valign:"middle"
        halign:"center"
'''
from kivy.lang import Builder

class Test(TestApp):
    def build(self):
        self.com=Builder.load_string(KV)
        return super().build()
    
if __name__ == "__main__":
    Test().run()