#include <stdio.h>
#include <GL/glew.h>
#include <GL/freeglut.h>
#include "graphicscore.h"
#include <os_generic.h>
#include <math.h>

float g_width, g_height;

struct Shader * defshader;
struct UniformMatch * shaderprops;
struct Texture * testtex;

float Ambient[4] = { .1, .1, .1, 1 };
float Emission[4] = { 0, 0, 0, 1 };
float TexSlot = 0;
double StartTime;

struct RFBuffer * myrb;
struct Texture * torender;

void SetupShaderProps()
{
	shaderprops = UniformMatchMake( "AmbientColor", Ambient, 0, 4, 0 );
	shaderprops = UniformMatchMake( "EmissionColor", Emission, 0, 4, shaderprops );
	shaderprops = UniformMatchMake( "tex0", &TexSlot, 1, 0, shaderprops );
}

void idle()
{
	glutPostRedisplay();
}

void reshape(int w, int h)
{
	g_width = w;
	g_height = h;

	glViewport(0, 0, w, h);

}

void display(void)
{
	double ElapsedTime = OGGetAbsoluteTime() - StartTime;

	glClearColor( .2, .2, .2, 0 );
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
	glEnable (GL_BLEND);
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);



	RFBufferGo( myrb, 100+ElapsedTime*15, 100+ElapsedTime*15, 1, &torender, 1 );

	glMatrixMode(GL_PROJECTION);
	glLoadIdentity();
	gluPerspective( 45.0, 1.0, 0.1f, 500.0 );
	glDepthFunc(GL_LESS);
	glMatrixMode(GL_MODELVIEW);
	glLoadIdentity();

	glRotatef( ElapsedTime * 100, 0, 0, 1 );
	glTranslatef( 0., 0., -10 );
	glRasterPos2f(1.5, .5);
	glColor3f( 1,1,1 );
	glutWireTeapot(1.0);
	

	RFBufferDone( myrb, g_width, g_height );






	glMatrixMode(GL_PROJECTION);
	glLoadIdentity();
	gluPerspective( 45.0, (GLfloat)(g_width)/(GLfloat)(g_height), 0.1f, 500.0 );
	glDepthFunc(GL_LESS);
	glMatrixMode(GL_MODELVIEW);
	glLoadIdentity();

	glRotatef( ElapsedTime * 100, 0, 0, 1 );
	glTranslatef( 0., 0., -10 );
	glRasterPos2f(1.5, .5);
	glColor3f( 1,1,1 );
	glutBitmapString( GLUT_BITMAP_9_BY_15, "(15,51)" );
	glutWireTeapot(1.0);

	glMatrixMode(GL_PROJECTION);
	glLoadIdentity();
	glOrtho(0, g_width, 0, g_height, -1, 1);
	glDepthFunc(GL_ALWAYS);
	glScalef(1, -1, 1);
	glTranslatef(0, -g_height, 0);

	glMatrixMode(GL_MODELVIEW);
	glLoadIdentity();

	CheckForNewerShader( defshader );
	ApplyShader( defshader,shaderprops );

	ActivateTexture( testtex );

	glBegin(GL_QUADS);
	glTexCoord2f(0.0, 0.0);
	glVertex3f(0.0, 0.0, 0.0);
	glTexCoord2f(1.0, 0.0);
	glVertex3f(100.0, 0.0, 0.0);
	glTexCoord2f(1.0, 1.0);
	glVertex3f(100.0, 100.0, 0.0);
	glTexCoord2f(0.0, 1.0);
	glVertex3f(0.0, 100.0, 0.0);
	glEnd();

	DeactivateTexture( testtex);

	CancelShader( defshader);

	ActivateTexture( torender );
	glScalef( 2, 2, 1 );
	glBegin(GL_QUADS);
	glTexCoord2f(0.0, 0.0);
	glVertex3f(100.0, 0.0, 0.0);
	glTexCoord2f(1.0, 0.0);
	glVertex3f(200.0, 0.0, 0.0);
	glTexCoord2f(1.0, 1.0);
	glVertex3f(200.0, 100.0, 0.0);
	glTexCoord2f(0.0, 1.0);
	glVertex3f(100.0, 100.0, 0.0);
	glEnd();
	DeactivateTexture( torender);

	glFlush();
}

int main(int argc, char **argv)
{
	glutInit( &argc, argv );
	glutCreateWindow( "Test" );
	if( glewInit() != GLEW_OK )
	{
		fprintf( stderr, "Error: GLEW Fault.\n" );
		return 0;
	}

	StartTime = OGGetAbsoluteTime();

	defshader = CreateShader( "shaders/default" );
	SetupShaderProps();

	testtex = CreateTexture();
	ReadTextureFromFile( testtex, "test.jpg" );
	UpdateDataInOpenGL( testtex );

	myrb = MakeRFBuffer( 1, TTRGBA );
	torender = CreateTexture();

	glutDisplayFunc( display );
	glutReshapeFunc( reshape );
	glutIdleFunc( idle );
	glutMainLoop();
	return 0;
}


