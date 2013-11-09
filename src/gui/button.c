#include "button.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

struct GUIBase * CreateButton( struct GUIWindow * parent, const char * text )
{
	struct Button * ret = malloc( sizeof( struct Button ) );
	ret->text = text?strdup(text):0;
	ret->x = 100;
	ret->y = 100;
	ret->w = 100;
	ret->h = 100;
	ret->color[0] = 1;
	ret->color[1] = 1;
	ret->color[2] = 0;
	ret->color[3] = 1;
	ret->wp = parent;
	ret->focused = 0;
	ret->clicked = 0;
	ret->depressed = 0;
	ret->oldtext = 0;
	ret->geotext = 0;

	ret->Prerender = 0;
	ret->Render = ButtonRender;
	ret->CheckClick = GenericCheckClick;
	ret->HandleMove = GenericHandleMove;
	ret->HandleKeyboard = GenericHandleKeyboard;
	ret->DestroyMe = ButtonDestroyMe;
	ret->ProcessClick = ButtonProcessClick;

	return (struct GUIBase*)ret;
}


void ButtonDestroyMe( struct Button * b )
{
	WindowRemoveElement( b->wp, (struct GUIBase*)b );
	if( b->text ) free( b->text );
	if( b->oldtext ) free( b->oldtext );
	if( b->geotext ) DestroyGPUGeometry( b->geotext );
	free( b );
}


void ButtonProcessClick( struct Button * b )
{
	printf( "I GOT CLICKED!\n" );
}


void ButtonRender( struct Button * b )
{
	if( b->text != b->oldtext || !b->geotext )
	{
		if( b->oldtext)
			free( b->oldtext );
		if( b->geotext )
			DestroyGPUGeometry( b->geotext );

		b->geotext = EmitGeometryFromFontString( OldSansBlack, b->text, 0 );
		b->oldtext = b->text;
	}


	ApplyShader( ButtonShader, OverallUniforms );
	glColor4fv( b->color );
	glBegin(GL_QUADS);
	glTexCoord4f(0.0, 0.0, b->w, b->h);
	glVertex3f(b->x, b->y, 0.0);
	glTexCoord4f(b->w, 0.0, b->w, b->h);
	glVertex3f(b->x+b->w, b->y, 0.0);
	glTexCoord4f(b->w, b->h, b->w, b->h );
	glVertex3f(b->x+b->w, b->y+b->h, 0.0);
	glTexCoord4f(0.0, b->h, b->w, b->h );
	glVertex3f(b->x, b->y+b->h, 0.0);
	glEnd();
	CancelShader( ButtonShader );

	if( b->color[0] + b->color[1] + b->color[2] > 1.5 )
		glColor4f( 0, 0, 0, 1 );
	else
		glColor4f( 1,1,1,1 );

	if( b->geotext )
	{
		float mx = b->geotext->maxs[0]-b->geotext->mins[0];
		float my = b->geotext->maxs[1]-b->geotext->mins[1];

		float scaleby = 32.0 / OldSansBlack->fontsize;

		glTranslatef( b->x+(-b->w+mx)/2, b->y+(-b->h*scaleby+my)/2, 0 );

		glScalef( scaleby, scaleby, 0.0 );
		ApplyShader( TextShader, OverallUniforms );
		RenderGPUGeometry( b->geotext );
		CancelShader( TextShader );
	}

	glColor4f( 1,1,1,1 );

}


