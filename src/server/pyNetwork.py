import struct
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

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
  def sendall(self, data):
    self.request.sendall(data)
    
class MyTCPHandler(SocketServer.BaseRequestHandler):
  def handle(self):
    self.data = self.request.recv(1024)
    print(self.data)

server = ThreadedTCPServer((bindIP, bindPort), MyTCPHandler)

server_thread = threading.Thread(target=server.serve_forever)
# Exit the server thread when the main thread terminates
server_thread.daemon = True
server_thread.start()

def update(dataName, dataList):
  packet = compatBytes(dataName)+compatBytes(0x80)+compatBytes(1+4*len(dataList))+compatBytes(struct.pack("%df" % len(dataList), *dataList))+compatBytes(1)
  print(dir(server))
  server.sendall(packet)