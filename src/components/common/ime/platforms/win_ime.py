# import ctypes
# from ctypes import wintypes, POINTER, Structure, c_void_p, c_byte, cast, pointer, addressof
# from typing import List, Tuple, Optional

# # 定义输入法上下文句柄类型
# HIMC = c_void_p

# # Windows DLL
# user32 = ctypes.WinDLL('user32')
# imm32 = ctypes.WinDLL('imm32')

# # === 输入法相关常量 ===
# WM_IME_COMPOSITION = 0x010F
# WM_IME_STARTCOMPOSITION = 0x010D
# WM_IME_ENDCOMPOSITION = 0x010E
# WM_IME_NOTIFY = 0x0282
# IMN_OPENCANDIDATE = 0x0005
# IMN_CHANGECANDIDATE = 0x0003
# IMN_CLOSECANDIDATE = 0x0004
# GCS_COMPSTR = 0x0008
# GCS_RESULTSTR = 0x0800
# NI_SELECTCANDIDATESTR = 0x0010
# NI_COMPOSITIONSTR = 0x0015
# CPS_COMPLETE = 0x0001

# # === Windows 结构体定义 ===
# class MSG(Structure):
#     _fields_ = [
#         ("hwnd", wintypes.HWND),
#         ("message", ctypes.c_uint),
#         ("wParam", wintypes.WPARAM),
#         ("lParam", wintypes.LPARAM),
#         ("time", wintypes.DWORD),
#         ("pt", wintypes.POINT)
#     ]

# class CANDIDATELIST(Structure):
#     _fields_ = [
#         ("dwSize", wintypes.DWORD),
#         ("dwStyle", wintypes.DWORD),
#         ("dwCount", wintypes.DWORD),
#         ("dwSelection", wintypes.DWORD),
#         ("dwPageStart", wintypes.DWORD),
#         ("dwPageSize", wintypes.DWORD),
#         ("dwOffset", wintypes.DWORD * 1)  # 动态数组占位符
#     ]

# # 配置API参数类型
# imm32.ImmGetContext.argtypes = [wintypes.HWND]
# imm32.ImmGetContext.restype = HIMC

# imm32.ImmGetCandidateListW.argtypes = [
#     HIMC, wintypes.DWORD, 
#     POINTER(CANDIDATELIST), wintypes.DWORD
# ]
# imm32.ImmGetCandidateListW.restype = wintypes.DWORD

# imm32.ImmReleaseContext.argtypes = [wintypes.HWND, HIMC]
# imm32.ImmReleaseContext.restype = wintypes.BOOL

# imm32.ImmGetCompositionStringW.argtypes = [
#     HIMC, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD
# ]
# imm32.ImmGetCompositionStringW.restype = wintypes.LONG

# imm32.ImmNotifyIME.argtypes = [
#     HIMC, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD
# ]
# imm32.ImmNotifyIME.restype = wintypes.BOOL

# # 定义钩子函数类型
# HOOKPROC = ctypes.WINFUNCTYPE(
#     ctypes.c_long, 
#     ctypes.c_int, 
#     ctypes.c_ulong, 
#     ctypes.POINTER(MSG)
# )

# class WindowsImeHandler:
#     """专注于输入法状态获取和操作的处理器"""
    
#     def __init__(self):
#         self.candidate_list: List[str] = []
#         self.selected_index: int = 0
#         self.page_start: int = 0
#         self.page_size: int = 5
#         self.hook_id: Optional[int] = None
#         self.hwnd: Optional[int] = None
#         self.imc: Optional[HIMC] = None
#         self.is_composing: bool = False
#         self.candidate_window_open: bool = False
#         self.composition_str: str = ""
        
#     def start_listening(self, hwnd: int) -> bool:
#         """开始监听输入法事件"""
#         if self.hook_id is not None:
#             return False
            
#         self.hwnd = hwnd
        
#         # 获取输入法上下文
#         self.imc = imm32.ImmGetContext(self.hwnd)
#         if not self.imc:
#             return False
        
#         # 安装消息钩子
#         self.hook_id = user32.SetWindowsHookExA(
#             14,  # WH_GETMESSAGE
#             HOOKPROC(self._low_level_handler),
#             0,
#             0
#         )
        
#         return self.hook_id is not None
    
#     def stop_listening(self):
#         """停止监听并释放资源"""
#         if self.hook_id:
#             user32.UnhookWindowsHookEx(self.hook_id)
#             self.hook_id = None
            
#         if self.imc:
#             imm32.ImmReleaseContext(self.hwnd, self.imc)
#             self.imc = None
            
#         self.candidate_list = []
#         self.is_composing = False
#         self.candidate_window_open = False
    
#     def get_candidates(self) -> List[str]:
#         """获取当前候选词列表"""
#         return self.candidate_list
    
