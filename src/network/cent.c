#include <arpa/inet.h>
#include "cent.h"
#include "os_generic.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <errno.h>

#define LISTENQ 7

static void GotChange( struct CentConnection * c, struct Cent * val );
static void SendCallbacks( struct CentMatchCallback * cmc, struct CentConnection * c, struct Cent * val );

static int FindFreeClient( struct CentServer * conn )
{
	int i;
	for( i = 0; i < MAX_CLIENTS; i++ )
	{
		if( !conn->clients[i].connectedA && !conn->clients[i].connectedB )
		{
			return i;
		}
	}
	return -1;
}

struct Cent * DupCent( struct Cent * c )
{
	struct Cent * ret = malloc( sizeof( struct Cent ) );
	DupCentInPlace( ret, c );
	return ret;
}

void FreeCent( struct Cent * c )
{
	if( !c ) return;
	FreeCentInPlace( c );
	free( c );
}

void FreeCentInPlace( struct Cent * c )
{
	if( c->name )
		free( c->name );

	if( c->data )
		free( c->data );
}

void DupCentInPlace( struct Cent * dest, struct Cent * c )
{
	dest->flags = c->flags;
	dest->code = c->code;
	dest->size = c->size;
	dest->name = strdup( c->name );
	dest->data = malloc( c->size );
	memcpy( dest->data, c->data, c->size );
	dest->lastChange = c->lastChange;
}



static int TackCentItem( struct Cent * c, uint8_t * buffer, uint16_t maxleft )
{
	int namelen = strlen( c->name );
	int expected_len = c->size + namelen + 1 + 4;

	if( expected_len > maxleft )
	{
		return -1;
	}

	//If it fits, it ships.

	uint16_t actualsize = c->size + namelen + 1;

	buffer[0] = c->flags;
	buffer[1] = c->code;
	buffer[2] = actualsize >> 8;
	buffer[3] = actualsize & 0xff;

	memcpy( &buffer[4], c->name, namelen+1 );
	memcpy( &buffer[4+namelen+1], c->data, c->size );

	return expected_len;
}


void * ServerWorkerThreadSend( void * v )
{
	struct CentConnection * nc = (struct CentConnection *)v;
	struct CentServer * p = nc->parent;
	while( nc->connectedB )
	{
		uint16_t place = 0;
		uint8_t buffer[MAX_OUT_BUFFER];

		//Check events first.

		if( p )
		{
			while( nc->event_tail != p->event_head )
			{
				int rs = TackCentItem( p->Events[nc->event_tail], &buffer[place], MAX_OUT_BUFFER-place-1 );

				if( rs < 0 ) //out of room?
				{
					if( place == 0 )
					{
						fprintf( stderr, "Error: Fault: Event was too large to fit into any messages.\n" );
					}
					else
					{
						goto go_and_send;  //Out of room, just go send and we'll get this one next time 'round.
					}
				}

				place += rs;

				nc->event_tail = (nc->event_tail+1)%MAX_EVENTS;
			}

			//Now, find any dictionary entries that don't match.
			{
				int i;

				OGLockSema( p->valuesema );
				struct chashlist * pl = HashProduceSortedTable( p->AllValues );

				//XXX WARN: This is slow and bad because the semaphore is around too much.

				for( i = 0; i < pl->length; i++ )
				{
					struct chashentry * h = &pl->items[i];
					struct Cent * newval = (struct Cent*)h->value;
					double * oldval = (double*)HashGetEntry( nc->LastValues, h->key );

					if( oldval )
					{
						if( *oldval == newval->lastChange )
						{
							continue;
						}
					}

					if( !oldval )
					{
						void ** vo = HashTableInsert( nc->LastValues, h->key, 0 );

						if( !vo )
						{
							fprintf( stderr, "Error: fault inserting new value flag in ServerWorkerThreadSend.\n" );
							return; 
						}

						oldval = (double*)*vo;

						if( !oldval )
						{
							*vo = oldval = malloc(sizeof(double));
						}
					}

					//Update the entry.
					*oldval = newval->lastChange;

					//Nope!  New change.  Send it.
					int rs = TackCentItem( newval, &buffer[place], MAX_OUT_BUFFER-place-1 );

					if( rs < 0 ) //out of room?
					{
						if( place == 0 )
						{
							fprintf( stderr, "Error: Fault: Event was too large to fit into any messages.\n" );
						}
						else
						{
							OGUnlockSema( p->valuesema );
							goto go_and_send;  //Out of room, just go send and we'll get this one next time 'round.
						}
					}

					place += rs;
				}
				free( pl );
			}
			OGUnlockSema( p->valuesema );
		}
		else
		{
			//We're a stand-alone client.
			while( nc->event_tail != nc->event_head )
			{
				int rs = TackCentItem( nc->Events[nc->event_tail], &buffer[place], MAX_OUT_BUFFER-place-1 );

				if( rs < 0 ) //out of room?
				{
					if( place == 0 )
					{
						fprintf( stderr, "Error: Fault: Event was too large to fit into any messages.\n" );
					}
					else
					{
						goto go_and_send;  //Out of room, just go send and we'll get this one next time 'round.
					}
				}

				place += rs;

				nc->event_tail = (nc->event_tail+1)%MAX_EVENTS;
			}

		}		

		if( place == 0 )
		{
			OGUSleep( CPAUSETIME );
			continue;
		}
go_and_send:
		//Check to send
		if( send( nc->socket, buffer, place, MSG_NOSIGNAL ) <= 0 )
		{
			break;
		}
		OGUSleep( CPAUSETIME );
	}

	close( nc->socket );
	nc->connectedA = 0;
	OGUnlockSema( nc->okforrecvtoshutdown );
}


