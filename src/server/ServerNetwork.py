from ClientUpdater import Client, ClientUpdater
import threading
import socket
import json
import time
import os
import physics

class VectorEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, physics.Vector):
            return list(obj.dimensions)
        return json.JSONEncoder.default(self, obj)

class SharedClientDataStore:
    def __init__(self):
        self.__data = {}
        self.readonly = []
        self.lock = threading.Lock()

    def get(self, key, default=None):
        with self.lock:
            if key in self.__data:
                return self.__data[key]
            else:
                return default

    def getAndStoreIfNew(self, key, default, ro=False):
        val = self.get(key, default)
        with self.lock:
            if key not in self.__data:
                self.__data[key] = val
                if ro:
                    self.readonly.append(key)
        return val

    def set(self, key, value, ro=False):
        if key not in self.readonly:
            with self.lock:
                self.__data[key] = value
                if ro:
                    self.readonly.append(key)
                return True
        return False

    def setIfMissing(self, key, value, ro=False):
        with self.lock:
            if key not in self.__data:
                self.__data[key] = value

                if ro:
                    self.readonly.append(key)
                return True
        return False

class SocketNetworker:
    def __init__(self, socket):
        self.socket = socket
        self.received = bytearray()
        self.listeners = []
        self.running = False

    def send(self, data):
        try:
            out = json.dumps(data, cls=VectorEncoder, separators=(',',':')).encode('UTF-8')
            self.socket.sendall(out)
            return True
        except Exception as e:
            print("Error in send!!!", e)
            self.running = False
            raise e
        return False

    def listen(self):
        self.running = True
        while self.running:
            data = self.receive()
            if data:
                for listener in self.listeners:
                    listener(data)
            else:
                time.sleep(10)

    def receive(self):
        while self.running:
            buf = None
            try:
                buf = self.socket.recv(4096)
            except Exception as e:
                self.running = False
                print("Error in receive!!!", e)
                raise e
            if len(buf) <= 0:
                time.sleep(10)
            else:
                self.received += buf
                try:
                    result = json.loads(received.decode('UTF-8'))
                    self.received = bytearray()
                    return result
                except: # TODO we really should handle errors here
                    continue
                return result
        return None

    def close(self):
        self.running = False
        self.socket.close()

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
            updater.requestUpdates("entity", 5)

            threading.Thread(target=client.sender.listen, daemon=True).start()

            self.universe.updaters.append(updater)

    def start(self):
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
