#include <sys/types.h>
#include <stdint.h>
#include "os_generic.h"
#include <GL/glew.h>
#include "graphicscore.h"
#include <GL/glext.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>


double TotalTime;
double DeltaTime;
float RenderW;
float RenderH;
float ScreenW;
float ScreenH;

#define MAX_STORAGE 8192

static struct Shader * CurrentShader;
static GLuint FreeBOs[MAX_STORAGE];
static int FreeBOHead = -1;



#ifdef WIN32

#include <windows.h>

//For graphics loading.
#include <gdiplus/gdiplus.h>
#include <gdiplus/gdiplusflat.h>

#else
#ifdef USE_PNG
#include <png.h>
#endif
#ifdef USE_JPG
#include <jpeglib.h>
#endif
#endif



unsigned char * ReadDataFile( const char * name )
{
	int r;
	FILE * f = fopen( name, "rb" );
	if( !f )
	{
		return 0;
	}
	fseek( f, 0, SEEK_END );
	long len = ftell( f );
	fseek( f, 0, SEEK_SET );

	unsigned char * ret = malloc( len + 1);
	r = fread( ret, len, 1, f );
	if( r < 1 )
	{
		free( ret );
		fclose( f );
		return 0;
	}
	fclose( f );
	ret[len] = 0;
	return ret;
}

static void ShaderErrorPrint( GLint shader )
{
	int written = 0;
	int loglen = 0;
	GLchar * log;

	glGetShaderiv( shader, GL_INFO_LOG_LENGTH, &loglen );

	if (loglen > 0)
	{
		log = malloc(loglen);

		glGetShaderInfoLog(shader, loglen, &written, log);
		fprintf( stderr, "%s\n", log );

		free( log );
	}
}

static int LoadShaderInPlace( struct Shader * ret )
{
	unsigned char * VertexText;
	unsigned char * FragmentText;
	GLint compiled;
	
	VertexText = ReadDataFile( ret->VertexName );
	if( !VertexText )
	{
		fprintf( stderr, "Error: Could not open vertex shader: %s\n", ret->VertexName );
		return 1;
	}

	FragmentText = ReadDataFile( ret->FragmentName );
	if( !FragmentText )
	{
		fprintf( stderr, "Error: Could not open fragment shader: %s\n", ret->FragmentName );
		free( VertexText );
		return 1;
	}

	ret->vertex = glCreateShader(GL_VERTEX_SHADER);
	ret->fragment = glCreateShader(GL_FRAGMENT_SHADER);

	GLint vl = strlen( VertexText );
	GLint fl = strlen( FragmentText );

	glShaderSource(ret->vertex, 1, (const GLchar **)&VertexText, &vl );
	glShaderSource(ret->fragment, 1, (const GLchar **)&FragmentText, &fl );

	glCompileShader(ret->vertex);
	glGetShaderiv(ret->vertex, GL_COMPILE_STATUS, &compiled);
	if(!compiled)
	{
		fprintf( stderr, "Error: Could not compile vertex shader: %s\n", ret->VertexName );
		ShaderErrorPrint( ret->vertex );

		goto cancel;
	}


	glCompileShader(ret->fragment);
	glGetShaderiv(ret->fragment, GL_COMPILE_STATUS, &compiled);
	if(!compiled)
	{
		fprintf( stderr, "Error: Could not compile fragment shader: %s\n", ret->FragmentName );
		ShaderErrorPrint( ret->fragment );

		goto cancel;
	}

	ret->program = glCreateProgram();

	glAttachShader(ret->program, ret->vertex);
	glAttachShader(ret->program, ret->fragment);

//	glBindAttribLocation(shaderProgram, 0, "InVertex");

    glLinkProgram(ret->program);
	GLint IsLinked;
	glGetProgramiv(ret->program, GL_LINK_STATUS, (GLint *)&IsLinked);
	if(!IsLinked)
	{
		fprintf( stderr, "Error: Could not link shader: %s + %s\n", ret->VertexName, ret->FragmentName );
		GLint maxlen;
		glGetProgramiv(ret->program, GL_INFO_LOG_LENGTH, &maxlen);

		if( maxlen > 0 )
		{
			char * log = malloc( maxlen );
			glGetProgramInfoLog(ret->program, maxlen, &maxlen, log);
			fprintf( stderr, "%s\n", log );
			free( log );
		}
		goto cancel_with_program;
	}

	free( VertexText );
	free( FragmentText );

	return 0; //Happy!

cancel_with_program:
	glDetachShader(ret->program, ret->vertex);
	glDetachShader(ret->program, ret->fragment );
	glDeleteShader(ret->program);
cancel:
	free( VertexText );
	free( FragmentText );

	glDeleteShader( ret->vertex );
	glDeleteShader( ret->fragment );
	return 1;
}


struct Shader * CreateShader( const char * file )
{
	struct Shader * ret;
	int lnl = strlen( file );
	char * lfv, *lff;

