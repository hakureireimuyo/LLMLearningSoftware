from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import NumericProperty,ColorProperty,StringProperty
from kivy.metrics import dp

class ColorBlock(MDBoxLayout):
    # 定义大小变化的属性
    min_size = dp(40)  # 最小尺寸
    max_size = dp(180)  # 最大尺寸
    center_zone = dp(200)  # 中心区域宽度（在此区域内会放大）
    index=NumericProperty(0)  # 用于标识颜色块的索引
    color=ColorProperty()  # 颜色属性
    text=StringProperty()  # 显示的文本

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(80), self.max_size+20)  #固定父容器
        self.padding = (dp(10), 0, dp(10), 0)
        #self.md_bg_color=(1,0,0,1)

        self.con=MDBoxLayout(    
                md_bg_color=self.color,
                size_hint=(None, None),
                size=(60,self.min_size),
                radius = (dp(10),dp(10),dp(10),dp(10)),
                pos_hint={"center_x": 0.5, "center_y": 0.5},
            )
        self.add_widget(self.con)
    
    def on_color(self,instance,value):
        self.con.md_bg_color=self.color

    def update_size(self, center_x):
        """
        根据位置更新大小
        :return 如果中心在当前组件就返回True,否则False
        """
        distance = abs(self.center_x - center_x)
        #print(f"distance: {distance}")
        # 检查是否在中心区域内
        if distance <= self.center_zone:
            # 计算大小比例 (0-1, 0在边缘, 1在中心)
            size_ratio = 1.0 - (distance / self.center_zone)
            # 计算新尺寸 (在min_size和max_size之间)
            new_size = self.min_size + (self.max_size - self.min_size) * size_ratio
            self.con.size = (dp(60), new_size)
            if distance<=self.width*0.5:
                return self
        return None