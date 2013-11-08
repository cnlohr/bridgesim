//http://nehe.gamedev.net/article/glsl_an_introduction/25007/

varying vec4 mtcx;

void main()
{
	gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;

	gl_TexCoord[0] = gl_MultiTexCoord0;
	gl_FrontColor = gl_Color;
	gl_BackColor = gl_Color;
}

