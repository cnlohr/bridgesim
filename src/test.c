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
#include "glutmain.h"
#include <string.h>


double StartTime;
double LastFPSTime;
int framecountsincefps;
int fpscount;

struct GPUGeometry * helloworld;
struct GUIWindow * guiwindow;

void MouseMotion( double x, double y, int mask )
{
	WindowHandleMouseMove( guiwindow, x, y, mask );
}

void MouseClick( double x, double y, int button, int state )
{
	WindowHandleMouseClick( guiwindow, x, y, button, state );
}

void HandleKeyboard( int c, int down )
{
	WindowHandleKeyboard( guiwindow, c, down );
}



void UpdatedDisplay(void)
{
	CheckCommonAssets();

	glClearColor( .2, .2, .2, 0 );
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
	glEnable (GL_BLEND);
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
	glEnable( GL_DEPTH_TEST );
	glDepthFunc(GL_LESS);

	guiwindow->width = ScreenW;
	guiwindow->height = ScreenH;
	WindowRender( guiwindow );

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
	DrawSquare(0,0,ScreenW,ScreenH );
	DeactivateTexture( guiwindow->torender );


	glLoadIdentity();

	glFlush();
}

int main(int argc, char **argv)
{
	StartGlutMain( argc, argv, "test", 640, 480 );

	SetupCommonAssets();

	guiwindow = CreateGUIWindow( );
	guiwindow->width = 300;
	guiwindow->height = 300;
	struct GUIBase * b;
	WindowAddElement( guiwindow, b = CreateButton( guiwindow, "Hi!" ) );

	SetMouseWarpMode( 0 );

	DoGlutLoop();
}


