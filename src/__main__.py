"""
本模块是所有模块的最顶层，加载了所有模块并实现模块之间的
数据传输，函数绑定，所有的功能都在此处进行协调，完成最终的效果
本模块会导入无任何数据的kv代码，实现软件的UI和交互
会导入提供某项具体功能的代码，实现数据的处理，函数和数据的注入
"""
from kivy.config import Config
Config.set('kivy', 'exit_on_escape', 0)  # turns off exit on esc
Config.set('input', 'mouse', 'mouse,disable_multitouch')  # turns off the multi-touch emulation
#放弃模拟多点触控，并让右键正常释放
import sys
from core.kivymd_component.main_windows import MainProgram
from global_instance import api_manager
# import sys
# sys.path.append("D:/ProjectFloder/Python/LLMLanguageLearingSoftware")

class LLMStudioProgram(MainProgram):
    """
    此处会定义整个程序如何加载数据，加载kivy框架，动态生成组件
    回收机制，覆写机制，异常处理，同时也是所有模块的最高层
    """
    def on_start(self):
        """
        在此处实现程序启动的时候需要的工作
        """
        return super().on_start()

if __name__ == "__main__":
    print(sys.path)
    LLMStudioProgram().run()

    