//http://nehe.gamedev.net/article/glsl_an_introduction/25007/

varying vec3 normal;
varying vec3 vertex_to_light_vector;

uniform sampler2D tex0;

void main()
{

#define THRESH 0.5
#define OVERRIDEALPHA
//#define SMARTALPHA

	vec4 DiffuseColor = texture2D(tex0,gl_TexCoord[0].st);
	if( DiffuseColor.a < THRESH ) discard;
#ifdef OVERRIDEALPHA
	gl_FragColor = vec4( DiffuseColor.rgb, 1.0 ) * gl_Color;
#else
#ifdef SMARTALPHA
    gl_FragColor = vec4( DiffuseColor.rgb, (DiffuseColor.a-THRESH)/(1.-THRESH) ) * gl_Color;
#else
    gl_FragColor = vec4( DiffuseColor.rgb, DiffuseColor.a ) * gl_Color;
#endif
#endif
}


