from kivy.lang import Builder
from kivy.properties import StringProperty, ListProperty, NumericProperty, BooleanProperty, ColorProperty,ObjectProperty

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.clock import Clock
from kivy.metrics import dp
import random

Builder.load_string('''
<SingleCharInput>:
    size_hint: None, None
    size: "80dp", "120dp"
    multiline: False
    #font_size: "50sp"
    font_style:"Display"
    role:"large"
    halign: "center"
    valign: "middle"
    mode: "outlined"
    #mode:"filled"
    background_color: app.theme_cls.secondaryContainerColor
    # padding: [dp(8), dp(8), dp(8), dp(8)]

    # canvas.before:
    #     Color:
    #         rgba:app.theme_cls.secondaryContainerColor
    #     Rectangle:
    #         pos: self.pos
    #         size: self.size

<WordInputCard>:
    orientation: "vertical"
    spacing: "15dp"
    padding: "20dp"
    md_bg_color: app.theme_cls.backgroundColor
    MDRelativeLayout:
        MDBoxLayout:
            id: input_container
            size_hint: None, None
            size: self.minimum_size
            pos_hint: {"center_x": 0.5, "center_y": 0.7}
            spacing: "5dp"
        
        MDLabel:
            text: root.pronunciation
            font_style: "ARIAL"
            halign: "center"
            pos_hint: {"center_x": 0.5, "center_y": 0.5}
        
        MDLabel:
            text: root.translation
            font_style: "STSONG"
            halign: "center"
            pos_hint: {"center_x": 0.5, "center_y": 0.3}
    
''')
from kivymd.uix.textfield import MDTextField
from kivy.uix.textinput import TextInput#使用这个组件有问题，暂时不能使用
class SingleCharInput(MDTextField):
    """单个字符输入组件"""
    expected_char = StringProperty()  # 期望字符
    is_correct = BooleanProperty(None)  # 验证状态
    mark_color = ColorProperty(None)  # 标记颜色
    callback = ObjectProperty(lambda: None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.bind(text=self.on_text)

    def insert_text(self, substring, from_undo=False):
        # 只允许输入一个字符
        if len(substring)>1:
            text=substring[-1]
        else:
            text=substring
        self.text=''
        if self.is_english_letter(text):
            super().insert_text(text, from_undo=from_undo)
        else:
            #print("只能输入字母")
            pass
        
    def on_text(self, instance, value):
        if self.focus:
            self.focus = False
            next_widget = self.get_focus_next()
            if next_widget and self.parent==next_widget.parent:
                next_widget.focus = True
        Clock.schedule_once(lambda dt: self.callback(), 0)

    def is_english_letter(self,char):
        if len(char) != 1:
            return False
        code = ord(char)
        return (65 <= code <= 90) or (97 <= code <= 122)
            
    def on_is_correct(self, instance, value):
        # 更新标记颜色
        if value is None:
            self.mark_color = None
        elif value:
            self.mark_color = (0, 0.5, 0, 1)  # 正确颜色
        else:
            self.mark_color = (1, 0, 0, 1)  # 错误颜色

    def locked_status(self,value:bool):
        self.disabled=value
        # self.disabled_foreground_color=(0, 0.5, 0, 1)
        #print("锁定输入")
        #更多的样式更改，敬请期待
        if value:
            pass
        else:
            pass
    def clear_input(self):
        self.text=""
        self.theme_text_color="Primary"

    def check_char_correct(self,is_correct:bool):
        self.theme_text_color="Custom"
        if is_correct:
            self.text_color_focus=(0, 0.5, 0, 1)  # 正确颜色
            self.text_color_normal=(0, 0.5, 0, 1)  # 正确颜色
        else:
            self.text_color_focus=(1, 0, 0, 1)  # 错误颜色
            self.text_color_normal=(1, 0, 0, 1)  # 错误颜色

from .basecard import BaseCard
class WordInputCard(BaseCard):
    """单词输入卡片组件"""
    # word = StringProperty()           # 原始单词
    # pronunciation = StringProperty()  # 音标
    # translation = StringProperty()    # 翻译
    #complete = ObjectProperty(None)    # 完成回调

    #滑动行为回调
    swipe_horizontal_callback=ObjectProperty(lambda x: None)
    swipe_vertical_callback=ObjectProperty(lambda: None)
    # 答题正确错误回调
    answer_correctly = ObjectProperty(lambda: None)
    answer_wrong = ObjectProperty(lambda: None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.processed_word = ""
        self.expected_chars = []
        self.input_widgets = []
        Clock.schedule_once(self._setup_inputs)
        self.wrong_count=0#多次回答错误只会调用一次wrong回调
        self.all_correct = False#是否完全拼写正确

    def _setup_inputs(self, dt):
        # 生成残缺单词
        original = self.word.replace("-", "").replace("'", "")  # 去除特殊符号
        # if len(original) < 4:
        #     if self.answer_correctly:
        #         self.answer_correctly()
        #     return
        # 确定空缺数量（2到字母数之间）
        min_blanks = 1
        max_blanks = len(original)
        num_blanks = random.randint(min_blanks, max_blanks)
        
        # 生成空缺位置
        blank_positions = random.sample(range(len(original)), num_blanks)
        blank_positions.sort()
        
        # 重建带格式的单词
        char_index = 0
        processed = []
        self.expected_chars = []
        for c in self.word:
            if c in ["-", "'"]:
                processed.append(c)
            else:
                if char_index in blank_positions:
                    processed.append("_")
                    self.expected_chars.append(c)
                else:
                    processed.append(c)
                char_index += 1
        
        self.processed_word = "".join(processed)
        self._create_input_widgets()

    def _create_input_widgets(self):
        container = self.ids.input_container
        container.clear_widgets()
        self.input_widgets = []
        
        index = 0
        for c in self.processed_word:
            if c == "_":
                # 创建输入框
                widget = SingleCharInput(
                    expected_char=self.expected_chars[index],
                    callback=self._validate_input
                )
                # widget.bind(on_text=self._validate_input)#第二种方式
                self.input_widgets.append(widget)
                container.add_widget(widget)
                index += 1
            else:
                # 添加固定字符标签
                container.add_widget(MDLabel(
                    text=f"[b]{c}[/b]",
                    font_style="Display",
                    markup=True,
                    size_hint_x=None,
                    width=dp(40),
                    size_hint_y=None,
                    height=dp(80),
                    pos_hint={"center_x": 0.6, "center_y": 0.1}
                ))

    def _validate_input(self):
        """
        某个特殊情况会出现两倍输入栏的回调，只在输入正确的时候触发
        具体问题尚不明确，会造成一道题目被判定为多次回答正确
        """
        #是否全部输入完成了
        if all(widget.text for widget in self.input_widgets):
            #逐个判断输入是否正确
            self.all_correct=True
            for widget in self.input_widgets:
                widget.is_correct = (widget.text.lower() == widget.expected_char.lower())
                if not widget.is_correct:
                    self.all_correct = False
                    widget.check_char_correct(False)
                else:
                    widget.check_char_correct(True)

            #回答正确并且存在回调
            if self.all_correct:
                if self.answer_correctly:
                    self.answer_correctly()
                #锁定输入
                self.locked_state()
                self.annimation_of_up_and_down_vibration()
            #回答错误并且存在回调
            else:
                if self.answer_wrong and self.wrong_count==0:
                    self.answer_wrong(self.get_date(),self.get_type())
                self.wrong_count+=1
                #错误回答反馈抖动并且清空输入栏
                self.clear_input()
                self.annimation_of_left_and_right_vibration()
        if self.wrong_count>=3:
            #结束该问题，给出提示
            self.all_correct=True
            for widget in self.input_widgets:
                widget.text=widget.expected_char
            self.locked_state()
            self.annimation_of_left_and_right_vibration()

    def _trigger_horizontal_swipe(self, is_right):
        if self.all_correct:
            super()._trigger_horizontal_swipe(is_right)
            if self.swipe_horizontal_callback:
                self.swipe_horizontal_callback(self)#这里应该传递自己的实例进去
        else:
            self._animate_back_to_center()
        return None
    
    def _trigger_vertical_swipe(self, is_up):
        if self.all_correct:
            super()._trigger_vertical_swipe(is_up)
            if self.swipe_vertical_callback:
                self.swipe_vertical_callback(self)
        else:
            self._animate_back_to_center()
        return None
    
    def clear_input(self):
        #清空输入栏，并且将焦点移到第一个输入框
        for child in self.input_widgets:
            child.clear_input()
        self.input_widgets[0].focus = True
    def locked_state(self):
        #锁定输入
        #self.disabled=True
        for child in self.input_widgets:
            child.locked_status(True)

# 使用示例
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.app import MDApp
class ExampleApp(MDApp):
    def build(self):
        f=MDFloatLayout()
        card = WordInputCard(
            word="ex-change",
            pronunciation="/ɪksˈtʃeɪndʒ/",
            translation="交换",
            answer_correctly=lambda : print("Correct!"),
            answer_wrong=lambda data,_type: print(data,_type)
        )
        f.add_widget(card)
        card2 = WordInputCard(
            word="apple",
            pronunciation="/ɪksˈtʃeɪndʒ/",
            translation="苹果",
            answer_correctly=lambda : print("Correct!"),
            answer_wrong=lambda data,_type: print(data,_type)
        )
        f.add_widget(card2)
        return f

if __name__ == "__main__":
    ExampleApp().run()