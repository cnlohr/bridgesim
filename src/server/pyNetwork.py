import struct
import threading
import socket
try:
  import SocketServer
except ImportError:
  import socketserver as SocketServer
import threading

bindIP, bindPort = "localhost", 8553
compatBytes = bytes
try:
  bytes("foo")
except TypeError:
  def compatBytes(string):
    return bytes(string, 'ascii')
  
class MyTCPHandler(SocketServer.BaseRequestHandler):
  def handle(self):
    data = self.request.recv(1024)
    cur_thread = threading.current_thread()
    response = "{}: {}".format(cur_thread.name, data)
    print response
    self.request.sendall(response)
    
class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
  pass

server = SocketServer.TCPServer((bindIP, bindPort), MyTCPHandler)
serverThread = threading.Thread(target=server.serve_forever)
serverThread.daemon = True
serverThread.start()
def update(dataName, dataList):
  packet = compatBytes(dataName)
  packet += compatBytes(0x80)
  packet += compatBytes(1)
  packet += compatBytes(4*len(dataList))
  packet += struct.pack("%df" % len(dataList), *dataList)
  packet += compatBytes(1)
#  print(dir(server))
#  print packet
#  serverThread.sendall(packet)
  
def shutdown():
  server.shutdown()