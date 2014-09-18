import time

class TimeoutError(Exception):
    pass

class RemoteError(Exception):
    pass

class RemoteFunction:
    def __init__(self, sender, seq, name, timeout=5, timeoutCb = None):
        self.sender = sender
        self.seq = seq
        self.name = name
        self.timeout = timeout
        self.timeoutCb = timeoutCb
        self.result = None

    def __call__(self, *args, context=None, **kwargs):
        obj = {
            "seq": self.seq,
            "op": self.name,
            "args": args,
            "kwargs": kwargs,
            "context": context
        }

        self.sender.send(obj)

        start = time.time()
        while True:
            if self.result:
                if "error" in self.result:
                    raise RemoteError(self.result["error"])
                else:
                    return self.result["result"]
            if time.time() - start >= self.timeout:
                if self.timeoutCb:
                    self.timeoutCb(self.seq)
                raise TimeoutError
            time.sleep(.005)

class RemoteFunctionCaller:
    def __init__(self, sender, timeout=5):
        self.sender = sender
        self.sender.listeners.append(self.dataReceived)

        self.timeout = timeout
        self.seqnum = 0
        self.calls = {}

    def functionTimeout(self, seq):
        if seq in self.calls:
            del self.calls[seq]

    def __getattr__(self, name):
        # Need to lock on seqnum if used by multiple threads
        self.seqnum += 1
        rf = RemoteFunction(self.sender, self.seqnum, name,
                            timeout=self.timeout, timeoutCb=self.functionTimeout)
        self.calls[self.seqnum] = rf
        return rf

    def dataReceived(self, data):
        print("Got data", data)
        if "seq" in data:
            if data["seq"] in self.calls:
                self.calls[data["seq"]].result = data
                del data["seq"]

    def destroy(self):
        self.sender.close()
