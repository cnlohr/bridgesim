from Client import Client, ClientUpdater
from SocketNetworker import SocketNetworker
import threading
import socket
import os

import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket

cherrypy.config.update({'server.socket_port': 9000, 'server.socket_host':'0.0.0.0'})
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


class ClientHandler(WebSocket):
    clients = {}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.listeners = []
        print("Client connected!")
        self.client = Client(self.api, None, self, SocketNetworker(self))
        self.client.id = len(ClientHandler.clients)
        ClientHandler.clients[self.client.id] = self.client
        updater = ClientUpdater(self.universe, self.client)
        self.universe.updaters.append(updater)

    def opened(self):
        print("Test send")

    def received_message(self, message):
        print(">>>", message)
        self.send(str({"id": self.client.id}))
        for i in self.listeners:
            i(message)
 
class NetworkServer:
    def __init__(self, config, universe):
        self.port = 9000
        self.__dict__.update(config)
        self.universe = universe
        ClientHandler.universe = universe
        ClientHandler.store = self.universe.clientDataStore
        self.clients = ClientHandler.clients

    def run(self):
            cherrypy.quickstart(Root(), '/', config={'/client': {'tools.websocket.on': True,
                                                     'tools.websocket.handler_cls': ClientHandler}})

    def start(self, api):
        ClientHandler.api = api
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
