from ClientAPI import BaseContext

class Universe:
  class Context(BaseContext):
    def __init__(self, instance=None, serial=None):
      if instance:
        self.id = instance.id

      elif serial:
        _, self.id = serial

    def serialized(self):
      return ("Universe", self.id)

    def instance(self, global_context):
      return global_context.universes[self.id]

  def __init__(self, size=(100000000, 100000000)):
    self.entities = {}
    self.height = size[1]
    self.width = size[0]
    self.teams = []
    self.state = []
    self.updaters = []
    self.maxID = 0
    
  def add(self, entity):
    entity.id = self.maxID
    self.maxID += 1
    self.entities[entity.id] = entity
    
  def remove(self, entity):
    del self.entities[entity.id]
    
  # Time passes and position updates during tick
  def tick(self, duration):
    data = []
    for i in self.entities.values():
      data.append(i.tick(duration))
    return data
      
  # Position changed, so check for collisions
  def collide(self):
    for i in list(self.entities.values()):
      for j in list(self.entities.values()):
        if i != j:
          if i.checkCollide(j):
            i.collide(j)
          
  # Now that damage is dealt in collisions, destroy objects and update logic
  def tock(self):
    for i in list(self.entities.values()):
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