#     def get_selected_index(self) -> int:
#         """获取当前选中的候选词索引"""
#         return self.selected_index
    
#     def get_page_info(self) -> Tuple[int, int]:
#         """获取分页信息（起始位置，页面大小）"""
#         return (self.page_start, self.page_size)
    
#     def get_composition(self) -> str:
#         """获取当前组合字符串"""
#         return self.composition_str
    
#     def is_candidate_window_open(self) -> bool:
#         """候选窗口是否打开"""
#         return self.candidate_window_open
    
#     def is_composing_text(self) -> bool:
#         """是否正在输入文本"""
#         return self.is_composing
    
#     def handle_key_event(self, key: str) -> bool:
#         """处理键盘事件（方向键选择、翻页等）"""
#         if not self.candidate_window_open:
#             return False
            
#         handled = False
        
#         # 方向键选择
#         if key == "right":
#             if self.selected_index < len(self.candidate_list) - 1:
#                 self.selected_index += 1
#                 handled = True
                
#                 # 翻页逻辑
#                 if self.selected_index >= self.page_start + self.page_size:
#                     self.page_start += self.page_size
                    
#         elif key == "left":
#             if self.selected_index > 0:
#                 self.selected_index -= 1
#                 handled = True
                
#                 # 翻页逻辑
#                 if self.selected_index < self.page_start:
#                     self.page_start = max(0, self.page_start - self.page_size)
                    
#         # 翻页功能
#         elif key == "up":
#             self.page_start = max(0, self.page_start - self.page_size)
#             self.selected_index = min(self.page_start + self.page_size - 1, self.selected_index)
#             handled = True
            
#         elif key == "down":
#             new_start = min(len(self.candidate_list) - self.page_size, self.page_start + self.page_size)
#             if new_start != self.page_start:
#                 self.page_start = new_start
#                 self.selected_index = max(self.page_start, self.selected_index)
#                 handled = True
                
#         # Enter 键选择候选词
#         elif key == "enter":
#             if self.candidate_list:
#                 self._select_candidate(self.selected_index)
#                 handled = True
                
#         # ESC 键关闭候选窗口
#         elif key == "escape":
#             self.candidate_window_open = False
#             handled = True
            
#         return handled
    
#     def _low_level_handler(self, nCode: int, wParam: int, lParam) -> int:
#         """低级消息处理钩子"""
#         if nCode >= 0:
#             msg = lParam.contents
#             if msg.hwnd == self.hwnd:  # 只处理目标窗口的消息
#                 self._process_ime_message(msg)
#         return user32.CallNextHookEx(None, nCode, wParam, lParam)
    
#     def _process_ime_message(self, msg: MSG):
#         """处理输入法相关消息"""
#         if msg.message == WM_IME_STARTCOMPOSITION:
#             self.is_composing = True
#             self.composition_str = ""
#             self.candidate_window_open = False
            
#         elif msg.message == WM_IME_ENDCOMPOSITION:
#             self.is_composing = False
#             self.composition_str = ""
#             self.candidate_window_open = False
#             self.candidate_list = []
            
#         elif msg.message == WM_IME_COMPOSITION:
#             if msg.lParam & GCS_COMPSTR:
#                 # 获取组合字符串
#                 length = imm32.ImmGetCompositionStringW(self.imc, GCS_COMPSTR, None, 0)
#                 if length > 0:
#                     buffer = ctypes.create_unicode_buffer(length // 2 + 1)
#                     imm32.ImmGetCompositionStringW(self.imc, GCS_COMPSTR, buffer, length)
#                     self.composition_str = buffer.value
                    
#             if msg.lParam & GCS_RESULTSTR:
#                 # 获取结果字符串（用户确认的输入）
#                 length = imm32.ImmGetCompositionStringW(self.imc, GCS_RESULTSTR, None, 0)
#                 if length > 0:
#                     buffer = ctypes.create_unicode_buffer(length // 2 + 1)
#                     imm32.ImmGetCompositionStringW(self.imc, GCS_RESULTSTR, buffer, length)
#                     # 处理结果字符串（如插入到文本框）
#                     self.composition_str = ""
            
#         elif msg.message == WM_IME_NOTIFY:
#             if msg.wParam == IMN_OPENCANDIDATE:
#                 self.candidate_window_open = True
#                 self._update_candidates()
                
#             elif msg.wParam == IMN_CHANGECANDIDATE:
#                 self._update_candidates()
                
#             elif msg.wParam == IMN_CLOSECANDIDATE:
#                 self.candidate_window_open = False
#                 self.candidate_list = []
    
#     def _update_candidates(self):
#         """安全地更新候选词列表"""
#         if not self.imc or not self.candidate_window_open:
#             return
            
