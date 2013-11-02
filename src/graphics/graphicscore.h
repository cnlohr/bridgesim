#ifndef _GRAPHICSCORE_H
#define _GARPHICSCORE_H

#include <GL/gl.h>

struct Shader
{
	GLuint vertex;
	GLuint fragment;
	GLuint program;
};

struct UniformMatch
{
	const char * name;
	float * data;
	int intcount;
	int floatcount;
	struct UniformMatch * next;
};

struct Shader * CreateShader( const char * file );
void ApplyShader( struct Shader * shader, struct UniformMatch * match );
struct UniformMatch * UniformMatchMake( const char* name, float * data, int intcount, int floatcount, struct UniformMatch * prev );
void CancelShader();

unsigned char * ReadDataFile( const char * name ); //Read a file and malloc

#endif


