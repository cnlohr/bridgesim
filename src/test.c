#include <stdio.h>
#include <GL/glew.h>
#include <GL/freeglut.h>
#include "graphicscore.h"
#include "bitmapfont.h"
#include <os_generic.h>
#include "objreader.h"
#include <math.h>
#include "commonassets.h"
#include "button.h"
#include <string.h>

float g_width, g_height;

double ElapsedTime;
double DeltaTime, StartTime;
double LastFPSTime;
int framecountsincefps;
int fpscount;

struct GPUGeometry * helloworld;
struct Button * testbutton;

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
	static double LastTime;
	ElapsedTime = OGGetAbsoluteTime() - StartTime;
	DeltaTime = ElapsedTime - LastTime;
	LastTime = ElapsedTime;

	if( LastFPSTime + 1 < ElapsedTime )
	{
		LastFPSTime += 1;
		fpscount = framecountsincefps;
		printf( "FPS: %d\n", fpscount );
		framecountsincefps = 0;
	}
	framecountsincefps++;

	CheckCommonAssets();

	glClearColor( .2, .2, .2, 0 );
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
	glEnable (GL_BLEND);
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
	glEnable( GL_DEPTH_TEST );
	glDepthFunc(GL_LESS);
	RenderW = g_width;
	RenderH = g_height;


/*
	RFBufferGo( myrb, 100, 100, 1, &torender, 1 );
	RenderW = 100;
	RenderH = 100;

	glMatrixMode(GL_PROJECTION);
	glLoadIdentity();
	gluPerspective( 45.0, 1.0, 0.1f, 500.0 );
	glMatrixMode(GL_MODELVIEW);
	glLoadIdentity();

	glRotatef( ElapsedTime * 100, 0, 0, 1 );
	glTranslatef( 0., 0., -10 );
	glColor3f( 1,1,1 );
	glRasterPos2f(1.5, .5);
	glutBitmapString( GLUT_BITMAP_9_BY_15, "(15,51)" );

	glutWireTeapot(1.0);


	RFBufferDone( myrb, g_width, g_height );
*/


	glMatrixMode(GL_PROJECTION);
	glLoadIdentity();
	glOrtho(0, g_width, 0, g_height, -1, 1);
	glDepthFunc(GL_ALWAYS);
	glScalef(1, -1, 1);
	glTranslatef(0, -g_height, 0);

	glMatrixMode(GL_MODELVIEW);
	glLoadIdentity();

	char st[15];
	sprintf( st, "FPS: %d", fpscount );
	glRasterPos2f(80, 50);
	glutBitmapString( GLUT_BITMAP_9_BY_15, st );



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


	glLoadIdentity();
	glScalef( 1.5, 1.5, 1.5 );
	RenderButton( testbutton );

	glFlush();
}

int main(int argc, char **argv)
{
	int i;
	glutInit( &argc, argv );
	glutCreateWindow( "Test" );
	if( glewInit() != GLEW_OK )
	{
		fprintf( stderr, "Error: GLEW Fault.\n" );
		return 0;
	}

	StartTime = OGGetAbsoluteTime();

	SetupCommonAssets();

	testbutton = CreateButton();
	testbutton->text = strdup( "Hello" );

	glutDisplayFunc( display );
	glutReshapeFunc( reshape );
	glutIdleFunc( idle );
	glutMainLoop();
	return 0;
}


