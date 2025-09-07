"""
当float作为子组件的时候,
测试box布局如何影响float布局
"""
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.app import MDApp
from kivy.lang import Builder

KV="""
MDBoxLayout:
    orientation:"vertical"
    md_bg_color: 0.5,0.5,1,1
    MDFloatLayout:
        size_hint: 1, 1
        md_bg_color: 1,0,0,1
        minimum_width: dp(300)
        pos_hint: {"center_x": 0.5, "center_y": 0.5}
        MDBoxLayout:
            orientation:'horizontal'
            size_hint:(1,None)
            height:dp(60)
            pos_hint:{'top':1}
            MDLabel:
                text:"chat"
                size_hint:(1,None)
                height:dp(60)
                valign:'middle'
                halign:'center'
                md_bg_color:self.theme_cls.onSecondaryColor
        MDScrollView:
            size_hint: 1, 1
            pos_hint: {"center_x": 0.5, "center_y": 0.5}
            md_bg_color: 1,1,0.5,1
            MDBoxLayout:
                orientation:"vertical"
                adaptive_height:True
                size_hint_x:1
                spacing:20
                padding:[10, 10, 10, 10]
                size_hint_min_x:300
                md_bg_color: 1,0,1,1
                MDLabel:
                    text:"1"
                    size_hint_y:None
                    height:dp(30)
                MDLabel:
                    text:"2"
                    size_hint_y:None
                    height:dp(30)
                MDLabel:
                    text:"3"
                    size_hint_y:None
                    height:dp(30)
    MDTextField:

"""
class Test(MDApp):
    def build(self):
        return Builder.load_string(KV)

Test().run()
