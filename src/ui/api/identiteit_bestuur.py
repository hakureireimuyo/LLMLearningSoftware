from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty,StringProperty,BooleanProperty,DictProperty,ListProperty,NumericProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.clock import Clock
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDButton

Builder.load_string('''
<BaseInputItem>:     
    orientation:'horizontal'
    MDLabel:
        text: root.title
        font_style: 'STSONG'
        role:"medium"
        size_hint_x:None
        width:"100dp"
    MDTextField:
        id:input_text
        text:"*"*len(root.content)
        readonly:True
        MDTextFieldTrailingIcon:
            id:trailing_icon
            icon: "eye-lock"
            on_touch_down: root.touch_look(*args)
                    

<InputItem>:
    orientation: 'vertical'
    radius:[dp(10),dp(10),dp(10),dp(10)]
    size_hint:1,None
    height:"300dp"
    padding:"10dp"
    md_bg_color: app.theme_cls.primaryContainerColor
    MDLabel:
        text: root.service_provider
        font_style: 'STSONG'
        role:"large"
        size_hint_y:None
        height:"50dp"
    MDBoxLayout:
        orientation:'vertical'
        id:input_items
        BaseInputItem:
            title:"应用ID"
            content:root.app_id
            callback:root.updata_app_id
        BaseInputItem:
            title:"API Key"
            content:root.api_key
            callback:root.updata_api_key
        BaseInputItem:
            title:"Secret Key"
            content:root.secret_key
            callback:root.updata_secret_key
<IdentityBestuur>:
    orientation: 'vertical'
    md_bg_color: app.theme_cls.backgroundColor
    # MDBoxLayout:
    #     size_hint: 1,None
    #     pos_hint: {"center_x":.5, "center_y":.5}
    #     height:"70dp"
    #     MDLabel:
    #         text: "身份管理"
    #         font_style: "STSONG"
    #         pos_hint: {"center_x":.5}
    MDTopAppBar:
        type: "small"
        size_hint_x: 1
        pos_hint: {"center_x": .5, "center_y": .5}

        MDTopAppBarLeadingButtonContainer:
            MDActionTopAppBarButton:
                icon: "arrow-left-bold"
                on_release: root.go_back()

        MDTopAppBarTitle:
            text: "身份管理"
            font_style: "STSONG"
            pos_hint: {"center_x": .5}

        MDTopAppBarTrailingButtonContainer:
            MDActionTopAppBarButton:
                icon: "content-save"
                on_release: root.save()
    MDScrollView:
        do_scroll_x: False
        do_scroll_y: True
        always_overscroll: True
        scroll_type: ['bars', 'content']
        pos_hint: {"center_x": .5, "center_y": .5}
        MDBoxLayout:
            orientation:'vertical'
            adaptive_height:True
            id:providers
        
''')
class BaseInputItem(MDBoxLayout):
    title=StringProperty()
    content=StringProperty()
    callback=ObjectProperty()
    #权限
    permissions=NumericProperty()
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.bind(permissions=self.on_permissions)
        

    def accept(self):
        #print(self.ids.input_text.text)
        if self.permissions==0:
            return None
        if self.ids.input_text.readonly==True:
            return None
        self.content=self.ids.input_text.text
        if self.content=='':
            self.content='None'
        if self.callback:
            self.callback(self.content)

    def on_permissions(self,*arges):
        if self.permissions==0:
            self.ids.input_text.readonly=True
            self.ids.trailing_icon.icon="eye-lock"
            self.ids.input_text.text="*"*len(self.content)
        else:
            self.ids.input_text.readonly=False
            self.ids.trailing_icon.icon="eye"
            self.ids.input_text.text=self.content    
    def touch_look(self,instance,touch):
        # print("touch_look")
        # print(instance,touch)
        if self.permissions==0:
            return None
        else:
            if instance.collide_point(*touch.pos):
                self.ids.input_text.readonly=False
                self.ids.trailing_icon.icon="eye"
                self.ids.input_text.text=self.content
            else:
                self.ids.input_text.readonly=True
                self.ids.trailing_icon.icon="eye-closed"
                self.ids.input_text.text="*"*len(self.content)
        
    def rollback(self):
        self.ids.input_text.text=self.content

class InputItem(MDBoxLayout):
    service_provider = StringProperty()
    app_id=StringProperty('')
    api_key=StringProperty('')
    secret_key=StringProperty('')
    user_id=NumericProperty()
    id=NumericProperty()
    def __init__(self,**kwargs):
        super().__init__()
        if 'app_id' in kwargs:
            if kwargs['app_id']!=None:
                self.app_id=kwargs['app_id']
            else:
                self.app_id=''
        if 'api_key' in kwargs:
            if kwargs['api_key']!=None:
                self.api_key=kwargs['api_key']
            else:
                self.api_key=''
        if 'secret_key' in kwargs:
            if kwargs['secret_key']!=None:
                self.secret_key=kwargs['secret_key']
            else:
                self.secret_key=''
        self.user_id=kwargs['user_id']
        self.id=kwargs['id']
        self.service_provider=kwargs['service_provider']
        self.orientation ='vertical'
        
    def rollback(self):
        for item in self.ids.input_items.children:
            item.rollback()
    def updata_app_id(self,app_id):
        self.app_id=app_id
        #print(app_id)

    def updata_api_key(self,api_key):
        self.api_key=api_key

    def updata_secret_key(self,secret_key):
        self.secret_key=secret_key

    def save(self):
        for item in self.ids.input_items.children:
            item.accept()

from global_instance import db_manager
from kivymd.uix.divider import MDDivider
class IdentityBestuur(MDBoxLayout):
    callback_go_back=ObjectProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dao=db_manager.get_module_dao('api_credentials')
        with self.dao.transaction():
            self.identity_bestuur=self.dao.api_credentials.get_all_user_credentials()
        #print(self.identity_bestuur)
        self.start()

    def start(self):
        self.ids.providers.clear_widgets()
        for item in self.identity_bestuur:
            self.ids.providers.add_widget(InputItem(**item))

    def save(self):
        with self.dao.transaction():
            for item in self.ids.providers.children:
                item.save()
                if item.app_id=='':
                    self.dao.api_credentials.update_app_id(item.id,'None')
                else:
                    self.dao.api_credentials.update_app_id(item.id,item.app_id)
                if item.api_key=='':
                    self.dao.api_credentials.update_api_key(item.id,'None')
                else:
                    self.dao.api_credentials.update_api_key(item.id,item.api_key)
                if item.secret_key=='':
                    self.dao.api_credentials.update_secret_key(item.id,'None')
                else:
                    self.dao.api_credentials.update_secret_key(item.id,item.secret_key)
    
    def cancel(self):
        with self.dao.transaction():
            for item in self.identity_bestuur:
                self.dao.api_credentials.update_app_id(item.id,item.app_id)
                self.dao.api_credentials.update_api_key(item.id,item.api_key)
                self.dao.api_credentials.update_secret_key(item.id,item.secret_key)
        for item in self.ids.providers.children:
            item.rollback()
    def go_back(self):
        self.cancel()
        if self.callback_go_back:
            self.callback_go_back()

from kivymd.app import MDApp
class ExampleApp(MDApp):
    def build(self):
        return IdentityBestuur()
if __name__ == '__main__':
    ExampleApp().run()