	lfv = malloc( lnl + 8 );
	sprintf( lfv, "%s.vert", file );

	lff = malloc( lnl + 8 );
	sprintf( lff, "%s.frag", file );

	ret = malloc( sizeof( struct Shader ) );
	ret->VertexName = lfv;
	ret->FragmentName = lff;
	ret->LastFileTimeVertex = OGGetFileTime( lfv );
	ret->LastFileTimeFragment = OGGetFileTime( lff );

	LoadShaderInPlace( ret );

	return ret;
}

void DeleteShader( struct Shader * s )
{
	glDetachShader(s->program, s->vertex);
	glDetachShader(s->program, s->fragment );
	glDeleteShader(s->program);
	glDeleteShader(s->vertex );
	glDeleteShader(s->fragment );
	free(s->VertexName );
	free(s->FragmentName );
	free(s);
}



struct UniformMatch * UniformMatchMake( const char* name, float * data, int intcount, int floatcount, struct UniformMatch * prev )
{
	int i;
	struct UniformMatch * m = malloc( sizeof( struct UniformMatch ) );
	m->next = prev;
	m->name = name;
	m->data = data;
	m->intcount = intcount;
	m->floatcount = floatcount;

	return m;
}


void ApplyShader( struct Shader * shader, struct UniformMatch * m )
{
	glUseProgramObjectARB( shader->program );

	CurrentShader = shader;

	while( m )
	{
		int place = glGetUniformLocationARB( shader->program, m->name );

		if( m->intcount == 1 )
		{
			glUniform1i( place, m->data[0] );
		}
		else if( m->intcount == 2 )
		{
			glUniform2i( place, m->data[0], m->data[1] );
		}
		else if( m->intcount == 3 )
		{
			glUniform3i( place, m->data[0], m->data[1], m->data[2] );
		}
		else if( m->intcount == 4 )
		{
			glUniform4i( place, m->data[0], m->data[1], m->data[2], m->data[3] );
		}
		else if( m->floatcount == 1 )
		{
			glUniform1f( place, m->data[0] );
		}
		else if( m->floatcount == 2 )
		{
			glUniform2f( place, m->data[0], m->data[1] );
		}
		else if( m->floatcount == 3 )
		{
			glUniform3f( place, m->data[0], m->data[1], m->data[2] );
		}
		else if( m->floatcount == 4 )
		{
			glUniform4f( place, m->data[0], m->data[1], m->data[2], m->data[3] );
		}

		m = m->next;
	}
	//Need to bind things...
}

void CancelShader( struct Shader * s )
{
	CurrentShader = 0;
	glUseProgramObjectARB( 0 );
}

void CheckForNewerShader( struct Shader * s )
{
	double VertTime = OGGetFileTime( s->VertexName );
	double FragTime = OGGetFileTime( s->FragmentName );

	if( s->LastFileTimeVertex != VertTime || s->LastFileTimeFragment != FragTime )
	{
		glDetachShader(s->program, s->vertex);
		glDetachShader(s->program, s->fragment );
		glDeleteShader(s->program);
		glDeleteShader(s->vertex );
		glDeleteShader(s->fragment );
		LoadShaderInPlace( s );
	}

	s->LastFileTimeVertex = VertTime;
	s->LastFileTimeFragment = FragTime;
}





//TEXTURE/////////////////////////////////////////////////////////////////////

//For things that require GL_RGBA when dealing with floating point data; usually when dealing with verticies or host data.
static GLuint imTypes[] = { 0, GL_LUMINANCE8, GL_LUMINANCE8_ALPHA8, GL_RGB, GL_RGBA, GL_RGBA16F_ARB, GL_RGBA32F_ARB, 0 };
static GLuint imXTypes[] ={ 0, GL_LUMINANCE, GL_LUMINANCE_ALPHA, GL_RGB, GL_RGBA, GL_RGBA, GL_RGBA, 0 };
static GLuint byTypes[] = { 0, GL_UNSIGNED_BYTE, GL_UNSIGNED_BYTE, GL_UNSIGNED_BYTE, GL_UNSIGNED_BYTE, GL_FLOAT, GL_FLOAT, 0 };
static int channels[] = { 0, 1, 2, 3, 4, 4, 4, 0 };


struct Texture * CreateTexture()
{
	struct Texture * ret = malloc( sizeof( struct Texture ) );
	ret->format = TTUNDEFINED;
	ret->type = 0;
	ret->texture = 0xaaaaaaaa;
	glGenTextures( 1, &ret->texture );
	ret->width = 0;
	ret->rawdata = 0;
	ret->height = 0;
	ret->slot = 0;
	return ret;
}


void MakeDynamicTexture2D( struct Texture * t, int width, int height, enum TextureType tt )
{
	t->width = width;
	t->height = height;
	t->format = tt;
	t->type = GL_TEXTURE_2D;

	glBindTexture( t->type, t->texture );
	glCopyTexImage2D( t->type, 0, imTypes[t->format], 0, 0, width, height, 0 );
	glTexParameteri( t->type, GL_TEXTURE_MIN_FILTER, GL_NEAREST );
	glTexParameteri( t->type, GL_TEXTURE_MAG_FILTER, GL_NEAREST );
	glBindTexture( t->type, 0 );
}

