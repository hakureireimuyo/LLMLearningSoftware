"""
主要用于显示当前配色方案动态生成的所有配色
"""
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.stacklayout import MDStackLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.widget import MDWidget
from kivy.metrics import dp
from kivymd.dynamic_color import DynamicColor
from kivymd.uix.divider import MDDivider

class ColorWall(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        #self.adaptive_size = True
        self.size_hint=(1,1)
        #self.size_hint_max_y=dp(500)
        # self.padding = dp(10)
        # self.spacing = dp(10)
        self.pos_hint={'center_x':0.5,'center_y':0.5}
        self.md_bg_color=self.theme_cls.backgroundColor
        self.color_wall=[]

        self.add_widget(MDDivider(color=self.theme_cls.primaryColor))
        # 滚动视图和网格布局
        self.grid = MDStackLayout(
            #cols=6,
            size_hint=(1,None),
            adaptive_height=True,
            # spacing=dp(20),
            # padding=(dp(10),dp(10,),dp(10),dp(10)),
            pos_hint={'center_x':0.5,'center_y':0.5}
        )
        self.scroll = MDScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            size_hint_y=None,
            pos_hint={'center_x':0.5,'center_y':0.5},
            height=dp(500)  # 设置固定高度
        )
        self.scroll.add_widget(self.grid)
        self.add_widget(self.scroll)
        self.create_color_wall()

    def update_theme(self,instance,value):
        self.md_bg_color=self.theme_cls.backgroundColor
        
        # 获取所有颜色属性
        color_properties = [
            attr for attr in dir(DynamicColor) 
            if attr.endswith("Color") and hasattr(self.theme_cls, attr)
        ]
        # 所有颜色
        all_colors = [getattr(self.theme_cls, cp) for cp in color_properties]

        # 排序颜色 - 按亮度从亮到暗
        sorted_colors = self.sort_colors_by_luminance(all_colors,color_properties)

        # 创建颜色方块
        for color_prop,color_block in zip(sorted_colors,self.color_wall):
            # 获取颜色值
            color_value = color_prop[0]
            color_block.md_bg_color=color_value

    def create_color_wall(self):
        """创建颜色方块墙"""
        # 清除现有内容
        self.grid.clear_widgets()
        
        # 色块引用
        self.color_wall.clear()

        # 获取所有颜色属性
        color_properties = [
            attr for attr in dir(DynamicColor) 
            if attr.endswith("Color") and hasattr(self.theme_cls, attr)
        ]
        # 所有颜色
        all_colors = [getattr(self.theme_cls, cp) for cp in color_properties]

        # 排序颜色 - 按亮度从亮到暗
        sorted_colors = self.sort_colors_by_luminance(all_colors,color_properties)

        # 创建方块（按排序后顺序）
        for color in sorted_colors:
            color_block = MDWidget(
                md_bg_color=color[0],
                size_hint=(None, None),
                size=(dp(120), dp(120)),
                radius=dp(10)
            )
            self.grid.add_widget(color_block)
            self.color_wall.append(color_block)



    def sort_colors_by_luminance(self, color_values,color_properties):
        """按亮度从最亮到最暗排序"""
        def calculate_luminance(rgba):
            r, g, b, _ = rgba  # 忽略alpha通道
            # 标准亮度计算公式（ITU-R BT.709）
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        # 为每个颜色计算亮度
        color_luminances = [
            (calculate_luminance(color), color,color_property)
            for color,color_property in zip(color_values,color_properties)
        ]
        
        # 按亮度降序排序
        color_luminances.sort(key=lambda x: x[0], reverse=True)
        i = 0
        for color in color_luminances:
            print(color[0],color[2])
            i+=1
            if i%6==0:
                print()


        # 返回排序后的颜色列表
        return [(color,properties) for _, color,properties in color_luminances]
    
from kivymd.app import MDApp
class Test(MDApp):
    def build(self):
        self.t=ColorWall()
        return self.t

    
if __name__ == '__main__':
    Test().run()