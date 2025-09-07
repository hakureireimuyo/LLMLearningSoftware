from datetime import datetime, timedelta
import sqlite3
import calendar
from kivymd.app import MDApp
from kivymd.uix.button import MDButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.boxlayout import MDBoxLayout
from global_instance import db_manager
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty, ColorProperty, ObjectProperty

Builder.load_string('''
<timeWidget>:
    md_bg_color:app.theme_cls.secondaryContainerColor
    orientation:'vertical'
    size_hint_x:1
    size_hint_y:None
    height:dp(160)
    #adaptive_height: True
    radius: [20,20,20,20]
    MDBoxLayout:
        orientation:'horizontal'
        size_hint_y:None
        height:dp(120)
        MDBoxLayout:
            orientation:'vertical'
            MDLabel:
                text: root.gregorian_date
                font_style: 'STSONG'
                role:"large"
                adaptive_height: True
                size_hint_y:None
                height:dp(90)
                valign: 'center'
                halign:'left'
                padding: dp(10)
            MDLabel:
                text: root.lunar_date
                font_style: 'STSONG'
                role:"medium"
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                size_hint_y:None
                height:dp(30)
                padding: dp(10)
        MDLabel:
            text: root.time_str
            font_style: 'STSONG'
            role:"medium"
            pos_hint: {'center_x': 0.5, 'center_y': 0.3}
            size_hint_y:None
            height:dp(120)
    MDBoxLayout:
        adaptive_height: True
        orientation:'horizontal'
        md_bg_color:app.theme_cls.backgroundColor
        padding: dp(10)
        size_hint_y:None
        height:dp(40)
        MDLabel:
            text: root.current_year_month_str
            font_style: 'STSONG'
            role:"medium"
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
            size_hint_y:None
            height:dp(40)
        MDIconButton:
            icon: 'chevron-left'
            on_release: root.last_month()
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        MDIconButton:
            icon: 'chevron-right'
            on_release: root.next_month()
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
<CalendarWidget>:
    #md_bg_color:app.theme_cls.backgroundColor
    start_color:app.theme_cls.primaryContainerColor
    end_color:app.theme_cls.primaryColor
    size_hint: None, None
    size: dp(600), dp(500)
''')


"""
以下实现了一些信息的悬浮显示
"""
from kivymd.uix.label import MDLabel
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.properties import NumericProperty

Builder.load_string("""
<HoverInfo>:
    md_bg_color: self.theme_cls.backgroundColor
    size_hint: None,None
    height: self.texture_size[1]
    text_size: self.width, None
    width:self.min_width
    markup: True
    radius:[10,10,10,10]
    halign:'left'
    valign:'top'
    font_style:"STSONG"
    role:"medium"
    allow_copy:True
""")
from kivy.metrics import sp,dp
from kivymd.uix.behaviors import HoverBehavior
from dateutil.relativedelta import relativedelta

