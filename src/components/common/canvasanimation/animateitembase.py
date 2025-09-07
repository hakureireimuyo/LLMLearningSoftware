from kivy.properties import BooleanProperty, ObjectProperty, NumericProperty
from collections import deque
from kivy.graphics import Color,Rotate,Rectangle,PushMatrix,PopMatrix,InstructionGroup
from kivymd.uix.behaviors import DeclarativeBehavior, BackgroundColorBehavior
from kivy.uix.widget import Widget
from kivymd.theming import ThemableBehavior
from .graphicitem import GraphicItem
from .graphicproxy import GraphicProxy

class AnimateItemBase(DeclarativeBehavior, Widget, ThemableBehavior, BackgroundColorBehavior):
    """整合版动画项基类 - 直接管理图形项"""
    is_animating = BooleanProperty(False)  # 动画是否正在运行
    _graphic_items = ObjectProperty(None, allownone=True)  # 存储图形项
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._graphic_items = deque()
        self._graphic_group = InstructionGroup()
        self.bind(
            size=self._on_layout_change,
            pos=self._on_layout_change,
        )
        self.is_first = True
        self.animate_num = 0
        self.playing_num = 0
        self.push_matrix = 0
        self.pop_matrix = 0

        #矩阵影响锁定在内部
        self.canvas.add(PushMatrix())
        self.canvas.add(self._graphic_group)
        self.canvas.add(PopMatrix())
    
    def start(self):
        """开始动画"""
        if self.is_first:
            self.create_initial_graphics()
            self.is_first=False
        if self.is_animating:
            return False
        
        self.is_animating = True
        self.playing_num=0
        self._add_canvas(self._graphic_items)
        #print(f"播放数量{self.playing_num}")
        return True
    
    def end(self):
        """直接播放结束动画"""
        if not self.is_animating:
            return False
        # 结束所有图形项动画
        for item in self._graphic_items:
            if item.state not in ["ending", "idle", "removed"]:
                item.end()
        return True
    
    def stop(self):
        """强制停止所有动画,无论处于什么状态,都会直接结束"""
        if not self.is_animating:
            return False
        self.is_animating = False
        self._graphic_group.clear() 
        return True


    def _add_canvas(self,graphic_item_list):
        """
        为了防止旋转矩阵的全局影响,使用此方法将图形添加进组中
        """
        for item in graphic_item_list:
            if item.graphic.color:
                self._graphic_group.add(item.graphic.color)
            if item.graphic.rotate:
                self._graphic_group.add(item.graphic.rotate)
            if item.graphic.shape:
                self._graphic_group.add(item.graphic.shape)
            item.start()
            self.playing_num+=1

        return True
    
    def add_graphic(self, graphic, start_anim=None,loop_anim=None,end_anim=None, auto_remove=False):
        """
        添加图形项,支持播放中添加新的图形项
        :param graphic: 图形指令或代理对象
        :param start_anim: 开启动画
        :param loop_anim: 循环动画
        :param end_anim: 结束动画
        :param auto_remove: 动画完成后是否自动移除
        :return: 图形项对象
        """
        
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
                self._graphic_group.add(item.graphic.color)
            if item.graphic.rotate:
                self._graphic_group.add(item.graphic.rotate)
            if item.graphic.shape:
                self._graphic_group.add(item.graphic.shape)
            item.start()
            self.playing_num+=1

        # print(len(self._graphic_items))
        return True
    
    def create_graphic(self, graphic, start_anim=None,loop_anim=None,end_anim=None, auto_remove=False):
        """
        添加图形项,支持播放中添加新的图形项
        :param graphic: 图形指令或代理对象
        """
        # 创建图形项
        item = GraphicItem(
            graphic=graphic,
            start_anim=start_anim,
            loop_anim=loop_anim,
            end_anim=end_anim,
            auto_remove=auto_remove,
            unified_recycling=self.unified_recycling   # 传递清除统一资源回收回调,结束动画完成后自己触发
        )
        return item
    
    def add_graphic_list(self, graphic_item_list):
        """
        添加图形项列表,支持播放中添加新的图形项
        :param graphic_list: 图形指令或代理对象列表
        """
        self._graphic_items.extend(graphic_item_list)
        # 如果动画正在运行，立即启动
        if self.is_animating:
            for item in graphic_item_list:
                if item.graphic.color:
                    self._graphic_group.add(item.graphic.color)
                if item.graphic.rotate:
                    self._graphic_group.add(item.graphic.rotate)
                if item.graphic.shape:
                    self._graphic_group.add(item.graphic.shape)
                self.playing_num+=1

        return True
    
    def create_color_shape_pair(self,
                                rgba=(1,1,1,1), 
                                shape_type=Rectangle,
                                pos=(100,100),
                                size=(100,100),
                                angle=0,
                                origin=(100,100),
                                keep_center=True):
        """
        创建颜色和形状指令对
        :return: 代理对象
        """
        color = Color(rgba=rgba)
        shape = shape_type(pos=pos,size=size)
        rotate = Rotate(angle=angle,origin=origin)
        
        gp=GraphicProxy(color=color, shape=shape,rotate=rotate)
        gp.uid=shape.uid
        gp._keep_rotate_origin_in_center=keep_center
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
        self.playing_num-=1
        # print(f"剩余数量{self.playing_num}")
        if self.playing_num==0:
            self.is_animating=False
            

    def _clear_canvas(self,graphic:GraphicItem=None):
        """ 以回调的方式清除画布上的图形指令 """
        if graphic and isinstance(graphic,GraphicItem):
            if graphic.graphic.color:
                self._graphic_group.remove(graphic.graphic.color)
            if graphic.graphic.rotate:
                self._graphic_group.remove(graphic.graphic.rotate)
            if graphic.graphic.shape:
                self._graphic_group.remove(graphic.graphic.shape)
            
    
    def _remove_item(self,graphic:GraphicItem=None):
        """
        移除单个图形项
        从数据和画布中移除
        """
        try:
            if graphic and isinstance(graphic,GraphicItem):
                self._graphic_items.remove(graphic)
                if graphic.graphic.color:
                    self._graphic_group.remove(graphic.graphic.color)
                if graphic.graphic.rotate:
                    self._graphic_group.remove(graphic.graphic.rotate)
                if graphic.graphic.shape:
                    self._graphic_group.remove(graphic.graphic.shape)
        except Exception as e:
                print(f"移除图形项时出错: {e}")

    # 以下方法需要子类实现
    def create_initial_graphics(self):
        """
        创建初始图形指令,不添加进入画布 - 需要子类实现,
        在子类中定义需要使用到的图形项,
        然后该方法会被自动调用
        """
        pass
    
    def add_dynamic_data(self, data):
        """
        更新动态数据,非动画实现,而是依赖外部输入数据,
        可以将输入值作为需要动画属性的末端 - 需要子类实现
        需要使用内部的方法才能在运行的时候添加新的动画,
        该方法可以作为事件驱动类型的动画实现,
        比如需要根据输入的音频数据实时更新动画
        """
        pass
