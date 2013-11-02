#ifndef _CentS_H
#define _CentS_H


#include <stdint.h>
#include "../util/os_generic.h"
#include <sys/types.h>
#include <netinet/in.h>

#include "chash.h"

//Amount of time to sleep after sending packets.
#define CPAUSETIME 1000

#define MAX_OUT_BUFFER 512

#define MAX_CLIENTS 64
#define MAX_EVENTS 8192

struct CentServer;
struct CentConnection;
struct CentCallbackList;


#define CENTFLAGS_OK     0x80
#define CENTFLAGS_EVENT  0x40

#define CENTCODES_FLOATS 1

struct Cent
{
	uint8_t flags;
	uint8_t code;
	uint16_t size; //This size has the qualified name and header taken back out.  Size of /data/ only.
	char * name;
	void * data;
	double lastChange;
};

typedef void (*CentCallback)( struct CentConnection * s, struct Cent * tn, void * id );

struct CentMatchCallback
{
	CentCallback cb;
	const char * match;
	struct CentMatchCallback * next;
	void * id;
};

struct CentCallbackList
{
	struct CentCallbackList * next;
	CentCallback cb;
	void * id;
};


struct CentConnection
{
	int connectedA;
	int connectedB;
	int socket;

	struct sockaddr_in addr;
	struct CentServer * parent;
	og_sema_t   okforrecvtoshutdown;
	og_thread_t sendthread;
	og_thread_t recvthread;

	uint32_t event_tail;

	//ONLY USED IN CLIENT-ONLY MODE!!!
	uint32_t event_head;
	og_sema_t   eventsema;  //Consumers need not lock.
	struct Cent * Events[MAX_EVENTS];

	//Ok, continue normal operation

	//Addy/port not yet filled in.
	const char * addy;
	int port;

	struct chash * LastValues; //(double*)Timestamps for all values only. (When part of a server)

	//For clients primarily.
	struct CentMatchCallback * firstcb;
};

struct CentServer
{
	int socket;
	const char * addy;
	int is_running;
	int port;

	struct sockaddr_in addr;

	og_thread_t thread;
	struct CentConnection clients[MAX_CLIENTS];

	//EVENTS
	uint32_t event_head;
	og_sema_t   eventsema;  //Consumers need not lock.
	struct Cent * Events[MAX_EVENTS];

	og_sema_t   valuesema;  //Consumers and producers both need to lock.
	struct chash * AllValues;

	//Callback
	struct CentMatchCallback * firstcb;
};

struct CentServer * StartCentServer( const char * addy, int port );
void CentServerAddCB( struct CentServer * server, unsigned char * filter, CentCallback cb, void * id );
void CentStop( struct CentServer * conn );
//Change value will replace the old with this.  It will copy it, too.
void ChangeValue( struct CentServer * conn, struct Cent * c, int dontneedtocopy );
void SendEvent( struct CentServer * conn, struct Cent * c, int dontneedtocopy );

//Todo: Add utility to close connection (and clean it up better)
struct CentConnection * CentConnect( const char * addy, int port );
void CentClientAddCB( struct CentConnection * conn, unsigned char * filter, CentCallback cb, void * id );
void SendEventClient( struct CentConnection * conn, struct Cent * c, int dontneedtocopy );

struct Cent * CreateCent( const char * name, uint8_t flags, uint8_t code, uint16_t size, void * data );



//Unusual utility function
void * CentGetDataFromCent( struct Cent * ci );


//More internal tools here

void FreeCent( struct Cent * c );
void FreeCentInPlace( struct Cent * c ); //Don't actually FREE it.
struct Cent * DupCent( struct Cent * c );
void DupCentInPlace( struct Cent * dest, struct Cent * c ); //Does not check to see if dest has anything in it.  Just plougs it.

//Match wildcard strings, i.e. match = "/*/test" check = "/abc/test"
int CentMatch( const char * match, const char * check );



#endif

