#ifndef _GARPHICSCORE_H
#define _GARPHICSCORE_H

#include <stdint.h>
#include <GL/gl.h>

#define USE_PNG
#define USE_JPG

#define MAX_TEXTURES 16

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
void DestroyTexture( struct Texture * t );
void ChangeTextureFilter( struct Texture * t, int linear );


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


unsigned char * ReadDataFile( const char * name ); //Read a file and malloc




//VBOs
struct VertexData
{
	int vertexcount;
	int stride;
	GLuint vbo;
};

struct IndexData
{
	int indexcount;
	GLuint * indexdata;
};

struct GPUGeometry
{
	struct Texture * textures[MAX_TEXTURES];
	int todelete[MAX_TEXTURES]; //if 1, will delete texture

	struct IndexData * indices;
	int vertexcount;
	struct VertexData ** vertexdatas;
	char ** names;

	//If 1, will cause indices, and vertexdatas to be deleted with names.  If 0, only names will be deleted.
	int uniquedata;

	GLint mode;
};

struct VertexData * VertexDataCreate();

//Call with verts=0 to make a strippable buffer (GPGPU only)
void UpdateVertexData( struct VertexData * vd, float * Verts, int iNumVerts, int iStride );
void DestroyVertexData( struct VertexData * vd );

struct IndexData * IndexDataCreate();
void UpdateIndexData( struct IndexData * id, int indexcount, int * data );
void DestroyIndexData( struct IndexData * id );



//Names[0] doesn't matter, but for all other names, it binds to a specific shader property.
//the 0th vd will ALWAYS be vertex position.
//
//if you say "texcoord" it will bind to that text coord.
//if you say "color" it will bind to the color.
struct GPUGeometry * CreateGeometry( struct IndexData * indices, int vertexcount, struct VertexData ** verts, char ** names, int unique, GLint mode );
void AttachTextureToGeometry( struct GPUGeometry * g, struct Texture * texture, int place, int take_ownership_of );
void RenderGPUGeometry( struct GPUGeometry * g );
void DestroyGPUGeometry( struct GPUGeometry * g );


//TODO: Shaders: Global parameters, i.e. for size-of-textures?
//TODO: Model loading
//TODO: Use index buffers

#endif


