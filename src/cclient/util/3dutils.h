#ifndef _3DUTILS_H
#define _3DUTILS_H

//NOTE: Expects triples for all three.
//Returns quadruples
float * CalculateTangentSpace( int Triangles, int VertexCount, int * Indices, float * verts, float * normals, float * texs );

#endif

