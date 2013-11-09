//Copyright 2013 <>< Charles Lohr, Relicensed under the MIT/x11 License.

#ifndef _OBJREADER_H
#define _OBJREADER_H

#define MAX_OBJECTS_PER_OBJ 128

#include "linmath.h"
#include "graphicscore.h"

struct OBJObject
{
	const char * OName;

	int VertCount;  //3 floats per vert count
	float * Vertices;

	int NormalCount; //3 floats per normal count
	float * Normals;
	float * Tangents; //4 floats per.

	int TexCount;    //3 floats per tex
	float * Textures;

	int TriCount;   //3 ints per face index, i.e. 9 per face... [vertex texture norm] [vertex texture norm]
	int * Faces;

	float mins[3];
	float maxs[3];
	float center[3];

	unsigned int OGLList; //Optionally implemented by user, may have OpenGL List.

	struct GPUGeometry * geometry;
};

struct OBJFile
{
	const char * Filename;
	int NumObjects;
	struct OBJObject * Objects[MAX_OBJECTS_PER_OBJ];
};

struct OBJFile * OpenOBJ( const char * Filename, int flipv );

#endif

