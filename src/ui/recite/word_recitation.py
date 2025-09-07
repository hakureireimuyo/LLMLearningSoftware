"""
该组件用于完成背诵单词所需要的所有完整功能

"""
from kivymd.uix.floatlayout import MDFloatLayout
import random
from collections import deque
import time
from ...components.custom.card.dictationcard import DictationCard
from ...components.custom.card.wordcard import WordCard
from ...components.custom.card.selectcard import QuizCard
from ...components.custom.card.spellingcard import WordInputCard
from kivy.animation import Animation
from kivymd.uix.boxlayout import MDBoxLayout
from global_instance import word_db
from kivy.properties import ListProperty, ObjectProperty, DictProperty,StringProperty
from kivy.lang import Builder

Builder.load_string('''
<ResultLabel>:
    orientation: "vertical"
    size_hint: 1,1
    padding: "10dp"
    spacing: "10dp"
    md_bg_color: app.theme_cls.backgroundColor
    MDBoxLayout:
        orientation: "vertical"
        size_hint: 1, 0.8
        padding: "10dp"
        spacing: "10dp"
        pos_hint: {"center_x": 0.5, "center_y": 0.5}
        MDLabel:
            text: root.use_time
            font_style: "STSONG"
            halign: "center"
            valign: "center"
            size_hint_y: None
            height: "50dp"
            md_bg_color: app.theme_cls.primaryContainerColor
        MDLabel:
            text: root.correct_count
            font_style: "STSONG"
            halign: "center"
            valign: "center"
            size_hint_y: None
            height: "50dp"
            md_bg_color: app.theme_cls.primaryContainerColor
        MDLabel:
            text: root.wrong_count
            font_style: "STSONG"
            halign: "center"
            valign: "center"
            size_hint_y: None
            height: "50dp"
            md_bg_color: app.theme_cls.primaryContainerColor
        MDLabel:
            text: root.accuracy
            font_style: "STSONG"
            halign: "center"
            valign: "center"
            size_hint_y: None
            height: "50dp"
            md_bg_color: app.theme_cls.primaryContainerColor
    # MDBoxLayout:
    #     orientation: "horizontal"
    #     spacing: "10dp"
    #     MDButton:   
    #         on_release: root.reset()
    #         radius: [0,0,0,0]
    #         MDButtonText:
    #             text: "重新开始"
    #             font_style: "STSONG"
    #             halign: "center"
    #             valign: "center"
    #     Widget: 
    #     MDButton:   
    #         on_release: root.reset()
    #         radius: [0,0,0,0]
    #         MDButtonText:
    #             text: "返回主界面"
    #             font_style: "STSONG"
    #             halign: "center"
    #             valign: "center"
<RecitationInterface>:
    orientation: "vertical"
    md_bg_color: app.theme_cls.backgroundColor
    MDBoxLayout:
        orientation: "vertical"
        
        MDNavigationBar:
            set_bars_color: True
            size_hint_y: None
            height: "56dp"
            padding: "12dp",0,"12dp",0
            elevation: 4
            MDNavigationItem:
                size_hint_x: None
                width: "64dp"
                on_release: root.end()
                MDNavigationItemIcon:
                    icon: "arrow-left-bold"
            Widget:
            MDLabel:
                text: "当前进度："+root.rate_str
                font_style: "STSONG"
                size_hint_x: None
                width: "300dp"
                valign: "center"
                halign: "left"
                size_hint_y: None
                height: "56dp"
                text_size: self.width, None
            Widget:
            MDNavigationItem:
                size_hint_x: None
                width: "64dp"
                on_release: root.back()
                MDNavigationItemIcon:
                    icon: "arrow-left-bold"
        MDDivider:
        MDBoxLayout:
            id: card_box

''')
class ResultLabel(MDBoxLayout):
    use_time = StringProperty()
    correct_count = StringProperty()
    wrong_count = StringProperty()
    accuracy = StringProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