#         # 获取候选列表所需大小
#         buf_size = imm32.ImmGetCandidateListW(self.imc, 0, None, 0)
#         if buf_size <= 0:
#             self.candidate_list = []
#             return
            
#         # 分配缓冲区
#         buffer = (c_byte * buf_size)()
#         p_candidate = cast(buffer, POINTER(CANDIDATELIST))
        
#         # 获取实际数据
#         if imm32.ImmGetCandidateListW(self.imc, 0, p_candidate, buf_size) <= 0:
#             self.candidate_list = []
#             return
            
#         # 安全提取候选词
#         self.candidate_list = []
#         cand_list = p_candidate.contents
        
#         # 计算偏移数组的位置（兼容32/64位）
#         offset_array_offset = ctypes.sizeof(CANDIDATELIST) - ctypes.sizeof(wintypes.DWORD)
#         base_addr = addressof(p_candidate)
#         offset_ptr = cast(base_addr + offset_array_offset, POINTER(wintypes.DWORD))
        
#         # 提取候选词
#         for i in range(cand_list.dwCount):
#             str_offset = offset_ptr[i]
#             str_ptr = cast(base_addr + str_offset, ctypes.c_wchar_p)
#             self.candidate_list.append(str_ptr.value)
            
#         # 更新分页和选择状态
#         self.page_start = cand_list.dwPageStart
#         self.page_size = cand_list.dwPageSize
#         self.selected_index = cand_list.dwSelection
        
#         # 确保选择索引在有效范围内
#         if self.selected_index >= len(self.candidate_list):
#             self.selected_index = len(self.candidate_list) - 1
    
#     def _select_candidate(self, index: int) -> bool:
#         """选择指定候选词"""
#         if not self.imc or index < 0 or index >= len(self.candidate_list):
#             return False
            
#         # 通知输入法选择候选词
#         if imm32.ImmNotifyIME(self.imc, NI_SELECTCANDIDATESTR, 0, index):
#             self.candidate_window_open = False
#             self.candidate_list = []
#             # 完成组合输入
#             imm32.ImmNotifyIME(self.imc, NI_COMPOSITIONSTR, CPS_COMPLETE, 0)
#             return True
            
#         return False

# 一种更加简单的实现方法
import ctypes
from ctypes import wintypes, cast, POINTER, addressof, c_byte, byref
import platform
from typing import List, Tuple, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('WindowsImeHandler')
# logger.setLevel(logging.WARNING)  # 只显示警告及以上级别的日志

# 定义输入法上下文句柄类型
HIMC = ctypes.c_void_p

# === 输入法相关常量 ===
GCS_COMPSTR = 0x0008
GCS_RESULTSTR = 0x0800
NI_SELECTCANDIDATESTR = 0x0010
NI_COMPOSITIONSTR = 0x0015
CPS_COMPLETE = 0x0001

# === Windows 结构体定义 ===
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

