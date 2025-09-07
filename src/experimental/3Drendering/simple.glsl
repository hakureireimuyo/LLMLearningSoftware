/* simple.glsl -*/
---VERTEX SHADER-------------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

attribute vec3  v_pos;
attribute vec3  v_normal;

uniform mat4 modelview_mat;
uniform mat4 projection_mat;

varying vec3 normal_vec;
varying vec3 vertex_pos;

void main (void) {
    vec4 pos = modelview_mat * vec4(v_pos, 1.0);
    vertex_pos = pos.xyz;
    
    normal_vec = v_normal;
    
    gl_Position = projection_mat * pos;
}

---FRAGMENT SHADER-----------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

varying vec3 normal_vec;
varying vec3 vertex_pos;

void main (void){
    vec3 normal = normalize(normal_vec);
    
    vec3 light_dir = normalize(vec3(0, 0, 1)); 
    
    float diff = max(dot(normal, light_dir), 0.0);
    
    float ambient = 0.3;
    float intensity = ambient + (1.0 - ambient) * diff;
    
    gl_FragColor = vec4(vec3(intensity), 1.0);
}