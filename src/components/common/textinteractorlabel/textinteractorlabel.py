"""
实现了文本的交互功能，支持文本的复制、粘贴、翻译、删除等功能
不可直接编辑文本，支持高亮显示，标记文本等功能
支持鼠标悬浮显示翻译结果
支持鼠标左键单机翻译单词
支持鼠标左键双击翻译句子
支持动态字体大小修改
"""
from kivy.properties import ListProperty, ObjectProperty,BooleanProperty,NumericProperty,DictProperty,ColorProperty,StringProperty
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, SmoothRoundedRectangle
from kivymd.uix.label import MDLabel
from kivy.core.clipboard import Clipboard
from kivy.metrics import sp,dp
import random
from components.common.callback import CallbackManager

# 专属于该类的事件与方法映射关系类
# 增加单例模式，且可以动态修改事件映射关系
# 初始化可以传入事件映射关系字典，具有默认值
class EventMapping:
    _event_mappings = {}
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(EventMapping, cls).__new__(cls)
        return cls._instance
    # 初始化事件映射关系
    def __init__(self,event_mappings=None):
        if event_mappings!=None:
            self._event_mappings=event_mappings
        else:
            self._event_mappings = {
                'single_click': 'print_info',
                'select': 'translate',
                'double_click': 'translate',
                'hover': 'word_query',
                'long_touch': 'print',
            }
    # 新增方法：获取所有事件映射关系
    def get_all_mappings(self):
        return self._event_mappings.copy()
    
    def __getitem__(self, key):
        return self._event_mappings.get(key, None)
    
    def __setitem__(self, key, value):
        self._event_mappings[key] = value

    def __delitem__(self, key):
        if key in self._event_mappings:
            del self._event_mappings[key]

    def __contains__(self, key):
        return key in self._event_mappings
    
    def __iter__(self):
        return iter(self._event_mappings.items())
    
    def __len__(self):
        return len(self._event_mappings)
    
    def __repr__(self):
        return repr(self._event_mappings)
    
    def __str__(self):
        return str(self._event_mappings)
    
    def pop(self, key, default=None):
        """移除指定事件映射关系"""
        return self._event_mappings.pop(key, default)

