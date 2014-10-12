#!/usr/bin/env python
# Echo client program
import threading
import socket
import sys
import time
from RemoteFunctionCaller import *
from SocketNetworker import SocketNetworker
from UpdateReceiver import UpdateReceiver
from ws4py.client.threadedclient import WebSocketClient

HOST = 'localhost'    # The remote host
PORT = 9000           # The same port as used by the server
PATH = '/client'

class Client(WebSocketClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.listeners = []

    def listen(self):
        return

    def closed(self, code, reason=None):
        print("Closed down", code, reason)

    def received_message(self, m):
        print(">>", m.data)
        for i in self.listeners:
            i(m.data)

    def send(self, data):
        print("<<", data)

nw = Client('ws://'+HOST+":"+str(PORT)+PATH)
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
