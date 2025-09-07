import threading
from kivy.clock import Clock, mainthread
from kivy.uix.widget import Widget
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty
from .chat_input import ChatInput,TooltipMDIconButton
from .user_and_message import UserAndMessage
from ...tools.interface.chat_and_api_interface import ChatAndAPIInterface
from .chat_setting import ChatSetting
from kivy.animation import Animation
from .character_setting.card import MyCard,CardManager
from .character_setting.role_card import  RoleCard, LoadRoleCard
from .character_setting.character_manager import CharacterManager
from core.tools.extract_words import auto_statistics
from .guiding_word import GudiingWordManager
from core.kivymd_component.slide_drawer import SlideDrawer
KV = """
<ChatMessageScoll>:
    id: chat_message_loader
    md_bg_color: app.theme_cls.backgroundColor
    MDNavigationLayout:
        id: nav_layout
        MDScreenManager:
            id: chat_message_screen_manager
            MDScreen:
                name: "chat_message_screen"
                MDBoxLayout:
                    orientation: "vertical"
                    size_hint_y: 1
                    md_bg_color: app.theme_cls.inverseOnSurfaceColor
                    MDNavigationBar:
                        id: chat_message_navigation_bar
                        set_bars_color: True
                        size_hint_y: None
                        height: "56dp"
                        padding: "12dp",0,"12dp",0
                        elevation: 4
                        MDLabel:
                            id: chat_name
                            text: root.name
                            font_style: "STSONG"
                            size_hint_x: None
                            width: "200dp"
                            valign: "center"
                            halign: "left"
                            size_hint_y: None
                            height: "56dp"
                        MDLabel:
                            text:root.scence_name
                            font_style: "STSONG"
                            valign: "center"
                            halign: "center"
                            size_hint_y: None
                            height: "56dp"
                            md_bg_color: app.theme_cls.secondaryContainerColor
                        MDNavigationItem:
                            size_hint_x: None
                            width: "64dp"
                            on_release: root.get_history()
                            MDNavigationItemIcon:
                                icon: "history"
                            
                        MDNavigationItem:
                            size_hint_x: None
                            width: "64dp"
                            on_release: chat_message_screen_manager.current ="character_setting_screen"
                            MDNavigationItemIcon:
                                icon: "account-box"
                            
                        MDNavigationItem:
                            size_hint_x: None
                            width: "64dp"
                            on_release: root.open_dialog()
                            MDNavigationItemIcon:
                                icon: "cards"
                            
                        MDNavigationItem:
                            size_hint_x: None
                            width: "64dp"
                            on_release: chat_message_screen_manager.current ="system_setting_screen"
                            MDNavigationItemIcon:
                                icon: "cogs"
                        MDNavigationItem:
                            size_hint_x: None
                            width: "64dp"
                            on_release: root.ids.slide_drawer.change()
                            MDNavigationItemIcon:
                                icon: "cogs"
                         
                    MDBoxLayout:
                        orientation: "horizontal"
                        size_hint:[1,1]
                        MDBoxLayout:
                            orientation: "vertical"
                            MDBoxLayout:
                                orientation: "horizontal"
                                size_hint: 1,1
                                MDScrollView:
                                    id: scroll_view
                                    do_scroll_x: False
                                    do_scroll_y: True
                                    always_overscroll: True
                                    bar_width: dp(3)
                                    scroll_type: ['bars', 'content']
                                    MDBoxLayout:
                                        orientation: "horizontal"
                                        MDBoxLayout:
                                            #md_bg_color: "red"
                                            id: chat_message_recycle_view
                                            padding: "500dp","20dp","30dp","20dp"#这里一直存在问题,也许该使用锚定布局
                                            orientation: "vertical"
                                            adaptive_height: True
                                            spacing: dp(50)
                                        GudiingWordManager:
                                            id: guiding_word_manager
                                            callback:root.input_guiding_word
                                SlideDrawer:
                                    id: slide_drawer
                                    size_hint_max_x: dp(200)
                            ChatInput:
                                id: chat_input
                                callback: root.add_user_input_message      
            MDScreen:
                name: "character_setting_screen"
                CharacterManager:
                    id: character_manager
                    callback: root.go_back_to_chat_message_screen
                    callback_change_role:root.switch_chat_partners
            MDScreen:
                name: "system_setting_screen"
                MDBoxLayout:
                    orientation: "vertical"
                    size_hint: 1,1
                    md_bg_color: app.theme_cls.inverseOnSurfaceColor
                    MDTopAppBar:
                        type: "small"
                        MDTopAppBarLeadingButtonContainer:
                            MDActionTopAppBarButton:
                                icon: "arrow-left-bold"
                                on_release: root.go_back_to_chat_message_screen()
                        MDTopAppBarTitle:
                            text: "System Settings"
                            pos_hint: {"center_x": .5}
                    MDScrollView:
                        do_scroll_x: False
                        do_scroll_y: True
                        always_overscroll: True
                        ChatSetting:
                            id: chat_setting 
"""
Builder.load_string(KV)

