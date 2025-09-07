from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from kivymd.uix.pickers import MDModalDatePicker
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from global_instance import db_manager
from ...components.custom.clendary.clendary import CalendarWidget
from .today import TodayCard
from kivy.properties import StringProperty, ObjectProperty,BooleanProperty,NumericProperty
from kivy.metrics import dp
from .word_recitation import CardManager

Builder.load_string('''
<PlanBook>:
    padding: "4dp"
    size_hint: None, None
    size: "240dp", "100dp"
    # theme_shadow_color: "Custom"
    # shadow_color: "green"
    theme_bg_color: "Custom"
    md_bg_color: app.theme_cls.onTertiaryColor
    md_bg_color_disabled: "grey"
    theme_shadow_offset: "Custom"
    shadow_offset: (1, -2)
    theme_shadow_softness: "Custom"
    shadow_softness: 1
    theme_elevation_level: "Custom"
    MDRelativeLayout:
        #adaptive_height: True
        MDLabel:
            text: root.title
            font_style: 'STSONG'
            adaptive_height: True
            pos_hint: {'center_x': 0.6, 'center_y': 0.5}
        MDLabel:
            text:"总计："+root.count
            font_style: 'STSONG'
            role:'small'
            adaptive_height: True            
            pos_hint: {'center_x': 0.6, 'center_y': 0.1}
        MDIconButton:
            icon: 'book-open-variant'
            pos_hint: {'center_x': 0.9, 'center_y': 0.9}

<LitterItem>:
    size_hint: None, None
    size: dp(240), dp(200)
    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
    theme_bg_color:"Custom"
    md_bg_color:app.theme_cls.backgroundColor
    radius: [20,20,20,20]
    MDRelativeLayout:
        padding: dp(10), dp(10), dp(10), dp(10)
        MDLabel:
            text: root.title
            font_style: 'STSONG'
            role: 'medium'
            pos_hint: {'center_x': 0.5, 'center_y': 0.8}
        MDDivider:
            pos_hint: {'center_x': 0.5, 'center_y': 0.75}
        MDLabel:
            text: root.content
            font_style: 'Display'
            role:'medium'
            valign: 'middle'
            halign: 'center'
            pos_hint: {'center_x': 0.5, 'center_y': 0.3}
        MDLabel:
            text: root.count
            font_style: 'STSONG'
            role:'small'
            pos_hint: {'center_x': 0.6, 'center_y': 0.1}         
<PlanSelectionButton>:
    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
    size_hint:None,None
    size:dp(300),dp(200)
    MDLabel:
        text:root.text
        style:"text"
        font_style: 'STSONG'         
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        halign: 'center'
        valign: 'middle'
<WordPlanPage>:
    md_bg_color:app.theme_cls.surfaceContainerColor
    MDBoxLayout:
        orientation:'vertical'
        padding: dp(10)
        spacing: dp(10)
        MDBoxLayout:
            size_hint: 1,None
            height: dp(600)
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
            Widget:
            CalendarWidget:
                id:calendar_widget
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                size_hint: None, None
                size: dp(600), dp(500)
            MDBoxLayout:
                orientation:'vertical'
                size_hint: None, None
                size: dp(600), dp(500)
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                padding: dp(10), dp(10), dp(10), dp(10)
                spacing: dp(50)
                MDBoxLayout:
                    orientation:'horizontal'
                    size_hint: None, None
                    size: dp(500), dp(200)
                    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                    spacing: dp(20)
                    LitterItem:
                        title:'单词书'
                        content:root.plan_word_table
                        count:root.word_count  
                        callback:root.create_new_plan
                    LitterItem:
                        title:'进度'
                        content:root.rate_of_plan
                        count:root.date
                        callback:root.show_rate
                TodayCard:
                    id:today_card
                    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                    size_hint_x: None
                    width: dp(500)
                    review_count:root.review_count
                    new_word_count:root.new_word_count
                    learing_time:root.learing_time
                    completed_count:root.completed_count
            Widget:
        MDDivider:
            height: dp(1)
        MDBoxLayout:
            orientation:'horizontal'
            size_hint: 1, None
            height: dp(200)
            #size: dp(600), dp(200)
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
            spacing: dp(20)
            Widget:
            PlanSelectionButton:
                callback:root.load_data
            WordModelButton:
                title:'开始学习'
                content:""
                callback:root.start_learning
            Widget:
        Widget:
<WordModelButton>:
    size_hint:None,None
    size:dp(300),dp(200)
    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
    id:button
    md_bg_color:app.theme_cls.secondaryColor
    MDRelativeLayout:
        padding: dp(10), dp(10), dp(10), dp(10)
        MDLabel:
            text:root.title
            style:"text"
            font_style: 'STSONG'
            valign:'middle'
            halign: 'center'
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        MDLabel:
            text:root.content
            style:"text"
            font_style: 'STSONG'
            role:'small'
            pos_hint: {'center_x': 0.5, 'center_y': 0.3}
<FinalInterface>:
    md_bg_color:app.theme_cls.surfaceContainerColor
    size_hint:1,1
    MDScreenManager:
        id:screen_manager
        MDScreen:
            name:'plan_page'
            WordPlanPage:
                id:plan_page
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                size_hint:1,1
                callback:root.start_learning
        MDScreen:
            name:'word_page'
            size_hint:1,1
            RecitationInterface:
                id:card_manager
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                size_hint:1,1
                callback:root.back
''')
class LitterItem(MDCard):
    title=StringProperty()
    content=StringProperty()
    count=StringProperty()
    callback=ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_touch_down(self, touch):
        #print(f"on_touch_down{self.id}")
        if self.collide_point(*touch.pos):
            if self.callback:
                self.callback()

