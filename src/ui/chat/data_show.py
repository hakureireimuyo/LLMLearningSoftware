from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty,ObjectProperty
from kivy.clock import Clock
from kivy.metrics import dp
Builder.load_string('''
<DataShow>:
    md_bg_color: app.theme_cls.backgroundColor
    cols:2
        
''')
class BaseLabel(MDLabel):
    trun_func=ObjectProperty()
    title=StringProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.radius=[dp(10),dp(10),dp(10),dp(10)]
        app=MDApp.get_running_app()
        self.md_bg_color=app.theme_cls.primaryContainerColor
        self.font_style="STSONG"
        self.role="medium"
        self.size_hint_min_x=dp(100)
        self.size_hint_min_y=dp(30)
        self.size_hint_max=dp(300),dp(50)
        self.halign="left"
        self.valign="middle"
        self.padding="10dp"
    #转换函数
    def turn(self,value):
        if self.trun_func!=None:
            return self.trun_func(value)
        else:
            return str(value)
    #更新函数
    def update(self,value):
        self.text=self.title+":"+self.turn(value)


class DataShow(MDGridLayout):
    #对话时长
    conversation_duration=NumericProperty()
    #对话次数
    conversation_count=NumericProperty()
    #输出字数
    output_count=NumericProperty()
    #输入字数
    input_count=NumericProperty()
    #当前难度
    difficulty=StringProperty()
    #当前模型
    model=StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.on_start()

    def on_start(self):
        self.clear_widgets()
        self.label_conversation_duration=BaseLabel(title="对话时长:",trun_func=self.num_to_time_string)
        self.label_conversation_count=BaseLabel(title="对话次数")
        self.label_output_count=BaseLabel(title="输出字数:")   
        self.label_input_count=BaseLabel(title="输入字数:")
        self.label_difficulty=BaseLabel(title="当前难度:")
        self.label_model=BaseLabel(title="当前模型:")
        self.add_widget(self.label_conversation_duration)
        self.add_widget(self.label_conversation_count)
        self.add_widget(self.label_output_count)
        self.add_widget(self.label_input_count)
        self.add_widget(self.label_difficulty)
        self.add_widget(self.label_model)

    def on_conversation_duration(self,instance,value):
        Clock.schedule_once(lambda dt:self.label_conversation_duration.update(value))
    
    def on_conversation_count(self,instance,value):
        Clock.schedule_once(lambda dt:self.label_conversation_count.update(value))

    def on_output_count(self,instance,value):
        Clock.schedule_once(lambda dt:self.label_output_count.update(value))

    def on_input_count(self,instance,value):
        Clock.schedule_once(lambda dt:self.label_input_count.update(value))

    def on_difficulty(self,instance,value):
        Clock.schedule_once(lambda dt:self.label_difficulty.update(value))

    def on_model(self,instance,value):
        Clock.schedule_once(lambda dt:self.label_model.update(value))


    def num_to_time_string(self,num):
        num=int(num)
        hour=num//3600
        minute=(num%3600)//60
        second=num%60
        return f"{hour}小时{minute}分钟{second}秒"
    
from kivymd.app import MDApp
class TestApp(MDApp):
    def build(self):
        _dict={
            "conversation_duration":10,
            "conversation_count":10,
            "output_count":10,
            "input_count":10,
            "difficulty":"easy",
            "model":"gpt-3.5-turbo"
        }
        return DataShow(**_dict)

if __name__ == '__main__':
    TestApp().run()

