import sys
from pathlib import Path

# 自动添加项目根目录和 src 目录
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / "src"))

from src.components.custom.audiolevelvisualizer import AudioVisualizerContainer
import random
import time
from src.app import TestApp
import threading

class RandomDataGenerator:
    """
    随机数据生成器
    提供开始和停止方法控制数据生成循环
    
    属性:
        callback: 数据更新回调函数
        frequency: 数据生成频率（Hz）
        min_val: 最小值
        max_val: 最大值
        is_running: 指示生成器是否正在运行
    """
    
    def __init__(self, callback, frequency=15, min_val=0, max_val=100):
        """
        初始化随机数据生成器
        
        参数:
            callback: 数据更新回调函数
            frequency: 数据生成频率（Hz），默认15Hz
            min_val: 随机值最小值，默认0
            max_val: 随机值最大值，默认100
        """
        self.callback = callback
        self.frequency = frequency
        self.min_val = min_val
        self.max_val = max_val
        self.is_running = False
        self._thread = None
        self._stop_event = threading.Event()
    
    def start(self):
        """启动数据生成循环"""
        if self.is_running:
            print("数据生成器已在运行中")
            return
        
        # 确保之前的线程已停止
        self._stop_event.clear()
        
        # 创建并启动新线程
        self._thread = threading.Thread(target=self._run, daemon=True)
        self.is_running = True
        self._thread.start()
        print(f"数据生成器已启动，频率: {self.frequency}Hz")
    
    def stop(self):
        """停止数据生成循环"""
        if not self.is_running:
            print("数据生成器未运行")
            return
        
        # 设置停止标志
        self._stop_event.set()
        
        # 等待线程结束
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        
        self.is_running = False
        print("数据生成器已停止")
    
    def _run(self):
        """内部线程运行方法"""
        interval = 1.0 / self.frequency
        
        while not self._stop_event.is_set():
            # 生成随机值
            value = random.uniform(self.min_val, self.max_val)
            
            # 调用回调函数
            if self.callback:
                self.callback(value)
            #print(f"生成随机值: {value}")
            # 精确等待指定间隔
            start_time = time.time()
            while time.time() - start_time < interval:
                if self._stop_event.is_set():
                    return
                time.sleep(0.001)  # 短暂睡眠减少CPU占用
    
    def set_frequency(self, frequency):
        """设置数据生成频率（Hz）"""
        self.frequency = max(1, frequency)  # 确保频率至少为1Hz
        print(f"数据生成频率已更新: {self.frequency}Hz")
    
    def set_value_range(self, min_val, max_val):
        """设置随机值范围"""
        self.min_val = min_val
        self.max_val = max_val
        print(f"随机值范围已更新: [{min_val}, {max_val}]")
    
    def __del__(self):
        """析构函数确保线程停止"""
        self.stop()

from kivymd.uix.button import  MDButton,MDButtonText
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.metrics import dp

class Test(TestApp):
    def build(self):
        self.avc=AudioVisualizerContainer()
        self._random=RandomDataGenerator(
            callback=lambda x:self.avc.update_visualize(x),
        )
        self.com=MDBoxLayout(orientation="vertical",size_hint=(1,1),padding=[50,10,10,10],pos_hint={"center_x":0.5,"center_y":0.5})
        self.com.add_widget(self.avc)
        _md=MDBoxLayout(orientation="horizontal",size_hint=(1,None),height=dp(50))
        self.com.add_widget(_md)
        
        self._button=MDButton(
            MDButtonText(text="open"),
            on_release=lambda *arges:self.avc.open(),
        )
        _md.add_widget(self._button)
    
        self._button=MDButton(
            MDButtonText(text="close"),
            on_release=lambda *arges:self.avc.close(),
        )
        _md.add_widget(self._button)
        self._button=MDButton(
            MDButtonText(text="start"),
            on_release=lambda *arges:self.avc.start(), 
        )
        _md.add_widget(self._button)
        self._button=MDButton(
            MDButtonText(text="pause"),
            on_release=lambda *arges:self.avc.pause(), 
        )
        _md.add_widget(self._button)
        self._button=MDButton(
            MDButtonText(text="resume"),
            on_release=lambda *arges:self.avc.resume(), 
        )
        _md.add_widget(self._button)

        self._button=MDButton(
            MDButtonText(text="stop"),
            on_release=lambda *arges:self.avc.stop()
        )
        _md.add_widget(self._button)
        self._button=MDButton(
            MDButtonText(text="change_visualize_mode"),
            on_release=lambda *arges:self.avc.change_visualize_mode()
        )
        _md.add_widget(self._button)

        self._button=MDButton(
            MDButtonText(text="start_random_data_generator"),
            on_release=lambda *arges:self._random.start()
        )
        _md.add_widget(self._button)

        self._button=MDButton(
            MDButtonText(text="stop_random_data_generator"),
            on_release=lambda *arges:self._random.stop()
        )
        _md.add_widget(self._button)

        return super().build()
    

if __name__=="__main__":
    Test().fps_monitor_start()
    Test().run()