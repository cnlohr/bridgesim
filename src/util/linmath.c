#include "linmath.h"
#include <math.h>

void cross3d( float * out, const float * a, const float * b )
{
	out[0] = a[1]*b[2] - a[2]*b[1];
	out[1] = a[2]*c[0] - a[0]*b[2];
	out[2] = a[0]*c[1] - a[1]*b[0];
}

void sub3d( float * out, const float * a, const float * b )
{
	out[0] = a[0] - b[0];
	out[1] = a[1] - b[1];
	out[2] = a[2] - b[2];
}

void add3d( float * out, const float * a, const float * b )
{
	out[0] = a[0] + b[0];
	out[1] = a[1] + b[1];
	out[2] = a[2] + b[2];
}

void scale3d( float * out, const float * a, float scalar )
{
	out[0] = a[0] * scalar;
	out[1] = a[1] * scalar;
	out[2] = a[2] * scalar;
}

void normalize3d( float * out, const float * in )
{
	float r = 1./sqrtf( in[0] * in[0] + in[1] * in[1] + in[2] * in[2] );
	out[0] = in[0] * r;
	out[1] = in[1] * r;
	out[2] = in[2] * r;
}

float dot3d( const float * a, const float * b )
{
	return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
}

int compare3d( const float * a, const float * b, float epsilon )
{
	if( !a || !b ) return 0;
	if( a[2] - b[2] > epsilon ) return 1;
	if( b[2] - a[2] > epsilon ) return -1;
	if( a[1] - b[1] > epsilon ) return 1;
	if( b[1] - a[1] > epsilon ) return -1;
	if( a[0] - b[0] > epsilon ) return 1;
	if( b[0] - a[0] > epsilon ) return -1;
	return 0;
}

void copy3d( float * out, const float * in )
{
	out[0] = in[0];
	out[1] = in[1];
	out[2] = in[2];
}

