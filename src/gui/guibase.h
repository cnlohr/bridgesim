#ifndef _GUIBASE_H
#define _GUIBASE_H

#define MAX_GUI_ELEMENTS 2048

#include "graphicscore.h"

struct GUIWindow;

struct GUIBase
{
	float x, y;
	float w, h;
	float color[4];
	int depressed;
	int clicked;
	int focused;
	struct GUIWindow * wp;
	void (*Prerender)( struct GUIBase * b );
	void (*Render)( struct GUIBase * b );
	int  (*CheckClick)( struct GUIBase * b, float screenx, float screeny, int button, int down ); 	//Return 0 if received event.
	void (*HandleMove)( struct GUIBase * b, float screenx, float screeny, int buttonmask ); 	//Return 0 if received event.
	void (*HandleKeyboard)( struct GUIBase * b, char c, int down, int focused ); //If unfocused, treat as a hotkey only.
	void (*DestroyMe)( struct GUIBase * b );

	//High level functionality.
	void (*ProcessClick)( struct GUIBase * b ); //High level: this gets called if the user actually CLICKs a button.
};


void GenericHandleKeyboard( struct GUIBase * b, int c, int down, int focused ); //If unfocused, treat as a hotkey only.
int  GenericCheckClick( struct GUIBase * b, float screenx, float screeny, int button, int down );
void GenericHandleMove( struct GUIBase * b, float screenx, float screeny, int buttonmask ); 	//Return 0 if received event.




struct GUIWindow
{
	int width;
	int height;
	int focusid;  //-1 if no focus

	struct RFBuffer * renderbuffer;
	struct Texture * torender;

	struct GUIBase * elements[MAX_GUI_ELEMENTS];
};

struct GUIWindow * CreateGUIWindow();
void WindowRemoveElement( struct GUIWindow * w, struct GUIBase * g ); //removes only, does not delete.
void WindowAddElement( struct GUIWindow * w, struct GUIBase * g );
void WindowTakeFocus( struct GUIWindow * w, struct GUIBase * g );
void WindowHandleMouseMove( struct GUIWindow * w, float x, float y, int mask );
void WindowHandleMouseClick( struct GUIWindow * w, float x, float y, int button, int down );
void WindowHandleKeyboard( struct GUIWindow * w, int c, int down );
void WindowRender( struct GUIWindow * w );
void DestroyGUIWindow( struct GUIWindow * w );

#endif

