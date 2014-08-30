class Tube:
  def __init__(self, config, ship):
    self.ship = ship
    self.relativeLocation = config['relativeLocation']
    self.relativeRotation = config['relativeRotation']
    self.payload = None
    self.loadTime = 0
    self.loadStatus = "Empty"
    
  def load(self, payload):
    if self.loadStatus == "Empty":
      self.loadStatus = "Loading"
      self.loadTime = payload.loadTime
      self.payload = payload      
    
  def unload(self, payload):
    if self.loadStatus == "Loading":
      self.loadStatus = "Unloading"
    
  def fire(self):
    if self.loadStatus = "Loaded":
      self.payload.fire(self)
      self.loadStatus = "Empty"
      self.payload = None
      
  def tick(self, duration):
    if self.loadStatus == "Loading":
      self.loadTime -= duration
      if self.loadTime <= 0:
        self.loadStatus = "Loaded"
    if self.loadStatus == "Unloading":
      self.loadTime += duration
      if self.loadTime >= self.payload.loadTime:
        self.loadStatus = "Empty"
        self.payload = None
