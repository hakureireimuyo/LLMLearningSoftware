
import os
from faker import Faker
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
import asynckivy
from kivy.uix.behaviors import ButtonBehavior

KV = '''
MDScreen:
    md_bg_color: self.theme_cls.backgroundColor

    MDBoxLayout:
        orientation: "vertical"
        padding: "12dp"
        spacing: "12dp"

        MDLabel:
            adaptive_height: True
            text: "Your downloads"
            theme_font_style: "Custom"
            font_style: "Display"
            role: "small"

        MDSegmentedButton:
            size_hint_x: 1

            MDSegmentedButtonItem:
                on_active: app.generate_card()

                MDSegmentButtonLabel:
                    text: "Songs"
                    active: True

            MDSegmentedButtonItem:
                on_active: app.generate_card()

                MDSegmentButtonLabel:
                    text: "Albums"

            MDSegmentedButtonItem:
                on_active: app.generate_card()

                MDSegmentButtonLabel:
                    text: "Podcasts"

        RecycleView:
            id: card_list
            viewclass: "UserCard"
            bar_width: 0

            RecycleBoxLayout:
                orientation: 'vertical'
                spacing: "16dp"
                padding: "16dp"
                default_size: None, dp(72)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
'''

Builder.load_string("""
<UserCard>
    adaptive_height: True
    radius: 16
    MDListItem:
        radius: 16
        theme_bg_color: "Custom"
        md_bg_color: self.theme_cls.secondaryContainerColor
        on_press: root.on_press()
        MDListItemLeadingAvatar:
            source: root.image_path

        MDListItemHeadlineText:
            text: root.name

        MDListItemSupportingText:
            text: root.text
""")
class UserCard(MDBoxLayout,ButtonBehavior):
    name = StringProperty()
    image_path = StringProperty()
    text = StringProperty()
    screen_name=StringProperty()
    callback = ObjectProperty(lambda x: print(f"默认回调：{x}"))
    def __init__(self, **kwargs):
        super(UserCard, self).__init__(**kwargs)

    def on_press(self):
        print(f"按钮{self.name}按下")
        self.callback(self.screen_name)
    # def set_callback(self,fun):
    #     self.callback = fun
    
class Example(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Olive"
        return Builder.load_string(KV)

    def generate_card(self):
        async def generate_card():
            for i in range(10):
                await asynckivy.sleep(0)
                self.root.ids.card_list.data.append(
                    {
                        "name": fake.name(),
                        "image_path": "D:/ProjectFloder/Python/LLMLanguageLearingSoftware/src/resource/image/character_avatar/defualtroleimage.png",
                        "album": fake.image_url(),
                    }
                )

        fake = Faker()
        self.root.ids.card_list.data = []
        Clock.schedule_once(lambda x: asynckivy.start(generate_card()))

if __name__ == "__main__":
    Example().run()