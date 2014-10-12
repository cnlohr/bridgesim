#!/usr/bin/env python
import time
import json
import threading
from RemoteFunctionCaller import *
from ws4py.client import WebSocketBaseClient
from ws4py.client.threadedclient import WebSocketClient

HOST = '192.168.43.29'    # The remote host
PORT = 9000           # The same port as used by the server
PATH = '/client'

class VectorEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, physics.Vector):
            return list(obj.dimensions)
        return json.JSONEncoder.default(self, obj)

class Client(WebSocketClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.listeners = []
        self.daemon = True
    def listen(self):
        return
    def closed(self, code, reason=None):
        print("Closed down", code, reason)
    def received_message(self, m):
        print(">>", m)
        msg = json.loads(m.data.decode('UTF-8'))
        for i in self.listeners:
            i(msg)
    def send(self, data):
        print("<<", data)
        encodeddata = json.dumps(data, cls=VectorEncoder, separators=(',',':')).encode('UTF-8')
        super().send(encodeddata)

fullpath = 'ws://'+HOST+":"+str(PORT)+PATH
print("Connecting to ", fullpath)
nw = Client(fullpath, protocols=['http-only', 'chat'])
nw.connect()
caller = RemoteFunctionCaller(nw)

ourCtx = ("ClientUpdater", 0)
print(caller.ClientUpdater__requestUpdates("entity", 10, context=ourCtx))

print(caller.SharedClientDataStore__set("test", "success"))
print(caller.SharedClientDataStore__get("test", default="failish"))

print("What should we call our ship?")
print(caller.Ship__name(input(), context=("Ship", 0, 0)))
print(caller.Ship__name(context=("Ship", 0, 1)))

print("Enabling shields!")
print(caller.ShieldGenerator__enable(context=("Component", 0, 0, 3)))

print("Press enter to make ship go boom . . .")
input()
print(caller.WeaponsStation__fire(context=("Component", 0, 0, 2)))

time.sleep(6)

nw.close()