#ifdef WIN32



int ReadTextureFromFile( struct Texture * t, const char * filename )
{
	int i;
	HGLOBAL hMem;
	LPVOID pMemImage;
	IStream *pStm;
	struct GdiplusStartupInput gdiplusStartupInput;
	ULONG_PTR gdiplusToken;
	GpBitmap *pImg;
	PixelFormat PixelFormat;

	//Read in data
	FILE * f = fopen( filename, "rb");
	if( !f )
	{
		fprintf( stderr, "Error: Could not open %s\n", filename );
		return -1;
	}
	fseek(f,0,SEEK_END);
	int l = ftell( f );
	unsigned char * buffer = malloc( l );
	fseek(f,0,SEEK_SET);
	fread(buffer, l, 1, f );
	fclose( f );

	//Prepare GDI+ imaging
	hMem = GlobalAlloc( GMEM_MOVEABLE, l );
	pMemImage = GlobalLock( hMem);
	memcpy( pMemImage, buffer, l );
	GlobalUnlock( hMem );

	//XXX: This requries OLE32, do we really want it?
	CreateStreamOnHGlobal( hMem, TRUE, &pStm );

	gdiplusStartupInput.GdiplusVersion = 1;
	gdiplusStartupInput.DebugEventCallback = NULL;
	gdiplusStartupInput.SuppressBackgroundThread = FALSE;
	gdiplusStartupInput.SuppressExternalCodecs = FALSE;
	GdiplusStartup( &gdiplusToken, &gdiplusStartupInput, NULL );

	if( GdipCreateBitmapFromStream( pStm, &pImg ) )
	{
		fprintf( stderr, "Error: cannot decode: %s\n", filename );
		return -2;
	}

	GdipGetImagePixelFormat( (GpImage *)pImg, &PixelFormat );

	UINT width;
	UINT height;
	GdipGetImageHeight( (GpImage *)pImg, &height );
	GdipGetImageWidth( (GpImage *)pImg, &width );
	GpRect r;
	r.X = 0;
	r.Y = 0;
	r.Width = width;
	r.Height = height;
	BitmapData bd;

		enum TextureType format;
	GLenum type; //Almost always GL_TEXTURE_2D (Could be GL_TEXTURE_3D)
	GLuint texture;

	int slot; //which texture slot (For multi-texturing)
	uint8_t * rawdata; //May be other types, too!

	t->width = width;
	t->height = height;
	t->type = GL_TEXTURE_2D;

	//Detect if has alpha or not...
	int ps;
	if( PixelFormat & PixelFormatAlpha )
	{
		GdipBitmapLockBits(pImg,&r,ImageLockModeRead,PixelFormat32bppARGB,&bd);
		ps = 4;
		t->format = TTRGBA;
	}
	else
	{
		GdipBitmapLockBits(pImg,&r,ImageLockModeRead,PixelFormat24bppRGB,&bd);
		ps = 3;
		t->format = TTRGB;
	}

	t->rawdata = malloc( ps * width * height );

	int x, y;
	if( ps == 3 )
	{
		for( y = 0; y < height; y++ )
		for( x = 0; x < width; x++ )
		{
			t->rawdata[(x+y*width)*3+0] = ((unsigned char*)bd.Scan0)[x*3+y*bd.Stride+2];
			t->rawdata[(x+y*width)*3+1] = ((unsigned char*)bd.Scan0)[x*3+y*bd.Stride+1];
			t->rawdata[(x+y*width)*3+2] = ((unsigned char*)bd.Scan0)[x*3+y*bd.Stride+0];
		}
	}
	else //ps = 4
	{
		for( y = 0; y < height; y++ )
		for( x = 0; x < width; x++ )
		{
			t->rawdata[(x+y*width)*4+0] = ((unsigned char*)bd.Scan0)[x*4+y*bd.Stride+2];
			t->rawdata[(x+y*width)*4+1] = ((unsigned char*)bd.Scan0)[x*4+y*bd.Stride+1];
			t->rawdata[(x+y*width)*4+2] = ((unsigned char*)bd.Scan0)[x*4+y*bd.Stride+0];
			t->rawdata[(x+y*width)*4+3] = ((unsigned char*)bd.Scan0)[x*4+y*bd.Stride+3];
		}
	}

	GdipBitmapUnlockBits(pImg, &bd );
	GdipDisposeImage( (GpImage *)pImg );
	GdiplusShutdown( gdiplusToken );

	return 0;
}


#else

#ifdef USE_PNG
static void mypngreadfn(png_struct *png, png_byte *p, png_size_t size )
{
	int r = fread( p, size, 1, png_get_io_ptr(png));
}
#endif


#ifdef USE_JPG
struct my_error_mgr {
  struct jpeg_error_mgr pub;        /* "public" fields */