class HoverInfo(MDLabel,HoverBehavior):
    max_width=NumericProperty(dp(200))
    min_width=NumericProperty(dp(50))
    fade_time = NumericProperty(2)  # 默认显示2秒
    event_dismiss=None
    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.text=text

    def show(self, pos):
        """显示信息面板并启动自动销毁定时器"""
        self.on_updata_width()
        x,y=pos
        x=x-self.width/2
        self.pos=(x,y)
        Window.add_widget(self)
        self.event_dismiss=Clock.schedule_once(self.dismiss, self.fade_time)
        # print(f"浮动面板size:{self.size}")
        # print(f"纹理大小:{self.texture_size}")

    def dismiss(self, dt):
        """移除面板"""
        Window.remove_widget(self)
    def on_enter(self, *args):
        '''
        The method will be called when the mouse cursor
        is within the borders of the current widget.
        '''
        if self.event_dismiss!=None:
            Clock.unschedule(self.event_dismiss)
            self.event_dismiss=None
        self.md_bg_color = self.theme_cls.primaryContainerColor

    def on_leave(self, *args):
        '''
        The method will be called when the mouse cursor goes beyond
        the borders of the current widget.
        '''
        if self.event_dismiss==None:
            self.event_dismiss=Clock.schedule_once(self.dismiss, self.fade_time/3)
        self.md_bg_color = self.theme_cls.backgroundColor
    def on_updata_width(self):
        def calculate_width(self):
            width = 0
            count=0
            max_width=0
            max_count=0
            for char in self.text:
                if char=="\n":
                    max_width=max(width,max_width)
                    max_count=max(count,max_count)
                    width=0
                    count=0
                count+=1
                char_size = self._label.get_extents(char)
                width += char_size[0]
                #print(char,"-",width,end="")
            max_width=max(width,max_width)
            max_count=max(count,max_count)
            #print(max_count,max_width)
            return max_width+dp(2)
        
        new_width = calculate_width(self)
        if new_width > self.max_width:
            self.width = self.max_width  # Set the width of the label
        else:
            if new_width < self.min_width:
                self.width = self.min_width  # Set the width of the label
            else:
                self.width = new_width  # Set the width of the label
        self.texture_update()  # Update the texture
                

#阴历计算库
from lunardate import LunarDate
class timeWidget(MDBoxLayout):
    """时间组件,自动更新时间"""
    time_str = StringProperty("")  # 用于绑定时间字符串
    gregorian_date = StringProperty("")  # 用于绑定日期字符串
    lunar_date = StringProperty("")  # 用于绑定农历日期字符串
    callabck_change_month=ObjectProperty(None)  # 回调函数
    current_year_month_str=StringProperty("")  #当前选择的月份
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        """初始化日期部分"""
        now = datetime.now()
        # 公历日期和星期
        self.gregorian_date = self._get_gregorian_str(now)
        # 农历日期
        self.lunar_date = self._get_lunar_str(now)
        #当前选择的月份
        self.current_year_month=datetime.now()  # 当前时间
        self.current_year_month_str = f"{self.current_year_month.year}年{self.current_year_month.month}月"
        # 组合初始日期字符串
        self.date_str = f"{self.gregorian_date}\n{self.lunar_date}"
        self.time_str = ""
        Clock.schedule_interval(lambda dt:self.update_time(), 1)  # 每秒更新一次
        self.update_time()  # 初始化显示

    def _get_gregorian_str(self, dt):
        """获取公历日期字符串：几月几日，星期几"""
        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        return f"{dt.month}月{dt.day}日，{weekdays[dt.weekday()]}"  # dt.weekday()返回0-6对应周一到周日

    def _get_lunar_str(self, dt):
        """获取农历日期字符串：几月初几"""
        lunar = LunarDate.fromSolarDate(dt.year, dt.month, dt.day)
        day_str = self._cn_lunar_day(lunar.day)
        return f"{lunar.month}月{day_str}"

    def _cn_lunar_day(self, day):
        """转换农历日为中文表述"""
        if 1 <= day <= 10:
            return f"初{self._num_to_cn(day)}"
        elif 11 <= day <= 19:
            return f"十{self._num_to_cn(day-10)}"
        elif day == 20:
            return "二十"
        elif 21 <= day <= 29:
            return f"廿{self._num_to_cn(day-20)}"
        elif day == 30:
            return "三十"
        return str(day)

    def _num_to_cn(self, num):
        """数字转中文（1-10）"""
        cn_numbers = {1: '一', 2: '二', 3: '三', 4: '四', 5: '五',
                      6: '六', 7: '七', 8: '八', 9: '九', 10: '十'}
        return cn_numbers.get(num, str(num))

    def update_time(self):
        """更新时间部分"""
        now = datetime.now()
        self.time_str = now.strftime("%H:%M:%S")
        #self.time_str = f"{self.date_str}\n时间：{time_part}"
        #print(self.time_str)

    def next_month(self):
        """下月按钮事件"""
        if self.callabck_change_month==None:return
        self.callabck_change_month(1)
        self.current_year_month+=relativedelta(months=1)  # 增加一个月
        self.current_year_month_str = f"{self.current_year_month.year}年{self.current_year_month.month}月"

    def last_month(self):
        """上月按钮事件"""
        if self.callabck_change_month==None:return
        self.callabck_change_month(-1)
        self.current_year_month+=relativedelta(months=-1)  # 减少一个月
        self.current_year_month_str = f"{self.current_year_month.year}年{self.current_year_month.month}月"

