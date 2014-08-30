class Universe:
  def __init__(self, height=100000000, width=100000000):
    self.entities = []
    self.height = height
    self.width = width
    self.teams = []
    self.state = []
    
  def add(self, entity):
    self.entities.append(entity)
    
  def remove(self, entity):
    self.entities.remove(entity)
    
  def tick(self):
    for i in entities:
      for j in i.tick(duration):
        self.state.update(j)
        
  def dumpState(self):
    return self.state
