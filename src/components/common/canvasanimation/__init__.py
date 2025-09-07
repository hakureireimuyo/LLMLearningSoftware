# from .old.baranimateitem import BarAnimateItem
# from .old.circleanimateitem import CircleAnimateItem
#from .dynamicanimatelabel import DynamicAnimateLabel
"""
动画项基类实现了对于canvas对象的多个动画阶段进行管理
用户可以通过灵活设置每个对象的三个阶段的动画和生成方法
就能够轻易的管理几百个动画对象
除了初始化的生成方法,该对象还支持在启动后添加新的canvas对象
这就可以实现通过该方法让任意需求都能被实现
比如需要实时显示声音频率和音量
或者单纯的需要一个不断生成的背景动画
"""
from .pulseloop import PulseCircle
from .risingmatrix import RisingMatrix
from .risingmatrixanimated import RisingMatrixAnimated
from .waveloop import WaveLoop
from .rotatematrix import RotateMatrixAnimated

__all__ = ["PulseCircle", 
           "RisingMatrix",
           "RisingMatrixAnimated",
           "WaveLoop",
           "RotateMatrixAnimated"]