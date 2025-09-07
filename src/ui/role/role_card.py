"""
当前组件是专门为了给聊天角色添加人物设定和剧情走向而设定的组件
可以动态的添加和删除新的设定，包含了读取和保存功能
并且有专门的组件UI来展示和进行交互，主要的功能是设定不同的角色和剧情走向
用户可以自己添加新的角色卡片

2025年3月18日 01点53分

"""
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.screen import MDScreen
from kivy.properties import ListProperty, ObjectProperty, StringProperty, BooleanProperty, NumericProperty, DictProperty, OptionProperty
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.animation import Animation
from typing import Union
from kivy.lang import Builder
from kivymd.app import MDApp
import json

# class RoleData:
#     """
#     角色数据实体类，封装角色设定信息的领域模型
#     """
#     def __init__(self, id: str, config: dict):
#         """
#         通过配置字典构造角色数据
#         :param id: 角色唯一标识符
#         :param config: 包含角色属性的字典
#         """
#         self.id = id
#         self.name = config.get('name', 'Unnamed')
#         self.description = config.get('description', '')
#         self.image_source = config.get('image_source', 'default.png')
#         self.end_condition = config.get('end_condition', 'normal')
#         self.restraint = config.get('restraint', '')
#         self.the_direction_of_the_plot = config.get('the_direction_of_the_plot', '')
#         self.greeting_text=config.get('greeting_text','')
#         self.scence=config.get('scence','')

#     def to_dict(self) -> dict:
#         """
#         将对象转换为字典格式（用于序列化）
#         """
#         return {
#             'name': self.name,
#             'description': self.description,
#             'image_source': self.image_source,
#             'scence': self.scence,
#             'end_condition': self.end_condition,
#             'restraint': self.restraint,
#             'the_direction_of_the_plot': self.the_direction_of_the_plot,
#             'greeting_text':self.greeting_text
#         }

#     def __repr__(self):
#         return f"<RoleData {self.id}: {self.name}>"
    
import json
from typing import Union

class RoleData:
    def __init__(self, role_id: str, config: dict):
        self.id = role_id
        # 使用get方法避免KeyError，并提供默认值
        self.name = config.get('name', '')
        self.description = config.get('description', '')
        self.image_source = config.get('image_source', '')
        self.end_condition = config.get('end_condition', '')
        self.restraint = config.get('restraint', '')
        self.the_direction_of_the_plot = config.get('the_direction_of_the_plot', '')
        self.greeting_text = config.get('greeting_text', '')  # 新增字段
        self.scence=config.get('scence','')

    def get(self, key: str, default: Union[str, None] = None) -> Union[str, None]:
        """获取属性值，如果不存在则返回默认值"""
        return getattr(self, key, default)
    
    def to_dict(self) -> dict:
        """将数据序列化为字典"""
        return {
            'name': self.name,
            'description': self.description,
            'image_source': self.image_source,
            'scence': self.scence,
            'end_condition': self.end_condition,
            'restraint': self.restraint,
            'the_direction_of_the_plot': self.the_direction_of_the_plot,
            'greeting_text': self.greeting_text
        }

