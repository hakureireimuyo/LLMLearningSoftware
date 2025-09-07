"""
# 十分离谱,一些属性在此处设置不会生效
# self.multiline = True
# self.font_name = "STSONG"
# self.font_size = "26sp"
# 要么延迟设置,要么在KV中设置
#

1 输入模块的可能功能:
1.1 输入框
1.2 输入框自动纠错/
1.3 输入框右侧的图标,点击图标可以触发事件
1.4 输入框包括提示文本,可以选择,选择后触发,将文本输入进输入栏
1.5 多行输入
1.6 修复输入法提示词不出现问题
1.7 增加按钮,点击按钮触发回调,可以进行图片.语音,文档等数据输入
1.8 语音输入快捷键,可以选择是否开启,可以选择长按触发还是作为一个开关
1.9 流式语音识别.可以选择开启,
1.10 彩蛋:按下~进入控制台模式,可以看到后台数据,可以正常交互,可以通过指令调用?(实现起来不难,但是麻烦)
2 输入逻辑
2.1 输入事件调用按下enter
2.2 语音输入长按空格
3 状态
3.1 未获得焦点/忽略一切行为
3.2 获得焦点,可以输入,可以选择提示,可以语音识别
3.3 语音识别中,输入锁定,无法输入,无法选择提示,无法输出
3.4 返回请求中(可中断)/大模型调用时可以在进行输入,但实际不会立刻请求,会等待大模型中断完成后再将新的数据一统再次请求
3.4.1 等待请求完成
3.4.2 等待中断
"""

from kivymd.uix.textfield import MDTextField,MDTextFieldHelperText,MDTextFieldTrailingIcon
from kivy.properties import (
    StringProperty, BooleanProperty, ObjectProperty, OptionProperty, NumericProperty, ListProperty
)
from kivy.clock import Clock
from kivy.animation import Animation

class Input(MDTextField):
    # 是否开启自动纠错
    auto_correct=BooleanProperty(False)
    # 是否开启语音输入
    voice_input=BooleanProperty(False)
    # 是否开启流式语音识别
    stream_voice_input=BooleanProperty(False)
    # 语音输入快捷键
    voice_input_key=StringProperty("~")
    # 是否长按语音输入快捷键
    voice_input_key_long_press=BooleanProperty(True)
    # 语音输入快捷键长按时间
    voice_input_key_long_press_time=NumericProperty(0.5)
    # 是否开启提示词模块
    helper_text=BooleanProperty(False)
    # 控制台模式
    console_mode=BooleanProperty(False)
    # 输入模块状态
    state=OptionProperty("no_fouce",options=["no_fouce",
                                             "focus",
                                             "voice_input",
                                             "stream_voice_input",
                                             "sending",
                                             "disabled",
                                             "console_mode"])
    # 输出回调函数
    output_callback=ObjectProperty(None)

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.add_widget(MDTextFieldHelperText(mode="on_focus"))
        self._icon=MDTextFieldTrailingIcon(icon="send-circle",on_release=self.on_enter)
        self._icon.icon_color_focus=self.theme_cls.primaryColor
        self.add_widget(self._icon)
        Clock.schedule_once(self.apply_settings)
        # 动画定义
        self._animate_icon=(Animation(rotate_value_angle=360, d=1, t="out_quad")
                                +Animation(rotate_value_angle=0,d=0.2, t="out_quad"))
        # recycle event
        self.clear_event=None
    # =====================属性设置=========================#
    def apply_settings(self, dt):
        self.multiline = True
        self.font_name = "STSONG"
        self.font_size = "20sp"

    #=====================属性监听==========================#
    def on_state(self, instance, value):
        if value=="no_fouce":
            self.disabled=False
            self._animate_icon.stop(self._icon)
            self._icon.icon="send-circle"

        if value=="focus":            
            self.disabled=False
            self._animate_icon.stop(self._icon)
            self._icon.icon="send-circle"
            self._icon.color=self.theme_cls.primaryColor

        if value=="voice_input":
            self.disabled=False
            self._icon.icon="microphone"
            self._animate_icon.stop(self._icon)

        if value=="stream_voice_input":
            self.disabled=False
            self._icon.icon="microphone"
            self._animate_icon.stop(self._icon)

        if value=="sending":
            self.disabled=True
            self._icon.icon="send-circle"
            self._animate_icon.repeat = True
            self._animate_icon.start(self._icon)

        if value=="disabled":
            self.disabled=True
            self._animate_icon.stop(self._icon)

        if value=="console_mode":
            self._animate_icon.stop(self._icon)

    def on_focus(self, instance, value):
        super().on_focus(instance, value)
        if value:
            self.state="focus"
        else:
            self.state="no_fouce"

    # =====================属性设置=========================#
    def set_output_callback(self,callback):
        self.output_callback=callback

    # =====================输入模块功能=========================#
    def on_touch_down(self, touch):
        t=(self.width+self.x-1.5*self._icon.width,self.height/2+self.y-self._icon.height/2)
        if self._icon.collide_point(touch.pos[0]-t[0],touch.pos[1]-t[1]):
            self.enter()
        return super().on_touch_down(touch)
    
    def insert_text(self, substring, from_undo=False):
        # print("insert_text",substring)
        if substring=="~":
            self.state="console_mode"
            return
        return super().insert_text(substring, from_undo)
    
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        super().keyboard_on_key_down(window, keycode, text, modifiers)
        print("key_down",keycode)

    def keyboard_on_key_up(self, window, keycode):
        super().keyboard_on_key_up(window, keycode)
        print("key_up",keycode)

    def enter(self):
        # 将文本内容输入回调函数,清空文本
        # print("enter")
        if self.output_callback:
            self.output_callback(self.text)
        self.clear_text()
        pass

    def clear_text(self):
        # 清空文本
        def clear_text_fun(dt):
            if len(self.text)<=5:
                self.text=""
                self.clear_event.cancel()
                self.clear_event=None
                return
            else:
                self.text=self.text[:-5]

        if self.clear_event is None:
            self.clear_event=Clock.schedule_interval(clear_text_fun,0.1)


    def long_time_press_space(self):
        # 长按空格触发
        pass