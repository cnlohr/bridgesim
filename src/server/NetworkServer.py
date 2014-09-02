from Client import Client, ClientUpdater
import threading
import socket
import os

class NetworkServer:
    def __init__(self, config, universe):
        self.ipmode = 4
        self.host = '::' if self.ipmode == 6 else '0.0.0.0'
        self.port = 8553
        self.__dict__.update(config)
        self.universe = universe
        self.store = SharedClientDataStore()
        self.clients = []

    def run(self):
        try:
            serversocket = socket.socket(socket.AF_INET6 if self.ipmode == 6 else socket.AF_INET, socket.SOCK_STREAM)
            serversocket.bind((self.host, self.port))
            serversocket.listen(0)
        except:
            print("Networking failed.")
            os._exit(1)

        while True:
            connection, address = serversocket.accept()
            client = Client(self, address, SocketNetworker(connection))

            self.clients.append(client)

            updater = ClientUpdater(self.universe, client)

            threading.Thread(target=client.sender.listen, daemon=True).start()

            self.universe.updaters.append(updater)

    def start(self):
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
