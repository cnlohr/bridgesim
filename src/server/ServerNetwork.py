from lock import Lock
import socket
import json
import time

class SharedClientDataStore:
    def __init__(self):
        self.__data = {}
        self.readonly = []
        self.lock = Lock()

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

    def send(self, data):
        out = json.dump(data).encode('UTF-8')
        self.socket.sendall(out)

    def listen(self):
        while True:
            data = self.receive()
            if data:
                for listener in self.listeners:
                    listener(data)
            else:
                time.sleep(10)

    def receive(self):
        while True:
            buf = self.socket.recv(4096)
            if len(buf) <= 0:
                time.sleep(10)
            else:
                self.received += buf
                try:
                    result = json.loads(received.decode('UTF-8'))
                    self.received = bytearray()
                    return result
                except: # TODO we really should handle errors here
                    continue()
                return result

class NetworkServer:
    def __init__(self, config, universe):
        self.ipmode = 4
        self.host = '::' if self.ipmode == 6 else '0.0.0.0'
        self.port = 8553
        self.__dict__.update(config)
        self.universe = universe
        self.store = SharedClientDataStore()
        self.clients = {}

    def run(self):
        serversocket = socket.socket(socket.AF_INET6 if self.ipmode == 6 else socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind((self.host, self.port))
        serversocket.listen()

        while True:
            connection, address = serversocket.accept()

            client = Client(SocketNetworker(connection))

            self.clients[address] = client
            self.universe.updaters.append(ClientUpdater(self.universe, client))

    def start(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
