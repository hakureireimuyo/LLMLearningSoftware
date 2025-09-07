from kivy.properties import (NumericProperty, ObjectProperty, BooleanProperty, ColorProperty, ListProperty, DictProperty, OptionProperty, StringProperty)
from kivy.graphics import (Color, Rectangle, Line, Ellipse, Quad, Triangle, Bezier, Mesh, RoundedRectangle, InstructionGroup)
from kivymd.uix.behaviors import DeclarativeBehavior, BackgroundColorBehavior
from kivy.uix.widget import Widget
from kivymd.theming import ThemableBehavior
from collections import deque
from kivy.clock import Clock
from .graphicitem import GraphicItem
from .graphicproxy import GraphicProxy
from .clockanimate import ClockAnimation

class AnimateItemBase(DeclarativeBehavior, Widget, ThemableBehavior, BackgroundColorBehavior):
    """整合版动画项基类 - 直接管理图形项"""
    is_animating = BooleanProperty(False)  # 动画是否正在运行
    max_items = NumericProperty(200)       # 最大图形项数量
    _graphic_items = ObjectProperty(None, allownone=True)  # 存储图形项
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._graphic_items = deque()
        self.bind(
            size=self._on_layout_change,
            pos=self._on_layout_change,
            max_items=self._update_max_items
        )
        self.is_first=True
        
    def text(self):
        with self.canvas:
            self.col=Color(0.5, 0.5, 0.4, 1)  # 红色
            self.ret=Rectangle(pos=self.pos, size=self.size)
        # print(self.pos,self.size)

    def _update_max_items(self, instance, value):
        """更新最大项数"""
        self._check_item_limit()
    
    def start(self):
        """开始动画"""
        if self.is_animating:
            return False
            
        if self.is_first:
            self.create_initial_graphics()
            self.is_first = False
            
        self.is_animating = True
        
        # 使用Clock统一更新所有动画项
        self._anim_clock = Clock.schedule_interval(self._update_animations, 1/60.)
        return True
    
    def _update_animations(self, dt):
        """统一更新所有动画项"""
        for item in self._graphic_items:
            if item.state == "starting" and item.start_anim and isinstance(item.start_anim, ClockAnimation):
                item.start_anim._update(dt)
            elif item.state == "looping" and item.loop_anim and isinstance(item.loop_anim, ClockAnimation):
                item.loop_anim._update(dt)
            elif item.state == "ending" and item.end_anim and isinstance(item.end_anim, ClockAnimation):
                item.end_anim._update(dt)
    
    def end(self):
        """结束动画"""
        if not self.is_animating:
            return False
            
        self.is_animating = False
        
        # 停止统一更新时钟
        if hasattr(self, '_anim_clock'):
            Clock.unschedule(self._anim_clock)
            del self._anim_clock
            
        # 结束所有图形项动画
        for item in self._graphic_items:
            if item.state not in ["ending", "idle", "removed"]:
                item.end()
        return True
    
    def stop(self):
        """完全停止并清除所有资源"""
        # 结束所有动画
        for item in self._graphic_items:
            item.end()
        
        # 清除所有图形项
        self._remove_all_items()
        self.is_animating = False
        return True
    
    def add_graphic(self, graphic, start_anim=None,loop_anim=None,end_anim=None, auto_remove=False):
        """
        添加图形项
        :param graphic: 图形指令或代理对象
        :param start_anim: 开启动画
        :param loop_anim: 循环动画
        :param end_anim: 结束动画
        :param auto_remove: 动画完成后是否自动移除
        :return: 图形项对象
        """
        # 检查项数限制
        self._check_item_limit()
        
        # 创建图形项
        item = GraphicItem(
            graphic=graphic,
            start_anim=start_anim,
            loop_anim=loop_anim,
            end_anim=end_anim,
            auto_remove=auto_remove,
            unified_recycling=self.unified_recycling   # 传递清除统一资源回收回调,结束动画完成后自己触发
        )
        # 添加到队列
        self._graphic_items.append(item)
        
        # 如果动画正在运行，立即启动
        if self.is_animating:
            if item.graphic.color:
                self.canvas.add(item.graphic.color)
            if item.graphic.shape:
                self.canvas.add(item.graphic.shape)
            item.start()
        
        return item
    
    def create_color_shape_pair(self, rgba, shape_type, **kwargs):
        """
        创建颜色和形状指令对
        :return: (color_instruction, shape_instruction) 元组
        """
        color = Color(rgba=rgba)
        shape = shape_type(**kwargs)
        
        gp=GraphicProxy(color, shape)
        gp.uid=shape.uid
        return gp
        
    
    def _on_layout_change(self, instance, value):
        """布局变化时更新所有图形项"""
        # if self.is_animating:
        #     for item in self._graphic_items:
        #         item.update_layout(self.size, self.pos)

    def _update_color(self, value):
        """更新颜色"""
        for item in self._graphic_items:
            if item.graphic.color:
                item.graphic.color.rgba = value
                
    def _check_item_limit(self):
        """检查并移除超限的图形项"""
        while len(self._graphic_items) > self.max_items:
            # 优先移除空闲或已完成项
            for item in list(self._graphic_items):
                if item.state in ["idle", "completed"]:
                    self._remove_item(item)
                    break
            else:
                # 如果没有合适的项，移除最老的项
                oldest = self._graphic_items.popleft()
                self._remove_item(oldest)
    
    def _remove_completed_items(self):
        """移除已完成的自动移除项"""
        items_to_remove = [item for item in self._graphic_items 
                          if item.state == "idle" and item.auto_remove]
        for item in items_to_remove:
            self._remove_item(item)

    
    def _remove_all_items(self):
        """移除所有图形项"""
        for item in list(self._graphic_items):
            self._remove_item(item)

    def unified_recycling(self,graphic:GraphicItem=None):
        """
        统一回收图形项
        自动移除的图形项会被移除
        未开始的图形项会被清除
        正在运行的图形项会被停止
        """
        if graphic.auto_remove:
            self._remove_item(graphic)
        else:
            self._clear_canvas(graphic)
            graphic.reset()

    def _clear_canvas(self,graphic:GraphicItem=None):
        """ 以回调的方式清除画布上的图形指令 """
        if graphic and isinstance(graphic,GraphicItem):
            if graphic.graphic.color:
                self.canvas.remove(graphic.graphic.color)
            if graphic.graphic.shape:
                self.canvas.remove(graphic.graphic.shape)
    
    def _remove_item(self,graphic:GraphicItem=None):
        """
        移除单个图形项
        从数据和画布中移除
        """
        try:
            if graphic and isinstance(graphic,GraphicItem):
                self._graphic_items.remove(graphic)
                if graphic.graphic.color:
                    self.canvas.remove(graphic.graphic.color)
                if graphic.graphic.shape:
                    self.canvas.remove(graphic.graphic.shape)
        except Exception as e:
                print(f"移除图形项时出错: {e}")

    # 以下方法需要子类实现
    def create_initial_graphics(self):
        """创建初始图形指令,不添加进入画布 - 需要子类实现"""
        pass
    
    def add_dynamic_data(self, data):
        """更新动态数据,非动画实现,而是外部输入数据,可以将输入值作为需要动画属性的末端 - 需要子类实现"""
        pass
