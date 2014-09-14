# This should be subclassed within each
# class that gets registered with the API
class BaseContext:
    def __init__(self, instance=None, serial=None):
        pass

    def serialized(self):
        return ()

    def instance(self, global_context):
        return None

class GlobalContext:
    def __init__(self, universes, data):
        self.universes = universes

# ** Function Decorator **
def expose(func, label=None):
    if not label:
        label = func.__name__
    setattr(func, "exposed", True)
    setattr(func, "label", label)
    return func

# There are two parts to this:
#
# One is a decorator which, applied to a function,
# marks it as registerable through the Client API.
#
# The other is a method in the ClientAPI, which gets
# passed a Class Name and searches through it for any
# applicable classes, as well as a Context class. If
# the class does not have a context, then the call
# will fail.
#
# Also, each Context will have a constructor that
# accepts a global context and either its object, or
# a tuple which represents its serialized value. It
# should also have an 'object' method which returns
# the object to which the context refers. And finally
# there should be a 'serialized' method which returns
# a tuple that uniquely identifies the context within
# the global context.
class ClientAPI:
    def __init__(self, globalContext):
        self.classes = {}
        self.globalContext = globalContext

    def onCall(self, name, ctx, *args, **kwargs):
        cls, func = name.split(".")
        classInfo = self.classes[cls]
        if func not in classInfo["methods"]:
            raise AttributeError("Method {} is not available -- did you @expose it?".format(func))

        context = classInfo["context"]
        instance = context(serial=ctx).instance(self.globalContext)

        method = classInfo["methods"][func]["callable"]
        return method(instance, *args, **kwargs)

    def register(self, cls):
        if not hasattr(cls, "Context"):
            raise AttributeError("Cannot register class {}; must have Context.".format(cls.__name__))
        if not issubclass(cls.Context, BaseContext):
            raise AttributeError("Cannot register class {}; Invalid Context.".format(cls.__name__))

        methods = {}
        for methname in dir(cls):
            method = getattr(cls, methname)
            if hasattr(method, "exposed") and hasattr(method, "label"):
                methods[method.label] = {"callable": method}
                        

        self.classes[cls.__name__] = {
            "class": cls,
            "context": cls.Context,
            "methods": methods
        }
