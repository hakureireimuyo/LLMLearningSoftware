from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.divider import MDDivider
from kivymd.uix.label import MDLabel
from kivy.utils import hex_colormap
from kivy.properties import ColorProperty, StringProperty,ObjectProperty
from kivy.clock import Clock
from materialyoucolor.utils.platform_utils import SCHEMES

Builder.load_string( '''
<ColorItem>:
    orientation: "vertical"
    size_hint: None, None
    size: "150dp", "150dp"

    MDBoxLayout:
        id: color_block
        size_hint: None, None
        size: "100dp", "75dp"
        radius: "8dp"
        md_bg_color: root.color_value
        elevation: 1
        pos_hint: {"center_x": 0.5}
    
    MDLabel:
        text: root.color_name
        font_style: "STSONG"
        role: "medium"
        size_hint: None,None
        #width: "100dp"
        size: "150dp", "75dp"
        #height: self.texture_size[1]
        text_size: self.width, None
        #halign: "center"
        halign: "center"
        valign: "top"
        #adaptive_size: True
        theme_text_color: "Primary"
        

<ThemeSettingsPanel>:
    orientation: "vertical"
    spacing: "4dp"
    padding: "24dp"
    adaptive_height: True

    MDLabel:
        text: "主题设置"
        font_style: "STSONG"
        adaptive_height: True
        
    # 调色板设置
    MDBoxLayout:
        orientation: "vertical"
        spacing: "8dp"
        adaptive_height: True
        
        MDLabel:
            text: "主要颜色:"
            font_style: "STSONG"
            role:"medium"
            theme_text_color: "Secondary"
            adaptive_height: True
            
        MDDropDownItem:
            pos_hint: {"center_x": 0.5}
            on_release: root.open_palette_menu(self)
            MDDropDownItemText:
                id: palette_dropdown
                text: "主要颜色"
                font_style: "STSONG"
                role: "medium"
            
    MDDivider:
        
    # 主题风格设置
    MDBoxLayout:
        orientation: "vertical"
        spacing: "4dp"
        adaptive_height: True
        
        MDLabel:
            text: "主题风格:"
            font_style: "STSONG"
            role:"medium"
            theme_text_color: "Secondary"
            adaptive_height: True
            
        MDDropDownItem:
            pos_hint: {"center_x": 0.5}
            on_release: root.open_theme_style_menu(self)
            MDDropDownItemText:
                id: theme_style_dropdown
                text: "亮暗"
                font_style: "STSONG"
                role: "medium"
            
    MDDivider:
    
    # 动态配色方案
    MDBoxLayout:
        orientation: "vertical"
        spacing: "4dp"
        adaptive_height: True
        
        MDLabel:
            text: "动态方案:"
            font_style: "STSONG"
            role:"medium"
            theme_text_color: "Secondary"
            adaptive_height: True
            
        MDDropDownItem:
            pos_hint: {"center_x": 0.5}
            on_release: root.open_scheme_menu(self)
            MDDropDownItemText:
                id: scheme_dropdown
                text: "动态方案"
                font_style: "STSONG"
                role: "medium"
    

<ThemeSettingsPage>:
    md_bg_color: self.theme_cls.backgroundColor
    orientation: "vertical"
    MDBoxLayout:
        orientation: "vertical"
        #spacing: "24dp"
        adaptive_height: True
        padding: "24dp",0,"24dp",0
        pos_hint: {"top": 1}
        
        ThemeSettingsPanel:
            id: theme_settings
            callback:root._updata_color_items
    MDDivider:
    
    MDLabel:
        text: "Color Palette Preview"
        font_style: "STSONG"
        adaptive_height: True
        padding: "8dp"
    
    MDScrollView:
        do_scroll_x: False
        do_scroll_y: True
        MDStackLayout:
            id: color_grid
            #cols: 4
            orientation:"lr-tb"
            spacing: "100dp"
            padding: "18dp", "18dp", "18dp", "18dp"
            #adaptive_size: True
            adaptive_height: True
            pos_hint: {"center_x": .5,"center_y": .5}
''')
from kivymd.uix.tooltip import MDTooltipPlain

class ColorItem(MDBoxLayout):
    color_name = StringProperty()
    color_value = ColorProperty()    # 颜色值
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    #self.text = f"{self.color_name}:\n{self.md_bg_color}"  # 更新文本内容为颜色值的字符串表示形式
    
class ThemeSettingsPanel(MDBoxLayout):
    callback=ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.menu_palette = None
        self.menu_theme_style = None
        self.menu_scheme = None
        

    def open_palette_menu(self, caller):
        menu_items = [
            {
                "text": name.capitalize(),
                "on_release": lambda x=name: self.set_palette(x, caller),
            } for name in hex_colormap.keys()
        ]
        self.menu_palette = MDDropdownMenu(
            caller=caller,
            items=menu_items,
            width_mult=4,
        )
        self.menu_palette.open()

    def open_theme_style_menu(self, caller):
        menu_items = [
            {
                "text": "Light",
                "on_release": lambda: self.switch_theme("Light", caller),
            },
            {
                "text": "Dark",
                "on_release": lambda: self.switch_theme("Dark", caller),
            }
        ]
        self.menu_theme_style = MDDropdownMenu(
            caller=caller,
            items=menu_items,
            width_mult=4,
        )
        self.menu_theme_style.open()

    def open_scheme_menu(self, caller):
        menu_items = [
            {
                "text": scheme,
                "on_release": lambda x=scheme: self.set_scheme(x, caller),
            } for scheme in SCHEMES.keys()
        ]
        self.menu_scheme = MDDropdownMenu(
            caller=caller,
            items=menu_items,
            width_mult=4,
        )
        self.menu_scheme.open()

    def set_palette(self, palette, caller):
        self.theme_cls.primary_palette = palette.capitalize()
        caller.text = palette
        self.menu_palette.dismiss()
        self._callback()

    def switch_theme(self, style, caller):
        self.theme_cls.theme_style = style
        caller.text = style
        self.menu_theme_style.dismiss()
        self._callback()

    def set_scheme(self, scheme, caller):
        self.theme_cls.dynamic_scheme_name = scheme
        caller.text = scheme
        self.menu_scheme.dismiss()
        self._callback()

    def _callback(self):
        if self.callback:
            self.callback()
    
from kivymd.dynamic_color import DynamicColor

class ThemeSettingsPage(MDBoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_color_items()

    def get_color_properties(self):
        return [
            name for name, value in vars(DynamicColor).items()
            if isinstance(value, ColorProperty)
            and not name.startswith('_')  # 过滤私有属性
        ]
    
    def _add_color_items(self):
        color_props =self.get_color_properties()
        print(color_props)
        for name in color_props:
            item = ColorItem(
                color_name=name,
                color_value=getattr(self.theme_cls, name, [1,1,1,1])
            )
            self.ids.color_grid.add_widget(item)
        #print(self.ids.color_grid.children)  # 打印子控件的数量和类型，用于调试和验证效果。这行代码可以在必要时移除。
    def _updata_color_items(self):
        for color_item in self.ids.color_grid.children:
            color_item.color_value = getattr(self.theme_cls, color_item.color_name, [1,1,1,1])

class Example(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        return ThemeSettingsPage()

if __name__ == "__main__":
    Example().run()