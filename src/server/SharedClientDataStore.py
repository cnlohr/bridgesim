import threading
from ClientAPI import BaseContext, expose

class SharedClientDataStore:
    class Context(BaseContext):
        def instance(self, global_context):
            return global_context.network.store

    def __init__(self):
        self.__data = {}
        self.readonly = []
        self.lock = threading.Lock()

    @expose
    def get(self, key, default=None):
        with self.lock:
            if key in self.__data:
                return self.__data[key]
            else:
                return default

    @expose
    def getAndStoreIfNew(self, key, default, ro=False):
        val = self.get(key, default)
        with self.lock:
            if key not in self.__data:
                self.__data[key] = val
                if ro:
                    self.readonly.append(key)
        return val

    @expose
    def set(self, key, value, ro=False):
        if key not in self.readonly:
            with self.lock:
                self.__data[key] = value
                if ro:
                    self.readonly.append(key)
                return True
        return False

    @expose
    def setIfMissing(self, key, value, ro=False):
        with self.lock:
            if key not in self.__data:
                self.__data[key] = value

                if ro:
                    self.readonly.append(key)
                return True
        return False
