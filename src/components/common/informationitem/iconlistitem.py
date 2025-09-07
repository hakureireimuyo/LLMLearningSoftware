"""
基础信息项，包含一个图标和一段文字
"""
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.label import MDIcon
from kivymd.uix.label import MDLabel
from components.common.callback import CallbackManager
class IconListItem(MDBoxLayout):
    icon = StringProperty()
    text = StringProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (1, None)
        self.adaptive_height = True
        self.md_bg_color = self.theme_cls.primaryContainerColor
        self.radius = [20, 20, 20, 20]
        self.padding = dp(10), dp(10), dp(10), dp(10)
        self.spacing = dp(10)
        self._icon = MDIcon(icon=self.icon, 
                            pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self._text = MDLabel(text=self.text, 
                             font_style='STSONG', 
                             role='medium',
                             adaptive_height=True,
                             size_hint_x=1,
                             halign='left',
                             valign='middle',
                             pos_hint={'center_x': 0.5, 'center_y': 0.5}) 
        self.add_widget(self._icon)
        self.add_widget(self._text)
        #self.theme_cls.on_colors=lambda :self.update_theme(None,None)
        #这种绑定只能给一个实例用
        #self.bind(theme_cls=lambda instance, value: self.update_theme(instance, value))
        #self.theme_cls.bind(primaryContainerColor=self.update_theme)
        #将具体的颜色进行绑定才是有效的
        self.theme_cls.bind(primary_palette=self.update_theme)
        self.theme_cls.bind(theme_style=self.update_theme)
        self.theme_cls.bind(dynamic_scheme_name=self.update_theme)
        # 将主题的重要属性进行绑定有效

    def update_theme(self, instance, value):
        self.md_bg_color = self.theme_cls.primaryContainerColor
        
class TestIconListItem(IconListItem):  
    def __init__(self):
        _dict={
            'icon': 'book-open-variant',
            'text': '111111111111111111111111111111111111111111111111111111111111111111111'
        }
        self._callback=CallbackManager()
        self._callback.register('on_click', self.print)
        super().__init__(**_dict)
        
    def print(self):
        print(f'icon: {self.icon}, text: {self.text}')
    
    def on_touch_down(self, touch): 
        if self.collide_point(*touch.pos):
            self._callback.trigger('on_click')
            return True