from kivymd.uix.behaviors import (
    RectangularRippleBehavior,
    BackgroundColorBehavior,
    CommonElevationBehavior,
)
# 自动可变限制宽度成功，采用计算字符宽度与基于父容器的方法,管理with属性
class TextInteractorLabel(MDLabel):
    """
    该组件只能增加文本,不能修改和删除,否则会导致状态不正确
    实现了文本的交互功能,实现了组件的宽度智能管理
    有固定最大宽度和依靠父级容器固定比例两种模式
    """
    # 存储每个字符的位置信息 (x, y, w, h)
    char_positions = ListProperty([])
    # 存储原始文本用于索引映射
    plain_text = ObjectProperty('')
    texture_start_x = NumericProperty(0) # 纹理起始X坐标（关键新增）
    texture_start_y = NumericProperty(0) # 纹理起始Y坐标（关键新增）
    selecting = BooleanProperty(False)   # 是否正在选区
    highlight_rects = DictProperty({})   # 字典存储高亮区域 {index: Rectangle}
    # 开启后每次文本修改和组件的大小更新都会自动更新字符位置信息，建议不要开启。需要时手动调用
    auto_updata=BooleanProperty(True)  # 是否自动更新字符布局信息?弃用
    # 回调函数管理，类属性，所有实例共享
    _callback = CallbackManager()
    # 类属性存储事件与方法的动态映射关系
    _event_mappings=EventMapping()
    # 选取颜色
    select_color=ColorProperty()
    # 开启按照父级宽度按比例自动调整宽度
    adaptive_width_from_parent=BooleanProperty(True)
    # 根据父级宽度按比例自动调整宽度
    adaptive_width_ratio=NumericProperty(0.8)

    def __init__(self, **kwargs):
        #================如果在on方法中使用了某些变量,就要在初始化前定义,或者之后再进行绑定============
        super().__init__(**kwargs)
        #self.adaptive_width = True #开启这个会覆盖witdh和text_size属性
        self.size_hint_max_x=dp(600)
        self.size_hint_x=None
        self.adaptive_height = True
        self.font_style = "STSONG"
        self.halign = 'left'
        self.valign = 'middle'
        self.padding = dp(10), dp(10), dp(10), dp(10)
        self.radius = [10, 10, 10, 10]
        self.markup = True
        self.role = "medium"
        self.width=dp(100)
        self.text_size = (self.size_hint_max_x, None)  # 允许文本自动换行
        self._pending_release=None
        #print("初始化文本坐标数据")
        self.select_start = -1           # 选区起始索引
        self.select_end = -1             # 选区结束索引
        self.full_update_event=None       # 全量更新事件
        self.auto_update_width_event = None     # 输入文本后自动更新组件宽度事件
        self.text_has_changed=False         # 用于管理计算字符串布局等信息

        # 标记新增字符串的相关信息
        self._last_text = ""            # 上次更新文本
        self._last_max_width = 0           # 上次更新文本最大宽度
        self._last_line_width = 0           # 上次更新文本最大行宽度
        self._last_text_length = 0              # 上次更新文本长度
        # 用于存储根据父容器宽度变化的延迟更新事件
        self._last_parent_width = 0                 #上次更新父容器宽度
        self._pending_parent_update = None          # 延迟更新父容器宽度事件
        self._last_text_width = 0                   # 上次更新文本宽度
        # 鼠标事件
        self.mouse_in=False     
        Clock.schedule_once(self.update_all,0)
        # 绑定事件要在最后定义,避免访问未定义的变量
        self.bind(
            center = self.update_highlight_positions,
            #width = self.full_update_event_buffer,
            #text = self.full_update_event_buffer,
            parent = self._on_parent_change
        )
    
    def _on_parent_change(self, instance, value):
        """当父容器改变时绑定父容器的尺寸变化"""
        if self.parent:
            # 解绑之前的父容器（如果存在）
            if hasattr(self, '_parent_binding'):
                self.parent.unbind(width=self._schedule_width_update)
            
            # 绑定新父容器的宽度变化
            self._parent_binding = self.parent.bind(
                width=self._schedule_width_update
            )
            # 立即触发一次更新
            self._update_width_from_parent()
            
    def _calculate_max_text_width(self):
        """增量计算文本最大宽度（假设文本只会增长）"""
        if not hasattr(self, '_label') or self._label is None:
            return 0
        
        # 如果文本未变化，使用缓存值
        if self.text == self._last_text:
            return self._last_max_width + self.padding[0] + self.padding[2] + 30
        
        # 获取文本变化部分
        new_text = self.text
        old_text = self._last_text
        
        # 如果文本被重置（长度变短），重新计算
        if len(new_text) < len(old_text):
            return self._recalculate_full_width()
        
        # 增量计算新增部分的宽度
        start_index = len(old_text)
        max_width = self._last_max_width
        current_line_width = self._last_line_width
        
        # 处理新增文本
        for char in new_text[start_index:]:
            if char == "\n":
                # 换行时更新最大宽度
                max_width = max(max_width, current_line_width)
                current_line_width = 0
            else:
                # 累加字符宽度
                char_size = self._label.get_extents(char)
                current_line_width += char_size[0]
        
        # 更新缓存值
        self._last_text = new_text
        self._last_max_width = max(max_width, current_line_width)
        self._last_line_width = current_line_width
        self._last_text_length = len(new_text)
        # 增加30避免某些原因导致宽度不足
        return self._last_max_width + self.padding[0] + self.padding[2]+30
    
    
    def _schedule_width_update(self, instance, width):
        """调度宽度更新，使用防抖机制"""
        # 只有当父容器宽度实际变化时才更新（避免频繁计算）
        if abs(width - self._last_parent_width) < 5:  # 小于5像素的变化忽略
            return
        
        # 如果已经存在延迟更新事件，则直接返回
        if self._pending_parent_update:
            return
        
        # 设置新的延迟更新
        self._pending_parent_update = Clock.schedule_once(
            lambda dt: self._update_width_from_parent(), 
            0.05  # 100ms延迟，可根据需要调整
        )
    
    def _update_width_from_parent(self):
        """实际执行宽度更新"""
        # 仅当启用自适应宽度时才处理
        if not self.adaptive_width_from_parent:
            self._pending_parent_update=None
            return
        
        # 计算文本实际需要的最大宽度
        max_text_width = self._calculate_max_text_width()
        
        # 如果文本宽度未变化且父容器宽度变化不大，跳过更新
        if abs(self.parent.width - self._last_parent_width) < 30:  # 父容器变化小于30像素
            self._pending_parent_update=None
            return
        
        # 检验后才记录,避免误差累积
        self._last_parent_width = self.parent.width

        self._last_text_width = max_text_width
        
        # 计算父容器允许的最大宽度（按比例）
        max_allowed = self.parent.width * self.adaptive_width_ratio
        
        # 根据文本宽度和父容器允许宽度动态调整
        if max_text_width <= max_allowed:
            # 文本宽度小于最大允许宽度，使用文本实际宽度
            self.width = max(max_text_width, dp(30))  # 保持最小宽度
        else:
            # 文本宽度超过最大允许宽度，使用比例宽度
            self.width  = max_allowed
        
        # 标记需要更新字符布局,已经使用了延迟更新
        # 所以这里不需要使用delay_update
        self.fully_update_the_text_layout()
        # 清除延迟更新事件,所有事情做完后才接收新事件
        self._pending_parent_update = None

    def _recalculate_full_width(self):
        """完整重新计算文本宽度"""
        width = 0
        max_width = 0
        
        for char in self.text:
            if char == "\n":
                max_width = max(max_width, width)
                width = 0
            else:
                char_size = self._label.get_extents(char)
                width += char_size[0]
        
        # 最后一行也需要比较
        max_width = max(max_width, width)
        
        # 更新缓存
        self._last_text = self.text
        self._last_max_width = max_width
        self._last_line_width = width
        self._last_text_length = len(self.text)
        
        return max_width + self.padding[0] + self.padding[2]
          
    def on_text(self,instance,value):
        """限制文本宽度，超过宽度自动换行
        Args:
            instance (_type_): 实例
            value (_type_): 参数

        Returns:
            _type_: 无返回值
        """        
        # 如果不包含self._label则直接返回
        if not hasattr(self, '_label'):
            return
        if self._label is None:
            return
        self.text_has_changed=True
        # 如果已经有更新事件在等待，则不再重复设置
        if self.auto_update_width_event is not None:
            return  
        # 字符更新快会导致宽度不匹配,要么一起更新,要么设置缓冲区
        # 否则会导致文本框剧烈变形
        #self.auto_update_width_event=Clock.schedule_once(lambda dt:self.auto_update_width(),0.1)
        self.auto_update_width()

    def update_theme(self, instance, value):
        self.select_color = self.theme_cls.primaryColor
        self.md_bg_color = self.theme_cls.backgroundColor
        self.shadow_color = self.theme_cls.primaryColor

    def update_all(self, *args):
        """统一更新布局和高亮位置，只在初始化的时候使用"""
        self.on_text(None,None)
        self.full_update_event_buffer()
        self.update_highlight_positions(None,None)
        self.update_theme(None,None)
        
    def full_update_event_buffer(self,*args):
        """全量更新事件缓冲"""
        if self.full_update_event!=None:
            return  # 如果已经有更新事件在等待，则不再重复设置
        self.full_update_event=Clock.schedule_once(self.fully_update_the_text_layout,0.5)

    def fully_update_the_text_layout(self, *args):
        """全量更新文本布局信息"""
        # 当至少触发了一次on_text的时候,才会触发全量更新
        if not self.text_has_changed:
            return
        self.text_has_changed=False

        # 如果没有_label属性，直接返回
        if not hasattr(self, '_label') or not hasattr(self._label, '_cached_lines'):
            self.full_update_event = None
            return
        
        # 重置所有字符位置信息
        self.char_positions = []
        self.plain_text = ""
        
        # 遍历每个字符计算位置
        x, y = 0, 0
        for line in self._label._cached_lines:
            # 设置行起始位置
            x = line.x
            y = line.y
            
            # 处理行中的单词
            for word in line.words:
                # 处理单词中的字符
                for char in word.text:
                    # 记录字符位置和尺寸
                    char_size = self._label.get_extents(char)
                    self.char_positions.append((
                        x, 
                        self.texture.size[1] - y,
                        char_size[0],
                        char_size[1]
                    ))
                    
                    # 更新纯文本
                    self.plain_text += char
                    
                    # 更新位置
                    x += char_size[0]

        # 清除延迟更新事件
        self.full_update_event = None
        #self.show_highlight()

    def auto_update_width(self):
        """
        自动更新宽度
        如果开启了根据父级宽度按比例自动调整宽度，
        则会绑定父级的witdh,当父级宽度变化时组件的宽度会重新计算
        当文本量会动态扩宽组件,直到达到子组件的最大宽度,
        父级组件宽度更新会重新计算
        如果不开启,则使用固定的最大宽度
        此时文本较少的时候组件仅仅包裹文本,
        文本量多到一定程度后会子组件达到最大宽度
        不受父级组件影响
        """
        # 如果启用自适应宽度
        if self.adaptive_width_from_parent:
            # 如果父容器存在，调度宽度更新
            if self.parent:
                self.update_width_from_parent()
            else:
                self.fixed_max_width_update()
        else:
            self.fixed_max_width_update()
        self.auto_update_width_event = None

    # 固定最大宽度更新
    def fixed_max_width_update(self):
        """固定最大宽度更新"""
        # 未启用自适应宽度的原有逻辑
        if self.size_hint_max_x is None:
            return
        
        # 当前宽度达到最大值,不必再计算
        if self.width>=self.size_hint_max_x :
            return
        
        # 计算文本实际需要的最大宽度
        new_width = self._calculate_max_text_width()
        #print(self.text_size,new_width,self.size_hint_max_x,self.width)
        
        if self.width<self.size_hint_max_x:
            if new_width > self.size_hint_max_x:
                self.width = self.size_hint_max_x  # Set the width of the label    
            else:
                self.width = max(new_width,dp(30))          
        else:
            self.width=self.size_hint_max_x

    # 按父容器相对宽度更新宽度,文本更新时调用
    def update_width_from_parent(self):
        """按父容器相对宽度更新宽度"""
        # 计算父容器允许的最大宽度（按比例）
        max_allowed = self.parent.width * self.adaptive_width_ratio
        if self.width>=max_allowed:
            # 达到最大值,不必再统计
            return
        
        # 计算文本实际需要的最大宽度
        max_text_width = self._calculate_max_text_width()
        #print(self.text_size,max_text_width,self.size_hint_max_x,self.width)
        if max_text_width <= max_allowed:
            # 文本宽度小于最大允许宽度，使用文本实际宽度
            self.width = max(max_text_width, dp(30))  # 保持最小宽度
        else:
            # 文本宽度超过最大允许宽度，使用比例宽度
            self.width = max_allowed

    def get_char_at_pos(self, x, y):
        """根据坐标返回字符索引"""
        # 转换坐标到文本相对位置
        text_x = x - self.pos[0] 
        text_y = y - self.pos[1]
        # 遍历所有字符位置
        for idx, (cx, cy, cw, ch) in enumerate(self.char_positions):
            if (cx <= text_x <= cx + cw and 
                cy-ch <= text_y <= cy):
                return idx
        return -1
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.clear_selection()
            idx = self.get_char_at_pos(touch.x, touch.y)
            if idx != -1:
                self.select_start = idx
                #添加单击判定事件
                if self._pending_release==None:
                    self._pending_release = Clock.schedule_once(lambda dt:self.on_single_click(touch=touch), 0.5)
            return True
        self.clear_selection()
        return False
    
    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            # 阻止在组件外按下鼠标后进入组件的拖动行为
            if self.select_start==-1:
                return False
            self.selecting= True
            new_end = self.get_char_at_pos(touch.x, touch.y)
            if new_end != -1 and new_end != self.select_end:
                #print(f"鼠标下的字符: {self.plain_text[new_end]}")
                self.select_end = new_end
                self.update_highlight()
            #如果滑动了则取消单击任务
            if self._pending_release!=None:
                Clock.unschedule(self._pending_release)
                self._pending_release=None
            return True
        return False
    
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            # 如果是双击就取消延迟的单击处理/先判断是否存在这个属性，再判定值
            if hasattr(touch, 'is_double_tap') and touch.is_double_tap:
                # 取消之前的延迟任务
                if self._pending_release!=None:
                    Clock.unschedule(self._pending_release)
                    self._pending_release=None
            # 如果是进行了选取
            if self.selecting:
                # 取消之前的单击延迟任务
                if self._pending_release!=None:
                    Clock.unschedule(self._pending_release)
                    self._pending_release=None
                # 执行选取操作
                self.selecting = False
                # 某些函数方法触发
                text=self._selected_text()
                self.select(touch,text)
            return True  # 直接返回，不执行后续逻辑
        return False
    
    def on_double_tap(self, touch,*args):
        if self.collide_point(*touch.pos):
            # 取消单击任务，如果存在
            if self._pending_release!=None:
                Clock.unschedule(self._pending_release)
                self._pending_release=None
            if self.select_start!=-1 and self.select_end==-1:
                # 如果只双击没有移动文本
                #某种函数方法触发了
                text = self.find_sentence(self.select_start)
                self.double_click(text,touch)
                self.clear_selection()
                return True
        return False

    def on_long_touch(self, touch,*args):
        if self.collide_point(*touch.pos):
            # 取消单击任务，如果存在
            if self._pending_release!=None:
                Clock.unschedule(self._pending_release)
                self._pending_release=None
            if self.select_start!=-1 and self.select_end==-1:
                # 如果只长按没有移动文本
                text = self.find_sentence(self.select_start)
                self.long_touch(text,touch)
                self.clear_selection()
            return True
        return False

    def __getattr__(self, name):
        """动态代理事件方法的调用"""
        if name in self._event_mappings:
            target_method = getattr(self, self._event_mappings[name])
            return target_method
        raise AttributeError(f"{self} object has no attribute '{name}'")
    
    # 类方法管理映射关系
    @classmethod
    def bind_event(cls, event_name, method_name):
        """动态绑定事件到指定方法"""
        if not hasattr(cls, method_name):
            raise ValueError(f"方法 {method_name} 不存在")
        cls._event_mappings[event_name] = method_name

    @classmethod
    def unbind_event(cls, event_name):
        """解除事件绑定"""
        cls._event_mappings.pop(event_name, None)

    def update_highlight(self):
        """动态更新高亮区域（解决重复绘制）"""
        new_indexes = set(range(min(self.select_start, self.select_end), 
                              max(self.select_start, self.select_end)+1))
        
        # 移除不再选中的矩形
        for idx in set(self.highlight_rects.keys()) - new_indexes:
            self.canvas.after.remove(self.highlight_rects[idx])
            del self.highlight_rects[idx]
        
        # 添加新选中的矩形
        with self.canvas.after:
            Color(self.select_color[0], self.select_color[1], self.select_color[2], 0.3)
            for idx in new_indexes - set(self.highlight_rects.keys()):
                if idx >= len(self.char_positions):
                    continue
                x, y, w, h = self.char_positions[idx]
                rect = Rectangle(
                    pos=(self.pos[0]+x, 
                         self.pos[1] +(y-h)),
                    size=(w, h)
                )
                self.highlight_rects[idx] = rect

    def color_rect_text(self):
        """给每个字符单独的背景颜色，判断计算是否出错"""

        with self.canvas.after:
            for  x, y, w, h in self.char_positions:
                Color(random.random(),random.random(), random.random(), 0.3)
                Rectangle(
                    pos=(self.pos[0]+x, 
                         self.pos[1] +(y-h)),
                    size=(w, h)
                )
                
    def update_highlight_positions(self,instance,touch):
        """更新现有高亮矩形的位置（解决窗口缩放问题）"""
        # print(f"组件坐标改变，当前坐标{self.center}")
        # print(f"当前纹理大小{self.texture_size}")
        for idx, rect in self.highlight_rects.items():
            if idx >= len(self.char_positions):
                continue
            x, y, w, h = self.char_positions[idx]
            rect.pos = (self.pos[0]+x, self.pos[1] +(y-h))
            rect.size = (w, h)
            # print(rect.pos)

    def show_highlight(self):
        """显示高亮区域"""
        self.clear_highlight()
        with self.canvas.after:
            Color(self.select_color[0], self.select_color[1], self.select_color[2], 0.3)
            for idx,(x, y, w, h) in enumerate(self.char_positions):
                rect = Rectangle(
                    pos=(self.pos[0]+x, 
                         self.pos[1] +(y-h)),
                    size=(w, h)
                )
                self.highlight_rects[idx] = rect

    def clear_selection(self):
        """优化清除逻辑"""
        self.selecting = False
        self.select_start = -1
        self.select_end = -1
        self.clear_highlight()

    def clear_highlight(self):
        """清除所有高亮区域"""
        for rect in self.highlight_rects.values():
            self.canvas.after.remove(rect)
        self.highlight_rects.clear()
    
    def find_english_word(self, index: int) -> str:
        """
        在混合字符串中查找指定索引所在的完整英文单词
        :param s: 输入的混合字符串
        :param index: 要查询的索引位置
        :return: 找到的英文单词，若索引不在单词中则返回空字符串
        """
        # 校验输入合法性
        if not isinstance(index, int) or index < 0 or index >= len(self.plain_text):
            return -1
        
        # 定义辅助函数判断字符是否为英文字母
        def is_alpha(c: str) -> bool:
            return 'a' <= c <= 'z' or 'A' <= c <= 'Z'
        
        # 如果当前字符不是字母，直接返回空
        if not is_alpha(self.plain_text[index]):
            return -1
        
        # 向左查找单词起始位置
        start = index
        while start > 0 and is_alpha(self.plain_text[start - 1]):
            start -= 1
        
        # 向右查找单词结束位置
        end = index
        while end < len(self.plain_text) - 1 and is_alpha(self.plain_text[end + 1]):
            end += 1
        
        # 返回完整单词
        return self.plain_text[start:end+1]
    
    def find_sentence(self, index: int) -> str:
        """
        根据索引定位完整句子，时间复杂度O(n)
        
        Args:
            s: 输入字符串
            index: 目标字符位置索引
        
        Returns:
            包含索引的完整句子字符串
        """
        # 定义句子终止符集合（可扩展）
        terminators = {'。', '.', '!', '？', '?', '！', ';', '；', '\n', '…'}
        
        # 校验输入合法性
        if not self.plain_text or index < 0 or index >= len(self.plain_text):
            return -1
        
        # 寻找起始边界
        start = index
        while start >= 0:
            if self.plain_text[start] in terminators:
                # 如果遇到终止符，则起始位置在下一个字符
                start += 1
                break
            start -= 1
        start = max(0, start)  # 保证不小于0
        
        # 寻找结束边界
        end = index
        while end < len(self.plain_text):
            if self.plain_text[end] in terminators:
                # 包含终止符作为句子结尾
                end += 1
                break
            end += 1
        
        return self.plain_text[start:end]
    
    def add_text(self,text):
        """添加文本"""
        self.text+=text

    def _selected_text(self):
        """获取选中的文本"""
        if self.select_start!=-1 and self.select_end!=-1:
            return self.plain_text[self.select_start:self.select_end]
        return "no select text"

    def print_info(self,*args, **kwargs):
        # 打印组件的基础信息
        print(f"组件ID: {self.id}")
        print(f"组件类型: {self.__class__.__name__}")
        print(f"组件位置: {self.pos}")
        print(f"组件大小: {self.size}")
        print(f"组件文本: {self.text}")
        print(f"组件回调管理器: {self._callback}")
        print(f"组件布局属性：{self.size_hint,self.size_hint_max}")
        print(f"纹理大小：{self.texture_size}")
        print(f"文本大小：{self.text_size}")
        print(f"组件背景颜色：{self.md_bg_color}")
        print(f"组件选取颜色：{self.select_color}")

    def on_enter(self, *args, **kwargs):
        """鼠标进入组件时触发"""
        self.mouse_in=True
        self.fully_update_the_text_layout()

    def on_leave(self, *args, **kwargs):
        """鼠标离开组件时触发"""
        self.mouse_in=False
        pass

    # def on_mouse_update(self, *args, **kwargs):
    #     """鼠标在组件中移动时触发"""
    #     if not self.mouse_in:
    #         return
    #     self.fully_update_the_text_layout()

    #事件触发方法
    def on_single_click(self,touch,*args, **kwargs):
        """单击事件处理"""
        word=self.find_english_word(self.select_start)
        self.single_click(touch,word)
        self._pending_release=None

    # 函数扩展方法，通过注册回调来实现具体的功能，可以在运行时随意切换
    def print(self,*args, **kwargs):
        """打印文本信息"""
        print("打印文本信息")
        print(args, kwargs)
        #self.md_bg_color=(random.random(),random.random(), random.random(), 1)

    def set_translate_callback(self, callback, *args, **kwargs):
        """设置翻译回调函数"""
        self._callback.set('on_translate', callback, *args, **kwargs)

    def translate(self, text, *args, **kwargs):
        """触发翻译回调"""
        print("触发翻译回调")
        self._callback.trigger('on_translate', text, *args, **kwargs)
        
    def set_word_query_callback(self, callback, *args, **kwargs):
        """设置单词查询回调函数"""
        self._callback.set('on_word_query', callback, *args, **kwargs)
    
    def word_query(self, word, *args, **kwargs):
        """触发单词查询回调"""
        print("触发单词查询回调")
        self._callback.trigger('on_word_query', word, *args, **kwargs)
        
    def set_read_aloud_callback(self, callback, *args, **kwargs):
        """设置朗读回调函数"""
        self._callback.set('on_read_aloud', callback, *args, **kwargs)

    def read_aloud(self, text, *args, **kwargs):
        """触发朗读回调"""
        print("触发朗读回调")
        self._callback.trigger('on_read_aloud', text, *args, **kwargs)

    def __del__(self):
        """确保在销毁时取消延迟事件"""
        if self.full_update_event:
            self.full_update_event.cancel()
        if self._pending_parent_update:
            self._pending_parent_update.cancel()

class TestTextInteractorLabel(TextInteractorLabel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = "Hello, World! This is a test. 你好，世界！这是一个测试。"
        # 由于一些属性初始化机制等问题，导致现在无法直接通过在KV文件中设置属性来初始化
        # 只能实例化后再设置文本 正在思考如何解决
        # 已经解决，开启了自动更新，不过设置了更新间隔为0.3秒，避免了频繁更新
        # 最好的使用场景是一次性大量写入，或者关闭自动更新，多次写入后后动更新
        # 测试，自动增加文本
        def add_text(dt):
            self.text += str(random.randint(0,100))
        self.test_event=Clock.schedule_interval(add_text, 0.13)
    
from kivymd.uix.boxlayout import MDBoxLayout
class TestTestInteractorLabel2(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        widget= TestTextInteractorLabel()
        widget.text = "Hello, World! This is a test. 你好，世界！这是一个测试。"
        self.add_widget(widget)
