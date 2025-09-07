"""
该类定义了消息的最终类，实现了消息类的各种功能，比如增加了悬停检测
一键翻译，右键唤起菜单并且在菜单中可以执行更多操作，比如删除消息，复制
tts，翻译，等功能
"""
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.app import MDApp
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivy.properties import StringProperty, NumericProperty, ListProperty, BooleanProperty
from kivy.properties import OptionProperty,DictProperty,ObjectProperty

from common_app import CommonApp
from kivy.core.text import LabelBase
from kivy.lang import Builder
from kivy.metrics import sp
from kivy.uix.label import Label
from kivymd.uix.label import MDLabel
from components.common.textinteractorlabel.textinteractorlabel import CharDetectLabel

Builder.load_string(
    """
<CustomLabel>:
    line_height: 1.5
    text: "This is a custom label with line height"

<Message>:
    orientation: "horizontal"
    adaptive_height: True
    #md_gb_color:(0.9, 0.9, 0.9, 1) if root.identity == "User" else (0.5, 0.5, 0.8, 1)
    #spacing: "10dp"  # 调整段之间的间距
    #md_gb_color:app.theme_cls.secondaryColor if root.identity == "User" else app.theme_cls.primaryColor
    size_hint_x: 0.9

    MDBoxLayout:
        orientation: "vertical"
        adaptive_height: True
        size_hint_x:0.9
        
        CharDetectLabel:
            id:text
            text: root.text
            markup: True
            halign: "left"
            #valign: "center"
            font_style:"STSONG"
            size_hint_y: None
            height: self.texture_size[1]
            text_size: self.width, None
            padding: 10, 0
            line_height:1
            color:"black"
            split_str:" "
            on_ref_press: print("1111")
            
            
        MDDivider:
            id: divider
            size_hint_x: 0.98
            pos_hint: {'center_x': .5, 'center_y': .5}
            color: app.theme_cls.secondaryColor
            opacity: 0

        CharDetectLabel:
            id:transition
            text: root.transition_text
            markup: True
            halign: "left"
            valign: "top"
            font_name: "STSONG"
            size_hint_y: None
            height: self.texture_size[1]
            text_size: self.width, None
            
        MDBoxLayout:
            id: image_box
            orientation: "vertical"
            adaptive_height: True

    MDBoxLayout:
        orientation: "vertical"
        adaptive_height: True
        size_hint_x:None
        width: "50dp"
        MDIconButton:
            on_release: root.open_menu(self)
            icon: "menu"
  
"""
)

