#include "button.h"
#include <stdlib.h>

struct Button * CreateButton()
{
	struct Button * ret = malloc( sizeof( struct Button ) );
	ret->text = "test";
	ret->x = 100;
	ret->y = 100;
	ret->w = 100;
	ret->h = 100;
	ret->color[0] = 1;
	ret->color[1] = 1;
	ret->color[2] = 0;
	ret->color[3] = 1;
	ret->depressed = 0;
	ret->oldtext = 0;
	ret->geotext = 0;
}

void RenderButton( struct Button * b )
{
	if( b->text != b->oldtext || !b->geotext )
	{
		if( b->oldtext)
			free( b->oldtext );
		if( b->geotext )
			DestroyGPUGeometry( b->geotext );

		b->geotext = EmitGeometryFromFontString( OldSansBlack, b->text, TEXTFLIPY );
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

	glColor4f( 1,1,1,1 );

	if( b->geotext )
	{
		float mx = b->geotext->maxs[0]-b->geotext->mins[0];
		float my = b->geotext->maxs[1]-b->geotext->mins[1];

		float scaleby = 32.0 / OldSansBlack->fontsize;

		glTranslatef( b->x+(-b->w+mx)/2, b->y+(-b->h*scaleby+my)/2, 0 );

//		printf( "%f-%f   %f-%f\n", b->geotext->mins[0], b->geotext->maxs[0], b->geotext->mins[1], b->geotext->maxs[1] );
//		glScalef( 0.5, 0.5, 0.0 );

		glScalef( scaleby, scaleby, 0.0 );
		ApplyShader( TextShader, OverallUniforms );
		RenderGPUGeometry( b->geotext );
		CancelShader( TextShader );
	}


}


