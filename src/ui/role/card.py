from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, ColorProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
# from kivymd.uix.behaviors import

KV = '''
<MyCard>:
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
    #elevation_level: 2
    MDRelativeLayout:
        # MDIconButton:
        #     icon: "dots-vertical"
        #     pos_hint: {"top": 1, "right": 1}
        #     on_release: app.card_manager.remove_card(root)
        MDLabel:
            text: root.text
            font_style:"STSONG"
            role:"large"
            adaptive_size: True
            color: "white" if root.selected else "grey"
            pos: "12dp", "12dp"
            bold: True

<CardManager>:
    theme_bg_color: "Custom"
    #md_bg_color: self.theme_cls.backgroundColor
    size_hint: None,None
    size: "500dp", "700dp"
    MDScrollView:
        do_scroll_x: False
        do_scroll_y: True
        MDStackLayout:
            orientation:"lr-tb"
            #md_bg_color: app.theme_cls.backgroundColor
            id: card_container
            adaptive_height: True
            spacing: "12dp"
            pos_hint: {"center_x": .5,"center_y": .5}
    # MDFloatLayout:
    #     MDIconButton:
    #         icon: "plus"
    #         pos_hint: {"center_x": .5, "center_y": .5}
    #         theme_text_color: "Custom"
    #         text_color: app.theme_cls.primaryColor
    #         on_release: app.card_manager.add_card("new","New Card")    
'''
Builder.load_string(KV)

class CardManager(MDBoxLayout):
    callback=ObjectProperty(None)

    def __init__(self,callback=lambda x:print("卡片管理"),**kwargs):
        super().__init__(**kwargs)
        self.current_selected = None
        self.callback=callback
        #self.on_start()

    def on_start(self):
        # 测试组件初始化示例卡片
        sample_texts = ["工作模式", "学习模式", "娱乐模式", "旅行模式","测试滚动","测试滚动","测试滚动","测试滚动","测试滚动","测试滚动","测试滚动","测试滚动","测试滚动","测试滚动","测试滚动","测试滚动"]
        for id, text in enumerate(sample_texts, start=1):
            self.add_card(str(id), text)

    def get_cureent_selected_id(self):
        return self.current_selected.id
    
    def add_card(self, id,text):
        """添加新卡片并自动管理选择状态"""
        new_card = MyCard(
            id=id,
            text=text,
            callback=self.select_card
        )
        self.ids.card_container.add_widget(new_card)
        if not self.current_selected:
            self.select_card(new_card)

    def select_card(self, selected_card):
        """处理卡片选择逻辑"""
        for card in self.ids.card_container.children:
            if card==selected_card:
                card.selected = True
                self.current_selected=card
            else:
                card.selected = False
        print("=============================")

    def select_card_from_id(self, id):
        """处理卡片选择逻辑"""
        for card in self.ids.card_container.children:
            if card.id==id:
                card.selected = True
                self.current_selected=card
            else:
                card.selected = False
        print("=============================")

    def change_role(self):
        """切换角色"""
        self.callback(self.current_selected.id)
        pass

class MyCard(MDCard):
    text = StringProperty() #角色名字
    selected = BooleanProperty(False)
    id=StringProperty("1") #角色的唯一编号
    callback=ObjectProperty(None)
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.bind(selected=self.on_select)

    def on_press(self):
        super().on_press()
        self.callback(self)

    def on_select(self,*arges):
        """更新卡片的颜色"""
        print(f"on_select{self.id}更新{self.selected}")
        self.update_colors()

    def update_colors(self):
        if self.selected:
            self.elevation = 4
            self.md_bg_color =MDApp.get_running_app().theme_cls.secondaryColor
            self.line_color = [1,1,1,1]
            print(self.elevation,self.md_bg_color,self.line_color)
        else:
            self.elevation = 0
            self.md_bg_color = MDApp.get_running_app().theme_cls.onTertiaryColor
            self.line_color = [0.8, 0.8, 0.8, 1]
            print(self.elevation,self.md_bg_color,self.line_color)
        

class MainApp(MDApp):
    card_manager = ObjectProperty()

    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Beige"
        self.card_manager=CardManager()
        return self.card_manager

    def on_start(self):
        # 初始化示例卡片
        sample_texts = ["工作模式", "学习模式", "娱乐模式", "旅行模式"]
        for id, text in enumerate(sample_texts, start=1):
            self.card_manager.add_card(str(id), text)


if __name__ == "__main__":
    MainApp().run()