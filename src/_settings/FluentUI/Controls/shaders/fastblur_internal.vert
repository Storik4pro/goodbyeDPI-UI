#version 440

layout(location = 0) in vec4 qt_Vertex;
layout(location = 1) in vec2 qt_MultiTexCoord0;

layout(location = 0) out vec2 qt_TexCoord0;
layout(location = 1) out vec2 qt_TexCoord1;
layout(location = 2) out vec2 qt_TexCoord2;
layout(location = 3) out vec2 qt_TexCoord3;

layout(std140, binding = 0) uniform buf {
    mat4 qt_Matrix;
    float qt_Opacity;
    float xStep;
    float yStep;
};

out gl_PerVertex { vec4 gl_Position; };

void main()
{
    qt_TexCoord0 = vec2(qt_MultiTexCoord0.x + xStep, qt_MultiTexCoord0.y + yStep * 0.36);
    qt_TexCoord1 = vec2(qt_MultiTexCoord0.x + xStep * 0.36, qt_MultiTexCoord0.y - yStep);
    qt_TexCoord2 = vec2(qt_MultiTexCoord0.x - xStep * 0.36, qt_MultiTexCoord0.y + yStep);
    qt_TexCoord3 = vec2(qt_MultiTexCoord0.x - xStep, qt_MultiTexCoord0.y - yStep * 0.36);
    gl_Position = qt_Matrix * qt_Vertex;
}