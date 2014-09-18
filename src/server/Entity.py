import math
import physics
from ClientAPI import BaseContext, readable

@readable('location', 'rotation', 'velocity', 'universe', 'radius', 'mass')
class Entity:
  class Context(BaseContext):
    def __init__(self, instance=None, serial=None):
      if instance:
        self.universe = instance.universe.id
        self.id = instance.id

      elif serial:
        _, self.universe, self.id = serial

    def serialized(self):
      return ("Entity", self.universe, self.id)

    def instance(self, global_context):
      return global_context.universes[self.universe].entities[self.id]

  def __init__(self, config, universe, radius=100, mass=1000):
    self.location = physics.Vector()
    self.rotation = physics.Vector()
    self.velocity = physics.Vector()
    self.universe = universe
    self.radius = radius
    self.mass = mass
  
  def instantiate(self):
    self.universe.add(self)
    
  def destroy(self):
    self.universe.remove(self)
    
  def checkCollide(self, other):
    vector = self.location - other.location
    distance = vector.magnitude()
    if distance < self.radius + other.radius:
      return True
    return False
  
  def tick(self, duration):
    self.location += self.velocity*duration
    return self.location[0], self.location[1], self.radius

  def tock(self):
    return
