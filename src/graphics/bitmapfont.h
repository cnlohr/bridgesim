#ifndef _BITMAPFONT_H
#define _BITMAPFONT_H


#include "graphicscore.h"

struct MChar
{
	float loffx;  //(U,V Tex coord) (Upper left)
	float loffy;
	float loffxe; //(U,V Tex coord) (Lower right)
	float loffye;
	int iW;			//Pixles Width
	int lbitrows;   //Pixels Height
	int bitmapleft; //Position left
	int bitmaptop;  //Position up (from bottom)
};

struct BitmapFont
{
	struct MChar chars[256];
	struct Texture * fonttex;
	float fontsize;
	float A, B, C; //???????
};

struct BitmapFont * LoadBitmapFontByName( const char * fontpath );

#define TEXTFLIPY 1

struct GPUGeometry * EmitGeometryFromFontString( struct BitmapFont * bf, const char * str, int flags );


#endif