class LoadRoleCard:
    def __init__(self, file_path: str = "src\\core\\kivymd_component\\chat_component\\character_setting\\roles.json"):
        self.file_path = file_path
        self.role_data = {}  # 存储角色数据的字典
        self.selected = ""   # 当前选中的角色ID
        self._dirty = False  # 标记是否有未保存的更改
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
                # 解析selected字段
                self.selected = raw_data.get('selected', '')
                # 解析roles字段
                roles = raw_data.get('roles', {})
                for role_id, config in roles.items():
                    self.role_data[role_id] = RoleData(role_id, config)
                if self.selected==None or self.role_data==None:    
                    raise ValueError("文件读取失败，检查路径和文件")
        except FileNotFoundError:
            print(f"Warning: {file_path} not found, initialized empty data")
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in {file_path}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")

    # 新增selected字段操作方法
    def set_selected_role(self, role_id: str):
        """设置当前选中的角色"""
        if role_id in self.role_data or role_id == "":
            self.selected = role_id
            self._dirty = True
        else:
            print(f"Error: Role {role_id} does not exist")

    def get_selected_role(self) -> Union[RoleData, None]:
        """获取当前选中的角色对象"""
        print("===================")
        print(self.selected)
        print(self.role_data)
        return self.role_data.get(self.selected)

    # 修改后的保存方法
    def save_to_file(self):
        print("试图保存数据")
        if not self._dirty:
            return
        serialized = {
            "selected": self.selected,
            "roles": {
                role_id: data.to_dict() 
                for role_id, data in self.role_data.items()
            }
        }

        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(serialized, f, indent=2, ensure_ascii=False)
            self._dirty = False
            #print(serialized)
            print("Data saved successfully")
        except IOError as e:
            print(f"Error saving data: {str(e)}")

    # 其他原有方法保持不变...
    def get_role(self, role_id: str) -> Union[RoleData, None]:
        return self.role_data.get(role_id)

    def add_role(self, role_id: str, role_data: RoleData):
        if role_id not in self.role_data:
            self.role_data[role_id] = role_data
            self._dirty = True
        else:
            print(f"Role {role_id} already exists")

    def update_role(self, role_id: str, role_data: RoleData):
        if role_id in self.role_data:
            self.role_data[role_id] = role_data
            self._dirty = True
            #print(role_data.to_dict())
        else:
            print(f"Role {role_id} not found")

    def remove_role(self, role_id: str):
        if role_id in self.role_data:
            del self.role_data[role_id]
            # 如果删除的是当前选中角色，清空选中状态
            if self.selected == role_id:
                self.selected = ""
            self._dirty = True
        else:
            print(f"Role {role_id} not found")

    def is_dirty(self):
        return self._dirty
    
    def __del__(self):
        # 在对象销毁时自动保存数据
        #print("对象销毁")
        if self._dirty:
            #print("回写数据")
            self.save_to_file()

role_datas=LoadRoleCard()

Builder.load_string("""
<ItemData>:
    orientation: 'vertical'
    adaptive_height: True
    MDLabel:
        id:title
        text: root.title
        font_style: "STSONG"
        size_hint_y: None
        height: dp(25)
    MDTextField:
        id: content
        font_name: "STSONG"
        text: root.content
        multiline: True
        size_hint_y: None
        font_size: "25sp"
    MDDivider:
        size_hint_y: None
        height: dp(1)
                    
<RoleCard>:
    orientation: 'vertical'
    MDTopAppBar:
        type: "small"
        size_hint_x: .8
        pos_hint: {"center_x": .5, "center_y": .5}

        MDTopAppBarLeadingButtonContainer:

            MDActionTopAppBarButton:
                icon: "arrow-left-bold"
                on_release: root.go_back()

        MDTopAppBarTitle:
            text: "对话场景设定"
            font_style: "STSONG"
            pos_hint: {"center_x": .5}

        MDTopAppBarTrailingButtonContainer:

            MDActionTopAppBarButton:
                icon: "account-circle-outline"
    MDScrollView:
        do_scroll_x: False,
        do_scroll_y: True,
                    
        MDBoxLayout:
            id: box_layout
            orientation: 'vertical'
            size_hint:1,1
            padding: [dp(20), 0, dp(20), 0]
            spacing: dp(30)
            md_bg_color:self.theme_cls.backgroundColor
            adaptive_height: True
        
    MDBoxLayout:
        size_hint: None, None
        size: dp(100), dp(100)
        spacing: dp(10)
        pos_hint: {'center_x': 0.5}
        padding: [0, dp(10), 0, 0]

        MDIconButton:
            icon: "content-save"
            theme_text_color: "Custom"
            text_color: app.theme_cls.primaryColor
            on_release: root.on_save()

        MDIconButton:
            icon: "close"
            theme_text_color: "Custom"
            text_color: app.theme_cls.errorColor
            on_release: root.on_cancel()
""")

class ItemData(MDBoxLayout):
    title=StringProperty()
    content=StringProperty()
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

