#version 330 core
in vec2 tex_coord;
out vec4 frag_color;
uniform sampler2D source_texture;
uniform float sigma;      // 模糊强度
uniform vec2 texture_size; // 纹理尺寸

void main() {
    vec4 color = vec4(0.0);
    float total_weight = 0.0;
    int kernel_size = int(sigma * 3.0) * 2 + 1; // 动态核大小

    for (int i = -kernel_size/2; i <= kernel_size/2; i++) {
        float weight = exp(-0.5 * pow(float(i)/sigma, 2.0));
        vec2 offset = vec2(0.0, float(i)/texture_size.y)
        color += texture(source_texture, tex_coord + offset) * weight;
        total_weight += weight;
    }
    frag_color = color / total_weight;
}