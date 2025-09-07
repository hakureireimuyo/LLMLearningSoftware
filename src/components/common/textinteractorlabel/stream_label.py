"""
通过多个label叠加,每个label仅渲染一部分文本
来避免全部的文本内容都随着追加新字符而被重新渲染
"""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Rectangle, Color,SmoothRoundedRectangle
from kivy.clock import Clock
from kivy.properties import (
    StringProperty, NumericProperty, BooleanProperty, ListProperty, 
    DictProperty, ObjectProperty, ColorProperty
)
from kivy.metrics import dp, sp
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
number=0
class ParagraphLabel(MDLabel):
    """
    段落标签组件 - 渲染单段文本
    支持鼠标交互和文本选择功能
    """
    # 存储每个字符的位置信息 (x, y, w, h)
    char_positions = ListProperty([])
    # 存储原始文本               
    plain_text = StringProperty('')
    # 是否正在选区
    selecting = BooleanProperty(False)
    # 选区起始和结束索引
    select_start = NumericProperty(-1)
    select_end = NumericProperty(-1)
    # 高亮矩形字典
    highlight_rects = DictProperty({})
    # 段落索引（在父容器中的位置）
    paragraph_index = NumericProperty(0)
    # 最大宽度
    max_width = NumericProperty(600)
    #背景透明度
    background_opacity = NumericProperty(0.5)
    #  宽度是否依赖父容器的父容器
    adaptive_width_from_parent=BooleanProperty(False)

    def __init__(self, **kwargs):
        # ===============新参数要在此处定义=============
        self.fixed_max_width_update_event=None
        self._last_text = ""            # 上次更新文本
        self._last_max_width = 0           # 上次更新文本最大宽度
        self._last_line_width = 0           # 上次更新文本最大行宽度
        self._last_text_length = 0              # 上次更新文本长度
        # 事件任务
        self._pending_release = None
        self.font_style="STSONG"        # 要先加载,否则会导致字体未加载,计算宽度出现问题

        super().__init__(**kwargs)
                #===============配置要在此处定义================
        # 初始化配置
        self.adaptive_height = True
        self.halign = 'left'
        self.valign = 'top'
        self.padding = [0, 0, 0, 0]
        self.markup = True
        self.role = "medium"
        
        self.text_has_changed=False
        self.size_hint_x=None
        self.width=50
        self.height=50
        self.radius=[dp(10),dp(10),dp(10),dp(10)]
        # 标记新增字符串的相关信息
        # =================绑定要在最后================
        self.bind(
            center = self.update_highlight_positions,
            size = self.update_highlight_positions,
        )
        # 初始更新字符位置
        Clock.schedule_once(self.fixed_widht_updata_event_buff)

    def add_text(self,text):
        #self.buff.append(text)
        self.text+=text
        #Clock.schedule_once(lambda dt:self.fixed_max_width_update(),0.1)
        self.fixed_widht_updata_event_buff()

    def join_buff(self,*arges):
        self.text+="".join(self.buff)
        self.buff.clear()

    def on_max_width(self,instacne,value):
        self.fixed_widht_updata_event_buff()

    def fixed_widht_updata_event_buff(self,*args):
        # if self.fixed_max_width_update_event:
        #     return
        #self.fixed_max_width_update_event=Clock.schedule_once(lambda dt:self.fixed_max_width_update(),0)
        #print(self.fixed_max_width_update_event)
        self.fixed_max_width_update()

    # 固定最大宽度更新
    def fixed_max_width_update(self,*args):
        """固定最大宽度更新"""
        self.text_has_changed=True

        # 计算文本实际需要的最大宽度
        new_width = self._calculate_max_text_width()
        if self.width<self.max_width:
            if new_width >= self.max_width:
                self.width = self.max_width # Set the width of the label    
            else:
                self.width = new_width    
        else:
            self.width=self.max_width

        # print(self.text_size,new_width,self.max_width,self.width)
        # print("self.text",self.text)

        self.fixed_max_width_update_event=None
            
    def _calculate_max_text_width(self,*args):
        """
        增量计算文本最大宽度（假设文本只会增长）
        由于字体资源未加载就会会调用的原因,导致了宽度计算错误
        并且错误会被累积
        """
        if not hasattr(self, '_label') or self._label is None:
            #print(f"当前_label尚未创建{args}")
            return 0
        
        # 如果文本未变化，使用缓存值
        if self.text == self._last_text:
            #print("未更新,使用缓存")
            return self._last_max_width + self.padding[0] + self.padding[2]
        
        # 获取文本变化部分
        new_text = self.text
        old_text = self._last_text
        
        # 如果文本被重置（长度变短），重新计算
        if len(new_text) < len(old_text):
            self._last_text = ""
            self._last_max_width = 0
            self._last_line_width = 0
            old_text = ""
        
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
        global number
        number+=1
        #print(f"更新,计算新的值{self._last_max_width , self.padding[0] ,self.padding[2]}")
        return self._last_max_width + self.padding[0] + self.padding[2]

    def update_char_positions(self, *args):
        """更新字符位置信息"""
        # 当至少触发了一次on_text的时候,才会触发全量更新
        if not self.text_has_changed:
            return
        
        # 如果没有_label属性，直接返回
        if not hasattr(self, '_label') or not hasattr(self._label, '_cached_lines'):
            self.full_update_event = None
            return
            
        self.char_positions = []
        self.plain_text = ""
        
        # 计算字符位置
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
        #self.show_highlight()
        self.text_has_changed = False
    
    def get_char_at_pos(self, x, y):
        """根据坐标返回字符索引"""
        # 转换为相对坐标
        rel_x = x - self.x
        rel_y = y - self.y  # 翻转Y坐标
        
        # 遍历所有字符位置
        for idx, (cx, cy, cw, ch) in enumerate(self.char_positions):
            if (cx <= rel_x <= cx + cw and 
                cy - ch <= rel_y <= cy):
                return idx
        return -1

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.select_start != -1:
                self.clear_selection()
                
            idx = self.get_char_at_pos(touch.x, touch.y)
            if idx != -1:
                self.select_start = idx
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
                print(text)
                #self.select(touch,text)
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
            r,g,b,a = self.theme_cls.primaryColor
            Color(r,g,b,0.3)
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

    def show_highlight(self):
        """显示高亮区域"""
        self.clear_highlight()
        with self.canvas.after:
            r,g,b,a = self.theme_cls.primaryColor
            Color(r,g,b,0.3)
            for idx,(x, y, w, h) in enumerate(self.char_positions):
                rect = Rectangle(
                    pos=(self.pos[0]+x, 
                         self.pos[1] +(y-h)),
                    size=(w, h)
                )
                self.highlight_rects[idx] = rect

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

    def clear_selection(self):
        """清除选择"""
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

    def _selected_text(self):
        """获取选中的文本"""
        if self.select_start!=-1 and self.select_end!=-1:
            return self.plain_text[self.select_start:self.select_end]
        return "no select text"
    
    def on_enter(self, *args, **kwargs):
        """鼠标进入组件时触发"""
        self.update_char_positions()

    def on_leave(self, *args, **kwargs):
        """鼠标离开组件时触发"""
        self.mouse_in=False
        pass

    def on_single_click(self,touch,*args, **kwargs):
        """单击事件处理"""
        #word=self.find_english_word(self.select_start)
        print(self)
        self._pending_release=None
    
    def __str__(self):
        global number
        data ={
            "text":self.text,
            "max_width":self.max_width,
            "width":self.width,
            "height":self.height,
            "new_width":self._calculate_max_text_width(),
            "pos":self.pos,
            "size":self.size,
            "plain_text":self.plain_text,
            "char_positions":self.char_positions,
            "highlight_rects":self.highlight_rects,
            "select_start":self.select_start,
            "select_end":self.select_end,
            "number":number
        }
        return str(data)


