import sys
from pathlib import Path

# 自动添加项目根目录和 src 目录
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / "src"))

from src.components.common.tooltipiconbutton import TooltipIconButton
from src.app import TestApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout

class Test(TestApp):
    def build(self):
        self.com =MDGridLayout(cols=3,rows=3,size_hint=(1,1),pos_hint={"center_x":0.5,"center_y":0.5},spacing=160)
        self.com.add_widget(TooltipIconButton(icon="account",tooltip_text="这是一个测试按钮",callback=lambda x:print("点击了按钮")))
        self.com.add_widget(TooltipIconButton(icon="account",tooltip_text="这是一个测试按钮",callback=lambda x:print("点击了按钮")))
        self.com.add_widget(TooltipIconButton(icon="account",tooltip_text="这是一个测试按钮",callback=lambda x:print("点击了按钮")))
        self.com.add_widget(TooltipIconButton(icon="account",tooltip_text="这是一个测试按钮",callback=lambda x:print("点击了按钮")))
        self.com.add_widget(TooltipIconButton(icon="account",tooltip_text="这是一个测试按钮",callback=lambda x:print("点击了按钮")))
        self.com.add_widget(TooltipIconButton(icon="account",tooltip_text="这是一个测试按钮",callback=lambda x:print("点击了按钮")))
        self.com.add_widget(TooltipIconButton(icon="account",tooltip_text="这是一个测试按钮",callback=lambda x:print("点击了按钮")))
        self.com.add_widget(TooltipIconButton(icon="account",tooltip_text="这是一个测试按钮",callback=lambda x:print("点击了按钮")))
        self.com.add_widget(TooltipIconButton(icon="account",tooltip_text="这是一个测试按钮",callback=lambda x:print("点击了按钮")))
        return super().build()

if __name__ == '__main__':
    Test().fps_monitor_start()
    Test().run()