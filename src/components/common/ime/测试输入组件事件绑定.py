from kivymd.uix.textfield import MDTextField
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('IMEManager')

class Mix:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        self.active_textinput=None
        self.is_active = False
        pass

    def activate(self, textinput):
        """激活输入法预览"""
        if self.is_active:
            return
        self.is_active=True
        logger.info(f"The type to which it is bound is:{type(textinput)}")
        self.active_textinput = textinput

    def deactivate(self):
        """关闭输入法预览"""
        logger.info("Deactivate ime")
        if not self.is_active:
            return
        self.is_active = False
        self._unbind_current()

    def _bind_current(self):
        """绑定当前激活文本框的事件"""
        if not self.active_textinput:
            return
        logger.info(f"Bind events to {self.active_textinput}")
        # 绑定键盘事件和文本输入事件
        self.active_textinput.bind(on_key_down=self.ime_keyboard_on_key_down)
        self.active_textinput.bind(on_textinput=self.ime_on_textinput)
    
    def _unbind_current(self):
        """解绑当前文本框的事件"""
        if not self.active_textinput:
            return
        try:
            logger.info(f"Unbind events from {self.active_textinput}")
            self.active_textinput.unbind(on_key_down=self.ime_keyboard_on_key_down)
            self.active_textinput.unbind(on_textinput=self.ime_on_textinput)
        except:
            logger.warning("Error unbinding events from textinput")

    def ime_keyboard_on_key_down(self, window, keycode, text, modifiers):
        """处理键盘事件"""
        print(self.is_active)
        if not self.is_active:
            return False
        logger.info(f"Key down: {window,keycode,text,modifiers}")
        return False
    
    def ime_on_textinput(self, instance, value):
        """输入完成后触发,可以进行一些其他处理,比如关闭输入法显示"""
        logger.info(f"Text input: {value}")
    

class TextInputImeMixin:
    """TextInput输入法混合类"""
    def __init__(self):
        self.ime_manager = Mix()
        self.bind(focus=self._on_focus_change)
    
    def _on_focus_change(self, instance, value):
        logger.info(f"Focus change: {value}")
        if value:
            self.ime_manager.activate(self)
        else:
            self.ime_manager.deactivate()

class MyInput(MDTextField,TextInputImeMixin):
    def __init__(self, *args, **kwargs):
        MDTextField.__init__(self, **kwargs)
        TextInputImeMixin.__init__(self)
    
    def on_key_down(self, window, keycode, text, modifiers):
        """处理键盘事件"""
        logger.info(f"Key down: {window,keycode,text,modifiers}")
        return super().on_key_down(window, keycode, text, modifiers)
    
    def insert_text(self, substring, from_undo=False):
        """处理文本输入"""
        logger.info(f"Insert text: {substring}")
        return super().insert_text(substring, from_undo)
    
    def window_on_textedit(self, window, ime_input):
        """处理IME输入事件"""
        # 调用父类方法处理基础IME逻辑
        super().window_on_textedit(window, ime_input)
        # IME输入时显示预览
        logger.info(f"IME input: {ime_input}")
    
from kivymd.app import MDApp

class Test(MDApp):
    def build(self):
        return MyInput()

if __name__ == "__main__":
    Test().run()
