"""
本模块实现一个输入栏，主要具有以下功能
1. 定义输入栏的样式
2. 定义输入栏的行为
3. 定义输入栏的功能
4. 定义输入栏的布局
5. 输入栏在滚动视图时会缩回
"""

from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, NumericProperty, OptionProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.app import MDApp
from kivy.metrics import dp,sp
from kivy.core.window import Window
from kivymd.uix.button import MDIconButton
from kivymd.uix.tooltip import MDTooltip
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.clock import Clock
from kivy.animation import Animation
import threading
import time
#import sounddevice as sd  # 需要安装 sounddevice 库
from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.uix.boxlayout import MDBoxLayout
import pyaudio
import numpy as np
from typing import Callable, Optional

class AudioRecorder:
    def __init__(
        self,
        sr: int = 16000,
        channels: int = 1,
        dtype: str = 'float32',
        asr_instance: Optional[object] = None,
        mode: str = 'batch',
        volume_callback: Optional[Callable[[float], None]] = None,
        error_callback: Optional[Callable[[Exception], None]] = None
    ):
        # 音频参数
        self.sr = sr
        self.channels = channels
        self.dtype = self._get_pyaudio_format(dtype)
        self.asr = asr_instance
        self.mode = mode
        
        # PyAudio 实例
        self.p = pyaudio.PyAudio()
        
        # 线程控制
        self._recording = False
        self._stream = None
        self._audio_buffer = []
        
        # 回调函数
        self.volume_cb = volume_callback
        self.error_cb = error_callback
        #终止标志
        self._should_terminate = False  
        self._validate_parameters()

    def _get_pyaudio_format(self, dtype: str) -> int:
        """将numpy类型转换为PyAudio格式"""
        format_map = {
            'float32': pyaudio.paFloat32,
            'int32': pyaudio.paInt32,
            'int16': pyaudio.paInt16
        }
        return format_map.get(dtype, pyaudio.paFloat32)

    def _validate_parameters(self):
        if self.mode not in ['batch', 'stream']:
            raise ValueError("Invalid mode, must be 'batch' or 'stream'")
            
        if self.asr and (
            not hasattr(self.asr, 'one_shot_recognize') or 
            not hasattr(self.asr, 'streaming_recognize')
        ):
            raise ValueError("ASR实例必须实现 one_shot_recognize 和 streaming_recognize 方法")

    def _audio_callback(self, in_data, frame_count, time_info, status):
        try:
            # 转换为numpy数组
            audio_np = np.frombuffer(in_data, dtype=np.float32)
            
            # 实时音量计算
            if self.volume_cb:
                rms = np.sqrt(np.mean(audio_np**2))
                self.volume_cb(rms)
                
            # 流模式处理
            if self.mode == 'stream' and self.asr:
                self.asr.streaming_recognize(audio_np.copy())
            
            # 保存音频数据
            self._audio_buffer.append(audio_np.copy())
            
            return (None, pyaudio.paContinue)
        except Exception as e:
            self._handle_error(e)
            return (None, pyaudio.paAbort)

    def _handle_error(self, error: Exception):
        if self.error_cb:
            self.error_cb(error)
        else:
            print(f"录音错误: {str(error)}")

    def start_recording(self):
        try:
            if self._recording:
                raise RuntimeError("录音已在进行中")
            self._recording = True
            self._audio_buffer = []
            
            # 创建音频流
            self._stream = self.p.open(
                format=self.dtype,
                channels=self.channels,
                rate=self.sr,
                input=True,
                stream_callback=self._audio_callback,
                frames_per_buffer=1024
            )
            
            self._stream.start_stream()
            
        except Exception as e:
            self._handle_error(e)
            self._recording = False

    def stop_recording(self, save_path: Optional[str] = None):
        #print("stop_recording")
        result=None
        try:
            if not self._recording:
                print("未开始录音")
                return None
            #print(self._recording)
            
            if self._stream and self._stream.is_active():
                self._stream.stop_stream()
                self._stream.close()
            self._recording = False
            # 合并数据前检查缓冲区
            if not self._audio_buffer:
                print("无录音数据")
                return None
            # 合并音频数据
            audio_data = np.concatenate(self._audio_buffer, axis=0)
            scaled = np.int16(audio_data * 32767)
            audio_bytes = scaled.tobytes()
            # 模式处理
            if self.mode == 'batch' and self.asr:
                result = self.asr.one_shot_recognize(audio_bytes)
                print(f"批量识别结果: {result}")
            elif self.mode == 'stream' and self.asr:
                result = self.asr.one_shot_recognize(audio_bytes)
                print(f"最终识别结果: {result}")
            
            # 保存数据
            if save_path:
                self._save_audio(audio_data, save_path)
            return result
        except Exception as e:
            self._handle_error(e)
            return None  # 确保返回None
        finally:
            # 统一资源释放（线程安全）
            self._recording = False
            if self._stream:
                try:
                    self._stream.stop_stream()
                except OSError as e:
                    if e.errno != -9988:
                        raise
                self._stream.close()
                self._stream = None
            self._audio_buffer.clear()
            

    def _save_audio(self, data: np.ndarray, path: str):
        """保存为WAV文件"""
        try:
            from scipy.io.wavfile import write
            scaled = np.int16(data * 32767)
            write(path, self.sr, scaled)
        except IOError as e:
            error_msg = f"保存失败: {str(e)}"
            self._handle_error(IOError(error_msg))
        except Exception as e:
            self._handle_error(e)

    def emergency_stop(self):
        """线程安全的紧急停止"""
        with threading.Lock():
            self._recording = False
            if self._stream:
                try:
                    self._stream.stop_stream()
                except OSError as e:
                    if e.errno!= -9988:
                        raise(e)
                self._stream.close()
                self._stream = None
            self._audio_buffer.clear()