from global_instance import db_manager
class CardManager(MDFloatLayout):
    current_cards = ListProperty()
    stats = DictProperty()  # 新增统计属性
    word_db = ObjectProperty()  # 新增数据库实例属性
    callback_set_rate = ObjectProperty(lambda: None)  # 新增设置进度回调函数
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.word_db = word_db
        self.base_word_list=[]
        self.raw_word_list = []#这个列表用于生成卡片，因此不能作为结算数据列表使用
        self.stats = {}
        self.card_queue = deque()
        self._init_default_callbacks()
        self.start_time =time.time()  # 记录开始时间
        self.rate=0
        self.count=0
        self.review_count=0 #自动将前几天错误的单词追加进入列表
        self.new_word_count=0 #新单词数量

    def _init_default_callbacks(self):
        # 统一回调处理
        self.swipe_horizontal_callback = self._handle_swipe
        self.swipe_vertical_callback = self._handle_swipe
        self.answer_correctly = self._handle_correct_answer
        self.answer_wrong = self._handle_wrong_answer

    def load_words(self, word_list):
        """热加载新单词列表"""
        self.reset()
        if len(word_list) == 0:
            self.error()
            return
        self.raw_word_list = word_list
        self.count=len(word_list)*4
        self.new_word_count=len(word_list)
        self._init_stats(word_list)
        self._init_card_queue()
        self._generate_initial_cards()
        self.set_parent_rate()

    def _init_card_queue(self):
        # 初始化卡片生成队列
        temp_queue = []
        
        # 第一阶段：所有单词生成WordCard
        for word_data in self.raw_word_list:
            temp_queue.append({
                'type': WordCard,
                'data': word_data
            })
        
        # 第二阶段：为每个单词生成其他卡片类型
        for word_data in self.raw_word_list:
            temp_queue.extend([
                {'type': WordInputCard, 'data': word_data},
                {'type': QuizCard, 'data': word_data},
                {'type': DictationCard, 'data': word_data}
            ])
        
        # 随机打乱顺序但保持WordCard在前
        word_cards = [c for c in temp_queue if c['type'] == WordCard]
        other_cards = [c for c in temp_queue if c['type'] != WordCard]
        random.shuffle(other_cards)
        self.card_queue = deque(word_cards + other_cards)

    def _generate_initial_cards(self):
        # 生成前两张卡片
        for _ in range(2):
            if self.card_queue:
                config = self.card_queue.popleft()
                self._create_card(config)
        #第一张卡片启用
        self.current_cards[0].disabled=False

    def _init_stats(self, word_list):
        """初始化统计信息"""
        self.stats = {
            word.get('id', ''): {'right': 0, 'wrong': 0}
            for word in word_list
        }

    def _create_card(self, config):
        """改进后的卡片创建方法"""
        card_type = config['type']
        word_data = config['data']
        
        # 生成卡片参数
        base_params = {
            'id': word_data.get('id', ''),
            'word': word_data.get('word', ''),
            'pronunciation': word_data.get('pronunciation', ''),
            'translation': word_data.get('translation', ''),
            'swipe_horizontal_callback': self.swipe_horizontal_callback,
            'swipe_vertical_callback': self.swipe_vertical_callback,
            'answer_correctly': self.answer_correctly,
            'answer_wrong': self.answer_wrong,
            'center': self.center,
            'pos': (self.center_x, self.center_y+3000),#避免闪烁，简单好用
        }

        # 特殊卡片处理
        if card_type==QuizCard:
            # 获取3个随机错误选项
            wrong_words = self.word_db.random_query('cet4lx', 3)
            #print(f"Wrong words: {wrong_words}")
            options = [word_data.get('translation', '')] + [
                w.translation for w in wrong_words
            ]
            random.shuffle(options)
            correct_index = options.index(word_data.get('translation', ''))
            
            base_params.update({
                'options': options,
                'correct_index': correct_index
            })
        elif card_type==DictationCard:
            # 获取3个随机错误选项
            wrong_words = self.word_db.random_query('cet4lx', 3)
            #print(f"Wrong words: {wrong_words}")
            options = [word_data.get('word', '')] + [
                w.get('word', '') for w in wrong_words
            ]
            random.shuffle(options)
            correct_index = options.index(word_data.get('word', ''))
            
            base_params.update({
                'options': options,
                'correct_index': correct_index
            })
        # 创建卡片实例
        card = card_type(**base_params)
        #先禁用
        card.disabled=True
        # 调整层级
        self._adjust_card_layer(card)
        return card

    def _adjust_card_layer(self, card):
        """调整卡片层级，最上层的卡片解除禁用"""
        index=len(self.current_cards)
        self.add_widget(card,index=index)
        self.current_cards.append(card)

    def _handle_swipe(self, instance):
        # 处理卡片划出
        self.current_cards.remove(instance)
        self.remove_widget(instance)
        
        # 生成新卡片
        if len(self.card_queue)>0:
            config = self.card_queue.popleft()
            self._create_card(config)
        
        # 保持两张卡片
        while len(self.current_cards) < 2 and self.card_queue:
            config = self.card_queue.popleft()
            self._create_card(config)

        if len(self.current_cards) == 0:
            self.end_of_quiz()
        #进度+1
        self.rate+=1
        self.set_parent_rate()
        #启用最上方的卡片
        if len(self.current_cards)>0:
            self.current_cards[0].disabled=False
            if type(self.current_cards[0])==DictationCard:
                self.current_cards[0].play_pronunciation()
            
    def _handle_correct_answer(self):
        """正确回答处理"""
        #print(self.stats)
        if type(self.current_cards[0])!=WordCard:
            current_word = self.current_cards[0].id
            self.stats[current_word]['right'] += 1
            print("答对了")

    def _handle_wrong_answer(self, word_data, card_type):
        """错误回答处理"""
        word = word_data.get('id', '')
        print(word)
        self.stats[word]['wrong'] += 1
        # 重新加入队列
        self.card_queue.append({
            'type': card_type,
            'data': word_data
        })
        # 追加到原始列表
        self.raw_word_list.append(word_data)
        #总数量+1
        self.count+=1
        self.set_parent_rate()

    def end_of_quiz(self):
        """结束时的处理"""
        print("Quiz ended. Statistics:", self.stats)
        # 计算用时
        end_time = time.time()
        total_time = end_time - self.start_time
        #转化为字符串
        total_time_str = f"{total_time:.2f}秒"
        # 这里可以添加结束时的逻辑，比如显示统计信息等
        # 统计信息处理
        stats_summary = self.get_stats_summary()
        print("Statistics Summary:", stats_summary)
        # 显示结果
        result_label = ResultLabel(
            use_time=f"用时: {total_time_str}",
            correct_count=f"正确: {stats_summary['right']}",
            wrong_count=f"错误: {stats_summary['wrong']}", 
            accuracy=f"准确率: {stats_summary['accuracy']*100:.2f}%"
        )
        result_label.reset_callback = self.reset  # 设置重置回调
        self.add_widget(result_label, index=0)
        #保存数据
        dao=db_manager.get_module_dao(['daily_study','study_plan'])
        with dao.transaction():
            study_plan_date=dao.study_plan.get_current_plan()
            if study_plan_date:
                id=study_plan_date.get('id')
                dao.daily_study.increment_today_stats(
                    study_plan_id=id,
                    question_count=self.count,
                    correct_count=stats_summary['right'],
                    wrong_count=stats_summary['wrong'],
                    wrong_word_id=[word_id for word_id, stat in self.stats.items() if stat.get('wrong', 0) > 2],
                    usage_time=int(total_time),
                    review_count=self.review_count,
                    new_word_count=self.new_word_count
                )
            #修改计划书的进度
            current_index=study_plan_date.get('current_index')
            dao.study_plan.update_progress(plan_id=id,current_index=current_index+self.new_word_count)

    def error(self):
        """错误处理"""
        # 显示错误信息
        error_label = ResultLabel(
            use_time="",
            correct_count="",
            wrong_count="没有单词可供复习",
            accuracy=""
        )
        error_label.reset_callback = self.reset
        self.add_widget(error_label, index=0)

    def get_stats_summary(self):
        """获取统计摘要"""
        total_right = sum(v['right'] for v in self.stats.values())
        total_wrong = sum(v['wrong'] for v in self.stats.values())
        accuracy = total_right / (total_right + total_wrong) if total_right + total_wrong > 0 else 0
        return {
            'total': len(self.raw_word_list),
            'right': total_right,
            'wrong': total_wrong,
            'accuracy': round(accuracy, 2)
        }
        
    def on_center(self, *args):
        """确保卡片居中"""
        for card in self.current_cards:
            card._update_center()
    def reset(self):
        """重置状态"""
        self.clear_widgets()
        self.current_cards.clear()
        self.card_queue.clear()
        self.stats.clear()

    def set_parent_rate(self):
        """获取进度"""
        if self.parent:
            self.callback_set_rate(f"{self.rate}/{self.count}")