class WindowsImeHandler:
    """改进的Windows输入法处理器，支持上下文生命周期管理"""
    
    def __init__(self):
        self.h_imc = None  # 输入法上下文句柄
        self.h_wnd = None  # 窗口句柄
        # 初始化Windows API
        self._init_windows_api()
    
    def _init_windows_api(self):
        """初始化Windows API函数原型"""
        # Windows DLL
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
        
        self.imm32.ImmGetCompositionStringW.argtypes = [
            HIMC, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD
        ]
        self.imm32.ImmGetCompositionStringW.restype = wintypes.LONG
        
        self.imm32.ImmNotifyIME.argtypes = [
            HIMC, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD
        ]
        self.imm32.ImmNotifyIME.restype = wintypes.BOOL
        
        self.user32.GetForegroundWindow.argtypes = []
        self.user32.GetForegroundWindow.restype = wintypes.HWND
        
        # 添加更多API函数
        self.imm32.ImmGetOpenStatus.argtypes = [HIMC]
        self.imm32.ImmGetOpenStatus.restype = wintypes.BOOL
        
        self.imm32.ImmGetConversionStatus.argtypes = [HIMC, POINTER(wintypes.DWORD), POINTER(wintypes.DWORD)]
        self.imm32.ImmGetConversionStatus.restype = wintypes.BOOL
    
    def activate(self):
        """启动输入法上下文管理，在窗口获得焦点时调用"""
        if self.h_imc is not None:
            self.stop()
            
        try:
            # 获取前台窗口
            self.h_wnd = self.user32.GetForegroundWindow()
            logger.debug(f"GetForegroundWindow returned: {self.h_wnd}")
            
            # 检查是否有效窗口
            if not self.h_wnd or self.h_wnd == 0:
                logger.warning("No foreground window found")
                return False
                
            # 获取输入法上下文
            self.h_imc = self.imm32.ImmGetContext(self.h_wnd)
            logger.debug(f"ImmGetContext returned: {self.h_imc}")
            
            # 检查是否有效上下文
            if not self.h_imc or self.h_imc == 0:
                logger.warning("Failed to get input method context")
                self.h_imc = None
                return False
                
            # 检查输入法是否开启
            if not self.imm32.ImmGetOpenStatus(self.h_imc):
                logger.debug("Input method is not open")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Error starting IME context: {e}")
            self.h_imc = None
            return False
    
    def deactivate(self):
        """停止输入法上下文管理，在窗口失去焦点时调用"""
        if self.h_imc is None:
            return
            
        try:
            # 确保我们有有效的窗口句柄
            if self.h_wnd is None or self.h_wnd == 0:
                logger.warning("Invalid window handle during stop")
                return
                
            # 释放上下文
            result = self.imm32.ImmReleaseContext(self.h_wnd, self.h_imc)
            logger.debug(f"ImmReleaseContext returned: {result}")
            self.h_imc = None
            self.h_wnd = None
        except Exception as e:
            logger.error(f"Error stopping IME context: {e}")
        finally:
            self.h_imc = None
            self.h_wnd = None
    
    def is_active(self) -> bool:
        """检查输入法上下文是否处于活动状态"""
        return self.h_imc is not None and self.h_imc != 0
    
    # 按下任意字母键都会调用这个完成实时更新
    def _get_candidate_list_real_time(self,start:int=0,count:int=5) -> Tuple[List[str], int, int, int]:
        """实时获取候选词列表及相关信息"""
        if not self.is_active():
            logger.warning("IME context not active, cannot get candidates")
            return [], 0, 0, 0
            
        try:
            # 检查转换状态 - 确保输入法处于候选模式
            conv_mode = wintypes.DWORD()
            sent_mode = wintypes.DWORD()
            if not self.imm32.ImmGetConversionStatus(self.h_imc, byref(conv_mode), byref(sent_mode)):
                logger.warning("Failed to get conversion status")
                return [], 0, 0, 0
            
            logger.debug(f"Conversion mode: {conv_mode.value}, Sentence mode: {sent_mode.value}")
            
            # 获取所需缓冲区大小
            buf_size = self.imm32.ImmGetCandidateListW(self.h_imc, 0, None, 0)
            logger.debug(f"Candidate list buffer size: {buf_size}")
            
                
            if buf_size < ctypes.sizeof(CANDIDATELIST):
                logger.warning("Candidate list buffer too small")
                return [], 0, 0, 0
                
            # 分配动态内存
            buffer = (c_byte * buf_size)()
            p_candidate = cast(buffer, POINTER(CANDIDATELIST))
            
            # 获取实际数据
            ret_size = self.imm32.ImmGetCandidateListW(
                self.h_imc, 0, p_candidate, buf_size
            )
            logger.debug(f"ImmGetCandidateListW returned size: {ret_size}")
            
            if ret_size <= 0:
                logger.warning("Failed to get candidate list")
                return [], 0, 0, 0
                
            # 使用正确的基地址 - 整个缓冲区的起始地址
            base_addr = addressof(buffer)
            cand_list = p_candidate.contents
            
            # 打印候选词信息用于调试
            logger.debug(f"Candidate list info: count={cand_list.dwCount}, "
                         f"selection={cand_list.dwSelection}, "
                         f"page_start={cand_list.dwPageStart}, "
                         f"page_size={cand_list.dwPageSize}")
            
            # 正确计算偏移数组的位置
            # 固定字段大小：6个DWORD = 6 * 4 = 24字节
            offset_array_offset = 24
            offset_ptr = cast(base_addr + offset_array_offset, POINTER(wintypes.DWORD))
            
            # 提取候选词
            candidates = []
            for i in range(min(cand_list.dwCount, start+count)):  # 最多取10个候选词
                if i<start:
                    continue
                # 获取候选词字符串偏移量
                str_offset = offset_ptr[i]
                # 计算候选词字符串的实际地址
                str_ptr = base_addr + str_offset
                # 读取宽字符串
                try:
                    wstr = ctypes.wstring_at(str_ptr)
                    candidates.append(wstr)
                    logger.debug(f"Candidate {i}: {wstr}")
                except Exception as e:
                    logger.error(f"Error reading candidate string: {e}")
                    break

            # 返回候选词列表及状态
            return (
                candidates,
                cand_list.dwSelection,
                cand_list.dwPageStart,
                cand_list.dwPageSize
            )
        except Exception as e:
            logger.error(f"Error getting candidate list: {e}")
            return [], 0, 0, 0
    
    
def Test():
    Win=WindowsImeHandler()
    Win.activate()
    Win.deactivate()

if __name__ == "__main__":
    Test()