  jmp_buf setjmp_buffer;        /* for return to caller */
};


typedef struct my_error_mgr * my_error_ptr;

void my_error_exit (j_common_ptr cinfo)
{
	my_error_ptr myerr = (my_error_ptr) cinfo->err;
	(*cinfo->err->output_message) (cinfo);
	longjmp(myerr->setjmp_buffer, 1);
}

#endif

int ReadTextureFromJPG( struct Texture * t, const char * filename )
{
#ifndef USE_JPG
	fprintf( stderr, "Error.  Cannot load: %s.  JPG Support not included.\n" );
	return -1;
#else

	//from: https://github.com/LuaDist/libjpeg/blob/master/example.c

	struct jpeg_decompress_struct cinfo;
	struct my_error_mgr jerr;
	FILE * infile;
	JSAMPARRAY buffer;
	int row_stride;

	if ((infile = fopen(filename, "rb")) == NULL) {
		fprintf(stderr, "can't open %s\n", filename);
		return 0;
	}

	cinfo.err = jpeg_std_error(&jerr.pub);
	jerr.pub.error_exit = my_error_exit;

	if (setjmp(jerr.setjmp_buffer)) {
		jpeg_destroy_decompress(&cinfo);
		fclose(infile);
		return 0;
	}

	jpeg_create_decompress(&cinfo);

	jpeg_stdio_src(&cinfo, infile);

	(void) jpeg_read_header(&cinfo, TRUE);

	(void) jpeg_start_decompress(&cinfo);

	row_stride = cinfo.output_width * cinfo.output_components;

	buffer = (*cinfo.mem->alloc_sarray)
	((j_common_ptr) &cinfo, JPOOL_IMAGE, row_stride, 1);

	if( cinfo.output_components != 3 && cinfo.output_components != 1 )
	{
		jpeg_finish_decompress(&cinfo);
		jpeg_destroy_decompress(&cinfo);
		fclose(infile);
		return -2;
	}

	t->format = (cinfo.output_components==3)?TTRGB:TTGRAYSCALE;
	t->width = cinfo.output_width;
	t->height = cinfo.output_height;
	t->type = GL_TEXTURE_2D;
	t->rawdata = malloc( t->width * t->height * cinfo.output_components );

	int line = 0;

	while (cinfo.output_scanline < cinfo.output_height)
	{
		int i;
		jpeg_read_scanlines(&cinfo, buffer, 1);
		memcpy( &t->rawdata[row_stride * line], buffer[0], row_stride );
		line++;
	}

fail:
	jpeg_finish_decompress(&cinfo);
	jpeg_destroy_decompress(&cinfo);
	fclose(infile);
	return 0;
#endif
}


int ReadTextureFromPNG( struct Texture * t, const char * filename )
{
#ifdef USE_PNG
	png_structp png_ptr;
	png_infop info_ptr;
	int number_of_passes;
	png_bytep* row_pointers;
	png_byte color_type;
	png_byte bit_depth;
	unsigned x;
	int r;
	unsigned char header[8];	// 8 is the maximum size that can be checked

	FILE * fp = fopen( filename, "rb" );

	//open file and test for it being a png 
	if (!fp)
	{
		fprintf( stderr, "[read_png_file] File %s could not be opened for reading", filename );
		goto quickexit;
	}

	r = fread(header, 8, 1, fp);

	if (png_sig_cmp(header, 0, 8))
	{
		fprintf( stderr, "[read_png_file] File %s is not recognized as a PNG file", filename );
		goto closeandquit;
	}

	//initialize stuff 
	png_ptr = png_create_read_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);

	if (!png_ptr)
	{
		fprintf( stderr, "[read_png_file] png_create_read_struct failed");
		goto closeandquit;
	}

	info_ptr = png_create_info_struct(png_ptr);
	if (!info_ptr)
	{
		fprintf( stderr, "[read_png_file] png_create_info_struct failed");
		goto closepngandquit;
	}

	if (setjmp(png_jmpbuf(png_ptr)))
	{
		fprintf( stderr, "[read_png_file] Error during init_io");
		goto closepngandquit;
	}

	png_set_sig_bytes(png_ptr, 8);
	png_set_read_fn( png_ptr, fp, mypngreadfn );

	png_read_info(png_ptr, info_ptr);

	t->width = png_get_image_width(png_ptr, info_ptr);
	t->height = png_get_image_height(png_ptr, info_ptr);
	color_type = png_get_color_type(png_ptr, info_ptr);
	bit_depth = png_get_bit_depth(png_ptr, info_ptr);

	if (color_type == PNG_COLOR_TYPE_PALETTE)
		png_set_palette_to_rgb(png_ptr);

	number_of_passes = png_set_interlace_handling(png_ptr);
	png_read_update_info(png_ptr, info_ptr);

	// read file 
	if (setjmp(png_jmpbuf(png_ptr)))
	{
		fprintf(stderr,"[read_png_file] Error during read_image");
		goto closepngandquit;		
	}

	row_pointers = (png_bytep*) malloc(sizeof(png_bytep) * t->height);
	unsigned int y;
	for ( y=0; y < (unsigned)t->height; y++)
		row_pointers[y] = (png_byte*) malloc(png_get_rowbytes(png_ptr, info_ptr));

	png_read_image(png_ptr, row_pointers);

	png_read_end( png_ptr, info_ptr );
	png_destroy_read_struct( &png_ptr, &info_ptr, NULL );

	png_free_data(png_ptr, info_ptr, PNG_FREE_ALL, -1);

	if (color_type & PNG_COLOR_MASK_COLOR )
		if (color_type & PNG_COLOR_MASK_ALPHA)
			t->format = TTRGBA;	
		else
			t->format = TTRGB;
	else
		if (color_type & PNG_COLOR_MASK_ALPHA)
			t->format = TTGRAYALPHA;	
		else
			t->format = TTGRAYSCALE;


