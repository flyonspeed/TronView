---vertex
attribute vec3 my_vertex_position;

uniform mat4 center_the_sphere;
uniform mat4 my_rotation;
uniform mat4 my_view;
uniform mat4 my_proj;

void main()
{
    gl_Position = my_proj * my_view * my_rotation * center_the_sphere *
                            vec4(my_vertex_position,1);
}

---fragment

void main()
{
    gl_FragColor = vec4(0.3, 0.6, 1.0, 1);  // Light blue color for the sphere
}