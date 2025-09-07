"""
管理角色数据和显示销毁回调角色设置的类
2025年3月20日 18点06分

"""
from .card import MyCard,CardManager
from .role_card import RoleCard,role_datas
from kivy.lang.builder import Builder
from kivy.properties import StringProperty,ObjectProperty
from kivy.clock import Clock
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogIcon,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogButtonContainer,
    MDDialogContentContainer,
)

Builder.load_string("""
<CardDialog>:
    size_hint:(1, 1)
    #size:("600dp", "400dp")
    # ----------------------------Icon-----------------------------
    MDDialogIcon:
        icon:"refresh"
    # -----------------------Headline text-------------------------
    MDDialogHeadlineText:
        text:"Select a scence card"
    # -----------------------Supporting text-----------------------
    # MDDialogSupportingText
    #     text:"This reloads the data and clears the conversation history, but it doesn't affect previously collected usage and learning data."
    # # -----------------------Custom content------------------------
    MDDialogContentContainer:
        id:card_manager
    MDDialogButtonContainer:
        spacing:"8dp"
        Widget:
        MDButton:
            on_release:root.on_cancel()
            MDButtonText:
                text:"Cancel"
                style:"text"
                
        MDButton:
            on_release:root.on_accept()
            MDButtonText:
                text:"Accept"
                style:"text"
               
""")

#==========Dialog不建议在ky文件中定义，当时当前类没有出现问题，暂时不修改=========
class CardDialog(MDDialog):
    def __init__(self,widgt,**kwargs):
        super().__init__(**kwargs)
        self.ids.card_manager.add_widget(widgt)
        self.select_id=widgt.get_cureent_selected_id()
        self.widgt=widgt

    def on_accept(self, *args):
        #确认选择，更新数据
        self.widgt.change_role()
        print("确认选择")
        return super().dismiss(*args)
    
    def on_cancel(self,*args):
        #取消选择，恢复到之前的状态
        if self.select_id!=self.widgt.get_cureent_selected_id():
            self.widgt.select_card_from_id(self.select_id)
        print("取消选择")
        return super().dismiss(*args)
    
    def on_dismiss(self, *args):
        #对话框关闭时，移除对话框
        self.ids.card_manager.clear_widgets()
        super().on_dismiss(*args)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            super().on_touch_down(touch)
            return True
        else:
            #关闭该组件
            self.dismiss()
            return True

class CharacterManager(RoleCard):
    callback_change_role=None

    def __init__(self, **kwargs):
        super().__init__(role_data=role_datas.get_selected_role(), **kwargs) 
        self.card_manager=CardManager(self.change_role)
        
        for id,data in role_datas.role_data.items():
            self.card_manager.add_card(id=id,text=data.name)
        Clock.schedule_once(lambda dt:self.init_item_data())

    def change_role(self,role_id:str):
        #切换角色
        print(f"切换角色{role_id}")
        self.role_id=role_id
        #print(self.role_data.to_dict())
        super().updata_role(role_datas.role_data[role_id])
        if self.parent!=None and self.callback_change_role:
            self.callback_change_role()

    def open_dialog(self):
        CardDialog(self.card_manager).open()
    
    def on_save(self):
        #保存数据后，需要同步更新role_data中的数据
        print("保存数据")
        super().get_data_from_component()
        role_datas.update_role(self.role_id, self.role_data)
        role_datas.save_to_file()

    def get_system_prompt(self):
        return self.description
    
    def get_init_text(self):
        return self.greeting_text
    
    def get_name(self):
        return self.name