//	SAFE_DELETE(texture->m_data);
	t->rawdata = malloc( t->width * t->height * channels[t->format] );

	switch (t->format)
	{
		case TTGRAYSCALE:
			for ( y=0; y < (unsigned)t->height; ++y) {
				png_byte* row = row_pointers[y];
				for ( x = 0; x < t->width; ++x) {
					png_byte* ptr = &(row[x]);
					t->rawdata[(x + y * t->width)] = ptr[0];
				}	
			}
			break;
		case TTGRAYALPHA:
			for ( y=0; y < (unsigned)t->height; ++y) {
				png_byte* row = row_pointers[y];
				for ( x = 0; x < t->width; ++x) {
					png_byte* ptr = &(row[x*2]);
					t->rawdata[(x + y * t->width) * 2] = ptr[0];
					t->rawdata[(x + y * t->width) * 2 + 1] = ptr[1];
				}	
			}
			break;
		case TTRGBA:
			for ( y=0; y < (unsigned)t->height; ++y) {
				png_byte* row = row_pointers[y];
				for ( x = 0; x < t->width; ++x) {
					png_byte* ptr = &(row[x*4]);
					t->rawdata[(x + y * t->width) * 4] = ptr[0];
					t->rawdata[(x + y * t->width) * 4 + 1] = ptr[1];
					t->rawdata[(x + y * t->width) * 4 + 2] = ptr[2];
					t->rawdata[(x + y * t->width) * 4 + 3] = ptr[3];
				}	
			}
			break;
		case TTRGB:
			for ( y=0; y < (unsigned)t->height; y++) {
				png_byte* row = row_pointers[y];
				for (x=0; x<t->width; x++) {
					png_byte* ptr = &(row[x * 3]);
					t->rawdata[(x + y * t->width) * 3] = ptr[0];
					t->rawdata[(x + y * t->width) * 3 + 1] = ptr[1];
					t->rawdata[(x + y * t->width) * 3 + 2] = ptr[2];
				}	
			}
			break;
		default:
			fprintf( stderr, "Warning: Invalid color byte type for PNG.");
			break;
	}

	for ( y=0; y < (unsigned)t->height; y++)
		free(row_pointers[y]);
	free(row_pointers);

	t->type = GL_TEXTURE_2D;

	return 0;
closepngandquit:
	png_read_end( png_ptr, info_ptr );
	png_destroy_read_struct( &png_ptr, &info_ptr, NULL );
	png_free_data(png_ptr, info_ptr, PNG_FREE_ALL, -1);	
closeandquit:
	fclose( fp );
quickexit:
	return -1;
#else
	fprintf( stderr, "Error.  Cannot load: %s.  PNG Support not included.\n" );
	return -1;
#endif
}


int ReadTextureFromFile( struct Texture * t, const char * filename )
{
	const char * extension = strrchr( filename, '.' );
	if( extension == 0 )
	{
		return -1;
	}
	if( *extension == 0 )
	{
		return -1;
	}

	extension++;

	if( strcmp( extension, "png" ) == 0 )
	{
		return ReadTextureFromPNG( t, filename );
	} else if( strcmp( extension, "jpg" ) == 0 || strcmp( extension, "jpeg" ) )
	{
		return ReadTextureFromJPG( t, filename );
	}
	return -1;
}

#endif

void UpdateDataInOpenGL( struct Texture * t )
{
	glEnable( GL_TEXTURE_2D );
	glBindTexture(GL_TEXTURE_2D, t->texture);

	glTexImage2D(t->type, 0, imTypes[t->format], t->width, t->height, 0, imXTypes[t->format], byTypes[t->format], t->rawdata);

/*
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
*/
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
}


void ChangeTextureFilter( struct Texture * t, int linear )
{
	if( linear )
	{
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
	}
	else
	{
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
	}
}

void ActivateTexture( struct Texture * t )
{
	glEnable( t->type );
	glActiveTextureARB( GL_TEXTURE0_ARB + t->slot );
	glBindTexture(t->type, t->texture );
}

