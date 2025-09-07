"""
基于Kivy.Clock实现下一帧调用的回调管理模块
主要功能可以注册多个回调函数，支持多个参数传递
"""
from functools import partial
from kivy.clock import Clock
from typing import Dict, List, Callable, Any
import traceback

class CallbackManager:
    """
    独立的回调管理系统
    """
    def __init__(self):
        # 存储结构：{事件类型: [(包装函数, 原始函数)]}
        self._callbacks: Dict[str, List[tuple]] = {}

    def register(
        self,
        event_type: str,
        callback: Callable,
        *fixed_args,
        **fixed_kwargs
    ) -> None:
        """注册回调函数
        :param event_type: 事件类型标识 (例如 "on_click")
        :param callback: 回调函数
        :param fixed_args: 固定位置参数
        :param fixed_kwargs: 固定关键字参数
        """
        if event_type not in self._callbacks:
            self._callbacks[event_type] = []
        
        # 使用partial固定参数并保留原始回调引用
        wrapped = partial(self._safe_call, callback, 
                        fixed_args, fixed_kwargs)
        self._callbacks[event_type].append( (wrapped, callback) )

    def unregister(self, event_type: str, callback: Callable) -> None:
        """移除回调函数"""
        if event_type in self._callbacks:
            self._callbacks[event_type] = [
                (w, c) for (w, c) in self._callbacks[event_type]
                if c != callback
            ]

    def trigger(
        self,
        event_type: str,
        *dynamic_args,
        delay: bool = False,
        **dynamic_kwargs
    ) -> None:
        """触发回调
        :param delay: 是否延迟到下一帧执行
        :param dynamic_args: 动态位置参数
        :param dynamic_kwargs: 动态关键字参数
        """
        if event_type not in self._callbacks:
            return

        for wrapped, _ in self._callbacks[event_type]:
            if delay:
                Clock.schedule_once(
                    lambda dt: wrapped(*dynamic_args, **dynamic_kwargs)
                )
            else:
                wrapped(*dynamic_args, **dynamic_kwargs)
    
    def _safe_call(self, callback: Callable, fixed_args: tuple, fixed_kwargs: dict,
                 *dynamic_args, **dynamic_kwargs) -> None:
        """执行回调并增强异常捕获"""
        try:
            merged_args = fixed_args + dynamic_args
            merged_kwargs = {**fixed_kwargs, **dynamic_kwargs}
            callback(*merged_args, **merged_kwargs)
        except Exception as e:
            # 收集完整错误信息
            error_info = {
                'callback': callback,
                'exception': e,
                'traceback': traceback.format_exc(),
                'args': merged_args,
                'kwargs': merged_kwargs
            }
            self._handle_error(error_info)  # 传递结构化错误信息

    def _handle_error(self, error_info: dict) -> None:
        """错误处理方法（可被子类扩展）"""
        cb_name = error_info['callback'].__name__
        tb = error_info['traceback']
        args = error_info['args']
        kwargs = error_info['kwargs']
        
        print(f"[Callback Error] {cb_name}\n"
              f"Arguments: {args}\n"
              f"Keyword args: {kwargs}\n"
              f"Exception: {error_info['exception']}\n"
              f"Traceback:\n{tb}")
    def set(
        self,
        event_type: str,
        callback: Callable,
        *fixed_args,
        **fixed_kwargs
    ) -> None:
        """替换指定事件类型的所有回调为新的回调"""
        self.clear(event_type)
        self.register(event_type, callback, *fixed_args, **fixed_kwargs)

    def exchange(self, event_a: str, event_b: str) -> None:
        """交换两个事件类型的回调函数列表
        
        若两个事件类型均存在，则它们的回调列表将互换。
        若任一事件类型不存在，则不执行任何操作。
        """
        if event_a in self._callbacks and event_b in self._callbacks:
            self._callbacks[event_a], self._callbacks[event_b] = (
                self._callbacks[event_b], 
                self._callbacks[event_a]
            )

    def clear(self, event_type: str = None) -> None:
        """清空回调"""
        if event_type:
            self._callbacks.pop(event_type, None)
        else:
            self._callbacks.clear()
    