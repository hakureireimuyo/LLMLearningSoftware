from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.video import Video
from kivy.uix.videoplayer import VideoPlayer
from kivy.uix.button import Button
from kivy.core.window import Window

class KivyVideoPlayer(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        
        # 创建视频播放器
        self.video = Video(
            source="D:/ProjectFloder/obs/2024-06-13 16-57-11.mp4",
            state='play',
            options={'eos': 'loop'},
        )
        
        # 创建控制面板
        control_panel = BoxLayout(size_hint_y=None, height=50, spacing=10, padding=10)
        
        # 创建控制按钮
        play_btn = Button(text='播放')
        play_btn.bind(on_press=self.play_video)
        
        pause_btn = Button(text='暂停')
        pause_btn.bind(on_press=self.pause_video)
        
        stop_btn = Button(text='停止')
        stop_btn.bind(on_press=self.stop_video)
        
        # 添加到控制面板
        control_panel.add_widget(play_btn)
        control_panel.add_widget(pause_btn)
        control_panel.add_widget(stop_btn)
        
        # 添加到主布局
        layout.add_widget(self.video)
        layout.add_widget(control_panel)
        
        return layout
    
    def play_video(self, instance):
        self.video.state = 'play'
    
    def pause_video(self, instance):
        self.video.state = 'pause'
    
    def stop_video(self, instance):
        self.video.state = 'stop'

if __name__ == '__main__':
    KivyVideoPlayer().run()