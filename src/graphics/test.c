#include <stdio.h>
#include <GL/glew.h>
#include <GL/freeglut.h>
#include "graphicscore.h"
#include <os_generic.h>
#include <math.h>

struct Shader * defshader;
struct UniformMatch * shaderprops;
void HSVtoRGB( float hue, float sat, float value, float * r, float * g, float * b );

float Ambient[4] = { .1, .1, .1, 1 };
float Emission[4] = { 0, 0, 0, 1 };
double StartTime;

void SetupShaderProps()
{
	shaderprops = UniformMatchMake( "AmbientColor", Ambient, 0, 4, 0 );
	shaderprops = UniformMatchMake( "EmissionColor", Emission, 0, 4, shaderprops );
}

void idle()
{
	glutPostRedisplay();
}

void reshape(int w, int h)
{
	glViewport(0, 0, w, h);
	glMatrixMode(GL_PROJECTION);
	glLoadIdentity();
	glOrtho(0, w, 0, h, -1, 1);
	glScalef(1, -1, 1);
	glTranslatef(0, -h, 0);
}

void display(void)
{
	double ElapsedTime = OGGetAbsoluteTime() - StartTime;

	glClearColor( .2, .2, .2, 1 );
	glClear(GL_COLOR_BUFFER_BIT);

	glRasterPos2f(120, 100);
	glColor3f( 1,1,1 );
	glutBitmapString( GLUT_BITMAP_9_BY_15, "(15,51)" );


	HSVtoRGB( ElapsedTime, 1, 1, &Emission[0], &Emission[1], &Emission[2] );


	ApplyShader( defshader,shaderprops );

	glBegin(GL_TRIANGLES);
	glColor3f(0.0, 0.0, 1.0);
	glVertex2i(0, 0);
	glColor3f(0.0, 1.0, 0.0);
	glVertex2i(200, 200);
	glColor3f(1.0, 0.0, 0.0);
	glVertex2i(20, 200);
	glEnd();

	CancelShader();

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

	glutDisplayFunc( display );
	glutReshapeFunc( reshape );
	glutIdleFunc( idle );
	glutMainLoop();
	return 0;
}










void HSVtoRGB( float hue, float sat, float value, float * r, float * g, float * b )
{
	float pr = 0;
	float pg = 0;
	float pb = 0;

	short or = 0;
	short og = 0;
	short ob = 0;

	float ro = fmod( hue * 6, 6. );

	float avg = 0;

	ro = fmod( ro + 6 + 1, 6 ); //Hue was 60* off...

	if( ro < 1 ) //yellow->red
	{
		pr = 1;
		pg = 1. - ro;
	} else if( ro < 2 )
	{
		pr = 1;
		pb = ro - 1.;
	} else if( ro < 3 )
	{
		pr = 3. - ro;
		pb = 1;
	} else if( ro < 4 )
	{
		pb = 1;
		pg = ro - 3;
	} else if( ro < 5 )
	{
		pb = 5 - ro;
		pg = 1;
	} else
	{
		pg = 1;
		pr = ro - 5;
	}

	//Actually, above math is backwards, oops!
	pr *= value;
	pg *= value;
	pb *= value;

	avg += pr;
	avg += pg;
	avg += pb;

	pr = pr * sat + avg * (1.-sat);
	pg = pg * sat + avg * (1.-sat);
	pb = pb * sat + avg * (1.-sat);

	*r = pr;
	*g = pg;
	*b = pb;
}

