#ifndef _GRAPHICSCORE_H
#define _GARPHICSCORE_H

#include <GL/gl.h>

struct Shader
{
	GLuint vertex;
	GLuint fragment;
	GLuint program;
};

struct Shader * CreateShader( const char * file );

unsigned char * ReadDataFile( const char * name ); //Read a file and malloc

#endif


