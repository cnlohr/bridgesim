import threading

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
