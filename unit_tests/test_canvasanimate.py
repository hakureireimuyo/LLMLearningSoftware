import sys
from pathlib import Path

# 自动添加项目根目录和 src 目录
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / "src"))

from src.app import TestApp
from src.components.common.canvasanimation import *
from kivymd.uix.button import  MDButton,MDButtonText
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.metrics import dp

class Test(TestApp):
    def build(self):
        self.pluse = PulseCircle()#RisingMatrixAnimated()  # 创建动画
        
        self.com=MDBoxLayout(orientation="vertical",size_hint=(1,1),padding=[50,10,10,10],pos_hint={"center_x":0.5,"center_y":0.5})
        self.com.add_widget(self.pluse)
        _md=MDBoxLayout(orientation="horizontal",size_hint=(1,None),height=dp(50))
        self.com.add_widget(_md)
        
        self._button=MDButton(
            MDButtonText(text="start"),
            on_release=lambda *arges:self.pluse.start(), 
        )
        _md.add_widget(self._button)
        self._button=MDButton(
           MDButtonText(text="end"),
            on_release=lambda *arges:self.pluse.end(), 
        )
        _md.add_widget(self._button)

        self._button=MDButton(
            MDButtonText(text="add_dynamic_data"),
            on_release=lambda *arges:self.pluse.add_dynamic_data(), 
        )
        _md.add_widget(self._button)
        return super().build()

if __name__ == "__main__":
    Test().fps_monitor_start()
    Test().run()