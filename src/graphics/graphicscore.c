#include <sys/types.h>
#include <stdint.h>

#include <GL/glew.h>
#include "graphicscore.h"
#include <GL/glext.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

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



/*
struct Shader
{
	GLuint vertex;
	GLuint fragment;
	GLint  compiled;
};
*/
struct Shader * CreateShader( const char * file )
{
	struct Shader * ret;
	int lnl = strlen( file );
	char * lfv, *lff;
	unsigned char * VertexText;
	unsigned char * FragmentText;
	GLint compiled;

	lfv = malloc( lnl + 8 );
	sprintf( lfv, "%s.vert", file );
	VertexText = ReadDataFile( lfv );
	if( !VertexText )
	{
		fprintf( stderr, "Error: Could not open vertex shader: %s\n", lfv );
		free( lfv );
		return 0;
	}

	lff = malloc( lnl + 8 );
	sprintf( lff, "%s.frag", file );
	FragmentText = ReadDataFile( lff );
	if( !FragmentText )
	{
		fprintf( stderr, "Error: Could not open fragment shader: %s\n", lff );
		free( lff );
		free( lfv );
		free( VertexText );
		return 0;
	}

	ret = malloc( sizeof( struct Shader ) );
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
		fprintf( stderr, "Error: Could not compile vertex shader: %s\n", lfv );
		ShaderErrorPrint( ret->vertex );

		goto cancel;
	}


	glCompileShader(ret->fragment);
	glGetShaderiv(ret->fragment, GL_COMPILE_STATUS, &compiled);
	if(!compiled)
	{
		fprintf( stderr, "Error: Could not compile fragment shader: %s\n", lff );
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
		fprintf( stderr, "Error: Could not link shader: %s\n", file );
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


	return ret;
cancel_with_program:
	glDetachShader(ret->program, ret->vertex);
	glDetachShader(ret->program, ret->fragment );
	glDeleteShader(ret->program);
cancel:
	free( lff );
	free( lfv );
	free( VertexText );
	free( FragmentText );

	glDeleteShader( ret->vertex );
	glDeleteShader( ret->fragment );
	free( ret );
	return 0;

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

void CancelShader()
{
	glUseProgramObjectARB( 0 );
}

