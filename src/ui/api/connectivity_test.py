"""
2025年3月21日 18点24分
这个模块接受一个对象的引用,调用对象的一个方法,通过返回的参数改变组件的状态
用于显示当前模块的使用情况,数据,信息等
"""

from kivy.lang import Builder
from kivy.properties import StringProperty, ListProperty, ObjectProperty, OptionProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivymd.app import MDApp
from kivy.clock import Clock
from kivymd.uix.expansionpanel import MDExpansionPanel
from kivy.metrics import dp

Builder.load_string('''
<MinLabel>:
    size_hint: (None, None)
    height: dp(60)
    width: self.minimum_width
    #size:(dp(500), dp(60))  
    orientation: 'horizontal'
    md_bg_color: app.theme_cls.primaryContainerColor
    padding: "12dp"
    MDLabel:
        text: root.text
        size_hint: None,None
        width: dp(200)
        height: "60dp"
        font_style: 'STSONG'
        role:"medium"
    MDLabel:
        text: root.tooltip_text
        #size_hint: (None,None)
        adaptive_size: True
        width: self.texture_size[0]
        height: "60dp"
        font_style: 'STSONG'
        role:"small"
    RotatingIcon:
        id:icon
        icon:root.state
    
<GroupLabel>:
    orientation: "vertical"
    padding: "12dp", 0, "12dp", "12dp"
    md_bg_color: self.theme_cls.surfaceContainerLowColor
    adaptive_height: True
    size_hint:1,None
    MDDivider:
    MDLabel:
        text: root.group_name
        font_style: 'STSONG'
        role:"large"
        size_hint:1,None
        height:"70dp"
    MDStackLayout:
        md_bg_color: self.theme_cls.surfaceContainerLowColor
        orientation:"lr-tb"
        id:models
        adaptive_height: True
        spacing: "12dp"
        padding: "12dp"
        pos_hint: {"center_x": .5,"center_y": .5}
''')
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.behaviors import (
    CommonElevationBehavior,
    DeclarativeBehavior,
    RectangularRippleBehavior,
    BackgroundColorBehavior,
)
from kivymd.uix.label import MDIcon
from kivymd.uix.behaviors import CommonElevationBehavior
from kivymd.uix.behaviors import RotateBehavior
from kivy.animation import Animation
import threading
from kivymd.uix.behaviors import HoverBehavior
from kivymd.uix.tooltip import MDTooltip

class RotatingIcon(RotateBehavior,MDIcon):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
import time

class instacne:
    def __init__(self,ToF):
        self.ToF=ToF
    def is_available(self):
        time.sleep(1)  # Sleep for 1 second
        if self.ToF:
            return True,"100ms"
        else:
            return False,"错误文本内容"
    
class MinLabel(ButtonBehavior,RectangularRippleBehavior,MDBoxLayout,HoverBehavior):
    text = StringProperty()
    #联通性状态,有联通,无法联通,正在加载,未测试
    state=OptionProperty('restart', options=['wifi', 'alert-outline', 'loading','restart'])
    #传入的实体参数,具有一个is_avilable方法
    instance=ObjectProperty()
    tooltip_text=StringProperty()
    width_min=NumericProperty(dp(300))
    def __init__(self,text,instacne,**kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.instance=instacne
        self.state="restart"
        self.anim=Animation(rotate_value_angle=360, d=1)+Animation(rotate_value_angle=0, d=1)
        self.bind(state=self.on_state)
        
    def on_state(self,*arges):
        self.ids.icon.rotate_value_angle=0
        if self.state=='loading':
            self.ids.icon.icon='loading'
            self.anim.repeat = True
            self.anim.start(self.ids.icon)
        elif self.state=='alert-outline':
            self.ids.icon.icon='alert-outline'
            self.anim.stop(self.ids.icon)
            self.ids.icon.rotate_value_angle=0
            self.md_bg_color=self.theme_cls.errorContainerColor
        else:
            self.ids.icon.icon=self.state
            self.anim.stop(self.ids.icon)
            self.ids.icon.rotate_value_angle=0

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.is_available()
            return True
        else:
            return False
        #return super().on_touch_move(touch, *args)
    def on_enter(self, *args):
        '''
        The method will be called when the mouse cursor
        is within the borders of the current widget.
        '''
        if self.state=='alert-outline':
            self.md_bg_color=self.theme_cls.errorColor
        else:
            self.md_bg_color = self.theme_cls.onSecondaryColor

    def on_leave(self, *args):
        '''
        The method will be called when the mouse cursor goes beyond
        the borders of the current widget.
        '''
        if self.state=='alert-outline':
            self.md_bg_color=self.theme_cls.errorContainerColor
        else:
            self.md_bg_color = self.theme_cls.primaryContainerColor
    #连通性测试
    def is_available(self):
            #开始异步等待结果返回
        #print(self.instance)
        def fun(*arges):
            self.state="loading"
            try:
                if self.instance:
                    result=self.instance.is_available()
                    #print(result)
                    self.tooltip_text=result[1]
                    if result[0]:
                        self.state="wifi"
                    else:
                        self.state="alert-outline"
                    self.do_layout()
            except:
                self.state="alert-outline"
                self.tooltip_text="API功能尚未完善"
        if self.instance != None:
            threading.Thread(target=fun).start()
        else:
            self.state="alert-outline"
            self.tooltip_text="实例未加载"

        #Clock.schedule_once(fun)  # Replace with actual functionality


from kivymd.uix.list import MDListItemTrailingIcon
class TrailingPressedIconButton(
    ButtonBehavior, RotateBehavior, MDListItemTrailingIcon
):
    ...

class GroupLabel(MDBoxLayout):
    group_name = StringProperty()
    def __init__(self, group_name, **kwargs):
        super().__init__(**kwargs)
        self.group_name = group_name
        self.orientation = 'vertical'
        ins=instacne(True)
        insf=instacne(False)
        for state in ['text_translate', 'voice_translate','tts']:
            self.ids.models.add_widget(MinLabel(state, ins))
        for state in ['text_translate', 'voice_translate','tts']:
            self.ids.models.add_widget(MinLabel(state, ins))
        self.ids.models.add_widget(MinLabel("glm-4-plus", insf))

    def loading_group(self,group):
        self.ids.models.clear_widgets()
        list_model_keys=group.list_base_models_id()
        list_modle_name=group.list_models()
        print(f"加载组{self.group_name}的实例")
        print(list_model_keys)
        print(list_modle_name)
        for instacne_id,name in zip(list_model_keys,list_modle_name):
            print(instacne_id,name)
            self.ids.models.add_widget(MinLabel(name, group.get_provider(instacne_id)))
        #print(self.ids.models.children)
    def is_available(self):
        for child in self.ids.models.children:
            child.is_available()
        pass

class Exmple(MDApp):
    def build(self):
        # Create a GroupLabel instance for demonstration
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Beige"
        temp=GroupLabel("api_manager")
        #temp.loading_group(baidu_group)
        return temp
    
if __name__ == '__main__':
    Exmple().run()
    pass
