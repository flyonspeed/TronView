---VERTEX SHADER-------------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

attribute vec3  v_pos;
uniform mat4 modelview_mat;
uniform mat4 projection_mat;

void main (void) {
    vec4 pos = projection_mat * modelview_mat * vec4(v_pos, 1.0);
    gl_Position = pos;
}

---FRAGMENT SHADER-----------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

void main (void) {
    gl_FragColor = vec4(1.0, 1.0, 1.0, 1.0);  // White color for wireframe
}
