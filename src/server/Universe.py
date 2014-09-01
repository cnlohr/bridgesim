class Universe:
  def __init__(self, height=100000000, width=100000000):
    self.entities = []
    self.height = height
    self.width = width
    self.teams = []
    self.state = []
    self.updaters = []
    self.maxID = 0
    
  def add(self, entity):
    self.maxID += 1
    entity.id = self.maxID
    self.entities.append(entity)
    
  def remove(self, entity):
    self.entities.remove(entity)
    
  # Time passes and position updates during tick
  def tick(self, duration):
    for i in self.entities:
      i.tick(duration)
      
  # Position changed, so check for collisions
  def collide(self):
    for i in self.entities:
      for j in self.entities:
        if i != j:
          if i.checkCollide(j):
            i.collide(j)
          
  # Now that damage is dealt in collisions, destroy objects and update logic
  def tock(self):
    for i in self.entities:
      i.tock()

    # This is just things that need to be ticked, in general
    # Right now, it's network stuff
    for i in list(self.updaters):
      try:
        i.tick()
      except OSError:
        print("Error updating client at", i.client.address," destroying")
        i.client.destroy()
        self.updaters.remove(i)
      
  def dumpState(self):
    return self.state
