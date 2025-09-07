from kivy.lang import Builder
from kivy.properties import StringProperty, ListProperty, NumericProperty, ObjectProperty, BooleanProperty
from kivy.clock import Clock
from kivy.animation import Animation
from kivymd.uix.button import MDButton
from .basecard import BaseCard
from global_instance import word_player
from threading import Thread

Builder.load_string('''
<DictationCard>:
    MDRelativeLayout:
        MDBoxLayout:
            orientation: "horizontal"
            size_hint: None, None
            height: "50dp"
            width: "400dp"
            pos_hint: {"center_x": 0.5, "center_y": 0.7}
            spacing: "10dp"

            MDLabel:
                text: root.pronunciation
                font_style: "ARIAL"
                halign: "center"
                valign: "center"
                size_hint_x: 0.7
                    

            MDIconButton:
                icon: "volume-high"
                theme_text_color: "Custom"
                text_color: app.theme_cls.primaryColor
                on_press: root.play_pronunciation()
                pos_hint: {"center_y": 0.7}

        MDGridLayout:
            id: options_container
            cols: 2
            spacing: "10dp"
            size_hint: None, None
            height: self.minimum_height
            width: self.minimum_width
            padding: "10dp"
            pos_hint: {"center_x": 0.5, "center_y": 0.3}

<DictationOptionButton>:
    style: "outlined"
    size_hint: None, None
    height: "80dp"
    width: "360dp"
    radius: [12, 12, 12, 12]
    theme_bg_color: "Custom"
    md_bg_color: 
        app.theme_cls.inversePrimaryColor if self.is_correct and self.is_selected else \
        app.theme_cls.errorContainerColor if self.is_selected else \
        app.theme_cls.primaryContainerColor
    theme_outline_color: "Custom"
    md_outline_color: app.theme_cls.primaryColor
    disabled: self.is_selected

    MDButtonText:
        text: root.text
        font_style: "STSONG"
        role: "medium"
        halign: "center"
        valign: "center"
''')

class DictationOptionButton(MDButton):
    """听写专用选项按钮"""
    is_correct = BooleanProperty(False)
    is_selected = BooleanProperty(False)
    text = StringProperty()
    callback = ObjectProperty()

    def on_release(self):
        """按钮释放事件处理"""
        if not self.is_selected:
            self.is_selected = True
            self.callback(self.is_correct)
            self._play_feedback_animation()

    def _play_feedback_animation(self):
        """播放反馈动画"""
        anim = Animation(
            md_bg_color=(
                self.theme_cls.inversePrimaryColor if self.is_correct 
                else self.theme_cls.errorContainerColor
            ),
            duration=0.3
        )
        anim.start(self)

class DictationCard(BaseCard):
    """
    听写选择卡片组件
    属性：
    - pronunciation: 音标
    - options: 单词选项列表
    - correct_index: 正确答案索引
    """
    #pronunciation = StringProperty()
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
        Clock.schedule_once(self._generate_options, 0)

    def _generate_options(self, dt):
        """生成选项按钮"""
        container = self.ids.options_container
        container.clear_widgets()

        for idx, word in enumerate(self.options):
            btn = DictationOptionButton(
                text=word,
                is_correct=(idx == self.correct_index),
                callback=self._handle_selection
            )
            container.add_widget(btn)

    def _handle_selection(self, is_correct):
        """处理选项选择"""
        if is_correct:
            if self.answer_correctly:
                self.answer_correctly()
                self.is_complete=True
            self._show_correct_feedback()
        else:
            if self.answer_wrong:
                self.answer_wrong(self.get_date(),self.get_type())
            self._show_wrong_feedback()

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
    
    def play_pronunciation(self):
        """播放发音"""
        Thread(target=word_player.play, args=(self.options[self.correct_index],)).start()
    
# 使用示例
from kivymd.app import MDApp
from kivymd.uix.floatlayout import MDFloatLayout
class ExampleApp(MDApp):
    def build(self):
        f=MDFloatLayout()
        d=DictationCard(
            pronunciation="/ˈæp.əl/",
            options=["Apple", "Appla", "Apply", "Apper"],
            correct_index=0,
            answer_correctly=lambda: print("正确！"),
            answer_wrong=lambda date,_type: print("请再试一次")
        )
        g=DictationCard(
            pronunciation=" /bəˈnɑːnə/",
            options=["Banana", "Canana", "Dnana", "Ciallo～(∠•ω＜)⌒☆"],
            correct_index=0,
            answer_correctly=lambda: print("正确！"),
            answer_wrong=lambda date,_type: print("请再试一次")
        )
        f.add_widget(d)
        f.add_widget(g)
        return f

if __name__ == "__main__":
    ExampleApp().run()