from kivymd.uix.navigationdrawer import (
    MDNavigationDrawerItem, MDNavigationDrawerItemTrailingText
)
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, ColorProperty

class CustomSwitch(MDSwitch):
    callback=ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def on_active(self, instance_switch, active_value):
        if self.callback:
            self.callback(active_value)

class ChatMessageScoll(MDBoxLayout):
    name = StringProperty("")
    color = StringProperty("red")
    init_text=StringProperty("初始信息为空")
    is_focus = BooleanProperty(False)
    scence_name=StringProperty("")
    auto_tts=BooleanProperty(True)
    auto_guiding=BooleanProperty(True)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._current_ai_widget = None  # 当前正在更新的AI消息组件
        self._stream_task = None        # 当前异步任务
        self.chat_api = ChatAndAPIInterface()
        self.chat_guiding=ChatAndAPIInterface()
        self.check_the_content_ai=ChatAndAPIInterface()
        self.is_frist_message=True
        self.on_start()
        self.set_api_moudel(zhipu_group.create_instance("glm-4-plus"),
                            zhipu_group.create_instance("glm-4-flash"))
        self.init_message()

    def on_start(self):
        #初始化完成后调用设置各种参数和回调
        #在输入栏上方添加小按钮
        self.ids.chat_input.ids.button_container.add_widget(TooltipMDIconButton(icon="delete",text_tool="删除",callback=self.clear_chat_message))
        self.ids.chat_input.ids.button_container.add_widget(TooltipMDIconButton(icon="camera",text_tool="相机",callback=lambda:print("相机")))
        self.ids.chat_input.ids.button_container.add_widget(TooltipMDIconButton(icon="image",text_tool="图片",callback=lambda:print("图片")))
        self.ids.chat_input.ids.button_container.add_widget(TooltipMDIconButton(icon="reload",text_tool="重加载引导",callback=lambda:self.get_guiding_word()))
        #空组件
        self.ids.chat_input.ids.button_container.add_widget(Widget())
        #switch
        self.ids.chat_input.ids.button_container.add_widget(CustomSwitch(callback=self.set_suto_guiding))
        self.ids.chat_input.ids.button_container.add_widget(CustomSwitch(callback=self.set_suto_tts))
        #设置通用数据模板
        chat_name=user_data.data.get('username','')
        self.kwargs = {
            'text': '',
            'transition_text': "",
            'transition_position': 'float',
            'transition_level': 'sentence',
            'voice': '',
            'message_id': 1,
            'is_new': False,
            'identity': '',
            'chat_name': chat_name,
            'image_list': [],
            'icon': 'account',
            'callback': lambda: print("No bind function"),
            'auto_update_text_layout':False,
        }

    def set_suto_tts(self,*arges):
        self.auto_tts=not self.auto_tts
        print(f"设置自动tts为{self.auto_tts}")

    def set_suto_guiding(self,*arges):
        self.auto_guiding=not self.auto_guiding
        print(f"设置自动引导词为{self.auto_guiding}")

    def set_api_moudel(self, moudel,moedel2,moedel3=None):
        print("注入api")
        self.chat_api.set_provider(moudel)
        self.chat_guiding.set_provider(moedel2)
        if moedel3:
            self.check_the_content_ai.set_provider(moedel3)
        #print(self.check_the_content_ai.have_provider())
        #print("ui实例通过接口调用")
        #print(self.chat_api.get_config())
        print("注入完成")

    def chack_ids(self):
        print("_____变量内容________")
        print(self.name)
        print("_____字典内容_________")
        print(self.ids)

    def _create_message_widget(self, text, is_user):
        """创建消息组件（根据实际组件类修改）"""
        temp=self.kwargs
        temp['text']=text
        temp['identity']='User' if is_user else 'Ai'
        return UserAndMessage(**temp)

    def add_user_input_message(self, text):
        """添加用户消息并触发AI响应"""
        if text == "":
            print(f"{self.name}:未输入有效内容")
            return False
        # 添加用户消息组件
        user_widget = self._create_message_widget(text, is_user=True)
        user_widget.ids.text_label.update_char_layout(None)#更新文字布局，实现鼠标选取文字功能
        self._add_to_scrollview(user_widget)
        #统计输入数据
        auto_statistics(text,"input")
        #print("开始添加ai消息")
        # 添加初始AI消息组件
        ai_widget = self._create_message_widget("", is_user=False)
        self._add_to_scrollview(ai_widget)
        self._current_ai_widget = ai_widget
        threading.Thread(target=self._add_ai_message, args=(text,)).start()
        # 启动异步任务

    def _add_ai_message(self, text):
        try:
            print(f"有效内容判定-{self.name}:{text}")
            #检查用户输入的消息是否合法
            if self.check_the_content_ai.have_provider():
                response=self.check_the_content_ai.chat_sync(text, stream=False)
                if response.choices[0].message.content=="True":
                    pass
                else:
                   text=response.choices[0].message.content
                   #print(text)

            #ai开始回答
            response = self.chat_api.chat_sync(text, stream=True)
            full_content = []  # 存储完整内容的列表
            temp_buffer = ""   # 临时缓冲区
            
            for result in response:
                # 获取增量内容
                delta_content = getattr(result.choices[0].delta, 'content', '') or ''
                
                # 合并到缓冲区
                temp_buffer += delta_content
                
                # 当缓冲区达到阈值或收到完整句子时更新
                if len(temp_buffer) >= 20 or '.' in delta_content:
                    # 使用闭包捕获当前缓冲区内容
                    def update_closure(content, buffer):
                        def wrapper(dt):
                            self._update_ai_text(content)
                            buffer[0] = ''  # 清空已处理内容
                        return wrapper
                    
                    # 使用列表包装实现可修改的闭包
                    buffer_wrapper = [temp_buffer]
                    Clock.schedule_once(update_closure(buffer_wrapper[0], buffer_wrapper), 0.01)
                    full_content.append(temp_buffer)
                    temp_buffer = ""  # 重置缓冲区

            # 处理剩余内容
            if temp_buffer:
                Clock.schedule_once(lambda dt: self._update_ai_text(temp_buffer), 0.01)
                full_content.append(temp_buffer)

            # 最终合并完整内容
            @mainthread
            def final_update():
                """更新当前ai回答的文本布局信息"""
                self._current_ai_widget.ids.text_label.update_char_layout(None)
            Clock.schedule_once(lambda dt: final_update(),0.05)
            #是否开启自动播放
            print(f"自动播放：{self.auto_tts}")
            if self.auto_tts:
                self._current_ai_widget.on_voice_get(None,None)
            #将ai的回答更新进入历史记录
            assistant_msg = {"role": "assistant", "content": "".join(full_content)}
            self.chat_api._provider.historical_dialogue.append(assistant_msg)
            self.chat_api._provider._update_usage(assistant_msg["content"])
            #self.chat_api._process_response(response=response)
            # 统计字数
            Clock.schedule_once(lambda dt: self.thead_add_ai_message("".join(full_content)), 0.01)
            
            #开始获得引导词
            if self.auto_guiding:
                Clock.schedule_once(lambda dt: self.Guiding_word("".join(full_content)), 0.1)
        except Exception as e:
            print(f"对话过程中发生异常: {e}")

    def get_guiding_word(self):
        Clock.schedule_once(lambda dt: self.Guiding_word(self._current_ai_widget.text), 0.1)

    def thead_add_ai_message(self, text):
        """由于SQLite不允许跨越线程访问，因此这里使用线程进行异步操作"""
        auto_statistics(text,"see")

    def get_history(self):
        """获取历史对话"""
        print(f"聊天记录框：{self.name}的历史记录")
        print(self.chat_api.get_history())
        return None
    
    def _add_to_scrollview(self, widget):
        """将组件添加到滚动视图，并且滚动到底部"""
        if self.is_frist_message:
            # 如果是第一次添加消息，不将其滚动到底部
            self.is_frist_message=False
            self.ids.chat_message_recycle_view.add_widget(widget)
            return None
        self.ids.chat_message_recycle_view.add_widget(widget)
        Clock.schedule_once(lambda dt: self._scroll_to_bottom(), 0.1)

    def _scroll_to_bottom(self):
        """滚动到底部"""
        #print(self.ids.scroll_view.viewport_size)
        if self.ids.scroll_view.viewport_size[1]>self.ids.scroll_view.height:
            self.ids.scroll_view.scroll_y = 0

    def delete_all_message(self):
        """删除所有消息"""
        self.ids.chat_message_recycle_view.clear_widgets()
    
    @mainthread
    def _update_ai_text(self, text):
        """线程安全的UI更新方法"""
        if self._current_ai_widget:
            # 追加而不是替换内容
            #current = self._current_ai_widget.get_text()
            self._current_ai_widget.add_text( text)
            
            # 自动滚动到底部
            self._scroll_to_bottom()

    def switch_chat_partners(self):
        """切换聊天对象"""
        #保存当前信息进入历史记录
        ...
        #清空聊天框
        self.delete_all_message()
        #加载角色数据
        self.chat_api.clear_history()
        self.chat_guiding.clear_history()
        self.init_message()
        print("当前选择的角色信息")
        print(self.ids.character_manager.get_data())

    def input_guiding_word(self,instance,text):
        """输入引导词"""
        self.ids.chat_input._insert_text(text)
        #self.ids.chat_input.ids.input_field.focus=True #不起作用

    def _show_error(self, error_msg):
        """显示错误信息"""
        if self._current_ai_widget:
            self._current_ai_widget.show_error(error_msg)

    def _finalize_message(self):
        """完成消息处理"""
        self._current_ai_widget = None
        self._stream_task = None

    def on_leave(self, *args):
        """离开页面时取消未完成的任务"""
        if self._stream_task and not self._stream_task.done():
            self._stream_task.cancel()

    def init_message(self):
        """
        添加初始消息，用于初始化对话
        初始消息由设定文本发出,属于固定开头
        随后会启动引导ai，添加引导词
        """
        username=user_data.data.get('username','')
        self.scence_name=self.ids.character_manager.get_name()
        self.chat_api.set_system_prompt(f"用户当前的名字叫做{username},你需要遵循以下设定开始场景对话："+self.ids.character_manager.get_system_prompt())
        text=f"""
以下是具体任务说明：
随后将会输入用户的句子，你需要根据该句子，带入当前角色的视角，对用户说一句话。
你的任务是带入用户的视角，对上述句子给出三条相关的英文回答，每条使用换行分割。
只返回回答，其他都不要返回。只返回回答的句子，只返回三条句子。只回答最近的一条句子。
当话题结束的时候返回END。
请让相关的回答尽可能围绕该场景进行，以下是当前聊天的场景设定:
            """+self.ids.character_manager.get_scence()
        #print(text)
        self.chat_guiding.set_system_prompt(text)
        #=============获取初始对话===============
        ai_widget = self._create_message_widget("", is_user=False)
        self.is_frist_message=True
        self._add_to_scrollview(ai_widget)
        self._current_ai_widget = ai_widget
        threading.Thread(target=self._add_ai_message, args=("请你带入当前身份，对用户说开场对白",)).start()
        #检查输入合法的ai初始化
        if self.check_the_content_ai.have_provider():
            self.check_the_content_ai.set_system_prompt("""
            你的任务是检查用户输入的信息是否符合以下规范,完全符合所有规范则返回字符串True,否则就修改输入，让话题只关于以下的内容：
            不得违反以下规则"""+self.ids.character_manager.get_restraint())

    def Guiding_word(self,text):
        """
        引导ai，添加引导词,额外线程等待数据返回
        """
        def fun(text):
            response=self.chat_guiding.chat_sync(text, stream=False)
            text=response.choices[0].message.content
            Clock.schedule_once(lambda dt: self.ids.guiding_word_manager.add_word(text),0.1)
            #print(self.chat_guiding.get_history())
        threading.Thread(target=fun,args=(text,)).start()

    def open_dialog(self):
        """
        打开对话框，用于切换角色
        """
        #打开切换面板
        self.ids.character_manager.open_dialog()

    def go_back_to_chat_message_screen(self):
        """
        从角色设置界面返回聊天界面
        """
        self.ids.chat_message_screen_manager.current = "chat_message_screen"

    def clear_chat_message(self):
        #清空对话记录，但是保留初始设定
        pass
    
