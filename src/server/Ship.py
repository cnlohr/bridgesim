from Entity import Entity
from Component import *
from Missile import Missile

class Ship(Entity):
  def __init__(self, universe, config):
    super.__init__(self, universe)
    self.__dict__.update(config)
    temp = []
    for i in self.components:
      temp.append(findComponent(i.type)(self, i))
    self.components = temp
    
  def collide(self, other):
    if type(other) is Missile:
      self.takeDamage(other.getDamage(self))
      
  def takeDamage(damage, vector):
    for i in self.components:
      damage = i.takeDamage(damage)
      if damage <= 0:
        break
      
  def tick(self, duration):
    for i in components:
      i.tick(duration)
  
  def tock(self):
    for i in self.components:
      if not self.isDead():
        return
    self.destroy()