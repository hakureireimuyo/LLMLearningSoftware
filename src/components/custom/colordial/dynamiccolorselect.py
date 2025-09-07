from kivy.clock import Clock
from kivy.lang import Builder
from kivy.utils import hex_colormap
from kivymd.uix.recycleview import MDRecycleView
from kivy.properties import ObjectProperty
from kivy.animation import Animation
from .colorblock import ColorBlock
from kivy.metrics import dp

Builder.load_string('''
<DynamicColorSelect>:
    # 必须在KV中进行定义才能正常加载数据
    key_viewclass: 'viewclass'
    key_size: 'height'
    do_scroll_x: True
    do_scroll_y: False
    size_hint_y: None
    height: dp(200)

    RecycleBoxLayout:
        id: box
        padding: (dp(10), dp(10), dp(10), dp(10))
        spacing: dp(10)
        orientation: "horizontal"
        default_size: dp(60), dp(200)
        default_size_hint: None,None
        size_hint: None,None
        width: self.minimum_width
        height: dp(200)
        #orientation: "vertical"
''')
import time

class DynamicColorSelect(MDRecycleView):
    callback=ObjectProperty()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Clock.schedule_once(lambda dt:self._create_color_blocks(), 0.1)
        Clock.schedule_once(lambda dt:self.dynamic_size(),1)
        Clock.schedule_once(lambda dt:self.on_size(None,None),1)
        self.current_color=None  # 当前选中的颜色块
        self._last_scroll_time = time.time() #避免一些错误
        self.check=Clock.create_trigger(lambda dt: self._check_scroll_stop(), 0.1, interval=True)
        self.is_scrolling=False

    def update_theme(self, instance, value):
        # 如果从其他地方更新了主题,需要将选择的颜色更新
        # 如果是自己更新的,则忽略
        pass
    def on_size(self, instance, value):
        # 更新用于填充的不可见组件宽度
        for widght in self.ids.box.children:
            if widght.__class__.__name__=='MDWidget':
                widght.width=self.width/2
    
    def _scroll_to_adjacent(self, direction):
        """滚动到相邻的颜色块"""
        if not self.current_color or not self.data:
            return
        #print("??")
        # 获取当前选中块的索引
        current_idx = self.current_color.index
        
        # 计算新索引（确保在有效范围内）
        new_idx = max(0, min(len(self.data) - 1, current_idx + direction))
        
        # 找到新的颜色块组件
        for child in self.ids.box.children:
            if isinstance(child, ColorBlock) and child.index == new_idx:
                self.current_color = child
                break
                
        # 调整到新块
        self._adjust_to_nearest_block()

    def on_scroll_move(self, touch):
        super().on_scroll_move(touch)
        
    def on_scroll_stop(self, touch, check_children=True):
        self.check()
        super().on_scroll_stop(touch, check_children=True)
        
    def _check_scroll_stop(self):
        """检测滚动是否真正停止（考虑阻尼效果）"""
        # 如果0.1秒内没有滚动事件，则认为停止
        if time.time() - self._last_scroll_time > 0.1:
            self._adjust_to_nearest_block()
            self.check.cancel()  # 停止检查滚动
    
    def _adjust_to_nearest_block(self):
        if not self.current_color:
            return
        # 获取布局和视口尺寸
        content_width = self.ids.box.width
        viewport_width = self.width
        
        # 目标点的x坐标（当前选中色块的中心）
        target_x = self.current_color.center_x
        
        # 如果内容宽度小于等于视口宽度，不需要滚动
        if content_width <= viewport_width:
            target_scroll = 0.0
        else:
            # 计算可滚动范围
            scrollable_width = content_width - viewport_width
            
            # 计算理想scroll_x
            target_scroll = (target_x - viewport_width / 2) / scrollable_width
            
            # 应用边界约束
            target_scroll = max(0.0, min(1.0, target_scroll))
        
        # 使用动画平滑滚动
        Animation(scroll_x=target_scroll, d=0.2, t='out_quad').start(self)
        # 将主题颜色切换
        self.theme_cls.primary_palette = self.current_color.text.capitalize()

    def _create_color_blocks(self):
        # 空白填充
        self.data.append({
            'viewclass':'MDWidget',
            'size':(dp(200), dp(20)),
            'size_hint': (None, None),
        })
        # 填充数据
        for i,color_name in enumerate(hex_colormap.keys()):
            self.data.append({
                'viewclass': 'ColorBlock',
                'index': i,
                'color': self._get_color(color_name),
                'text': color_name,
                #'size': (dp(80), dp(200)),
                # 'size_hint': (None, None),
                'pos_hint': {'center_x': 0.5, 'center_y': 0.5},
            })
        # 空白填充
        self.data.append({
            'viewclass':'MDWidget',
            'size': (dp(200), dp(20)),
            'size_hint': (None, None),
        })
        

    def on_scroll_x(self,instance,value):
        self.dynamic_size()
        self._last_scroll_time = time.time()
        
    def dynamic_size(self):
        """当触摸移动时更新颜色块大小"""
        center=self.ids.box.width*self.scroll_x+self.width*(0.5-self.scroll_x)
        for child in self.ids.box.children:
            if isinstance(child, ColorBlock):
                if child.update_size(center)!= None:
                    self.current_color=child
        #print(self.current_color)
        if self.current_color is None:
            return
        if self.callback:
            self.callback(self.current_color.text)
        return

    def _get_color(self, color_name):
        # 从KivyMD颜色定义中获取颜色
        return self.hex_to_rgb(hex_colormap[color_name.lower()])

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return (r, g, b, 1.0)