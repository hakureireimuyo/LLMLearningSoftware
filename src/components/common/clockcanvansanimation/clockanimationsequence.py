class ClockAnimationSequence:
    """动画序列，支持多个动画按顺序播放"""
    
    def __init__(self):
        self._animations = []
        self._current_index = 0
        self._current_anim = None
        self._on_complete = None
    
    def add(self, anim):
        """添加动画"""
        self._animations.append(anim)
        return self
    
    def start(self, proxy):
        """启动序列"""
        if not self._animations:
            return self
            
        self._current_index = 0
        self._current_anim = self._animations[0]
        self._current_anim.bind(on_complete=self._on_anim_complete)
        self._current_anim.start(proxy)
        return self
    
    def _on_anim_complete(self, anim):
        """单个动画完成回调"""
        self._current_index += 1
        
        if self._current_index < len(self._animations):
            self._current_anim = self._animations[self._current_index]
            self._current_anim.bind(on_complete=self._on_anim_complete)
            self._current_anim.start(anim._proxy)
        else:
            if self._on_complete:
                self._on_complete(self)
    
    def stop(self):
        """停止序列"""
        if self._current_anim:
            self._current_anim.stop()
    
    def bind(self, on_complete=None):
        """绑定完成回调"""
        if on_complete:
            self._on_complete = on_complete