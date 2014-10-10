function SocketWrapper(socket) {
    this.socket = socket;
    this.onOpens = [];
    this.onMessages = [];
    this.onErrors = [];
    this.onCloses = [];
    var wrap = this; // wat.

    socket.onopen = function(evt) {
	// APPARENTLY, this is now socket.this
	for (var l in wrap.onOpens) {
	    wrap.onOpens[l](evt);
	}
    }

    socket.onmessage = function(evt) {
	for (var l in wrap.onMessages) {
	    wrap.onMessages[l](JSON.parse(atob(evt.data)));
	}
    }

    socket.onerror = function(evt) {
	for (var l in wrap.onErrors) {
	    wrap.onErrors[l](evt);
	}
    }

    socket.onclose = function(evt) {
	for (var l in wrap.onCloses) {
	    wrap.onCloses[l](evt);
	}
    }
}

SocketWrapper.prototype.addOnOpen = function(cb) {
    console.log("Adding an onOpen...");
    this.onOpens.push(cb);
    console.log("Added! (" + this.onOpens.length + ")");
}

SocketWrapper.prototype.addOnMessage = function(cb) {
    this.onMessages.push(cb);
}

SocketWrapper.prototype.addOnError = function(cb) {
    this.onErrors.push(cb);
}

SocketWrapper.prototype.addOnClose = function(cb) {
    this.onCloses.push(cb);
}

SocketWrapper.prototype.send = function(data) {
    this.socket.send(btoa(JSON.stringify(data)));
}

function RemoteFunction(socket, seq, name, callback, timeoutCallback) {
    this.socket = socket;
    this.seq = seq;
    this.name = name;
    this.timer = null;
    this.callback = callback;
    this.timeoutCallback = timeoutCallback;
    this.completed = false;
}

RemoteFunction.prototype.call = function(context) {
    var data = {
	"seq": this.seq,
	"op": this.name,
	"args": Array.slice(arguments, 1),
	"kwargs": {},
	"context": this.context
    };

    var theese = this;

    this.socket.addOnMessage(function(data) {
	if (data) {
	    console.log("data is:");
	    console.log(data);
	    if ("seq" in data) {
		if (data["seq"] == theese.seq) {
		    clearTimeout(theese.timer);
		    theese.complete = true;
		    theese.callback(data);
		}
	    }
	}
    });
    this.socket.send(data);
    // All functions will have a 5 second timeout I guess
    if (this.callback) {
	this.timer = setTimeout(function() {theese.callback(null);}, 5000);
    } else {
	console.log("this.callback is not anything:");
	console.log(this.callback);
    }
}

window.client = {
    id: null, // This will be updated when connection is successful
    seq: 0,
    socket: null, // This needs to be set before we can initialize
    init: function(socket) {
	this.socket = socket;
	this.socket.addOnOpen(function(evt) {
	    console.log("Socket opened. Now calling whoami...");
	    window.client.call("whoami", null, function(res) {
		this.id = res;
	    });
	});
    },
    call: function(name, context, callback) {
	var tmpSeq = ++this.seq;
	var rf = new RemoteFunction(this.socket, tmpSeq, name, callback, null);
	var newArgs = [context];
	newArgs.concat(Array.slice(arguments, 3));
	rf.call.apply(rf, newArgs);
    }
}

$(function() {
    var wsUri = "ws://echo.websocket.org/";

    window.client.init(new SocketWrapper(new WebSocket("ws://" + location.hostname + ":" + (parseInt(location.port) + 1), ['base64', 'binary'])));

    window.client.socket.addOnOpen(function(evt) { console.log("WebSocket is open!"); registerWithServer();});
    window.client.socket.addOnMessage(function(data) { console.log(data); });
});

function registerWithServer() {
    window.client.socket.send({"message": "Hello, socket!"});
    $("#center-btn").click(function(){window.client.call("whoami", null, function(res) {console.log("You are " + res.seq);});});
}