from kivymd.uix.behaviors import HoverBehavior
from kivy.graphics import Color, Rectangle
from kivymd.uix.behaviors import (
    CommonElevationBehavior,
    DeclarativeBehavior,
    RectangularRippleBehavior,
    BackgroundColorBehavior,
)
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.behaviors import ButtonBehavior
class MyDateButton(MDLabel,RectangularRippleBehavior,ButtonBehavior,HoverBehavior):
    """自定义日期按钮，支持悬停效果"""
    date_obj = None  # 存储日期对象，用于传递给点击事件
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.temp_color=(0,0,0,0)  # 叠加颜色
        self.r=None
        self.info=None

    def on_leave(self, *args):
        """鼠标离开时的处理函数"""
        if self.r!=None:
            Clock.unschedule(self.r)
        self.close_data()  # 关闭数据
        pass
    
    def on_enter(self, *args):
        """鼠标进入时的处理函数"""
        self.r=Clock.schedule_once(lambda dt:self.show_data(),0.3)
        pass

    def on_press(self):
        """点击事件处理"""
        if self.date_obj:
            # 调用回调函数并传递日期对象
            pass
            #print(f"Clicked on date: {self.date_obj}")

    def on_touch_down(self, touch):
        """处理触摸事件"""
        if self.collide_point(*touch.pos):
            # 处理触摸事件
            print(self.text)
            self.show_data()  # 显示数据
            return True
        return False
    def on_touch_up(self, touch):
        """处理触摸事件"""
        if self.collide_point(*touch.pos):
            # 处理触摸事件
            return True
        return False
    
    def show_data(self):
        """显示数据"""
        # 这里可以添加显示数据的逻辑
        self.info = HoverInfo("date")
        pos=[self.pos[0]+self.width/2,self.pos[1]+self.height]
        self.info.show(pos)  # 显示信息面板

    def close_data(self):
        """关闭数据"""
        if self.info!= None:
            self.info.dismiss(None)
        self.info = None  # 清除引用
        
