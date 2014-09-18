import json
import time
import physics

class VectorEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, physics.Vector):
            return list(obj.dimensions)
        return json.JSONEncoder.default(self, obj)

class SocketNetworker:
    def __init__(self, socket):
        self.socket = socket
        self.received = bytearray()
        self.listeners = []
        self.running = False

    def send(self, data):
        print("N >>>", data)
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
                print("N <<<", data)
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
                    result = json.loads(self.received.decode('UTF-8'))
                    self.received = bytearray()
                    return result
                except Exception as e: # TODO we really should handle errors here
                    print("Warning: ", e)
                    continue
                return result
        return None

    def close(self):
        self.running = False
        self.socket.close()