class WordModelButton(MDCard):
    callback=ObjectProperty(None)
    title=StringProperty()
    content=StringProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_touch_down(self, touch):
        #print(f"on_touch_down{self.id}")
        if self.collide_point(*touch.pos):
            if self.callback:
                self.callback()
class PlanBook(MDCard):
    title = StringProperty()
    org_title = StringProperty()
    count = StringProperty()
    selected = BooleanProperty(False)
    callback=ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(selected=self.on_select)
        self.org_title=self.title
        if self.title=="cet4lx":
            self.title="四级乱序版"
        if self.title=="cet6lx":    
            self.title="六级乱序版"
        if self.title=="cet4":
            self.title="四级"
        if self.title=="cet6":
            self.title="六级"
        if self.title=="gk":
            self.title="高考"
        if self.title=="gre":
            self.title="GRE"
        if self.title=="toefl":
            self.title="托福"
        if self.title=="ielts":
            self.title="雅思"
        if self.title=="zk":
            self.title="中考"

    def on_press(self):
        super().on_press()
        if self.callback:
            self.callback(self)
        #self.selected = not self.selected

    def on_select(self,*arges):
        """更新卡片的颜色"""
        #print(f"on_select{self.id}更新{self.selected}")
        self.update_colors()

    def update_colors(self):
        if self.selected:
            self.elevation = 4
            self.md_bg_color =MDApp.get_running_app().theme_cls.secondaryColor
            self.line_color = [1,1,1,1]
            #print(self.elevation,self.md_bg_color,self.line_color)
        else:
            self.elevation = 0
            self.md_bg_color = MDApp.get_running_app().theme_cls.onTertiaryColor
            self.line_color = [0.8, 0.8, 0.8, 1]
            #print(self.elevation,self.md_bg_color,self.line_color)
    

from global_instance import word_db
from kivymd.uix.stacklayout import MDStackLayout
Builder.load_string('''
<PlanBooks>:
    size_hint: None,None
    size: "500dp", "700dp"
    MDScrollView:
        do_scroll_x: False
        do_scroll_y: True
        MDStackLayout:
            orientation:"lr-tb"
            id: plan_container
            adaptive_height: True
            spacing: "12dp"
            pos_hint: {"center_x": .5,"center_y": .5}
<WordBooks>:
    size_hint: None,None
    size: "500dp", "500dp"
    MDScrollView:
        do_scroll_x: False
        do_scroll_y: True
        MDStackLayout:
            orientation:"lr-tb"
            id: plan_container
            adaptive_height: True
            spacing: "12dp"
            pos_hint: {"center_x": .5,"center_y": .5}              
            
''')
from global_instance import db_manager

