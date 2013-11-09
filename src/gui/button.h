#ifndef _BUTTON_H
#define _BUTTON_H

#include "commonassets.h"
#include "guibase.h"

struct Button
{
	float x, y;
	float w, h;
	float color[4];
	int depressed;
	int clicked;
	int focused;
	struct GUIWindow * wp;
	void (*Prerender)( struct Button * b );
	void (*Render)( struct Button * b );
	int  (*CheckClick)( struct GUIBase * b, float screenx, float screeny, int button, int down ); 	//Return 0 if received event.
	void (*HandleMove)( struct GUIBase * b, float screenx, float screeny, int buttonmask ); 	//Return 0 if received event.
	void (*HandleKeyboard)( struct GUIBase * b, char c, int down, int focused ); //If unfocused, treat as a hotkey only.
	void (*DestroyMe)( struct Button * b );
	void (*ProcessClick)( struct Button * b );

	char * text;
	char * oldtext;
	struct GPUGeometry * geotext;
};

struct GUIBase * CreateButton( struct GUIWindow * parent, const char * text );

//Below here are kind of private-ish.
//Assumes you are in ortho or an orto-like mode.
void ButtonRender( struct Button * b );
void ButtonDestroyMe( struct Button * b );
void ButtonProcessClick( struct Button * b );

#endif