void * ServerWorkerThreadRecv( void * v )
{
	#define recvbuffersize 65540
	uint8_t buffer[recvbuffersize];
	struct CentConnection * nc = (struct CentConnection *)v;
	ssize_t read;
	int place = 0, i;
	int didtriggerimmediate = 0;

	while( nc->connectedA && ( read = recv( nc->socket, buffer + place, recvbuffersize - place, 0 ) ) > 0 )
	{
		uint8_t flags, code;
		uint16_t size;
		uint32_t end;
keepgoing:

		end = read + place;
		if( end < 5 )
		{
			place += read;
			continue;
		}

		//WARNING: This part of the process is slow.

		flags = buffer[0];
		code  = buffer[1];
		size = ( buffer[2] << 8 ) | buffer[3];
		char * name = (char*)&buffer[4];

		if( size+4 > end )
		{
			place += read;
			continue;
		}

		//We know we have a proper packet now.
		uint32_t slen = strlen( name );

		struct Cent * val = malloc( sizeof( struct Cent ) );
		val->flags = flags;
		val->code = code;
		val->size = size - slen - 1;
		val->name = strdup( name );
		val->data = malloc( val->size );
		memcpy( val->data, &buffer[4+slen+1], val->size );
		val->lastChange = OGGetAbsoluteTime();

		GotChange( nc, val );

		FreeCent( val );

		int endofpack = size+4;

		//Shift the buffer back...
		for( i = 0; i < end-endofpack; i++ )
		{
			buffer[i] = buffer[i+endofpack];
		}
		place -= endofpack;
		goto keepgoing;
	}

	close( nc->socket );

	OGLockSema( nc->okforrecvtoshutdown );

	//Handle cleaning things up.

	struct CentMatchCallback * del = nc->firstcb;
	while( del )
	{
		struct CentMatchCallback * tmp = del->next;
		free( del->match );
		free( del );
		del = tmp;
	}

	HashDestroy( nc->LastValues, 1 );

	//XXX TODO CLEAN UP SOCKET AND MEMORY!!!

	//The receiver handles cleaning up things like subscription lists.

	OGDeleteSema( nc->okforrecvtoshutdown );

	nc->connectedB = 0;
}

void * ServerThread( void * v )
{
	struct CentServer * conn = (struct CentServer*)v;
	int newpos = FindFreeClient( conn );
	int newconn;
	socklen_t slt;

	if( newpos < 0 ) 
	{
		fprintf( stderr, "Fatal error: Cannot find free client slot in new connection.\n" );
		return 0;
	}

	struct CentConnection * nc = &conn->clients[newpos];

	slt = sizeof( nc->addr );

	conn->is_running = 1;

	memset( &nc->addr, 0, slt );
	while( (newconn = accept(conn->socket, (struct sockaddr *) &nc->addr, &slt ) ) > 0 )
	{
		struct linger so_linger;
		int sendbuff;
		int r;

		//Make send(...)s blocking.
		sendbuff = 0;
		r = setsockopt(newconn, SOL_SOCKET, SO_SNDBUF, &sendbuff, sizeof(sendbuff));

		so_linger.l_onoff = 1;
		so_linger.l_linger = 0;
		setsockopt(newconn, SOL_SOCKET, SO_LINGER, &so_linger, sizeof so_linger );

		


		//TODO: Make addy from addr.
		nc->socket = newconn;
		nc->event_tail = conn->event_head;
		nc->connectedA = 1;
		nc->connectedB = 1;
		nc->parent = conn;
		nc->firstcb = 0;
		nc->eventsema = OGCreateSema();
		OGUnlockSema( nc->eventsema );
		nc->event_head = 0;
		nc->LastValues = GenerateHashTable( 0 );
		nc->addy = (const char*)inet_ntoa( nc->addr.sin_addr );
		nc->port = ntohs( nc->addr.sin_port );
		nc->okforrecvtoshutdown = OGCreateSema();
		nc->sendthread = OGCreateThread( ServerWorkerThreadSend, nc );
		nc->recvthread = OGCreateThread( ServerWorkerThreadRecv, nc  );

		newpos = FindFreeClient( conn );
		nc = &conn->clients[newconn];
		memset( &nc->addr, 0, slt );
	}

	fprintf( stderr, "Error: Accept failed (%d) %s.\n", newconn, strerror( errno )  );
	conn->is_running = 0;

	//Connection failed.
	return 0;
}