class DummyASR:
    def __init__(self,instance=None):
        self.instance=instance
        pass
    def one_shot_recognize(self, data):
        return self.instance.recognize_sync(data)
        
    def streaming_recognize(self, data):
        #print(f"收到流式数据: {len(data)} 采样点")
        ...

def volume_handler(vol):
    print(f"当前音量: {vol:.4f}")

from global_instance import baidu_stt,zhipu_group
chuck_ai=zhipu_group.create_instance('glm-4-flash')
chuck_ai.set_system_prompt("我将会输入一些通过语音识别得到的英语文本内容，你需要尝试修复识别出来的文本中的错误，给句子添加标点符号，不要多加无用的符号，只返回文本内容，不要返回任何其他信息。如果输入的文本过于简短或者无法理解，那就直接返回原始文本内容。")

KV = """
<YourTooltipClass>
    MDTooltipPlain:
        text:root.text_tool
        font_style: "STSONG" 
        font_role:"large"
        
<TooltipMDIconButton>
    MDIconButton:
        icon: root.icon
<DynamicAnimateLabel>:
    size_hint:None,None
    size:"200dp","200dp"
    pos_hint:{"center_x":.5,"center_y":.5}
    md_bg_color:app.theme_cls.secondaryContainerColor

<VoiceDynamicLabel>:
    #pos_hint:{"x":1,"y":1}
    MDBoxLayout:
        id:VoiceDynamicLabel
        #md_bg_color:app.theme_cls.primaryColor
        orientation:"vertical"
        size_hint:None,None
        size:"300dp","200dp"
        pos_hint:{"center_x":.5,"center_y":-20}
        DynamicAnimateLabel:
            id:DynamicAnimateLabel
        MDLabel:
            id:Voice_text
            text:"语音输入中..."
            font_style: "STSONG"
            font_role:"medium"
            halign:"center"
            valign:"middle"

<ChatInput>:
    orientation: "vertical"
    padding: dp(10)
    md_bg_color: app.theme_cls.backgroundColor
    size_hint_y: None
    height: self.minimum_height + dp(20)
    MDBoxLayout:
        orientation: "horizontal"
        size_hint_y: None
        height: dp(20)
        padding: dp(5)
        spacing: dp(10)
        id: button_container
        
    MDBoxLayout:
        size_hint_y: None
        height: self.minimum_height
        MDTextField:
            id: input_field
            hint_text: "输入内容"
            multiline: True
            size_hint_y: None
            font_name: "STSONG"  # 设置中文字体
            font_size: "26sp"  # 设置字体大小
            on_text: root.input(self.text)
            on_text_validate: root.on_enter()
            on_focus: root.is_focus = self.focus
            disabled: False  # 初始启用状态
            MDTextFieldHelperText:
                mode: "on_focus"
            MDTextFieldTrailingIcon:
                id: trailing_icon
                icon: "send"
                on_touch_down: root.on_enter()
<ErrorPopup>:
    md_bg_color: app.theme_cls.errorContainerColor
    font_style: "STSONG"  # 设置中文字体
    role: "medium"  # 设置字体大小
    size_hint: None, None
    size:dp(200),dp(100)
    halign: "center"  # 水平居中
    valign: "middle"  # 垂直居中
    #pos_hint: {"center_x": .5, "center_y": .5}
    opacity: 0
    radius: [dp(10),dp(10),dp(10),dp(10)]  # 设置圆角半径

"""
Builder.load_string(KV)

