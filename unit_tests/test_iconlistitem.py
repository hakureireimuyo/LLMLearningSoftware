# tests/test_example.py
import sys
from pathlib import Path

# 自动添加项目根目录和 src 目录
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / "src"))
def test_path():
    print("\n当前 Python 路径:")
    for p in sys.path:
        print(p)
    assert str(Path(__file__).parent.parent / "src") in sys.path
test_path()
from src.app import TestApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton
from kivy.uix.widget import Widget
from src.components.common.informationitem import IconListItem,TestIconListItem
class Test(TestApp):
    def build(self):
        self.com=MDBoxLayout(orientation='vertical')
        self.com.add_widget(TestIconListItem())
        self.com.add_widget(TestIconListItem())
        self.com.add_widget(MDButton(on_press=lambda x:self.com.add_widget(Widget(size_hint=(None,None),size=(100,100)))))
        self.com.add_widget(MDButton(on_press=lambda x:self.com.remove_widget(self.com.children[0])))

        return super().build()

if __name__ == '__main__':
    Test().run()