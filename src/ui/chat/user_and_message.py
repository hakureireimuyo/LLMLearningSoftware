from kivymd.uix.button import MDIconButton
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty,ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDButton,MDIconButton
from kivy.properties import StringProperty, NumericProperty, ListProperty, BooleanProperty
from kivy.properties import OptionProperty,DictProperty,ObjectProperty
import threading
from .common_app import CommonApp
from kivy.core.text import LabelBase
from kivy.lang import Builder
from kivy.metrics import sp,dp
from kivy.uix.label import Label
from kivymd.uix.label import MDLabel
from kivy.clock import Clock
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from ...components.common.textinteractorlabel.textinteractorlabel import CharDetectLabel
from global_instance import edge_tts
from global_instance import api_manager
tran=api_manager.create_instance("baidu_translate","text_translate")
Builder.load_string(
"""
<UserAndMessage>:
    orientation: "horizontal"
    size_hint: None,None
    height: self.minimum_height
    width: self.minimum_width
    
    MDBoxLayout:
        id:head_image_left
        orientation: "vertical"
        size_hint:None,None
        size: dp(40), dp(40)
        pos_hint: {"center_y":.5, "center_y":1}
        MDIconButton:
            id: head_image
            size_hint: None, None
            size: dp(40), dp(40)
            icon: root.icon
            on_release: root.on_head_image_press()
    MDBoxLayout:
        id:message_box
        orientation: "horizontal"
        size_hint: None,None
        height: self.minimum_height
        width: self.minimum_width
        # width: root.ids.text.width+dp(50)
        md_bg_color: app.theme_cls.onPrimaryColor if root.identity == "User" else app.theme_cls.onTertiaryContainerColor
        MDBoxLayout:
            id:message
            orientation: "vertical"
            adaptive_size: True
            
            CharDetectLabel:
                id:text_label
                text: root.text
                markup: True
                halign: "left"
                valign: "top"
                #md_bg_color:"green"
                font_style: "STSONG"
                role:"large"
                size_hint: None,None
                height: self.texture_size[1]
                text_size: self.width, None
                allow_selection: True
                allow_copy: True
                padding: 10, 0
                #on_copy: print("The text is copied to the clipboard") #MDLabe中可用
                #on_selection : print("The text is selected")
                line_height:1
                color:"black"
                split_str:" "
                radius:[dp(12),dp(12),dp(12),dp(12)]
                auto_updata:root.auto_update_text_layout
            MDDivider:
                id: divider
                size_hint_x: 0.98
                pos_hint: {'center_x': .5, 'center_y': .5}
                color: app.theme_cls.secondaryColor
                opacity: 0
            CharDetectLabel:
                id:transition_label
                text: root.transition_text
                markup: True
                halign: "left"
                valign: "top"
                font_style: "STSONG"
                role:"medium"
                size_hint_y: None
                height: self.texture_size[1]
                text_size: self.width, None
                radius:[dp(12),dp(12),dp(12),dp(12)]
                auto_updata:root.auto_update_text_layout

        MDBoxLayout:
            orientation: "vertical"
            adaptive_height: True
            size_hint_x:None
            width: "50dp"
            MDIconButton:
                on_release: root.open_menu(self)
                icon: "menu"
    MDBoxLayout:
        id:head_image_right
        orientation: "vertical"
        adaptive_height: True
        size_hint:None,None
        size: dp(40), dp(40)
        pos_hint: {"center_y":.5, "center_y":1}
        MDIconButton:
            id: head_image
            size_hint: None, None
            size: dp(40), dp(40)
            icon: root.icon
            on_release: root.on_head_image_press()
""")
from global_instance import pcm_player
baidutts=api_manager.create_instance("baidu_mind_cloud","tts")
class UserAndMessage(MDBoxLayout):
    #文本信息
    text=StringProperty()
    """
    该变量记录了消息中的所有文本信息，并且会被用于在MDLabe中进行渲染
    MDLabel中可以通过特殊格式实现文本的渲染，比如[color=#ff0000]红色[/color]
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
    #头像
    icon=StringProperty("account")
    """
    头像标签
    """
    #回调函数
    callback = ObjectProperty(None)
    """
    设置回调函数，用于在消息被点击的时候调用
    """
    #每条消息的最大宽度
    max_width=NumericProperty(dp(700))
    """
    通过数据与本类的函数回调实现数据更新时自动更新合适的文本宽度
    """
    #每条消息的最小宽度
    min_width=NumericProperty(dp(50))
    """
    通过数据与本类的函数回调实现数据更新时自动更新合适的文本宽度
    """
    #符号列表
    allowed_symbols = "!@#$%^&*()-_=+[]{}|;:',.<>?/"
    """
    用于粗略计算字符的宽度使用的,但是后来我知道了一种可以准确获取字符宽度的方法
    不过目前我不需要使用这个方法。
    """
    #没有超过最大宽度限制
    not_exceeded_maximum_width_limit=True
    """
    当文本数量超过最大限制的时候，后续不再计算宽度了，除非文本字体发生改变
    需要重新计算。
    """
    #自动更新文本布局
    auto_update_text_layout=BooleanProperty(True)
    """
    此处为为了给自定义具有鼠标选取文字功能的CharDetectLabel类的属性
    可以选择是否每当文本更新的时候就自动更新用于处理鼠标选取文本的布局信息
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #self.ids.message_box.md_bg_color=[1,1,1,1] if self.identity == "User" else [0.8,0.8,1.1]
        #print(kwargs)
        if kwargs.get("identity", None)=="User":
            self.remove_widget(self.ids.head_image_left)
            self.pos_hint={"right": 1, "center_y": .5}  
        else:
            self.remove_widget(self.ids.head_image_right)
            self.pos_hint={"center_x":0.01,"center_y":.5}
        
    def add_text(self,text):
        self.text += text

    def show_transition(self):
        def update_transition_text():
            if self.ids.divider.opacity == 0:
                self.transition_text=self.transition_text_copy
                self.ids.transition_label.opacity = 1
                self.ids.divider.opacity = 1
                print("1")
            else:
                print("2")
                self.ids.transition_label.opacity = 0
                self.ids.divider.opacity = 0
                self.transition_text = ''
            return False  # Return False to stop the Clock from rescheduling

        # Schedule the update on the main thread
        Clock.schedule_once(lambda dt: update_transition_text())

    def get_transition_text(self,instance,value):

        self.transition_text = tran.translate(self.text)
        self.transition_text_copy = self.transition_text
        self.show_transition()

    def on_transition_position(self, instance, value):
        pass

    def on_voice_get(self, instance, value):
        def tts():
            data=baidutts.synthesize_sync(self.text)
            pcm_player.play_pcm(data,16000)
        threading.Thread(target=tts).start()
        pass

    def on_transition_level(self, instance, value):
        pass

    async def tts(self):
        pass

    def text_appen(self,text_appen):
        """
        追加字符
        """
        self.text+=text_appen
        #print(self.text)
        pass

    def show_size(self):
        print(f"Text font size: {self.ids.text_label.font_size}")
        print(f"Transition font size: {self.ids.transition_label.font_size}")
        print(f"Message size: {self.size}")

    def print_it(self,instance, value):
        print("111")
        print('User click on', value)

    def change_font_size(self,value):
        print(self.ids.text_label.font_size)
        self.ids.text_label.font_size=self.ids.text_label.font_size+sp(value)
        self.ids.transition_label.font_size+=sp(value)
        print(self.ids.text_label.font_size)
        print(sp(value))

    def print(self):
        """
            输出:
                self.text: 文本内容
                self.image_list: 图片列表
                self.transition_text: 过渡文本
                self.transition_text_copy: 过渡文本副本
                self.transition_position: 过渡位置
                self.transition_level: 过渡级别
                self.voice: 语音内容
                self.message_id: 消息ID
                self.is_new: 是否为新消息
                self.identity: 身份标识
                self.chat_name: 聊天名称
        打印所有变量的值
        """
        print(f"text: {self.text}")
        print(f"image_list: {self.image_list}")
        print(f"transition_text: {self.transition_text}")
        print(f"transition_text_copy: {self.transition_text_copy}")
        print(f"transition_position: {self.transition_position}")
        print(f"transition_level: {self.transition_level}")
        print(f"voice: {self.voice}")
        print(f"message_id: {self.message_id}")
        print(f"is_new: {self.is_new}")
        print(f"identity: {self.identity}")
        print(f"chat_name: {self.chat_name}")
        print(f"root.size{self.size}")
    
    def set_head_image_callback(self, func):
        self.callback = func

    def on_head_image_press(self):
        if self.callback:
            self.callback()
        # No need to call super().on_press() as MDBoxLayout has no on_press method
        return  
      
    def open_menu(self, menu_button):
        menu_items = []
        for item, method in {
            "transition": lambda: self.get_transition_text(None,None),
            "vioce": lambda:self.on_voice_get(None,None),
            #"share to note": lambda: print("1"),
            #"delete message": lambda: print("1"),
            #"Add text": lambda:self.add_text("你好世界"),
            #"show size": lambda:self.show_size(),
            "print": lambda:self.print(),
            #"updata_text":lambda:self.updata_text(),
            "delete": lambda:self.delete_message(),
            #"color_rect": lambda:self.color_rect(),
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

    def show_error(self,e):
        print(e)
        self.text=str(e)

    def delete_message(self):
        if self.parent:
            self.parent.remove_widget(self)

    def color_rect(self):
        self.ids.text_label.color_rect_text()

class ExampleApp(MDApp,CommonApp):
    def build(self):
        self.theme_cls.primary_palette = "Red"
        kwargs={
            'text':'[color=#ff0000]hello world[/color]\n33adhoahdoauhdoauhd\n',
            'transition_text':"",
            'transition_position':'float',
            'transition_level':'sentence',
            'voice':'',
            'message_id':1,
            'is_new':False,
            'chat_name':'User',
            'image_list':[],
            'icon':'account',
            'identity':'Ai',
            'callback':lambda:print("No bind function")}
        temp=UserAndMessage(**kwargs)
        
        md=MDBoxLayout(
                md_bg_color=[1,1,1,1],
                orientation="horizontal",
                size_hint=(None,None),
                size=(dp(500),dp(500))
            )
        md.add_widget(MDButton(
            MDIconButton(icon="plus"),
            on_release=lambda x:temp.add_text("1239"),
            md_bg_color=[1,1,1,1],
            pos_hint={"center_x":.5,"center_y":.5}
        ))
        md.add_widget(temp)
        return md
    
class SingletonCounter:
        _instance = None
        _counter = 0

        def __new__(cls):
            if cls._instance is None:
                cls._instance = super(SingletonCounter, cls).__new__(cls)
            return cls._instance

        def get_next_value(self):
            value = self._counter
            self._counter += 1
            return value

    # Instantiate the singleton
counter_instance = SingletonCounter()

class UserAndMessageView(RecycleDataViewBehavior, UserAndMessage):
    key=NumericProperty()
    def __init__(self, **kwargs):
        super(UserAndMessageView, self).__init__(**kwargs)
        self.data = []
    def on_data(self, instance, value):
        self.data = value
        print("数据已更新")
if __name__ == '__main__':
    ExampleApp().run()