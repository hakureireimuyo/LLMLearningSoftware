from kivy.lang import Builder
Builder.load_string('''
<TodayCard>:
    orientation:'vertical'
    adaptive_height: True
    md_bg_color:app.theme_cls.backgroundColor
    padding: dp(10)
    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
    radius: [20,20,20,20]
    MDLabel:
        text: 'Today'
        font_style: 'Display'
        role: 'medium'
        size_hint_y: None
        height: self.texture_size[1]
        valign:'middle'
        halign:'center'
    MDGridLayout:
        #orientation:'vertical'
        cols: 2
        adaptive_height: True
        spacing: dp(20)
        BaseItem:
            icon: 'book-open-variant'
            text: root.review_count
        BaseItem:
            icon: 'plus'
            text: root.new_word_count
        BaseItem:
            icon: 'clock'
            text: root.learing_time
        BaseItem:
            icon: 'check'
            text: root.completed_count
''')

from kivy.properties import StringProperty
class TodayCard(MDBoxLayout):   
    review_count = StringProperty()
    new_word_count = StringProperty()
    learing_time = StringProperty()
    completed_count = StringProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

from kivymd.app import MDApp
class ExampleApp(MDApp):
    def build(self):
        return TodayCard(review_count='12', new_word_count='34', learing_time='1h 30m', completed_count='5')

if __name__ == '__main__':
    ExampleApp().run()