from kivy.uix.behaviors import FocusBehavior
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
class SelectableLabel(CharDetectLabel, FocusBehavior):
    """
    A label that allows text selection with mouse drag.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._textinput = TextInput(
            text=self.text,
            readonly=True,
            background_color=(0, 0, 0, 0),
            foreground_color=self.color,
            cursor_color=self.color,
            size_hint=(None, None),
            size=self.size,
            pos=self.pos,
        )
        self._textinput.bind(size=self._update_textinput, pos=self._update_textinput)
        self.bind(text=self._on_text, color=self._on_color, size=self._update_textinput, pos=self._update_textinput)
        self.add_widget(self._textinput)

    def _on_text(self, instance, value):
        self._textinput.text = instance.text

    def _on_color(self, instance, value):
        self._textinput.foreground_color = instance.color
        self._textinput.cursor_color = instance.color

    def _update_textinput(self, instance, value):
        self._textinput.size = instance.size
        self._textinput.pos = instance.pos

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            return self._textinput.on_touch_down(touch)
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            return self._textinput.on_touch_move(touch)
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            return self._textinput.on_touch_up(touch)
        return super().on_touch_up(touch)


class CustomLabel(CharDetectLabel):
    selected_text = StringProperty('')
    '''The text that is selected by the user through mouse dragging.

    :attr:`selected_text` is a :class:`~kivy.properties.StringProperty` and
    defaults to ''.
    '''

    def __init__(self, **kwargs):
        super(CharDetectLabel, self).__init__(**kwargs)
        self._selection_start = None
        self._selection_end = None
        self.bind(on_touch_move=self._on_touch_move, on_touch_up=self._on_touch_up)

    def _on_touch_move(self, instance, touch):
        if self.collide_point(*touch.pos):
            if self._selection_start is None:
                self._selection_start = touch.pos
            self._selection_end = touch.pos
            self._update_selection()

    def _on_touch_up(self, instance, touch):
        if self._selection_start and self._selection_end:
            self._update_selection()
        self._selection_start = None
        self._selection_end = None

    def _update_selection(self):
        if not self._selection_start or not self._selection_end:
            self.selected_text = ''
            return

        start_x, start_y = self._selection_start
        end_x, end_y = self._selection_end

        # Convert touch positions to text positions
        start_pos = self._get_text_position(start_x, start_y)
        end_pos = self._get_text_position(end_x, end_y)

        if start_pos and end_pos:
            start_idx = min(start_pos, end_pos)
            end_idx = max(start_pos, end_pos)
            self.selected_text = self.text[start_idx:end_idx]

    def _get_text_position(self, x, y):
        tx = x - (self.center_x - self.texture_size[0] / 2.)
        ty = self.texture_size[1] - (y - (self.center_y - self.texture_size[1] / 2.))
        for i, (char, pos) in enumerate(self._label._glyphs):
            if pos[0] <= tx <= pos[0] + pos[2] and pos[1] <= ty <= pos[1] + pos[3]:
                return i
        return None
    
class Message(MDBoxLayout):
    #文本信息
    text=StringProperty()
    """
    该变量记录了消息中的所有文本信息，并且会被用于在MDLabe中进行渲染
    CharDetectLabel中可以通过特殊格式实现文本的渲染，比如[color=#ff0000]红色[/color]
    后续会添加多种函数用于实现自动化特殊文本渲染函数用于实现不同的效果
    """
    #图像列表
    image_list= ListProperty()
    """
    该变量记录图片列表，列表的内容通常为图片的路径，后续会添加图片的渲染功能
    无论图片多少都会被渲染在文本之后，并且图片会尽量贴合Message类，即在宽度上
    和Message保持一致。
    该方法暂时不实现
    """
    #翻译文本内容
    transition_text=StringProperty()
    """
    该变量记录了消息的翻译内容，用户获取到文本内容的翻译后，有三种方式将翻译和原文进行对比
    1 将翻译和原文逐句放置在一起，并且包括,逐句放置在下方，空间不够则延伸。每对句子单独另起一行。一句原文一句翻译
    2 将翻译和原文按照自然段进行交叉放置。
    3 将翻译和原文分别放置，其中包括，左右分割，上下分割
    """
    #翻译内容缓存
    transition_text_copy=StringProperty()
    """
    在翻译内容需要隐藏和显示的时候，通过这个来存储上次翻译的结果
    """
    #翻译插入位置
    transition_position=OptionProperty('down', options=['down', 'right', 'together','float'])
    """
    该变量记录了翻译的文本应该插入在原始文件中的那个位置
    分别会将翻译的文本插入到原始文本的下方，右侧，或者是交叉插入
    float表明将翻译的内容作为一个悬浮新窗口进行展示，通常为渲染出一个鼠标指针悬停的时候会自动产生一个
    悬浮窗口，不可操作，当进入到范围的时候就会自动触发，并且直接翻译全文，与文本分割程度无关，文本过长可以滑动
    悬浮窗口的大小有最大值，不会达到非常大的地步
    """
    #翻译文本的分割程度
    transition_level=OptionProperty('sentence', options=['sentence', 'paragraph', 'whole'])
    """
    翻译文本的分割成度，分别为句子，自然段，全文
    不同的分割成度搭配插入的位置具有不同的效果
    比如句子插入到右侧不会新建一个独立的区域，而当是自然段进行分割或者全文的时候，会新建一个区域，用于对照显示
    而如果插入位置在下方，则无论是哪种程度，都是将翻译内容插入到原始文本下方，只是段会与段在一起，全文则是追加在末尾
    如果是直接一起，那么在句子的分割程度下，会按句子追加在句子的末尾，而在自然段的分割程度下，会将自然段追加在末尾
    而在全文的分割程度下，会将全文追加在末尾
    如果是float,则最终结果与该变量无关，是固定的结果
    """

    #录音文件
    voice=StringProperty()
    """
    用户将某些内容转为语音后，语音会被存储在一个集中缓存的地方，该变量会保存一个唯一文件名字
    通过一个函数将文件名转为路径，则可以获取到记录在磁盘中的录音文件。随后可以播放该录音
    录音文件通过一些api或者内置的功能实现，会将结果先存储，并分配一个唯一标识，随后才能播放
    但如果调用的方法获取到的是流式数据，则使用另一个方式来处理，可以立即播放录音，但当录音数据
    全部接收后，依旧会执行上述操作，保存文件进磁盘，并分配一个唯一标识
    """
    #消息id
    message_id=NumericProperty()
    """
    当消息生成的时候会分配一个唯一id，并且会向数据库中写入数据，用于长期保存聊天数据
    为了确保数据库调用不会太频繁，该部分的数据存储操作在一些特定情况下才会触发，比如
    当程序关闭的时候，才会将新产生的数据记录进数据库。
    通过此id，可以从数据库中获取到消息并生成消息对象，id数据由更高一层此的管理方法从数据库中获取
    由于本程序只包含一对多的对话，因此，只需要记录每个不同的聊天对象所产生的消息id就
    存在一个专门的表，记录该消息的id,以及生成的时间，当这个类将自己删除的时候，会先删除数据库中该消息的记录
    和消息的id以及相关的数据，然后再删除该消息对象。
    消息的生成有两种方式
    1 初始化从数据库列表中获取到近期的消息数据，并生成消息对象，返还给聊天类
    2 通过输入栏进行消息的输入，会产生用户的消息对象
    3 ai的回答会产新消息对象，除了身份不同，功能是等价的
    """
    #是否是新消息
    is_new=BooleanProperty()
    """
    该变量用于记录消息是否是新消息，新消息会在程序退出的时候记录进入数据库
    """
    #身份，一般为User和Ai
    identity = OptionProperty('User', options=['User', 'Ai'])
    """
    该变量记录消息的身份，取值范围为'User'和'Ai'
    """
    #聊天对象名字
    chat_name=StringProperty()
    """
    该变量用于记录聊天对象的名字，后续可能会有用，比如在数据库中查询相关聊天的内容
    或者是删除相关聊天的数据，因此该名字创建完成后不能被修改，如果允许修改，则会需要
    更新数据库中所有的相关数据，因此最好直接限制，不让用户作出修改
    """
    #弹出菜单
    menu: MDDropdownMenu = None
    """
    该菜单会用于实现将原始文本翻译，将翻译内容转语音并实现播放等操作
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color=[1,1,1,1] if self.identity == "User" else [0.8,0.8,1.1]
        print(kwargs)

    def on_text(self,instance,value):
        print("文本内容已更新")
        pass

    def show_transition(self):
        def update_transition_text():
            if self.ids.divider.opacity == 0:
                self.transition_text=self.transition_text_copy
                self.ids.transition.opacity = 1
                self.ids.divider.opacity = 1
                print("1")
            else:
                print("2")
                self.ids.transition.opacity = 0
                self.ids.divider.opacity = 0
                self.transition_text = ''
            return False  # Return False to stop the Clock from rescheduling

        # Schedule the update on the main thread
        Clock.schedule_once(lambda dt: update_transition_text())

    def get_transition_text(self,instance,value):
        self.transition_text = '此处获取原始文本翻译的调用结果'
        self.transition_text_copy = self.transition_text
        self.show_transition()

    def on_transition_position(self, instance, value):
        pass
    def on_voice_get(self, instance, value):
        pass
    def on_transition_level(self, instance, value):
        pass
    async def tts(self):
        pass
    def text_appen(self,text_appen):
        """
        追加字符
        """
        self.text+=text_appen+"\n"
        #print(self.text)
        pass
    def show_size(self):
        print(f"Text font size: {self.ids.text.font_size}")
        print(f"Transition font size: {self.ids.transition.font_size}")
        print(f"Message width: {self.width}")
        print(f"Message height: {self.height}")

    def print_it(self,instance, value):
        print("111")
        print('User click on', value)

    def change_font_size(self,value):
        print(self.ids.text.font_size)
        self.ids.text.font_size=self.ids.text.font_size+sp(value)
        self.ids.transition.font_size+=sp(value)
        print(self.ids.text.font_size)
        print(sp(value))
    def print(self):
        """
        打印所有变量的值
        """
        # print(self.text)
        # print(self.image_list)
        # print(self.transition_text)
        # print(self.transition_text_copy)
        # print(self.transition_position)
        # print(self.transition_level)
        # print(self.voice)
        # print(self.message_id)
        # print(self.is_new)
        # print(self.identity)
        # print(self.chat_name)
        print(self.ids.text.center)
        
    def open_menu(self, menu_button):
        menu_items = []
        for item, method in {
            "transition": lambda: self.get_transition_text(None,None),
            "vioce": lambda:self.on_voice_get(None,None),
            "share to note": lambda: print("1"),
            "delete message": lambda: print("1"),
            "Add text": lambda:self.text_appen("p"),
            "show size": lambda:self.show_size(),
            "print": lambda:self.print(),
        }.items():
            menu_items.append(
                {
                    "text": item,
                    "on_release": method,
                }
            )
        self.menu = MDDropdownMenu(
            caller=menu_button,
            items=menu_items,
            
        )
        self.menu.open()
    
from head_image import HeadImage

Builder.load_string("""
<UserAndMessage>:
    orientation: "horizontal"
    adaptive_height: True
    #spacing: "10dp"  # 调整段之间的间距
    size_hint_x: 1 
    #md_bg_color:"white"
    message_data: root.message_data              
    head_image_data: root.head_image_data
""") 
class UserAndMessage(MDBoxLayout):
    message_data=DictProperty({})
    head_image_data=DictProperty({})
    message = ObjectProperty()
    head_image = ObjectProperty()
    def __init__(self, **kwargs):
        super(UserAndMessage,self).__init__(**kwargs)
        #print(kwargs)
        # self.message_data = kwargs.get("message_data", {'text':'默认文本',})
        # self.head_image_data = kwargs.get("head_image_data", {})
    def on_kv_post(self, *args):    
        self.message = Message(**self.message_data)
        self.head_image = HeadImage(**self.head_image_data)
        
        if self.message.identity == "User":
            self.add_widget(self.message)
            self.add_widget(self.head_image)
        else:
            self.add_widget(self.head_image)
            self.add_widget(self.message)

"""
目前在回收试图中遇到了多个子类加载后更新与数据传递出现异常的问题
目前有以下三种解决方法
1 继承回收试图的行为作为数据子类实现数据的自我监视更新
2 为了让字典类型的数据可以传入，将组合类变为一个继承类，更换头像的加载模式
3 放弃回收试图，转而使用基础的布局，并且后续尝试自己实现部分功能
"""

class ExampleApp(MDApp,CommonApp):
    def build(self):
        self.theme_cls.primary_palette = "Red"
        
        kwargs={
            'text':'[color=#ff0000]hello world[/color]\n    你好世界This is an indented line.[color=#ff0000][ref=hello]link[/ref][/color]aaa aaaa aaaaa aaaaa aaaaaa aaaaa aaaaa.This is an indented line.aaa1 aaa2a aaaa3a aaaaa4 aaaaaa5 aaaaa aaaaa.This is an indented line.aaa aaaa aaaaa aaaaa aaaaaa aaaaa aaaaa',
            'transition_text':"",
            'transition_position':'float',
            'transition_level':'sentence',
            'voice':'',
            'message_id':1,
            'is_new':False,
            'identity':'User',
            'chat_name':'User',
            'image_list':[],
        } 
        return Message(**kwargs)
    
class ExampleApp2(MDApp,CommonApp):
    def build(self):
        self.theme_cls.primary_palette = "Red"
        
        message_data={'text':'[color=#ff0000]hello world[/color]\n    你好世界This is an indented line.[color=#ff0000][ref=hello]link[/ref][/color]aaa aaaa aaaaa aaaaa aaaaaa aaaaa aaaaa.This is an indented line.aaa1 aaa2a aaaa3a aaaaa4 aaaaaa5 aaaaa aaaaa.This is an indented line.aaa aaaa aaaaa aaaaa aaaaaa aaaaa aaaaa',
            'transition_text':"122",
            'transition_position':'float',
            'transition_level':'sentence',
            'voice':'',
            'message_id':1,
            'is_new':False,
            'identity':'Ai',
            'chat_name':'User',
            'image_list':[]}
        head_image_data={'icon':'account',
            'identity':'User',
            'callback':lambda:print("No bind function")}
        
        kwargs={
            "message_data":message_data,
            "head_image_data":head_image_data
        }
        return UserAndMessage(**kwargs)
    
class ExampleApp3(MDApp,CommonApp):
    def build(self):
        self.theme_cls.primary_palette = "Red"
        
        kwargs={
            'text':'你好世界',
            'transition_text':"",
            'transition_position':'float',
            'transition_level':'sentence',
            'voice':'',
            'message_id':1,
            'is_new':False,
            'identity':'Ai',
            'chat_name':'User',
            'image_list':[],
        } 
        return Message(**kwargs)
    

"""
以下部分使用最简单粗暴的方式实现我需要的类
"""


if __name__ == '__main__':
    ExampleApp3().run()
    #