import sys
from pathlib import Path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / "src"))
from src.app import TestApp

from src.components.custom.colordial import ColorDial
class Test(TestApp):
    def build(self):
        self.com=ColorDial()
        return super().build()
    
if __name__ == '__main__':
    Test().fps_monitor_start()
    Test().run()