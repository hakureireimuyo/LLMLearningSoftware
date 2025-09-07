from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty,ObjectProperty
from kivy.metrics import dp
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivy.animation import Animation
Builder.load_string( '''
<WordCard>
    MDRelativeLayout:
        MDLabel:
            text:root.word
            font_style:"Display"
            pos_hint: {"center_x":.5, "center_y":.8}
            halign:"center"
            valign:"center"
            role:"large"
        MDBoxLayout:
            size_hint_y: None
            height: 50
            spacing: 10
            orientation: "horizontal"
            pos_hint: {"center_x":.5, "center_y":.7}
            Widget:
            MDLabel:
                text:root.pronunciation
                font_style:"ARIAL"
                pos_hint: {"center_x":.5, "center_y":.5}
                halign:"center"
                valign:"center"
                role:"medium"
                size_hint_x: None
                width: 200
            MDIconButton:
                icon: "volume-high"
                pos_hint: {"center_x":0, "center_y":.6}
                on_press: root.word_play()
            Widget:
        MDLabel:
            #pos_hint: {"top":.3, "left":.6}
            text:root.translation
            font_style:"STSONG"
            pos_hint: {"center_x":.5, "center_y":.6}
            halign:"center"
            valign:"center"
            role:"medium"
        MDLabel:
            text: root.example
            role:"medium"
            font_style:"STSONG"
            pos_hint: {"center_x":.5, "center_y":.4}
            halign:"center"
            valign:"center"
            role:"medium"

''')
from .basecard import BaseCard
from global_instance import word_player
from threading import Thread
from global_instance import zhipu_group
import weakref
import threading
glm_4_flash=zhipu_group.create_instance("glm-4-flash")
glm_4_flash.set_system_prompt("给你一个单词，你需要用它造一个英语句子，只返回句子和中文翻译，英文句子和中文句子使用换行分开。其余的都不要返回。")
class WordCard(BaseCard):
    """
    该类是一个卡片，用于显示单词
    具有以下属性：
    - word:单词
    - translation:翻译
    - pronunciation:发音
    """
    #滑动行为回调#注：回调函数不能以on开头，会被kivy的检测机制误判
    swipe_horizontal_callback=ObjectProperty(lambda: None)
    swipe_vertical_callback=ObjectProperty(lambda: None)
    # 答题正确错误回调
    answer_correctly = ObjectProperty(lambda: None)
    answer_wrong =ObjectProperty(lambda: None)
    #AI获取例句
    example=StringProperty()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_active = True  # 实例活动状态标志
        self._example_lock = threading.Lock()  # 线程安全锁
        if self.word:
            self.create_example()
    def word_play(self):
        Thread(target=word_player.play,args=(self.word,)).start()

    def _trigger_horizontal_swipe(self, is_right):
        super()._trigger_horizontal_swipe(is_right)
        if self.swipe_horizontal_callback:
            self.swipe_horizontal_callback(self)#这里应该传递自己的实例进去
        return None
    
    def _trigger_vertical_swipe(self, is_up):
        super()._trigger_vertical_swipe(is_up)
        if self.swipe_vertical_callback:
            self.swipe_vertical_callback(self)
        return None
    def __del__(self):
        """实例销毁时自动触发的清理"""
        self._is_active = False

    def create_example(self):
        """创建例句（线程安全版）"""
        def _safe_get_example(weak_self, word):
            # 通过弱引用获取实例
            self_ref = weak_self()
            if not self_ref:
                return

            try:
                response = glm_4_flash.chat_sync(word, stream=True)
                for result in response:
                    # 双重检查实例状态
                    if not self_ref._is_active:
                        break

                    delta = getattr(result.choices[0].delta, 'content', '') or ''
                    with self_ref._example_lock:
                        if self_ref._is_active:
                            self_ref.example += delta
            except Exception as e:
                print(f"Error in example thread: {e}")

        # 使用弱引用避免循环引用
        weak_self = weakref.ref(self)
        Thread(
            target=_safe_get_example,
            args=(weak_self, self.word),
            daemon=True  # 设置为守护线程
        ).start()
class Example(MDApp):
    def build(self):
        return WordCard(word="word",translation="单词",pronunciation="/wɜrd/")

    # def on_start(self):
    #     self.root.ids.box.add_widget(MyCard(style="elevated", text="elevated"))
    #     #self.root.ids.box.add_widget(MyCard(style="elevated", text="elevated"))