class YourTooltipClass(MDTooltip):
    '''Implements your tooltip base class.'''

class TooltipMDIconButton(YourTooltipClass, MDIconButton):
    '''Implements a button with tooltip behavior.'''
    icon = StringProperty()
    text_tool=StringProperty()
    callback=ObjectProperty(None)
    inputHeight=NumericProperty(0)
    def __init__(self,callback=None, **kwargs):
        super().__init__(**kwargs)
        self.callback=callback
        if self.inputHeight!=0:
            self.ids.input_field.height=self.inputHeight

    def on_press(self, *args):
        #print("鼠标点击")
        if self.callback:
            self.callback()
        return True
    
class HoverIconButton(MDIconButton):
    """
    悬浮弹出提示
    """
    hovered = BooleanProperty(False)
    text=StringProperty()
    icon=StringProperty()
    tooltip_text = StringProperty()

    def __init__(self,callback=None, **kwargs):
        super(HoverIconButton, self).__init__(**kwargs)
        self.bind(on_enter=self.show_tooltip)
        self.bind(on_leave=self.hide_tooltip)
        self.callback=callback

    def on_enter(self, *args):
        self.hovered = True

        #print("鼠标进入")

    def on_leave(self, *args):
        self.hovered = False
        #print("鼠标离开")

    def on_press(self, *args):
        #print("鼠标点击")
        if self.callback:
            self.callback()
        return True
    
#异常信息提示框


class ExponentialSmoothing:
    def __init__(self, alpha=0.3):
        self.alpha = alpha  # 越小越平滑（但响应变慢）
        self.smoothed = None
    
    def smooth(self, value):
        if self.smoothed is None:
            self.smoothed = value
        else:
            self.smoothed = self.alpha * value + (1 - self.alpha) * self.smoothed
        return self.smoothed
    
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.properties import NumericProperty, ListProperty
from kivymd.uix.floatlayout import MDFloatLayout
import math

