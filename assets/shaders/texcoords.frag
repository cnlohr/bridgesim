//http://nehe.gamedev.net/article/glsl_an_introduction/25007/

varying vec3 normal;
varying vec3 vertex_to_light_vector;

uniform sampler2D tex0;

void main()
{
    // Defining The Material Colors
    //const vec4 AmbientColor = vec4(0.1, 0.3, 0.0, 1.0);
	vec4 DiffuseColor = texture2D(tex0,gl_TexCoord[0].st);

//	gl_FragColor = vec4( 1, 1, 1, pow( DiffuseColor.a, 1.0 ) );
    gl_FragColor = vec4( gl_TexCoord[0].xy, DiffuseColor.a, 1.0 );
//    gl_FragColor = gl_Color;
}


