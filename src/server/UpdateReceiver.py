class UpdateReceiver:
    def __init__(self, sender, threshold=.1):
        self.sender = sender
        sender.listeners.append(self.dataReceived)
        self.threshold = threshold
        self.state = {}
        self.listeners = []

    def dataReceived(self, data):
        if "updates" in data:
            old = self.state
            del data["updates"]
            self.state.update(data)
            for l in list(self.listeners):
                l(self.state)
            
