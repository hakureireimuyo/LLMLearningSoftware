from kivy.core.window import Window
from .ime_ui import IMEPreviewUI
from .platforms import WindowsImeHandler
import ctypes
from ctypes import wintypes, POINTER, Structure
import platform
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('IMEManager')

class IMEManager:
    """输入法管理器（单例）"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        # 创建平台相关处理器
        self.platform_handler = WindowsImeHandler()
        self.preview_ui = IMEPreviewUI()
        self.active_textinput = None
        self.is_active = False
        self.last_ime_text=''
        # 翻页需要用到的数据
        self.start_index = 0    #用于截取字段的起点
        self.page_size = self.preview_ui.page_size  #一次截取的最大数量
        self.select_index=0     #截取范围内的选择索引
    
    def activate(self, textinput):
        """激活输入法预览"""
        # 如果已激活且是同一个实例，直接返回
        if self.is_active and self.active_textinput == textinput:
            return
        self.last_ime_text=''
        logger.info(f"Activating IME for: {type(textinput)}")
        self.active_textinput = textinput
        self.is_active = True
        
        # 激活输入法上下文
        self.platform_handler.activate()
        
        # 添加到Window
        Window.add_widget(self.preview_ui)
    
    def deactivate(self, textinput):
        """关闭输入法预览"""
        # 只停用当前激活的实例
        if not self.is_active or self.active_textinput != textinput:
            return
            
        logger.info(f"Deactivating IME for: {type(textinput)}")
        self.is_active = False
        
        # 停用输入法上下文
        self.platform_handler.deactivate()
        Window.remove_widget(self.preview_ui)
        self.active_textinput = None
   
    def update_preview(self, start: int = 0, count: int = 5):
        """更新预览UI"""
        if not self.is_active:
            return
            
        # 获取候选词列表
        candidates, _, _, pagesize= self.platform_handler._get_candidate_list_real_time(start=start,count=count)
        if len(candidates)==0:
            self.visable(False)
            return
        self.preview_ui.update_candidates(candidates)

    def update_pos_of_ui(self):
        # 更新UI位置（基于当前激活的文本框）
        if self.active_textinput:
            # 获取文本框位置（示例坐标，需根据实际位置计算）
            x,y=self.active_textinput._get_cursor_pos()
            if y<=50:
                self.preview_ui.update_position(x,y+10)
            else:
                self.preview_ui.update_position(x,y-75)

    def visable(self,visible:bool):
        # 当焦点没有更改,但是完成了一组输入的时候,可以将ui变为不可见,或者是再次显示
        self.preview_ui.set_visible(visible)
    
    def handle_ime_input(self, textinput, text):
        """
        处理输入法输入事件
        确保只有当前激活的文本输入框处理事件
        """
        if textinput != self.active_textinput:
            return False
        if self.last_ime_text==text:
            return False
        self.last_ime_text=text
        self.update_preview(self.start_index,self.page_size)
        return False
    
    def left_move(self,step:int=1):
        self.select_index-=step
        if self.select_index<0:
            self.page_up(1)
            return
        self.select_index=max(0,self.select_index)
        self.preview_ui.update_selected_index(self.select_index)

    def right_move(self,step:int=1):
        self.select_index+=step
        if self.select_index>=self.page_size:
            self.page_down(1)
            return
        self.select_index=min(self.select_index,self.page_size-1)
        self.preview_ui.update_selected_index(self.select_index)

    def page_up(self,step:int=1):
        """
        向上翻页
        """
        self.select_index=0
        self.preview_ui.update_selected_index(self.select_index)
        self.start_index-=step*self.page_size
        self.start_index=max(0,self.start_index)
        self.update_preview(self.start_index,self.page_size)

    def page_down(self,step:int=1):
        """
        向下翻页
        """
        self.select_index=0
        self.preview_ui.update_selected_index(self.select_index)
        self.start_index+=step*self.page_size
        #self.start_index=min(len(self.candidates)-self.page_size,self.start_index) ????
        self.update_preview(self.start_index,self.page_size)
    
    def reset_index(self):
        # 当一次输入完成后调用
        self.start_index=0
        self.select_index=0
        self.preview_ui.update_candidates_animate(self.select_index)

