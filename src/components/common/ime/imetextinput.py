from .ime_core import IMEManager
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('TextInputIme')

from kivy.graphics import Color, Rectangle
from kivy.properties import ObjectProperty
from kivymd.uix.textfield import MDTextField
class ImeTextInput(MDTextField):
    """TextInput中文输入法实现类"""
    # 按下回车时候的回调函数
    callback = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.md_bg_color = self.theme_cls.backgroundColor
        self.font_name="STSONG"
        self.mode='filled'
        self.ime_manager = IMEManager()
        self.bind(focus=self._on_focus_change)
        self.is_activate_ime=False
    
    def _on_focus_change(self, instance, value):
        if value:
            # 获得焦点时激活输入法
            self.is_activate_ime=True
            self.ime_manager.activate(self)
        else:
            # 失去焦点时停用输入法
            self.is_activate_ime=False
            self.ime_manager.deactivate(self)

    def window_on_textedit(self, window, ime_input):
        """
        自定义文本编辑事件处理
        优先处理输入法事件，如果输入法未处理则使用原始逻辑
        当中文输入法的时候,按下字母键会调用这部分函数
        由于一些机制,每按下一次按键会调用很多次,不过我排除了一些相同输入
        """
        logger.info("="*50)
        logger.info(f"window_on_textedit: {ime_input}")
        # 先尝试让输入法管理器处理
        if ime_input == None or ime_input=='':
            self.ime_manager.visable(False)
            self.ime_manager.update_pos_of_ui()
            return super().window_on_textedit(window, ime_input)
        
        self.ime_manager.handle_ime_input(self, ime_input)
        self.ime_manager.visable(True)
        return super().window_on_textedit(window, ime_input)
    
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        """
        处理键盘特殊指令事件
        中文输入法的时候字母键不会触发,其他状态输入任何按键都会触发
        因此如果需要实现输入法的索引控制,需要先检测是否处于中文输入法状态
        判断是否是中文输入法状态可以使用一个变量来表示
        随后可以解析一些指令,并进行对应的调用
        """
        logger.info(f"Key down: {window,keycode,text,modifiers}")
        if keycode[0]==13:
            # 按下了enter键
            if 'shift' in modifiers:
                self.key_shift_enter()
            else:
                self.key_down_enter()
            return True
        return super().keyboard_on_key_down(window, keycode, text, modifiers)
    
    def key_down_enter(self):
        if self.callback is not None and self.text:
            self.callback(self.text)
            self.text=""
            return True
        self.text=""
        return False
    
    def key_shift_enter(self):
        self.text+="\n"