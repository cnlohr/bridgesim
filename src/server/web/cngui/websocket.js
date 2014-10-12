var wsRunning = 0;
var wsUri = "ws://" +location.hostname+ ":9000/client";
var wsInitString = '{"args": ["entity", 1000], "kwargs": {}, "op": "ClientUpdater__requestUpdates", "seq": 1 }'
var wsSocket;
var wsWasInit = 0;
var wsLastUpdateTime = 0;  //in ms
var wsDictionary;
//NOTE: If you receive "updates":"true" then that has to do with the general state that should be added here.

function InternalStartwsSocket( )
{
	if( wsSocket )
		wsSocket.close();
	wsSocket = new WebSocket(wsUri);
	wsSocket.onopen = function(evt) { onOpen(evt) };
	wsSocket.onclose = function(evt) { onClose(evt) };
	wsSocket.onmessage = function(evt) { onMessage(evt) };
	wsSocket.onerror = function(evt) { onError(evt) };
}

function StartWebSocket()
{
	if( wsWasInit == 0 )	
	{
		setTimeout( "InternalStartwsSocket( )", 10 );
		wsWasInit = 1;
	}
}


function onOpen(evt)
{
//	doSend('{}' );
	console.log( "Starting wsSocket interface:" + wsUri + " " + wsInitString );
	wsRunning = 1;
	doSend( wsInitString );
}

function onClose(evt)
{
	wsRunning = 0;
	StartWebSocket();
}

function onMessage(evt)
{
	obj = JSON.parse(evt.data);
	wsLastUpdateTime = new Date().getTime();
	wsDictionary = obj;
	WSUpdate();
}

function onError(evt)
{
	wsRunning = 0;
	StartWebSocket();
}

function doSend(message)
{
	wsSocket.send(message);
}

