import math

class Entity:
  def __init__(self, universe, radius=100, mass=1000):
    self.universe = universe
    self.radius = radius
    self.mass = mass
  
  def instantiate(self):
    self.universe.add(self)
    
  def destroy(self):
    self.universe.remove(self)
    
  def checkCollide(self, other):
    vector = self.location - other.location
    distance = math.sqrt(vector.x**2 + vector.y**2 + vector.z**2)
    if distance < self.radius + other.radius:
      return True
    return False
  
  def tick(self, duration):
    self.location += self.velocity*duration
