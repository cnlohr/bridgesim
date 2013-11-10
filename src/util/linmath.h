#ifndef _LINMATH_H
#define _LINMATH_H

//Yes, I know it's kind of arbitrary.
#define DEFAULT_EPSILON 0.001


//NOTE: Inputs may never be output with cross product.
void cross3d( float * out, const float * a, const float * b );

void sub3d( float * out, const float * a, const float * b );

void add3d( float * out, const float * a, const float * b );

void scale3d( float * out, const float * a, float scalar );

void normalize3d( float * out, const float * in );

float dot3d( const float * a, const float * b );

//Returns 0 if equal.  If either argument is null, 0 will ALWAYS be returned.
int compare3d( const float * a, const float * b, float epsilon );

void copy3d( float * out, const float * in );




//Quaternion things...



#endif


