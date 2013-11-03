#include "cent.h"
#include <stdio.h>
#include <stdlib.h>
#include "os_generic.h"

void MyClientCentCB( struct CentConnection * s, struct Cent * tn, void * id )
{
	float * values = (float*)tn->data;
	printf( "CLIENT: %s %p %f %f %f\n", tn->name, id, values[0], values[1], values[2] );
}


void * CentClientThread( void * v )
{
	struct Cent * c;
	int q;
	struct CentConnection * conn = CentConnect( "127.0.0.1", 8553 );

	CentClientAddCB( conn, "sta", MyClientCentCB, (void*)1 );
	CentClientAddCB( conn, "/*/mark", MyClientCentCB, 0 );

	while(1)
	{
		float * fvs2 = malloc( 8 );
		fvs2[0] = 5;
		fvs2[1] = q++;
		c = CreateCent( "/fromclient/test", CENTFLAGS_OK, CENTCODES_FLOATS, 8, (void*)fvs2 );
		SendEventClient( conn, c, 1 );

		OGUSleep(250000);
	}
}


int main()
{
	og_thread_t client;

	client = OGCreateThread( CentClientThread, 0 );

	while(1)
	{
		OGSleep(1);
	}
}

