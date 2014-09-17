#!/usr/bin/env python
# Echo client program
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

try:
    caller.setData("test", "success")
    print(caller.getData("test", default="failish"))
except TimeoutError:
    print("Timed out.")

nw.close()
