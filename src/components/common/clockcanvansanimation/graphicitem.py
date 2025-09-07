class GraphicItem:
    """支持FBO和实例池的图形项"""
    
    def __init__(self, container, graphic=None, 
                 start_anim=None, loop_anim=None, end_anim=None,
                 auto_remove=False):
        self.container = container
        self.graphic = graphic
        self.start_anim = start_anim
        self.loop_anim = loop_anim
        self.end_anim = end_anim
        self.state = "idle"
        self.auto_remove = auto_remove
        self._clock_time = 0
    
    def __str__(self):
        return str([
        f"GraphicItem({self.graphic.__str__()}",
        f"state={self.state})",
        f"start_anim={self.start_anim.__str__() if self.start_anim else None}",
        f"loop_anim={self.loop_anim.__str__() if self.loop_anim else None}",
        f"end_anim={self.end_anim.__str__() if self.end_anim else None}",
        f"auto_remove={self.auto_remove}"
        ])
    
    def update_animation(self, dt):
        """更新动画状态"""
        self._clock_time += dt
        
        if self.state == "starting" and self.start_anim:
            self._update_anim(self.start_anim, dt)
        elif self.state == "looping" and self.loop_anim:
            self._update_anim(self.loop_anim, dt)
        elif self.state == "ending" and self.end_anim:
            self._update_anim(self.end_anim, dt)
    
    def _update_anim(self, anim, dt):
        """更新单个动画"""
        progress = min(self._clock_time / anim.duration, 1.0)
        
        if progress >= 1.0:
            if anim == self.start_anim:
                self._on_start_complete()
            elif anim == self.loop_anim and anim.repeat:
                self._clock_time = 0
            elif anim == self.end_anim:
                self._on_end_complete()
        
        # 应用动画效果
        t = self._get_transition_value(progress, anim.transition)
        
        for prop, target in anim._properties.items():
            start = getattr(self.graphic, prop)
            if isinstance(start, (tuple, list)):
                current = tuple(s + (t - s) * t for s, t in zip(start, target))
            else:
                current = start + (target - start) * t
            setattr(self.graphic, prop, current)
    
    def _get_transition_value(self, progress, transition):
        """获取过渡函数值"""
        if not transition or transition[0] == 'linear':
            return progress
        
        # 简化的过渡函数实现
        if transition[0] == 'in_quad':
            return progress * progress
        elif transition[0] == 'out_quad':
            return 1 - (1 - progress) * (1 - progress)
        
        return progress
    
    def reset(self):
        """重置图形项"""
        self.state = "idle"
        self._clock_time = 0
        if self.graphic:
            self.graphic.reset()
    
    def start(self):
        """启动开启动画"""
        if self.state != "idle":
            return False
        self.state = "starting"
        if self.start_anim:
            self.start_anim.start(self.graphic)
            self.start_anim.bind(on_complete=self._on_start_complete)
        else:
            self._on_start_complete()
        return True
        
    def _on_start_complete(self, *args):
        """开启动画完成,开启循环动画"""
        self.state = "looping"
        # print('start_complete')
        # print('loop')
        if self.loop_anim:
            self.loop_anim.start(self.graphic)
            self.loop_anim.bind(on_complete=self._on_loop_complete)
        else:
            # 如果没有循环动画，直接进入结束状态
            self._on_loop_complete()

    def loop(self,*args):
        self.state = "looping"
        # print('loop')
        self.cancel_animations()
        if self.loop_anim:
            self.loop_anim.start(self.graphic)
            self.loop_anim.bind(on_complete=self._on_loop_complete)
        else:
            # 如果没有循环动画，直接进入结束状态
            self._on_loop_complete()

    def _on_loop_complete(self,*args):
        """循环动画完成,启动结束动画"""
        self.state = "ending"
        # print('loop_complete')
        # print("end")
        if self.end_anim:
            self.end_anim.start(self.graphic)
            self.end_anim.bind(on_complete=self._on_end_complete)
        else:
            self._on_end_complete()
        return True
    
    def end(self,*args):
        """启动循环动画"""
        self.state = "ending"
        # print('end')
        # 主动关闭循环动画
        self.cancel_animations()
        if self.end_anim:
            self.end_anim.start(self.graphic)
            self.end_anim.bind(on_complete=self._on_end_complete)
            return self.end_anim.duration
        else:
            self._on_end_complete()
            return 0
    
    def _on_end_complete(self, *args):
        """结束动画完成回调"""
        # print('end_complete')
        # 从画布中移除图形指令
        # 根据auto_remove决定是否移除数据
        if self.unified_recycling:
            # 统一回收
            self.unified_recycling(self)
        return True
            
    def remove(self):
        """
        移除图形项
        调用后不仅在画布上清除,还会将自己的数据也清理掉
        还是将这部分挪动到GraphicGroup中比较好么
        """
        if hasattr(self.graphic, 'remove'):
            self.graphic.remove()
        self.state = "removed"
    
    def cancel_animations(self):
        """
        暂时取消所有动画,不触发回调,不会进入下一阶段
        通过回调触发画布清除,清除画布就会将引用从动画中移除
        但是数据保留,开始后又会重新添加
        """
        # print(f"取消前状态{self.state}")
        if self.start_anim:
            self.start_anim.cancel(self.graphic)
        if self.loop_anim:
            self.loop_anim.stop(self.graphic)   #主动停止循环需要触发回调
        if self.end_anim:
            self.end_anim.cancel(self.graphic)

    def update_layout(self,pos,size):
        """更新图形项布局"""
        if hasattr(self.graphic,'update_layout'):
            self.graphic.update_layout(pos,size)
        # 还需要更新动画的几个属性,否则不会改变的