class DynamicAnimateLabel(MDBoxLayout):
    animation_mode = StringProperty("bars")  # 新增动画模式属性
    is_animating = BooleanProperty(False)

    # 柱状图模式专有属性
    frequency = NumericProperty(15.675)         # 生成频率（Hz）
    time_window = NumericProperty(0.0638)     # 超时时间（秒）
    spacing = NumericProperty(2)           # 柱间距（dp）
    default_height = NumericProperty(5)   # 默认柱高（dp）
    animation_duration = NumericProperty(0.5)  # 高度动画时长（秒）
    bars = ListProperty([])
    
     # 圆形模式专有属性
    circle_radius = NumericProperty(1)
    circle_color = ListProperty([0.2, 0.6, 1, 0.5])
    min_radius = NumericProperty(10)
    max_radius = NumericProperty(60)
    pulse_speed = NumericProperty(1.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(
            pos=self.update_canvas,
            size=self.update_canvas,
            frequency=self._update_params,
            time_window=self._update_params,
            spacing=self._update_params,
        )
        self._circle_phase = 0  # 新增相位控制
        self._pending_value = None
        self._last_window_end = 0
        self._last_generate_time = 0
        self._update_params()
        self.es=ExponentialSmoothing(0.6)
        
    def switch_animation_mode(self, mode):
        """切换动画模式"""
        if mode not in ["bars", "circle"]:
            raise ValueError("Invalid animation mode")
        
        if self.animation_mode != mode:
            if self.is_animating:
                self.stop_animation()
                self.animation_mode = mode
                self.start_animation()
            else:
                self.animation_mode = mode

    def _update_params(self, *args):
        """参数变化时更新计算属性"""
        # 计算柱体宽度（根据组件宽度和生成频率）
        total_bars = self.frequency * self.time_window
        if total_bars > 0 and self.width > 0:
            self.bar_width = max(1, (self.width / self.frequency) - self.spacing)
        
        # 计算动画速度（保证间距一致性）
        self.animation_speed = (self.bar_width + self.spacing) * self.frequency
        # 对齐最新窗口边界
        self._last_window_end = time.time()

    def start_animation(self):
        if not self.is_animating:
            self.is_animating = True
            if self.animation_mode == "bars":
                Clock.schedule_interval(self.update_bars, 1/60)
                print("动画启动 | 参数：", {
                "柱宽": self.bar_width,
                "速度": self.animation_speed,
                "间距": self.spacing
            })
            elif self.animation_mode == "circle":
                Clock.schedule_interval(self.update_circle, 1/60)
                print("动画启动 | 参数：", {
                "半径": self.circle_radius,
                "颜色": self.circle_color, 
                "最小半径": self.min_radius,
                "最大半径": self.max_radius,
                })
            
    def stop_animation(self):
        if self.is_animating:
            self.is_animating = False
            Clock.unschedule(self.update_bars)
            Clock.unschedule(self.update_circle)
            self.clear_canvas()
            print("动画停止")

    def clear_canvas(self):
        """统一清理画布"""
        self.canvas.clear()
        self.bars.clear()

    def add_bar(self, value):
        """外部输入接口"""
        #平滑曲线
        self._pending_value = self.es.smooth(value*1000*4)

    def update_bars(self, dt):
        # 1. 生成新柱体
        current_time = time.time()
        if current_time - self._last_generate_time >= 1/self.frequency:
            self._generate_bar()
            self._last_generate_time = current_time

        # 2. 更新现有柱体状态
        for bar in self.bars:
            # 更新水平位置
            bar['x'] -= self.animation_speed * dt
            
            # 更新高度动画
            elapsed = current_time - bar['start_time']
            if elapsed < self.animation_duration:
                # 应用缓动函数（out_quad）
                progress = min(elapsed / self.animation_duration, 1.0)
                bar['height'] = bar['target_height'] * (1 - (1 - progress)**2)
            else:
                bar['height'] = bar['target_height']
            
            # 移出边界检测
            if bar['x'] + self.bar_width < self.x:
                self.bars.remove(bar)
        
        # 3. 重绘画布
        self._redraw()

    def _generate_bar(self):
        """生成新柱体"""
        target_height = self._pending_value or self.default_height
        self._pending_value = None  # 重置待处理值
        
        self.bars.append({
            'x': self.x+self.width,                   # 初始X位置
            'start_time': time.time(),         # 动画开始时间
            'target_height': target_height,    # 目标高度
            'height': 0,                       # 当前高度
            'color': (0.2, 0.6, 1, 1)          # 颜色值
        })

    def _redraw(self):
        """重绘所有柱体"""
        self.canvas.clear()
        with self.canvas:
            for bar in self.bars:
                Color(*bar['color'])
                Rectangle(
                    pos=(bar['x'], self.center_y - bar['height']/2),
                    size=(self.bar_width, bar['height'])
                )

    # region 新增圆形波动画逻辑
    def update_circle(self, dt):
        """圆形波动画更新"""
        # 计算相位变化
        self._circle_phase += dt * self.pulse_speed
        if self._circle_phase > 1:
            self._circle_phase -= 1
        
        # 使用正弦波计算半径
        progress = (math.sin(self._circle_phase * 2 * math.pi) + 1) / 2
        current_radius = self.min_radius + (self.max_radius - self.min_radius) * progress
        #print(current_radius)
        # 更新并重绘
        self.circle_radius = current_radius
        self.draw_circle()

    def draw_circle(self):
        """绘制圆形"""
        self.canvas.clear()
        with self.canvas:
            Color(*self.circle_color)
            Ellipse(
                pos=(
                    self.center_x - self.circle_radius,
                    self.center_y - self.circle_radius
                ),
                size=(self.circle_radius * 2, self.circle_radius * 2)
            )
    # endregion

    def on_is_animating(self, instance, value):
        if not value:
            self.bars.clear()
            self.canvas.clear()

    def update_canvas(self, *args):
        self.canvas.clear()
        if self.animation_mode == "bars":
            with self.canvas:
                for bar in self.bars:
                    Color(*bar['color'])
                    Rectangle(
                        pos=(bar['x'], self.center_y - bar['height']/2),
                        size=(self.bar_width, bar['height'])
                    )
        elif self.animation_mode == "circle":
            with self.canvas:
                Color(*self.circle_color)
                Ellipse(
                    pos=(
                        self.center_x - self.circle_radius,
                        self.center_y - self.circle_radius
                    ),
                    size=(self.circle_radius * 2, self.circle_radius * 2)
                )


class VoiceDynamicLabel(MDFloatLayout):
    def __init__(self, **kwargs):
        super(VoiceDynamicLabel, self).__init__(**kwargs)
    

class ChatInput(MDBoxLayout):
    """
    输入栏
    """
    text = StringProperty("")
    is_focus = BooleanProperty(False)
    callback = ObjectProperty(lambda x:print(f"回调内容：{x.strip()}"))
    state = OptionProperty(
        'no_fouce', 
        options=[
            'on_fouce', 
            'no_fouce',
            'keyborad_inputting', 
            'voice_inputting',
            'outputting',
            "lading_voice_result"
        ]
    )
    recognition_mode = OptionProperty('full', options=['full', 'stream'])  # 识别模式
    speech_completion=BooleanProperty(False)  # 语音识别完成
    def __init__(self,**kwargs):
        super(ChatInput, self).__init__(**kwargs)
        # 绑定属性变化监听
        self.bind(
            is_focus=self._update_state,  # 焦点变化时更新状态
            text=self._update_state       # 文本变化时更新状态
        )
        Window.bind(
            on_key_down=self._on_key_down,
            on_key_up=self._on_key_up  # 新增按键释放绑定
        )
        # 新增语音输入相关属性
        self.voice_threshold = 0.5  # 长按时间阈值（秒）
        self.space_pressed_time = 0
        self.voice_scheduled = None
        self.voice_float_layout=VoiceDynamicLabel()
        self.max_voice_time=59  #最大录音时间
        self.add_widget(self.voice_float_layout)
        #升起动画
        self.animated_up=Animation(pos_hint={"center_x":.5,"center_y":5},duration=0.1)
        #落下动画
        self.animated_down=Animation(pos_hint={"center_x":.5,"center_y":-20},duration=0.3)
        self._voice_lock = threading.Lock()
        self._voice_timeout =None

        #录音类
        self.recorder = AudioRecorder(
            asr_instance=DummyASR(baidu_stt),
            mode='stream',
            volume_callback=self.voice_float_layout.ids.DynamicAnimateLabel.add_bar,
            error_callback=lambda e: print(f"错误发生: {e}")
            )

    def _update_state(self, *args):
        """核心状态更新逻辑"""
        if self.state == "outputting":
            return  # 输出状态时保持锁定
        if self.state=="lading_voice_result":
            return  # 获取回答时保持锁定
        
        if not self.is_focus:
            self.state = "no_fouce"
        else:
            if len(self.text.strip()) == 0:
                self.state = "on_fouce"
            else:
                self.state = "keyborad_inputting"
        

    def input(self, value):
        self.text = value
        print("输入栏中的内容：", value)

    def _on_key_down(self, window, key, scancode, codepoint, modifier):
        if not self.is_focus:
            return False    # 如果没有焦点，忽略按键事件

        if 'shift' in modifier and key == 13:  # 13 is the Enter key
            if self.is_focus:
                self.on_shift_enter()
                return True
            else:
                return False
        # 处理按键按下事件
        print(f"Key DOWN: {key} | State: {self.state}")
        if self.state == "outputting":
            return True
        if self.state == "lading_voice_result":
            return True
        # 空格键处理逻辑改进
        if key == 32:  # 空格键
            if self.voice_scheduled== None:
                # 如果当前状态是语音输入，直接返回
                self.space_pressed_time = time.time()
                self.voice_scheduled = Clock.schedule_once(
                    self._start_voice_input, 
                    self.voice_threshold
                )
                return True
            else:
                self.ids.input_field.readonly = True
        return False

    def _on_key_up(self, window, key, *args):
        if not self.is_focus:
            return False    # 如果没有焦点，忽略按键事件
        print(f"Key UP: {key} | State: {self.state}")
        if key == 32:  # 空格键
            # 确保定时器存在时才取消
            if self.voice_scheduled:
                Clock.unschedule(self.voice_scheduled)
                self.voice_scheduled = None
                print("取消语音定时器")
                self.ids.input_field.readonly = False
            # 状态保护检查
            if self.state == 'voice_inputting':
                print("正常结束语音输入")
                self.state="lading_voice_result"
                threading.Thread(target=self._stop_voice_input).start()
            elif time.time() - self.space_pressed_time < self.voice_threshold:
                print("插入空格")
                self._insert_space()
            return True
        return False

    def on_shift_enter(self):
        if self.ids.input_field.text.strip():
            print("Shift + Enter pressed")
            self.callback(self.ids.input_field.text)
            self.ids.input_field.text = ""
        
    def set_callback(self, func):
        self.callback = func 

    def on_enter(self):
        if not self.is_focus:
            return False    # 如果没有焦点，忽略按键事件
        # print("Enter pressed")
        # print(self.text)
        # if self.callback:
        #     self.callback(self.ids.input_field.text)
        #     self.ids.input_field.text = ""
        return True

    # 语音输入相关方法
    def _start_voice_input(self, dt):
        self.ids.input_field.do_backspace() #删掉一个空格
        self.state = "voice_inputting"
        #self.ids.input_field.disabled = True
        print("开始语音输入线程")
        self.recorder.start_recording()
        #浮窗升起动画
        self.voice_float_layout.ids.DynamicAnimateLabel.switch_animation_mode("bars")
        self.animated_up.start(self.voice_float_layout.ids.VoiceDynamicLabel)
        self.voice_float_layout.ids.DynamicAnimateLabel.start_animation()
        # 启动超时定时器
        self._voice_timeout = Clock.create_trigger(self._voice_timeout_handler, self.max_voice_time)
        #self.recorder.start_recording()

    def _stop_voice_input(self):
        """线程安全停止语音输入"""
        with self._voice_lock:
            try:
                print("停止语音输入线程")
                Clock.schedule_once(lambda dt:self.voice_float_layout.ids.DynamicAnimateLabel.switch_animation_mode("circle"))
                self.result = self.recorder.stop_recording(save_path="recording.wav")
                print(f"识别结果: {self.result}")
            except Exception as e:
                print(f"停止录音时发生错误: {str(e)}")
                Clock.schedule_once(lambda dt: self._show_error("录音终止异常"))
                self._force_reset_voice_state()
            finally:
                if self._voice_timeout is not None:
                    print("取消超时定时器")
                    self._voice_timeout.cancel()
                    self._voice_timeout = None
                Clock.schedule_once(lambda dt:self._stop_voice_ui())

    def _stop_voice_ui(self):
        try:
            if self.result != None:
                #ai修复语音识别的文本
                if self.speech_completion:
                    response=chuck_ai.chat_sync(self.result,stream=True)
                    temp_buffer=''
                    for result in response:
                        delta_content = getattr(result.choices[0].delta, 'content', '') or ''
                        temp_buffer += delta_content
                    print(f"初始文本：{self.result}--修复后文本：{temp_buffer}")
                    self._insert_text(temp_buffer)
                else:
                    self._insert_text(self.result)
            else:
                self._show_error("未能识别语音内容")
        except Exception as e:
            print(f"处理语音返回的结果时发生错误: {str(e)}")
            self._show_error("处理语音返回的结果时发生错误")
        finally:
            # 确保状态重置
            self.animated_down.start(self.voice_float_layout.ids.VoiceDynamicLabel)
            self.voice_float_layout.ids.DynamicAnimateLabel.stop_animation()
            self.state = "on_fouce"
            if self._voice_timeout is not None:
                self._voice_timeout.cancel()
                self._voice_timeout = None
            self.ids.input_field.readonly = False

    def _voice_timeout_handler(self, dt):
        """语音处理超时保护"""
        if self.state == 'lading_voice_result':
            self._show_error("语音识别超时")
            self._force_reset_voice_state()

    def _force_reset_voice_state(self):
        """强制重置语音相关状态"""
        with self._voice_lock:
            self.state = "on_fouce"
            self.animated_down.start(self.voice_float_layout.ids.VoiceDynamicLabel)
            self.ids.input_field.readonly = False
            self.recorder.emergency_stop()  # 新增强制终止录音

    def _insert_text(self, text):
        self.ids.input_field.text += text
        self.text = self.ids.input_field.text

    def _insert_space(self):
        self.ids.input_field.insert_text(' ')
        self.text = self.ids.input_field.text

    def _show_error(self, error):
        ErrorPopup(text=error).show(self.pos,self.size)
        #self.ids.input_field.text = f"[错误] {error}"

    # 输出状态控制
    def set_outputting(self):
        """进入等待回答状态"""
        self.state = "outputting"
        self.ids.input_field.disabled = True
        self.ids.trailing_icon.icon = "stop-circle"  # 显示可中断图标

    def resume_input(self):
        """恢复输入状态"""
        self.ids.input_field.disabled = False
        self._update_state()  # 根据当前状态自动更新

    def on_state(self, instance, value):
        """状态变化时更新UI"""
        icon_mapping = {
            'on_fouce': 'send-circle-outline',
            'no_fouce': 'send-circle',
            'keyborad_inputting': 'send-variant',
            'voice_inputting': 'microphone',
            'outputting': 'stop-circle',
            'lading_voice_result': 'microphone-off',
        }
        self.ids.trailing_icon.icon = icon_mapping.get(value, 'send-circle')

KV_ex="""
MDScreen:
    md_bg_color: "white"
    ChatInput:
"""
class ExampleApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Olive"
        return Builder.load_string(KV_ex)

if __name__ == "__main__":
    ExampleApp().run()            
    