void DeactivateTexture( struct Texture * t )
{
	glActiveTextureARB( GL_TEXTURE0_ARB + t->slot );
	glBindTexture(t->type, 0 );
}

void DestroyTexture( struct Texture * t )
{
	glDeleteTextures( 1, &t->texture );
	if( t->rawdata ) free( t->rawdata );
	free( t->rawdata );
}




//RF BUFFERS

struct RFBuffer * MakeRFBuffer( int use_depth_buffer, enum TextureType type )
{
	struct RFBuffer * ret = malloc( sizeof( struct RFBuffer ) );

	ret->mtt = type;
	ret->use_depth_buffer = use_depth_buffer;
	if( use_depth_buffer )
		glGenRenderbuffersEXT( 1, &ret->renderbuffer );
	glGenFramebuffersEXT( 1, &ret->outputbuffer );

	return ret;
}

int RFBufferGo( struct RFBuffer *rb, int width, int height, int texturecount, struct Texture ** textures, int do_clear )
{
	int i;
	static const GLenum buffers[8] = {   GL_COLOR_ATTACHMENT0_EXT, GL_COLOR_ATTACHMENT1_EXT, GL_COLOR_ATTACHMENT2_EXT,
			GL_COLOR_ATTACHMENT3_EXT, GL_COLOR_ATTACHMENT4_EXT, GL_COLOR_ATTACHMENT5_EXT,
			GL_COLOR_ATTACHMENT6_EXT, GL_COLOR_ATTACHMENT7_EXT };

	for( i = 0; i < texturecount; i++ )
	{
		struct Texture * t = textures[i];
		if( t->width != width || t->height != height )
		{
			MakeDynamicTexture2D( t, width, height, rb->mtt );
		}
	}

	RenderW = width;
	RenderH = height;

	rb->width = width;
	rb->height = height;
	rb->outextures = texturecount;

	if( rb->use_depth_buffer )
	{
		glBindRenderbuffer( GL_RENDERBUFFER, rb->renderbuffer );
		glRenderbufferStorage( GL_RENDERBUFFER, GL_DEPTH_COMPONENT24, width, height );
	}

	glBindFramebufferEXT( GL_FRAMEBUFFER_EXT, rb->outputbuffer );
	for( i = 0; i < texturecount; i++ )
	{
		struct Texture * t = textures[i];
		glFramebufferTexture2DEXT( GL_FRAMEBUFFER_EXT, GL_COLOR_ATTACHMENT0_EXT + i, 
			GL_TEXTURE_2D, t->texture, 0 );
	}

	if( rb->use_depth_buffer )
		glFramebufferRenderbufferEXT( GL_FRAMEBUFFER_EXT, 
			GL_DEPTH_ATTACHMENT_EXT, GL_RENDERBUFFER_EXT, rb->renderbuffer );

	glDrawBuffers( texturecount, buffers );
	glViewport( 0, 0, width, height );

	//Check to see if there were any errors with the framebuffer
	switch( (GLenum)glCheckFramebufferStatusEXT(GL_FRAMEBUFFER_EXT) )
	{
		case GL_FRAMEBUFFER_COMPLETE_EXT: break;  //GOOD!
		case GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT_EXT:
			fprintf( stderr, "OpenGL Framebuffer error: GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT_EXT\n");
			return -1;
		case GL_FRAMEBUFFER_UNSUPPORTED_EXT:
			fprintf( stderr, "OpenGL Framebuffer error: GL_FRAMEBUFFER_UNSUPPORTED_EXT\n");
			return -2;
		case GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT_EXT:
			fprintf( stderr, "OpenGL Framebuffer error: GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT_EXT\n");
			return -3;
		case GL_FRAMEBUFFER_INCOMPLETE_DIMENSIONS_EXT:
			fprintf( stderr, "OpenGL Framebuffer error: GL_FRAMEBUFFER_INCOMPLETE_DIMENSIONS_EXT\n");
			return -4;
		case GL_FRAMEBUFFER_INCOMPLETE_FORMATS_EXT:
			fprintf( stderr, "OpenGL Framebuffer error: GL_FRAMEBUFFER_INCOMPLETE_FORMATS_EXT\n");
			return -5;
		case GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER_EXT:
			fprintf( stderr, "OpenGL Framebuffer error: GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER_EXT\n");
			return -6;
		case GL_FRAMEBUFFER_INCOMPLETE_READ_BUFFER_EXT:
			fprintf( stderr, "OpenGL Framebuffer error: GL_FRAMEBUFFER_INCOMPLETE_READ_BUFFER_EXT\n");
			return -7;
		default:
			fprintf( stderr, "UNKNWON error with OpenGL Framebuffer\n");
			return -8;
	}

	if( do_clear )
		glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT );


	return 0;
}

