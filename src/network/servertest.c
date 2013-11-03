#include "cent.h"
#include <stdio.h>
#include <stdlib.h>
#include "os_generic.h"

struct CentServer * sv;

void MyServerCentCB( struct CentConnection * s, struct Cent * tn, void * id )
{
	printf( "Server: %s %p\n", tn->name, id );
}


void * CentServerThread( void *  v)
{
	int i = 0, q = 0;
	sv = StartCentServer( "0.0.0.0", 8553 );

	CentServerAddCB( sv, "*", MyServerCentCB, 0 );
	printf( "Server: %p\n", sv );
	while(1)
	{
		char stn[64];
		sprintf( stn, "/%d/mark", i++ );

		uint32_t * fvs = malloc( 8 );
		fvs[0] = 5;
		fvs[1] = 6;

		uint32_t * fvs2 = malloc( 8 );
		fvs2[0] = 5;
		fvs2[1] = q++;

		struct Cent * c;


		c = CreateCent( stn, CENTFLAGS_OK|CENTFLAGS_EVENT, CENTCODES_FLOATS, 8, (void*)fvs );
		SendEvent( sv, c, 1 );
		
		c = CreateCent( "/hi", CENTFLAGS_OK, CENTCODES_FLOATS, 8, (void*)fvs2 );
		ChangeValue( sv, c, 1 );

		OGUSleep(100000);
	}
}

void MyClientCentCB( struct CentConnection * s, struct Cent * tn, void * id )
{
	printf( "CLIENT: %s %p\n", tn->name, id );
}


void * CentClientThread( void * v )
{
	struct Cent * c;
	int q;
	struct CentConnection * conn = CentConnect( "127.0.0.1", 8553 );

	CentClientAddCB( conn, "*i", MyClientCentCB, (void*)1 );
	CentClientAddCB( conn, "/*/mark", MyClientCentCB, 0 );

	while(1)
	{
		uint32_t * fvs2 = malloc( 8 );
		fvs2[0] = 5;
		fvs2[1] = q++;
		c = CreateCent( "/fromclient", CENTFLAGS_OK, CENTCODES_FLOATS, 8, (void*)fvs2 );
		SendEventClient( conn, c, 1 );

		OGUSleep(250000);
	}
}


int main()
{
	int i;
	og_thread_t server;
	og_thread_t client;

	server = OGCreateThread( CentServerThread, 0 );
	OGSleep(1);
	client = OGCreateThread( CentClientThread, 0 );

	for( i = 0; i < 10; i++ )
	{
		OGSleep(1);
	}

	CentStop( sv );

}