from global_instance import api_manager

class ExampleApp(MDApp):
    def build(self):
        temp=ChatMessageScoll()
        zhipu=api_manager.get_group("zhipu")
        model=zhipu.get_model("glm-4-flash")
        temp.set_api_moudel(model)
        return temp

    def on_start(self):
        message_data = {
            'text': '[color=#ff0000]hello world[/color]\n    你好世界This is an indented line.[color=#ff0000][ref=hello]link[/ref][/color]aaa aaaa aaaaa aaaaa aaaaaa aaaaa aaaaa.This is an indented line.aaa1 aaa2a aaaa3a aaaaa4 aaaaaa5 aaaaa aaaaa.This is an indented line.aaa aaaa aaaaa aaaaa aaaaaa aaaaa aaaaa',
            'transition_text': "",
            'transition_position': 'float',
            'transition_level': 'sentence',
            'voice': '',
            'message_id': 1,
            'is_new': False,
            'identity': 'User',
            'chat_name': 'User',
            'image_list': [],
            'icon': 'account',
            'callback': lambda: print("No bind function")
        }
        temp=UserAndMessage(**message_data)

        self.root.ids.chat_message_recycle_view.add_widget(temp)
        
        message_data = {
            'text': '[color=#ff0000]hello world[/color]\n    你好世界',
            'transition_text': "",
            'transition_position': 'float',
            'transition_level': 'sentence',
            'voice': '',
            'message_id': 1,
            'is_new': False,
            'identity': 'Ai',
            'chat_name': 'User',
            'image_list': [],
            'icon': 'account',
            'callback': lambda: print("No bind function")
        }
        temp=UserAndMessage(**message_data)
        self.root.ids.chat_message_recycle_view.add_widget(temp)
        return super().on_start()
    
    
if __name__ == "__main__":
    ExampleApp().run()