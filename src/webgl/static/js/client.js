function SocketWrapper(socket) {
    this.socket = socket;
    this.onOpens = [];
    this.onMessages = [];
    this.onErrors = [];
    this.onCloses = [];
    var wrap = this; // wat.

    socket.onopen = function(evt) {
	// APPARENTLY, this is now socket.this
	for (var l in wrap.onOpens.slice(0)) {
	    wrap.onOpens[l](evt);
	}
    }

    socket.onmessage = function(evt) {
	console.log("Receiving: ", evt.data);
	for (var l in wrap.onMessages.slice(0)) {
	    // Might need to do atob() here?
	    wrap.onMessages[l](JSON.parse(evt.data));
	}
    }

    socket.onerror = function(evt) {
	for (var l in wrap.onErrors.slice(0)) {
	    wrap.onErrors[l](evt);
	}
    }

    socket.onclose = function(evt) {
	for (var l in wrap.onCloses.slice(0)) {
	    wrap.onCloses[l](evt);
	}
    }
}

SocketWrapper.prototype.addOnOpen = function(cb) {
    this.onOpens.push(cb);
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
    // FIXME maybe need btoa here?
    console.log("Sending: ", data);
    this.socket.send(JSON.stringify(data));
}

function RemoteFunction(socket, seq, name, callback, timeoutCallback) {
    this.socket = socket;
    this.seq = seq;
    this.name = name;
    this.timer = null;
    this.callback = callback;
    this.timeoutCallback = timeoutCallback;
    this.completed = false;
    this.boundMethod = null;
}

RemoteFunction.prototype.listener = function(data) {
    try {
	if (data && "seq" in data) {
	    if (data.seq == this.seq) {
		clearTimeout(this.timer);
		this.complete = true;
		this.callback(data);

		// if we leave this around we get exponential calls, oops
		var ourIndex = this.socket.onMessages.indexOf(this.boundMethod);
		delete this.socket.onMessages[ourIndex];
	    }
	}
    } catch (e) {
	console.log("Data is", data);
	console.log(e);
    }
};

RemoteFunction.prototype.call = function(context, kwargs) {
    if (!kwargs) kwargs = {};
    var data = {
	"seq": this.seq,
	"op": this.name,
	"args": Array.prototype.slice.call(arguments, 2),
	"kwargs": kwargs,
	"context": context
    };

    // javascript is stupid
    var theese = this;

    this.boundMethod = function(data){theese.listener(data);};
    this.socket.addOnMessage(this.boundMethod);

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
	    window.client.call("SharedClientDataStore__set", ["GlobalContext"], function(res) {
		this.id = res;
	    }, {"key": "testVal", "value": "success"});
	});
    },
    call: function(name, context, callback, kwargs) {
	var tmpSeq = ++this.seq;
	var rf = new RemoteFunction(this.socket, tmpSeq, name, callback, null);
	var newArgs = [context, kwargs].concat(Array.prototype.slice.call(arguments, 4));
	rf.call.apply(rf, newArgs);
    }
}

$(function() {
    window.client.init(new SocketWrapper(new WebSocket("ws://" + location.hostname + ":9000/client")));

    window.client.socket.addOnOpen(function(evt) { console.log("WebSocket is open!"); registerWithServer();});
    //window.client.socket.addOnMessage(function(data) { console.log(data); });

    $("#test-btn").click(function() {
	window.client.call("SharedClientDataStore__set", ["GlobalContext"], function(res) {
	    $("#result-text").val(res.result[0] ? ("OK: " + res.result[1]) : "Failed");
	}, {}, "shipName", prompt("Ship Name"));
    });

    $("#update-enable").change(function() {
	window.client.call("ClientUpdater__requestUpdates", ["ClientUpdater", 0], function(res) {}, {}, "entity", this.checked ? $("#update-freq").val() : 0);
    });
    $("#update-freq").change(function() {
	if ($("#update-enable").prop("checked")) {
	    window.client.call("ClientUpdater__requestUpdates", ["ClientUpdater", 0], function(res) {}, {}, "entity", $(this).val());
	}
    });
});

function registerWithServer() {
    //window.client.socket.send({"message": "Hello, socket!"});
    $("#center-btn").click(function(){window.client.call("whoami", null, function(res) {console.log("You are " + res.seq);});}, {});
    window.client.call("SharedClientDataStore__get", ["GlobalContext"], function(res) {
	$("#result-text").val("From server: " + res.result);
    }, {}, "shipName");
}