class StreamLabel(MDBoxLayout):
    """
    流式文本组件 - 高效渲染大量文本
    支持段落分割、文本选择和交互功能
    """
    # 最大宽度（像素）
    max_width = NumericProperty(dp(600))
    # 开启按照父级宽度按比例自动调整宽度
    adaptive_width_from_parent=BooleanProperty(False)
    # 根据父级宽度按比例自动调整宽度
    adaptive_width_ratio=NumericProperty(0.8)
    # 一次性消息
    text = StringProperty()
    # 透明度
    background_opacity = NumericProperty(0.86)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 初始化配置
        self.orientation = 'vertical'
        #self.spacing = dp(5)
        self.adaptive_height=True
        self.size_hint_x=None
        self.width=50
        self.height=50
        self.padding=[0,dp(10),0,dp(10)]
        #self.radius=[dp(10),dp(10),dp(10),dp(10)]
        # r,g,b,a=self.theme_cls.surfaceContainerHighestColor
        # self.md_bg_color=(r,g,b,self.background_opacity)
        with self.canvas.before:
            r,g,b,a=self.theme_cls.surfaceContainerHighestColor
            self.bk_color=Color(r,g,b,self.background_opacity)
            self.bk=SmoothRoundedRectangle(pos=self.pos,size=self.size,radius=self.radius,segments=30)
        # 段落标签列表
        self.paragraph_labels:list[ParagraphLabel] = []
        # 父容器相关数据
        self._pending_parent_update = None          # 延迟更新父容器宽度事件
        self.relative_max_with=0
        self.bind(
            parent = self._on_parent_change,
            size=self.updata_background,
            pos=self.updata_background
        )
        Clock.schedule_once(lambda dt:self.stream_text(self.text))

    def set_background_color(self,color):
        if len(color)==3:
            self.bk_color.rgba=(*color,self.background_opacity)
        if len(color)==4:
            self.bk_color.rgba=color

    def updata_background(self,instacne,value):
        self.bk.pos=self.pos
        self.bk.size=self.size

    def on_adaptive_width_ratio(self,instance,value):
        if self.adaptive_width_from_parent:
            if self.parent:
                self.relative_max_with = self.parent.width*self.adaptive_width_ratio
            for child in self.paragraph_labels:
                child.max_width=self.relative_max_with

    def on_width(self,instacne,value):
        if not hasattr(self,'paragraph_labels'):
            return
        if self.adaptive_width_from_parent:
            for child in self.paragraph_labels:
                child.max_width=self.width

    def _on_parent_change(self, instance, value):
        """当父容器改变时绑定父容器的尺寸变化"""
        if not self.adaptive_width_from_parent:
            return
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

    def _schedule_width_update(self,*arges):
        """调度宽度更新，使用防抖机制"""
        if not self.adaptive_width_from_parent:
            print("不自动调整宽度")
            return
        if not self.parent:
            return
        # 如果已经存在延迟更新事件，则直接返回
        if self._pending_parent_update:
            return
        # 设置新的延迟更新
        #print(self.adaptive_width_from_parent)
        self._pending_parent_update = Clock.schedule_once(
            lambda dt: self._update_width_from_parent(), 1 )

    def _update_width_from_parent(self):
        """实际执行宽度更新"""
        # 计算子组件最大宽度
        max_text_width = self._get_max_paragraphlabel_width() 
        # print(f"子组件期望的最大大小{max_text_width}")
        # 计算父容器允许的最大宽度（按比例）
        if  self.adaptive_width_from_parent:            
            # 计算父容器允许的最大宽度（按比例）

            self.relative_max_with = self.parent.width * self.adaptive_width_ratio 
            # print(f"父组件的最大大小{self.relative_max_with}")
            # 根据文本宽度和父容器允许宽度动态调整
            if max_text_width <= self.relative_max_with:
                # 文本宽度小于最大允许宽度，使用文本实际宽度
                self.width = max(max_text_width, dp(30))  # 保持最小宽度
            else:
                # 文本宽度超过最大允许宽度，使用比例宽度
                self.width  = self.relative_max_with
        else:
            # 固定最大宽度
            if max_text_width <= self.max_width:
                # 文本宽度小于最大允许宽度，使用文本实际宽度
                self.width = max(max_text_width, dp(30))  # 保持最小宽度
            else:
                # 文本宽度超过最大允许宽度，使用最大宽度
                self.width  = self.max_width
        self._pending_parent_update = None

    def _get_max_paragraphlabel_width(self):
        """修改为:计算子组件的应该有的最大宽度"""
        max_width = 0
        for label in self.paragraph_labels:
            max_width = max(max_width, label._calculate_max_text_width())
            # print(f"max_width:{max_width}")
        return max_width

    def stream_text(self, text):
        """流式添加文本"""
        if not text:
            return
        if text =="\n":
            self.add_paragraph("")
            return
        # 处理换行符
        if '\n' in text:
            parts = text.split('\n')
            for part in parts[:-1]:
                if part:
                    self.add_paragraph(part)
            self.append_to_last(parts[-1])
        else:
            self.append_to_last(text)

        self._update_width_from_parent()
    
    def add_paragraph(self, text):
        """添加新段落"""
        label = ParagraphLabel(
            text=text,
            max_width=self.relative_max_with if self.adaptive_width_from_parent else self.max_width,
            paragraph_index=len(self.paragraph_labels)
        )
        self.paragraph_labels.append(label)
        self.add_widget(label)

    def append_to_last(self, text):
        """追加文本到最后一个段落"""
        if not self.paragraph_labels:
            self.add_paragraph(text)
            return
            
        last_label = self.get_last_paragraph_label()
        if last_label:
            last_label.add_text(text)
    
    def get_last_paragraph_label(self):
        """获取最后一个段落标签"""
        if self.paragraph_labels:
            return self.paragraph_labels[-1]
        else:
            return None
        
    def clear(self):
        for item in self.paragraph_labels:
            self.remove_widget(item)
        self.paragraph_labels.clear()
        self._update_width_from_parent()

    def on_text_selected(self, paragraph_index, start_idx, end_idx, text):
        """文本选择事件"""
        print(f"Selected text in paragraph {paragraph_index}: {text}")
        # 这里可以添加自定义处理逻辑，如复制、翻译等
    
    def on_char_clicked(self, paragraph_index, char_idx, char):
        """字符点击事件"""
        print(f"Clicked character in paragraph {paragraph_index}: {char}")
        # 这里可以添加自定义处理逻辑，如显示翻译等

