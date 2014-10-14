#include "3dutils.h"
#include <stdlib.h>
#include <string.h>

//WARNING: This function probably doesn't work AT ALL!
float * CalculateTangentSpace( int Triangles, int VertexCount, int * Indices, float * verts, float * normals, float * texs )
{
	//Here is the place to calculate the Tangent values.
	//It is a vector pointing in the direction of increasing u.
	int i;
	float * tans = 0;

	if( normals && texs && verts )
	{
		//If we have both Texture coords and normals, we can calculate a tangent matrix.
		tans = malloc( VertexCount * sizeof( float ) * 4 );
		memset( tans, 0, VertexCount * sizeof( float ) * 4 );

		//Process modeled after: http://www.terathon.com/code/tangent.html

		float * tan1 = malloc( VertexCount * sizeof( float ) * 3 );
		float * tan2 = malloc( VertexCount * sizeof( float ) * 3 );

		memset( tan1, 0, VertexCount * sizeof( float ) * 3 );
		memset( tan2, 0, VertexCount * sizeof( float ) * 3 );

		for( i = 0; i < Triangles; i++ )
		{
			int v1 = Indices[i*3+0];
			int v2 = Indices[i*3+1];
			int v3 = Indices[i*3+2];


			float * t1 = &texs[v1*3];
			float * t2 = &texs[v2*3];
			float * t3 = &texs[v3*3];
			float * p1 = &verts[v1*3];
			float * p2 = &verts[v2*3];
			float * p3 = &verts[v3*3];

			float vec1[3];
			float vec2[3];
			float tex1[3];
			float tex2[3];

			sub3d( vec1, p2, p1 ); //(x,y,z)
			sub3d( vec2, p3, p1 );
			sub3d( tex1, t2, t1 ); //(s,t,u)
			sub3d( tex2, t3, t1 );

	        float r = 1.0f / ( tex1[0] * tex2[1] - tex2[0] * tex1[1] );
			float sdir[3] = {
				(tex2[1] * vec1[0] - tex1[1] * vec2[0]) * r,
				(tex2[1] * vec1[1] - tex1[1] * vec2[1]) * r,
                (tex2[1] * vec1[2] - tex1[1] * vec2[2]) * r };
			float tdir[3] = {
				(tex1[0] * vec2[0] - tex2[0] * vec1[0]) * r,
				(tex1[0] * vec2[1] - tex2[0] * vec1[1]) * r,
                (tex1[0] * vec2[2] - tex2[0] * vec1[2]) * r };

			add3d( &tan1[v1*3], &tan1[v1*3], sdir );
			add3d( &tan1[v2*3], &tan1[v2*3], sdir );
			add3d( &tan1[v3*3], &tan1[v3*3], sdir );

			add3d( &tan2[v1*3], &tan2[v1*3], sdir );
			add3d( &tan2[v2*3], &tan2[v2*3], sdir );
			add3d( &tan2[v3*3], &tan2[v3*3], sdir );
		}

		//Normalize and orthoganlize.
		for (i = 0; i < VertexCount; i++)
		{
		    const float * n = &normals[i*3];
		    const float * t = &tan1[i*3];
		    
		    // Gram-Schmidt orthogonalize
			float tmp[3];
			float tdn[3];
			float thisdot = dot3d( n, t );
			scale3d( tdn, n, thisdot );
			sub3d( tmp, t, tdn );
			normalize3d( &tans[i*4], tmp );

			cross3d( tmp, n, t );
			tans[i*4+3] = (dot3d( tmp, &tan2[i*3] ) < 0)?-1:1; //set handedness
		}
	}

	return tans;
}

