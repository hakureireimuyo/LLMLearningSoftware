import sys
from pathlib import Path

# 自动添加项目根目录和 src 目录
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / "src"))

from src.app import TestApp
from src.components.common.hoverinfo import TextHoverInfo

class Test(TestApp):
    def build(self):
        self.com=TextHoverInfo()
        return super().build()
if __name__ == '__main__':
    Test().run()