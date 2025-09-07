from kivy.properties import ListProperty, NumericProperty, ObjectProperty,StringProperty,BooleanProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivy.clock import Clock
from kivy.lang import Builder
from .basecard import BaseCard
from kivy.animation import Animation


Builder.load_string('''
<OptionButton>:
    # style: "text"
    style: "outlined"
    theme_width: "Custom"
    height: "120dp"
    width: "560dp"
    radius: [12, 12, 12, 12]
    theme_bg_color: "Custom"
    md_bg_color:app.theme_cls.primaryContainerColor 
    theme_outline_color: "Custom"
    md_outline_color:app.theme_cls.primaryColor

    MDButtonText:
        id:button_text
        text: root.text
        font_style:"STSONG"
        role:"medium"
        size_hint: None, None
        text_size:self.width, None
        size_hint:1,1
        #size: self.texture_size[0], self.texture_size[1]
        pos_hint: {"center_x": .5, "center_y": .5}
    
<QuizCard>:
    orientation: "vertical"
    spacing: "15dp"
    padding: "20dp"
    #size_hint_y: None,
    # height: self.minimum_height
    MDRelativeLayout:
        MDLabel:
            text: root.word
            font_style: "Display"
            halign: "center"
            size_hint_y: None
            height: self.texture_size[1]
            pos_hint: {"center_x": 0.5, "center_y": 0.8}

        MDLabel:
            text: root.pronunciation
            font_style: "ARIAL"
            halign: "center"
            size_hint_y: None
            height: self.texture_size[1]
            pos_hint: {"center_x": 0.5, "center_y": 0.7}

        MDGridLayout:
            id: options_container
            cols: 1
            spacing: "10dp"
            size_hint_y: None
            height: self.minimum_height
            size_hint_x: None
            width: self.minimum_width
            padding: "10dp"
            pos_hint: {"center_x": 0.5, "center_y": 0.4}
                
''')
from kivymd.uix.button import MDButton

class OptionButton(MDButton):
    """改进后的选项按钮组件"""
    is_correct = BooleanProperty(False)
    is_selected = BooleanProperty(False)
    text=StringProperty()
    callback = ObjectProperty(lambda: None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_release(self, *args):
        """改进后的按钮释放事件"""
        self._on_button_press(self)
        return super().on_release(*args)
    
    def _on_button_press(self, instance):
        """触发选择回调"""
        self.disabled = True    #禁用按钮
        if not self.is_selected:
            self.callback(self.is_correct)  #调用回调函数
            self.is_selected = True #标记为已选择
            app = MDApp.get_running_app()
            if self.is_correct:
                Animation(md_bg_color=app.theme_cls.inversePrimaryColor, d=0.5).start(self)
            else:
                Animation(md_bg_color=app.theme_cls.errorContainerColor, d=0.5).start(self)
    

class QuizCard(BaseCard):
    """
    选择题卡片组件
    属性：
    - word: 单词
    - pronunciation: 音标
    - options: 选项列表
    - correct_index: 正确答案索引
    """
    word = StringProperty()
    pronunciation = StringProperty()
    options = ListProperty()
    correct_index = NumericProperty(-1)
    
    #滑动行为回调
    swipe_horizontal_callback=ObjectProperty(lambda: None)
    swipe_vertical_callback=ObjectProperty(lambda: None)
    # 答题正确错误回调
    answer_correctly = ObjectProperty(lambda: None)
    answer_wrong = ObjectProperty(lambda: None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_complete=False
        self.only_one_wrong=False
        Clock.schedule_once(lambda dt: self._update_options(None, self.options), 0)

    def _update_options(self, instance, value):
        """改进后的选项生成方法"""
        container = self.ids.options_container
        container.clear_widgets()
        
        for idx, option in enumerate(self.options):
            btn = OptionButton(
                text=option,
                is_correct=(idx == self.correct_index),
                callback=lambda x: self._process_answer_result(x)
            )   
            container.add_widget(btn)

    def _process_answer_result(self, is_correct):
        """处理答题结果"""
        if is_correct:
            self.is_complete=True
            self._show_correct_feedback()
            if self.answer_correctly:
                self.answer_correctly()
        else:
            self._show_wrong_feedback()
            if self.answer_wrong and not self.only_one_wrong:
                self.only_one_wrong=True
                self.answer_wrong(self.get_date(),self.get_type())

    def _show_correct_feedback(self):
        """正确反馈动画"""
        self.annimation_of_up_and_down_vibration()
        pass

    def _show_wrong_feedback(self):
        """错误反馈动画"""
        self.annimation_of_left_and_right_vibration()
        pass
    
    def _trigger_horizontal_swipe(self, is_right):
        if self.is_complete:
            super()._trigger_horizontal_swipe(is_right)
            if self.swipe_horizontal_callback:
                self.swipe_horizontal_callback(self)#这里应该传递自己的实例进去
        else:
            self._animate_back_to_center()
        return None
    
    def _trigger_vertical_swipe(self, is_up):
        if self.is_complete:
            super()._trigger_vertical_swipe(is_up)
            if self.swipe_vertical_callback:
                self.swipe_vertical_callback(self)
        else:
            self._animate_back_to_center()
        return None
    
from kivymd.app import MDApp
class ExampleApp(MDApp):
    def build(self):
        quiz_card = QuizCard(
        word="Apple",
        pronunciation="/ˈæp.əl/",
        options=["苹果", "香蕉", "梨子", "橙子"],
        correct_index=0,
        answer_wrong=lambda date,_type:print(date,_type)
        )
        return quiz_card
    
if __name__ == "__main__":
    ExampleApp().run()