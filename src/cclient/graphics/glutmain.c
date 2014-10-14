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


double StartTime;
double LastFPSTime;
int framecountsincefps;
int fpscount;
int domousewarp;

double absoluteMouseMotionX = 0;
double absoluteMouseMotionY = 0;
double currentMouseX = 0;
double currentMouseY = 0;

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
	TotalTime = OGGetAbsoluteTime() - StartTime;
	DeltaTime = TotalTime - LastTime;
	LastTime = TotalTime;

	if( ( ScreenW <= 0 || ScreenH <= 0 ) && TotalTime < 1.0 ) return;

	if( LastFPSTime + 1 < TotalTime )
	{
		LastFPSTime += 1;
		fpscount = framecountsincefps;
		printf( "FPS: %d\n", fpscount );
		framecountsincefps = 0;
	}
	framecountsincefps++;

	RenderW = ScreenW;
	RenderH = ScreenH;	

	UpdatedDisplay();

	glFlush();
}

void myupfunc( unsigned char key, int x, int y )
{
	HandleKeyboard( key, 0 );
}

void mykeyfunc( unsigned char key, int x, int y )
{
	HandleKeyboard( key, 1 );
}

void myspecialfunc( int key, int x, int y )
{
	HandleKeyboard( key, 1 );
}

void myspecialupfunc( int key, int x, int y )
{
	HandleKeyboard( key, 0 );
}


static int mousebuttonmask = 0;

void mousepassive(int x, int y)
{
	if( domousewarp )
	{
		absoluteMouseMotionX += x - (int)(RenderW/2);
		absoluteMouseMotionY += y - (int)(RenderH/2);
		glutWarpPointer( (int)(RenderW/2), (int)(RenderH/2) );

		MouseMotion( x - (int)(RenderW/2), y - (int)(RenderH/2), mousebuttonmask );
	}
	else
	{
		currentMouseY = y;
		currentMouseX = x;
		MouseMotion( x, y, mousebuttonmask );
	}
}

void mousemotion(int x, int y)
{
	mousepassive( x, y );
}

void mousefunc( int button, int state, int x, int y )
{
	if( state )
	{
		mousebuttonmask |= 1<<button;
	}
	else
	{
		mousebuttonmask &= ~(1<<button);
	}
	if( domousewarp )
	{
		MouseClick( absoluteMouseMotionX, absoluteMouseMotionY, button, state );
	}
	else
	{
		double dx = x;
		double dy = y;
		MouseClick( dx, dy, button, state );
	}
}


int StartGlutMain(int argc, char **argv, const char * title, int initsizeX, int initsizeY)
{
	int i;
	glutInitWindowSize(initsizeX,initsizeY);
	glutInit( &argc, argv );
	glutCreateWindow( "Test" );
	if( glewInit() != GLEW_OK )
	{
		fprintf( stderr, "Error: GLEW Fault.\n" );
		return 0;
	}

	StartTime = OGGetAbsoluteTime();

	glutSetKeyRepeat( GLUT_KEY_REPEAT_OFF );

	glutDisplayFunc( display );
	glutReshapeFunc( reshape );
	glutIdleFunc( idle );
	glutKeyboardFunc( mykeyfunc );
	glutKeyboardUpFunc( myupfunc );
	glutSpecialFunc( myspecialfunc );
	glutSpecialUpFunc( myspecialupfunc );

	glutMotionFunc( mousemotion );
	glutPassiveMotionFunc( mousepassive );
	glutMouseFunc( mousefunc );
}

void DoGlutLoop()
{
	glutMainLoop();
}

void SetMouseWarpMode( int dowarp )
{
	domousewarp = dowarp;
	if( dowarp )
	{
		glutSetCursor( GLUT_CURSOR_NONE );
	}
	else
	{
		glutSetCursor( GLUT_CURSOR_INHERIT );
	}
}

