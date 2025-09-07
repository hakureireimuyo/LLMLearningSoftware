from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty
from kivy.metrics import dp
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivy.animation import Animation
Builder.load_string('''
<BaseCard>:
    padding: "4dp"
    size_hint: None, None
    size: "1000dp", "800dp"
    style:"elevated"
''')
KV='''
MDScreen:
    theme_bg_color: "Custom"
    md_bg_color: self.theme_cls.backgroundColor
    size_hint:1,1
    pos_hint: {"center_x":.5, "center_y":.5}
    # on_center:print(self.center)
    MyCard:
'''
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import NumericProperty, StringProperty
from kivymd.uix.card import MDCard
class BaseCard(MDCard):
    swipe_distance = NumericProperty(dp(600))
    swipe_time_threshold = NumericProperty(0.05)
    swipe_distance_threshold = NumericProperty(dp(35))

    #以下是基本数据，给继承类使用
    id=NumericProperty()
    word=StringProperty()
    translation=StringProperty()
    pronunciation=StringProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_center = (0, 0)  # 存储父容器中心坐标
        self.start_touch = (0, 0)
        self.start_time = 0
        self.is_swiping = False
        self.swipe_direction = None
        # self.swipe_left_callback = kwargs.pop('swipe_left_callback', None)
        # self.swipe_right_callback = kwargs.pop('swipe_right_callback', None)
        # self.swipe_up_callback = kwargs.pop('swipe_up_callback', None)
        # self.swipe_down_callback = kwargs.pop('swipe_down_callback', None)
        #self.center=self.parent.center if self.parent else (0, 0)
        self._is_animating = False
        self._scheduled_remove = None
        self.shake_count = 0  # 震动次数计数器
        Clock.schedule_once(self._update_center)  # 确保在布局完成后更新中心坐标

    def _update_center(self, *args):
        if self.parent:  # 确保父容器存在
            def update_center(dt):
                self.original_center = self.parent.center  # 更新父容器中心坐标
                self.center = self.original_center  # 确保初始位置准确
            Clock.schedule_once(update_center)  # 确保在布局完成后更新中心坐标

    def on_touch_down(self, touch):
        if self._is_animating:  # 阻止动画期间的新触摸
            return False
        if self.disabled:  # 阻止禁用状态下的触摸
            return False
        if self.collide_point(*touch.pos):
            super().on_touch_down(touch)
            touch.grab(self)
            
            # 获取父容器中心坐标
            parent_center = self.parent.center if self.parent else (0, 0)
            self.original_center = parent_center
            self.center = parent_center  # 确保初始位置准确
            
            # 记录触摸起始点（基于窗口坐标）
            self.start_touch = (touch.x, touch.y)
            self.start_time = touch.time_start
            self.is_swiping = False
            self.swipe_direction = None
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self._is_animating:  # 阻止动画期间的新触摸
            return False
        if self.disabled:  # 阻止禁用状态下的触摸
            return False
        if touch.grab_current is not self:
            return super().on_touch_move(touch)
        
        # 计算基于父容器中心的偏移量
        dx = touch.x - self.start_touch[0]
        dy = touch.y - self.start_touch[1]
        # print(dx,dy)
        # print(self.center)
        # print(self.original_center)
        if not self.is_swiping:
            elapsed_time = touch.time_update - self.start_time
            if elapsed_time > self.swipe_time_threshold:
                adx, ady = abs(dx), abs(dy)
                if adx > self.swipe_distance_threshold or ady > self.swipe_distance_threshold:
                    self.is_swiping = True
                    self.swipe_direction = 'horizontal' if adx > ady else 'vertical'
                
                    if self.swipe_direction == 'horizontal':
                        Animation.stop_all(self, 'y')
                        self.center_y = self.original_center[1]
                    else:
                        Animation.stop_all(self, 'x')
                        self.center_x = self.original_center[0]
        
        if self.is_swiping:
            if self.swipe_direction == 'horizontal':
                self.center_x =self.original_center[0]+ dx
                
            else:
                self.center_y =self.original_center[1] +dy
            return True
        
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self._is_animating:  # 阻止动画期间的新触摸
            return False
        if self.disabled:  # 阻止禁用状态下的触摸
            return False
        if touch.grab_current is not self:
            return super().on_touch_up(touch)
            
        dx = touch.x - self.start_touch[0]
        dy = touch.y - self.start_touch[1]
        
        if self.is_swiping:
            if self.swipe_direction == 'horizontal':
                if abs(dx) >= self.swipe_distance:
                    self._trigger_horizontal_swipe(dx > 0)
                    #print("调用了水平移除一次")
                else:
                    self._animate_back_to_center()
            else:
                if abs(dy) >= self.swipe_distance:
                    self._trigger_vertical_swipe(dy > 0)
                else:
                    self._animate_back_to_center()
        else:
            self.dispatch('on_release')
        
        touch.ungrab(self)
        return True

    def _animate_back_to_center(self):
        self._is_animating = True
        parent_center = self.parent.center if self.parent else self.original_center
        anim = Animation(center_x=parent_center[0],
                        center_y=parent_center[1],
                        duration=0.2,
                        t='out_quad')
        anim.bind(on_complete=self._reset_animation_state)
        anim.start(self)

    def _trigger_horizontal_swipe(self, is_right):
        if self._is_animating:
            return
        
        self._is_animating = True
        # callback = self.swipe_right_callback if is_right else self.swipe_left_callback
        # if callable(callback):
        #     callback(self)
        
        # 停止所有进行中的动画
        Animation.cancel_all(self)
        if self._scheduled_remove:
            self._scheduled_remove.cancel()

        target_x = 3000 if is_right else -3000
        anim = Animation(x=target_x, duration=0.2)
        #anim.bind(on_complete=self._safe_remove)   #移除卡片的操作在夫级中进行
        anim.start(self)

    def _trigger_vertical_swipe(self, is_up):
        if self._is_animating:
            return
        
        self._is_animating = True
        # callback = self.swipe_up_callback if is_up else self.swipe_down_callback
        # if callable(callback):
        #     callback(self)
        
        # 停止所有进行中的动画
        Animation.cancel_all(self)
        if self._scheduled_remove:
            self._scheduled_remove.cancel()

        target_y = 3000 if is_up else -3000
        anim = Animation(y=target_y, duration=0.2)
        #anim.bind(on_complete=self._safe_remove)
        anim.start(self)

    def _safe_remove(self, *args):
        if self.parent:
            self.parent.remove_widget(self)
        self._reset_animation_state()

    def _reset_animation_state(self, *args):
        self._is_animating = False
        if self._scheduled_remove:
            self._scheduled_remove.cancel()
            self._scheduled_remove = None
            
    def annimation_of_up_and_down_vibration(self,amplitude=30, shakes=3):
        self.shake_count = shakes
        self.orgnal_y=self.y
        self._do_shake_y(amplitude)

    def _do_shake_y(self, amplitude):
        if self.shake_count <= 0:
            return
        # 正向震动
        if self.shake_count==1:
            self._animate_back_to_center()
            return
        else:
            anim = Animation(y=self.orgnal_y + amplitude, duration=0.1)
            anim += Animation(y=self.orgnal_y - amplitude, duration=0.1)
        # 振幅衰减
        anim.on_complete = lambda dt: self._do_shake_y(amplitude * 0.6)
        self.shake_count -= 1
        anim.start(self)

    def annimation_of_left_and_right_vibration(self,amplitude=30, shakes=3):
        self.shake_count = shakes
        self.orgnal_x=self.x
        self._do_shake_x(amplitude)
        
    def _do_shake_x(self, amplitude):
        if self.shake_count <= 0:
            return
        # 正向震动
        if self.shake_count==1:
            self._animate_back_to_center()
            return
        else:
            anim = Animation(x=self.orgnal_x + amplitude, duration=0.1)
            anim += Animation(x=self.orgnal_x - amplitude, duration=0.1)
        # 振幅衰减
        anim.on_complete = lambda dt: self._do_shake_x(amplitude * 0.6)
        self.shake_count -= 1
        anim.start(self)

    def get_date(self):
        return {'id':self.id,'word':self.word,'pronunciation':self.pronunciation,'translation':self.translation}
    
    def get_type(self):
        return type(self)

class Example(MDApp):
    def build(self):
        return Builder.load_string(KV)

    # def on_start(self):
    #     self.root.ids.box.add_widget(MyCard(style="elevated", text="elevated"))
    #     #self.root.ids.box.add_widget(MyCard(style="elevated", text="elevated"))
if __name__ == '__main__':
    Example().run()