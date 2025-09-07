2. Kivy 着色器的默认参数
Kivy 的着色器会自动提供以下关键变量：

变量名

类型

描述

来源

texture0

sampler2D

当前绘制的纹理

Rectangle的 texture属性

tex_coord0

varying vec2

当前片元的纹理坐标

自动计算 (0.0-1.0)

v_color

varying vec4

顶点颜色

Color指令设置的值

frag_color

out vec4

输出颜色 (GLES3)

必须赋值

gl_FragColor

vec4

输出颜色 (GLES2)

必须赋值