class RoleCard(MDBoxLayout):
    """
    角色卡片组件，用于展示角色的基本信息和设定,此处是交互组件
    """
    role_data=ObjectProperty(RoleData)
    callback=None

    def __init__(self,role_data:RoleData,**kwargs):
        """
        初始化角色卡片
        :param role_id: 角色ID"""
        super().__init__(**kwargs)
        self.do_scroll_x= False,
        self.do_scroll_y= True,
        self.role_data=role_data
        
        self.role_id=role_data.id
        self.name=role_data.name
        self.description=role_data.description
        self.scence=role_data.scence
        self.image_source=role_data.image_source
        self.end_condition=role_data.end_condition
        self.restraint=role_data.restraint
        self.the_direction_of_the_plot=role_data.the_direction_of_the_plot
        self.greeting_text=role_data.greeting_text 

    def updata_role(self,role_data:RoleData):
        #从单个内容更新角色数据
        self.role_data=role_data
        self.role_id=role_data.id
        self.name=role_data.name
        self.description=role_data.description
        self.scence=role_data.scence
        self.image_source=role_data.image_source
        self.end_condition=role_data.end_condition
        self.restraint=role_data.restraint
        self.the_direction_of_the_plot=role_data.the_direction_of_the_plot
        self.greeting_text=role_data.greeting_text 
        self.init_item_data()

    def get_data_from_component(self):
        #从组件中获取数据
        self.name=self.role_name_com.ids.content.text
        self.description=self.llm_setting_com.ids.content.text
        self.scence=self.scence_com.ids.content.text
        self.restraint=self.restraint_com.ids.content.text
        self.the_direction_of_the_plot=self.the_direction_of_the_plot_com.ids.content.text
        self.greeting_text=self.greeting_text_com.ids.content.text
        self.end_condition=self.end_condition_com.ids.content.text

        self.role_data=RoleData(self.role_id,
                                {"name":self.name,
                                 "description":self.description,
                                 "scence":self.scence,
                                 "restraint":self.restraint,
                                 "the_direction_of_the_plot":self.the_direction_of_the_plot,
                                 "greeting_text":self.greeting_text,
                                 "end_condition":self.end_condition})
        print(self.role_data.to_dict())
        
    def init_item_data(self):
        #更新角色数据
        self.ids.box_layout.clear_widgets()
        #初始化数据
        self.role_name_com=ItemData(title="场景名称",content=self.name)
        self.ids.box_layout.add_widget(self.role_name_com)
        self.llm_setting_com=ItemData(title="大语言模型角色设定",content=self.description)
        self.ids.box_layout.add_widget(self.llm_setting_com)
        self.scence_com=ItemData(title="场景设定",content=self.scence)
        self.ids.box_layout.add_widget(self.scence_com)
        self.restraint_com=ItemData(title="限制规范",content=self.restraint)
        self.ids.box_layout.add_widget(self.restraint_com)
        self.the_direction_of_the_plot_com=ItemData(title="剧情走向",content=self.the_direction_of_the_plot)
        self.ids.box_layout.add_widget(self.the_direction_of_the_plot_com)
        self.greeting_text_com=ItemData(title="初始对话",content=self.greeting_text)
        self.ids.box_layout.add_widget(self.greeting_text_com)
        self.end_condition_com=ItemData(title="结束条件",content=self.end_condition)
        self.ids.box_layout.add_widget(self.end_condition_com)
        

    def set_callback(self,callback):
        self.callback=callback

    def go_back(self):
        #通过回调返回上一个界面
        if self.callback:
            self.callback()
    def on_save(self):
        """
        保存角色设定
        """
        pass
    def on_cancel(self):
        """
        取消编辑，恢复原始状态
        """
        self.name=self.role_data.name
        self.description=self.role_data.description
        self.scence=self.role_data.scence
        self.image_source=self.role_data.image_source
        self.end_condition=self.role_data.end_condition
        self.restraint=self.role_data.restraint
        self.the_direction_of_the_plot=self.role_data.the_direction_of_the_plot
        self.greeting_text=self.role_data.greeting_text 
    
    def get_data(self):
        return self.role_data.to_dict()
    
    def get_scence(self):
        return self.scence
    def get_restraint(self):
        return self.restraint
    
class Expmal(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"  # 设置主色调为蓝色
        self.theme_cls.theme_style = "Light"  # 设置主题风格为浅色
        self.theme_cls.primary_hue = "500"  # 设置主色调的亮度
        return RoleCard(role_datas.get_role("1"))
    
if __name__ == "__main__":
    Expmal().run()