#ifndef _GRAPHICSCORE_H
#define _GARPHICSCORE_H

#include <stdint.h>
#include <GL/gl.h>

#define USE_PNG
#define USE_JPG

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
struct Shader * CreateShader( const char * file );  //Returns a shader even if compilation fails.
void ApplyShader( struct Shader * shader, struct UniformMatch * match );
struct UniformMatch * UniformMatchMake( const char* name, float * data, int intcount, int floatcount, struct UniformMatch * prev );
void CancelShader( struct Shader * s );
void DeleteShader( struct Shader * s );
void CheckForNewer( struct Shader * s );


enum TextureType
{
	TTUNDEFINED = 0,
	TTGRAYSCALE,
	TTGRAYALPHA,
	TTRGB,
	TTRGBA,
	TTRGBA16,
	TTRGBA32,
};

struct Texture
{
	enum TextureType format;
	GLenum type; //Almost always GL_TEXTURE_2D (Could be GL_TEXTURE_3D)
	GLuint texture; //Texture ID
	int width, height;
	int slot; //which texture slot (For multi-texturing)
	uint8_t * rawdata; //May be other types, too!
};

struct Texture * CreateTexture();

//Zero return = OKAY! Nonzero = bad.
int ReadTextureFromFile( struct Texture * t, const char * filename );
void MakeDynamicTexture2D( struct Texture * t, int width, int height, enum TextureType tt );
void UpdateDataInOpenGL( struct Texture * t );
void ActivateTexture( struct Texture * t );
void DeactivateTexture( struct Texture * t );




struct RFBuffer
{
	int width, height;
	int use_depth_buffer;

	enum TextureType mtt;

	GLuint renderbuffer;
	GLuint outputbuffer;
	int outextures;
};

struct RFBuffer * MakeRFBuffer( int use_depth_buffer, enum TextureType type );
int RFBufferGo( struct RFBuffer *rb, int width, int height, int texturecount, struct Texture ** textures, int do_clear );
void RFBufferDone( struct RFBuffer *rb, int newwidth, int newheight );
void DestroyRFBuffer( struct RFBuffer *rb );

//TODO: Shaders: Global parameters, i.e. for size-of-textures?
//TODO: Model loading


unsigned char * ReadDataFile( const char * name ); //Read a file and malloc

#endif


