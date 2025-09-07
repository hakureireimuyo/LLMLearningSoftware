import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / "src"))

from src.components.custom.input import Input
from src.app import TestApp
from kivy.lang import Builder

KV="""
<MDBoxlayout>:
    orientation:"vertical"
    size_hint:(1,1)
    md_bg_color:app.theme_cls.primaryColor
    Input:
        
    MDTextField:
        font_name:"STSONG"
        font_size:"26sp"

"""
class Test(TestApp):
    def build(self):
        self.com=Builder.load_string(KV)
        return super().build()
    
if __name__ == '__main__':
    Test().run()
