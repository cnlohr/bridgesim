#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D sampler2d;

varying vec3 v_Dot;
varying vec2 v_texCoord;
varying float fDot;

void main()
{
	vec2 texCoord = vec2(v_texCoord.s, 1.0 - v_texCoord.t);
	vec4 color = texture2D(sampler2d, texCoord);
	color.a = 1.;
	//gl_FragColor = vec4( 1.-abs( color.xyz * (v_Dot-0.5)*2.0 ), color.a);
	gl_FragColor = vec4( (color.rgb * v_Dot), color.a );
}