from kivymd.uix.dialog import MDDialog    
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogIcon,
    MDDialogHeadlineText,
    MDDialogContentContainer,
    MDDialogButtonContainer,
)
from kivymd.uix.button import MDButton, MDButtonText
from kivy.uix.widget import Widget
from kivymd.uix.label import MDLabel

class RecitationInterface(MDBoxLayout):
    """
    背诵单词的界面
    """
    rate_str=StringProperty()
    callback=ObjectProperty(lambda: None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.dialog=MDDialog(
                MDDialogButtonContainer(
                MDBoxLayout(
                    MDLabel(
                    text="是否确认退出？部分数据会保存",
                    font_style="STSONG",
                    halign="center", 
                    valign="center",
                    ),
                MDBoxLayout(
                    MDButton(
                        MDButtonText(text="Cancel"),
                        style="text",
                        on_release=lambda x: self.cancel(),  # 绑定取消事件
                    ),
                    Widget(),  # 占位符
                    MDButton(
                        MDButtonText(text="Accept"),
                        style="text",
                        on_release=lambda x: self.close_dialog(),  # 绑定确认事件
                    ),
                size_hint=(None, None),
                size=("500dp", "200dp"),
                padding=("10dp", "10dp"),
                ),
                orientation="vertical",
                spacing="8dp",
                size_hint=(None, None),
                size=("500dp", "200dp"),
                padding=("10dp", "10dp"),
                ),
                spacing="8dp",
            ),
            )
        #self.manager.load_words(word_db.random_query('cet4lx', 5))
    
    def start(self, table_name, index,count):
        """
        加载单词
        params:
            table_name:单词表名称
            index:单词表索引
            count:单词数量
        """
        self.manager = CardManager(size_hint=(1,1),callback_set_rate=self.set_rate)
        self.ids.card_box.add_widget(self.manager)
        # print("背诵组件的数据")
        # print(self.size,self.pos,self.center)
        # print(self.ids.card_box.size,self.ids.card_box.pos,self.ids.card_box.center)
        #当前父级组件的大小不符合我的需求，导致以父级为准的card出现了问题
        word_list = word_db.batch_query(table_name, index,count)
        self.manager.load_words(word_list)
    
    def end(self):
        """
        收尾工作,接收数据，在数据库中处理
        """
        #self.manager.end_of_quiz()
        #检查答题是否完成
        if self.manager.count==self.manager.rate:
            self.ids.card_box.remove_widget(self.manager)
            self.back()
        else:
            self.dialog.open()
        pass

    def set_rate(self,rate_str):
        self.rate_str=rate_str

    def back(self):
        if self.callback:
            self.callback()

    def close_dialog(self):
        """关闭对话框，且调用返回函数"""
        self.dialog.dismiss()
        self.ids.card_box.remove_widget(self.manager)
        self.back()
    def cancel(self):
        """取消对话框"""
        if self.dialog:
            self.dialog.dismiss()

from kivymd.app import MDApp
class Example(MDApp):
    def build(self):
        # 示例单词数据
        # word_list = [
        #     {
        #         'word': 'Apple',
        #         'pronunciation': '/ˈæp.əl/',
        #         'translation': '苹果'
        #     },
        #     {
        #         'word': 'banana',
        #         'pronunciation': '/bəˈnɑːnə/',
        #         'translation': '香蕉'
        #     }
        # ]
        word_list = word_db.random_query('cet4lx', 1)
        # 创建卡片管理器
        manager = CardManager(
            size_hint=(1, 1)
        )
        manager.load_words(word_list)
        return manager

    def handle_error(self, word_data):
        print(f"需要复习的单词：{word_data['word']}")

class ExampleApp(MDApp):
    def build(self):
        return RecitationInterface()
if __name__ == '__main__':
    Example().run()