import time

class GraphicItem:
    """
    单个图形项，包含图形指令和动画
    开启start后,将自动动过回调进行状态维护
    直接调用其他两个动画阶段,也会再通过回调进行状态维护
    idle:准备好了数据资源和画布资源,已经获取了图形指令和动画数据,但是画布上看不到
    start:将图形指令添加到画布上,并且数据动画开始变化
    looping:进入循环动画中,可以被直接结束
    ending:进入结束动画状态,此阶段仍旧是动画
        之后会根据是否开启自动销毁进入idle或者removed状态,
    removed会删除图形指令引用,并且会清除画布资源,而idle则会将状态恢复
    """
    def __init__(self,
                 graphic, 
                 start_anim=None, 
                 loop_anim=None, 
                 end_anim=None,
                 auto_remove=False,
                 unified_recycling=False
                 ):
        self.graphic = graphic
        self.start_anim = start_anim
        self.loop_anim = loop_anim
        self.end_anim = end_anim
        self.created_time = time.time()
        self.unified_recycling = unified_recycling
        self.state = "idle"  # idle, starting, looping, ending, removed
        self.auto_remove = auto_remove  # 动画完成后自动移除
        
    def __str__(self):
        return str([
        f"GraphicItem({self.graphic.__str__()}",
        f"state={self.state})",
        f"start_anim={self.start_anim.__str__() if self.start_anim else None}",
        f"loop_anim={self.loop_anim.__str__() if self.loop_anim else None}",
        f"end_anim={self.end_anim.__str__() if self.end_anim else None}",
        f"created_time={self.created_time}",
        f"auto_remove={self.auto_remove}"
        ])
    
    def start(self):
        """启动开启动画"""
        # print(f"启动前状态{self.state}")
        if self.state != "idle":
            return False
        # print('start')
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
        # print('loopping')
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
        # print("ending")
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

    def reset(self):
        """重置图形项"""
        self.cancel_animations()
        self.state = "idle"
        # print('reset')
        if self.graphic and hasattr(self.graphic, 'reset'):
            self.graphic.reset()
            
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
            self.loop_anim.cancel(self.graphic)   #主动停止循环需要触发回调
        if self.end_anim:
            self.end_anim.cancel(self.graphic)

    def update_layout(self,pos,size):
        """更新图形项布局"""
        if hasattr(self.graphic,'update_layout'):
            self.graphic.update_layout(pos,size)
        # 还需要更新动画的几个属性,否则不会改变的