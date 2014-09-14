import uuid
import random

ALL_KINDS = (
    "entity",
    "comms",
    "weapons",
    "engineer",
    "helm",
    "ship",
    "meta",
    "universe"
)

class Client:
    def __init__(self, api, address, server, sender):
        self.updates = {}
        self.sender = sender
        self.address = address
        self.server = server
        self.api = api
        self.sender.listeners.append(self.dataReceived)

#        <op name>: {
#            "function": <function pointer>,
#            "args": <predefined arguments list>,
#            "kwargs": <predefined kwargs dictionary>
#        }

    def dataReceived(self, data):
        print("Got data:",data)
        if data and "op" in data:
            if "seq" in data:
                clsName, funcName = data["op"].split('__', 2)
                info = api.classes[clsName]
                if funcName in info["methods"]:
                    func = info["methods"][funcName]
                    args = data.get("args", [])
                    kwargs = data.get("kwargs", {})

                elif funcName in info["writable"] and len(data["args"]) == 1:
                    pass

                elif funcName in info["readable"] and len(data["args"]) == 0:
                    pass

                try:
                    print("Calling",func.__name__,"(", args, kwargs, ")")
                    result = func(*args, **kwargs)
                    print("Sending result")
                    self.sender.send({"result": result, "seq": data["seq"]})
                except Exception as e:
                    print(e)
                    self.sender.send({"result": None, "error": e, "seq": data["seq"]})
            else:
                print("Warning: received command without seq")
        else:
            print("Warning: received invalid op", data["op"])

    def queueUpdate(self, kind, data):
        if kind not in self.updates:
            self.updates[kind] = []

        if kind == "entity":
            self.updates[kind].append(
                { "id": data.id,
                  "loc": data.location,
                  "rot": data.rotation,
                  "vel": data.velocity
              })
        # TODO add the remaining kinds of updates

    def destroy(self):
        self.sender.close()
        self.server.clients.remove(self)

    def sendUpdate(self):
        if self.updates:
            self.sender.send(self.updates)
        self.updates = {}

class ClientUpdater:
    def __init__(self, universe, client):
        self.universe = universe
        self.client = client
        self.client.updater = self

        self.ticks = 0

        # {"kind": <frequency>}
        self.clientWants = {}

        # {"kind": <offset>}
        self.offsets = {}

    # Expose to client
    def flulSync(self):
        self.sendUpdates(ALL_KINDS)

    # Expose to client
    def stopUpdates(self, kind):
        self.clientWants[kind] = 0

    # Expose to client
    def requestUpdates(self, kind, frequency):
        self.clientWants[kind] = frequency
        if kind not in self.offsets:
            # We use a random offset to attempt a more
            # steady usage of networking
            self.offsets[kind] = random.randrange(frequency)

    def sendUpdates(self, kinds):
        for kind in kinds:
            if kind == "entity":
                for entity in self.universe.entities:
                    self.client.queueUpdate(kind, entity)
            elif kind == "comms":
                pass
            elif kind == "weapons":
                pass
            elif kind == "engineer":
                pass
            elif kind == "helm":
                pass
            elif kind == "ship":
                pass
            elif kind == "meta":
                pass
        self.client.sendUpdate()

    def tick(self):
        toUpdate = []
        for kind in self.clientWants:
            if self.clientWants[kind] > 0 and self.ticks % self.clientWants[kind] == self.offsets[kind]:
                toUpdate.append(kind)

        self.sendUpdates(toUpdate)

        self.ticks += 1
