from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
from kivy.animation import Animation
from kivy.properties import NumericProperty
from kivy.clock import Clock
import random
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout

class AnimatedRectangle:
    """表示一个带有动画的矩形对象"""
    def __init__(self, widget):
        # 随机大小
        self.width = random.randint(30, 120)
        self.height = random.randint(30, 120)
        
        # 随机位置 - 确保在窗口内
        self.pos_x = random.randint(0, int(Window.width - self.width))
        self.pos_y = random.randint(0, int(Window.height - self.height))
        
        # 随机颜色
        self.color = (
            random.random(), 
            random.random(), 
            random.random(), 
            1
        )
        
        # 创建图形对象
        with widget.canvas:
            # 创建颜色对象
            self.col = Color(*self.color)
            # 创建矩形对象
            self.rect = Rectangle(pos=(self.pos_x, self.pos_y), size=(self.width, self.height))
        
        # 动画相关属性
        self.anim_speed = random.uniform(0.5, 4.0)
        self.anim_direction = random.choice(['horizontal', 'vertical', 'diagonal'])
        self.anim_offset = random.randint(30, 200)
        self.anim_rotating = random.random() > 0.7  # 30% 几率旋转动画
        
        # 存储关联的widget
        self.widget = widget
        
        # 开始动画
        self.start_animation()

    def start_animation(self):
        """启动矩形动画"""
        # 移动动画
        if self.anim_direction == 'horizontal':
            # 左右移动
            self.move_x_animation = Animation(
                pos=(self.pos_x + self.anim_offset,self.pos_y), 
                duration=self.anim_speed,
                t=random.choice(['out_quad', 'in_quad', 'in_out_quad', 'in_circ'])
            )
            self.move_x_animation += Animation(
                pos=(self.pos_x,self.pos_y), 
                duration=self.anim_speed,
                t=random.choice(['out_quad', 'in_quad', 'in_out_quad', 'in_circ'])
            )
            self.move_x_animation.repeat = True
            self.move_x_animation.start(self.rect)
            
        elif self.anim_direction == 'vertical':
            # 上下移动
            self.move_y_animation = Animation(
                pos=(self.pos_x,self.pos_y + self.anim_offset), 
                duration=self.anim_speed,
                t=random.choice(['out_quad', 'in_quad', 'in_out_quad', 'in_circ'])
            )
            self.move_y_animation += Animation(
                pos=(self.pos_x, self.pos_y),
                duration=self.anim_speed,
                t=random.choice(['out_quad', 'in_quad', 'in_out_quad', 'in_circ'])
            )
            self.move_y_animation.repeat = True
            self.move_y_animation.start(self.rect)
            
        else:  # diagonal
            # 对角线移动
            self.move_diagonal_animation = Animation(
                pos=(self.pos_x + self.anim_offset,self.pos_y + self.anim_offset), 
                duration=self.anim_speed,
                t=random.choice(['out_quad', 'in_quad', 'in_out_quad', 'in_circ'])
            )
            self.move_diagonal_animation += Animation(
                pos=(self.pos_x,self.pos_y), 
                duration=self.anim_speed,
                t=random.choice(['out_quad', 'in_quad', 'in_out_quad', 'in_circ'])
            )
            self.move_diagonal_animation.repeat = True
            self.move_diagonal_animation.start(self.rect)
        
        # # 旋转动画（仅部分矩形）
        # if self.anim_rotating:
        #     self.rotation_angle = 0
        #     self.rotation_animation = Animation(
        #         angle=360, 
        #         duration=self.anim_speed * 2,
        #         t=random.choice(['in_out_quad', 'in_out_circ'])
        #     )
        #     self.rotation_animation.repeat = True
        #     self.rotation_animation.bind(on_progress=self.update_rotation)
        #     self.rotation_animation.start(self)
            
        # 颜色动画
        target_color = (
            min(1.0, self.color[0] + random.uniform(-0.5, 0.5)), 
            min(1.0, self.color[1] + random.uniform(-0.5, 0.5)), 
            min(1.0, self.color[2] + random.uniform(-0.5, 0.5)),
            1
        )
        
        self.color_animation = Animation(
            rgba=target_color, 
            duration=self.anim_speed * 2,
            t=random.choice(['out_quad', 'in_quad'])
        ) + Animation(
            rgba=self.color, 
            duration=self.anim_speed * 2,
            t=random.choice(['out_quad', 'in_quad'])
        )
        self.color_animation.repeat = True
        self.color_animation.start(self.col)
        
        # 大小动画（部分矩形）
        if random.random() > 0.5:  # 50% 几率大小变化
            scale_factor = random.uniform(0.7, 1.3)
            target_size = (self.width * scale_factor, self.height * scale_factor)
            
            self.size_animation = Animation(
                size=target_size, 
                duration=self.anim_speed * 1.5,
                t=random.choice(['in_out_circ', 'in_out_quad'])
            ) + Animation(
                size=(self.width, self.height), 
                duration=self.anim_speed * 1.5,
                t=random.choice(['in_out_circ', 'in_out_quad'])
            )
            self.size_animation.repeat = True
            self.size_animation.start(self.rect)

    def update_rotation(self, animation, instance, progress):
        """更新旋转角度"""
        self.rotation_angle = progress * 360
        self.rect.angle = self.rotation_angle
        
    angle = NumericProperty(0)  # 用于旋转动画的绑定


class RandomRectsApp(App):
    """主应用类，包含随机矩形生成逻辑"""
    def build(self):
        # 使用浮动布局以便正确处理位置
        self.layout = FloatLayout()
        
        # 创建矩形管理器widget
        self.canvas_widget = Widget()
        self.layout.add_widget(self.canvas_widget)
        
        # 设置矩形数量（这里设置为20个）
        self.num_rects = 1000
        
        # 存储所有动画矩形对象
        self.animated_rects = []
        
        # 设置计时器生成矩形
        Clock.schedule_once(self.generate_rects, 0.1)
        
        # 设置一个退出按钮
        from kivy.uix.button import Button
        exit_btn = Button(text="退出", size_hint=(None, None), size=(100, 50), pos_hint={'right': 0.99, 'top': 0.99})
        exit_btn.bind(on_press=self.stop)
        self.layout.add_widget(exit_btn)
        
        return self.layout
    
    def generate_rects(self, dt):
        """生成随机矩形和动画"""
        for _ in range(self.num_rects):
            # 创建新的动画矩形
            rect = AnimatedRectangle(self.canvas_widget)
            self.animated_rects.append(rect)
        
        # 添加刷新按钮（可选）
        from kivy.uix.button import Button
        refresh_btn = Button(text="刷新", size_hint=(None, None), size=(100, 50), pos_hint={'x': 0.01, 'top': 0.99})
        refresh_btn.bind(on_press=self.refresh)
        self.layout.add_widget(refresh_btn)
    
    def refresh(self, instance):
        """刷新所有矩形"""
        # 清除现有的矩形
        self.canvas_widget.canvas.clear()
        self.animated_rects = []
        
        # 重新生成
        for _ in range(self.num_rects):
            rect = AnimatedRectangle(self.canvas_widget)
            self.animated_rects.append(rect)
        
        # 重置按钮位置（如果需要）
        if instance:
            instance.pos_hint = {'x': 0.01, 'top': 0.99}


if __name__ == '__main__':
    RandomRectsApp().run()