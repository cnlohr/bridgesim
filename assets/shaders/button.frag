//http://nehe.gamedev.net/article/glsl_an_introduction/25007/

#define ROUNDSIZE 10.0
void main()
{
	vec2 pos = gl_TexCoord[0].xy;
	vec2 siz = gl_TexCoord[0].zw;
	float alpha = 1.0;

	if( pos.x < ROUNDSIZE && pos.y < ROUNDSIZE )
	{
		float calc = length( pos - vec2( ROUNDSIZE ) );
		if( calc > ROUNDSIZE )
			discard;
	}

	if( pos.x > siz.x-ROUNDSIZE && pos.y < ROUNDSIZE )
	{
		float calc = length( pos - vec2( siz.x-ROUNDSIZE,ROUNDSIZE ) );
		if( calc > ROUNDSIZE )
			discard;
	}

	if( pos.x > siz.x - ROUNDSIZE && pos.y > siz.y - ROUNDSIZE )
	{
		float calc = length( pos - vec2( siz - ROUNDSIZE ) );
		if( calc > ROUNDSIZE )
			discard;
	}

	if( pos.x < ROUNDSIZE && pos.y > siz.y - ROUNDSIZE )
	{
		float calc = length( pos - vec2( ROUNDSIZE, siz.y - ROUNDSIZE ) );
		if( calc > ROUNDSIZE )
			discard;
	}

//	gl_FragColor = vec4( gl_TexCoord[0].xy, 0.0, 1.0);
	gl_FragColor = gl_Color;
}


