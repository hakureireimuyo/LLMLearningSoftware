from kivymd.uix.label import MDLabel
from kivy.properties import StringProperty

class Timestamp(MDLabel):
    time=StringProperty("")
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.pos_hint={"center_x":0.5,"center_y":0.5}
        self.font_style="STSONG"
        self.role="small"
        self.adaptive_size=True
        self.valign="middle"
        self.halign="center"
        self.text=self.time
        temp=self.theme_cls.primaryContainerColor.copy()
        self.radius=[10,10,10,10]
        self.padding=[10,0,10,0]
        temp[3]=0.6
        self.md_bg_color=temp
    def on_time(self,instance,value):
        self.text=value

    def on_md_bg_color(self, instance_label, color):
        temp=color.copy()
        temp[3]=0.6
        return super().on_md_bg_color(instance_label, temp)
