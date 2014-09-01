import uuid
import random

ALL_KINDS = (
    "entity",
    "comms",
    "weapons",
    "engineer",
    "helm",
    "ship",
    "meta"
)

class Client:
    def __init__(self, server, address, sender):
        self.updates = {}
        self.sender = sender
        self.address = address
        self.server = server
        self.sender.listeners.append(self.clientListener)

    def clientListener(self, data):
        print("Data:", data)

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

        self.ticks = 0

        # {"kind": <frequency>}
        self.clientWants = {}

        # {"kind": <offset>}
        self.offsets = {}

    # Expose to client
    def fullSync(self):
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
