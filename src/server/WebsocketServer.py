from Client import Client, ClientUpdater
from SocketNetworker import SocketNetworker
import threading
import socket
import physics
import os
import json

import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket

cherrypy.config.update( {
	'server.socket_port': 9000,
	'server.socket_host':'0.0.0.0',
})
WebSocketPlugin(cherrypy.engine).subscribe()
cherrypy.tools.websocket = WebSocketTool()

class Root():
    @cherrypy.expose
    def index(self):
        return 'some HTML with a websocket javascript connection'

    @cherrypy.expose
    def client(self):
        # you can access the class instance through
        handler = cherrypy.request.ws_handler

class VectorEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, physics.Vector):
            return list(obj.dimensions)
        return json.JSONEncoder.default(self, obj)

class ClientHandler(WebSocket):
    clients = {}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.listeners = []
        self.listening = False
        print("Client connected!")
        self.client = Client(self.api, None, self, self)
        self.client.id = len(ClientHandler.clients)
        ClientHandler.clients[self.client.id] = self.client
        updater = ClientUpdater(self.universe, self.client)
        self.universe.updaters.append(updater)

    def opened(self):
        print("Test send")

    def send(self, data):
        try:
            encodeddata = json.dumps(data, cls=VectorEncoder, separators=(',',':')).encode('UTF-8')
            super().send(encodeddata)
        except:
            print("Send Failed")

    def received_message(self, message):
        try:
            print(">>>", message.data)
            self.send(str({"id": self.client.id}))
            print(self.listeners)
            for i in self.listeners:
                print("Handling Message")
                msg = json.loads(message.data.decode('UTF-8'))
                if not 'context' in msg:
                    print("Adding context")
                    msg['context'] = ["ClientUpdater", self.client.id]
                i(msg)
        except:
            print("Receive Failed")
 
class NetworkServer:
    def __init__(self, config, universe):
        self.__dict__.update(config)
        self.universe = universe
        ClientHandler.universe = universe
        ClientHandler.store = self.universe.clientDataStore
        self.clients = ClientHandler.clients

    def run(self):
            cherrypy.quickstart(Root(), '/', config={
				'/client': {
					'tools.websocket.on': True,
					'tools.websocket.handler_cls': ClientHandler
				},
				'/': {
					'tools.staticdir.on' : True,
				    'tools.staticdir.dir' : os.path.join( os.getcwd(), 'web/' ),
	    			'tools.staticdir.index' : 'index.html'
				}
			});

    def start(self, api):
        ClientHandler.api = api
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
