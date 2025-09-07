"""
信号处理模块 - 提供各种平滑和滤波算法
"""

import numpy as np
from collections import deque

class ExponentialSmoothing:
    """指数平滑滤波器"""
    def __init__(self, alpha=0.3):
        self.alpha = alpha  # 平滑因子 (0 < alpha < 1)
        self.smoothed = None
    
    def smooth(self, value):
        if self.smoothed is None:
            self.smoothed = value
        else:
            self.smoothed = self.alpha * value + (1 - self.alpha) * self.smoothed
        return self.smoothed

class MovingAverage:
    """简单移动平均滤波器"""
    def __init__(self, window_size=5):
        self.window_size = window_size
        self.values = deque(maxlen=window_size)
    
    def smooth(self, value):
        self.values.append(value)
        return sum(self.values) / len(self.values) if self.values else value

class WeightedMovingAverage:
    """加权移动平均滤波器"""
    def __init__(self, window_size=5):
        self.window_size = window_size
        self.values = deque(maxlen=window_size)
        # 创建权重：最近的值权重最大
        self.weights = np.linspace(1, 0.2, window_size)
    
    def smooth(self, value):
        self.values.append(value)
        if len(self.values) < self.window_size:
            return sum(self.values) / len(self.values)
        return np.dot(np.array(self.values), self.weights) / np.sum(self.weights)

class DoubleExponentialSmoothing:
    """双重指数平滑（带趋势）"""
    def __init__(self, alpha=0.3, beta=0.1):
        self.alpha = alpha  # 水平平滑因子
        self.beta = beta    # 趋势平滑因子
        self.level = None
        self.trend = None
    
    def smooth(self, value):
        if self.level is None or self.trend is None:
            self.level = value
            self.trend = 0
            return value
        
        last_level = self.level
        self.level = self.alpha * value + (1 - self.alpha) * (self.level + self.trend)
        self.trend = self.beta * (self.level - last_level) + (1 - self.beta) * self.trend
        
        return self.level

class MedianFilter:
    """中值滤波器（有效去除离群点）"""
    def __init__(self, window_size=5):
        self.window_size = window_size
        self.values = deque(maxlen=window_size)
    
    def smooth(self, value):
        self.values.append(value)
        if len(self.values) < self.window_size:
            return value
        return sorted(self.values)[len(self.values) // 2]

class KalmanFilter:
    """卡尔曼滤波器（适合动态系统）"""
    def __init__(self, process_variance=1e-4, measurement_variance=0.1):
        # 初始化参数
        self.process_variance = process_variance
        self.measurement_variance = measurement_variance
        self.posteri_estimate = 0.0
        self.posteri_error_estimate = 1.0
    
    def smooth(self, measurement):
        # 预测步骤
        priori_estimate = self.posteri_estimate
        priori_error_estimate = self.posteri_error_estimate + self.process_variance
        
        # 更新步骤
        blending_factor = priori_error_estimate / (priori_error_estimate + self.measurement_variance)
        self.posteri_estimate = priori_estimate + blending_factor * (measurement - priori_estimate)
        self.posteri_error_estimate = (1 - blending_factor) * priori_error_estimate
        
        return self.posteri_estimate

class AdaptiveSmoothing:
    """自适应指数平滑（根据变化率调整平滑因子）"""
    def __init__(self, min_alpha=0.1, max_alpha=0.9, sensitivity=0.5):
        self.min_alpha = min_alpha
        self.max_alpha = max_alpha
        self.sensitivity = sensitivity  # 灵敏度 (0-1)
        self.last_value = None
        self.smoothed = None
    
    def smooth(self, value):
        if self.smoothed is None:
            self.smoothed = value
            self.last_value = value
            return value
        
        # 计算变化率
        change_rate = abs(value - self.last_value) / max(1, abs(self.last_value))
        
        # 自适应调整alpha
        alpha = self.min_alpha + (self.max_alpha - self.min_alpha) * min(1.0, change_rate * self.sensitivity)
        
        # 应用指数平滑
        self.smoothed = alpha * value + (1 - alpha) * self.smoothed
        self.last_value = value
        
        return self.smoothed

# 辅助函数
def normalize(value, min_val, max_val):
    """将值归一化到0-1范围"""
    return (value - min_val) / (max_val - min_val) if max_val > min_val else 0

def clamp(value, min_val, max_val):
    """限制值在指定范围内"""
    return max(min_val, min(value, max_val))