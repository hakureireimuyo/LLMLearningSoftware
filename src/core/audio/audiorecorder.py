import pyaudio
import numpy as np
import threading
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