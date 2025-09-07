import sys
from pathlib import Path
# 自动添加项目根目录和 src 目录
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / "src"))

from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from src.behavior.markdowntomarkup import MarkdownToKivyMarkupMixin
from kivymd.uix.label import MDLabel
from src.app import TestApp

class MarkdownLabel(MarkdownToKivyMarkupMixin, MDLabel):
    pass

class MarkdownDemoApp(TestApp):
    def build(self):
        # 使用 Markdown 文本
        markdown_text = """
# 标题 1
## 标题 2

这是一个 **粗体** 文本的例子，以及 *斜体* 文本。

列表示例:
- 项目 1
- 项目 2
- 项目 3

链接示例:
访问 [Kivy 官网](https://kivy.org) 或者直接打开 https://google.com

代码示例:
行内代码: `print("Hello, World!")`

删除线示例: ~~已删除的文本~~

下划线示例: <u>带下划线的文本</u>

引用示例:
> 这是引用的文本
> 多行引用

特殊字符转义: \\* \\_ \\[ \\] \\&
        """.strip()
        
        # 创建支持 Markdown 的标签
        label = MarkdownLabel(
            original_text=markdown_text,
            md_bg_color=(1, 1, 1, 1), 
            use_markdown=True,
            size_hint=(1, 1),
            valign='top',
            font_style='STSONG',
            role='small',
            halign='left',
            markup=True)
        self.com=label
        return self.com

if __name__ == '__main__':
    # 未通过测试，后续再修复
    # 2025年6月2日
    MarkdownDemoApp().run()