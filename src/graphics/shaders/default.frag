//http://nehe.gamedev.net/article/glsl_an_introduction/25007/

varying vec3 normal;
varying vec3 vertex_to_light_vector;

uniform sampler2D tex0;
uniform vec4 AmbientColor;
uniform vec4 EmissionColor;

void main()
{
    // Defining The Material Colors
    //const vec4 AmbientColor = vec4(0.1, 0.3, 0.0, 1.0);
    vec4 DiffuseColor;

	DiffuseColor = ( texture2D(tex0,gl_TexCoord[0].st) + EmissionColor ) * gl_Color;
//	DiffuseColor = ( texture2D(tex0,gl_TexCoord[0].st) );
 
    // Scaling The Input Vector To Length 1
    vec3 normalized_normal = normalize(normal);
    vec3 normalized_vertex_to_light_vector = normalize(vertex_to_light_vector);
 
    // Calculating The Diffuse Term And Clamping It To [0;1]
    float DiffuseTerm = clamp(dot(normal, vertex_to_light_vector), 0.0, 1.0);
 
    // Calculating The Final Color
    gl_FragColor = AmbientColor + DiffuseColor;// * DiffuseTerm;
//	gl_FragColor = vec4( texture2D(tex0,gl_TexCoord[0].st).xyz + gl_TexCoord[0].rgb, 1 );

//	gl_FragColor = vec4( 1., 0., .5 ,1. );
}


