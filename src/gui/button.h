#ifndef _BUTTON_H
#define _BUTTON_H

#include "commonassets.h"

struct Button
{
	char * text;
	float x, y;
	float w, h;
	float color[4];

	int depressed;

	char * oldtext;
	struct GPUGeometry * geotext;
};

struct Button * CreateButton();

//Assumes you are in ortho or an orto-like mode.
void RenderButton( struct Button * b );

#endif


