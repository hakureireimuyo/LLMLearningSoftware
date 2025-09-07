from kivy.properties import BooleanProperty, ObjectProperty
from kivy.animation import Animation
from kivy.clock import Clock
from collections import defaultdict

class GraphicGroup:
    """管理多个图形指令及其对应的动画对象"""
    def __init__(self):
        self.items = []  # 存储图形指令和相关动画
        self.current_animations = defaultdict(list)  # 当前正在运行的动画
        self.animating_number = 0  # 当前正在运行的动画数量#
    def add_item(self, graphic, start_anim=None, loop_anim=None, end_anim=None):
        """添加一个图形指令及其关联的动画"""
        self.items.append({
            'graphic': graphic,
            'start_anim': start_anim,
            'loop_anim': loop_anim,
            'end_anim': end_anim
        })
    
    def remove_all(self):
        """移除所有图形指令"""
        self.cancel_all_animations()  # 先取消所有动画
        self.items.clear()
    
    def start_animations(self, anim_type, callback=None):
        """启动指定类型的动画"""
        self.cancel_all_animations()
        self.animating_number=0
        # 统计需要启动的动画数量
        anim_count = 0
        for item in self.items:
            anim = item.get(anim_type)
            if anim:
                anim_count += 1
        
        if anim_count == 0:
            if callback:
                callback()
            return True
        
        # 启动所有动画并设置统计回调
        for item in self.items:
            anim = item.get(anim_type)
            if anim:
                # 为动画目标设置图形指令
                anim.start(item['graphic'])
                anim.bind(on_complete=lambda *args, anim_type=anim_type, callback=callback: self._on_animation_complete(anim_type, callback))
                self.current_animations[anim_type].append((anim,item['graphic']))  
        return True
    
    def _on_animation_complete(self, anim_type, callback):
        """当动画完成时调用，统计完成情况"""
        pass
    
    def cancel_all_animations(self):
        """取消所有正在进行的动画"""
        for anim_type, anim_list in list(self.current_animations.items()):
            for anim_tuple in anim_list:
                anim, target = anim_tuple
                # 使用目标对象取消动画
                anim.cancel(target)
        self.current_animations.clear()

from kivymd.uix.behaviors import DeclarativeBehavior, BackgroundColorBehavior
from kivy.uix.widget import Widget
from kivymd.theming import ThemableBehavior

class AnimateItemBase(DeclarativeBehavior, Widget, ThemableBehavior, BackgroundColorBehavior):
    """重制的动画项基类 - 使用GraphicGroup管理多个图形指令"""
    is_animating = BooleanProperty(False)  # 动画是否正在运行
    graphic_group = ObjectProperty(None, allownone=True)  # 图形组对象
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self.on_size, pos=self.on_pos)
        self.graphic_group = GraphicGroup()
        self.initialize()
    
    def initialize(self):
        """初始化动画状态"""
        self.is_animating = False
    
    def start(self):
        """开始开启动画"""
        if self.is_animating:
            return False
            
        self.is_animating = True
        
        # 创建图形指令
        self.create_graphics()
        
        # 启动开启动画
        self.graphic_group.start_animations(
            'start_anim', 
            self._on_start_animations_complete
        )
            
        return True
    
    def end(self):
        """开始结束动画"""
        if not self.is_animating:
            return False
            
        # 取消所有正在进行的动画
        self.graphic_group.cancel_all_animations()
        
        # 启动结束动画
        self.graphic_group.start_animations(
            'end_anim',
            self._on_end_animations_complete
        )

        self.is_animating = False
        return True

    def stop(self):
        """停止所有动画并清除画布"""
        self.graphic_group.cancel_all_animations()
        self.clear_canvas()
        self.graphic_group.remove_all()
        self.is_animating = False
        return True

    def _on_start_animations_complete(self):
        """开启动画完成后的回调"""
        # 开始循环动画
        self.graphic_group.start_animations('loop_anim')
    
    def _on_end_animations_complete(self):
        """结束动画完成后的回调"""
        self.stop()

    def on_size(self, instance, size):
        """尺寸变化时更新动画"""
        if self.is_animating:
            self.update_layout()

    def on_pos(self, instance, pos):
        """位置变化时更新动画"""
        if self.is_animating:
            self.update_layout()
    
    # 以下方法需要子类实现
    def create_graphics(self):
        """创建图形指令并添加到graphic_group - 需要子类实现"""
        pass
    
    def update_layout(self):
        """更新布局 - 需要子类实现"""
        pass
    
    def clear_canvas(self):
        """清除画布内容 - 需要子类实现"""
        self.canvas.clear()

    def add_item(self, item):
        """添加新图形指令（可选功能）"""
        pass
    
    def __del__(self):
        """析构函数 - 确保资源释放"""
        self.stop()