void RFBufferDone( struct RFBuffer *rb )
{
	unsigned i;

	for( i = 0; i < rb->outextures; i++ )
	{
		glFramebufferTexture2DEXT( GL_FRAMEBUFFER_EXT, GL_COLOR_ATTACHMENT0_EXT + i, 
			GL_TEXTURE_2D, 0, 0 );

		glActiveTextureARB( GL_TEXTURE0_ARB + i );
		glDisable( GL_TEXTURE_2D );
	}

	glBindFramebufferEXT( GL_FRAMEBUFFER_EXT, 0 );
	glBindRenderbufferEXT( GL_RENDERBUFFER_EXT, 0 );

	RenderW = ScreenW;
	RenderH = ScreenH;

	glViewport( 0, 0, ScreenW, ScreenH );
}

void DestroyRFBuffer( struct RFBuffer *rb )
{
	if( rb->use_depth_buffer )
		glDeleteRenderbuffersEXT( 1, &rb->renderbuffer );
	glDeleteFramebuffersEXT( 1, &rb->outputbuffer );
}





//VBOs, etc.


struct VertexData * VertexDataCreate()
{
	struct VertexData * vd = malloc( sizeof( struct VertexData ) );
	vd->vertexcount = 0;
	vd->stride = 1;
	vd->vbo = 0;
	return vd;
}

void UpdateVertexData( struct VertexData * vd, float * Verts, int iNumVerts, int iStride )
{
	vd->stride = iStride;

	if( !vd->vbo )
	{
		if( FreeBOHead != -1 )
			vd->vbo = FreeBOs[FreeBOHead--];
		else
			glGenBuffersARB( 1, &vd->vbo );
	}

	if( !Verts )
	{
		glBindBufferARB( GL_PIXEL_PACK_BUFFER_ARB, vd->vbo );
		glBufferDataARB( GL_PIXEL_PACK_BUFFER_ARB, iNumVerts*4 * sizeof( float ), 0, GL_STREAM_COPY );
		glBindBufferARB( GL_PIXEL_PACK_BUFFER_ARB, 0 );
		//glBufferDataARB( GL_ARRAY_BUFFER_ARB, iNumVerts * iStride*4, 0, GL_DYNAMIC_DRAW );
	}
	else
	{
		glBindBufferARB( GL_ARRAY_BUFFER_ARB, vd->vbo  );
		glBufferDataARB( GL_ARRAY_BUFFER_ARB, iNumVerts * iStride * sizeof( float ), Verts, GL_STATIC_DRAW_ARB );
		glBindBufferARB( GL_ARRAY_BUFFER_ARB, 0 );
	}
}

void DestroyVertexData( struct VertexData * vd )
{
	if( FreeBOHead+1 < MAX_STORAGE )
		FreeBOs[++FreeBOHead] = vd->vbo;
	else
		glDeleteBuffersARB( 1, &vd->vbo );
	free( vd );
}


struct IndexData * IndexDataCreate()
{
	struct IndexData * ret = malloc( sizeof( struct IndexData ) );
	ret->indexcount = 0;
#ifdef USE_IBO
	ret->ido = 0;
#else
	ret->indexdata = 0;
#endif
}

void UpdateIndexData( struct IndexData * id, int indexcount, int * data )
{
	int i;

	id->indexcount = indexcount;
#ifdef USE_IBO
	if( !id->ido )
	{
		if( FreeBOHead != -1 )
			id->ido = FreeBOs[FreeBOHead--];
		else
			glGenBuffersARB( 1, &id->ido );
	}

	glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, id->ido);
	glBufferData(GL_ELEMENT_ARRAY_BUFFER, indexcount*sizeof(int), data, GL_STATIC_DRAW);
	glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0);
#else


	if( id->indexdata ) free( id->indexdata );
	id->indexdata = malloc( sizeof( GLuint ) * indexcount );
	for( i = 0; i < indexcount; i++ )
		id->indexdata[i] = data[i];
#endif

}

void DestroyIndexData( struct IndexData * id )
{
	if( id )
	{
#ifdef USE_IBO
		if( id->ido )
		{
			if( FreeBOHead+1 < MAX_STORAGE )
				FreeBOs[++FreeBOHead] = id->ido;
			else
				glDeleteBuffersARB( 1, &id->ido );
		}
#else
		if( id->indexdata )
			free( id->indexdata );
#endif
		free( id );
	}
}






struct GPUGeometry * CreateGeometry( struct IndexData * indices, int vertexcount, struct VertexData ** verts, char ** names, int unique, GLint mode )
{
	int i, j;
	struct GPUGeometry * ret = malloc( sizeof( struct GPUGeometry ) );
	ret->indices = indices;
	ret->vertexcount = vertexcount;
	ret->vertexdatas = verts;
	ret->uniquedata = unique;
	ret->names = malloc( sizeof( const char *) * vertexcount );
	ret->names[0] = 0;
	ret->mode = mode;
	ret->maxs[0] = -10000;
	ret->maxs[1] = -10000;
	ret->maxs[2] = -10000;
	ret->mins[0] = 10000;
	ret->mins[1] = 10000;
	ret->mins[2] = 10000;

