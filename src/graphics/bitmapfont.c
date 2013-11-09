#include "bitmapfont.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

struct BitmapFont * LoadBitmapFontByName( const char * fontpath )
{
	int line = 0;
	struct BitmapFont * ret = 0;
	char sfname[2048];
	FILE * f = fopen( fontpath, "r" );
	if( !f )
	{
		fprintf( stderr, "Error: could not open up path to: %s\n", fontpath );
	}

	if( strlen( fontpath ) > 1024 )
	{
		fprintf( stderr, "Error: pathname to font too long: %s\n", fontpath );
		fclose( f );
		return 0;
	}

	memcpy( sfname, fontpath, strlen( fontpath )+1 );
	char * rr = strrchr( sfname, '/' );

	if( !rr || fscanf( f, "%1000s\n", rr+1 ) != 1 )
	{
		fprintf( stderr, "Error: could not find font image in font: %s\n", fontpath );
		return 0;
	}
	
	struct Texture * t = CreateTexture();

	if( ReadTextureFromFile( t, sfname ) )
	{
		fprintf( stderr, "Error: could not load font image for: %s\n", fontpath );
		goto cancel;
	}

	UpdateDataInOpenGL( t );

	ret = malloc( sizeof( struct BitmapFont ) );
	memset( ret, 0, sizeof( struct BitmapFont ) );

	if( fscanf( f, "%f %f %f %f\n", &ret->fontsize, &ret->A, &ret->B, &ret->C ) != 4 )
	{
		fprintf( stderr, "Error: first line of font is corrupt: %s\n", fontpath );
		goto cancel;
	}

	while( !feof( f ) && !ferror( f ) )
	{
		struct MChar m;
		int actualchar;
		int r = fscanf( f, "%d %f %f %f %f %d %d %d %d\n", &actualchar, &m.loffx, &m.loffy,
			&m.loffxe, &m.loffye, &m.iW, &m.lbitrows, &m.bitmapleft, &m.bitmaptop );

		if( r != 9 )
		{
			fgetc( f );
			continue;
		}

		memcpy( &ret->chars[actualchar], &m, sizeof( struct MChar ) );

		line++;
	}

	ChangeTextureFilter( t, 1 );
	ret->fonttex = t;

	return ret;
cancel:
	fclose( f );
	DestroyTexture( t );
	if( ret )
		free( ret );
	return 0;
}

struct GPUGeometry * EmitGeometryFromFontString( struct BitmapFont * bf, const char * str, int flags )
{
	if( !bf )
	{
		fprintf( stderr, "Error: Fault.  Cannot find bitmapfont.\n ");
		return 0;
	}

	struct GPUGeometry * ret;
	struct VertexData * vd; //Places
	struct VertexData * tc; //Texture coords.
	struct IndexData * id;
	int slen, i, actualchars;
	int * indexdata;
	float * verts;
	float * tcs;
	int line = 0;
	float progressx = 0;

	float gminx = 1e20;
	float gminy = 1e20;
	float gmaxx = -1e20;
	float gmaxy = -1e20;

	if( str == 0 || *str == 0 ) return 0;
	slen = strlen( str );


	indexdata = malloc( 6 * sizeof(int) * slen );
	verts = malloc( 4 * 2 * sizeof( float ) * slen );
	tcs = malloc( 4 * 2 * sizeof( float ) * slen );

	actualchars = 0;

	for( i = 0; i < slen; i++ )
	{
		if( str[i] == '\n' )
		{
			line++;
			progressx = 0;
			continue;
		}

		struct MChar * mc = &bf->chars[(unsigned char)str[i]];
		indexdata[i*6+0] = i * 4;
		indexdata[i*6+1] = i * 4 + 1;
		indexdata[i*6+2] = i * 4 + 2;
		indexdata[i*6+3] = i * 4 + 2;
		indexdata[i*6+4] = i * 4 + 1;
		indexdata[i*6+5] = i * 4 + 3;


		tcs[i*2*4+0] = mc->loffx;  tcs[i*2*4+1] = mc->loffy;
		tcs[i*2*4+2] = mc->loffxe; tcs[i*2*4+3] = mc->loffy;
		tcs[i*2*4+4] = mc->loffx;  tcs[i*2*4+5] = mc->loffye;
		tcs[i*2*4+6] = mc->loffxe; tcs[i*2*4+7] = mc->loffye;


		float minx = progressx;// + mc->bitmapleft/3.0f;
		float miny = mc->bitmaptop + line * bf->fontsize;
		float maxx = minx + mc->iW;
		float maxy = mc->bitmaptop - mc->lbitrows + line * bf->fontsize;

		if( flags & TEXTFLIPY )
		{
			maxy = bf->fontsize - maxy;
			miny = bf->fontsize - miny;
		}

		verts[i*2*4+0] = minx; verts[i*2*4+1] = miny;
		verts[i*2*4+2] = maxx; verts[i*2*4+3] = miny;
		verts[i*2*4+4] = minx; verts[i*2*4+5] = maxy;
		verts[i*2*4+6] = maxx; verts[i*2*4+7] = maxy;

		if( minx < gminx ) gminx = minx;
		if( miny < gminy ) gminy = miny;
		if( maxx > gmaxx ) gmaxx = maxx;
		if( maxy > gmaxy ) gmaxy = maxy;

		actualchars++;
		progressx += mc->iW + bf->A;
	}

	id = IndexDataCreate();
	vd = VertexDataCreate();
	tc = VertexDataCreate();
	
	UpdateIndexData( id, 6 * actualchars, indexdata );
	UpdateVertexData( vd, verts, actualchars * 4, 2 );
	UpdateVertexData( tc, tcs, actualchars * 4, 2 );

	free( indexdata );
	free( verts );
	free( tcs );

	struct VertexData ** vertslist = malloc( sizeof( struct VertexData * ) * 2 );
	vertslist[0] = vd;
	vertslist[1] = tc;
	char ** names = malloc( sizeof( char * ) * 2 );
	names[0] = 0;
	names[1] = strdup( "texture" );

	ret = CreateGeometry( id, 2, vertslist, names, 1, GL_TRIANGLES );
	ret->mins[0] = gminx;
	ret->mins[1] = gminy;
	ret->mins[2] = 0;
	ret->maxs[0] = gmaxx;
	ret->maxs[1] = gmaxy;
	ret->maxs[2] = 0;

	AttachTextureToGeometry( ret, bf->fonttex, 0, 0 );

	free( names[1] );
	free( names );

	return ret;
}


