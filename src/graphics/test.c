#include <stdio.h>
#include <GL/freeglut.h>


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
	glClearColor( .2, .2, .2, 1 );
	glClear(GL_COLOR_BUFFER_BIT);

	glRasterPos2f(10, 100);
	glColor3f( 1,0,1 );
	glutBitmapString( GLUT_BITMAP_9_BY_15, "(15,51)" );

/*
  glBegin(GL_TRIANGLES);
    glColor3f(0.0, 0.0, 1.0);
    glVertex2i(0, 0);
    glColor3f(0.0, 1.0, 0.0);
    glVertex2i(200, 200);
    glColor3f(1.0, 0.0, 0.0);
    glVertex2i(20, 200);
  glEnd();
*/
	glFlush();
}

int main(int argc, char **argv)
{
	glutInit( &argc, argv );
	glutCreateWindow( "Test" );
	glutDisplayFunc( display );
	glutReshapeFunc( reshape );
	glutMainLoop();
	return 0;
}
