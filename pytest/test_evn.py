import sys
import os

# 添加项目根目录到模块查找路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.evn import external_resource_path,internal_resource_path

def test_path():
    resource = internal_resource_path("data/app.db")
    print(resource)
    image = external_resource_path("image.png")
    print(image)
    
if __name__=="__main__":
    test_path()