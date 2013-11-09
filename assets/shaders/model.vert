//http://nehe.gamedev.net/article/glsl_an_introduction/25007/

attribute vec4 tangent;
attribute vec3 mynormal;
varying vec4 tanout;
varying vec3 normal;

void main()
{
	//from: http://www.ozone3d.net/tutorials/bump_mapping_p4.php

	gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;

	tanout = tangent;
	normal = gl_Normal;

/*	vec3 n = normalize(gl_NormalMatrix * gl_Normal);
	vec3 t = normalize(gl_NormalMatrix * tangent.xyz); 
	vec3 b = normalize( cross(n, t) * tangent.w ); //Many times n and t will be nonorthogonal
	vec3 vVertex = vec3(gl_ModelViewMatrix * gl_Vertex);

	vec3 tmpVec = gl_LightSource[0].position.xyz - vVertex;
	lightVec.x = dot(tmpVec, t);
	lightVec.y = dot(tmpVec, b);
	lightVec.z = dot(tmpVec, n);

	tmpVec = -vVertex;
	eyeVec.x = dot(tmpVec, t);
	eyeVec.y = dot(tmpVec, b);
	eyeVec.z = dot(tmpVec, n);*/


	gl_TexCoord[0] = gl_MultiTexCoord0;
	gl_FrontColor = gl_Color;
	gl_BackColor = gl_Color;
}

