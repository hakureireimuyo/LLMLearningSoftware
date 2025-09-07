import ctypes
from ctypes import wintypes, cast, POINTER, addressof, c_byte
import platform
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.core.text import LabelBase
from kivy.clock import Clock

# === Windows输入法处理模块 ===
HIMC = ctypes.c_void_p  # 定义输入法上下文句柄类型

class CANDIDATELIST(ctypes.Structure):
    _fields_ = [
        ('dwSize', wintypes.DWORD),
        ('dwStyle', wintypes.DWORD),
        ('dwCount', wintypes.DWORD),
        ('dwSelection', wintypes.DWORD),
        ('dwPageStart', wintypes.DWORD),
        ('dwPageSize', wintypes.DWORD),
        ('dwOffset', wintypes.DWORD * 0)  # 动态数组占位符
    ]

class WindowsInputMethodHandler:
    def __init__(self):
        self.user32 = ctypes.WinDLL('user32')
        self.imm32 = ctypes.WinDLL('imm32')
        
        # 配置API参数类型
        self.imm32.ImmGetContext.argtypes = [wintypes.HWND]
        self.imm32.ImmGetContext.restype = HIMC
        
        self.imm32.ImmGetCandidateListW.argtypes = [
            HIMC, wintypes.DWORD, 
            POINTER(CANDIDATELIST), wintypes.DWORD
        ]
        self.imm32.ImmGetCandidateListW.restype = wintypes.DWORD
        
        self.imm32.ImmReleaseContext.argtypes = [wintypes.HWND, HIMC]
        self.imm32.ImmReleaseContext.restype = wintypes.BOOL

    def get_candidates(self):
        """获取输入法候选词列表（修复版）"""
        h_wnd = self.user32.GetForegroundWindow()
        if not h_wnd:
            return []
            
        h_imc = self.imm32.ImmGetContext(h_wnd)
        if not h_imc:
            return []
        
        try:
            # 获取所需缓冲区大小
            buf_size = self.imm32.ImmGetCandidateListW(h_imc, 0, None, 0)
            if buf_size < ctypes.sizeof(CANDIDATELIST):
                return []
            
            # 分配动态内存
            buffer = (c_byte * buf_size)()
            p_candidate = cast(buffer, POINTER(CANDIDATELIST))
            
            # 获取实际数据
            ret_size = self.imm32.ImmGetCandidateListW(
                h_imc, 0, p_candidate, buf_size
            )
            if ret_size == 0:
                return []
            
            # 动态访问偏移数组
            base_addr = addressof(p_candidate.contents)
            offset_array = cast(
                base_addr + 24,  # 前6个字段总长度24字节
                POINTER(wintypes.DWORD * p_candidate.contents.dwCount)
            ).contents
            
            # 提取候选词
            candidates = []
            # for i in range(p_candidate.contents.dwCount):
            #     str_ptr = base_addr + offset_array[i]
            #     wstr = ctypes.wstring_at(str_ptr)
            #     candidates.append(f"{i+1}.{wstr}")
            for i in range(7):
                str_ptr = base_addr + offset_array[i]
                wstr = ctypes.wstring_at(str_ptr)
                candidates.append(f"{i+1}.{wstr}")
            
            return candidates
        finally:
            self.imm32.ImmReleaseContext(h_wnd, h_imc)

# === Kivy界面模块 ===
LabelBase.register(
    name='fzh',
    fn_regular='D:\\ProjectFloder\\Python\\LLMLearingSoftware\\resource\\font\\STSONG.TTF'
)
from kivy.core.window import Window

class IMEBoxLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ime_handler = WindowsInputMethodHandler() if platform.system() == 'Windows' else None
        self._update_clock = None
        Window.bind(on_key_down=self.on_key_down)

    def update_candidates(self, candidates):
        self.ids.outl.text = "\n".join(candidates) if candidates else ""

    # def start_monitor(self):
    #     """启动候选词监听"""
    #     if self.ime_handler and not self._update_clock:
    #         self._update_clock = Clock.schedule_interval(
    #             self._check_candidates, 0.05)

    # def stop_monitor(self):
    #     """停止监听"""
    #     if self._update_clock:
    #         self._update_clock.cancel()
    #         self._update_clock = None
    def on_key_down(self, window, key, scancode, text, modifiers, **kwarg):
        """处理键盘事件"""
        self._check_candidates(dt=0)
        return False
    
    def _check_candidates(self, dt):
        candidates = self.ime_handler.get_candidates()
        self.update_candidates(candidates)

class IMEDemoApp(App):
    def build(self):
        return Builder.load_string('''
IMEBoxLayout:
    orientation: 'vertical'
    TextInput:
        id: ipt
        font_name: 'fzh'
        size_hint_y: 0.7
        # on_focus: 
        #     root.start_monitor() if args[1] else root.stop_monitor()
    Label:
        id: outl
        font_name: 'fzh'
        size_hint_y: 0.3
        text_size: self.width, None
        height: self.texture_size[1]
''')

if __name__ == '__main__':
    IMEDemoApp().run()