class PlanBooks(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #self.date=word_db.get_all_stats()
        #print(self.date)
        self.dao=db_manager.get_module_dao("study_plan")
        with self.dao.transaction():
            self.date=self.dao.study_plan.get_user_plans()
        #print(self.date)
        for date in self.date:
            self.ids.plan_container.add_widget(PlanBook(title=date.get('wordlist_name'), count=str(date.get('word_count')),callback=self.select_plan))
        #self.ids.plan_container.add_widget(PlanBook(title='CET4', count='12'))
    def select_plan(self,instance):
        for child in self.ids.plan_container.children:
            child.selected=False
        instance.selected=True
        pass

#现在只看这个
class WordBooks(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.date=word_db.get_all_stats()
        self.current_plan=None
        for key, value in self.date.items():
           #print(key, value.word_count)
            if value.word_count==0:
                continue
            self.ids.plan_container.add_widget(PlanBook(title=key, count=str(value.word_count),callback=self.select_plan))
    
    def select_plan(self,instance):
        for child in self.ids.plan_container.children:
            child.selected=False
        instance.selected=True
        self.current_plan=instance

from kivymd.uix.dialog import (
    MDDialog,
    MDDialogIcon,
    MDDialogHeadlineText,
    MDDialogContentContainer,
    MDDialogButtonContainer,
)
from kivymd.uix.button import MDButton, MDButtonText
from kivy.uix.widget import Widget
from kivymd.uix.dialog import MDDialog
class PlanDialog(MDDialog):
    callback=ObjectProperty(None)
    def __init__(self,is_plan,**kwargs):
        self.content_container = MDDialogContentContainer()  # 创建内容容器
        if is_plan:
            self.plan_books = WordBooks()  # 你的自定义内容组件
        else:
            self.plan_books = WordBooks()  # 你的自定义内容组件
        self.content_container.add_widget(self.plan_books)  # 将内容添加到容器
        # ---------------------------- 构造对话框 ----------------------------
        super().__init__(
            # ---------------------------- Icon ----------------------------
            MDDialogIcon(icon="refresh"),
            # ----------------------- Headline text ------------------------
            MDDialogHeadlineText(text="Select a plan book"),
            # ----------------------- Content container --------------------
            self.content_container,
            # --------------------- Button container -----------------------
            MDDialogButtonContainer(
                Widget(),  # 左边留空
                MDButton(
                    MDButtonText(text="Cancel"),
                    style="text",
                    on_release=lambda x: self.on_cancel(),  # 绑定取消事件
                ),
                MDButton(
                    MDButtonText(text="Accept"),
                    style="text",
                    on_release=lambda x: self.on_accept(),  # 绑定确认事件
                ),
                spacing="8dp",
            ),
            **kwargs
        )

    def on_accept(self, *args):
        #确认选择，更新数据
        #print("确认选择")
        title=self.plan_books.current_plan.org_title
        count=self.plan_books.current_plan.count
        #print(title,count)
        dao=db_manager.get_module_dao("study_plan")
        with dao.transaction():
            dao.study_plan.create_study_plan(word_count=count,wordlist_name=title,is_current=1)
        if self.callback:
            self.callback(title)
        return super().dismiss(*args)
    
    def on_cancel(self,*args):
        #取消选择，恢复到之前的状态
        #print("取消选择")
        return super().dismiss(*args)
    
    def on_dismiss(self, *args):
        #对话框关闭时，移除对话框
        super().on_dismiss(*args)
        
class SelectPlanDialog(MDDialog):
    callback=ObjectProperty(None)
    def __init__(self,callback,number,count,**kwargs):
        # print(self.callback)
        self.callback=callback
        self.count=count
        self.number=number
        self.slider=MDSlider(
                        MDSliderHandle(
                        ),
                        MDSliderValueLabel(
                        ),
                        id="slider",
                        step=5,
                        value=number,
                        min=5,
                        max=100,
                    )
        self.lb=MDLabel(
                        text="背完需要"+str(int(count/number)+1)+"天",
                        font_style="STSONG",
                        role="medium",
                        pos_hint={"center_x":.5, "center_y":.5},
                    ) 
        super().__init__(
            MDDialogIcon(icon="refresh"),
            MDDialogButtonContainer(
                MDBoxLayout(
                    MDBoxLayout(
                        MDLabel(
                        text="请选择每日计划背诵单词的数量",
                        font_style="STSONG",
                        role="medium",
                        pos_hint={"center_x": .5, "center_y": .5},
                    ),
                    self.lb,
                    self.slider,
                        orientation='vertical',
                        size_hint_y=None,
                        height=dp(300),
                    ),
                    MDBoxLayout(    
                        MDButton(
                            MDButtonText(text="Cancel"),
                            style="text",
                            on_release=lambda x: self.cancel(),  # 绑定取消事件
                        ),  
                        MDButton(
                            MDButtonText(text="Accept"),
                            style="text",
                            on_release=lambda x: self.accept(),  # 绑定确认事件 
                        ),
                    orientation="horizontal",
                    ),
                orientation="vertical",
                size_hint_y=None,
                height=dp(408), 
                )
            )
        )
        self.slider.bind(value=self.update_lb)

    def update_lb(self,*args):
        print(self.slider.value)
        self.lb.text="背完需要"+str(int(self.count/self.slider.value)+1)+"天"

    def cancel(self,*args):
        return super().dismiss(*args)
    
    def accept(self,*args):
        if self.callback:
            self.callback(self.slider.value)
        return super().dismiss(*args)

from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.button import MDButton, MDButtonText
class PlanSelectionButton(MDCard):
    text = StringProperty()
    callback=ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        dao=db_manager.get_module_dao("study_plan")
        with dao.transaction():
            result=dao.study_plan.get_current_plan()
        if result:
            self.text=result.get('wordlist_name','未能获取计划')
        else:
            self.text='当前未选择\n任何计划'

    def on_touch_down(self, touch):
        #print(f"on_touch_down{self.id}")
        if self.collide_point(*touch.pos):
            PlanDialog(True,callback=self.set_text).open()
    
    def set_text(self, text):
        self.text = text
        if self.callback:
            self.callback()

from  datetime import datetime
from kivymd.uix.label import MDLabel
from kivymd.uix.slider import MDSlider,MDSliderHandle,MDSliderValueLabel
class WordPlanPage(MDBoxLayout):
    plan_word_table =StringProperty('')
    word_count = StringProperty('')
    rate_of_plan = StringProperty('')
    date = StringProperty('')
    callback=ObjectProperty(None)
    quantity=NumericProperty(0)
    #today的数据
    review_count = StringProperty('')
    new_word_count = StringProperty('')
    learing_time = StringProperty('')
    completed_count = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dao=db_manager.get_module_dao(["study_plan","daily_study"])
        self.load_data()

    def load_data(self):    
        with self.dao.transaction():
            result=self.dao.study_plan.get_current_plan()
        if result:
            self.plan_word_table=result.get('wordlist_name','未能获取计划')
            word_count=result.get('word_count','0')
            self.word_count=str(word_count)+"个"
            rate_of_plan=result.get('current_index','0')
            self.quantity=result.get('quantity',0)
            if word_count==0:
                self.rate_of_plan='0%'
            else:
                self.rate_of_plan=f"{rate_of_plan/word_count*100:.2f}%"
            date_str = result.get('created_time','2000-01-01 00:00:00')
            past_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').date()
            current_date = datetime.now().date()
            self.date="已经过去"+str(abs((current_date - past_date).days))+"天"
        else:
            self.plan_word_table='当前未选择\n任何计划'
            self.word_count='0个'
            self.rate_of_plan='0%'
            self.rate_of_plan_count='0%'
            self.date='未知'
        #today的数据
        study_plan_id=result.get('id',None)
        #print(result)
        today_data=self.dao.daily_study.get_today_stats(study_plan_id)
        print("获取今日数据")
        print(today_data)
        if today_data:
            self.review_count="复习单词"+str(today_data.get('review_count',0))+"个"
            self.new_word_count="新学单词"+str(today_data.get('new_word_count',0))+"个"
            self.learing_time="今日学习"+str(int(today_data.get('usage_time',0)/60))+"分钟"
            self.completed_count="今日答题"+str(today_data.get('question_count',0))+"个"
        else:
            self.review_count="复习单词0个"
            self.new_word_count="新学单词0个"
            self.learing_time="今日学习0分钟"
            self.completed_count="今日答题0个"

    def start_learning(self):
        if self.callback:
            self.callback()

    def create_new_plan(self):
        with self.dao.transaction():
            result=self.dao.study_plan.get_current_plan()
        if result:
            quantity=result.get('quantity',0)
            count=result.get('word_count',0)
        else:
            quantity=0
            count=0
        SelectPlanDialog(callback=self.set_number,number=quantity,count=count).open()
        
    def set_number(self,number):
        with self.dao.transaction():
            result=self.dao.study_plan.get_current_plan()
            study_plan_id=result.get('id',None)
            self.dao.study_plan.update_quantity(plan_id=study_plan_id,quantity=number)

    def show_rate(self):
        pass
class FinalInterface(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def start_learning(self):
        #首先获取用户的计划书数据
        dao=db_manager.get_module_dao("study_plan")
        with dao.transaction():
            result=dao.study_plan.get_current_plan()
        if result:
            self.ids.card_manager.start(result.get('wordlist_name','cet4lx'),result.get('current_index',0),result.get('quantity',10))
            self.ids.screen_manager.current='word_page'
        else:
            print("未获取到计划")

    def back(self):
        self.ids.screen_manager.current='plan_page'
        self.ids.plan_page.load_data()

from kivymd.app import MDApp
class TestApp(MDApp):
    def build(self):
        return FinalInterface()
        #return WordPlanPage(plan_word_table = 'CET4',rate_of_plan = '0.4%',rate_of_plan_count = '3342',word_count = '12')
    
if __name__ == '__main__':
    TestApp().run()
