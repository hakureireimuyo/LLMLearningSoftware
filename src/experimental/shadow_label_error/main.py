from kivymd.uix.behaviors import CommonElevationBehavior
from kivymd.uix.label import MDLabel, MDIcon
from kivy.graphics import Color, SmoothRoundedRectangle
from kivy.clock import Clock

class ErrorLabel(CommonElevationBehavior,MDLabel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.elevation = 2
        self.size_hint = (None, None)
        self.size = (200, 50)
        self.pos_hint = {"right": 1, "center_y": 0.5}
    
    def on_md_bg_color(self, instance_label, color) -> None:
        """Fired when the :attr:`md_bg_color` value changes."""

        def on_md_bg_color(*args) -> None:
            from kivymd.uix.selectioncontrol import MDCheckbox
            from kivymd.uix.tooltip import MDTooltipPlain

            if not issubclass(
                self.__class__, (MDCheckbox, MDIcon, MDTooltipPlain)
            ):
                self.canvas.remove_group("Background_instruction")

                FIXME: IndexError
                try:
                    self.canvas.before.clear()
                except IndexError:
                    pass

                with self.canvas.before:
                    Color(rgba=color, group="md-label-selection-color")
                    self._canvas_bg = SmoothRoundedRectangle(
                        pos=self.pos,
                        size=self.size,
                        radius=self.radius,
                        group="md-label-selection-color-rectangle",
                    )
                    self.bind(pos=self.update_canvas_bg_pos)

        Clock.schedule_once(on_md_bg_color)

from kivy.lang import Builder

KV="""
MDBoxLayout:
    orientation: "vertical"
    spacing: dp(10)
    padding: dp(10)
    size_hint: 1, 1
    md_bg_color: 0.5,0.5,0.5,1
    pos_hint: {"center_x": 0.5, "center_y": 0.5}
    MDButton:
        on_release: root.theme_cls.switch_theme()
    ErrorLabel:
        id: label1
        text: "11111"
        md_bg_color: self.theme_cls.primaryColor
"""

from kivymd.app import MDApp
class TestApp(MDApp):
    def build(self):
        return Builder.load_string(KV)
    
if __name__=="__main__":
    TestApp().run()