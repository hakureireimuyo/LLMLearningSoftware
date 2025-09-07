"""
本模块用于显示一个数据的统计结果
主要是呈现一个单词的出现过的频率
初始化会从数据库加载
也会回写进数据库
为了避免过多组件同时加载，当组件第一次启动的时候
只会从数据库中读取一定量的数据传入，随着用户的下滑行为，
再不断地从数据库中进行读取。
"""

from kivymd.uix.recyclegridlayout import RecycleGridLayout
from kivymd.uix.recycleview import MDRecycleView
from kivymd.uix.refreshlayout import MDScrollViewRefreshLayout
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, BooleanProperty, ListProperty, DictProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivymd.app import MDApp
from global_instance import wd,sd
from kivy.metrics import dp
from kivy.clock import Clock
from core.tools.extract_words import count_words

Builder.load_string("""
<TasBox>:
    text: root.tag
    size_hint:None, None
    size:30,20
    role: "medium"
    font_style: "STSONG"
    halign: "center"
    valign: "center"
    pos_hint: {"center_x": 0.5, "center_y": 0.5}

<WordComponent>:
    padding: "4dp", 0, "4dp", 0
    orientation: "horizontal"
    md_bg_color: app.theme_cls.secondaryContainerColor
    padding:12,0,12,0
    MDBoxLayout:
        orientation: "vertical"
        size_hint_x:None
        width: "220dp"
        MDLabel:
            text: root.word+"  /"+root.phonetic+"/"
            font_style: "ARIAL"
            role: "medium"
            size_hint_x:None
            size_hint_y:None
            height:"60dp"
            width: "220dp"
            halign: "left"
            valign: "center"
        MDDivider:
        ExchangList:
            size_hint_x:None
            size_hint_y:1
            width: "220dp"
            md_bg_color: app.theme_cls.secondaryContainerColor
            exchange: root.exchange
            orientation:"vertical"
            #orientation:"lr-tb"
            MDLabel:
                text:root.exchange
    MDLabel:
        text: root.translation
        md_bg_color: app.theme_cls.primaryContainerColor
        font_style: "STSONG"
        role: "small"
        size_hint_x: 1
        size_hint_y: 1
        halign: "left"
        valign: "center"     
        
    MDBoxLayout:
        orientation: "vertical"
        size_hint_y: 1
        size_hint_x: None
        width:"200dp"
        padding:dp(12),0,dp(12),0
        MDLabel:
            text: "看:"+str(root.see)+"|"+"听:"+str(root.listen)+"|"+"用:"+str(root.use)+"|"+"译:"+str(root.translate)
            font_style: "STSONG"
            role: "small"
            # size_hint_y:None
            # height: "30dp"
            # size_hint_x:None
            # width: "30dp"
            size_hint_y:None
            height:"60dp"
            halign: "center"
            valign:"center"
        MDDivider:
        TagsListBox:
            tags: root.tags
            size_hint_y:1
            id:tags_box_layout
            spacing: "4dp"
            orientation:"lr-tb"
            MDLabel:
                text:root.tags
                
<WordList>:
    viewclass: "WordComponent"
    md_bg_color: app.theme_cls.backgroundColor
    lock_swiping: True
    RecycleBoxLayout:
        default_size: None, dp(120)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
        spacing: dp(12)
""")
class TagBox(MDLabel):
    tag=StringProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_style="STSONG"
        self.role="small"
        self.valign="center"
        self.halign="center"
        self.size_hint=(None, None)
        self.size=(40, 30)
        self.pos_hint={"center_x": 0.5, "center_y": 0.5}
        self.text_color=(1,1,1,1)
        if self.tag=="zk":
            self.text='中'
            self.md_bg_color=(0.416, 0.173, 0.439,1)
        elif self.tag=="gk":
            self.text='高'
            self.md_bg_color=(0.722, 0.231, 0.369,1)
        elif self.tag=="ky":
            self.text='研' 
            self.md_bg_color=(0.941, 0.541, 0.365,1)
        elif self.tag=="cet4":
            self.text='四'
            self.md_bg_color=(0.976, 0.929, 0.412,1)
        elif self.tag=="cet6":
            self.text='六'
            self.md_bg_color=(0.988, 0.729, 0.827,1)
        elif self.tag=="toefl":
            self.text='托'
            self.md_bg_color=(0.667, 0.588, 0.855,1)
        elif self.tag=="ielts":
            self.text='雅'
            self.md_bg_color=(0.659, 0.847, 0.918,1)
        elif self.tag=="gre":
            self.text='宝'
            self.md_bg_color=(0.027, 0.408, 0.624,1)
        else:
            self.text='error'
            self.md_bg_color=(0.5, 0.5, 0.5,1)