class StreamLabelTestApp(MDApp):
    def build(self):
        layout = MDBoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # 创建控制面板
        control_panel = MDBoxLayout(size_hint=(1, None), height=50)
        
        # 添加控制按钮
        self.start_btn = Button(text="Start", on_press=self.start_stream)
        self.stop_btn = Button(text="Stop", on_press=self.stop_stream, disabled=True)
        self.reset_btn = Button(text="Reset", on_press=self.reset_label)
        
        control_panel.add_widget(self.start_btn)
        control_panel.add_widget(self.stop_btn)
        control_panel.add_widget(self.reset_btn)
        
        # 创建输入框
        self.input_box = TextInput(
            hint_text="Enter text to stream", 
            size_hint=(1, None), 
            height=100,
            multiline=True
        )
        
        # 创建StreamLabel实例
        self.stream_label = StreamLabel(
            max_width=dp(600),
            size_hint=(1, 1)
        )

        # 添加所有部件
        layout.add_widget(control_panel)
        layout.add_widget(self.input_box)
        layout.add_widget(self.stream_label)
        
        # 初始化流式输入状态
        self.is_streaming = False
        self.stream_index = 0
        
        return layout
    
    def start_stream(self, instance):
        """开始流式输入"""
        if not self.input_box.text:
            return
        
        self.is_streaming = True
        self.stream_index = 0
        self.start_btn.disabled = True
        self.stop_btn.disabled = False
        
        # 设置流式更新定时器
        Clock.schedule_interval(self.add_next_char, 0.01)  # 100字符/秒
    
    def stop_stream(self, instance):
        """停止流式输入"""
        self.is_streaming = False
        self.start_btn.disabled = False
        self.stop_btn.disabled = True
        Clock.unschedule(self.add_next_char)
    
    def reset_label(self, instance):
        """重置标签"""
        self.stream_label.clear()
    
    def add_next_char(self, dt):
        """添加下一个字符"""
        if not self.is_streaming:
            return
        
        text = self.input_box.text
        if self.stream_index >= len(text):
            self.stop_stream(None)
            return
        
        # 获取下一个字符
        char = text[self.stream_index]
        self.stream_index += 1
        
        # 添加到流式标签
        self.stream_label.stream_text(char)
        #self.pl.add_text(char)



if __name__ == '__main__':
    StreamLabelTestApp().run()