struct CentServer * StartCentServer( const char * addy, int port )
{
	struct CentServer * ret;
	int sock;
	struct sockaddr_in addr;

	//First make sure we can get a connection.

    memset(&addr, 0, sizeof(addr));
    addr.sin_family      = AF_INET;
    addr.sin_addr.s_addr = inet_addr(addy);
    addr.sin_port        = htons(port);
	//    server = gethostbyname(hostname);


    if( (sock = socket(AF_INET, SOCK_STREAM, 0)) < 0 )
	{
		fprintf(stderr, "Error creating listening socket.\n");
		return 0;
    }

	if( bind(sock, (struct sockaddr *) &addr, sizeof(addr) ) < 0 )
	{
		fprintf(stderr, "Error binding\n");
		return 0;
    }

    if ( listen(sock, LISTENQ) < 0 )
	{
		fprintf(stderr, "Error listening()\n");
		return 0;
	}

	ret = malloc( sizeof( struct CentServer ) );
	memset( ret, 0, sizeof( struct CentServer ) );
	ret->port = port;
	ret->socket = sock;
	ret->addy = addy;
	ret->firstcb = 0;
	ret->event_head = 0;
	ret->eventsema = OGCreateSema();
	OGUnlockSema(ret->eventsema); 
	ret->valuesema = OGCreateSema();
	OGUnlockSema(ret->valuesema);
	ret->AllValues = GenerateHashTable( 0 );
	memset( ret->clients, 0, sizeof( ret->clients ) );
	memcpy( &ret->addr, &addr, sizeof(addr) );

	ret->thread = OGCreateThread( ServerThread, ret );

	struct linger so_linger;
	so_linger.l_onoff = 1;
	so_linger.l_linger = 0;
	setsockopt(sock, SOL_SOCKET, SO_LINGER, &so_linger, sizeof so_linger );

	return ret;
}

struct CentConnection * CentConnect( const char * addy, int port )
{
	struct CentConnection * nc;
	int sock, r;
	struct sockaddr_in addr;

	//First make sure we can get a connection.

    memset(&addr, 0, sizeof(addr));
    addr.sin_family      = AF_INET;
    addr.sin_addr.s_addr = inet_addr(addy);
    addr.sin_port        = htons(port);
	//    server = gethostbyname(hostname);

    if( (sock = socket(AF_INET, SOCK_STREAM, 0)) < 0 )
	{
		fprintf(stderr, "Error creating listening socket.\n");
		return 0;
    }

	if( (r = connect( sock, (struct sockaddr*)&addr, sizeof( addr ) ) ) < 0 )
	{
		fprintf( stderr, "Error: could not connect to server: %d\n", r );
		return 0;
	}

	nc = malloc( sizeof( struct CentConnection ) );
	memset( nc, 0, sizeof( struct CentConnection ) );
	nc->socket = sock;
	nc->event_tail = 0;
	nc->connectedA = 1;
	nc->connectedB = 1;
	nc->parent = 0;
	nc->firstcb = 0;
	nc->eventsema = OGCreateSema();
	OGUnlockSema( nc->eventsema );
	nc->event_head = 0;
	nc->LastValues = GenerateHashTable( 0 );
	nc->addy = strdup( addy );
	nc->port = port;
	nc->okforrecvtoshutdown = OGCreateSema();
	nc->sendthread = OGCreateThread( ServerWorkerThreadSend, nc );
	nc->recvthread = OGCreateThread( ServerWorkerThreadRecv, nc  );

	return nc;
}

void CentStop( struct CentServer * conn )
{
	int i;

	close( conn->socket );

	//thread should automatically clear out.

	//First, stop all connections.
	for( i = 0; i < MAX_CLIENTS; i++ )
	{
		struct CentConnection * nc = &conn->clients[i];
		close( nc->socket );
	}

	OGLockSema( conn->eventsema );
	for( i = 0; i < MAX_EVENTS; i++ )
	{
		if( conn->Events[i] )
			FreeCent( conn->Events[i] );
	}

	HashDestroy( conn->AllValues, 1 );
}