from kivymd.uix.stacklayout import MDStackLayout
class TagsListBox(MDStackLayout):
    tags=StringProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_style="STSONG"
        self.role="small"
        self.valign="center"
        self.halign="center"
        self.size_hint=(1, 1)
        #self.size=(40, 30)
        self.pos_hint={"center_x": 0.5, "center_y": 0.5}
        self.loaded = False
        self.add_tag()
        #self.bind(tags=self.add_tag)

    def add_tag(self):
        # print("---------------")
        #print(value)
        # print(self.tags)
        # print(self.tags.split())
        if self.loaded and self.tags!= None:
            return
        if self.tags != None:
            for tag in self.tags.split():
                tag_box = TagBox(tag=tag)
                self.add_widget(tag_box)
        self.loaded = True

class Exchange(MDLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.font_style="STSONG"
        self.role="small"
        self.valign="center"
        self.halign="left"
        self.size_hint=(None, None)
        self.size=(100, 20)
        

class ExchangList(MDBoxLayout):
    exchange=StringProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loaded = False
        #self.bind(exchange=self.add_exchange)

    def add_exchange(self,instance,value):
        # print(self.exchange)
        # print(self.exchange.split('/'))
        if self.loaded:
            return
        print(self.exchange)
        for exchange in self.exchange.split('/'):
            _exchange = Exchange(text=exchange)
            self.add_widget(_exchange)
        self.loaded = True

class WordComponent(MDBoxLayout):
    """
    一个单词组件
    """
    word = StringProperty()
    translation = StringProperty()
    exchange = StringProperty()
    tags = StringProperty()
    phonetic=StringProperty()
    translate=NumericProperty(-1)
    use=NumericProperty(-1)
    listen=NumericProperty(-1)
    see=NumericProperty(-1)
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

class WordList(MDRecycleView):
    _load_trigger = None                   # 加载触发器
                           # 每次加载的数量
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.batch_size = 8
        self.get_data()


    def get_data(self):
        data_1=wd.get_statistics(self.batch_size)
        data_id=[data[1] for data in data_1]
        #print(data_id)
        data=sd.query_batch_partial_data(data_id)
        #print(data)
        # print(data_1)   
        for dict_item, data_item in zip(data, data_1):
            translate, use, listen, see = data_item[-4:]
            dict_item.update({"translate": translate, "use": use, "listen": listen, "see": see})
            #print(dict_item)
            self.data.append(dict_item)
        #self.data.extend(data)

    def on_touch_move(self, touch):
        super().on_touch_move(touch)
        #print(self.scroll_y, abs(touch.oy - touch.y), self.scroll_distance)
        scroll_distance=dp(100)
        if self.scroll_y < 0 and abs(touch.oy - touch.y) > scroll_distance:
            if abs(touch.ox - touch.x) < scroll_distance:
                self.schedule_load(False)
                return True
        if self.scroll_y > 1 and abs(touch.oy - touch.y) > scroll_distance:
            if abs(touch.ox - touch.x) < scroll_distance:
                self.schedule_load(True)
                return True
        return False
    
    def resart_load(self):
        self.data=[]
        data_1=wd.get_statistics(self.batch_size,True)
        data_id=[data[1] for data in data_1]
        data=sd.query_batch_partial_data(data_id)
        for dict_item, data_item in zip(data, data_1):
            translate, use, listen, see = data_item[-4:]
            dict_item.update({"translate": translate, "use": use, "listen": listen, "see": see})
        self.data.extend(data)

    def schedule_load(self,check=False):
        """ 调度加载任务 """
        # 取消之前的未执行任务
        if self._load_trigger:
            self._load_trigger.cancel()
        # 创建新的延迟任务
        if check:
            self._load_trigger = Clock.schedule_once(lambda dt: self.resart_load(), 1)
        else:
            self._load_trigger = Clock.schedule_once(lambda dt: self.get_data(), 1)

    def add_word(self,id):
        """
        添加一个单词
        通过id从数据库中读取单词
        """
        data_test={
            "word":"perceive",
            'phonetic':"pə'si:v",
            "translation":"v. 感觉; 认识, 理解; 察觉到, 意识到, 注意到",
            "exchange":"d:perceived/p:perceived/3:perceives/i:perceiving",
            "tags":"cet4 cet6 ky toefl ielts",
            "translate" :1,
            "use":1,
            "listen":1,
            "see":1
        }
        #print("添加单词")
        self.data.append(data_test)
        
class WordStatisticsPage(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class Example(MDApp):
    def build(self):
        return WordList()
    def on_start(self):
        pass

if __name__ == '__main__':
    Example().run()