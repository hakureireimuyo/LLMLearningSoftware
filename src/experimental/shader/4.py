from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import RenderContext, Color, Rectangle, Rotate,PushMatrix,PopMatrix
from kivy.clock import Clock

shader_code = '''
$HEADER$
uniform float time;

void main(void) {
    // 应用矩阵变换到片段坐标
    vec4 pos = frag_modelview_mat * gl_FragCoord;
    
    // 创建动态效果（基于变换后的坐标）
    float r = abs(sin(pos.x * 0.02 + time));
    float g = abs(sin(pos.y * 0.02 + time));
    
    gl_FragColor = vec4(r, g, 1.0, 1.0) * 
                  frag_color * 
                  texture2D(texture0, tex_coord0);
}
'''

class AdvancedShaderWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 创建支持矩阵传递的渲染上下文
        self.canvas = RenderContext(
            use_parent_projection=True,
            use_parent_modelview=True,
            use_parent_frag_modelview=True
        )
        self.canvas.shader.fs = shader_code
        self.size = (400, 400)
        # 定期更新时间
        Clock.schedule_interval(self.update_time, 1/60)
        
        with self.canvas.before:
            # 应用45度旋转到片段坐标
            PushMatrix(stack='frag_modelview_mat')
            Rotate(angle=45, origin=(200, 150), stack='frag_modelview_mat')
        
        with self.canvas:
            Color(1, 1, 1)
            Rectangle(pos=(0, 0), size=self.size)
        
        with self.canvas.after:
            PopMatrix(stack='frag_modelview_mat')

    def update_time(self, dt):
        self.canvas['time'] = Clock.get_boottime()

class TestApp(App):
    def build(self):
        return AdvancedShaderWidget()

if __name__ == '__main__':
    TestApp().run()