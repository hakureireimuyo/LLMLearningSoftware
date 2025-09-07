KV = """
#:import Widget kivy.uix.widget.Widget
#:import dp kivy.metrics.dp
#:import MDLabel kivymd.uix.label.MDLabel
MDScreen:
    md_bg_color: self.theme_cls.backgroundColor
    ScrollView:

        MDBoxLayout:
            orientation: "vertical"
            padding: "32dp", 0, "32dp", "32dp"
            spacing: "24dp"
            adaptive_height: True
            id: widget_box

            MDLabel:
                id: label1
                text: "First update the theme, then add new components to update the position of the label, in order to discover any additional afterimages"
                font_style: "Title"
                md_bg_color: self.theme_cls.primaryColor
                size_hint_y: None
                height:dp(200)

            Widget:
                size_hint_y: None
                height: "200dp"

            MDButton:
                on_release: root.ids.widget_box.add_widget(MDLabel(size_hint=(None, None), size=(dp(100), dp(20)),md_bg_color = (1,0,0,0.2)))
                MDButtonText:
                    text: "add widget"

            MDButton:
                on_release: root.theme_cls.switch_theme()
                MDButtonText:
                    text: "switch_theme"

            MDButton:
                on_release: root.ids.label1.canvas.before.clear()
                MDButtonText:
                    text: "clear MDLabel canvas"

            

            MDButton:
                on_release: if self!=root.ids.widget_box.children[0]:root.ids.widget_box.remove_widget(root.ids.widget_box.children[0])
                MDButtonText:
                    text: "remove widget"
                    
"""
from kivymd.app import MDApp
from kivy.lang import Builder

class textapp(MDApp):
    def build(self):
        return Builder.load_string(KV)
    
if __name__=="__main__":
    textapp().run()