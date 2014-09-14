from ClientAPI import *

things = {}

@writable('name')
class Thing:
    class Context(BaseContext):
        def __init__(self, instance=None, serial=None):
            if instance:
                self.id = instance.id

            elif serial:
                self.id = serial[0]

        def serialized(self):
            return self.id,

        def instance(self, global_context):
            return things[self.id]

    def __init__(self, id, name):
        self.id = id
        self.name = name
        things[id] = self

    @expose
    def do_thing(self):
        print("Hi! I'm {} (ID {})".format(self.name, self.id))

    def dont_expose(self):
        print("I shouldn't be called!")

api = ClientAPI(None)

bob = Thing(1, "Bob")

api.register(Thing)
api.onCall('Thing.do_thing', (1,))
print("name is {}".format(api.onGet('Thing.name', (1,))))
api.onSet('Thing.name', (1,), "not bob")
print("name is {}".format(api.onGet('Thing.name', (1,))))
