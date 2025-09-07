from kivymd.uix.fitimage import FitImage
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty,ObjectProperty,NumericProperty
from components.common.callback import CallbackManager
from kivy.uix.widget import Widget

class AvatarBadge(MDBoxLayout):
    sizeVariant=StringProperty("small")
    source=StringProperty("")
    callbackManager=CallbackManager()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation="vertical"
        self.size_hint=(None,1)
        if self.sizeVariant=="small":
            l=30
            r=int(l/2)    
        elif self.sizeVariant=="medium":
            l=40
            r=int(l/2)
        elif self.sizeVariant=="large":
            l=60
            r=int(l/2)
        else:
            l=20
            r=int(l/2)
        self.adaptive_width=True
        self._image=FitImage(size=(2*r,2*r),
                            radius=[r,r,r,r],
                            size_hint=(None,None),
                            source=self.source)
        self.pos_hint={"center_x":0.5,"center_y":0.5}
        self.add_widget(self._image)
        self.add_widget(Widget(size_hint_y=1,width=10))

    def on_sizeVariant(self,instance,value):
        if self.sizeVariant=="small":
            l=30
            r=int(l/2)
        elif self.sizeVariant=="medium":
            l=40
            r=int(l/2)
        elif self.sizeVariant=="large":
            l=60
            r=int(l/2)
        else:
            l=20
            r=int(l/2)
        self.size=(l,l)
        if not hasattr(self,"_image"):
            return
        self._image.size=(l,l)
        self._image.radius=[r,r,r,r]
    
    def regerister_callback(self,callback,*args,**kwargs):
        self.callbackManager.register("callback",callback,*args,**kwargs)

    def on_source(self,instance,value):
        if not hasattr(self,"_image"):
            return
        self._image.source=self.source
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            print("AvatarBadge被点击了")
            print(f"AvatarBadge touch: pos={touch.pos}, my pos={self.pos}, size={self.size}, collide={self.collide_point(*touch.pos)}")
            self.callbackManager.trigger("callback")
            return True
        return False
            
    
