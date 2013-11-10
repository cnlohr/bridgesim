#include <stdio.h>
#include <GL/glew.h>
#include <GL/freeglut.h>
#include "graphicscore.h"
#include "bitmapfont.h"
#include <os_generic.h>
#include "objreader.h"
#include <math.h>

struct Shader * modelshader;
struct Shader * defshader;
struct Shader * texcoords;
struct Shader * textshader;
struct UniformMatch * shaderprops;
struct Texture * testtex;

float Ambient[4] = { .1, .1, .1, 1 };
float Emission[4] = { 0, 0, 0, 1 };
float TexSlot = 0;
float TexSlot1 = 0;
double StartTime;

struct RFBuffer * myrb;
struct Texture * torender;
struct BitmapFont * mbf;
struct BitmapFont * captureitfont;
struct GPUGeometry * helloworld = 0;
struct GPUGeometry * bridgesim = 0;
struct GPUGeometry * lottatext = 0;


struct GPUGeometry * modelgeo;

double ElapsedTime;
double DeltaTime;
double LastFPSTime;
int framecountsincefps;
int fpscount;

void SetupShaderProps()
{
	shaderprops = UniformMatchMake( "AmbientColor", Ambient, 0, 4, 0 );
	shaderprops = UniformMatchMake( "EmissionColor", Emission, 0, 4, shaderprops );
	shaderprops = UniformMatchMake( "tex0", &TexSlot, 1, 0, shaderprops );
	shaderprops = UniformMatchMake( "tex1", &TexSlot1, 1, 0, shaderprops );
}

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

	glClearColor( .2, .2, .2, 0 );
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
	glEnable (GL_BLEND);
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
	glEnable( GL_DEPTH_TEST );
	glDepthFunc(GL_LESS);


	RFBufferGo( myrb, 100, 100, 1, &torender, 1 );

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


	RFBufferDone( myrb );



	glMatrixMode(GL_PROJECTION);
	glLoadIdentity();
	gluPerspective( 45.0, (GLfloat)(ScreenW)/(GLfloat)(ScreenH), 0.1f, 500.0 );
	glMatrixMode(GL_MODELVIEW);
	glLoadIdentity();

	glTranslatef( 0., 0., -10 );
	glRotatef( ElapsedTime * 100, 0, 1, 0 );
	glColor3f( 1,1,1 );

	CheckForNewerShader( modelshader );
	ApplyShader( modelshader, shaderprops );
	RenderGPUGeometry( modelgeo );
	CancelShader( modelshader );


	glLoadIdentity();
	glTranslatef( 0., -6., -30 );
	glColor4f( 1,1,0,1 );
	glScalef( .07, .07, .07 );
	CheckForNewerShader( textshader );
	ApplyShader( textshader, shaderprops );
	RenderGPUGeometry( helloworld );
	CancelShader( textshader );
	glColor4f( 1,1,1,1 );



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


	glPushMatrix();
	glTranslatef( 0, 100, 0 );
	glScalef( 0.1*ScreenW/250.0, 0.1*ScreenH/250.0, 0.0 );
	glScalef(1, -1, 1);
	char stx[85];
	sprintf( stx, "[BRIDGE SIM %4.2f]", ElapsedTime );
	if( bridgesim ) DestroyGPUGeometry( bridgesim );
	bridgesim = EmitGeometryFromFontString( captureitfont, stx, 0 );
	CheckForNewerShader( textshader );
	ApplyShader( textshader, shaderprops );
	RenderGPUGeometry( bridgesim );
	CancelShader( textshader );
	glPopMatrix();



/*
	glPushMatrix();
	glTranslatef( 0, 20, 0 );
	glScalef( 0.005*g_width/250.0, 0.005*g_width/250.0, 0.0 );
	CheckForNewerShader( texcoords );
	ApplyShader( texcoords, shaderprops );
	RenderGPUGeometry( lottatext );
	RenderGPUGeometry( lottatext );
	CancelShader( texcoords );
	glPopMatrix();

*/

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

	defshader = CreateShader( "../../assets/shaders/default" );
	texcoords = CreateShader( "../../assets/shaders/texcoords" );
	textshader = CreateShader( "../../assets/shaders/text" );
	modelshader = CreateShader( "../../assets/shaders/model" );
	SetupShaderProps();

	testtex = CreateTexture();
	ReadTextureFromFile( testtex, "test.jpg" );
	UpdateDataInOpenGL( testtex );

	myrb = MakeRFBuffer( 1, TTRGBA );
	torender = CreateTexture();

	mbf = LoadBitmapFontByName( "../../assets/fonts/OldSansBlack.hgfont" );
	captureitfont = LoadBitmapFontByName( "../../assets/fonts/CaptureIt.hgfont" );
	helloworld = EmitGeometryFromFontString( mbf, "Hello, world.", 0 );


	struct OBJFile * model = OpenOBJ( "../../assets/models/ball.obj", 1 );
	modelgeo = model->Objects[0]->geometry;


	char stx[65536];
	for( i = 0; i < 65535; i++ )
	{
		if( (i % 350) == 0 )
			stx[i] = '\n';
		else
			stx[i] = (rand()%95) + 32;

	}
	stx[i] = 0;
	lottatext = EmitGeometryFromFontString( captureitfont, stx, 0 );
	RenderGPUGeometry( lottatext );

	glutDisplayFunc( display );
	glutReshapeFunc( reshape );
	glutIdleFunc( idle );
	glutMainLoop();
	return 0;
}


