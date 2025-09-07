import sys
from pathlib import Path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / "src"))

from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.button import MDButton,MDButtonText
from src.components.custom.label import DynamicCharLabel

KV = '''
BoxLayout:
    orientation: 'vertical'
    
    DynamicCharLabel:
        id: label
        text: "初始文本"
        halign: 'center'
        valign: 'center'
        size_hint_y: 0.6
    
    MDBoxLayout:
        size_hint_y: 0.4
        spacing: '10dp'
        padding: '10dp'
        
        MDButton:
            on_release: app.add_text("短文本")
            MDButtonText:
                font_style: "STSONG"

                text: "添加短文本"
        
        MDButton:
            on_release: app.add_text("这是一个较长的文本，将逐步添加到标签中，测试动态添加效果。")
            MDButtonText
                font_style: "STSONG"
                text: "添加长文本"
        
        MDButton:
            on_release: app.delete_text()
            MDButtonText:
                font_style: "STSONG"
                text: "删除"
        
        MDButton:
            on_release: app.clear_text()
            MDButtonText:
                font_style: "STSONG"
                text: "清除"
'''

from src.app import TestApp
class Test(TestApp):
    def build(self):
        return Builder.load_string(KV)
    
    def add_text(self, text: str):
        """向标签添加文本"""
        self.root.ids.label.add_text(text)
    
    def delete_text(self):
        """删除标签文本"""
        self.root.ids.label.delete_all()
    
    def clear_text(self):
        """立即清除标签文本"""
        self.root.ids.label.clear()

if __name__ == "__main__":
    Test().run()