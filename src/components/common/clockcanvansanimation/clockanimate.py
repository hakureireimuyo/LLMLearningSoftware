from kivy.clock import Clock
from kivy.properties import NumericProperty, ListProperty, ObjectProperty
import math
from collections import defaultdict
from bisect import bisect_right
import abc

# 抽象基类 - 缓动策略接口
class EasingStrategy(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def ease(self, t):
        """计算缓动函数值"""
        return t

# 具体缓动策略实现
class LinearEasing(EasingStrategy):
    """线性缓动函数"""
    def ease(self, t):
        return t

class InQuadEasing(EasingStrategy):
    """二次缓入函数"""
    def ease(self, t):
        return t * t

class OutQuadEasing(EasingStrategy):
    """二次缓出函数"""
    def ease(self, t):
        return 1 - (1 - t) * (1 - t)

class InOutQuadEasing(EasingStrategy):
    """二次缓入缓出函数"""
    def ease(self, t):
        if t < 0.5:
            return 2 * t * t
        else:
            return 1 - 2 * (1 - t) * (1 - t)

class InCubicEasing(EasingStrategy):
    """三次缓入函数"""
    def ease(self, t):
        return t * t * t

class OutCubicEasing(EasingStrategy):
    """三次缓出函数"""
    def ease(self, t):
        return 1 - (1 - t) ** 3

class InOutCubicEasing(EasingStrategy):
    """三次缓入缓出函数"""
    def ease(self, t):
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - 4 * (1 - t) ** 3

class InQuartEasing(EasingStrategy):
    """四次缓入函数"""
    def ease(self, t):
        return t ** 4

class OutQuartEasing(EasingStrategy):
    """四次缓出函数"""
    def ease(self, t):
        return 1 - (1 - t) ** 4

class InOutQuartEasing(EasingStrategy):
    """四次缓入缓出函数"""
    def ease(self, t):
        if t < 0.5:
            return 8 * t ** 4
        else:
            return 1 - 8 * (1 - t) ** 4

class InSineEasing(EasingStrategy):
    """正弦缓入函数"""
    def ease(self, t):
        return 1 - math.cos(t * math.pi / 2)

class OutSineEasing(EasingStrategy):
    """正弦缓出函数"""
    def ease(self, t):
        return math.sin(t * math.pi / 2)

class InOutSineEasing(EasingStrategy):
    """正弦缓入缓出函数"""
    def ease(self, t):
        return 0.5 * (1 - math.cos(math.pi * t))

class InExpoEasing(EasingStrategy):
    """指数缓入函数"""
    def ease(self, t):
        if t == 0:
            return 0
        return 2 ** (10 * (t - 1))

class OutExpoEasing(EasingStrategy):
    """指数缓出函数"""
    def ease(self, t):
        if t == 1:
            return 1
        return 1 - 2 ** (-10 * t)

class InOutExpoEasing(EasingStrategy):
    """指数缓入缓出函数"""
    def ease(self, t):
        if t == 0:
            return 0
        if t == 1:
            return 1
        if t < 0.5:
            return 0.5 * 2 ** (20 * t - 10)
        else:
            return 1 - 0.5 * 2 ** (10 - 20 * t)

class InCircEasing(EasingStrategy):
    """圆形缓入函数"""
    def ease(self, t):
        return 1 - math.sqrt(1 - t * t)

class OutCircEasing(EasingStrategy):
    """圆形缓出函数"""
    def ease(self, t):
        return math.sqrt(1 - (t - 1) ** 2)

class InOutCircEasing(EasingStrategy):
    """圆形缓入缓出函数"""
    def ease(self, t):
        if t < 0.5:
            return 0.5 * (1 - math.sqrt(1 - 4 * t * t))
        else:
            return 0.5 * (math.sqrt(1 - 4 * (1 - t) ** 2) + 1)

class InElasticEasing(EasingStrategy):
    """弹性缓入函数"""
    def ease(self, t):
        if t == 0:
            return 0
        if t == 1:
            return 1
        return -2 ** (10 * t - 10) * math.sin((10 * t - 10.75) * (2 * math.pi) / 3)

class OutElasticEasing(EasingStrategy):
    """弹性缓出函数"""
    def ease(self, t):
        if t == 0:
            return 0
        if t == 1:
            return 1
        return 2 ** (-10 * t) * math.sin((10 * t - 0.75) * (2 * math.pi) / 3) + 1

class InOutElasticEasing(EasingStrategy):
    """弹性缓入缓出函数"""
    def ease(self, t):
        if t == 0:
            return 0
        if t == 1:
            return 1
        if t < 0.5:
            return -0.5 * 2 ** (20 * t - 10) * math.sin((20 * t - 11.125) * (2 * math.pi) / 4.5)
        else:
            return 0.5 * 2 ** (-20 * t + 10) * math.sin((20 * t - 11.125) * (2 * math.pi) / 4.5) + 1

class InBounceEasing(EasingStrategy):
    """弹跳缓入函数"""
    def ease(self, t):
        return 1 - OutBounceEasing().ease(1 - t)

class OutBounceEasing(EasingStrategy):
    """弹跳缓出函数"""
    def ease(self, t):
        if t < 1 / 2.75:
            return 7.5625 * t * t
        elif t < 2 / 2.75:
            t -= 1.5 / 2.75
            return 7.5625 * t * t + 0.75
        elif t < 2.5 / 2.75:
            t -= 2.25 / 2.75
            return 7.5625 * t * t + 0.9375
        else:
            t -= 2.625 / 2.75
            return 7.5625 * t * t + 0.984375

class InOutBounceEasing(EasingStrategy):
    """弹跳缓入缓出函数"""
    def ease(self, t):
        if t < 0.5:
            return 0.5 * InBounceEasing().ease(2 * t)
        else:
            return 0.5 * OutBounceEasing().ease(2 * t - 1) + 0.5

# 缓动函数工厂类
class EasingFactory:
    """缓动函数工厂，根据名称创建缓动策略对象"""
    
    _easing_strategies = {
        'linear': LinearEasing(),
        'in_quad': InQuadEasing(),
        'out_quad': OutQuadEasing(),
        'in_out_quad': InOutQuadEasing(),
        'in_cubic': InCubicEasing(),
        'out_cubic': OutCubicEasing(),
        'in_out_cubic': InOutCubicEasing(),
        'in_quart': InQuartEasing(),
        'out_quart': OutQuartEasing(),
        'in_out_quart': InOutQuartEasing(),
        'in_sine': InSineEasing(),
        'out_sine': OutSineEasing(),
        'in_out_sine': InOutSineEasing(),
        'in_expo': InExpoEasing(),
        'out_expo': OutExpoEasing(),
        'in_out_expo': InOutExpoEasing(),
        'in_circ': InCircEasing(),
        'out_circ': OutCircEasing(),
        'in_out_circ': InOutCircEasing(),
        'in_elastic': InElasticEasing(),
        'out_elastic': OutElasticEasing(),
        'in_out_elastic': InOutElasticEasing(),
        'in_bounce': InBounceEasing(),
        'out_bounce': OutBounceEasing(),
        'in_out_bounce': InOutBounceEasing(),
    }
    
    @classmethod
    def get_easing(cls, name):
        """获取缓动策略"""
        # 默认使用线性缓动
        strategy = cls._easing_strategies.get(name)
        if strategy is None:
            strategy = cls._easing_strategies['linear']
        return strategy
    
    @classmethod
    def available_easings(cls):
        """获取所有可用的缓动函数名称"""
        return list(cls._easing_strategies.keys())

# 基于策略模式重构的动画类
class ClockAnimation:
    """基于Clock的动画实现，支持串联(+)和并联(&)运算符"""
    duration = NumericProperty(1.0)
    transition = ListProperty(['linear'])
    easing_strategy = ObjectProperty(LinearEasing())
    
    def __init__(self, **kwargs):
        super().__init__()
        self._clock_event = None
        self._proxy = None
        self._properties = defaultdict(list)  # 每个属性对应关键帧列表 [(时间, 值)]
        self._on_complete = None
        self._repeat = False
        self._progress = 0.0
        self._is_running = False
        
        # 解析传入的属性
        for key, value in kwargs.items():
            if key in ('duration', 'transition', 'repeat'):
                setattr(self, key, value)
            else:
                # 处理不同类型的属性输入
                if isinstance(value, (list, tuple)):
                    # 如果传入的是关键帧列表 [(时间, 值), ...]
                    self._properties[key] = value
                else:
                    # 单个值作为最后的关键帧 (时间=0 作为起始关键帧)
                    self._properties[key] = [(0, None), (self.duration, value)]
        
        # 根据传入的transition设置缓动策略
        if 'transition' in kwargs:
            self.easing_strategy = EasingFactory.get_easing(
                kwargs['transition'][0] if isinstance(kwargs['transition'], list) 
                else kwargs['transition']
            )
    
    def start(self, proxy):
        """启动动画"""
        if self._is_running:
            self.stop()
        
        self._proxy = proxy
        self._is_running = True
        
        # 计算最大持续时间
        self.duration = self._calculate_max_duration()
        
        # 处理起始关键帧
        for prop, frames in self._properties.items():
            # 对起始关键帧进行特殊处理（值为None表示使用当前值）
            if frames[0][1] is None:
                current_value = getattr(proxy, prop)
                frames[0] = (0.0, current_value)
        
        self._progress = 0.0
        self._clock_event = Clock.schedule_interval(self._update, 1/60.)
        return self
    
    def _calculate_max_duration(self):
        """计算所有属性的最大持续时间"""
        max_duration = 0.0
        for frames in self._properties.values():
            if frames and frames[-1][0] > max_duration:
                max_duration = frames[-1][0]
        return max_duration
    
    def _update(self, dt):
        """更新动画进度"""
        self._progress += dt
        
        if self._progress >= self.duration:
            # 动画结束
            self._apply_progress(self.duration)
            
            if self._repeat:
                self._progress = 0.0
            else:
                self.stop()
                if self._on_complete:
                    self._on_complete(self)
        else:
            self._apply_progress(self._progress)
    
    def _apply_progress(self, t_abs):
        """应用当前绝对时间进度"""
        if not self._proxy:
            return
        
        for prop, frames in self._properties.items():
            # 跳过空关键帧
            if not frames:
                continue
                
            # 处理当前时间点对应的值
            if t_abs <= frames[0][0]:
                # 尚未到第一个关键帧
                setattr(self._proxy, prop, frames[0][1])
            elif t_abs >= frames[-1][0]:
                # 超过最后一个关键帧
                setattr(self._proxy, prop, frames[-1][1])
            else:
                # 找到当前时间所处的关键帧区间
                # 使用二分查找确定右边界
                right_index = bisect_right([frame[0] for frame in frames], t_abs)
                left_index = right_index - 1
                
                t0, v0 = frames[left_index]
                t1, v1 = frames[right_index]
                
                # 计算区间内的局部进度 [0, 1]
                local_progress = (t_abs - t0) / (t1 - t0) if t1 > t0 else 0.0
                
                # 使用缓动策略计算变换后的进度
                t_val = self.easing_strategy.ease(local_progress)
                
                # 处理不同类型的值
                if isinstance(v0, (list, tuple)) and isinstance(v1, (list, tuple)):
                    # 向量属性（如pos, size）
                    current = tuple(v0_i + (v1_i - v0_i) * t_val for v0_i, v1_i in zip(v0, v1))
                else:
                    # 标量属性
                    current = v0 + (v1 - v0) * t_val
                
                setattr(self._proxy, prop, current)
    
    def stop(self):
        """停止动画"""
        if self._clock_event:
            Clock.unschedule(self._clock_event)
            self._clock_event = None
        self._is_running = False
    
    def bind(self, on_complete=None):
        """绑定完成回调"""
        if on_complete:
            self._on_complete = on_complete
        return self
    
    def __add__(self, other):
        """串联运算符 (+) - 将两个动画在时间上拼接起来"""
        new_anim = ClockAnimation()
        new_anim._on_complete = self._on_complete
        new_anim.easing_strategy = self.easing_strategy  # 继承第一个动画的缓动策略
        
        # 收集所有属性
        all_props = set(self._properties.keys()) | set(other._properties.keys())
        
        for prop in all_props:
            frames = []
            
            # 添加第一个动画的关键帧
            if prop in self._properties:
                frames.extend(self._properties[prop])
            
            # 计算第一个动画的结束时间
            offset = max([frame[0] for frame in frames]) if frames else 0.0
            
            # 添加第二个动画的关键帧（时间偏移）
            if prop in other._properties:
                for t, value in other._properties[prop]:
                    # 跳过第二个动画中时间为0的起始关键帧
                    if frames and t == 0 and value is None:
                        continue
                    frames.append((t + offset, value))
            
            # 对关键帧按时间排序
            frames.sort(key=lambda x: x[0])
            new_anim._properties[prop] = frames
        
        # 计算新动画的总持续时间
        new_anim.duration = new_anim._calculate_max_duration()
        return new_anim
    
    def __and__(self, other):
        """并联运算符 (&) - 同时播放两个动画"""
        new_anim = ClockAnimation()
        new_anim._on_complete = self._on_complete
        new_anim.easing_strategy = self.easing_strategy  # 继承第一个动画的缓动策略
        
        # 收集所有属性
        all_props = set(self._properties.keys()) | set(other._properties.keys())
        
        for prop in all_props:
            frames = []
            
            # 处理两个动画都有的属性 - 时间片合并
            if prop in self._properties and prop in other._properties:
                # 获取两个属性的关键帧
                frames1 = self._properties[prop]
                frames2 = other._properties[prop]
                
                # 提取所有的时间点
                time_points = sorted(set(frame[0] for frame in frames1) | set(frame[0] for frame in frames2))
                
                # 在每个时间点插值
                for t in time_points:
                    # 获取两个动画在当前时间点的值
                    v1 = self._get_value_at_time(frames1, t)
                    v2 = self._get_value_at_time(frames2, t)
                    
                    # 计算合并值（平均）
                    if v1 is not None and v2 is not None:
                        if isinstance(v1, (list, tuple)) and isinstance(v2, (list, tuple)):
                            # 向量属性取平均
                            merged_value = tuple((v1_i + v2_i) / 2 for v1_i, v2_i in zip(v1, v2))
                        else:
                            # 标量属性取平均
                            merged_value = (v1 + v2) / 2
                        frames.append((t, merged_value))
                    elif v1 is not None:
                        frames.append((t, v1))
                    elif v2 is not None:
                        frames.append((t, v2))
            
            # 处理只有一个动画有的属性
            elif prop in self._properties:
                frames = self._properties[prop][:]
            elif prop in other._properties:
                frames = other._properties[prop][:]
            
            # 对关键帧按时间排序
            frames.sort(key=lambda x: x[0])
            new_anim._properties[prop] = frames
        
        # 计算新动画的总持续时间
        new_anim.duration = max(self.duration, other.duration)
        return new_anim
    
    def _get_value_at_time(self, frames, t):
        """在给定时间获取关键帧的值（或插值）"""
        if not frames:
            return None
            
        # 找到当前时间所处的关键帧区间
        indices = [i for i, frame in enumerate(frames) if frame[0] <= t]
        
        if not indices:
            return frames[0][1]
        
        # 最后一个 <= t 的关键帧
        last_index = indices[-1]
        
        if t >= frames[-1][0]:
            return frames[-1][1]
            
        if last_index == len(frames) - 1:
            return frames[-1][1]
        
        # 获取区间
        t0, v0 = frames[last_index]
        t1, v1 = frames[last_index + 1]
        
        if t0 == t1 or v0 is None or v1 is None:
            return v0 if v0 is not None else v1
            
        # 计算局部进度
        local_progress = (t - t0) / (t1 - t0)
        # 使用缓动策略
        t_val = self.easing_strategy.ease(local_progress)
        
        # 插值
        if isinstance(v0, (list, tuple)) and isinstance(v1, (list, tuple)):
            return tuple(v0_i + (v1_i - v0_i) * t_val for v0_i, v1_i in zip(v0, v1))
        else:
            return v0 + (v1 - v0) * t_val