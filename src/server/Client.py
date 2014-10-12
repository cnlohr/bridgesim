import uuid
import random
from ClientAPI import BaseContext, expose

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
        self.maxage = 30
        self.sender.listeners.append(self.dataReceived)

#        <op name>: {
#            "function": <function pointer>,
#            "args": <predefined arguments list>,
#            "kwargs": <predefined kwargs dictionary>
#        }

    def dataReceived(self, data):
        if data and "op" in data:
            if "seq" in data:
                clsName, funcName = data["op"].split('__', 2)
                info = self.api.classes[clsName]
                context = data.get("context", ())
                args = data.get("args", [])
                kwargs = data.get("kwargs", {})

                # handle method calls
                if funcName in info["methods"]:
                    try:
                        result = self.api.onCall(clsName + "." + funcName,
                                                 context, *args, **kwargs)
                        rDict = {"result": None, "seq": data["seq"]}
                        rDict.update(result)
                        self.sender.send(rDict)
                    except Exception as e:
                        print(e)
                        self.sender.send({"result": None, "error": e, "seq": data["seq"]})

                # handle setting properties
                elif funcName in info["writable"] and len(data["args"]) == 1:
                    try:
                        result = self.api.onSet(clsName + "." + funcName,
                                                context, *args)
                        rDict = {"result": None, "seq": data["seq"]}
                        rDict.update(result)
                        self.sender.send(rDict)
                    except Exception as e:
                        print(e)
                        self.sender.send({"result": None, "error": e, "seq": data["seq"]})
                    print("Client tried to set {} to {} in class {} -- IMPLEMENT ME".format(
                        funcName, data["args"][0], clsName))

                # handle getting properties
                elif funcName in info["readable"] and len(data["args"]) == 0:
                    try:
                        result = self.api.onGet(clsName + "." + funcName,
                                                 context, *args, **kwargs)
                        rDict = {"result": None, "seq": data["seq"]}
                        rDict.update(result)
                        self.sender.send(rDict)
                    except Exception as e:
                        print(e)
                        self.sender.send({"result": None, "error": e, "seq": data["seq"]})
                    print("Client tried to get {} of class {} -- IMPLEMENT ME".format(funcName, clsName))
                # unavailable function?
                else:
                    print("Client tried to do {}.{}. Returning error.")
                    self.sender.send({"result": None, "error": "Operation not found", "seq": data["seq"]})
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
                  "vel": data.velocity,
                  "events": [x.__str__() for x in data.events if x.age() < self.maxage]
              })
        # TODO add the remaining kinds of updates

    def destroy(self):
        self.sender.close()
        del self.server.clients[self.id]

    def sendUpdate(self):
        if self.updates:
            self.updates['updates'] = True
            self.sender.send(self.updates)
        self.updates = {}

class ClientUpdater:
    class Context(BaseContext):
        def __init__(self, instance=None, serial=None):
            if instance:
                self.client = instance.client.id
            elif serial:
                _, self.client = serial
            else:
                raise Exception("Context must be given instance or serial")

        def instance(self, global_context):
            return global_context.network.clients[self.client].updater

        def serialize(self):
            return ("ClientUpdater", self.client)

    def __init__(self, universe, client):
        self.universe = universe
        self.client = client
        self.client.updater = self

        self.ticks = 0

        # {"kind": <frequency>}
        self.clientWants = {}

        # {"kind": <offset>}
        self.offsets = {}

    @expose
    def fullSync(self):
        self.sendUpdates(ALL_KINDS)

    @expose
    def stopUpdates(self, kind):
        self.clientWants[kind] = 0

    @expose
    def requestUpdates(self, kind, frequency):
        self.clientWants[kind] = frequency
        if kind not in self.offsets:
            # We use a random offset to attempt a more
            # steady usage of networking
            self.offsets[kind] = random.randrange(frequency)

    def sendUpdates(self, kinds):
        for kind in kinds:
            if kind == "entity":
                for entity in self.universe.entities.values():
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