	memset( &ret->textures[0], 0, sizeof( ret->textures ) );
	memset( &ret->todelete[0], 0, sizeof( ret->todelete ) );
	for( i = 1; i < vertexcount; i++ )
	{
		ret->names[i] = strdup( names[i] );
	}

	return ret;
}

void RenderGPUGeometry( struct GPUGeometry * g )
{
	struct VertexData ** vd  = g->vertexdatas;
	char ** names = g->names;
	int NumVertexSets = g->vertexcount;
	struct IndexData * id = g->indices;

	int i;
	int tcarrayset = 0;
	int normalarrayset = 0;
	int colorarrayset = 0;

	//Can't render.
	if( !vd[0] ) return;
	if( !(vd[0]->vbo) ) return;

	for( i = 0; i < MAX_TEXTURES; i++ )
	{
		if( g->textures[i] )
		{
			ActivateTexture( g->textures[i] );
		}
	}

	for( i = 1; i < NumVertexSets; ++i )
	{
		const char * name = names[i];

		if( !vd[i] ) continue;
		if( !vd[i]->vbo ) continue;

		glBindBufferARB( GL_ARRAY_BUFFER_ARB, vd[i]->vbo );

		if( strcmp( name, "texture" ) == 0 )
		{
		    glEnableClientState( GL_TEXTURE_COORD_ARRAY );
			glTexCoordPointer( vd[i]->stride, GL_FLOAT, 0, 0 );
			tcarrayset = 1;
		}
		else if( strcmp( name, "color" ) == 0 )
		{
		    glEnableClientState( GL_COLOR_ARRAY );
			glColorPointer( vd[i]->stride, GL_FLOAT, 0, 0 );
			colorarrayset = 1;
		}
		else if( strcmp( name, "normal" ) == 0 )
		{
		    glEnableClientState( GL_NORMAL_ARRAY );
			glNormalPointer( GL_FLOAT, vd[i]->stride*4, 0 );
			normalarrayset = 1;
		}
		else if( CurrentShader )
		{
			int iTexPosID = glGetAttribLocationARB( CurrentShader->program, name );
			glEnableVertexAttribArrayARB( iTexPosID );
			glVertexAttribPointerARB( iTexPosID, vd[i]->stride, GL_FLOAT, 0, 0, 0 );
		}
	}

	glBindBufferARB( GL_ARRAY_BUFFER_ARB, vd[0]->vbo );
	glVertexPointer( vd[0]->stride, GL_FLOAT, 0, 0 );

#ifdef USE_IBO
	glEnableClientState( GL_VERTEX_ARRAY );
	glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, id->ido);
	glDrawElements(GL_TRIANGLES, id->indexcount, GL_UNSIGNED_INT, 0);
	glDisableClientState( GL_VERTEX_ARRAY );
#else
	glEnableClientState( GL_VERTEX_ARRAY );
	glDrawElements( g->mode, id->indexcount, GL_UNSIGNED_INT, id->indexdata );
	glDisableClientState( GL_VERTEX_ARRAY );
#endif

	if( tcarrayset )
	{
	    glDisableClientState( GL_TEXTURE_COORD_ARRAY );
	}

	if( colorarrayset )
	{
	    glDisableClientState( GL_COLOR_ARRAY );
	}

	if( normalarrayset )
	{
		glDisableClientState( GL_NORMAL_ARRAY );
	}

	for( i = 0; i < MAX_TEXTURES; i++ )
	{
		if( g->textures[i] )
		{
			DeactivateTexture( g->textures[i] );
		}
	}

}

void AttachTextureToGeometry( struct GPUGeometry * g, struct Texture * texture, int place, int take_ownership_of )
{
	g->textures[place] = texture;
	g->todelete[place] = take_ownership_of;
}

void DestroyGPUGeometry( struct GPUGeometry * g )
{
	int i;
	for( i = 1; i < g->vertexcount; i++ )
	{
		free( g->names[i] );
	}
	free( g->names );

	if( g->uniquedata )
	{
		DestroyIndexData( g->indices );
		for( i = 0; i < g->vertexcount; i++ )
		{
			DestroyVertexData( g->vertexdatas[i] );
		}
	}

	for( i = 0; i < MAX_TEXTURES; i++ )
	{
		if( g->todelete[i] && g->textures[i] )
		{
			DestroyTexture( g->textures[i] );
		}
	}

	free( g );
}


void DrawSquare( float x, float y, float w, float h )
{
	glBegin(GL_QUADS);
	glTexCoord2f(0.0, 0.0);
	glVertex3f(0.0, 0.0, 0.0);
	glTexCoord2f(1.0, 0.0);
	glVertex3f(ScreenW, 0.0, 0.0);
	glTexCoord2f(1.0, 1.0);
	glVertex3f(ScreenW, ScreenH, 0.0);
	glTexCoord2f(0.0, 1.0);
	glVertex3f(0.0, ScreenH, 0.0);
	glEnd();
}






