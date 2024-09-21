#version 440

layout(location = 0) in vec2 qt_TexCoord0;
layout(location = 0) out vec4 fragColor;

layout(std140, binding = 0) uniform buf {
    // qt_Matrix and qt_Opacity must always be both present
    // if the built-in vertex shader is used.
    mat4 qt_Matrix;
    float qt_Opacity;
    float weight1;
    float weight2;
    float weight3;
    float weight4;
    float weight5;
};

layout(binding = 1) uniform sampler2D source1;
layout(binding = 2) uniform sampler2D source2;
layout(binding = 3) uniform sampler2D source3;
layout(binding = 4) uniform sampler2D source4;
layout(binding = 5) uniform sampler2D source5;

void main()
{
    vec4 sourceColor = texture(source1, qt_TexCoord0) * weight1;
    sourceColor += texture(source2, qt_TexCoord0) * weight2;
    sourceColor += texture(source3, qt_TexCoord0) * weight3;
    sourceColor += texture(source4, qt_TexCoord0) * weight4;
    sourceColor += texture(source5, qt_TexCoord0) * weight5;
    fragColor = sourceColor * qt_Opacity;
}