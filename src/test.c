#include <stdio.h>
#include <GL/glew.h>
#include <GL/freeglut.h>
#include "graphicscore.h"
#include "bitmapfont.h"
#include <os_generic.h>
#include "objreader.h"
#include <math.h>
#include "commonassets.h"
#include "guibase.h"
#include "button.h"
#include <string.h>


double ElapsedTime;
double DeltaTime, StartTime;
double LastFPSTime;
int framecountsincefps;
int fpscount;

struct GPUGeometry * helloworld;
struct GUIWindow * guiwindow;

void idle()
{
	glutPostRedisplay();
}

void reshape(int w, int h)
{
	ScreenW = w;
	ScreenH = h;

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
	RenderW = ScreenW;
	RenderH = ScreenH;


	WindowRender( guiwindow );

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
	glOrtho(0, ScreenW, 0, ScreenH, -1, 1);
	glDepthFunc(GL_ALWAYS);
	glScalef(1, -1, 1);
	glTranslatef(0, -ScreenH, 0);

	glMatrixMode(GL_MODELVIEW);
	glLoadIdentity();

	char st[15];
	sprintf( st, "FPS: %d", fpscount );
	glRasterPos2f(80, 50);
	glutBitmapString( GLUT_BITMAP_9_BY_15, st );


	ActivateTexture( guiwindow->torender );
	glTranslatef( 0, 200, 0 );
	glBegin(GL_QUADS);
	glTexCoord2f(0.0, 0.0);
	glVertex3f(0.0, 0.0, 0.0);
	glTexCoord2f(1.0, 0.0);
	glVertex3f(300.0, 0.0, 0.0);
	glTexCoord2f(1.0, 1.0);
	glVertex3f(300.0, 300.0, 0.0);
	glTexCoord2f(0.0, 1.0);
	glVertex3f(0.0, 300.0, 0.0);
	glEnd();
	DeactivateTexture( guiwindow->torender );


	glLoadIdentity();

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

	guiwindow = CreateGUIWindow( );
	guiwindow->width = 300;
	guiwindow->height = 300;
	struct GUIBase * b;
	WindowAddElement( guiwindow, b = CreateButton( guiwindow, "Hi!" ) );

	glutDisplayFunc( display );
	glutReshapeFunc( reshape );
	glutIdleFunc( idle );
	glutMainLoop();
	return 0;
}


