"""
提供一个界面,可以滑动列表,最中间的颜色会被选中
下方则提供所有该配色方案的颜色
"""
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from .dynamiccolorselect import DynamicColorSelect
from .colorwall import ColorWall
    
class ColorDial(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color =self.theme_cls.backgroundColor
        self.orientation='vertical'
        #self.adaptive_height=True
        self.dycolor=DynamicColorSelect(callback=self.current_color)
        self.add_widget(self.dycolor)
        self.button= MDIconButton(
            icon='weather-sunny',
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            size_hint=(None, None),
            size=(dp(48), dp(48)),
            on_release=lambda *args: self.switch_theme(),
        )
        self.add_widget(self.button)
        self.label=MDLabel(
            text="",
            pos_hint={'center_x':0.5,'center_y':0.5},
            #adaptive_size=True,
            size_hint=(1,None),
            height=dp(100),
            font_style="Display",
            role="large",
            halign="center",
            valign="center",
        )
        self.add_widget(self.label)

        self.color_wall=ColorWall()
        self.add_widget(self.color_wall)
        
    def update_theme(self,instance,value):
        self.md_bg_color=self.theme_cls.backgroundColor

    def current_color(self,value):
        if self.label.text!=value:
            self.label.text=value

    def switch_theme(self):
        # 切换亮/暗模式
        self.theme_cls.switch_theme()
        self.button.icon='weather-night' if self.theme_cls.theme_style == 'Dark' else 'weather-sunny'
    
class ColorDialApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Aliceblue"
        return ColorDial()

if __name__ == '__main__':
    ColorDialApp().run()