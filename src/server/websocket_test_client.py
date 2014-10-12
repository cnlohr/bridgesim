#!/usr/bin/env python
import threading
import socket
import sys
import time
import json
from RemoteFunctionCaller import *
from SocketNetworker import SocketNetworker
from UpdateReceiver import UpdateReceiver
from ws4py.client import WebSocketBaseClient

HOST = '192.168.43.29'    # The remote host
PORT = 9000           # The same port as used by the server
PATH = '/client'

class VectorEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, physics.Vector):
            return list(obj.dimensions)
        return json.JSONEncoder.default(self, obj)

class Client(WebSocketBaseClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.listeners = []
    def handshake_ok(self):
        pass
    def listen(self):
        return
    def closed(self, code, reason=None):
        print("Closed down", code, reason)
    def received_message(self, m):
        print(">>", m.data)
        msg = json.loads(message.data.decode('UTF-8'))
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
receiver = UpdateReceiver(nw)

threading.Thread(target=nw.listen, daemon=True).start()

try:
    print(caller.SharedClientDataStore__set("test", "success"))

    print(caller.SharedClientDataStore__get("test", default="failish"))

    ourCtx = ("ClientUpdater", 0)
    print(caller.ClientUpdater__requestUpdates("entity", 30, context=ourCtx))

    print("What should we call our ship?")
    print(caller.Ship__name(input(), context=("Ship", 0, 0)))
    print(caller.Ship__name(context=("Ship", 0, 1)))

    print("Enabling shields!")
    print(caller.ShieldGenerator__enable(context=("Component", 0, 0, 3)))

    print("Press enter to make ship go boom . . .")
    input()
    print(caller.WeaponsStation__fire(context=("Component", 0, 0, 2)))
    time.sleep(6)
except TimeoutError:
    print("Timed out.")
finally:
    nw.close()
