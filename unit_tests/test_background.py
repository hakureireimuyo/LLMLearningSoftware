import sys
from pathlib import Path
# 自动添加项目根目录和 src 目录
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / "src"))
from src.app import TestApp
from src.components.common.hoverinfo import TextHoverInfo
from kivymd.uix.fitimage import FitImage
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
class Test(TestApp):
    def build(self):
        _box_layout=MDBoxLayout(size_hint=(1,1),
                                pos_hint={"center_x":0.5,"center_y":0.5})
        _float_layout=MDFloatLayout(size_hint=(1,1),
                                    pos_hint={"center_x":0.5,"center_y":0.5})
        _image=FitImage(source='resource/image/back_image.jpg',
                        size_hint=(1,1),
                        pos_hint={"center_x":0.5,"center_y":0.5})
        _float_layout.add_widget(_image)
        _label=MDLabel(text="这是一个测试",size_hint=(0.5,0.5),pos_hint={"center_x":0.5,"center_y":0.5},font_style="STSONG")
        #_float_layout.add_widget(TextHoverInfo(hover_widget=_label,hover_text="这是一个测试"))
        _label2=MDLabel(text="这是一个测试2",size_hint=(0.5,0.5),pos_hint={"center_x":0.5,"center_y":0.8},font_style="STSONG")
        
        _float_layout.add_widget(_box_layout)
        _box_layout.add_widget(_label)
        _box_layout.add_widget(_label2)
        self.com=_float_layout
        self.print_component_info
        return self.com
Test().run()