class CalendarWidget(MDBoxLayout):
    """日历组件"""
    sp=5    # 间距属性
    start_color = ColorProperty((0.5, 0.5, 0.5, 1)) 
    end_color = ColorProperty((0.1, 0.5, 0.8, 1)) 
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.dao = db_manager.get_module_dao(['daily_study','study_plan'])

        self.current_time = datetime.now()  # 当前时间
        # 添加时间组件和网格
        self.add_widget(timeWidget(callabck_change_month=self.change_month))
        self._create_week_header()
        self.grid = MDGridLayout(
            size_hint=(1, 1),
            cols=7, rows=6,
            spacing=self.sp)
        
        self.add_widget(self.grid)
        #self._create_calendar_grid()
        Clock.schedule_once(lambda dt: self._create_calendar_grid())
        self.bind(size=self.on_size)
        Clock.schedule_once(self.update_size)
        #self.bing(start_color=self.change_color)

    def change_month(self, delta):
        """切换月份"""
        self.current_time += relativedelta(months=delta)
        self._create_calendar_grid()

    def _create_week_header(self):
        """创建周标题栏"""
        weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        theme_cls = MDApp.get_running_app().theme_cls
        header = MDBoxLayout(size_hint_x=1,adaptive_height=True,spacing=self.sp,md_bg_color=theme_cls.secondaryContainerColor)
        for day in weekdays:
            header.add_widget(MDLabel(text=day, size_hint_x=0.14,size_hint_y=None,height=50,font_style='STSONG',halign='center', valign='middle',role='medium'))
        self.add_widget(header)
                
    def _create_calendar_grid(self):
        """创建日历网格（基于current_time）"""
        # 获取当前视图时间
        current_time = self.current_time
        current_year = current_time.year
        current_month = current_time.month

        # 计算本月天数
        month_days = calendar.monthrange(current_year, current_month)[1]
        first_day = datetime(current_year, current_month, 1)
        
        # 修正偏移计算：周一为0，周日为6
        offset = first_day.weekday()  # 周一=0，周日=6

        with self.dao.transaction():
            self.grid.clear_widgets()
            plan_data = self.dao.study_plan.get_current_plan()
            if plan_data:
                study_plan_id = plan_data.get('id', None)  # 获取计划ID
            else:
                return
            # 填充前月日期（从周一开始）
            prev_day = first_day - timedelta(days=offset+1)  # 修正起始日
            for _ in range(offset):
                prev_day += timedelta(days=1)
                self._add_day_button(
                    day=prev_day.day,
                    is_current_month=False,
                    date_obj=prev_day
                )

            # 填充本月日期
            for day in range(1, month_days + 1):
                current_date = datetime(current_year, current_month, day)
                date_str = current_date.strftime("%Y-%m-%d")
                record = self.dao.daily_study.get_record_by_date(date_str,study_plan_id)
                heat = self._calculate_heat(record) if record else 0
                self._add_day_button(
                    day=day,
                    heat=heat,
                    date_obj=current_date
                )

            # 填充后月日期（补齐最后一行）
            next_day = datetime(current_year, current_month, month_days) + timedelta(days=1)
            while len(self.grid.children) % 7 != 0:
                self._add_day_button(
                    day=next_day.day,
                    is_current_month=False,
                    date_obj=next_day
                )
                next_day += timedelta(days=1)

    def _add_day_button(self, day, heat=0, is_current_month=True, date_obj=None):
        """添加日期按钮（增加颜色叠加）"""
        base_color = self._calculate_color(heat)
        
        # 非本月日期叠加灰色
        if not is_current_month:
            temp_color = base_color
            base_color=[temp_color[0]*0.7,temp_color[1]*0.7,temp_color[2]*0.7,temp_color[3]]

        btn = MyDateButton(
            text=str(day),
            halign='center',
            valign='middle',
            font_style='Title',
            role='medium',
            size_hint=(None, None),
            size=(int(self.grid.width/7)-self.sp, int(self.grid.height/5)-self.sp),
            md_bg_color=base_color,
            markup=True,  # 启用Markdown格式
            radius=[20,20,20,20],  # 圆角
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            
        )
        if date_obj and date_obj.date() == datetime.today().date():
            btn.text = f"[color=#ffffff]{day}[/color]"  # 标注当天日期
            # theme_cls = MDApp.get_running_app().theme_cls
            # base_color=theme_cls.primaryContainerColor
        self.grid.add_widget(btn)
    
    def change_color(self):
        """
        当主题颜色改变的时候，自动改变日历的颜色
        """
        pass
    
        #self._create_calendar_grid()
    def _calculate_heat(self, record):
        """优化热力计算"""
        if not record:
            return 0
            
        return (
            record['question_count'] * 1 +
            record['correct_count'] * 3 +
            record['usage_time'] // 60 * 2 -
            record['wrong_count'] * 0.5
        )

    def _calculate_color(self, heat):
        """计算热力颜色"""
        a = min(heat / 400, 1) if heat < 400 else 1
        return [
            self.start_color[i] * (1 - a) + self.end_color[i] * a
            for i in range(4)
        ]
    def on_size(self, *args):
        # 当窗口大小改变时重新创建日历
        Clock.schedule_once(self.update_size)

    def update_size(self,*args):
        for child in self.grid.children:
            child.size = (int(self.grid.width/7)-self.sp, int(self.grid.height/5)-self.sp)

class CalendarApp(MDApp):
    def build(self):
        return CalendarWidget()

if __name__ == '__main__':
    CalendarApp().run()