void ChangeValue( struct CentServer * conn, struct Cent * c, int dontneedtocopy )
{
	OGLockSema( conn->valuesema );

	void ** v = HashTableInsert( conn->AllValues,  c->name, 0 );

	if( !v )
	{
		fprintf( stderr, "Error: cannot update value in table root!\n" );
		return;
	}

	struct Cent * cold = (struct Cent *)*v;

	if( cold )
		FreeCent( cold );

	if( dontneedtocopy )
		cold = c;
	else
		cold = DupCent( c );
	*v = (void*)cold;

	OGUnlockSema( conn->valuesema );
}


void SendEvent( struct CentServer * conn, struct Cent * c, int dontneedtocopy )
{
	OGLockSema( conn->eventsema );

	if( conn->Events[conn->event_head] )
		FreeCent( conn->Events[conn->event_head] );

	if( dontneedtocopy )
		conn->Events[conn->event_head] = c;
	else
		conn->Events[conn->event_head] = DupCent( c );

	conn->event_head = (conn->event_head+1)%MAX_EVENTS;

	OGUnlockSema( conn->eventsema );
}

void ClientStop( struct CentConnection * c )
{
	close( c->socket );
}

void SendEventClient( struct CentConnection * conn, struct Cent * c, int dontneedtocopy )
{
	OGLockSema( conn->eventsema );

	if( conn->Events[conn->event_head] )
		FreeCent( conn->Events[conn->event_head] );

	if( dontneedtocopy )
		conn->Events[conn->event_head] = c;
	else
		conn->Events[conn->event_head] = DupCent( c );

	conn->event_head = (conn->event_head+1)%MAX_EVENTS;

	OGUnlockSema( conn->eventsema );
}

struct Cent * CreateCent( const char * name, uint8_t flags, uint8_t code, uint16_t size, void * data )
{
	struct Cent * dest = malloc( sizeof( struct Cent ) );
	dest->flags = flags;
	dest->code = code;
	dest->size = size;
	dest->name = strdup( name );
	dest->data = malloc( size );
	memcpy( dest->data, data, size );
	dest->lastChange = OGGetAbsoluteTime();

	return dest;
}



/////////////////////////////////////////////////////////////////////////////////////////////////////
//Callbacks

int CentMatch( const char * match, const char * check )
{
	//compare the "match"
	//I.e.
	//cmc->match:  /*/hit*
	//matches:     /e/44/hit
	const char * m = match;
	const char * h = check;

	while( *m && *h )
	{
		if( *m == '*' )
		{
			if( *(m+1) == *h )
			{
				m++;
				continue;
			}
			else
			{
				h++;
			}
		}
		else if( *m != *h )
		{
			return 0;
		}
		else //Regular match
		{
			m++;
			h++;
		}
	}

	if( *h == 0 && ( *m == *h || ( *m == '*' && *(m+1) == 0 ) ) )
	{
		return 1;
	}

	return 0;
}

static void SendCallbacks( struct CentMatchCallback * cmc, struct CentConnection * c, struct Cent * val )
{
	while( cmc )
	{
		const char * m = cmc->match;
		const char * h = val->name;
		if( CentMatch( m, h ) )
		{
			cmc->cb( c, val, cmc->id );
		}
		cmc = cmc->next;
	}
}

static void GotChange( struct CentConnection * c, struct Cent * val )
{
	if( c->parent )
		SendCallbacks( c->parent->firstcb, c, val );
	SendCallbacks( c->firstcb, c, val );
} 

void CentServerAddCB( struct CentServer * server, unsigned char * filter, CentCallback cb, void * id )
{
	struct CentMatchCallback * walk, *last;
	struct CentMatchCallback * cmc = malloc( sizeof( struct CentMatchCallback ) );
	cmc->cb = cb;
	cmc->match = strdup( filter );
	cmc->id = id;
	cmc->next = 0;


	if( server->firstcb )
	{
		for( walk = server->firstcb; walk; walk = walk->next ) last = walk;

		last->next = cmc;
	}
	else
	{
		server->firstcb = cmc;
	}
}

void CentClientAddCB( struct CentConnection * conn, unsigned char * filter, CentCallback cb, void * id )
{
	struct CentMatchCallback * walk, *last;
	struct CentMatchCallback * cmc = malloc( sizeof( struct CentMatchCallback ) );
	cmc->cb = cb;
	cmc->match = strdup( filter );
	cmc->id = id;
	cmc->next = 0;

	if( conn->firstcb )
	{
		for( walk = conn->firstcb; walk; walk = walk->next ) last = walk;

		last->next = cmc;
	}
	else
	{
		conn->firstcb = cmc;
	}
}




//Unusual tools


void * CentGetDataFromCent( struct Cent * ci ) { return ci->data; }


