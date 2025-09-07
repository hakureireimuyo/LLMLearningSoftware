from kivy.core.window import Window
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.behaviors import CommonElevationBehavior
from kivy.properties import (ListProperty, 
                             NumericProperty, 
                             BooleanProperty,
                             ObjectProperty)
from kivy.graphics import RoundedRectangle,Color,Line
from kivymd.uix.divider import MDDivider
from kivy.animation import Animation
from kivy.clock import Clock

class  IMEPreviewUI(MDBoxLayout, CommonElevationBehavior):
    """输入法候选词UI组件（高效对象池版）"""
    candidates = ListProperty([])
    selected_index = NumericProperty(0)
    page_size = NumericProperty(5)
    is_visible = BooleanProperty(False)

    # 动画引用
    current_animation = ObjectProperty(None, allownone=True)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.adaptive_size = True
        self.orientation = 'horizontal'
        self.spacing = 5
        self.padding = (4, 4, 4, 4)
        self.md_bg_color = self.theme_cls.backgroundColor
        self.radius = (10, 10, 10, 10)
        self.line_color = self.theme_cls.primaryColor
        self.elevation_level = 1
        self.shadow_color = self.theme_cls.secondaryColor
        self.shadow_offset = (0, -4)
        self.shadow_softness = 0.8
        
        # 对象池配置
        self.max_components = 10  # 最大候选词数量
        self.button_pool = []     # 按钮对象池
        self.divider_pool = []    # 分割线对象池
        self.active_count = 0     # 当前激活的组件数量
        
        # 初始化对象池
        self._init_component_pool()

        # 添加高亮块绘制指令
        with self.canvas:
            self.highlight_color = Color(*self.theme_cls.primaryContainerColor[0:3],1)
            self.highlight = RoundedRectangle(
                pos=(0,0),
                size=(10,10),
                radius=(10,10,10,10)
            )
    
    def _init_component_pool(self):
        """初始化组件对象池"""
        # 创建候选词按钮池
        for i in range(self.max_components):
            btn = MDLabel(
                text="",
                adaptive_size=True,
                role="medium",
                font_style="STSONG",
                radius=(5, 5, 5, 5),
                opacity=0  # 初始不可见
            )
            self.button_pool.append(btn)
        
        # 创建分割线池（比按钮少一个）
        for i in range(self.max_components - 1):
            divider = MDDivider(
                orientation="vertical",
                width=1,
                color=self.theme_cls.primaryColor,
                opacity=0  # 初始不可见
            )
            self.divider_pool.append(divider)
    
    def _update_active_components(self, new_count):
        """根据新数量调整激活组件（修复交替布局问题）"""
        new_count = min(new_count, self.max_components)
        
        # 添加新组件（交替添加按钮和分割线）
        if new_count > self.active_count:
            # 从当前激活数量开始，逐个添加新组件
            for i in range(self.active_count, new_count):
                # 添加按钮
                self.add_widget(self.button_pool[i])
                
                # 如果不是最后一个按钮，添加分割线
                if i < new_count - 1:
                    self.add_widget(self.divider_pool[i])
        
        # 移除多余组件（反向交替移除）
        elif new_count < self.active_count:
            # 从最后一个开始，逐个移除组件
            for i in range(self.active_count - 1, new_count - 1, -1):
                # 先移除分割线（如果有）
                if i >= 0 and self.divider_pool[i].parent is self:
                    self.remove_widget(self.divider_pool[i])
                
                # 移除按钮
                self.remove_widget(self.button_pool[i])
        
        # 更新激活数量
        self.active_count = new_count
    
    def set_visible(self, visible):
        """设置组件可见性"""
        self.is_visible = visible
        self.opacity = 1 if visible else 0
        
        # 更新所有激活组件的可见性
        for i in range(self.active_count):
            self.button_pool[i].opacity = 1 if visible else 0
            if i < self.active_count - 1:
                self.divider_pool[i].opacity = 1 if visible else 0
        # 清理缓存数据
            
        if not visible:
            self.selected_index = 0
            self.update_candidates([])

    def update_theme(self, instance, value):
        """更新主题颜色"""
        self.md_bg_color = self.theme_cls.backgroundColor
        self.line_color = self.theme_cls.primaryColor
        self.shadow_color = self.theme_cls.secondaryColor
        self.highlight_color.rgba =(*self.theme_cls.primaryContainerColor[0:3],1)
    
    def update_candidates(self, candidates: list):
        """更新候选词列表"""
        self.candidates = candidates
        
        # 确定需要显示的数量
        display_count = min(len(candidates), self.page_size)
        
        # 更新激活组件数量
        self._update_active_components(display_count)
        
        # 更新按钮文本
        for i in range(display_count):
            self.button_pool[i].text = f"{i+1} {candidates[i]}"
        
        Clock.schedule_once(lambda dt:self.update_selected_index(0), 0.1)
    
    def update_selected_index(self, new_index: int):
        """更新选中索引（带动画效果）"""
        if not self.is_visible or self.active_count == 0:
            return 
        
        # 确保索引在有效范围内
        new_index = max(0, min(new_index, self.active_count - 1))
        
        # 如果已经有动画在进行，取消它
        if self.current_animation:
            self.current_animation.cancel(self)
            self.current_animation = None
        
        # 获取目标按钮
        target_btn = self.button_pool[new_index]
        # 计算目标位置（相对于预览框）
        target_pos = target_btn.pos
        # 动画序列
        def start_animation():
            # 第一步：缩小并移动到目标位置
            anim1 = Animation(
                size=(target_btn.width*0.8,target_btn.height*0.8),
                pos=(target_pos[0]+target_btn.width*0.1,target_pos[1]+target_btn.height*0.1),
                duration=0.2,
                t='in_out_quad'
            )
            
            # 第二步：放大到110%并改变颜色
            anim2 = Animation(
                size=(target_btn.width * 1.1,target_btn.height * 1.1),
                pos=(target_pos[0]+target_btn.width*0.05,target_pos[1]+target_btn.height*0.05),
                duration=0.15,
                t='in_out_quad'
            )
            
            # 第三步：恢复到正常大小
            anim3 = Animation(
                size=(target_btn.width,target_btn.height),
                pos=target_pos,
                duration=0.1,
                t='in_out_quad'
            )
            
            # # 更新字体颜色
            # def update_font_color(animation, widget):
            #      # 立即更新旧字体的颜色
            #     if 0 <= self.selected_index < self.active_count:
            #         old_btn = self.button_pool[self.selected_index]
            #         old_btn.text_color = self.theme_cls.onBackgroundColor
            #     # 设置新选中项的颜色
            #     target_btn.text_color = self.theme_cls.tertiaryContainerColor
            #     # 更新当前选中索引
            #     self.selected_index = new_index

            # 链式动画
            self.current_animation = anim1 + anim2 + anim3
            #self.current_animation.bind(on_complete=update_font_color)
            self.current_animation.start(self.highlight)
        
        # 立即开始动画
        start_animation()
    #不是选择动画,而是更新预选词后的背景色块调整动画
    def update_candidates_animate(self):
        # 获取当前索引按钮的大小和位置属性
        # 如果当前索引不在区间内,就取最近的合理数字
        # 如果不存在可用按钮,就直接退出
        if self.active_count==0 or not self.is_visible:
            return
        self.selected_index=max(self.selected_index,0)
        self.selected_index=min(self.selected_index,self.active_count)

        target_btn=self.button_pool[self.selected_index]
        target_pos= target_btn.pos
        def start_animate():
            anim1=Animation(
                size=(target_btn.width*0.8,target_btn.height*0.8),
                pos=(target_pos[0]+target_btn.width*0.1,target_pos[1]+target_btn.height*0.1),
                duration=0.2,
                t='in_out_quad'
            )
            anim2=Animation(
                size=(target_btn.width,target_btn.height),
                pos=(target_pos[0],target_pos[1]),
                duration=0.15,
                t='in_out_quad'
            )
            self.current_animation = anim1 + anim2
            self.current_animation.start(self.highlight)

        start_animate()

    def update_position(self, x, y):
        """更新位置/更新背景色块位置"""
        self.pos = (x, y)
        self.highlight.pos=(x,y)
