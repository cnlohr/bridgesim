#ifndef _GRAPHICSCORE_H
#define _GARPHICSCORE_H

#include <GL/gl.h>

struct Shader
{
	GLuint vertex;
	GLuint fragment;
	GLuint program;

	char * VertexName;
	char * FragmentName;
	double LastFileTimeVertex;
	double LastFileTimeFragment;
};

struct UniformMatch
{
	const char * name;
	float * data;
	int intcount;
	int floatcount;
	struct UniformMatch * next;
};

//Shaders utilities
struct Shader * CreateShader( const char * file );
void ApplyShader( struct Shader * shader, struct UniformMatch * match );
struct UniformMatch * UniformMatchMake( const char* name, float * data, int intcount, int floatcount, struct UniformMatch * prev );
void CancelShader( struct Shader * s );
void DeleteShader( struct Shader * s );
void CheckForNewer( struct Shader * s );


struct Texture
{
	//TODO!
};



//TODO: Texture (PNG Loading, Render-to-texture)

//TODO: Model loading


unsigned char * ReadDataFile( const char * name ); //Read a file and malloc

#endif


