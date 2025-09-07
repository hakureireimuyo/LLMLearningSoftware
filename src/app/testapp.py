from src.app import App
from .common_app import CommonApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton
from kivy.core.window import Window

class TestApp(App,CommonApp):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.com=None
        self.box=None
    
    def print_component_info(self):
        """打印组件结构信息"""
        print("\n=== Component Structure ===")
        # if self.box:
        #     self._print_widget_tree(self.box)
        # else:
        #     self._print_widget_tree(self.com)
        self._print_widget_tree(self.root)
        print("===========================\n")
        # print("\n=========== Window ========")
        # self._print_widget_tree(Window)
        print("===========================\n")
    
    def build(self):
        self.box=MDBoxLayout(orientation="vertical",size_hint=(1,1))
        self.box.md_bg_color=self.theme_cls.backgroundColor
        self.MDIconButton=MDButton(
            pos_hint={"center_x":0.5,"center_y":0.5},
            on_release=lambda x:self.open_menu(self.MDIconButton),
            size_hint=(None,None),
            size=(30,30),
            radius=[0,0,0,0]
        )
        self.box.add_widget(self.MDIconButton)
        if self.com:
            self.box.add_widget(self.com)
        return self.box

    def _print_widget_tree(self, widget, prefix="", is_last=True):
        """递归打印组件树，使用清晰的树形结构"""
        # 当前节点的连接符号
        connector = "└── " if is_last else "├── "
        
        # 打印当前节点信息
        node_info = f"{widget.__class__.__name__}"
        widget_id = f" id={widget.id}" if hasattr(widget, 'id') and widget.id else ""
        node_info += widget_id
        print(prefix + connector + node_info)
        
        # 准备子节点的前缀
        new_prefix = prefix + ("    " if is_last else "│   ")
        
        # 处理子节点（从最后一个子节点开始，这样显示顺序更自然）
        children = list(widget.children)
        child_count = len(children)
        
        for i, child in enumerate(reversed(children)):
            # 判断是否是最后一个子节点
            child_is_last = (i == child_count - 1)
            self._print_widget_tree(child, new_prefix, child_is_last)
    
    def on_start(self):
        super().on_start()
        self.print_component_info()
        return