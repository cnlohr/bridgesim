#!/usr/bin/env python
# Echo client program
import threading
import socket
import sys
from RemoteFunctionCaller import *
from SocketNetworker import SocketNetworker

HOST = 'localhost'    # The remote host
PORT = 8553           # The same port as used by the server
s = None
for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res
    try:
        s = socket.socket(af, socktype, proto)
    except OSError as msg:
        s = None
        continue
    try:
        s.connect(sa)
    except OSError as msg:
        s.close()
        s = None
        continue
    break
if s is None:
    print('could not open socket')
    sys.exit(1)

nw = SocketNetworker(s)
caller = RemoteFunctionCaller(nw)

threading.Thread(target=nw.listen, daemon=True).start()

try:
    print(caller.SharedClientDataStore__set("test", "success"))
    print(caller.SharedClientDataStore__get("test", default="failish"))

    print("What should we call the victim?",)
    print(caller.Ship__name(input(), context=("Ship", 0, 1)))
    print(caller.Ship__name(context=("Ship", 0, 1)))

    print(caller.ShieldGenerator__enable(context=("Component", 0, 1, 3)))

    print("Press enter to make ship go boom . . .")
    input()
    print(caller.WeaponsStation__fire(context=("Component", 0, 0, 2)))
except TimeoutError:
    print("Timed out.")

nw.close()
