from kivymd.uix.button import MDIconButton
from kivymd.uix.tooltip import MDTooltip,MDTooltipPlain
from kivy.properties import StringProperty, NumericProperty,ObjectProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp

class TooltipIconButton(MDTooltip,MDIconButton):
    """
    悬浮显示工具提示的图标按钮 (支持点击回调)
    
    属性:
        text: 工具提示文本
        icon: 图标名称 (Material Design Icons)
        tooltip_delay: 悬停延迟显示时间(秒)
    """
    tooltip_text = StringProperty()  # 工具提示文本
    icon = StringProperty()  # 图标名称
    callback = ObjectProperty(None)  # 点击回调函数
    def __init__(self,**kwargs):
        self.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        super().__init__(**kwargs)
        print(kwargs)
        print(self.tooltip_text)
        self.tooltip_display_delay = 0.5  # 悬停延迟显示时间(秒)
        tooltip=MDTooltipPlain(
            text=self.tooltip_text,
            font_style="STSONG",
            adaptive_size=True,
            size_hint_max_x=dp(200),
            radius=[10, 10, 10, 10],
            theme_bg_color="Custom",
            theme_text_color="Custom",
            md_bg_color=self.theme_cls.backgroundColor,
            line_color=self.theme_cls.primaryColor,
        )
        self.style="filled"
        self.add_widget(tooltip)
        self.bind(text=self.update_text)  # 绑定文本属性变化

    def update_text(self, *args):
        self._tooltip.text = self.tooltip_text
        print(self._tooltip.text)
    
    def update_theme(self, instance, value):
        self._tooltip.md_bg_color = self.theme_cls.backgroundColor
        self._tooltip.line_color = self.theme_cls.primaryColor
        self.md_bg_color = self.theme_cls.backgroundColor

    def adjust_tooltip_position(self) -> tuple:
        """
        调整工具提示的位置，使其始终不会遮挡父级组件
        """
        p_center = self.to_window(self.center_x, self.center_y)
        p_size=self.size
        c_size=self._tooltip.size
        shift_x,shift_y=0,0
        c_center=[0,0]
        up,down,left,right=False,False,False,False
        # print(p_center,p_size,c_size,Window.size)
        if p_center[1]+p_size[1]/2+c_size[1]+shift_y<Window.height-dp(50):
            up=True
        if p_center[1]-p_size[1]/2-c_size[1]-shift_y>0:
            down=True
        if p_center[0]-c_size[0]-p_size[0]-shift_x>0:
            left=True
        if p_center[0]+c_size[0]+p_size[1]+shift_x<Window.width:
            right=True
        #print(up,down,left,right)
        if up and left and right:
            c_center=[p_center[0],p_center[1]+c_size[1]+shift_y+p_size[1]/2]
            return c_center[0]-c_size[0]/2,c_center[1]-c_size[1]/2
        if down and left and right:
            c_center=[p_center[0],p_center[1]-c_size[1]-shift_y-p_size[1]/2]
            return c_center[0]-c_size[0]/2,c_center[1]-c_size[1]/2
        if left:
            c_center=[p_center[0]-c_size[0]/2-shift_x-p_size[0]/2,p_center[1]]
            return c_center[0]-c_size[0]/2,c_center[1]-c_size[1]/2
        if right:
            c_center=[p_center[0]+c_size[0]/2+shift_x+p_size[0]/2,p_center[1]]
            return c_center[0]-c_size[0]/2,c_center[1]-c_size[1]/2
        #如果四个方向都不满足，就返回中间的位置
        return p_center[0]-c_size[0]/2,p_center[1]-c_size[1]/2
    
    def on_press(self):
        if self.callback:
            self.callback(self)
        return super().on_press()

