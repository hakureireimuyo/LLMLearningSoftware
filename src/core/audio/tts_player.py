import pyaudio

class PCMPlayer:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.is_playing = False  # 播放状态标志
        self.current_audio = None  # 当前音频数据缓存

    def play_pcm(self, pcm_data: bytes, sample_rate: int = 16000):
        """播放PCM音频（支持中断当前播放）"""
        # 如果正在播放，先停止当前播放
        if self.is_playing:
            return None

        # 缓存当前音频参数
        self.current_audio = {
            "data": pcm_data,
            "sample_rate": sample_rate
        }

        try:
            self._start_stream(sample_rate)
            self.is_playing = True
            
            # 分块播放（带中断检查）
            chunk_size = 1024
            for i in range(0, len(pcm_data), chunk_size):
                if not self.is_playing:  # 检查播放状态
                    break
                self.stream.write(pcm_data[i:i+chunk_size])
                
        except Exception as e:
            print(f"播放失败: {str(e)}")
        finally:
            # 仅暂停流，不清除资源
            self._pause()

    def _start_stream(self, sample_rate: int):
        """初始化/重启音频流"""
        if self.stream:
            self.stream.close()
            
        self.stream = self.p.open(
            format=self.p.get_format_from_width(2),
            channels=1,
            rate=sample_rate,
            output=True
        )

    def _pause(self):
        """暂停播放（保持流打开）"""
        if self.stream and self.stream.is_active():
            self.stream.stop_stream()
        self.is_playing = False

    def resume(self):
        """继续播放（需有缓存音频）"""
        if self.current_audio and not self.is_playing:
            self.play_pcm(
                self.current_audio["data"],
                self.current_audio["sample_rate"]
            )

    def _cleanup(self):
        """完全清除资源"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        self.is_playing = False

    def stop(self):
        """停止并清除缓存"""
        self._pause()
        self.current_audio = None

    def terminate(self):
        """彻底释放所有资源"""
        self._cleanup()
        self.p.terminate()