"""
该模块存储多个显示不同信息的组件，用于不同的场景。
所有组件都通过暴露的接口完成信息的输入和展示
通过注册回调，可以实现信息的交互，模块的调用
包含以下组件：
    - MinLabel: 显示最小化的标签，用于显示信息
    - 
"""
from .iconlistitem import IconListItem,TestIconListItem
from .notification import Notification
