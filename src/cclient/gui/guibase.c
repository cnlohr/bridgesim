#include "guibase.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

void  GenericHandleKeyboard( struct GUIBase * b, int c, int down, int focused )
{
	if( b->focused )
	{
		if( c == '\n' || c == ' ' )
		{
			if( b->depressed && !down )
			{
				b->ProcessClick( b );
			}
			else if( down )
			{
				b->depressed = 1;
			}
		}
	}
}

void GenericHandleMove( struct GUIBase * b, float screenx, float screeny, int buttonmask )
{
	int inside = b->x <= screenx && b->y <= screeny && b->x + b->w >= screenx && b->y + b->h >= screeny;
	if( (buttonmask & 1) && b->clicked )
	{
		if( inside )
			b->depressed = 1;
		else
			b->depressed = 0;
	}
}

int  GenericCheckClick( struct GUIBase * b, float screenx, float screeny, int button, int down )
{
	int inside = b->x <= screenx && b->y <= screeny && b->x + b->w >= screenx && b->y + b->h >= screeny;

	if( button != 0 ) return;

	if( down )
	{
		if( inside )
		{
			b->depressed = 1;
			b->clicked = 1;
			if( b->w )
			{
				WindowTakeFocus( b->wp, b );
			}
			return 0;
		}
		else
			return -1;
	}
	else
	{
		if( b->clicked && inside )
		{
			b->ProcessClick( b );
		}
		b->clicked = 0;
		b->depressed = 0;
	}
}









struct GUIWindow * CreateGUIWindow()
{
	struct GUIWindow * ret = malloc( sizeof( struct GUIWindow ) );
	memset( ret->elements, 0, sizeof( ret->elements ) );
	ret->renderbuffer = MakeRFBuffer( 0, TTRGBA );
	ret->torender = CreateTexture();
	return ret;
}

void WindowHandleMouseMove( struct GUIWindow * w, float x, float y, int mask )
{
	int i;
	for( i = 0; i < MAX_GUI_ELEMENTS; i++ )
	{
		struct GUIBase * g = w->elements[i];
		if( g && g->HandleMove )
			g->HandleMove( g, x, y, mask );
	}
}

void WindowHandleMouseClick( struct GUIWindow * w, float x, float y, int button, int down )
{
	int i;

	for( i = 0; i < MAX_GUI_ELEMENTS; i++ )
	{
		struct GUIBase * g = w->elements[i];

		if( g && g->CheckClick )
			g->CheckClick( g, x, y, button, down );
	}
}

void WindowHandleKeyboard( struct GUIWindow * w, int c, int down )
{
	int i;
	for( i = 0; i < MAX_GUI_ELEMENTS; i++ )
	{
		struct GUIBase * g = w->elements[i];

		if( g && g->HandleKeyboard )
			g->HandleKeyboard( g, c, down, i==w->focusid );
	}
}


void DestroyGUIWindow( struct GUIWindow * w )
{
	int i;
	for( i = 0; i < MAX_GUI_ELEMENTS; i++ )
	{
		struct GUIBase * g = w->elements[i];
		if( g && g->DestroyMe ) g->DestroyMe( g );
	}

	if( w->renderbuffer ) DestroyRFBuffer( w->renderbuffer );
	if( w->torender ) DestroyTexture( w->torender );
}


void WindowTakeFocus( struct GUIWindow * w, struct GUIBase * g )
{
	int i;
	for( i = 0; i < MAX_GUI_ELEMENTS; i++ )
	{
		if( g == w->elements[i] )
		{
			if( w->focusid >= 0 )
				w->elements[w->focusid]->focused = 0;
			w->elements[i]->focused = 1;
			w->focusid = i;
			return;
		}
	}
}

void WindowRender( struct GUIWindow * w  )
{
	int i;
	for( i = 0; i < MAX_GUI_ELEMENTS; i++ )
	{
		struct GUIBase * g = w->elements[i];
		if( g && g->Prerender ) g->Prerender( g );
	}

	RFBufferGo( w->renderbuffer, w->width, w->height, 1, &w->torender, 1 );

	glMatrixMode(GL_PROJECTION);
	glPushMatrix();
	glLoadIdentity();
	glOrtho(0, w->width, 0, w->height, -1, 1);
	glDepthFunc(GL_ALWAYS);

//Flip-y
//	glScalef(1, -1, 1);
//	glTranslatef(0, -w->height, 0);

	glMatrixMode(GL_MODELVIEW);
	glLoadIdentity();
	glPushMatrix();

	for( i = 0; i < MAX_GUI_ELEMENTS; i++ )
	{
		struct GUIBase * g = w->elements[i];
		if( g && g->Render ) g->Render( g );
	}


	glMatrixMode(GL_PROJECTION);
	glPopMatrix();
	glMatrixMode(GL_MODELVIEW);
	glPopMatrix();


	RFBufferDone( w->renderbuffer );
}

void WindowAddElement( struct GUIWindow * w, struct GUIBase * g )
{
	int i;
	for( i = 0; i < MAX_GUI_ELEMENTS; i++ )
	{
		if( !w->elements[i] )
		{
			w->elements[i] = g;
			return;
		}
	}

	if( i == MAX_GUI_ELEMENTS )
	{
		fprintf( stderr, "Error: too many GUI Elements.\n" );
	}
}


void WindowRemoveElement( struct GUIWindow * w, struct GUIBase * g )
{
	int i;
	for( i = 0; i < MAX_GUI_ELEMENTS; i++ )
	{
		if( w->elements[i] == g )
			w->elements[i] = 0;
	}

}


